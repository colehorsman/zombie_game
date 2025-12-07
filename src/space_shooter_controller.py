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
    damage: int = 25
    radius: int = 5
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
    PLAYER_SPEED = 400  # Horizontal movement speed
    PROJECTILE_SPEED = 600  # Upward projectile speed
    FIRE_COOLDOWN = 0.15  # Seconds between shots
    ZOMBIE_DESCENT_SPEED = 80  # Base descent speed
    FORMATION_SWAY_SPEED = 50  # Horizontal sway speed
    FORMATION_SWAY_AMPLITUDE = 100  # Sway distance

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

        logger.info("SpaceShooterController initialized")

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up space shooter level with formation.

        Args:
            account_id: AWS account ID for this level
            zombies: List of zombie entities to place
            level_width: Width of the level (ignored, uses screen width)
            level_height: Height of the level (ignored, uses screen height)
        """
        self.zombies = zombies
        self.projectiles.clear()
        self.zombie_positions.clear()

        # Position zombies in formation at top of screen
        self._create_formation()

        self.is_initialized = True
        logger.info(f"Space shooter level initialized with {len(zombies)} zombies")

    def _create_formation(self) -> None:
        """Create Galaga-style formation for zombies."""
        if not self.zombies:
            return

        # Calculate formation grid
        cols = min(10, len(self.zombies))
        rows = (len(self.zombies) + cols - 1) // cols

        spacing_x = self.screen_width // (cols + 1)
        spacing_y = 60
        start_y = 80

        for i, zombie in enumerate(self.zombies):
            row = i // cols
            col = i % cols

            x = spacing_x * (col + 1)
            y = start_y + row * spacing_y

            self.zombie_positions[zombie] = Vector2(x, y)
            zombie.position = Vector2(x, y)

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

        # Check if zombies reached bottom
        self._check_bottom_collision(player)

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
        """Update zombie formation movement."""
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            if zombie not in self.zombie_positions:
                continue

            base_pos = self.zombie_positions[zombie]

            # Apply descent
            base_pos.y += self.ZOMBIE_DESCENT_SPEED * delta_time

            # Apply formation sway
            zombie.position.x = base_pos.x + self.formation_offset_x
            zombie.position.y = base_pos.y

            # Clamp to screen bounds
            zombie.position.x = max(20, min(self.screen_width - 20, zombie.position.x))

    def _check_projectile_collisions(self) -> None:
        """Check for projectile-zombie collisions."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            proj_rect = pygame.Rect(
                proj.position.x - proj.radius,
                proj.position.y - proj.radius,
                proj.radius * 2,
                proj.radius * 2,
            )

            for zombie in self.zombies:
                if getattr(zombie, "is_quarantining", False):
                    continue

                zombie_rect = zombie.get_bounds()
                if proj_rect.colliderect(zombie_rect):
                    # Hit!
                    proj.active = False
                    zombie.take_damage(proj.damage)

                    # Check if zombie eliminated
                    if zombie.health <= 0:
                        self.on_zombie_eliminated(zombie)
                    break

    def _check_bottom_collision(self, player) -> None:
        """Check if zombies reached the bottom (damages player)."""
        if self.player_damage_cooldown > 0:
            return

        bottom_threshold = self.screen_height - 100

        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            if zombie.position.y >= bottom_threshold:
                # Zombie reached bottom - damage player
                if hasattr(player, "take_damage"):
                    player.take_damage(10)
                    self.player_damage_cooldown = 1.0  # 1 second cooldown

                # Reset zombie to top
                if zombie in self.zombie_positions:
                    self.zombie_positions[zombie].y = random.randint(-100, -50)
                break

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
        return self.is_complete or self.get_active_zombie_count() == 0

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render space shooter elements.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (ignored for space shooter)
        """
        # Render starfield background effect
        self._render_starfield(surface)

        # Render projectiles
        for proj in self.projectiles:
            if proj.active:
                pygame.draw.circle(
                    surface,
                    (0, 255, 255),  # Cyan projectiles
                    (int(proj.position.x), int(proj.position.y)),
                    proj.radius,
                )

        # Render player ship (triangle)
        ship_points = [
            (self.player_x, self.player_y - 20),  # Top
            (self.player_x - 15, self.player_y + 10),  # Bottom left
            (self.player_x + 15, self.player_y + 10),  # Bottom right
        ]
        pygame.draw.polygon(surface, (0, 200, 255), ship_points)
        pygame.draw.polygon(surface, (255, 255, 255), ship_points, 2)

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
