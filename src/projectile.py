"""Projectile implementation."""

import pygame

from models import Vector2


class Projectile:
    """Represents a fired shot from the player."""

    def __init__(self, position: Vector2):
        """
        Initialize a projectile.

        Args:
            position: Starting position (typically from player's gun)
        """
        self.position = position
        self.velocity = Vector2(400, 0)  # Move right at 400 pixels/second

        # Projectile dimensions
        self.radius = 4

        # Create simple sprite
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a simple programmatic sprite for the projectile.

        Returns:
            Pygame surface with the projectile sprite
        """
        size = self.radius * 2
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)

        # Yellow circle
        pygame.draw.circle(sprite, (255, 255, 0), (self.radius, self.radius), self.radius)

        return sprite

    def update(self, delta_time: float) -> None:
        """
        Update projectile position based on velocity.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the projectile's bounds
        """
        return pygame.Rect(
            int(self.position.x - self.radius),
            int(self.position.y - self.radius),
            self.radius * 2,
            self.radius * 2
        )

    def is_off_screen(self, screen_width: int, screen_height: int) -> bool:
        """
        Check if the projectile has moved off screen.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen

        Returns:
            True if off screen, False otherwise
        """
        return (
            self.position.x < -self.radius or
            self.position.x > screen_width + self.radius or
            self.position.y < -self.radius or
            self.position.y > screen_height + self.radius
        )
