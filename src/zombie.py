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
        self.is_hidden = True  # Hidden until player gets close

        # Zombie dimensions - make them bigger and more visible
        self.width = 40
        self.height = 40

        # Extract test user number for display
        self.display_number = self.extract_test_user_number()

        # Create simple sprite
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a retro 8-bit zombie sprite.

        Returns:
            Pygame surface with the zombie sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Classic zombie green color palette
        ZOMBIE_GREEN = (76, 153, 0)      # Main body
        DARK_GREEN = (51, 102, 0)        # Shadows
        PALE_GREEN = (102, 204, 51)      # Highlights
        BLOOD_RED = (153, 0, 0)          # Eyes/gore
        BLACK = (0, 0, 0)                # Outlines
        GREY = (128, 128, 128)           # Torn clothes

        # Head (top portion)
        head_rect = pygame.Rect(8, 2, 24, 16)
        pygame.draw.rect(sprite, ZOMBIE_GREEN, head_rect)
        pygame.draw.rect(sprite, BLACK, head_rect, 1)  # Outline

        # Body (middle portion)
        body_rect = pygame.Rect(6, 18, 28, 16)
        pygame.draw.rect(sprite, DARK_GREEN, body_rect)
        pygame.draw.rect(sprite, BLACK, body_rect, 1)  # Outline

        # Torn shirt details
        pygame.draw.rect(sprite, GREY, (10, 20, 8, 2))  # Shirt piece
        pygame.draw.rect(sprite, GREY, (22, 20, 8, 2))  # Shirt piece

        # Arms (shambling pose - extended forward)
        # Left arm
        pygame.draw.rect(sprite, ZOMBIE_GREEN, (2, 22, 4, 8))
        pygame.draw.rect(sprite, BLACK, (2, 22, 4, 8), 1)

        # Right arm
        pygame.draw.rect(sprite, ZOMBIE_GREEN, (34, 22, 4, 8))
        pygame.draw.rect(sprite, BLACK, (34, 22, 4, 8), 1)

        # Legs
        pygame.draw.rect(sprite, DARK_GREEN, (12, 34, 6, 6))  # Left leg
        pygame.draw.rect(sprite, DARK_GREEN, (22, 34, 6, 6))  # Right leg
        pygame.draw.rect(sprite, BLACK, (12, 34, 6, 6), 1)    # Left leg outline
        pygame.draw.rect(sprite, BLACK, (22, 34, 6, 6), 1)    # Right leg outline

        # Zombie face details
        # Glowing red eyes
        pygame.draw.rect(sprite, BLOOD_RED, (12, 8, 4, 4))   # Left eye
        pygame.draw.rect(sprite, BLOOD_RED, (24, 8, 4, 4))   # Right eye

        # Eye highlights (make them glow)
        pygame.draw.rect(sprite, (255, 100, 100), (13, 9, 2, 2))  # Left eye highlight
        pygame.draw.rect(sprite, (255, 100, 100), (25, 9, 2, 2))  # Right eye highlight

        # Mouth/jaw
        pygame.draw.rect(sprite, BLACK, (14, 13, 12, 2))  # Mouth line

        # Teeth/gore details
        for i in range(3):
            pygame.draw.rect(sprite, (200, 200, 200), (15 + i*4, 14, 2, 2))  # Teeth

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
