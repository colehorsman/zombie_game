"""Player character implementation."""

import pygame
from typing import Optional

from models import Vector2


class Player:
    """Represents the controllable Mega Man-style character."""

    def __init__(self, position: Vector2, map_width: Optional[int] = None, map_height: Optional[int] = None):
        """
        Initialize the player.

        Args:
            position: Starting position
            map_width: Width of the map for boundary checking (None for screen-based)
            map_height: Height of the map for boundary checking (None for screen-based)
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.map_width = map_width
        self.map_height = map_height

        # Player dimensions (match zombie size)
        self.width = 40
        self.height = 40

        # Movement speed (pixels per second) - realistic walking speed
        self.move_speed = 120.0  # Slower for realistic navigation

        # Facing direction for firing projectiles
        self.facing_direction = Vector2(1, 0)  # Start facing right

        # Visual direction (only left/right for sprite)
        self.visual_direction = 1  # 1 = right, -1 = left

        # Create base sprite (facing right)
        self.base_sprite = self._create_sprite()
        self.sprite = self.base_sprite.copy()  # Current displayed sprite

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a retro 8-bit Megaman-inspired sprite with purple colors.

        Returns:
            Pygame surface with the player sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Purple color palette inspired by Megaman
        DARK_PURPLE = (80, 40, 120)      # Dark armor/shadows
        PURPLE = (120, 60, 180)          # Main body color
        LIGHT_PURPLE = (160, 100, 220)   # Highlights
        BRIGHT_PURPLE = (200, 140, 255)  # Bright highlights
        CYAN = (100, 200, 255)           # Visor/eyes (classic Megaman cyan)
        BLACK = (0, 0, 0)                # Outlines
        GREY = (128, 128, 128)           # Gun details
        YELLOW = (255, 220, 100)         # Energy/accents

        # Helmet (top portion)
        helmet_rect = pygame.Rect(10, 2, 20, 12)
        pygame.draw.rect(sprite, PURPLE, helmet_rect)
        pygame.draw.rect(sprite, BLACK, helmet_rect, 1)  # Outline

        # Helmet highlights
        pygame.draw.rect(sprite, LIGHT_PURPLE, (12, 4, 8, 3))

        # Visor/face area
        visor_rect = pygame.Rect(12, 12, 16, 8)
        pygame.draw.rect(sprite, CYAN, visor_rect)
        pygame.draw.rect(sprite, BLACK, visor_rect, 1)

        # Eyes (classic Megaman style)
        pygame.draw.rect(sprite, BLACK, (15, 14, 3, 3))  # Left eye
        pygame.draw.rect(sprite, BLACK, (22, 14, 3, 3))  # Right eye

        # Body/chest armor
        body_rect = pygame.Rect(8, 20, 18, 12)
        pygame.draw.rect(sprite, DARK_PURPLE, body_rect)
        pygame.draw.rect(sprite, BLACK, body_rect, 1)  # Outline

        # Chest plate detail
        pygame.draw.rect(sprite, PURPLE, (12, 22, 10, 3))

        # Left arm (normal arm)
        pygame.draw.rect(sprite, PURPLE, (4, 22, 4, 10))
        pygame.draw.rect(sprite, BLACK, (4, 22, 4, 10), 1)

        # Right arm - MEGA BUSTER / RAYGUN (iconic!)
        # Upper arm
        pygame.draw.rect(sprite, PURPLE, (26, 22, 5, 8))
        pygame.draw.rect(sprite, BLACK, (26, 22, 5, 8), 1)

        # Arm cannon/raygun barrel (extended forward)
        cannon_rect = pygame.Rect(31, 23, 7, 5)
        pygame.draw.rect(sprite, GREY, cannon_rect)
        pygame.draw.rect(sprite, BLACK, cannon_rect, 1)

        # Cannon muzzle (darker opening)
        pygame.draw.rect(sprite, DARK_PURPLE, (36, 24, 2, 3))

        # Energy glow on cannon
        pygame.draw.rect(sprite, YELLOW, (32, 24, 3, 3))

        # Legs/boots
        # Left leg
        pygame.draw.rect(sprite, DARK_PURPLE, (10, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (10, 32, 6, 8), 1)

        # Right leg
        pygame.draw.rect(sprite, DARK_PURPLE, (18, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (18, 32, 6, 8), 1)

        # Boot highlights
        pygame.draw.rect(sprite, PURPLE, (11, 33, 4, 3))
        pygame.draw.rect(sprite, PURPLE, (19, 33, 4, 3))

        return sprite

    def _update_sprite_rotation(self) -> None:
        """Update the sprite to match the current visual direction (only left/right)."""
        if self.visual_direction > 0:  # Facing right
            self.sprite = self.base_sprite.copy()
        else:  # Facing left
            self.sprite = pygame.transform.flip(self.base_sprite, True, False)

    def move_left(self) -> None:
        """Set velocity to move left."""
        self.velocity.x = -self.move_speed
        self.facing_direction = Vector2(-1, 0)
        self.visual_direction = -1
        self._update_sprite_rotation()

    def move_right(self) -> None:
        """Set velocity to move right."""
        self.velocity.x = self.move_speed
        self.facing_direction = Vector2(1, 0)
        self.visual_direction = 1
        self._update_sprite_rotation()

    def move_up(self) -> None:
        """Set velocity to move up."""
        self.velocity.y = -self.move_speed
        self.facing_direction = Vector2(0, -1)
        # Don't change visual direction - keep facing left or right

    def move_down(self) -> None:
        """Set velocity to move down."""
        self.velocity.y = self.move_speed
        self.facing_direction = Vector2(0, 1)
        # Don't change visual direction - keep facing left or right

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self.velocity.x = 0

    def stop_vertical(self) -> None:
        """Stop vertical movement."""
        self.velocity.y = 0

    def fire_projectile(self) -> 'Projectile':
        """
        Create a projectile at the player's current position, firing in facing direction.

        Returns:
            New Projectile instance
        """
        from projectile import Projectile

        # Fire from the center of the player
        center_x = self.position.x + self.width // 2
        center_y = self.position.y + self.height // 2

        # Spawn projectile offset from player in the firing direction
        # This prevents immediate collision with nearby zombies
        spawn_offset = 30  # pixels away from player center
        projectile_x = center_x + (self.facing_direction.x * spawn_offset)
        projectile_y = center_y + (self.facing_direction.y * spawn_offset)

        projectile_pos = Vector2(projectile_x, projectile_y)

        print(f"DEBUG: Firing projectile at ({projectile_pos.x}, {projectile_pos.y}) facing {self.facing_direction.x}, {self.facing_direction.y}")

        return Projectile(projectile_pos, self.facing_direction)

    def update(self, delta_time: float) -> None:
        """
        Update player position based on velocity and delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Constrain to map boundaries if map dimensions are set
        if self.map_width is not None and self.map_height is not None:
            self.position.x = max(0, min(self.position.x, self.map_width - self.width))
            self.position.y = max(0, min(self.position.y, self.map_height - self.height))

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the player's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )
