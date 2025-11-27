"""Cyber Attack Themed Boss System.

This module implements bosses themed after famous cyber attacks with educational
dialogue and unique mechanics.
"""

import pygame
import logging
import math
import time
from typing import Optional, List
from enum import Enum
from models import Vector2

logger = logging.getLogger(__name__)


class BossType(Enum):
    """Types of cyber attack bosses."""
    SCATTERED_SPIDER = "scattered_spider"  # Level 7 - Org
    BLACKCAT = "blackcat"  # Level 5 - Production Data
    MIDNIGHT_BLIZZARD = "midnight_blizzard"  # Level 6 - Production
    VOLT_TYPHOON = "volt_typhoon"  # Level 4 - Staging
    SANDWORM = "sandworm"  # Level 3 - Test/QA
    HEARTBLEED = "heartbleed"  # Level 2 - Development
    WANNACRY = "wannacry"  # Level 1 - Sandbox


# Map boss types to level numbers
BOSS_LEVEL_MAP = {
    1: BossType.WANNACRY,
    2: BossType.HEARTBLEED,
    3: BossType.SANDWORM,
    4: BossType.VOLT_TYPHOON,
    5: BossType.BLACKCAT,
    6: BossType.MIDNIGHT_BLIZZARD,
    7: BossType.SCATTERED_SPIDER,
}


