"""Core game engine and game loop."""

import logging
import time
from typing import List, Optional

import pygame

from models import GameState, GameStatus, Vector2
from player import Player
from zombie import Zombie
from projectile import Projectile
from collision import check_collisions_with_spatial_grid, SpatialGrid
from sonrai_client import SonraiAPIClient
from game_map import GameMap


logger = logging.getLogger(__name__)


class GameEngine:
    """Core game loop and state management."""

    def __init__(
        self,
        api_client: SonraiAPIClient,
        zombies: List[Zombie],
        screen_width: int,
        screen_height: int,
        use_map: bool = True
    ):
        """
        Initialize the game engine.

        Args:
            api_client: Sonrai API client for quarantine operations
            zombies: Initial list of zombie entities
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            use_map: Whether to use map-based navigation (True) or classic scrolling (False)
        """
        self.api_client = api_client
        self.zombies = zombies
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.use_map = use_map

        # Initialize game map if enabled
        if use_map:
            self.game_map = GameMap("assets/reinvent_floorplan.png", screen_width, screen_height)

            # Initialize player at center of map
            player_start_pos = Vector2(
                self.game_map.map_width // 2,
                self.game_map.map_height // 2
            )
            self.player = Player(player_start_pos, self.game_map.map_width, self.game_map.map_height)

            # Spatial grid for entire map
            self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
        else:
            self.game_map = None
            # Classic mode - initialize player on screen
            player_start_pos = Vector2(50, screen_height // 2 - 16)
            self.player = Player(player_start_pos, screen_width, screen_height)

            # Spatial grid for screen
            self.spatial_grid = SpatialGrid(screen_width, screen_height)

        # Game entities
        self.projectiles: List[Projectile] = []

        # Game state
        self.game_state = GameState(
            status=GameStatus.PLAYING,
            zombies_remaining=len(zombies),
            zombies_quarantined=0,
            total_zombies=len(zombies)
        )

        # Timing
        self.start_time = time.time()
        self.running = True

        # Input state
        self.keys_pressed = set()

        # Scrolling (only for classic mode)
        self.scroll_speed = 50.0  # pixels per second
        self.scroll_offset = 0.0

    def start(self) -> None:
        """Start the game."""
        self.running = True
        self.start_time = time.time()
        logger.info("Game started")

    def update(self, delta_time: float) -> None:
        """
        Update game state for one frame.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update play time
        if self.game_state.status == GameStatus.PLAYING:
            self.game_state.play_time = time.time() - self.start_time

        # Handle different game states
        if self.game_state.status == GameStatus.PLAYING:
            self._update_playing(delta_time)
        elif self.game_state.status == GameStatus.PAUSED:
            # Game is paused, don't update entities
            pass

    def _update_playing(self, delta_time: float) -> None:
        """
        Update game logic during PLAYING state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Handle pending elimination delay
        if self.game_state.pending_elimination is not None:
            self.game_state.elimination_delay -= delta_time
            if self.game_state.elimination_delay <= 0:
                # Delay complete - show the message and pause
                zombie = self.game_state.pending_elimination
                self.game_state.status = GameStatus.PAUSED
                self.game_state.congratulations_message = (
                    f"You leveraged the Cloud Permissions Firewall to quarantine {zombie.identity_name}"
                )
                logger.info(f"Zombie eliminated: {zombie.identity_name}")
                # Clear pending elimination
                self.game_state.pending_elimination = None
                return  # Don't update game entities while paused

        # Update scrolling (classic mode only)
        if not self.use_map:
            self.scroll_offset += self.scroll_speed * delta_time

        # Update player
        self.player.update(delta_time)

        # Map mode: update camera and reveal nearby zombies
        if self.use_map and self.game_map:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
            self.game_map.reveal_nearby_zombies(self.player.position, self.zombies)

        # Update zombies
        for zombie in self.zombies:
            zombie.update(delta_time)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)

            # Remove off-screen/off-map projectiles
            if self.use_map and self.game_map:
                # Map mode: check against map bounds
                if projectile.is_off_screen(self.game_map.map_width, self.game_map.map_height, map_mode=True):
                    self.projectiles.remove(projectile)
            else:
                # Classic mode: check against screen bounds
                if projectile.is_off_screen(self.screen_width, self.screen_height, map_mode=False):
                    self.projectiles.remove(projectile)

        # Check collisions (only with revealed zombies in map mode)
        if self.use_map and self.game_map:
            # In map mode: only collide with zombies that are revealed AND on screen
            visible_zombies = [
                z for z in self.zombies
                if not z.is_hidden and self.game_map.is_on_screen(z.position.x, z.position.y, z.width, z.height)
            ]
        else:
            visible_zombies = self.zombies

        collisions = check_collisions_with_spatial_grid(
            self.projectiles,
            visible_zombies,
            self.spatial_grid
        )

        # Handle collisions
        for projectile, zombie in collisions:
            # Remove projectile
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

            # Pause game and show congratulations message
            self._handle_zombie_elimination(zombie)

    def _handle_zombie_elimination(self, zombie: Zombie) -> None:
        """
        Handle a zombie being eliminated.

        Args:
            zombie: The zombie that was hit
        """
        # Set pending elimination with delay (0.3 seconds for visual feedback)
        self.game_state.pending_elimination = zombie
        self.game_state.elimination_delay = 0.3  # Short delay to see the hit

        # Mark zombie as quarantining
        zombie.mark_for_quarantine()

    def dismiss_message(self) -> None:
        """Dismiss the congratulations message and resume gameplay."""
        if self.game_state.status == GameStatus.PAUSED and self.game_state.congratulations_message:
            # Get the zombie that was just eliminated
            eliminated_zombie = None
            for zombie in self.zombies:
                if zombie.is_quarantining and zombie.identity_name in self.game_state.congratulations_message:
                    eliminated_zombie = zombie
                    break

            if eliminated_zombie:
                # Attempt to quarantine via API (async in real implementation)
                # For now, we'll do it synchronously
                self._quarantine_zombie(eliminated_zombie)

            # Clear message and resume
            self.game_state.congratulations_message = None
            self.game_state.status = GameStatus.PLAYING

    def _quarantine_zombie(self, zombie: Zombie) -> None:
        """
        Quarantine a zombie via the API.

        Args:
            zombie: The zombie to quarantine
        """
        try:
            result = self.api_client.quarantine_identity(
                identity_id=zombie.identity_id,
                identity_name=zombie.identity_name
            )

            if result.success:
                # Successfully quarantined - remove zombie permanently
                if zombie in self.zombies:
                    self.zombies.remove(zombie)
                    self.game_state.zombies_remaining -= 1
                    self.game_state.zombies_quarantined += 1

                    logger.info(f"Successfully quarantined {zombie.identity_name}")

                    # Check for victory
                    if self.game_state.zombies_remaining == 0:
                        self.game_state.status = GameStatus.VICTORY
                        logger.info("Victory! All zombies quarantined")
            else:
                # Quarantine failed - restore zombie
                zombie.is_quarantining = False
                self.game_state.error_message = f"Failed to quarantine {zombie.identity_name}"
                logger.error(f"Quarantine failed: {result.error_message}")

        except Exception as e:
            # Error during quarantine - restore zombie
            zombie.is_quarantining = False
            self.game_state.error_message = f"Error: {str(e)}"
            logger.error(f"Exception during quarantine: {e}")

    def handle_input(self, events: List[pygame.event.Event]) -> None:
        """
        Handle input events.

        Args:
            events: List of Pygame events
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)

                # Handle message dismissal
                if event.key == pygame.K_RETURN:
                    if self.game_state.status == GameStatus.PAUSED:
                        self.dismiss_message()

                # Handle firing
                if event.key == pygame.K_SPACE:
                    if self.game_state.status == GameStatus.PLAYING:
                        projectile = self.player.fire_projectile()
                        self.projectiles.append(projectile)

                # Handle quit
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

        # Handle continuous movement
        if self.game_state.status == GameStatus.PLAYING:
            # Horizontal movement
            if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
                self.player.move_left()
            elif pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
                self.player.move_right()
            else:
                self.player.stop_horizontal()
            
            # Vertical movement
            if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
                self.player.move_up()
            elif pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
                self.player.move_down()
            else:
                self.player.stop_vertical()

    def is_running(self) -> bool:
        """
        Check if the game is still running.

        Returns:
            True if running, False otherwise
        """
        return self.running

    def get_game_state(self) -> GameState:
        """
        Get the current game state.

        Returns:
            Current GameState
        """
        return self.game_state

    def get_player(self) -> Player:
        """Get the player instance."""
        return self.player

    def get_zombies(self) -> List[Zombie]:
        """Get the list of zombies."""
        return self.zombies

    def get_projectiles(self) -> List[Projectile]:
        """Get the list of projectiles."""
        return self.projectiles

    def get_scroll_offset(self) -> float:
        """Get the current scroll offset."""
        return self.scroll_offset

    def distribute_zombies(self) -> None:
        """Distribute zombies across the level space."""
        if not self.zombies:
            logger.warning("No zombies to distribute!")
            return

        if self.use_map and self.game_map:
            # Map mode: scatter zombies randomly across the floorplan
            self.game_map.scatter_zombies(self.zombies)
            logger.info(f"Scattered {len(self.zombies)} zombies across the re:invent floorplan")
        else:
            # Classic mode: distribute zombies across a wide horizontal space
            # Start from 200 pixels so some are visible immediately
            level_width = self.screen_width * 10  # 10 screens wide
            spacing = level_width / len(self.zombies)

            for i, zombie in enumerate(self.zombies):
                # Distribute horizontally starting from x=200
                x = 200 + (i * spacing)
                # Vary vertical position across 5 rows
                y = 100 + ((i % 5) * 80)

                zombie.position = Vector2(x, y)
                zombie.is_hidden = False  # All visible in classic mode

            logger.info(f"Distributed {len(self.zombies)} zombies. First zombie at ({self.zombies[0].position.x}, {self.zombies[0].position.y})")

    def get_game_map(self) -> Optional[GameMap]:
        """Get the game map instance (None if not in map mode)."""
        return self.game_map if self.use_map else None
