"""Door/Pipe system for transitioning between AWS account rooms."""

import pygame
from typing import Optional
from models import Vector2


class Door:
    """Represents a Mario-style pipe door that connects rooms."""

    def __init__(self, position: Vector2, direction: str = "vertical", destination_room: Optional[int] = None, destination_room_name: Optional[str] = None):
        """
        Initialize a door/pipe.

        Args:
            position: Door position in world coordinates
            direction: "vertical" or "horizontal" pipe orientation
            destination_room: Index of the room this door leads to
            destination_room_name: Friendly name of the destination room (e.g., "MyHealth Sandbox")
        """
        self.position = position
        self.direction = direction
        self.destination_room = destination_room
        self.destination_room_name = destination_room_name

        # Door dimensions (Mario pipe size)
        if direction == "vertical":
            self.width = 32
            self.height = 48
        else:  # horizontal
            self.width = 48
            self.height = 32

        # Animation state
        self.is_open = False
        self.animation_timer = 0.0
        
        # Completion state
        self.is_completed = False  # True if the level this door leads to has been completed

        # Create door sprite
        self.sprite = self._create_pipe_sprite()

    def _create_pipe_sprite(self) -> pygame.Surface:
        """Create a Mario-style pipe sprite with purple theme."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Purple pipe colors (matching our theme)
        PIPE_PURPLE = (100, 70, 140)      # Main pipe color
        PIPE_DARK = (60, 40, 90)          # Shadow
        PIPE_LIGHT = (140, 110, 180)      # Highlight
        PIPE_OPENING = (40, 25, 60)       # Dark opening
        BLACK = (0, 0, 0)

        if self.direction == "vertical":
            # Vertical pipe (like Mario warp pipes)
            # Pipe opening (top oval)
            pygame.draw.ellipse(sprite, PIPE_OPENING, (2, 0, self.width - 4, 16))
            pygame.draw.ellipse(sprite, BLACK, (2, 0, self.width - 4, 16), 2)

            # Pipe lip (rim)
            pygame.draw.ellipse(sprite, PIPE_LIGHT, (0, 2, self.width, 14))
            pygame.draw.ellipse(sprite, BLACK, (0, 2, self.width, 14), 2)

            # Pipe body
            body_rect = pygame.Rect(4, 12, self.width - 8, self.height - 12)
            pygame.draw.rect(sprite, PIPE_PURPLE, body_rect)

            # Highlights and shadows on body
            pygame.draw.line(sprite, PIPE_LIGHT, (6, 14), (6, self.height - 1), 3)
            pygame.draw.line(sprite, PIPE_DARK, (self.width - 7, 14), (self.width - 7, self.height - 1), 3)

            # Outline
            pygame.draw.rect(sprite, BLACK, (4, 12, self.width - 8, self.height - 12), 2)

        else:  # horizontal
            # Horizontal pipe (side-facing)
            # Pipe opening (left oval)
            pygame.draw.ellipse(sprite, PIPE_OPENING, (0, 2, 16, self.height - 4))
            pygame.draw.ellipse(sprite, BLACK, (0, 2, 16, self.height - 4), 2)

            # Pipe lip (rim)
            pygame.draw.ellipse(sprite, PIPE_LIGHT, (2, 0, 14, self.height))
            pygame.draw.ellipse(sprite, BLACK, (2, 0, 14, self.height), 2)

            # Pipe body
            body_rect = pygame.Rect(12, 4, self.width - 12, self.height - 8)
            pygame.draw.rect(sprite, PIPE_PURPLE, body_rect)

            # Highlights and shadows on body
            pygame.draw.line(sprite, PIPE_LIGHT, (14, 6), (self.width - 1, 6), 3)
            pygame.draw.line(sprite, PIPE_DARK, (14, self.height - 7), (self.width - 1, self.height - 7), 3)

            # Outline
            pygame.draw.rect(sprite, BLACK, (12, 4, self.width - 12, self.height - 8), 2)

        return sprite

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the door's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )

    def check_collision(self, player_bounds: pygame.Rect) -> bool:
        """
        Check if player is colliding with the door.

        Args:
            player_bounds: Player's bounding rectangle

        Returns:
            True if player is touching the door
        """
        return self.get_bounds().colliderect(player_bounds)

    def update(self, delta_time: float) -> None:
        """
        Update door animation.

        Args:
            delta_time: Time elapsed since last frame
        """
        if self.is_open:
            self.animation_timer += delta_time
        else:
            self.animation_timer = 0.0

    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render the door/pipe to the screen.

        Args:
            screen: Pygame surface to render to
            camera_x: Camera x position
            camera_y: Camera y position
        """
        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y)

        screen.blit(self.sprite, (screen_x, screen_y))

        # Optional: Add label above door showing destination
        if self.destination_room is not None:
            try:
                font = pygame.font.Font(None, 16)
                # Use friendly name if available, otherwise fallback to "Room X"
                if self.destination_room_name:
                    label = self.destination_room_name
                else:
                    label = f"Room {self.destination_room + 1}"
                text = font.render(label, True, (255, 153, 0))  # AWS Orange
                text_rect = text.get_rect(center=(screen_x + self.width // 2, screen_y - 8))
                screen.blit(text, text_rect)
            except:
                pass