class MiniSpider:
    """Individual spider for the Scattered Spider swarm boss."""

    def __init__(self, position: Vector2, movement_type: str, color_variant: int):
        """
        Initialize a mini spider.

        Args:
            position: Starting position
            movement_type: "fast", "slow", "zigzag", "jumping", or "teleport"
            color_variant: 0-4 for different spider colors
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.movement_type = movement_type
        self.color_variant = color_variant

        # Spider dimensions (hybrid size: 60x80 base + effects = ~120x140 total)
        self.width = 60
        self.height = 80

        # Visual effect sizing (glow/aura adds perceived size)
        self.effect_radius = 30  # Adds 30px on each side

        # Health - each spider has 30 HP (150 total / 5 spiders)
        self.health = 30
        self.max_health = 30

        # Movement parameters based on type
        if movement_type == "fast":
            self.move_speed = 120.0
        elif movement_type == "slow":
            self.move_speed = 40.0
        elif movement_type == "zigzag":
            self.move_speed = 80.0
            self.zigzag_timer = 0.0
        elif movement_type == "jumping":
            self.move_speed = 60.0
            self.jump_timer = 0.0
            self.can_jump = True
        elif movement_type == "teleport":
            self.move_speed = 50.0
            self.teleport_timer = 0.0

        # Physics
        self.gravity = 1200.0
        self.max_fall_speed = 600.0
        self.on_ground = False

        # Visual feedback
        self.is_flashing = False
        self.flash_timer = 0.0
        self.is_defeated = False

        # Create sprite and glow effect
        self.sprite = self._create_sprite()
        self.glow_sprite = self._create_glow_effect()

    def _create_sprite(self) -> pygame.Surface:
        """Create 8-bit spider sprite with color variant (60x80)."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Color variants for different spiders
        colors = [
            (20, 20, 20),      # Black (variant 0)
            (180, 20, 20),     # Red (variant 1)
            (20, 180, 20),     # Green (variant 2)
            (20, 80, 200),     # Blue (variant 3)
            (160, 20, 160),    # Purple (variant 4)
        ]
        body_color = colors[self.color_variant % len(colors)]

        # Spider body (oval) - scaled for 60x80 size
        center_x, center_y = self.width // 2, self.height // 2
        body_width = 24  # Scaled from 16 (1.5x)
        body_height = 18  # Scaled from 12 (1.5x)
        pygame.draw.ellipse(sprite, body_color,
                          (center_x - body_width//2, center_y - body_height//2,
                           body_width, body_height))

        # Spider legs (4 pairs, 8 legs total) - scaled up
        leg_color = tuple(max(0, c - 40) for c in body_color)  # Darker legs
        leg_length = 20  # Scaled from 12 (1.67x for dramatic effect)
        leg_width = 3    # Scaled from 2 (1.5x)

        # Left legs (top to bottom)
        for i, angle in enumerate([135, 160, 200, 225]):
            rad = math.radians(angle)
            start_x = center_x - 10  # Scaled from 6
            start_y = center_y + (i - 1.5) * 3  # Scaled spacing
            end_x = start_x + int(leg_length * math.cos(rad))
            end_y = start_y + int(leg_length * math.sin(rad))
            pygame.draw.line(sprite, leg_color, (start_x, start_y), (end_x, end_y), leg_width)

        # Right legs (top to bottom)
        for i, angle in enumerate([45, 20, -20, -45]):
            rad = math.radians(angle)
            start_x = center_x + 10  # Scaled from 6
            start_y = center_y + (i - 1.5) * 3  # Scaled spacing
            end_x = start_x + int(leg_length * math.cos(rad))
            end_y = start_y + int(leg_length * math.sin(rad))
            pygame.draw.line(sprite, leg_color, (start_x, start_y), (end_x, end_y), leg_width)

        # Eyes (red) - scaled up
        eye_color = (255, 20, 20)
        eye_radius = 3  # Scaled from 2 (1.5x)
        pygame.draw.circle(sprite, eye_color, (center_x - 5, center_y - 3), eye_radius)  # Scaled positions
        pygame.draw.circle(sprite, eye_color, (center_x + 5, center_y - 3), eye_radius)

        return sprite

    def _create_glow_effect(self) -> pygame.Surface:
        """Create glow/aura effect for hybrid sizing (adds 30px radius)."""
        # Glow surface is larger than sprite to add perceived size
        glow_width = self.width + (self.effect_radius * 2)
        glow_height = self.height + (self.effect_radius * 2)
        glow = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)

        # Color variants for glow (semi-transparent matching spider color)
        glow_colors = [
            (80, 80, 80, 100),      # Gray glow for black spider
            (255, 100, 100, 100),   # Red glow
            (100, 255, 100, 100),   # Green glow
            (100, 150, 255, 100),   # Blue glow
            (200, 100, 200, 100),   # Purple glow
        ]
        glow_color = glow_colors[self.color_variant % len(glow_colors)]

        # Create pulsing glow effect with gradient circles
        center_x = glow_width // 2
        center_y = glow_height // 2

        # Draw multiple circles with decreasing opacity for gradient effect
        for i in range(3, 0, -1):
            radius = self.effect_radius * (i / 3)
            alpha = glow_color[3] // (4 - i)  # Fade out toward edges
            color_with_alpha = (*glow_color[:3], alpha)

            # Create temp surface for this ring
            temp = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
            pygame.draw.circle(temp, color_with_alpha, (center_x, center_y), int(radius))
            glow.blit(temp, (0, 0))

        return glow

    def update(self, delta_time: float, player_pos: Vector2, game_map: Optional['GameMap'] = None) -> None:
        """
        Update spider AI based on movement type.

        Args:
            delta_time: Time elapsed since last frame
            player_pos: Player's position
            game_map: Game map for collision detection
        """
        if self.is_defeated:
            return

        # Movement AI based on type
        dx = player_pos.x - self.position.x

        if self.movement_type == "fast":
            # Fast spider - chase player directly
            if abs(dx) > 30:
                self.velocity.x = self.move_speed if dx > 0 else -self.move_speed
            else:
                self.velocity.x = 0

        elif self.movement_type == "slow":
            # Slow spider - plodding approach
            if abs(dx) > 30:
                self.velocity.x = self.move_speed if dx > 0 else -self.move_speed
            else:
                self.velocity.x = 0

        elif self.movement_type == "zigzag":
            # Zigzag spider - changes direction periodically
            self.zigzag_timer += delta_time
            if self.zigzag_timer > 1.0:  # Change direction every second
                self.zigzag_timer = 0.0
                if abs(dx) > 30:
                    self.velocity.x = self.move_speed if dx > 0 else -self.move_speed
                else:
                    self.velocity.x = 0

        elif self.movement_type == "jumping":
            # Jumping spider - jumps toward player
            self.jump_timer += delta_time
            if abs(dx) > 30:
                self.velocity.x = self.move_speed if dx > 0 else -self.move_speed
            else:
                self.velocity.x = 0

            # Jump if on ground and timer ready
            if self.on_ground and self.can_jump and self.jump_timer > 1.5:
                self.velocity.y = -400.0  # Jump velocity
                self.jump_timer = 0.0
                self.on_ground = False

        elif self.movement_type == "teleport":
            # Teleporting spider - teleports periodically
            self.teleport_timer += delta_time
            if self.teleport_timer > 3.0:  # Teleport every 3 seconds
                self.teleport_timer = 0.0
                # Teleport to random position near player
                import random
                offset_x = random.randint(-200, 200)
                offset_y = random.randint(-100, 0)
                self.position.x = player_pos.x + offset_x
                self.position.y = player_pos.y + offset_y
            else:
                # Move slowly when not teleporting
                if abs(dx) > 30:
                    self.velocity.x = self.move_speed if dx > 0 else -self.move_speed
                else:
                    self.velocity.x = 0

        # Apply gravity
        if not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            if self.velocity.y > self.max_fall_speed:
                self.velocity.y = self.max_fall_speed

        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Ground collision
        if game_map:
            tiles_high = game_map.map_height // 16
            ground_height = 8
            ground_start_tile = tiles_high - ground_height
            ground_y = (ground_start_tile * 16) - self.height
        else:
            ground_y = 792  # Default ground

        if self.position.y >= ground_y:
            self.position.y = ground_y
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Update flash timer
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to the spider.

        Args:
            damage: Amount of damage to apply

        Returns:
            True if spider is defeated, False otherwise
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
            logger.info(f"Mini spider ({self.movement_type}) defeated!")
            return True

        return False

    def get_bounds(self) -> pygame.Rect:
        """Get the bounding rectangle for collision detection."""
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )


class ScatteredSpiderBoss:
    """Scattered Spider - Swarm of 5 mini spiders (identity theft attack)."""

    def __init__(self, spawn_positions: List[Vector2]):
        """
        Initialize Scattered Spider boss.

        Args:
            spawn_positions: List of 5 starting positions for the spiders
        """
        self.name = "Scattered Spider"
        self.boss_type = BossType.SCATTERED_SPIDER
        self.is_defeated = False

        # Create 5 mini spiders with different movement types
        movement_types = ["fast", "slow", "zigzag", "jumping", "teleport"]
        self.spiders: List[MiniSpider] = []

        for i in range(5):
            spider = MiniSpider(
                position=spawn_positions[i] if i < len(spawn_positions) else Vector2(100 * i, 100),
                movement_type=movement_types[i],
                color_variant=i
            )
            self.spiders.append(spider)
            logger.info(f"Spawned {movement_types[i]} spider at {spawn_positions[i]}")

    def update(self, delta_time: float, player_pos: Vector2, game_map: Optional['GameMap'] = None) -> None:
        """Update all spiders in the swarm."""
        if self.is_defeated:
            return

        # Update each spider
        for spider in self.spiders:
            if not spider.is_defeated:
                spider.update(delta_time, player_pos, game_map)

        # Check if all spiders defeated
        if all(spider.is_defeated for spider in self.spiders):
            self.is_defeated = True
            logger.info("🕷️ SCATTERED SPIDER BOSS DEFEATED!")

    def get_all_spiders(self) -> List[MiniSpider]:
        """Get list of all spiders (for collision detection)."""
        return [spider for spider in self.spiders if not spider.is_defeated]

    def get_total_health_remaining(self) -> int:
        """Get combined health of all remaining spiders."""
        return sum(spider.health for spider in self.spiders if not spider.is_defeated)

    def get_max_health(self) -> int:
        """Get maximum combined health."""
        return 150  # 5 spiders * 30 HP each


def create_cyber_boss(boss_type: BossType, level_width: int, ground_y: int):
    """
    Factory function to create the appropriate boss for a level.

    Args:
        boss_type: Type of boss to create
        level_width: Width of the level (for positioning)
        ground_y: Y position of the ground

    Returns:
        Boss instance (type depends on boss_type)
    """
    if boss_type == BossType.SCATTERED_SPIDER:
        # Create 5 spawn positions spread across the level
        spawn_positions = []
        for i in range(5):
            x = (level_width // 6) * (i + 1)  # Spread evenly
            y = ground_y - 100  # Start slightly above ground
            spawn_positions.append(Vector2(x, y))

        return ScatteredSpiderBoss(spawn_positions)

    # TODO: Implement other boss types
    elif boss_type == BossType.BLACKCAT:
        logger.warning("BlackCat boss not yet implemented")
        return None
    elif boss_type == BossType.MIDNIGHT_BLIZZARD:
        logger.warning("Midnight Blizzard boss not yet implemented")
        return None
    elif boss_type == BossType.VOLT_TYPHOON:
        logger.warning("Volt Typhoon boss not yet implemented")
        return None
    elif boss_type == BossType.SANDWORM:
        logger.warning("Sandworm boss not yet implemented")
        return None
    elif boss_type == BossType.HEARTBLEED:
        logger.warning("Heartbleed boss not yet implemented")
        return None
    elif boss_type == BossType.WANNACRY:
        logger.warning("WannaCry boss not yet implemented")
        return None

    logger.error(f"Unknown boss type: {boss_type}")
    return None


def get_boss_dialogue(boss_type: BossType) -> dict:
    """
    Get the educational dialogue for a boss.

    Args:
        boss_type: Type of boss

    Returns:
        Dictionary with dialogue content
    """
    if boss_type == BossType.SCATTERED_SPIDER:
        return {
            "title": "🕷️ SCATTERED SPIDER APPEARS! 🕷️",
            "description": "Scattered Spider was a sophisticated threat group active in 2023-2024\nthat specialized in IDENTITY THEFT and SOCIAL ENGINEERING.",
            "how_attacked": [
                "Called help desks pretending to be employees",
                "Bypassed MFA through SIM swapping attacks",
                "Stole session tokens from identity providers",
                "Moved laterally through cloud environments"
            ],
            "victims": "MGM Resorts, Caesars Entertainment, Okta customers",
            "prevention": [
                "Just-In-Time (JIT) access limits credential exposure",
                "Session token monitoring and anomaly detection",
                "Phishing-resistant MFA (passkeys, FIDO2)",
                "Help desk verification protocols",
                "Cloud Permissions Firewall to limit lateral movement"
            ],
            "mechanic": "Defeat all 5 spiders to win!\nEach spider represents a different attack vector."
        }

    # TODO: Add dialogues for other bosses
    return {
        "title": "BOSS BATTLE",
        "description": "A powerful enemy approaches!",
        "how_attacked": [],
        "victims": "",
        "prevention": [],
        "mechanic": "Defeat the boss to continue!"
    }
