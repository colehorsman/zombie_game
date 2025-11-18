"""Projectile implementation."""

import pygame

from models import Vector2


class Projectile:
    """Represents a fired shot from the player."""

    def __init__(self, position: Vector2, direction: Vector2 = None):
        """
        Initialize a projectile.

        Args:
            position: Starting position (typically from player's gun)
            direction: Direction vector (default: right)
        """
        self.position = position
        # Default to moving right if no direction specified
        if direction is None:
            self.velocity = Vector2(400, 0)
        else:
            # Normalize direction and set speed to 400 pixels/second
            speed = 400
            length = (direction.x ** 2 + direction.y ** 2) ** 0.5
            if length > 0:
                self.velocity = Vector2(
                    (direction.x / length) * speed,
                    (direction.y / length) * speed
                )
            else:
                self.velocity = Vector2(400, 0)  # Fallback to right

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

        # Black circle for visibility on light background
        pygame.draw.circle(sprite, (0, 0, 0), (self.radius, self.radius), self.radius)

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

    def is_off_screen(self, screen_width: int, screen_height: int, map_mode: bool = False) -> bool:
        """
        Check if the projectile has moved off screen or off the map.

        Args:
            screen_width: Width of the game screen/map
            screen_height: Height of the game screen/map
            map_mode: If True, use larger bounds for map mode

        Returns:
            True if off screen/map, False otherwise
        """
        # In map mode, give projectiles much more range before removing them
        if map_mode:
            margin = 100
        else:
            margin = self.radius

        return (
            self.position.x < -margin or
            self.position.x > screen_width + margin or
            self.position.y < -margin or
            self.position.y > screen_height + margin
        )
