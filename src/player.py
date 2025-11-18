"""Player character implementation."""

import pygame
from typing import Optional

from models import Vector2


class Player:
    """Represents the controllable Mega Man-style character."""

    def __init__(self, position: Vector2, screen_width: int, screen_height: int):
        """
        Initialize the player.

        Args:
            position: Starting position
            screen_width: Width of the game screen for boundary checking
            screen_height: Height of the game screen for boundary checking
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Player dimensions
        self.width = 32
        self.height = 32

        # Movement speed (pixels per second)
        self.move_speed = 200.0

        # Create simple sprite
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a simple programmatic sprite for the player.

        Returns:
            Pygame surface with the player sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Blue rectangle body
        pygame.draw.rect(sprite, (50, 100, 255), (0, 0, self.width, self.height))

        # Gun protrusion (small rectangle on the right)
        pygame.draw.rect(sprite, (100, 150, 255), (self.width - 5, 10, 8, 5))

        # Simple face details
        # Eyes
        pygame.draw.circle(sprite, (255, 255, 255), (10, 12), 3)
        pygame.draw.circle(sprite, (255, 255, 255), (22, 12), 3)
        pygame.draw.circle(sprite, (0, 0, 0), (10, 12), 1)
        pygame.draw.circle(sprite, (0, 0, 0), (22, 12), 1)

        return sprite

    def move_left(self) -> None:
        """Set velocity to move left."""
        self.velocity.x = -self.move_speed

    def move_right(self) -> None:
        """Set velocity to move right."""
        self.velocity.x = self.move_speed

    def move_up(self) -> None:
        """Set velocity to move up."""
        self.velocity.y = -self.move_speed

    def move_down(self) -> None:
        """Set velocity to move down."""
        self.velocity.y = self.move_speed

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self.velocity.x = 0

    def stop_vertical(self) -> None:
        """Stop vertical movement."""
        self.velocity.y = 0

    def fire_projectile(self) -> 'Projectile':
        """
        Create a projectile at the player's current position.

        Returns:
            New Projectile instance
        """
        from projectile import Projectile

        # Fire from the gun position (right side of player)
        projectile_pos = Vector2(
            self.position.x + self.width,
            self.position.y + self.height // 2
        )
        return Projectile(projectile_pos)

    def update(self, delta_time: float) -> None:
        """
        Update player position based on velocity and delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Constrain to screen boundaries
        self.position.x = max(0, min(self.position.x, self.screen_width - self.width))
        self.position.y = max(0, min(self.position.y, self.screen_height - self.height))

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
