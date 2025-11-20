"""Zombie entity implementation."""

import pygame
import re
import random
from typing import Optional

from models import Vector2


class Zombie:
    """Represents an unused identity as a game entity."""

    def __init__(self, identity_id: str, identity_name: str, position: Vector2, account: str = None, scope: str = None):
        """
        Initialize a zombie.

        Args:
            identity_id: Unique identifier from Sonrai API
            identity_name: Name of the identity (e.g., "test-user-42")
            position: Starting position
            account: AWS account number this zombie belongs to
            scope: Full scope path from API (e.g., "aws/r-ui1v/ou-ui1v-abc123/577945324761")
        """
        self.identity_id = identity_id
        self.identity_name = identity_name
        self.position = position
        self.account = account
        self.scope = scope  # Store scope for quarantine  # AWS account this zombie belongs to
        self.is_quarantining = False
        self.is_hidden = True  # Hidden until player gets close

        # Health system
        self.health = 3
        self.max_health = 3

        # Visual damage feedback
        self.is_flashing = False
        self.flash_timer = 0.0

        # Zombie dimensions - make them bigger and more visible
        self.width = 40
        self.height = 40

        # Extract test user number for display
        self.display_number = self.extract_test_user_number()

        # Randomly select zombie variant (Walking Dead inspired)
        self.variant = random.randint(0, 3)  # 4 different zombie types

        # Create simple sprite
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a retro 8-bit zombie sprite with Walking Dead inspired variety.

        Returns:
            Pygame surface with the zombie sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Create different walker types based on variant
        if self.variant == 0:
            return self._create_fresh_walker(sprite)
        elif self.variant == 1:
            return self._create_decayed_walker(sprite)
        elif self.variant == 2:
            return self._create_burned_walker(sprite)
        else:  # variant == 3
            return self._create_starved_walker(sprite)

    def _create_fresh_walker(self, sprite: pygame.Surface) -> pygame.Surface:
        """Create a fresh walker (recently turned, greenish-grey)."""
        # Color palette - recently turned walker
        SKIN_GREY = (120, 130, 115)      # Greyish-green skin
        DARK_GREY = (80, 90, 75)         # Shadow areas
        BLOOD_RED = (139, 0, 0)          # Fresh blood
        DARK_RED = (100, 0, 0)           # Dark blood
        SHIRT_BLUE = (60, 80, 120)       # Torn blue shirt
        PANTS_BROWN = (70, 60, 50)       # Brown pants
        BLACK = (0, 0, 0)
        WHITE_EYE = (230, 230, 220)      # Milky white eyes

        # Head
        pygame.draw.rect(sprite, SKIN_GREY, (10, 4, 20, 14))
        pygame.draw.rect(sprite, BLACK, (10, 4, 20, 14), 1)
        # Skull shadow
        pygame.draw.rect(sprite, DARK_GREY, (11, 6, 6, 8))

        # Eyes (milky white, walker style)
        pygame.draw.rect(sprite, WHITE_EYE, (13, 9, 4, 3))
        pygame.draw.rect(sprite, WHITE_EYE, (23, 9, 4, 3))

        # Bite wound on neck
        pygame.draw.circle(sprite, DARK_RED, (12, 17), 2)
        pygame.draw.circle(sprite, BLOOD_RED, (13, 17), 1)

        # Body - torn shirt
        pygame.draw.rect(sprite, SHIRT_BLUE, (8, 18, 24, 14))
        pygame.draw.rect(sprite, BLACK, (8, 18, 24, 14), 1)
        # Rips in shirt
        pygame.draw.rect(sprite, SKIN_GREY, (12, 22, 4, 6))  # Exposed skin

        # Blood stains on shirt
        pygame.draw.circle(sprite, DARK_RED, (18, 24), 2)
        pygame.draw.circle(sprite, BLOOD_RED, (24, 28), 3)

        # Arms reaching forward
        pygame.draw.rect(sprite, SKIN_GREY, (4, 20, 4, 10))  # Left arm
        pygame.draw.rect(sprite, BLACK, (4, 20, 4, 10), 1)
        pygame.draw.rect(sprite, SKIN_GREY, (32, 20, 4, 10))  # Right arm
        pygame.draw.rect(sprite, BLACK, (32, 20, 4, 10), 1)

        # Legs
        pygame.draw.rect(sprite, PANTS_BROWN, (12, 32, 6, 8))
        pygame.draw.rect(sprite, PANTS_BROWN, (22, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (12, 32, 6, 8), 1)
        pygame.draw.rect(sprite, BLACK, (22, 32, 6, 8), 1)

        return sprite

    def _create_decayed_walker(self, sprite: pygame.Surface) -> pygame.Surface:
        """Create a decayed walker (heavily rotted, missing pieces)."""
        # Color palette - advanced decay
        ROT_GREEN = (90, 100, 70)        # Rotting green skin
        DARK_ROT = (60, 70, 50)          # Dark decay
        BONE_WHITE = (200, 195, 180)     # Exposed bone
        OLD_BLOOD = (80, 20, 20)         # Old dried blood
        TATTERED_GREY = (90, 90, 85)     # Tattered clothes
        BLACK = (0, 0, 0)
        DEAD_EYE = (40, 40, 35)          # Empty eye sockets

        # Head - partially skeletal
        pygame.draw.rect(sprite, ROT_GREEN, (10, 4, 20, 14))
        pygame.draw.rect(sprite, BLACK, (10, 4, 20, 14), 1)
        # Exposed skull section
        pygame.draw.rect(sprite, BONE_WHITE, (24, 6, 6, 8))
        pygame.draw.rect(sprite, BLACK, (24, 6, 6, 8), 1)

        # Empty eye sockets
        pygame.draw.rect(sprite, DEAD_EYE, (13, 9, 4, 4))
        pygame.draw.rect(sprite, DEAD_EYE, (23, 9, 4, 4))
        # Hollow centers
        pygame.draw.rect(sprite, BLACK, (14, 10, 2, 2))
        pygame.draw.rect(sprite, BLACK, (24, 10, 2, 2))

        # Open jaw/missing lower jaw
        pygame.draw.rect(sprite, BLACK, (12, 14, 10, 4))
        # Visible teeth
        for i in range(4):
            pygame.draw.rect(sprite, BONE_WHITE, (13 + i*2, 14, 2, 2))

        # Body - heavily tattered
        pygame.draw.rect(sprite, TATTERED_GREY, (8, 18, 24, 14))
        pygame.draw.rect(sprite, BLACK, (8, 18, 24, 14), 1)
        # Large tear exposing ribs
        pygame.draw.rect(sprite, DARK_ROT, (14, 20, 8, 10))
        pygame.draw.rect(sprite, BONE_WHITE, (16, 22, 2, 6))  # Rib
        pygame.draw.rect(sprite, BONE_WHITE, (20, 22, 2, 6))  # Rib

        # Old blood stains
        pygame.draw.circle(sprite, OLD_BLOOD, (10, 22), 2)
        pygame.draw.circle(sprite, OLD_BLOOD, (26, 26), 3)

        # Arms - one missing flesh
        pygame.draw.rect(sprite, ROT_GREEN, (4, 20, 4, 10))  # Left arm
        pygame.draw.rect(sprite, BLACK, (4, 20, 4, 10), 1)
        # Right arm - skeletal
        pygame.draw.rect(sprite, BONE_WHITE, (32, 20, 3, 10))
        pygame.draw.rect(sprite, BLACK, (32, 20, 3, 10), 1)

        # Legs - stumbling
        pygame.draw.rect(sprite, DARK_ROT, (12, 32, 6, 8))
        pygame.draw.rect(sprite, DARK_ROT, (22, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (12, 32, 6, 8), 1)
        pygame.draw.rect(sprite, BLACK, (22, 32, 6, 8), 1)

        return sprite

    def _create_burned_walker(self, sprite: pygame.Surface) -> pygame.Surface:
        """Create a burned walker (charred from fire)."""
        # Color palette - fire damage
        CHARRED_BLACK = (30, 30, 30)     # Burned skin
        ASH_GREY = (80, 80, 80)          # Ash and char
        BURNT_RED = (100, 40, 40)        # Burned flesh
        EMBER_ORANGE = (200, 80, 20)     # Hot embers
        BLACK = (0, 0, 0)
        SMOKE_GREY = (120, 120, 115)     # Smoke damaged clothes

        # Head - heavily charred
        pygame.draw.rect(sprite, CHARRED_BLACK, (10, 4, 20, 14))
        pygame.draw.rect(sprite, BLACK, (10, 4, 20, 14), 1)
        # Burnt flesh patches
        pygame.draw.rect(sprite, BURNT_RED, (12, 8, 6, 6))
        pygame.draw.rect(sprite, ASH_GREY, (22, 6, 6, 8))

        # Eyes - still glowing (eerie)
        pygame.draw.rect(sprite, EMBER_ORANGE, (13, 10, 3, 3))
        pygame.draw.rect(sprite, EMBER_ORANGE, (24, 10, 3, 3))

        # Charred mouth
        pygame.draw.rect(sprite, BLACK, (14, 14, 8, 2))

        # Body - burned clothes and skin
        pygame.draw.rect(sprite, SMOKE_GREY, (8, 18, 24, 14))
        pygame.draw.rect(sprite, BLACK, (8, 18, 24, 14), 1)
        # Charred sections
        pygame.draw.rect(sprite, CHARRED_BLACK, (10, 20, 8, 8))
        pygame.draw.rect(sprite, BURNT_RED, (20, 22, 6, 6))
        # Ash marks
        pygame.draw.circle(sprite, ASH_GREY, (16, 26), 2)

        # Arms - unevenly burned
        pygame.draw.rect(sprite, CHARRED_BLACK, (4, 20, 4, 10))
        pygame.draw.rect(sprite, BLACK, (4, 20, 4, 10), 1)
        pygame.draw.rect(sprite, BURNT_RED, (32, 20, 4, 8))
        pygame.draw.rect(sprite, BLACK, (32, 20, 4, 8), 1)

        # Legs - charred
        pygame.draw.rect(sprite, CHARRED_BLACK, (12, 32, 6, 8))
        pygame.draw.rect(sprite, CHARRED_BLACK, (22, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (12, 32, 6, 8), 1)
        pygame.draw.rect(sprite, BLACK, (22, 32, 6, 8), 1)

        return sprite

    def _create_starved_walker(self, sprite: pygame.Surface) -> pygame.Surface:
        """Create a starved walker (emaciated, skeletal)."""
        # Color palette - extreme starvation
        PALE_SKIN = (160, 155, 145)      # Very pale, thin skin
        DARK_HOLLOW = (100, 95, 85)      # Sunken areas
        BONE_WHITE = (200, 195, 180)     # Visible bones
        DRIED_BLOOD = (90, 30, 30)       # Old blood
        RAGGED_BROWN = (80, 70, 60)      # Ragged clothes
        BLACK = (0, 0, 0)
        HOLLOW_GREY = (60, 60, 55)       # Hollow eyes

        # Head - gaunt and skeletal
        pygame.draw.rect(sprite, PALE_SKIN, (12, 4, 16, 14))
        pygame.draw.rect(sprite, BLACK, (12, 4, 16, 14), 1)
        # Skull showing through
        pygame.draw.rect(sprite, BONE_WHITE, (14, 6, 12, 10))
        # Sunken cheeks
        pygame.draw.rect(sprite, DARK_HOLLOW, (13, 12, 4, 4))
        pygame.draw.rect(sprite, DARK_HOLLOW, (23, 12, 4, 4))

        # Hollow, sunken eyes
        pygame.draw.rect(sprite, HOLLOW_GREY, (14, 8, 3, 3))
        pygame.draw.rect(sprite, HOLLOW_GREY, (23, 8, 3, 3))
        pygame.draw.rect(sprite, BLACK, (15, 9, 1, 1))  # Tiny pupil
        pygame.draw.rect(sprite, BLACK, (24, 9, 1, 1))  # Tiny pupil

        # Exposed teeth/jaw
        for i in range(5):
            pygame.draw.rect(sprite, BONE_WHITE, (14 + i*2, 14, 2, 2))

        # Body - extremely thin, ribs visible
        pygame.draw.rect(sprite, RAGGED_BROWN, (10, 18, 20, 14))
        pygame.draw.rect(sprite, BLACK, (10, 18, 20, 14), 1)
        # Visible ribs through torn shirt
        pygame.draw.rect(sprite, PALE_SKIN, (14, 20, 12, 10))
        for i in range(4):
            pygame.draw.rect(sprite, DARK_HOLLOW, (15, 21 + i*2, 10, 1))

        # Skinny arms - bone showing
        pygame.draw.rect(sprite, PALE_SKIN, (5, 20, 3, 10))
        pygame.draw.rect(sprite, BLACK, (5, 20, 3, 10), 1)
        pygame.draw.rect(sprite, PALE_SKIN, (32, 20, 3, 10))
        pygame.draw.rect(sprite, BLACK, (32, 20, 3, 10), 1)

        # Thin legs
        pygame.draw.rect(sprite, DARK_HOLLOW, (14, 32, 4, 8))
        pygame.draw.rect(sprite, DARK_HOLLOW, (24, 32, 4, 8))
        pygame.draw.rect(sprite, BLACK, (14, 32, 4, 8), 1)
        pygame.draw.rect(sprite, BLACK, (24, 32, 4, 8), 1)

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

    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to this zombie.

        Args:
            damage: Amount of damage to apply

        Returns:
            True if the zombie is eliminated (health reaches 0), False otherwise
        """
        self.health = max(0, self.health - damage)
        
        # Trigger flash effect
        self.is_flashing = True
        self.flash_timer = 0.1  # Flash for 0.1 seconds
        
        return self.health == 0

    def update(self, delta_time: float) -> None:
        """
        Update zombie state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update flash effect timer
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False
                self.flash_timer = 0.0
        
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
