"""Player character implementation."""

import pygame
from typing import Optional

from models import Vector2


class Player:
    """Represents the controllable Mega Man-style character."""

    def __init__(self, position: Vector2, map_width: Optional[int] = None, map_height: Optional[int] = None, game_map: Optional['GameMap'] = None):
        """
        Initialize the player.

        Args:
            position: Starting position
            map_width: Width of the map for boundary checking (None for screen-based)
            map_height: Height of the map for boundary checking (None for screen-based)
            game_map: GameMap instance for collision detection (None to disable)
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.map_width = map_width
        self.map_height = map_height
        self.game_map = game_map

        # Player dimensions (match zombie size)
        self.width = 40
        self.height = 40

        # Movement speed (pixels per second) - realistic walking speed
        self.move_speed = 120.0  # Slower for realistic navigation

        # Facing direction for firing projectiles
        self.facing_direction = Vector2(1, 0)  # Start facing right

        # Visual direction (only left/right for sprite)
        self.visual_direction = 1  # 1 = right, -1 = left

        # Create base sprite (facing right)
        self.base_sprite = self._create_sprite()
        self.sprite = self.base_sprite.copy()  # Current displayed sprite

    def _create_sprite(self) -> pygame.Surface:
        """
        Create a retro 8-bit survivor character inspired by The Walking Dead.

        Returns:
            Pygame surface with the player sprite
        """
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # re:Invent survivor color palette
        HAIR_BROWN = (80, 50, 30)        # Dark brown hair
        SKIN = (220, 180, 140)           # Skin tone
        DARK_SKIN = (180, 140, 100)      # Shadow on skin
        PURPLE = (120, 60, 180)          # re:Invent purple shirt
        DARK_PURPLE = (80, 40, 120)      # Purple shadows
        LIGHT_PURPLE = (160, 100, 220)   # Purple highlights
        CAP_PURPLE = (100, 50, 160)      # Purple baseball cap
        CAP_DARK = (70, 35, 110)         # Cap shadows
        PANTS_BLACK = (40, 40, 40)       # Black pants
        DARK_PANTS = (25, 25, 25)        # Pants shadows
        BOOTS_BLACK = (30, 30, 30)       # Black boots
        BACKPACK_GREY = (90, 90, 80)     # Grey backpack
        DARK_GREY = (60, 60, 55)         # Backpack shadows
        GUN_METAL = (100, 100, 100)      # Metallic gun
        DARK_METAL = (60, 60, 60)        # Gun shadows
        BLACK = (0, 0, 0)                # Outlines
        RED = (150, 30, 30)              # Blood stains

        # Baseball cap
        # Cap crown (rounded top)
        cap_crown = pygame.Rect(11, 2, 18, 8)
        pygame.draw.rect(sprite, CAP_PURPLE, cap_crown)
        pygame.draw.rect(sprite, BLACK, cap_crown, 1)

        # Cap bill/visor (extends forward)
        cap_bill = pygame.Rect(20, 9, 12, 3)
        pygame.draw.rect(sprite, CAP_PURPLE, cap_bill)
        pygame.draw.rect(sprite, BLACK, cap_bill, 1)
        # Bill shadow underneath
        pygame.draw.line(sprite, CAP_DARK, (20, 11), (31, 11))

        # Cap details/shading
        pygame.draw.rect(sprite, CAP_DARK, (12, 3, 16, 3))  # Top shadow
        pygame.draw.circle(sprite, LIGHT_PURPLE, (20, 5), 2)  # Logo/emblem

        # Hair peeking out from under cap
        pygame.draw.rect(sprite, HAIR_BROWN, (10, 8, 4, 3))  # Left side
        pygame.draw.rect(sprite, HAIR_BROWN, (26, 8, 4, 3))  # Right side

        # Face (adjusted to be under cap)
        face_rect = pygame.Rect(14, 10, 12, 8)
        pygame.draw.rect(sprite, SKIN, face_rect)
        pygame.draw.rect(sprite, BLACK, face_rect, 1)

        # Eyes (determined look)
        pygame.draw.rect(sprite, BLACK, (16, 13, 2, 2))  # Left eye
        pygame.draw.rect(sprite, BLACK, (22, 13, 2, 2))  # Right eye

        # Facial shadow (beard stubble)
        pygame.draw.rect(sprite, DARK_SKIN, (15, 16, 10, 2))

        # Backpack (behind body)
        backpack_rect = pygame.Rect(6, 18, 12, 14)
        pygame.draw.rect(sprite, BACKPACK_GREY, backpack_rect)
        pygame.draw.rect(sprite, BLACK, backpack_rect, 1)
        # Backpack straps
        pygame.draw.rect(sprite, DARK_GREY, (8, 20, 2, 10))
        pygame.draw.rect(sprite, DARK_GREY, (14, 20, 2, 10))
        # Backpack pocket
        pygame.draw.rect(sprite, DARK_GREY, (9, 22, 6, 4))

        # Body/torso - purple re:Invent shirt
        body_rect = pygame.Rect(10, 16, 16, 14)
        pygame.draw.rect(sprite, PURPLE, body_rect)
        pygame.draw.rect(sprite, BLACK, body_rect, 1)

        # Shirt details/highlights
        pygame.draw.rect(sprite, LIGHT_PURPLE, (12, 18, 12, 4))  # Chest highlight
        pygame.draw.rect(sprite, DARK_PURPLE, (14, 24, 8, 4))     # Shadow area

        # Collar detail
        pygame.draw.rect(sprite, DARK_PURPLE, (14, 16, 8, 2))

        # Blood stain on shirt (survivor has been through combat)
        pygame.draw.circle(sprite, RED, (22, 23), 2)

        # Left arm - purple sleeve
        pygame.draw.rect(sprite, PURPLE, (5, 20, 5, 12))
        pygame.draw.rect(sprite, BLACK, (5, 20, 5, 12), 1)
        # Sleeve shadow
        pygame.draw.rect(sprite, DARK_PURPLE, (6, 21, 2, 10))
        # Hand
        pygame.draw.rect(sprite, SKIN, (4, 28, 4, 4))

        # Right arm - purple sleeve with raygun/arm cannon (Mega Man style)
        # Upper arm
        pygame.draw.rect(sprite, PURPLE, (26, 20, 5, 8))
        pygame.draw.rect(sprite, BLACK, (26, 20, 5, 8), 1)

        # Arm cannon/raygun (integrated with arm - Mega Man style)
        # Cannon base (cylindrical shape)
        cannon_base = pygame.Rect(29, 22, 6, 6)
        pygame.draw.rect(sprite, GUN_METAL, cannon_base)
        pygame.draw.rect(sprite, BLACK, cannon_base, 1)

        # Cannon highlights (top edge)
        pygame.draw.line(sprite, (150, 150, 150), (29, 22), (34, 22), 2)

        # Cannon barrel (extending forward)
        barrel = pygame.Rect(34, 23, 4, 4)
        pygame.draw.rect(sprite, DARK_METAL, barrel)
        pygame.draw.rect(sprite, BLACK, barrel, 1)

        # Energy core (glowing cyan center - classic raygun look)
        pygame.draw.circle(sprite, (100, 200, 255), (32, 25), 2)  # Cyan glow

        # Muzzle opening (dark)
        pygame.draw.rect(sprite, (40, 40, 60), (36, 24, 2, 2))

        # Legs/pants - black pants
        # Left leg
        pygame.draw.rect(sprite, PANTS_BLACK, (11, 30, 6, 10))
        pygame.draw.rect(sprite, BLACK, (11, 30, 6, 10), 1)
        # Pants shadow
        pygame.draw.rect(sprite, DARK_PANTS, (12, 31, 2, 8))

        # Right leg
        pygame.draw.rect(sprite, PANTS_BLACK, (19, 30, 6, 10))
        pygame.draw.rect(sprite, BLACK, (19, 30, 6, 10), 1)
        # Pants shadow
        pygame.draw.rect(sprite, DARK_PANTS, (20, 31, 2, 8))

        # Boots
        # Left boot
        pygame.draw.rect(sprite, BOOTS_BLACK, (11, 38, 6, 2))
        pygame.draw.rect(sprite, BLACK, (11, 38, 6, 2), 1)
        # Right boot
        pygame.draw.rect(sprite, BOOTS_BLACK, (19, 38, 6, 2))
        pygame.draw.rect(sprite, BLACK, (19, 38, 6, 2), 1)

        return sprite

    def _update_sprite_rotation(self) -> None:
        """Update the sprite to match the current visual direction (only left/right)."""
        if self.visual_direction > 0:  # Facing right
            self.sprite = self.base_sprite.copy()
        else:  # Facing left
            self.sprite = pygame.transform.flip(self.base_sprite, True, False)

    def move_left(self) -> None:
        """Set velocity to move left."""
        self.velocity.x = -self.move_speed
        self.facing_direction = Vector2(-1, 0)
        self.visual_direction = -1
        self._update_sprite_rotation()

    def move_right(self) -> None:
        """Set velocity to move right."""
        self.velocity.x = self.move_speed
        self.facing_direction = Vector2(1, 0)
        self.visual_direction = 1
        self._update_sprite_rotation()

    def move_up(self) -> None:
        """Set velocity to move up."""
        self.velocity.y = -self.move_speed
        self.facing_direction = Vector2(0, -1)
        # Don't change visual direction - keep facing left or right

    def move_down(self) -> None:
        """Set velocity to move down."""
        self.velocity.y = self.move_speed
        self.facing_direction = Vector2(0, 1)
        # Don't change visual direction - keep facing left or right

    def stop_horizontal(self) -> None:
        """Stop horizontal movement."""
        self.velocity.x = 0

    def stop_vertical(self) -> None:
        """Stop vertical movement."""
        self.velocity.y = 0

    def fire_projectile(self) -> 'Projectile':
        """
        Create a projectile at the player's current position, firing in facing direction.

        Returns:
            New Projectile instance
        """
        from projectile import Projectile

        # Fire from the center of the player
        center_x = self.position.x + self.width // 2
        center_y = self.position.y + self.height // 2

        # Spawn projectile offset from player in the firing direction
        # This prevents immediate collision with nearby zombies
        spawn_offset = 30  # pixels away from player center
        projectile_x = center_x + (self.facing_direction.x * spawn_offset)
        projectile_y = center_y + (self.facing_direction.y * spawn_offset)

        projectile_pos = Vector2(projectile_x, projectile_y)

        print(f"DEBUG: Firing projectile at ({projectile_pos.x}, {projectile_pos.y}) facing {self.facing_direction.x}, {self.facing_direction.y}")

        return Projectile(projectile_pos, self.facing_direction)

    def update(self, delta_time: float) -> None:
        """
        Update player position based on velocity and delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Calculate next position
        next_x = self.position.x + self.velocity.x * delta_time
        next_y = self.position.y + self.velocity.y * delta_time

        # Constrain to map boundaries if map dimensions are set
        if self.map_width is not None and self.map_height is not None:
            next_x = max(0, min(next_x, self.map_width - self.width))
            next_y = max(0, min(next_y, self.map_height - self.height))

        # Check collision with booth boundaries if game_map is available
        if self.game_map is not None:
            # Try moving horizontally
            can_move_x = self._can_move_to(next_x, self.position.y)
            if can_move_x:
                self.position.x = next_x

            # Try moving vertically
            can_move_y = self._can_move_to(self.position.x, next_y)
            if can_move_y:
                self.position.y = next_y
        else:
            # No collision detection - just move
            self.position.x = next_x
            self.position.y = next_y

    def _can_move_to(self, x: float, y: float) -> bool:
        """
        Check if the player can move to a position (walkability check).

        Args:
            x: Target x position
            y: Target y position

        Returns:
            True if the position is walkable, False otherwise
        """
        if self.game_map is None:
            return True

        # Check multiple points around the player's bounding box
        # This ensures we don't clip into walls
        check_points = [
            (x + 5, y + 5),                           # Top-left corner (with margin)
            (x + self.width - 5, y + 5),              # Top-right corner
            (x + 5, y + self.height - 5),             # Bottom-left corner
            (x + self.width - 5, y + self.height - 5), # Bottom-right corner
            (x + self.width // 2, y + self.height // 2) # Center
        ]

        # All points must be walkable
        for check_x, check_y in check_points:
            if not self.game_map.is_walkable(int(check_x), int(check_y)):
                return False

        return True

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the player's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )
