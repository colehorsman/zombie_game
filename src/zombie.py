"""Zombie entity implementation."""

import pygame
import re
from typing import Optional

from models import Vector2


class Zombie:
    """Represents an unused identity as a game entity."""

    def __init__(self, identity_id: str, identity_name: str, position: Vector2):
        """
        Initialize a zombie.

        Args:
            identity_id: Unique identifier from Sonrai API
            identity_name: Name of the identity (e.g., "test-user-42")
            position: Starting position
        """
        self.identity_id = identity_id
        self.identity_name = identity_name
        self.position = position
        self.is_quarantining = False

        # Zombie dimensions - make them bigger and more visible
        self.width = 40
        self.height = 40

        # Extract test user number for display
        self.display_number = self.extract_test_user_number()

        # Create simple sprite
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a simple programmatic sprite for the zombie.

        Returns:
            Pygame surface with the zombie sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Bright green rectangle body - make it very visible
        pygame.draw.rect(sprite, (0, 255, 0), (0, 0, self.width, self.height))
        
        # Black border for contrast
        pygame.draw.rect(sprite, (0, 0, 0), (0, 0, self.width, self.height), 2)

        # Simple face details
        # Eyes (red) - bigger
        pygame.draw.circle(sprite, (255, 0, 0), (12, 12), 4)
        pygame.draw.circle(sprite, (255, 0, 0), (28, 12), 4)

        # Mouth (dark line)
        pygame.draw.line(sprite, (0, 0, 0), (10, 28), (30, 28), 3)

        return sprite

    def extract_test_user_number(self) -> Optional[int]:
        """
        Extract the numeric identifier from identity names like "test-user-42" or "unused-identity-42".

        Returns:
            The numeric portion if pattern matches, None otherwise
        """
        # Try test-user pattern
        match = re.match(r'test-user-(\d+)', self.identity_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Try unused-identity pattern
        match = re.match(r'unused-identity-(\d+)', self.identity_name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None

    def mark_for_quarantine(self) -> None:
        """Mark this zombie as having a pending quarantine request."""
        self.is_quarantining = True

    def update(self, delta_time: float) -> None:
        """
        Update zombie state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Zombies are stationary in this version
        # Could add movement logic here if needed
        pass

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the zombie's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )
