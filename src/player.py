"""Player character implementation."""

import logging
from typing import Optional

import pygame

from models import Vector2

logger = logging.getLogger(__name__)


class Player:
    """Represents the controllable Mega Man-style character."""

    def __init__(
        self,
        position: Vector2,
        map_width: Optional[int] = None,
        map_height: Optional[int] = None,
        game_map: Optional["GameMap"] = None,
    ):
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

        # Movement speed (pixels per second) - realistic walking speed for lobby
        # Platformer mode will use different speeds
        self.base_move_speed = 120.0  # Base speed for lobby (top-down)
        self.move_speed = 120.0  # Current movement speed
        self.base_jump_speed = 600.0  # Base jump velocity for platformer
        self.jump_speed = 600.0  # Current jump velocity
        self.gravity = 1200.0  # Gravity acceleration (pixels/s²) for platformer
        self.max_fall_speed = 600.0  # Terminal velocity

        # Ground detection for platformer mode
        self.on_ground = False
        if map_height:
            ground_tiles = 8  # Number of ground tiles
            tile_size = 16  # Tile size in pixels
            tiles_high = map_height // tile_size
            ground_start_tile = tiles_high - ground_tiles
            self.ground_y = (ground_start_tile * tile_size) - self.height
        else:
            self.ground_y = 500

        # Crouching state
        self.is_crouching = False

        # Facing direction for firing projectiles
        self.facing_direction = Vector2(1, 0)  # Start facing right

        # Visual direction (only left/right for sprite)
        self.visual_direction = 1  # 1 = right, -1 = left

        # Health system
        self.max_health: int = 10
        self.current_health: int = self.max_health

        # Invincibility frames (after taking damage)
        self.is_invincible: bool = False
        self.invincibility_timer: float = 0.0
        self.invincibility_duration: float = 0.5  # seconds (reduced for faster gameplay)
        self.flash_timer: float = 0.0
        self.flash_interval: float = 0.1  # Flash every 0.1s during invincibility
        self.is_visible: bool = True  # For flashing effect

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
        HAIR_BROWN = (80, 50, 30)  # Dark brown hair
        SKIN = (220, 180, 140)  # Skin tone
        DARK_SKIN = (180, 140, 100)  # Shadow on skin
        PURPLE = (120, 60, 180)  # re:Invent purple shirt
        DARK_PURPLE = (80, 40, 120)  # Purple shadows
        LIGHT_PURPLE = (160, 100, 220)  # Purple highlights
        CAP_PURPLE = (100, 50, 160)  # Purple baseball cap
        CAP_DARK = (70, 35, 110)  # Cap shadows
        PANTS_BLACK = (40, 40, 40)  # Black pants
        DARK_PANTS = (25, 25, 25)  # Pants shadows
        BOOTS_BLACK = (30, 30, 30)  # Black boots
        BACKPACK_GREY = (90, 90, 80)  # Grey backpack
        DARK_GREY = (60, 60, 55)  # Backpack shadows
        GUN_METAL = (100, 100, 100)  # Metallic gun
        DARK_METAL = (60, 60, 60)  # Gun shadows
        BLACK = (0, 0, 0)  # Outlines
        RED = (150, 30, 30)  # Blood stains

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
        pygame.draw.rect(sprite, DARK_PURPLE, (14, 24, 8, 4))  # Shadow area

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
        # Cannon base (cylindrical shape) - enlarged for visibility
        cannon_base = pygame.Rect(28, 21, 8, 8)
        pygame.draw.rect(sprite, GUN_METAL, cannon_base)
        pygame.draw.rect(sprite, BLACK, cannon_base, 1)

        # Cannon highlights (top edge - metallic shine)
        pygame.draw.line(sprite, (180, 180, 180), (28, 21), (35, 21), 1)
        pygame.draw.line(sprite, (140, 140, 140), (28, 22), (35, 22), 1)

        # Cannon barrel (extending forward) - longer and more prominent
        barrel = pygame.Rect(35, 22, 6, 6)
        pygame.draw.rect(sprite, DARK_METAL, barrel)
        pygame.draw.rect(sprite, BLACK, barrel, 1)
        # Barrel ridges for detail
        pygame.draw.line(sprite, (80, 80, 80), (36, 22), (36, 27), 1)
        pygame.draw.line(sprite, (80, 80, 80), (38, 22), (38, 27), 1)

        # Energy core (glowing cyan center - classic raygun look) - brighter
        pygame.draw.circle(sprite, (0, 255, 255), (32, 25), 3)  # Bright cyan core
        pygame.draw.circle(sprite, (150, 255, 255), (32, 25), 2)  # Inner glow
        pygame.draw.circle(sprite, (255, 255, 255), (32, 25), 1)  # White hot center

        # Muzzle opening (orange glow - ready to fire)
        pygame.draw.rect(sprite, (255, 150, 50), (39, 23, 2, 4))  # Orange glow
        pygame.draw.rect(sprite, (255, 200, 100), (40, 24, 1, 2))  # Bright center

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

    def jump(self) -> None:
        """Make the player jump (platformer mode only)."""
        if self.on_ground:
            self.velocity.y = -self.jump_speed
            self.on_ground = False

    def crouch(self) -> None:
        """Crouch down (platformer mode)."""
        self.is_crouching = True

    def stand_up(self) -> None:
        """Stand up from crouching (platformer mode)."""
        self.is_crouching = False

    def set_speed_multiplier(self, multiplier: float) -> None:
        """
        Set the speed multiplier for movement and jumping (for power-ups).

        Args:
            multiplier: Speed multiplier (1.0 = normal, 2.0 = double speed, etc.)
        """
        self.move_speed = self.base_move_speed * multiplier
        self.jump_speed = self.base_jump_speed * multiplier

    def fire_projectile(self) -> "Projectile":
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

        print(
            f"DEBUG: Firing projectile at ({projectile_pos.x}, {projectile_pos.y}) facing {self.facing_direction.x}, {self.facing_direction.y}"
        )

        return Projectile(projectile_pos, self.facing_direction)

    def update(self, delta_time: float, is_platformer_mode: bool = False) -> None:
        """
        Update player position based on velocity and delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
            is_platformer_mode: If True, apply platformer physics (gravity, ground collision)
        """
        # PLATFORMER MODE: Apply gravity when in air
        if is_platformer_mode and not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            # Cap fall speed (terminal velocity)
            if self.velocity.y > self.max_fall_speed:
                self.velocity.y = self.max_fall_speed

        # Calculate next position
        next_x = self.position.x + self.velocity.x * delta_time
        next_y = self.position.y + self.velocity.y * delta_time

        # Constrain to map boundaries if map dimensions are set
        if self.map_width is not None and self.map_height is not None:
            next_x = max(0, min(next_x, self.map_width - self.width))
            if not is_platformer_mode:  # Only constrain Y in top-down mode
                next_y = max(0, min(next_y, self.map_height - self.height))

        # PLATFORMER MODE: Ground and platform collision
        if is_platformer_mode:
            if next_y >= self.ground_y:
                # Hit ground
                self.position.y = self.ground_y
                self.velocity.y = 0
                self.on_ground = True
            else:
                # Check if landing on a platform
                if self.game_map is not None and hasattr(self.game_map, "tile_map"):
                    # Check tile below player's feet
                    feet_x = int(self.position.x + self.width // 2)
                    feet_y = int(next_y + self.height)

                    # Convert to tile coordinates
                    tile_size = self.game_map.tile_size
                    tile_x = feet_x // tile_size
                    tile_y = feet_y // tile_size

                    # Check if moving downward and tile below is solid (platform)
                    if (
                        self.velocity.y > 0
                        and 0 <= tile_x < self.game_map.tiles_wide
                        and 0 <= tile_y < self.game_map.tiles_high
                        and self.game_map.tile_map[tile_y][tile_x] == 1
                    ):
                        # Landing on platform - snap to platform top
                        platform_top_y = tile_y * tile_size - self.height
                        self.position.y = platform_top_y
                        self.velocity.y = 0
                        self.on_ground = True
                    elif self.velocity.y < 0:
                        # Moving upward - check for ceiling collision
                        head_x = int(self.position.x + self.width // 2)
                        head_y = int(next_y)
                        head_tile_x = head_x // tile_size
                        head_tile_y = head_y // tile_size

                        if (
                            0 <= head_tile_x < self.game_map.tiles_wide
                            and 0 <= head_tile_y < self.game_map.tiles_high
                            and self.game_map.tile_map[head_tile_y][head_tile_x] == 1
                        ):
                            # Hit ceiling - stop upward movement
                            self.velocity.y = 0
                        else:
                            # Can move up freely
                            self.position.y = next_y
                            self.on_ground = False
                    else:
                        # Falling through air
                        self.position.y = next_y
                        self.on_ground = False
                else:
                    self.position.y = next_y
                    self.on_ground = False

        # Check collision with map boundaries if game_map is available
        if self.game_map is not None:
            # Check horizontal and vertical movement independently
            can_move_x = self._can_move_to(next_x, self.position.y)
            if can_move_x:
                self.position.x = next_x

            # In top-down mode, check vertical movement independently
            if not is_platformer_mode:
                can_move_y = self._can_move_to(self.position.x, next_y)
                if can_move_y:
                    self.position.y = next_y
        else:
            # No collision detection - just move
            self.position.x = next_x
            if not is_platformer_mode:
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

        # For lobby mode (top-down), check multiple points around the player's bounding box
        # Require at least 3 out of 5 points to be walkable to prevent going through walls
        # but allow movement in hallways
        check_points = [
            (x + self.width // 2, y + self.height // 2),  # Center (most important)
            (x + 5, y + self.height // 2),  # Left edge center
            (x + self.width - 5, y + self.height // 2),  # Right edge center
            (x + self.width // 2, y + 5),  # Top edge center
            (x + self.width // 2, y + self.height - 5),  # Bottom edge center
        ]

        # Count how many points are walkable
        walkable_count = sum(
            1
            for check_x, check_y in check_points
            if self.game_map.is_walkable(int(check_x), int(check_y))
        )

        # Require at least 3 out of 5 points to be walkable (prevents going through walls)
        # Center point is most important - if center is walkable, allow movement
        center_walkable = self.game_map.is_walkable(
            int(check_points[0][0]), int(check_points[0][1])
        )
        if center_walkable and walkable_count >= 2:
            return True

        # Otherwise require majority (3/5) to be walkable
        return walkable_count >= 3

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the player's bounds
        """
        return pygame.Rect(int(self.position.x), int(self.position.y), self.width, self.height)

    # ========== Health System Methods ==========

    def take_damage(self, amount: int = 1) -> bool:
        """
        Apply damage to the player.

        Args:
            amount: Amount of damage to apply

        Returns:
            True if damage was applied, False if player is invincible
        """
        if self.is_invincible:
            return False

        self.current_health -= amount
        self.current_health = max(0, self.current_health)

        # Start invincibility frames
        self.is_invincible = True
        self.invincibility_timer = self.invincibility_duration
        self.flash_timer = 0.0
        self.is_visible = True

        logger.info(
            f"💔 Player took {amount} damage! Health: {self.current_health}/{self.max_health}"
        )

        return True

    def heal(self, amount: int) -> None:
        """
        Restore health to the player.

        Args:
            amount: Amount of health to restore
        """
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        healed = self.current_health - old_health

        if healed > 0:
            logger.info(
                f"💚 Player healed {healed} HP! Health: {self.current_health}/{self.max_health}"
            )

    def full_heal(self) -> None:
        """Restore player to full health."""
        self.current_health = self.max_health
        logger.info(f"💚 Player fully healed! Health: {self.current_health}/{self.max_health}")

    def update_invincibility(self, delta_time: float) -> None:
        """
        Update invincibility frames and flashing effect.

        Args:
            delta_time: Time since last update in seconds
        """
        if not self.is_invincible:
            self.is_visible = True
            return

        self.invincibility_timer -= delta_time

        if self.invincibility_timer <= 0:
            # Invincibility ended
            self.is_invincible = False
            self.is_visible = True
            logger.debug("🛡️ Invincibility ended")
        else:
            # Flash effect
            self.flash_timer += delta_time
            if self.flash_timer >= self.flash_interval:
                self.flash_timer = 0.0
                self.is_visible = not self.is_visible

    @property
    def is_dead(self) -> bool:
        """Check if player has no health remaining."""
        return self.current_health <= 0

    @property
    def health_percentage(self) -> float:
        """Get health as a percentage (0.0 to 1.0)."""
        return self.current_health / self.max_health

    def reset_health(self) -> None:
        """Reset health and invincibility state (for level restart)."""
        self.current_health = self.max_health
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.is_visible = True
        logger.info("🔄 Player health reset")
