"""Platformer genre controller for side-scrolling gameplay.

Implements Mario-style platformer mechanics with gravity, jumping,
and horizontal movement. This is the default genre for all levels.

**Feature: multi-genre-levels**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""

import logging
from typing import List, Optional

import pygame

from genre_controller import GenreController, GenreControllerFactory, InputState
from models import GenreType, Vector2

logger = logging.getLogger(__name__)


class PlatformerController(GenreController):
    """Controller for platformer-style side-scrolling gameplay.

    Handles:
    - Horizontal movement (left/right)
    - Jumping with gravity
    - Platform collision detection
    - Zombie patrol behavior
    """

    # Physics constants
    GRAVITY = 1200  # Pixels per second squared
    JUMP_VELOCITY = -500  # Initial upward velocity
    MOVE_SPEED = 300  # Horizontal movement speed
    GROUND_Y = 832  # Default ground level

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the platformer controller.

        Args:
            genre: Should be GenreType.PLATFORMER
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        super().__init__(genre, screen_width, screen_height)

        # Level dimensions
        self.level_width = screen_width
        self.level_height = screen_height

        # Platform data
        self.platforms: List[pygame.Rect] = []
        self.ground_level = self.GROUND_Y

        # Camera/scroll offset
        self.camera_offset = Vector2(0, 0)

        # Player state tracking
        self.player_on_ground = False
        self.player_velocity_y = 0

        logger.info("PlatformerController initialized")

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up platformer level layout.

        Args:
            account_id: AWS account ID for this level
            zombies: List of zombie entities to place
            level_width: Width of the level
            level_height: Height of the level
        """
        self.level_width = level_width
        self.level_height = level_height
        self.zombies = zombies

        # Generate platforms based on level size
        self._generate_platforms()

        # Position zombies on platforms
        self._position_zombies_on_platforms()

        self.is_initialized = True
        logger.info(
            f"Platformer level initialized: {level_width}x{level_height}, "
            f"{len(zombies)} zombies"
        )

    def _generate_platforms(self) -> None:
        """Generate platform layout for the level."""
        self.platforms.clear()

        # Ground platform (full width)
        ground = pygame.Rect(0, self.ground_level, self.level_width, 50)
        self.platforms.append(ground)

        # Add floating platforms at regular intervals
        platform_spacing = 400
        platform_width = 200
        platform_height = 20

        for x in range(200, self.level_width - 200, platform_spacing):
            # Alternate platform heights
            y_offset = 150 if (x // platform_spacing) % 2 == 0 else 250
            platform = pygame.Rect(
                x, self.ground_level - y_offset, platform_width, platform_height
            )
            self.platforms.append(platform)

    def _position_zombies_on_platforms(self) -> None:
        """Position zombies on platforms for patrol behavior."""
        if not self.zombies:
            return

        # Distribute zombies across the level
        spacing = self.level_width / (len(self.zombies) + 1)

        for i, zombie in enumerate(self.zombies):
            x = spacing * (i + 1)
            y = self.ground_level - 50  # Above ground level

            # Find nearest platform
            for platform in self.platforms:
                if platform.left <= x <= platform.right:
                    y = platform.top - 50
                    break

            zombie.position = Vector2(x, y)

            # Set patrol bounds
            if hasattr(zombie, "patrol_left"):
                zombie.patrol_left = max(0, x - 150)
                zombie.patrol_right = min(self.level_width, x + 150)

    def update(self, delta_time: float, player) -> None:
        """Update platformer game logic.

        Args:
            delta_time: Time since last frame in seconds
            player: Player entity
        """
        if not self.is_initialized:
            return

        # Apply gravity to player
        self._apply_gravity(delta_time, player)

        # Check platform collisions
        self._check_platform_collisions(player)

        # Update zombie patrol behavior
        self._update_zombie_patrol(delta_time)

        # Update camera to follow player
        self._update_camera(player)

        # Check completion
        if self.get_active_zombie_count() == 0:
            self.is_complete = True

    def _apply_gravity(self, delta_time: float, player) -> None:
        """Apply gravity to the player.

        Args:
            delta_time: Time since last frame
            player: Player entity
        """
        if not self.player_on_ground:
            self.player_velocity_y += self.GRAVITY * delta_time
            player.position.y += self.player_velocity_y * delta_time

    def _check_platform_collisions(self, player) -> None:
        """Check and resolve platform collisions.

        Args:
            player: Player entity
        """
        player_rect = player.get_bounds()
        self.player_on_ground = False

        for platform in self.platforms:
            if player_rect.colliderect(platform):
                # Check if landing on top of platform
                if (
                    self.player_velocity_y > 0
                    and player_rect.bottom <= platform.top + 20
                ):
                    player.position.y = platform.top - player_rect.height
                    self.player_velocity_y = 0
                    self.player_on_ground = True
                    break

    def _update_zombie_patrol(self, delta_time: float) -> None:
        """Update zombie patrol movement.

        Args:
            delta_time: Time since last frame
        """
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            # Simple patrol behavior
            if hasattr(zombie, "patrol_left") and hasattr(zombie, "patrol_right"):
                speed = getattr(zombie, "speed", 50)
                direction = getattr(zombie, "patrol_direction", 1)

                zombie.position.x += speed * direction * delta_time

                # Reverse at patrol bounds
                if zombie.position.x <= zombie.patrol_left:
                    zombie.patrol_direction = 1
                elif zombie.position.x >= zombie.patrol_right:
                    zombie.patrol_direction = -1

    def _update_camera(self, player) -> None:
        """Update camera to follow player.

        Args:
            player: Player entity
        """
        # Center camera on player with some lead room
        target_x = player.position.x - self.screen_width // 3

        # Clamp to level bounds
        target_x = max(0, min(target_x, self.level_width - self.screen_width))

        # Smooth camera movement
        self.camera_offset.x += (target_x - self.camera_offset.x) * 0.1

    def handle_input(self, input_state: InputState, player) -> None:
        """Process platformer input.

        Args:
            input_state: Current input state
            player: Player entity to control
        """
        # Horizontal movement
        if input_state.left:
            player.velocity.x = -self.MOVE_SPEED
        elif input_state.right:
            player.velocity.x = self.MOVE_SPEED
        else:
            player.velocity.x = 0

        # Jumping
        if input_state.jump and self.player_on_ground:
            self.player_velocity_y = self.JUMP_VELOCITY
            self.player_on_ground = False

    def check_completion(self) -> bool:
        """Check if all zombies are eliminated.

        Returns:
            True if level is complete
        """
        return self.is_complete or self.get_active_zombie_count() == 0

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render platformer-specific elements.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset for scrolling
        """
        # Render platforms
        for platform in self.platforms:
            # Adjust for camera
            render_rect = pygame.Rect(
                platform.x - camera_offset.x,
                platform.y - camera_offset.y,
                platform.width,
                platform.height,
            )

            # Only render if visible
            if render_rect.right > 0 and render_rect.left < self.screen_width:
                pygame.draw.rect(surface, (100, 100, 100), render_rect)
                pygame.draw.rect(surface, (150, 150, 150), render_rect, 2)

    def get_camera_offset(self) -> Vector2:
        """Get current camera offset.

        Returns:
            Camera offset vector
        """
        return self.camera_offset

    def player_jump(self, player) -> bool:
        """Make the player jump if on ground.

        Args:
            player: Player entity

        Returns:
            True if jump was successful
        """
        if self.player_on_ground:
            self.player_velocity_y = self.JUMP_VELOCITY
            self.player_on_ground = False
            return True
        return False


# Register the platformer controller with the factory
GenreControllerFactory.register(GenreType.PLATFORMER, PlatformerController)
