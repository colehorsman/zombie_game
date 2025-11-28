"""Collectible items - Mario-style question blocks for data caches."""

import pygame
from typing import Optional
from models import Vector2


class Collectible:
    """Represents a Mario-style question block containing data caches."""

    def __init__(self, position: Vector2, data_value: int = 10):
        """
        Initialize a collectible.

        Args:
            position: Position in world coordinates
            data_value: Points/value when collected
        """
        self.position = position
        self.data_value = data_value
        self.collected = False

        # Block dimensions (Mario block size)
        self.width = 16
        self.height = 16

        # Animation
        self.animation_timer = 0.0
        self.bounce_offset = 0

        # Create block sprite
        self.sprite = self._create_question_block()

    def _create_question_block(self) -> pygame.Surface:
        """Create a Mario-style question block with purple/AWS theme."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Purple question block colors
        BLOCK_PURPLE = (120, 80, 160)  # Main block color
        BLOCK_LIGHT = (160, 120, 200)  # Highlights
        BLOCK_DARK = (80, 50, 110)  # Shadows
        QUESTION_COLOR = (255, 153, 0)  # AWS Orange question mark
        BLACK = (0, 0, 0)

        # Main block body
        pygame.draw.rect(sprite, BLOCK_PURPLE, (0, 0, self.width, self.height))

        # Top and left highlights (3D effect)
        pygame.draw.line(sprite, BLOCK_LIGHT, (0, 0), (self.width - 1, 0), 2)
        pygame.draw.line(sprite, BLOCK_LIGHT, (0, 0), (0, self.height - 1), 2)

        # Bottom and right shadows
        pygame.draw.line(
            sprite,
            BLOCK_DARK,
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
            2,
        )
        pygame.draw.line(
            sprite,
            BLOCK_DARK,
            (self.width - 1, 0),
            (self.width - 1, self.height - 1),
            2,
        )

        # Question mark (simplified pixel art)
        # Top curve of ?
        pygame.draw.rect(sprite, QUESTION_COLOR, (6, 3, 4, 2))
        pygame.draw.rect(sprite, QUESTION_COLOR, (9, 5, 2, 2))
        # Middle stem of ?
        pygame.draw.rect(sprite, QUESTION_COLOR, (7, 7, 2, 2))
        # Dot of ?
        pygame.draw.rect(sprite, QUESTION_COLOR, (7, 10, 2, 2))

        # Black outline
        pygame.draw.rect(sprite, BLACK, (0, 0, self.width, self.height), 1)

        return sprite

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the block's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y + self.bounce_offset),
            self.width,
            self.height,
        )

    def check_collision(self, player_bounds: pygame.Rect) -> bool:
        """
        Check if player is colliding with the collectible.

        Args:
            player_bounds: Player's bounding rectangle

        Returns:
            True if player is touching the collectible
        """
        if self.collected:
            return False
        return self.get_bounds().colliderect(player_bounds)

    def collect(self) -> int:
        """
        Collect this item.

        Returns:
            The data value of this collectible
        """
        if not self.collected:
            self.collected = True
            return self.data_value
        return 0

    def update(self, delta_time: float) -> None:
        """
        Update collectible animation.

        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.collected:
            # Gentle bobbing animation like Mario coins
            self.animation_timer += delta_time * 3  # Speed of animation
            self.bounce_offset = int(
                2
                * (
                    0.5
                    + 0.5
                    * pygame.math.Vector2(0, 1).rotate(self.animation_timer * 180).y
                )
            )

    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render the collectible to the screen.

        Args:
            screen: Pygame surface to render to
            camera_x: Camera x position
            camera_y: Camera y position
        """
        if not self.collected:
            screen_x = int(self.position.x - camera_x)
            screen_y = int(self.position.y - camera_y + self.bounce_offset)

            screen.blit(self.sprite, (screen_x, screen_y))
