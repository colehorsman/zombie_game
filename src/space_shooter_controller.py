"""Space Shooter genre controller for vertical shooter gameplay.

Implements Galaga/Space Invaders style mechanics with the player ship
at the bottom and zombies descending from the top.

**Feature: multi-genre-levels**
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.6**
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import List, Optional

import pygame

from genre_controller import GenreController, GenreControllerFactory, InputState
from models import GenreType, Vector2

logger = logging.getLogger(__name__)


@dataclass
class SpaceProjectile:
    """Projectile fired by the player ship."""

    position: Vector2
    velocity: Vector2
    damage: int = 34  # ~3 hits to kill (zombie has 100 HP)
    radius: int = 15  # Larger hitbox for easier hits
    active: bool = True


class SpaceShooterController(GenreController):
    """Controller for Space Shooter vertical shooter gameplay.

    Features:
    - Player ship at bottom of screen
    - Horizontal movement only
    - Projectiles travel upward
    - Zombies spawn at top in formations
    - Zombies descend toward player
    - Damage when zombies reach bottom

    **Property 4: Space Shooter Player Position**
    Player at bottom, projectiles travel upward.
    **Validates: Requirements 3.2, 3.4**

    **Property 5: Space Shooter Zombie Behavior**
    Zombies spawn at top, move down, damage on bottom reach.
    **Validates: Requirements 3.3, 3.6**
    """

    # Game constants
    PLAYER_Y_OFFSET = 50  # Distance from bottom
    PLAYER_SPEED = 350  # Horizontal movement speed
    PROJECTILE_SPEED = 500  # Upward projectile speed
    FIRE_COOLDOWN = 0.2  # Seconds between shots
    ZOMBIE_DESCENT_SPEED = 30  # Slower descent speed
    FORMATION_SWAY_SPEED = 20  # Slower horizontal sway
    FORMATION_SWAY_AMPLITUDE = 60  # Less sway distance

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the space shooter controller.

        Args:
            genre: Should be GenreType.SPACE_SHOOTER
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        super().__init__(genre, screen_width, screen_height)

        # Player state
        self.player_x = screen_width // 2
        self.player_y = screen_height - self.PLAYER_Y_OFFSET

        # Projectiles
        self.projectiles: List[SpaceProjectile] = []
        self.fire_cooldown = 0

        # Formation state
        self.formation_time = 0
        self.formation_offset_x = 0

        # Zombie positions (separate from zombie entities for formation control)
        self.zombie_positions: dict = {}  # zombie -> Vector2

        # Player damage tracking
        self.player_damage_cooldown = 0

        # Wave-based spawning
        self.all_zombies: List = []  # All zombies for the level
        self.active_zombie_indices: List[int] = []  # Indices of currently active zombies
        self.max_active_zombies = 3  # Only 3 zombies on screen at once (slower pace)
        self.spawn_timer = 0.0
        self.spawn_interval = 4.0  # Spawn new zombie every 4 seconds
        self.zombies_spawned = 0

        # Reference to game engine for quarantine API calls
        self.game_engine = None
        self.total_zombies_to_spawn = 0

        # Callback for zombie elimination (set by game engine)
        self.on_zombie_eliminated_callback = None

        logger.info("SpaceShooterController initialized")

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up space shooter level with wave-based spawning.

        Args:
            account_id: AWS account ID for this level
            zombies: List of zombie entities to place
            level_width: Width of the level (ignored, uses screen width)
            level_height: Height of the level (ignored, uses screen height)
        """
        self.all_zombies = zombies
        self.zombies = []  # Start with no active zombies
        self.projectiles.clear()
        self.zombie_positions.clear()

        # Set up wave spawning
        self.total_zombies_to_spawn = len(zombies)
        self.zombies_spawned = 0
        self.spawn_timer = 0.0

        # Hide all zombies initially
        for zombie in self.all_zombies:
            zombie.position = Vector2(-100, -100)  # Off screen
            zombie.is_hidden = True

        # Spawn initial wave
        self._spawn_wave()

        self.is_initialized = True
        logger.info(
            f"Space shooter level initialized with {len(zombies)} total zombies, spawning in waves"
        )

    def _spawn_wave(self) -> None:
        """Spawn a new wave of zombies at random positions at top."""
        zombies_to_spawn = min(
            self.max_active_zombies - len(self.zombies),
            self.total_zombies_to_spawn - self.zombies_spawned,
        )

        for _ in range(zombies_to_spawn):
            if self.zombies_spawned >= self.total_zombies_to_spawn:
                break

            zombie = self.all_zombies[self.zombies_spawned]
            self.zombies_spawned += 1

            # Random spawn position at top
            x = random.randint(50, self.screen_width - 50)
            y = random.randint(-150, -50)  # Start above screen

            zombie.position = Vector2(x, y)
            zombie.is_hidden = False
            zombie.health = 100  # Reset health

            # Random movement properties
            zombie._random_offset = random.uniform(-50, 50)
            zombie._random_speed = random.uniform(0.6, 1.4)
            zombie._wobble_phase = random.uniform(0, math.pi * 2)
            zombie._wobble_speed = random.uniform(1.0, 4.0)

            self.zombie_positions[zombie] = Vector2(x, y)
            self.zombies.append(zombie)

        logger.info(
            f"Spawned wave: {len(self.zombies)} active, {self.zombies_spawned}/{self.total_zombies_to_spawn} total"
        )

    def _create_formation(self) -> None:
        """Create random spawn positions for zombies (legacy, now using wave spawning)."""
        pass  # No longer used - using _spawn_wave instead

    def update(self, delta_time: float, player) -> None:
        """Update space shooter game logic.

        Args:
            delta_time: Time since last frame in seconds
            player: Player entity (position overridden for space shooter)
        """
        if not self.is_initialized:
            return

        # Update formation sway
        self.formation_time += delta_time
        self.formation_offset_x = (
            math.sin(self.formation_time * self.FORMATION_SWAY_SPEED * 0.1)
            * self.FORMATION_SWAY_AMPLITUDE
        )

        # Update fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= delta_time

        # Update player damage cooldown
        if self.player_damage_cooldown > 0:
            self.player_damage_cooldown -= delta_time

        # Update projectiles
        self._update_projectiles(delta_time)

        # Update zombie positions (descent + sway)
        self._update_zombie_formation(delta_time, player)

        # Check projectile-zombie collisions
        self._check_projectile_collisions()

        # Check if zombies reached bottom (removes 1 heart)
        self._check_bottom_collision(player)

        # Spawn new zombies periodically
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval and len(self.zombies) < self.max_active_zombies:
            self.spawn_timer = 0.0
            self._spawn_wave()

        # Sync player position to our controlled position
        player.position.x = self.player_x
        player.position.y = self.player_y

        # Check completion
        if self.get_active_zombie_count() == 0:
            self.is_complete = True

    def _update_projectiles(self, delta_time: float) -> None:
        """Update projectile positions and remove off-screen ones."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            proj.position.y += proj.velocity.y * delta_time

            # Remove if off screen
            if proj.position.y < -10:
                proj.active = False

        # Clean up inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def _update_zombie_formation(self, delta_time: float, player) -> None:
        """Update zombie formation movement with randomness."""
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            if zombie not in self.zombie_positions:
                continue

            base_pos = self.zombie_positions[zombie]

            # Initialize random movement offset if not set
            if not hasattr(zombie, "_random_offset"):
                zombie._random_offset = random.uniform(-30, 30)
                zombie._random_speed = random.uniform(0.8, 1.2)
                zombie._wobble_phase = random.uniform(0, math.pi * 2)
                zombie._wobble_speed = random.uniform(1.5, 3.0)

            # Apply descent with random speed variation
            base_pos.y += self.ZOMBIE_DESCENT_SPEED * zombie._random_speed * delta_time

            # Apply formation sway plus individual wobble
            individual_wobble = (
                math.sin(self.formation_time * zombie._wobble_speed + zombie._wobble_phase) * 25
            )
            zombie.position.x = (
                base_pos.x + self.formation_offset_x + zombie._random_offset + individual_wobble
            )
            zombie.position.y = base_pos.y

            # Clamp to screen bounds
            zombie.position.x = max(20, min(self.screen_width - 20, zombie.position.x))

    def _check_projectile_collisions(self) -> None:
        """Check for projectile-zombie collisions."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            # Larger collision box for projectile
            proj_rect = pygame.Rect(
                proj.position.x - proj.radius,
                proj.position.y - proj.radius - 10,  # Extend upward for laser beam
                proj.radius * 2,
                proj.radius * 2 + 20,  # Taller hitbox
            )

            for zombie in self.zombies:
                if getattr(zombie, "is_quarantining", False):
                    continue
                if zombie.health <= 0:
                    continue

                zombie_rect = zombie.get_bounds()
                if proj_rect.colliderect(zombie_rect):
                    # Hit!
                    proj.active = False
                    zombie.take_damage(proj.damage)
                    logger.debug(
                        f"Hit zombie! Damage: {proj.damage}, Health remaining: {zombie.health}"
                    )

                    # Check if zombie eliminated
                    if zombie.health <= 0:
                        zombie.is_quarantining = True  # Mark as being eliminated
                        zombie.is_hidden = True
                        # Remove from active zombies first
                        if zombie in self.zombies:
                            self.zombies.remove(zombie)
                        if zombie in self.zombie_positions:
                            del self.zombie_positions[zombie]
                        # Call the callback to trigger quarantine API
                        if self.on_zombie_eliminated_callback:
                            self.on_zombie_eliminated_callback(zombie)
                        else:
                            self.on_zombie_eliminated(zombie)
                        logger.info(
                            f"Zombie eliminated! {len(self.zombies)} active, {self.zombies_spawned}/{self.total_zombies_to_spawn} spawned"
                        )
                    break

    def _check_bottom_collision(self, player) -> None:
        """Check if zombies reached the player's level (takes 1 heart from player)."""
        # Zombies that reach the player's Y position escape and deal damage
        bottom_threshold = self.player_y - 10  # At player level

        zombies_to_remove = []
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            # Debug: log zombie positions periodically
            if zombie.position.y > 500:
                logger.debug(
                    f"Zombie {zombie.identity_name} at Y={zombie.position.y}, threshold={bottom_threshold}"
                )

            if zombie.position.y >= bottom_threshold:
                # Zombie escaped past player - take 1 heart (2 damage = 1 heart, max_health=10)
                logger.info(f"💔 Zombie {zombie.identity_name} escaped past player!")
                player.take_damage(2)
                logger.info(
                    f"💔 Player health after damage: {player.current_health}/{player.max_health}"
                )

                # Mark zombie for removal
                zombie.is_hidden = True
                zombies_to_remove.append(zombie)

        # Remove escaped zombies
        for zombie in zombies_to_remove:
            if zombie in self.zombies:
                self.zombies.remove(zombie)
            if zombie in self.zombie_positions:
                del self.zombie_positions[zombie]

    def handle_input(self, input_state: InputState, player) -> None:
        """Process space shooter input.

        Args:
            input_state: Current input state
            player: Player entity (position controlled by this controller)
        """
        # Horizontal movement only
        if input_state.left:
            self.player_x -= self.PLAYER_SPEED * 0.016  # Approximate delta
            self.player_x = max(30, self.player_x)
        elif input_state.right:
            self.player_x += self.PLAYER_SPEED * 0.016
            self.player_x = min(self.screen_width - 30, self.player_x)

        # Shooting
        if input_state.shoot and self.fire_cooldown <= 0:
            self._fire_projectile()
            self.fire_cooldown = self.FIRE_COOLDOWN

    def _fire_projectile(self) -> None:
        """Fire a projectile from the player ship."""
        proj = SpaceProjectile(
            position=Vector2(self.player_x, self.player_y - 20),
            velocity=Vector2(0, -self.PROJECTILE_SPEED),
        )
        self.projectiles.append(proj)

    def check_completion(self) -> bool:
        """Check if all zombies are eliminated.

        Returns:
            True if level is complete
        """
        # Complete when all zombies spawned and none remain active
        all_spawned = self.zombies_spawned >= self.total_zombies_to_spawn
        none_active = len(self.zombies) == 0
        return self.is_complete or (all_spawned and none_active)

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render space shooter elements.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (ignored for space shooter)
        """
        # Render starfield background effect
        self._render_starfield(surface)

        # Render zombies with labels (NO health bars)
        self._render_zombies(surface)

        # Render projectiles (purple laser beams)
        for proj in self.projectiles:
            if proj.active:
                # Draw laser beam
                pygame.draw.rect(
                    surface,
                    (180, 100, 255),  # Purple laser
                    (int(proj.position.x) - 2, int(proj.position.y) - 10, 4, 20),
                )
                pygame.draw.rect(
                    surface,
                    (255, 200, 255),  # Bright center
                    (int(proj.position.x) - 1, int(proj.position.y) - 8, 2, 16),
                )

        # Render purple spaceship (Space Invaders style)
        self._render_spaceship(surface)

    def _render_spaceship(self, surface) -> None:
        """Render a purple Space Invaders style spaceship."""
        x, y = int(self.player_x), int(self.player_y)

        # Ship colors
        PURPLE_DARK = (80, 40, 120)
        PURPLE_MID = (120, 60, 180)
        PURPLE_LIGHT = (180, 100, 255)
        PURPLE_GLOW = (200, 150, 255)

        # Main body (wider base, narrower top)
        # Bottom section (wide)
        pygame.draw.rect(surface, PURPLE_MID, (x - 20, y, 40, 8))
        # Middle section
        pygame.draw.rect(surface, PURPLE_MID, (x - 15, y - 8, 30, 8))
        # Top section (cockpit)
        pygame.draw.rect(surface, PURPLE_LIGHT, (x - 8, y - 16, 16, 8))
        # Tip
        pygame.draw.rect(surface, PURPLE_GLOW, (x - 3, y - 22, 6, 6))

        # Wings
        pygame.draw.polygon(
            surface,
            PURPLE_DARK,
            [
                (x - 20, y + 8),
                (x - 30, y + 15),
                (x - 20, y + 2),
            ],
        )
        pygame.draw.polygon(
            surface,
            PURPLE_DARK,
            [
                (x + 20, y + 8),
                (x + 30, y + 15),
                (x + 20, y + 2),
            ],
        )

        # Engine glow
        pygame.draw.rect(surface, (255, 150, 50), (x - 8, y + 8, 6, 4))
        pygame.draw.rect(surface, (255, 150, 50), (x + 2, y + 8, 6, 4))
        pygame.draw.rect(surface, (255, 255, 150), (x - 6, y + 10, 4, 3))
        pygame.draw.rect(surface, (255, 255, 150), (x + 2, y + 10, 4, 3))

    def _render_zombies(self, surface) -> None:
        """Render zombies with their identity name labels (NO health bars)."""
        font = pygame.font.Font(None, 18)

        for zombie in self.zombies:
            if zombie.is_hidden:
                continue

            x, y = int(zombie.position.x), int(zombie.position.y)

            # Draw zombie as a green alien invader shape
            GREEN = (0, 200, 0)
            GREEN_LIGHT = (100, 255, 100)

            # Body
            pygame.draw.rect(surface, GREEN, (x - 12, y - 8, 24, 16))
            # Eyes
            pygame.draw.rect(surface, GREEN_LIGHT, (x - 8, y - 4, 6, 6))
            pygame.draw.rect(surface, GREEN_LIGHT, (x + 2, y - 4, 6, 6))
            # Antennae
            pygame.draw.rect(surface, GREEN, (x - 10, y - 14, 4, 6))
            pygame.draw.rect(surface, GREEN, (x + 6, y - 14, 4, 6))
            # Legs
            pygame.draw.rect(surface, GREEN, (x - 10, y + 8, 4, 6))
            pygame.draw.rect(surface, GREEN, (x + 6, y + 8, 4, 6))

            # Render zombie name label above the zombie
            label_text = zombie.identity_name
            if len(label_text) > 15:
                label_text = label_text[:12] + "..."
            label_surface = font.render(label_text, True, (255, 255, 255))
            label_x = x - label_surface.get_width() // 2
            label_y = y - 28  # Above the zombie
            surface.blit(label_surface, (label_x, label_y))

    def _render_starfield(self, surface) -> None:
        """Render scrolling starfield background."""
        # Simple star effect based on time
        random.seed(42)  # Consistent star positions
        for _ in range(50):
            x = random.randint(0, self.screen_width)
            y = (
                random.randint(0, self.screen_height) + int(self.formation_time * 20)
            ) % self.screen_height
            brightness = random.randint(100, 255)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)


# Register the space shooter controller with the factory
GenreControllerFactory.register(GenreType.SPACE_SHOOTER, SpaceShooterController)
