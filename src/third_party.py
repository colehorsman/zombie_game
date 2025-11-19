"""Third party entity - represents external access to AWS accounts."""

import pygame
import random
from typing import Optional

from models import Vector2


class ThirdParty:
    """Represents a 3rd party with access to AWS accounts (e.g., Cloudflare, Datadog)."""

    def __init__(self, name: str, account: str, position: Vector2, third_party_id: str = None):
        """
        Initialize a third party entity.

        Args:
            name: Name of the 3rd party (e.g., "Cloudflare", "Datadog")
            account: AWS account number this 3rd party has access to
            position: Starting position
            third_party_id: UUID of the 3rd party from Sonrai API
        """
        self.name = name
        self.account = account
        self.position = position
        self.velocity = Vector2(0, 0)
        self.third_party_id = third_party_id  # UUID for API calls

        # Third parties are worth more points
        self.point_value = 50  # vs zombies at 10

        # Entity dimensions
        self.width = 40
        self.height = 40

        # Movement - 3rd parties patrol hallways
        self.move_speed = 80.0  # Slower than player
        self.patrol_direction = random.choice([-1, 1])  # Left or right
        self.patrol_timer = 0.0
        self.patrol_change_interval = 3.0  # Change direction every 3 seconds

        # Interaction state
        self.is_hidden = False  # 3rd parties are always visible
        self.is_interacted = False  # Has player made a decision on this?
        self.is_allowed = None  # True if allowed, False if denied, None if not decided
        self.is_blocking = False  # True if being blocked via API

        # Visual
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a 3rd party sprite - looks different from zombies (more professional/corporate).

        Returns:
            Pygame surface with the 3rd party sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Corporate professional color palette (not zombie-like)
        SUIT_BLUE = (40, 60, 100)        # Dark blue suit
        SUIT_LIGHT = (60, 90, 140)       # Light blue
        TIE_RED = (180, 40, 40)          # Red tie
        SKIN = (220, 180, 140)           # Skin tone
        BRIEFCASE_BROWN = (100, 70, 40)  # Brown briefcase
        GOLD = (255, 215, 0)             # Gold watch/details
        BLACK = (0, 0, 0)                # Outlines
        WHITE = (255, 255, 255)          # Shirt

        # Head
        head_rect = pygame.Rect(12, 4, 16, 12)
        pygame.draw.rect(sprite, SKIN, head_rect)
        pygame.draw.rect(sprite, BLACK, head_rect, 1)

        # Professional haircut
        pygame.draw.rect(sprite, BLACK, (12, 4, 16, 4))  # Hair

        # Eyes (professional look)
        pygame.draw.rect(sprite, BLACK, (15, 10, 2, 2))  # Left eye
        pygame.draw.rect(sprite, BLACK, (23, 10, 2, 2))  # Right eye

        # Smile (friendly but corporate)
        pygame.draw.line(sprite, BLACK, (16, 13), (24, 13), 1)

        # Body - business suit
        suit_rect = pygame.Rect(10, 16, 20, 16)
        pygame.draw.rect(sprite, SUIT_BLUE, suit_rect)
        pygame.draw.rect(sprite, BLACK, suit_rect, 1)

        # White shirt collar
        pygame.draw.rect(sprite, WHITE, (14, 16, 12, 3))

        # Red tie
        pygame.draw.rect(sprite, TIE_RED, (18, 19, 4, 10))
        pygame.draw.rect(sprite, BLACK, (18, 19, 4, 10), 1)

        # Suit highlights
        pygame.draw.line(sprite, SUIT_LIGHT, (11, 18), (11, 30), 2)

        # Briefcase in left hand
        briefcase = pygame.Rect(4, 24, 8, 10)
        pygame.draw.rect(sprite, BRIEFCASE_BROWN, briefcase)
        pygame.draw.rect(sprite, BLACK, briefcase, 1)
        # Briefcase handle
        pygame.draw.rect(sprite, GOLD, (6, 26, 4, 2))

        # Watch on right wrist (corporate status symbol)
        pygame.draw.rect(sprite, GOLD, (30, 28, 4, 3))

        # Legs - suit pants
        # Left leg
        pygame.draw.rect(sprite, SUIT_BLUE, (12, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (12, 32, 6, 8), 1)

        # Right leg
        pygame.draw.rect(sprite, SUIT_BLUE, (22, 32, 6, 8))
        pygame.draw.rect(sprite, BLACK, (22, 32, 6, 8), 1)

        return sprite

    def update(self, delta_time: float, game_map: Optional['GameMap'] = None) -> None:
        """
        Update 3rd party movement (pace back and forth along wall).

        Args:
            delta_time: Time elapsed since last frame
            game_map: Game map for collision detection
        """
        # If we have patrol bounds, pace back and forth along the wall
        if hasattr(self, 'patrol_axis') and hasattr(self, 'patrol_min') and hasattr(self, 'patrol_max'):
            # Patrol back and forth along assigned wall segment
            self.patrol_timer += delta_time

            if self.patrol_axis == 'horizontal':
                # Move horizontally (top or bottom wall)
                self.velocity.x = self.move_speed * self.patrol_direction
                self.velocity.y = 0

                # Check if we've reached the end of patrol range
                if self.patrol_direction > 0:  # Moving right
                    if self.position.x >= self.patrol_max - self.width:
                        self.patrol_direction = -1  # Reverse to left
                else:  # Moving left
                    if self.position.x <= self.patrol_min:
                        self.patrol_direction = 1  # Reverse to right

            else:  # vertical
                # Move vertically (left or right wall)
                self.velocity.x = 0
                self.velocity.y = self.move_speed * self.patrol_direction

                # Check if we've reached the end of patrol range
                if self.patrol_direction > 0:  # Moving down
                    if self.position.y >= self.patrol_max - self.height:
                        self.patrol_direction = -1  # Reverse to up
                else:  # Moving up
                    if self.position.y <= self.patrol_min:
                        self.patrol_direction = 1  # Reverse to down

        else:
            # Fallback to old patrol behavior if no patrol bounds set
            self.patrol_timer += delta_time
            if self.patrol_timer >= self.patrol_change_interval:
                self.patrol_timer = 0.0
                self.patrol_direction *= -1

            self.velocity.x = self.move_speed * self.patrol_direction
            self.velocity.y = 0

        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Basic boundary check if map provided
        if game_map:
            # Keep in map bounds
            self.position.x = max(0, min(self.position.x, game_map.map_width - self.width))
            self.position.y = max(0, min(self.position.y, game_map.map_height - self.height))

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the 3rd party's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )

    def interact(self) -> str:
        """
        Trigger interaction with this 3rd party (show dialog).

        Returns:
            Dialog message to display
        """
        return f"This 3rd party ({self.name}) has access to account {self.account}.\nWould you like to ALLOW or DENY this access?"

    def allow_access(self) -> int:
        """
        Player chose to allow this 3rd party access.

        Returns:
            Points awarded (negative for allowing external access)
        """
        self.is_interacted = True
        self.is_allowed = True
        return -10  # Penalty for allowing external access

    def deny_access(self) -> int:
        """
        Player chose to deny this 3rd party access.

        Returns:
            Points awarded (positive for securing the account)
        """
        self.is_interacted = True
        self.is_allowed = False
        return self.point_value  # 50 points for denying/securing
