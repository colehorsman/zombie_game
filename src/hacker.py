"""Hacker AI character for service protection quests."""

import pygame
from models import Vector2


# Physics constants
GRAVITY = 500.0  # Pixels per second squared
HACKER_SPEED = 130.0  # Pixels per second (slightly slower than before for fair race)


class Hacker:
    """AI character that races to compromise AWS services."""

    def __init__(self, spawn_position: Vector2, target_position: Vector2):
        """
        Initialize hacker character.

        Args:
            spawn_position: Starting position (on ground for side-by-side race)
            target_position: Service icon position to race toward
        """
        self.position = Vector2(spawn_position.x, spawn_position.y)
        self.velocity = Vector2(0.0, 0.0)
        self.target_position = target_position
        self.speed = HACKER_SPEED
        # Start grounded if spawned near ground level
        self.grounded = spawn_position.y > 700  # If y > 700, assume on ground

        # Visual properties
        self.width = 24
        self.height = 32

    def update(self, delta_time: float, game_map) -> None:
        """
        Update hacker physics and AI movement.

        Args:
            delta_time: Time since last frame in seconds
            game_map: Game map for collision detection
        """
        # Apply gravity if not grounded
        if not self.grounded:
            self.velocity.y += GRAVITY * delta_time

            # Apply vertical velocity
            self.position.y += self.velocity.y * delta_time

            # Check ground collision (simple ground check at y=832)
            ground_y = 832
            if self.position.y + self.height >= ground_y:
                self.position.y = ground_y - self.height
                self.velocity.y = 0
                self.grounded = True

        # Move horizontally toward target if grounded
        if self.grounded:
            # Calculate direction to target
            dx = self.target_position.x - self.position.x

            # Move toward target if not there yet
            if abs(dx) > 5:  # 5 pixel tolerance
                direction = 1 if dx > 0 else -1
                self.velocity.x = direction * self.speed
                self.position.x += self.velocity.x * delta_time
            else:
                # Reached target
                self.velocity.x = 0

    def render(self, surface: pygame.Surface, camera_offset: Vector2) -> None:
        """
        Render hacker character (black hoodie silhouette style).

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for world-to-screen conversion
        """
        # Calculate screen position
        screen_x = int(self.position.x - camera_offset.x)
        screen_y = int(self.position.y - camera_offset.y)

        # All-black silhouette body (24x32)
        body_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, (0, 0, 0), body_rect)

        # Hoodie top (wider at top for hood shape)
        hoodie_top = pygame.Rect(screen_x - 3, screen_y, 30, 12)
        pygame.draw.rect(surface, (0, 0, 0), hoodie_top)

        # Hoodie shadow/depth (very dark gray for subtle depth)
        hoodie_shadow = pygame.Rect(screen_x - 2, screen_y + 2, 28, 10)
        pygame.draw.rect(surface, (15, 15, 15), hoodie_shadow)

        # Face area (completely black - mysterious)
        face_rect = pygame.Rect(screen_x + 6, screen_y + 6, 12, 8)
        pygame.draw.rect(surface, (0, 0, 0), face_rect)

        # Small glowing red eyes (2x2 each) - only visible feature
        left_eye = pygame.Rect(screen_x + 8, screen_y + 9, 2, 2)
        right_eye = pygame.Rect(screen_x + 14, screen_y + 9, 2, 2)
        pygame.draw.rect(surface, (255, 0, 0), left_eye)
        pygame.draw.rect(surface, (255, 0, 0), right_eye)

        # Optional: Add thin white outline for silhouette effect
        pygame.draw.rect(surface, (40, 40, 40), body_rect, 1)
        pygame.draw.rect(surface, (40, 40, 40), hoodie_top, 1)

    def get_bounds(self) -> pygame.Rect:
        """
        Get bounding box for collision detection.

        Returns:
            Rectangle representing hacker's position and size
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )
