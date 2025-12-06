"""Cyber Attack Themed Boss System.

This module implements bosses themed after famous cyber attacks with educational
dialogue and unique mechanics.
"""

import logging
import math
import time
from enum import Enum
from typing import List, Optional

import pygame

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
# Level order: Sandbox(1) → Stage(2) → Automation(3) → WebApp(4) → ProdData(5) → Prod(6) → Org(7)
BOSS_LEVEL_MAP = {
    1: BossType.WANNACRY,  # Sandbox - Ransomware attack
    2: BossType.HEARTBLEED,  # Stage - Red Queen (data leak)
    3: BossType.SCATTERED_SPIDER,  # Automation - Swarm of 5 spiders
    4: BossType.VOLT_TYPHOON,  # WebApp
    5: BossType.BLACKCAT,  # Production Data
    6: BossType.MIDNIGHT_BLIZZARD,  # Production
    7: BossType.SANDWORM,  # Org - Final boss
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
            (20, 20, 20),  # Black (variant 0)
            (180, 20, 20),  # Red (variant 1)
            (20, 180, 20),  # Green (variant 2)
            (20, 80, 200),  # Blue (variant 3)
            (160, 20, 160),  # Purple (variant 4)
        ]
        body_color = colors[self.color_variant % len(colors)]

        # Spider body (oval) - scaled for 60x80 size
        center_x, center_y = self.width // 2, self.height // 2
        body_width = 24  # Scaled from 16 (1.5x)
        body_height = 18  # Scaled from 12 (1.5x)
        pygame.draw.ellipse(
            sprite,
            body_color,
            (
                center_x - body_width // 2,
                center_y - body_height // 2,
                body_width,
                body_height,
            ),
        )

        # Spider legs (4 pairs, 8 legs total) - scaled up
        leg_color = tuple(max(0, c - 40) for c in body_color)  # Darker legs
        leg_length = 20  # Scaled from 12 (1.67x for dramatic effect)
        leg_width = 3  # Scaled from 2 (1.5x)

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
        pygame.draw.circle(
            sprite, eye_color, (center_x - 5, center_y - 3), eye_radius
        )  # Scaled positions
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
            (80, 80, 80, 100),  # Gray glow for black spider
            (255, 100, 100, 100),  # Red glow
            (100, 255, 100, 100),  # Green glow
            (100, 150, 255, 100),  # Blue glow
            (200, 100, 200, 100),  # Purple glow
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

    def update(
        self,
        delta_time: float,
        player_pos: Vector2,
        game_map: Optional["GameMap"] = None,
    ) -> None:
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
        return pygame.Rect(int(self.position.x), int(self.position.y), self.width, self.height)


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
                position=(
                    spawn_positions[i] if i < len(spawn_positions) else Vector2(100 * i, 100)
                ),
                movement_type=movement_types[i],
                color_variant=i,
            )
            self.spiders.append(spider)
            logger.info(f"Spawned {movement_types[i]} spider at {spawn_positions[i]}")

    def update(
        self,
        delta_time: float,
        player_pos: Vector2,
        game_map: Optional["GameMap"] = None,
    ) -> None:
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


