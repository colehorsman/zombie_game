"""Boss entity implementation - NES-style Wizard."""

import pygame
import logging
import time
from typing import Optional
from models import Vector2

logger = logging.getLogger(__name__)


class Boss:
    """Represents a boss enemy - NES-style Wizard with hat and 'W' on shirt."""

    def __init__(self, position: Vector2, name: str = "Wizard Boss"):
        """
        Initialize the wizard boss.

        Args:
            position: Starting position
            name: Boss name
        """
        self.name = name
        self.position = position
        self.velocity = Vector2(0, 0)

        # Boss dimensions (larger than regular zombies)
        self.width = 80
        self.height = 80

        # Boss health (much higher than zombies)
        self.health = 150  # 50x regular zombie (3 HP)
        self.max_health = 150

        # Boss movement
        self.move_speed = 30.0  # Slower than zombies (0.5x zombie speed)
        self.gravity = 1200.0
        self.max_fall_speed = 600.0
        self.on_ground = False
        self.ground_y = 792  # Will be updated if needed

        # Visual damage feedback
        self.is_flashing = False
        self.flash_timer = 0.0

        # Boss state
        self.is_defeated = False
        self.on_cloud = True  # Boss starts on cloud during entrance
        self.cloud_y_offset = 0  # Cloud position offset for animation

        # Create NES-style wizard sprite
        self.sprite = self._create_sprite()
        self.cloud_sprite = self._create_cloud_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """Create NES-style wizard sprite with hat and 'W' on shirt."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # NES color palette
        PURPLE = (120, 60, 180)      # Wizard robe
        DARK_PURPLE = (80, 40, 120)  # Shadow
        BLUE = (60, 100, 200)        # Hat
        DARK_BLUE = (40, 60, 150)    # Hat shadow
        WHITE = (255, 255, 255)      # 'W' on shirt
        BLACK = (0, 0, 0)            # Outline
        SKIN = (255, 200, 150)       # Face/hands
        GOLD = (255, 215, 0)         # Hat star/decoration

        # Draw wizard body (robe)
        # Body rectangle
        body_rect = pygame.Rect(20, 30, 40, 50)
        pygame.draw.rect(sprite, DARK_PURPLE, body_rect)
        pygame.draw.rect(sprite, PURPLE, (body_rect.x + 2, body_rect.y + 2, body_rect.width - 4, body_rect.height - 4))
        pygame.draw.rect(sprite, BLACK, body_rect, 2)

        # Draw large 'W' on shirt (centered on body)
        font = pygame.font.Font(None, 36)
        w_text = font.render("W", True, WHITE)
        w_rect = w_text.get_rect(center=(body_rect.centerx, body_rect.centery))
        # Draw black outline for 'W'
        for dx, dy in [(1,1), (-1,-1), (1,-1), (-1,1)]:
            outline = font.render("W", True, BLACK)
            sprite.blit(outline, (w_rect.x + dx, w_rect.y + dy))
        sprite.blit(w_text, w_rect)

        # Draw wizard hat (pointed hat on top)
        hat_points = [
            (30, 25),   # Left base
            (50, 25),   # Right base
            (40, 5),    # Top point
        ]
        pygame.draw.polygon(sprite, DARK_BLUE, hat_points)
        pygame.draw.polygon(sprite, BLUE, [(p[0] + 1, p[1] + 1) if i < 2 else (p[0], p[1] - 1) for i, p in enumerate(hat_points)])
        pygame.draw.polygon(sprite, BLACK, hat_points, 2)

        # Draw star on hat (gold star decoration)
        star_center = (40, 15)
        star_size = 6
        for angle in [0, 72, 144, 216, 288]:
            import math
            rad = math.radians(angle)
            x = star_center[0] + int(star_size * math.cos(rad))
            y = star_center[1] + int(star_size * math.sin(rad))
            pygame.draw.circle(sprite, GOLD, (x, y), 2)

        # Draw face (simple eyes)
        pygame.draw.circle(sprite, SKIN, (35, 40), 8)
        pygame.draw.circle(sprite, SKIN, (45, 40), 8)
        pygame.draw.circle(sprite, BLACK, (35, 40), 2)  # Left eye
        pygame.draw.circle(sprite, BLACK, (45, 40), 2)  # Right eye

        # Draw hands (simple circles)
        pygame.draw.circle(sprite, SKIN, (15, 50), 6)
        pygame.draw.circle(sprite, SKIN, (65, 50), 6)

        return sprite

    def _create_cloud_sprite(self) -> pygame.Surface:
        """Create a fluffy cloud sprite for the boss to float on."""
        cloud_width = 120
        cloud_height = 40
        cloud = pygame.Surface((cloud_width, cloud_height), pygame.SRCALPHA)
        
        # Cloud colors (white/light gray)
        CLOUD_WHITE = (240, 240, 255)
        CLOUD_SHADOW = (200, 200, 220)
        CLOUD_OUTLINE = (180, 180, 200)
        
        # Draw fluffy cloud using overlapping circles
        # Main cloud body
        center_x, center_y = cloud_width // 2, cloud_height // 2
        
        # Large center circle
        pygame.draw.circle(cloud, CLOUD_SHADOW, (center_x, center_y + 5), 20)
        pygame.draw.circle(cloud, CLOUD_WHITE, (center_x, center_y), 20)
        
        # Left puff
        pygame.draw.circle(cloud, CLOUD_SHADOW, (center_x - 25, center_y + 3), 18)
        pygame.draw.circle(cloud, CLOUD_WHITE, (center_x - 25, center_y - 2), 18)
        
        # Right puff
        pygame.draw.circle(cloud, CLOUD_SHADOW, (center_x + 25, center_y + 3), 18)
        pygame.draw.circle(cloud, CLOUD_WHITE, (center_x + 25, center_y - 2), 18)
        
        # Small puffs on edges
        pygame.draw.circle(cloud, CLOUD_WHITE, (center_x - 40, center_y), 12)
        pygame.draw.circle(cloud, CLOUD_WHITE, (center_x + 40, center_y), 12)
        
        # Outline
        pygame.draw.circle(cloud, CLOUD_OUTLINE, (center_x, center_y), 20, 2)
        
        return cloud

    def update(self, delta_time: float, player_pos: Vector2, game_map: Optional['GameMap'] = None) -> None:
        """
        Update boss AI - move toward player. Drops from cloud during entrance.

        Args:
            delta_time: Time elapsed since last frame
            player_pos: Player's position
            game_map: Game map for collision detection
        """
        if self.is_defeated:
            return

        # Entrance phase: boss drops from cloud
        if self.on_cloud:
            # Calculate ground level
            if game_map:
                tiles_high = game_map.map_height // 16
                ground_height = 8
                ground_start_tile = tiles_high - ground_height
                target_ground_y = (ground_start_tile * 16) - self.height
            else:
                target_ground_y = self.ground_y

            # Drop down toward ground
            fall_speed = 200.0  # Slower fall for dramatic entrance
            self.position.y += fall_speed * delta_time

            # Animate cloud (bob up and down slightly)
            import math
            self.cloud_y_offset = math.sin(time.time() * 3.0) * 3  # Gentle bobbing

            # Land on ground
            if self.position.y >= target_ground_y:
                self.position.y = target_ground_y
                self.on_cloud = False
                self.velocity.y = 0
                self.on_ground = True
                logger.info("🧙 Wizard Boss has landed!")
            else:
                self.on_ground = False
                return  # Don't move horizontally while dropping

        # After landing: move toward player
        dx = player_pos.x - self.position.x
        distance = abs(dx)

        if distance > 50:  # Don't move if too close
            if dx > 0:
                self.velocity.x = self.move_speed
            elif dx < 0:
                self.velocity.x = -self.move_speed
        else:
            self.velocity.x = 0

        # Apply gravity (only if not on ground)
        if not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            if self.velocity.y > self.max_fall_speed:
                self.velocity.y = self.max_fall_speed

        # Update position
        self.position.x += self.velocity.x * delta_time
        if not self.on_cloud:  # Only apply vertical velocity after landing
            self.position.y += self.velocity.y * delta_time

        # Ground collision - calculate ground level from map
        if game_map:
            tiles_high = game_map.map_height // 16
            ground_height = 8
            ground_start_tile = tiles_high - ground_height
            ground_y = (ground_start_tile * 16) - self.height
        else:
            ground_y = self.ground_y

        if not self.on_cloud and self.position.y >= ground_y:
            self.position.y = ground_y
            self.velocity.y = 0
            self.on_ground = True
        elif not self.on_cloud:
            self.on_ground = False

        # Update flash timer
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to the boss.

        Args:
            damage: Amount of damage to apply

        Returns:
            True if boss is defeated, False otherwise
        """
        if self.is_defeated:
            return True

        self.health -= damage
        if self.health < 0:
            self.health = 0

        # Flash on damage
        self.is_flashing = True
        self.flash_timer = 0.2

        if self.health <= 0:
            self.is_defeated = True
            logger.info(f"Boss {self.name} defeated!")
            return True

        return False

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the boss's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )

