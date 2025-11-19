"""Projectile implementation."""

import pygame

from models import Vector2


class Projectile:
    """Represents a fired shot from the player."""

    def __init__(self, position: Vector2, direction: Vector2 = None, damage: int = 1):
        """
        Initialize a projectile.

        Args:
            position: Starting position (typically from player's gun)
            direction: Direction vector (default: right)
            damage: Amount of damage this projectile deals (default: 1)
        """
        self.position = position
        self.damage = damage  # Damage dealt on hit
        
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
        Create a retro raygun energy beam sprite with purple glow.

        Returns:
            Pygame surface with the projectile sprite
        """
        # Make it larger for better visibility
        size = 16
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)

        center = size // 2

        # Outer glow layer (dithered purple) - for retro soft edge effect
        for x in range(size):
            for y in range(size):
                if (x + y) % 2 == 0:  # Checkerboard dithering
                    pygame.draw.circle(sprite, (80, 40, 120), (center, center), 7)

        # Middle bright layer (light purple)
        pygame.draw.circle(sprite, (180, 100, 255), (center, center), 5)

        # Inner glow (cyan/white - energy core)
        pygame.draw.circle(sprite, (100, 200, 255), (center, center), 3)

        # Core white hot center
        pygame.draw.circle(sprite, (255, 255, 255), (center, center), 2)

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

    def hits_wall(self, game_map: 'GameMap') -> bool:
        """
        Check if the projectile has hit a wall tile.

        Args:
            game_map: The game map to check wall collisions against

        Returns:
            True if projectile hit a wall, False otherwise
        """
        if not game_map:
            return False

        # Convert projectile position to tile coordinates
        tile_x = int(self.position.x // game_map.tile_size)
        tile_y = int(self.position.y // game_map.tile_size)

        # Check if tile is within map bounds
        if 0 <= tile_x < game_map.tiles_wide and 0 <= tile_y < game_map.tiles_high:
            # Check if this tile is a wall (non-zero value means wall)
            return game_map.tile_map[tile_y][tile_x] != 0

        return False