class HeartbleedBoss:
    """
    Heartbleed Boss - The Red Queen.

    Themed after the 2014 Heartbleed vulnerability (CVE-2014-0160),
    the most devastating OpenSSL bug that leaked sensitive data from
    memory, depicted as the Queen of Hearts bleeding secrets.
    """

    def __init__(self, position: Vector2):
        """
        Initialize the Heartbleed Red Queen boss.

        Args:
            position: Starting position for the boss
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.name = "HEARTBLEED - THE RED QUEEN"

        # Boss dimensions (hybrid size: 60x80 base + effects = ~120x140 total)
        self.width = 60
        self.height = 80
        self.effect_radius = 30  # Glow/aura adds perceived size

        # Health
        self.health = 150
        self.max_health = 150
        self.is_defeated = False

        # Movement - regal, slower paced
        self.move_speed = 50.0
        self.facing_right = True

        # Physics
        self.gravity = 1200.0
        self.max_fall_speed = 600.0
        self.on_ground = False
        self.ground_y = 0

        # Attack mechanics
        self.attack_timer = 0.0
        self.attack_cooldown = 2.5  # Throws hearts every 2.5 seconds
        self.heart_projectiles = []  # List of bleeding heart projectiles

        # Special mechanic: "Card Flip" teleport
        self.teleport_timer = 0.0
        self.teleport_cooldown = 8.0  # Teleports every 8 seconds
        self.is_teleporting = False
        self.teleport_animation_timer = 0.0

        # Visual effects
        self.bleeding_particles = []  # Red data leak particles
        self.particle_spawn_timer = 0.0
        self.glow_pulse_timer = 0.0
        self.is_flashing = False
        self.flash_timer = 0.0

        # Health-based phase changes
        self.current_phase = 1  # Phase 1: 100-150 HP, Phase 2: 50-99 HP, Phase 3: 1-49 HP

        # Create visuals
        self.sprite = self._create_red_queen_sprite()
        self.glow_sprite = self._create_glow_effect()
        self.crown_sprite = self._create_crown()

    def _create_red_queen_sprite(self) -> pygame.Surface:
        """Create 8-bit Red Queen sprite with dress and bleeding heart (60x80)."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        sprite.fill((0, 0, 0, 0))  # Fill with fully transparent

        # Color palette - Red Queen colors
        dress_red = (200, 20, 30)
        dress_dark = (140, 10, 20)
        skin_tone = (255, 220, 200)
        card_black = (20, 20, 20)
        hair_black = (10, 10, 10)

        center_x = self.width // 2
        center_y = self.height // 2

        # === DRESS (shorter, bell-shaped, slimmer) ===
        # Dress upper body (trapezoid shape)
        dress_top = center_y - 10
        dress_upper_points = [
            (center_x - 8, dress_top),  # Left shoulder (slimmer)
            (center_x + 8, dress_top),  # Right shoulder (slimmer)
            (center_x + 12, center_y + 8),  # Right waist (slimmer)
            (center_x - 12, center_y + 8),  # Left waist (slimmer)
        ]
        pygame.draw.polygon(sprite, dress_red, dress_upper_points)
        pygame.draw.lines(sprite, dress_dark, True, dress_upper_points, 2)

        # Dress skirt (shorter, slimmer bell shape)
        dress_skirt_points = [
            (center_x - 12, center_y + 8),  # Left waist
            (center_x + 12, center_y + 8),  # Right waist
            (center_x + 18, center_y + 22),  # Right hem (slimmer)
            (center_x - 18, center_y + 22),  # Left hem (slimmer)
        ]
        pygame.draw.polygon(sprite, dress_red, dress_skirt_points)
        pygame.draw.lines(sprite, dress_dark, True, dress_skirt_points, 2)

        # === BLACK HEART ON CHEST (Heartbleed symbol, lowered) ===
        heart_center_y = center_y + 2
        # Heart top lobes
        pygame.draw.circle(sprite, card_black, (center_x - 4, heart_center_y - 2), 5)
        pygame.draw.circle(sprite, card_black, (center_x + 4, heart_center_y - 2), 5)
        # Heart bottom point
        heart_bottom = [
            (center_x - 8, heart_center_y),
            (center_x + 8, heart_center_y),
            (center_x, heart_center_y + 10),
        ]
        pygame.draw.polygon(sprite, card_black, heart_bottom)

        # Bleeding drips from heart (red data leak)
        for drip_x in [center_x - 2, center_x + 2]:
            pygame.draw.circle(sprite, dress_red, (drip_x, heart_center_y + 12), 2)
            pygame.draw.circle(sprite, dress_red, (drip_x, heart_center_y + 15), 1)

        # === LEGS WITH FISHNET STOCKINGS ===
        # Left leg
        left_leg_x = center_x - 10
        pygame.draw.line(
            sprite,
            skin_tone,
            (left_leg_x, center_y + 22),
            (left_leg_x, center_y + 38),
            5,
        )
        # Fishnet pattern on left leg (diamond pattern)
        for leg_y in range(center_y + 24, center_y + 38, 4):
            pygame.draw.line(
                sprite,
                card_black,
                (left_leg_x - 2, leg_y),
                (left_leg_x + 2, leg_y + 2),
                1,
            )
            pygame.draw.line(
                sprite,
                card_black,
                (left_leg_x + 2, leg_y),
                (left_leg_x - 2, leg_y + 2),
                1,
            )

        # Right leg
        right_leg_x = center_x + 10
        pygame.draw.line(
            sprite,
            skin_tone,
            (right_leg_x, center_y + 22),
            (right_leg_x, center_y + 38),
            5,
        )
        # Fishnet pattern on right leg
        for leg_y in range(center_y + 24, center_y + 38, 4):
            pygame.draw.line(
                sprite,
                card_black,
                (right_leg_x - 2, leg_y),
                (right_leg_x + 2, leg_y + 2),
                1,
            )
            pygame.draw.line(
                sprite,
                card_black,
                (right_leg_x + 2, leg_y),
                (right_leg_x - 2, leg_y + 2),
                1,
            )

        # === HEAD (above dress) ===
        head_y = dress_top - 13

        # === NECK (connecting head to body) ===
        neck_top = head_y + 8
        neck_bottom = dress_top
        pygame.draw.line(sprite, skin_tone, (center_x, neck_top), (center_x, neck_bottom), 6)

        # === BLACK HAIR FIRST (drawn behind face - Harley Quinn flowing style) ===
        # Hair volume on top of head (fuller, more dramatic)
        pygame.draw.ellipse(sprite, hair_black, (center_x - 12, head_y - 15, 24, 14))

        # Left flowing pigtail (voluminous, elegant)
        left_hair_outer = [
            (center_x - 9, head_y - 6),  # Start at head
            (center_x - 11, head_y - 3),  # Flow out
            (center_x - 16, head_y + 2),  # Wide curve
            (center_x - 18, head_y + 8),  # Continue flowing
            (center_x - 17, head_y + 15),  # Flow down gracefully
            (center_x - 14, head_y + 18),  # Taper
            (center_x - 10, head_y + 16),  # Inner curve
            (center_x - 8, head_y + 10),  # Back toward face
            (center_x - 7, head_y + 3),  # Up along face
        ]
        pygame.draw.polygon(sprite, hair_black, left_hair_outer)

        # Right flowing pigtail (voluminous, elegant)
        right_hair_outer = [
            (center_x + 9, head_y - 6),  # Start at head
            (center_x + 11, head_y - 3),  # Flow out
            (center_x + 16, head_y + 2),  # Wide curve
            (center_x + 18, head_y + 8),  # Continue flowing
            (center_x + 17, head_y + 15),  # Flow down gracefully
            (center_x + 14, head_y + 18),  # Taper
            (center_x + 10, head_y + 16),  # Inner curve
            (center_x + 8, head_y + 10),  # Back toward face
            (center_x + 7, head_y + 3),  # Up along face
        ]
        pygame.draw.polygon(sprite, hair_black, right_hair_outer)

        # Add highlights to hair for shine/flow effect
        # Left hair highlight
        left_highlight = [
            (center_x - 10, head_y),
            (center_x - 13, head_y + 5),
            (center_x - 12, head_y + 10),
        ]
        pygame.draw.lines(sprite, (40, 40, 40), False, left_highlight, 2)

        # Right hair highlight
        right_highlight = [
            (center_x + 10, head_y),
            (center_x + 13, head_y + 5),
            (center_x + 12, head_y + 10),
        ]
        pygame.draw.lines(sprite, (40, 40, 40), False, right_highlight, 2)

        # === FACE (drawn on top of hair) ===
        # Face shape (slightly oval for feminine look)
        pygame.draw.ellipse(sprite, skin_tone, (center_x - 9, head_y - 10, 18, 20))
        pygame.draw.ellipse(sprite, card_black, (center_x - 9, head_y - 10, 18, 20), 2)

        # Cheekbones (subtle highlight circles)
        cheek_y = head_y + 2
        pygame.draw.circle(sprite, (255, 180, 180), (center_x - 6, cheek_y), 3, 1)  # Left cheek
        pygame.draw.circle(sprite, (255, 180, 180), (center_x + 6, cheek_y), 3, 1)  # Right cheek

        # Feminine eyes with eyelashes
        eye_y = head_y - 2
        # Left eye
        pygame.draw.circle(sprite, card_black, (center_x - 4, eye_y), 2)
        pygame.draw.circle(sprite, (255, 255, 255), (center_x - 5, eye_y - 1), 1)  # Eye shine
        # Right eye
        pygame.draw.circle(sprite, card_black, (center_x + 4, eye_y), 2)
        pygame.draw.circle(sprite, (255, 255, 255), (center_x + 5, eye_y - 1), 1)  # Eye shine

        # Elegant eyebrows (curved, thinner)
        pygame.draw.arc(sprite, card_black, (center_x - 8, eye_y - 5, 6, 3), 0, 3.14, 2)
        pygame.draw.arc(sprite, card_black, (center_x + 2, eye_y - 5, 6, 3), 0, 3.14, 2)

        # Small feminine nose
        pygame.draw.line(sprite, card_black, (center_x, eye_y + 2), (center_x, eye_y + 4), 1)

        # Red lips (fuller, more feminine)
        # Upper lip (slight M-shape)
        upper_lip = [
            (center_x - 3, head_y + 6),
            (center_x - 1, head_y + 5),
            (center_x, head_y + 6),
            (center_x + 1, head_y + 5),
            (center_x + 3, head_y + 6),
        ]
        pygame.draw.lines(sprite, dress_red, False, upper_lip, 2)
        # Lower lip (curved)
        lower_lip = [
            (center_x - 3, head_y + 6),
            (center_x, head_y + 8),
            (center_x + 3, head_y + 6),
        ]
        pygame.draw.lines(sprite, dress_red, False, lower_lip, 2)

        # === ARMS ===
        # Left arm
        pygame.draw.line(
            sprite,
            skin_tone,
            (center_x - 10, dress_top + 5),
            (center_x - 20, center_y + 5),
            4,
        )
        # Right arm
        pygame.draw.line(
            sprite,
            skin_tone,
            (center_x + 10, dress_top + 5),
            (center_x + 20, center_y + 5),
            4,
        )

        return sprite

    def _create_crown(self) -> pygame.Surface:
        """Create a golden crown sprite that sits above the queen."""
        crown = pygame.Surface((30, 15), pygame.SRCALPHA)
        royal_gold = (255, 215, 0)
        gold_dark = (200, 170, 0)

        # Crown base
        pygame.draw.rect(crown, royal_gold, (2, 10, 26, 5))

        # Crown spikes (5 points)
        for i in range(5):
            x = 4 + i * 6
            points = [(x, 10), (x + 3, 0), (x + 6, 10)]
            pygame.draw.polygon(crown, royal_gold, points)
            pygame.draw.polygon(crown, gold_dark, points, 1)

        # Jewels on crown (red hearts)
        for i in [7, 15, 23]:
            pygame.draw.circle(crown, (220, 20, 20), (i, 12), 2)

        return crown

    def _create_glow_effect(self) -> pygame.Surface:
        """Create pulsing red glow effect for the Red Queen."""
        glow_width = self.width + (self.effect_radius * 2)
        glow_height = self.height + (self.effect_radius * 2)
        glow = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        glow.fill((0, 0, 0, 0))  # Fill with fully transparent

        center_x, center_y = glow_width // 2, glow_height // 2

        # Red glow rings (representing data leak/bleeding)
        glow_colors = [
            (220, 20, 20, 15),  # Outermost - faint red
            (220, 20, 20, 25),
            (220, 20, 20, 35),
            (220, 20, 20, 45),  # Innermost - stronger red
        ]

        for i, color in enumerate(glow_colors):
            radius = self.effect_radius - (i * 7)
            pygame.draw.circle(glow, color, (center_x, center_y), radius)

        return glow

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and check if defeated.

        Args:
            damage: Amount of damage to take

        Returns:
            True if boss is defeated, False otherwise
        """
        if self.is_defeated:
            return True

        self.health -= damage
        self.is_flashing = True
        self.flash_timer = 0.2  # Flash for 0.2 seconds

        # Spawn bleeding particles when hit
        for _ in range(5):
            self._spawn_bleeding_particle()

        # Check phase transitions
        if self.health <= 50 and self.current_phase == 1:
            self.current_phase = 2
            self.attack_cooldown = 2.0  # Faster attacks in phase 2
            logger.info("💔 Heartbleed Phase 2: Queen's Rage!")
        elif self.health <= 25 and self.current_phase == 2:
            self.current_phase = 3
            self.attack_cooldown = 1.5  # Even faster in phase 3
            self.teleport_cooldown = 5.0  # More frequent teleports
            logger.info("💔 Heartbleed Phase 3: Desperate Bleed!")

        if self.health <= 0:
            self.health = 0
            self.is_defeated = True
            logger.info("👑 The Red Queen has fallen!")
            return True

        return False

    def _spawn_bleeding_particle(self):
        """Spawn a red particle representing leaked data."""
        particle = {
            "x": self.position.x + self.width // 2,
            "y": self.position.y + self.height // 2,
            "vx": (pygame.time.get_ticks() % 100 - 50) / 10.0,
            "vy": -50.0 - (pygame.time.get_ticks() % 50),
            "lifetime": 1.0,
            "alpha": 255,
        }
        self.bleeding_particles.append(particle)

    def update(self, delta_time: float, player_position: Vector2, game_map=None) -> None:
        """Update boss logic."""
        if self.is_defeated:
            return

        # Update flash effect
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

        # Update glow pulse
        self.glow_pulse_timer += delta_time

        # Update bleeding particles
        for particle in self.bleeding_particles[:]:
            particle["lifetime"] -= delta_time
            particle["x"] += particle["vx"] * delta_time
            particle["y"] += particle["vy"] * delta_time
            particle["vy"] += 200.0 * delta_time  # Gravity on particles
            particle["alpha"] = int(255 * (particle["lifetime"] / 1.0))

            if particle["lifetime"] <= 0:
                self.bleeding_particles.remove(particle)

        # Spawn bleeding particles periodically (data leak visual)
        self.particle_spawn_timer += delta_time
        if self.particle_spawn_timer >= 0.3:
            self._spawn_bleeding_particle()
            self.particle_spawn_timer = 0.0

        # Teleport mechanic (card flip)
        if not self.is_teleporting:
            self.teleport_timer += delta_time
            if self.teleport_timer >= self.teleport_cooldown:
                self._initiate_teleport(player_position, game_map)

        # Update teleport animation
        if self.is_teleporting:
            self.teleport_animation_timer -= delta_time
            if self.teleport_animation_timer <= 0:
                self.is_teleporting = False

        # Movement AI - move toward player
        if not self.is_teleporting:
            dx = player_position.x - self.position.x
            if abs(dx) > 50:  # Move if not too close
                direction = 1 if dx > 0 else -1
                self.velocity.x = direction * self.move_speed
                self.facing_right = direction > 0
            else:
                self.velocity.x = 0

        # Apply gravity
        if not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            self.velocity.y = min(self.velocity.y, self.max_fall_speed)

        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Ground collision
        if game_map:
            # Platform mode ground detection
            self.on_ground = False
            if self.position.y + self.height >= self.ground_y:
                self.position.y = self.ground_y - self.height
                self.velocity.y = 0
                self.on_ground = True

        # Attack - throw bleeding hearts
        self.attack_timer += delta_time
        if self.attack_timer >= self.attack_cooldown:
            self._throw_bleeding_heart(player_position)
            self.attack_timer = 0.0

    def _initiate_teleport(self, player_position: Vector2, game_map=None):
        """Initiate card flip teleport."""
        self.is_teleporting = True
        self.teleport_animation_timer = 0.5  # 0.5 second animation
        self.teleport_timer = 0.0

        # Teleport to random position near player (but not too close)
        offset_x = 200 if pygame.time.get_ticks() % 2 == 0 else -200
        self.position.x = player_position.x + offset_x
        logger.info("👑 The Red Queen teleports! (Card Flip)")

    def _throw_bleeding_heart(self, player_position: Vector2):
        """Throw a bleeding heart projectile at the player."""
        # TODO: Add heart projectile to game's projectile system
        logger.info("💔 Red Queen throws a bleeding heart!")

    def get_bounds(self) -> pygame.Rect:
        """Get bounding box for collision detection."""
        return pygame.Rect(int(self.position.x), int(self.position.y), self.width, self.height)


class WannaCryBoss:
    """
    WannaCry Boss - "Wade" the Crying Water Character.

    Themed after the 2017 WannaCry ransomware, depicted as an emotional
    water element character (inspired by Wade from Pixar's Elemental) who
    constantly cries tears that spread like the worm-like ransomware.
    """

    def __init__(self, position: Vector2):
        """
        Initialize the WannaCry Wade boss.

        Args:
            position: Starting position for the boss
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.name = "WANNACRY - WADE THE WEEPER"

        # Boss dimensions (60x80 base + 30px glow = ~120x140 total)
        self.width = 60
        self.height = 80
        self.effect_radius = 30  # Watery glow

        # Health
        self.health = 150
        self.max_health = 150
        self.is_defeated = False

        # Movement - flows like water
        self.move_speed = 60.0
        self.facing_right = True

        # Physics
        self.gravity = 1200.0
        self.max_fall_speed = 600.0
        self.on_ground = False
        self.ground_y = 0

        # Crying mechanics
        self.tear_particles = []  # Falling tears
        self.tear_spawn_timer = 0.0
        self.puddles = []  # Tear puddles on ground (max 10)
        self.max_puddles = 10

        # Sob wave attack
        self.sob_timer = 0.0
        self.sob_cooldown = 12.0  # Phase 1: every 12 seconds
        self.is_sobbing = False
        self.sob_charge_timer = 0.0
        self.sob_wave = None  # Active sob wave

        # Tear projectile attacks
        self.attack_timer = 0.0
        self.attack_cooldown = 3.0  # Phase 1: every 3 seconds

        # Visual effects
        self.wobble_timer = 0.0
        self.glow_pulse_timer = 0.0
        self.is_flashing = False
        self.flash_timer = 0.0
        self.animation_frame = 0
        self.animation_timer = 0.0

        # Emotional phase system
        self.current_phase = 1  # 1: Sniffling, 2: Crying, 3: Ugly Crying

        # Create visuals
        self.sprite_frames = self._create_wade_sprites()
        self.sprite = self.sprite_frames[0]  # Default to first frame
        self.glow_sprite = self._create_watery_glow()

    def _create_wade_sprites(self) -> List[pygame.Surface]:
        """Create animated water blob sprites (Wade/Valery water character style)."""
        frames = []

        # Create 3 frames for wobble animation
        for frame_idx in range(3):
            # Create fully transparent surface
            sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            sprite.fill((0, 0, 0, 0))  # Fill with fully transparent

            # Water colors - rich cyan/blue palette with depth
            water_base = (25, 180, 200)  # Rich cyan
            water_dark = (15, 120, 140)  # Deep cyan
            water_bright = (100, 230, 255)  # Bright cyan
            water_highlight = (180, 245, 255)  # Very light cyan
            water_shadow = (10, 80, 100)  # Dark shadow
            outline_color = (5, 140, 160)  # Darker outline

            center_x, center_y = self.width // 2, self.height // 2

            # Wobble offset for animation
            wobble = [0, -2, 2][frame_idx]

            # === MAIN BODY (Organic blob shape) ===
            # Lower body - flowing blob shape with curves
            body_points = [
                (center_x, center_y + 30 + wobble),  # Bottom center
                (center_x - 20, center_y + 25 + wobble // 2),  # Bottom left curve
                (center_x - 25, center_y + 10),  # Mid left bulge
                (center_x - 22, center_y - 5),  # Upper left
                (center_x - 15, center_y - 15),  # Shoulder left
                (center_x, center_y - 18),  # Neck
                (center_x + 15, center_y - 15),  # Shoulder right
                (center_x + 22, center_y - 5),  # Upper right
                (center_x + 25, center_y + 10),  # Mid right bulge
                (center_x + 20, center_y + 25 + wobble // 2),  # Bottom right curve
            ]
            # Only draw with water_base - remove the dark layer behind
            pygame.draw.polygon(sprite, water_base, body_points)

            # Body outline for definition
            pygame.draw.lines(sprite, outline_color, True, body_points, 2)

            # === WAVY WATER HAIR (Multiple flowing blobs) ===
            # Left hair blob
            hair_left = [
                (center_x - 15, center_y - 18),
                (center_x - 25, center_y - 22),
                (center_x - 28, center_y - 30),
                (center_x - 22, center_y - 38),
                (center_x - 12, center_y - 35),
            ]
            pygame.draw.polygon(sprite, water_base, hair_left)
            pygame.draw.lines(sprite, water_bright, False, hair_left, 2)

            # Right hair blob
            hair_right = [
                (center_x + 15, center_y - 18),
                (center_x + 25, center_y - 22),
                (center_x + 28, center_y - 30),
                (center_x + 22, center_y - 38),
                (center_x + 12, center_y - 35),
            ]
            pygame.draw.polygon(sprite, water_base, hair_right)
            pygame.draw.lines(sprite, water_bright, False, hair_right, 2)

            # Center hair blob (tallest)
            hair_center = [
                (center_x - 8, center_y - 35),
                (center_x - 5, center_y - 45),
                (center_x, center_y - 48 - wobble),
                (center_x + 5, center_y - 45),
                (center_x + 8, center_y - 35),
            ]
            pygame.draw.polygon(sprite, water_bright, hair_center)

            # === INTERNAL WATER FLOW PATTERNS ===
            # Flowing curves inside body to show water movement
            flow_curves = [
                # Left flow
                [
                    (center_x - 18, center_y - 8),
                    (center_x - 15, center_y),
                    (center_x - 12, center_y + 8),
                    (center_x - 8, center_y + 15),
                ],
                # Right flow
                [
                    (center_x + 18, center_y - 8),
                    (center_x + 15, center_y),
                    (center_x + 12, center_y + 8),
                    (center_x + 8, center_y + 15),
                ],
                # Center swirl
                [
                    (center_x - 5, center_y + 5),
                    (center_x, center_y + 10),
                    (center_x + 5, center_y + 15),
                ],
            ]
            for curve in flow_curves:
                pygame.draw.lines(sprite, (*water_highlight, 100), False, curve, 2)

            # === WATER DROPLETS AROUND CHARACTER ===
            droplet_positions = [
                (center_x - 30, center_y - 10),
                (center_x + 30, center_y - 5),
                (center_x - 25, center_y + 18),
                (center_x + 28, center_y + 20),
                (center_x - 15, center_y - 40),
                (center_x + 18, center_y - 38),
            ]
            for dx, dy in droplet_positions:
                pygame.draw.circle(sprite, water_bright, (dx, dy), 3)
                pygame.draw.circle(sprite, water_highlight, (dx - 1, dy - 1), 1)

            # Sad mouth (downturned curve)
            mouth_y = center_y + 5
            mouth_curve = [
                (center_x - 10, mouth_y),
                (center_x - 5, mouth_y + 3),
                (center_x, mouth_y + 4),
                (center_x + 5, mouth_y + 3),
                (center_x + 10, mouth_y),
            ]
            pygame.draw.lines(sprite, water_shadow, False, mouth_curve, 3)

            # === HIGHLIGHTS AND DEPTH ===
            # Large highlight on left side for wet shiny look
            highlight_points = [
                (center_x - 15, center_y - 5),
                (center_x - 10, center_y - 10),
                (center_x - 8, center_y),
                (center_x - 12, center_y + 8),
            ]
            for i, point in enumerate(highlight_points):
                alpha = 60 - (i * 10)
                pygame.draw.circle(sprite, (*water_highlight, alpha), point, 8 - i)

            # Shadow on right side for depth
            shadow_points = [
                (center_x + 18, center_y + 5),
                (center_x + 15, center_y + 15),
            ]
            for point in shadow_points:
                pygame.draw.circle(sprite, (*water_shadow, 40), point, 6)

            # === FACE (drawn last so it's on top) ===
            # Large expressive eyes
            eye_y = center_y - 8
            # Left eye - large with multiple layers
            pygame.draw.circle(sprite, (255, 255, 255), (center_x - 10, eye_y), 7)
            pygame.draw.circle(sprite, (100, 150, 200), (center_x - 10, eye_y), 5)
            pygame.draw.circle(sprite, (20, 40, 80), (center_x - 10, eye_y + 1), 3)
            # Eye shine (bright highlight)
            pygame.draw.circle(sprite, water_highlight, (center_x - 12, eye_y - 2), 2)
            pygame.draw.circle(sprite, (255, 255, 255), (center_x - 7, eye_y - 1), 1)

            # Right eye
            pygame.draw.circle(sprite, (255, 255, 255), (center_x + 10, eye_y), 7)
            pygame.draw.circle(sprite, (100, 150, 200), (center_x + 10, eye_y), 5)
            pygame.draw.circle(sprite, (20, 40, 80), (center_x + 10, eye_y + 1), 3)
            pygame.draw.circle(sprite, water_highlight, (center_x + 12, eye_y - 2), 2)
            pygame.draw.circle(sprite, (255, 255, 255), (center_x + 13, eye_y - 1), 1)

            # Tear streams (flowing down from eyes)
            tear_stream_left = [
                (center_x - 10, eye_y + 5),
                (center_x - 11, eye_y + 15),
                (center_x - 10, eye_y + 25),
            ]
            pygame.draw.lines(sprite, (*water_bright, 180), False, tear_stream_left, 3)

            tear_stream_right = [
                (center_x + 10, eye_y + 5),
                (center_x + 11, eye_y + 15),
                (center_x + 10, eye_y + 25),
            ]
            pygame.draw.lines(sprite, (*water_bright, 180), False, tear_stream_right, 3)

            frames.append(sprite)

        return frames

    def _create_watery_glow(self) -> pygame.Surface:
        """Create rippling watery glow effect."""
        glow_width = self.width + (self.effect_radius * 2)
        glow_height = self.height + (self.effect_radius * 2)
        glow = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        glow.fill((0, 0, 0, 0))  # Fill with fully transparent

        center_x, center_y = glow_width // 2, glow_height // 2

        # Cyan/blue water glow rings
        glow_colors = [
            (0, 255, 255, 20),  # Cyan (outermost)
            (135, 206, 235, 35),  # Sky blue
            (0, 206, 209, 50),  # Dark turquoise (innermost)
        ]

        for i, color in enumerate(glow_colors):
            radius = self.effect_radius - (i * 10)
            pygame.draw.circle(glow, color, (center_x, center_y), radius)

        return glow

    def take_damage(self, damage: int) -> bool:
        """Take damage and cry harder."""
        if self.is_defeated:
            return True

        self.health -= damage
        self.is_flashing = True
        self.flash_timer = 0.2

        # Cry more when damaged!
        for _ in range(8):
            self._spawn_tear_particle()

        # Check phase transitions (gets more emotional)
        if self.health <= 100 and self.current_phase == 1:
            self.current_phase = 2
            self.attack_cooldown = 2.0  # Faster tears
            self.sob_cooldown = 8.0  # More frequent sobs
            logger.info("😭 WannaCry Phase 2: Uncontrollable Crying!")
        elif self.health <= 50 and self.current_phase == 2:
            self.current_phase = 3
            self.attack_cooldown = 1.0  # Rapid tears
            self.sob_cooldown = 5.0  # Constant sobbing
            self.move_speed = 80.0  # Running while crying
            logger.info("😭 WannaCry Phase 3: UGLY CRYING!!!")

        if self.health <= 0:
            self.health = 0
            self.is_defeated = True
            logger.info("💧 Wade has cried himself out...")
            return True

        return False

    def _spawn_tear_particle(self):
        """Spawn a falling tear droplet."""
        # Tears fall from eyes
        tear = {
            "x": self.position.x + self.width // 2 + (10 if time.time() % 2 < 1 else -10),
            "y": self.position.y + 25,  # Eye level
            "vx": (time.time() % 40 - 20) * 2,  # Slight horizontal spread
            "vy": 100.0,  # Falling speed
            "lifetime": 2.0,
            "alpha": 255,
            "on_ground": False,
        }
        self.tear_particles.append(tear)

    def _trigger_sob_wave(self):
        """Trigger the sob wave attack."""
        self.is_sobbing = True
        self.sob_charge_timer = 1.0  # 1 second charge time

        # Create sob wave
        self.sob_wave = {
            "x": self.position.x + self.width // 2,
            "y": self.position.y + self.height // 2,
            "radius": 0,
            "max_radius": 300,
            "lifetime": 1.0,
            "alpha": 255,
            "active": False,  # Becomes active after charge
        }
        logger.info("😭 WAAAAHHH! Wade unleashes a sob wave!")

    def _create_puddle(self, x: float, y: float):
        """Create a tear puddle on the ground."""
        if len(self.puddles) >= self.max_puddles:
            self.puddles.pop(0)  # Remove oldest puddle

        puddle = {"x": x, "y": y, "lifetime": 5.0, "alpha": 200, "radius": 20}
        self.puddles.append(puddle)

    def update(self, delta_time: float, player_position: Vector2, game_map=None) -> None:
        """Update boss logic."""
        if self.is_defeated:
            return

        # Update flash effect
        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.is_flashing = False

        # Update animation frame (wobble)
        self.animation_timer += delta_time
        if self.animation_timer >= 0.3:
            self.animation_timer = 0.0
            self.animation_frame = (self.animation_frame + 1) % 3
            self.sprite = self.sprite_frames[self.animation_frame]

        # Update glow pulse
        self.glow_pulse_timer += delta_time

        # Update wobble
        self.wobble_timer += delta_time

        # Constant crying - spawn tears periodically
        self.tear_spawn_timer += delta_time
        tears_per_second = 2 + (self.current_phase - 1) * 2  # More tears in higher phases
        if self.tear_spawn_timer >= (1.0 / tears_per_second):
            self._spawn_tear_particle()
            self.tear_spawn_timer = 0.0

        # Update tear particles
        for tear in self.tear_particles[:]:
            tear["lifetime"] -= delta_time
            tear["x"] += tear["vx"] * delta_time
            tear["y"] += tear["vy"] * delta_time
            tear["vy"] += 300.0 * delta_time  # Gravity
            tear["alpha"] = int(255 * (tear["lifetime"] / 2.0))

            # Check if tear hit ground
            if game_map and tear["y"] >= self.ground_y and not tear["on_ground"]:
                tear["on_ground"] = True
                self._create_puddle(tear["x"], tear["y"])

            if tear["lifetime"] <= 0:
                self.tear_particles.remove(tear)

        # Update puddles
        for puddle in self.puddles[:]:
            puddle["lifetime"] -= delta_time
            puddle["alpha"] = int(200 * (puddle["lifetime"] / 5.0))
            if puddle["lifetime"] <= 0:
                self.puddles.remove(puddle)

        # Sob wave attack
        if not self.is_sobbing:
            self.sob_timer += delta_time
            if self.sob_timer >= self.sob_cooldown:
                self._trigger_sob_wave()
                self.sob_timer = 0.0
        else:
            # Charging sob
            if self.sob_charge_timer > 0:
                self.sob_charge_timer -= delta_time
                if self.sob_charge_timer <= 0:
                    # Release sob wave!
                    self.sob_wave["active"] = True

            # Update active sob wave
            if self.sob_wave and self.sob_wave["active"]:
                self.sob_wave["lifetime"] -= delta_time
                expand_speed = 600.0  # pixels per second
                self.sob_wave["radius"] += expand_speed * delta_time
                self.sob_wave["alpha"] = int(255 * (self.sob_wave["lifetime"] / 1.0))

                if self.sob_wave["lifetime"] <= 0:
                    self.sob_wave = None
                    self.is_sobbing = False

        # Movement AI - chase player while crying
        if not self.is_sobbing:  # Can't move while sobbing
            dx = player_position.x - self.position.x
            if abs(dx) > 50:
                direction = 1 if dx > 0 else -1
                self.velocity.x = direction * self.move_speed
                self.facing_right = direction > 0
            else:
                self.velocity.x = 0

        # Apply gravity
        if not self.on_ground:
            self.velocity.y += self.gravity * delta_time
            self.velocity.y = min(self.velocity.y, self.max_fall_speed)

        # Update position
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Ground collision
        if game_map:
            self.on_ground = False
            if self.position.y + self.height >= self.ground_y:
                self.position.y = self.ground_y - self.height
                self.velocity.y = 0
                self.on_ground = True

        # Tear projectile attacks
        self.attack_timer += delta_time
        if self.attack_timer >= self.attack_cooldown:
            self._throw_tear(player_position)
            self.attack_timer = 0.0

    def _throw_tear(self, player_position: Vector2):
        """Throw a tear projectile at player."""
        # TODO: Integrate with game projectile system
        logger.info("💧 Wade throws a tear!")

    def get_bounds(self) -> pygame.Rect:
        """Get bounding box for collision detection."""
        return pygame.Rect(int(self.position.x), int(self.position.y), self.width, self.height)

    def get_sob_wave_bounds(self) -> Optional[pygame.Rect]:
        """Get sob wave collision bounds if active."""
        if self.sob_wave and self.sob_wave["active"]:
            radius = int(self.sob_wave["radius"])
            return pygame.Rect(
                int(self.sob_wave["x"] - radius),
                int(self.sob_wave["y"] - radius),
                radius * 2,
                radius * 2,
            )
        return None


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
        # Create Heartbleed Red Queen boss
        x = level_width // 2  # Center of level
        y = ground_y - 100  # Start slightly above ground
        boss = HeartbleedBoss(Vector2(x, y))
        boss.ground_y = ground_y
        return boss
    elif boss_type == BossType.WANNACRY:
        # Create WannaCry Wade boss
        x = level_width // 2  # Center of level
        y = ground_y - 100  # Start slightly above ground
        boss = WannaCryBoss(Vector2(x, y))
        boss.ground_y = ground_y
        return boss

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
                "Moved laterally through cloud environments",
            ],
            "victims": "MGM Resorts, Caesars Entertainment, Okta customers",
            "prevention": [
                "Just-In-Time (JIT) access limits credential exposure",
                "Session token monitoring and anomaly detection",
                "Phishing-resistant MFA (passkeys, FIDO2)",
                "Help desk verification protocols",
                "Cloud Permissions Firewall to limit lateral movement",
            ],
            "mechanic": "Defeat all 5 spiders to win!\nEach spider represents a different attack vector.",
            "sonrai_tie_in": "THREAT VECTORS: Credential Theft, Lateral Movement, Account Takeover\nUnused identities are prime targets for social engineering attacks!",
        }

    elif boss_type == BossType.HEARTBLEED:
        return {
            "title": "👑💔 THE RED QUEEN APPROACHES! 💔👑",
            "description": "Heartbleed (CVE-2014-0160) was a catastrophic OpenSSL vulnerability discovered in 2014\nthat leaked SENSITIVE DATA directly from server memory - like a bleeding heart.",
            "how_attacked": [
                "Exploited OpenSSL heartbeat extension flaw",
                "Leaked 64KB of memory per heartbeat request",
                "Stole encryption keys, passwords, and session tokens",
                "Affected 17% of all secure web servers worldwide",
                "Could be exploited without leaving traces in logs",
            ],
            "victims": "Yahoo, Amazon, Google, NSA, Canadian Revenue Agency, hospitals worldwide",
            "prevention": [
                "Immediate OpenSSL patching (1.0.1g or later)",
                "Revoke and reissue ALL SSL/TLS certificates",
                "Force password resets for all users",
                "Memory-safe cryptographic libraries",
                "Regular security audits of open source dependencies",
                "Secret rotation and key management best practices",
            ],
            "mechanic": "The Red Queen has 3 phases based on health!\nWatch for bleeding particles and card-flip teleports.\nOFF WITH YOUR HEAD!",
            "sonrai_tie_in": "THREAT VECTORS: Data Exfiltration, Credential Theft\nOverprivileged roles with SecretsManagerReadWrite leak sensitive data!",
        }

    elif boss_type == BossType.WANNACRY:
        return {
            "title": "😭💧 WANNACRY APPEARS! 💧😭",
            "description": "WannaCry was a devastating ransomware worm in May 2017 that spread globally\nlike tears, encrypting files and demanding Bitcoin ransoms.",
            "how_attacked": [
                "Exploited EternalBlue (MS17-010) Windows SMB vulnerability",
                "Worm-like self-propagation across networks",
                "Encrypted user files with RSA-2048 encryption",
                "Displayed ransom note demanding $300-600 in Bitcoin",
                "Spread to 150+ countries in just 4 days",
            ],
            "victims": "UK NHS (80 trusts), FedEx, Telefónica, Deutsche Bahn - 200,000+ computers, $4B damages",
            "prevention": [
                "Patch MS17-010 immediately (critical security update)",
                "Disable SMBv1 protocol on all systems",
                "Network segmentation to prevent lateral movement",
                "Regular offline backups (ransomware protection)",
                "Email filtering and security awareness training",
                "Cloud Permissions Firewall to limit blast radius",
            ],
            "mechanic": "Wade cries tears that spread like WannaCry ransomware!\nAvoid sob waves and don't stand in puddles.\nThe more you hurt him, the more he cries!",
            "sonrai_tie_in": "THREAT VECTORS: Ransomware, Lateral Movement, Data Destruction\nUnused credentials enable worm-like spread across your cloud!",
        }

    elif boss_type == BossType.VOLT_TYPHOON:
        return {
            "title": "⚡🌀 VOLT TYPHOON EMERGES! 🌀⚡",
            "description": "Volt Typhoon is a Chinese state-sponsored APT group targeting critical infrastructure\nusing 'living off the land' techniques to avoid detection.",
            "how_attacked": [
                "Exploited internet-facing devices (Fortinet, Ivanti)",
                "Used legitimate admin tools to blend in",
                "Established persistent access for future operations",
                "Targeted energy, water, and communications sectors",
                "Pre-positioned for potential destructive attacks",
            ],
            "victims": "US critical infrastructure, Guam military bases, telecommunications providers",
            "prevention": [
                "Monitor for anomalous use of admin tools",
                "Implement network segmentation",
                "Regular third-party access audits",
                "Cloud Permissions Firewall blocks unauthorized access",
                "Service Control Policies (SCPs) limit blast radius",
            ],
            "mechanic": "Volt Typhoon uses stealth attacks!\nWatch for lightning strikes and wind gusts.\nIt hides among legitimate traffic!",
            "sonrai_tie_in": "THREAT VECTORS: Persistence, Lateral Movement, Resource Abuse\nThird-party integrations are APT entry points - block unknown vendors!",
        }

    elif boss_type == BossType.BLACKCAT:
        return {
            "title": "🐱‍👤 BLACKCAT PROWLS! 🐱‍👤",
            "description": "BlackCat (ALPHV) was a sophisticated Ransomware-as-a-Service operation\nthat pioneered triple extortion and public data leak sites.",
            "how_attacked": [
                "Recruited affiliates through criminal forums",
                "Exploited compromised credentials and VPNs",
                "Used Rust-based ransomware for cross-platform attacks",
                "Triple extortion: encrypt, steal, DDoS",
                "Published stolen data on dark web leak sites",
            ],
            "victims": "MGM Resorts, Reddit, Western Digital, healthcare organizations",
            "prevention": [
                "Eliminate unused service accounts",
                "Implement least privilege access",
                "Regular credential rotation",
                "Offline backups with tested recovery",
                "Cloud Permissions Firewall prevents lateral movement",
            ],
            "mechanic": "BlackCat has 9 lives!\nEach life represents a different attack phase.\nWatch for pounce attacks and data theft claws!",
            "sonrai_tie_in": "THREAT VECTORS: Ransomware, Credential Theft, Data Exfiltration\nService accounts with S3FullAccess enable massive data theft!",
        }

    elif boss_type == BossType.MIDNIGHT_BLIZZARD:
        return {
            "title": "❄️🌙 MIDNIGHT BLIZZARD DESCENDS! 🌙❄️",
            "description": "Midnight Blizzard (APT29/Cozy Bear) is a Russian state-sponsored group\nresponsible for the SolarWinds supply chain attack.",
            "how_attacked": [
                "Compromised SolarWinds Orion build process",
                "Distributed malware to 18,000+ organizations",
                "Targeted government agencies and tech companies",
                "Used OAuth tokens for persistent access",
                "Exfiltrated emails from Microsoft executives",
            ],
            "victims": "US Treasury, DHS, Microsoft, SolarWinds customers worldwide",
            "prevention": [
                "Audit all third-party integrations",
                "Monitor OAuth token usage",
                "Implement zero-trust architecture",
                "Regular supply chain security reviews",
                "Cloud Permissions Firewall controls third-party access",
            ],
            "mechanic": "Midnight Blizzard attacks from the shadows!\nWatch for ice storms and blinding snow.\nIt targets your most privileged accounts!",
            "sonrai_tie_in": "THREAT VECTORS: Account Takeover, Persistence, Privilege Escalation\nAdmin roles are nation-state targets - apply JIT protection!",
        }

    elif boss_type == BossType.SANDWORM:
        return {
            "title": "🪱🏜️ SANDWORM RISES! 🏜️🪱",
            "description": "Sandworm (Unit 74455) is a Russian military cyber unit responsible for\nthe most destructive cyberattacks in history, including NotPetya.",
            "how_attacked": [
                "NotPetya: $10B in damages, disguised as ransomware",
                "Attacked Ukrainian power grid (2015, 2016)",
                "Olympic Destroyer targeted 2018 Winter Olympics",
                "Industroyer malware designed for industrial systems",
                "Wiper malware destroys data without recovery option",
            ],
            "victims": "Maersk, Merck, FedEx, Ukrainian infrastructure, global organizations",
            "prevention": [
                "Comprehensive identity governance",
                "Network segmentation and air gaps",
                "Incident response planning and testing",
                "Regular security assessments",
                "Cloud Permissions Firewall as last line of defense",
            ],
            "mechanic": "FINAL BOSS: Sandworm controls the entire organization!\nIt spawns mini-worms and triggers org-wide outages.\nDefeat it to save your cloud!",
            "sonrai_tie_in": "THREAT VECTORS: Data Destruction, Lateral Movement, Resource Abuse\nOrg-wide identity sprawl enables catastrophic attacks - clean up ALL zombies!",
        }

    # Default fallback
    return {
        "title": "BOSS BATTLE",
        "description": "A powerful enemy approaches!",
        "how_attacked": [],
        "victims": "",
        "prevention": [],
        "mechanic": "Defeat the boss to continue!",
        "sonrai_tie_in": "Unused identities are attack vectors. Eliminate them all!",
    }
