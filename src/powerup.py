"""AWS-themed power-up system for platformer gameplay."""

import pygame
import random
from enum import Enum
from typing import Optional

from models import Vector2


class PowerUpType(Enum):
    """Types of AWS-themed power-ups."""
    STAR_POWER = "Star Power"              # Invincibility + quarantine on touch (best power-up)
    LAMBDA_SPEED = "Lambda Speedup"        # Move faster
    LASER_BEAM = "Laser Beam"              # 10 seconds continuous fire (arcade mode)
    BURST_SHOT = "Burst Shot"              # 3 one-shot kills (arcade mode)


class PowerUp:
    """Collectible AWS-themed power-up."""

    def __init__(self, position: Vector2, powerup_type: PowerUpType):
        """
        Initialize a power-up.

        Args:
            position: World position of the power-up
            powerup_type: Type of power-up
        """
        self.position = position
        self.powerup_type = powerup_type
        self.width = 32
        self.height = 32
        self.collected = False

        # Effect properties
        self.duration = self._get_duration()
        self.effect_value = self._get_effect_value()

        # Animation
        self.bounce_offset = 0
        self.bounce_speed = 2.0  # Speed of bounce animation

        # Create sprite
        self.sprite = self._create_sprite()

    def _get_duration(self) -> float:
        """Get the duration of this power-up effect in seconds."""
        durations = {
            PowerUpType.STAR_POWER: 10.0,      # 10 seconds invincibility + quarantine
            PowerUpType.LAMBDA_SPEED: 12.0,    # 12 seconds speed boost
            PowerUpType.LASER_BEAM: 10.0,      # 10 seconds continuous fire
            PowerUpType.BURST_SHOT: 0.0,       # Instant (3 charges)
        }
        return durations.get(self.powerup_type, 10.0)

    def _get_effect_value(self) -> float:
        """Get the effect multiplier/value for this power-up."""
        values = {
            PowerUpType.STAR_POWER: 1.0,       # Invincibility + quarantine on touch
            PowerUpType.LAMBDA_SPEED: 2.0,     # 2x speed multiplier
            PowerUpType.LASER_BEAM: 1.0,       # Continuous fire enabled
            PowerUpType.BURST_SHOT: 3.0,       # 3 one-shot kills
        }
        return values.get(self.powerup_type, 1.0)

    def get_description(self) -> str:
        """Get a friendly description of what this power-up does."""
        descriptions = {
            PowerUpType.STAR_POWER: "10 seconds of untouchable status - any zombie you contact will be quarantined!",
            PowerUpType.LAMBDA_SPEED: "Move 2x faster for 12 seconds with Lambda speed!",
            PowerUpType.LASER_BEAM: "10 seconds of continuous laser fire - no reload needed!",
            PowerUpType.BURST_SHOT: "3 one-shot eliminations - instant kills!",
        }
        return descriptions.get(self.powerup_type, "Power-up collected!")

    def _create_sprite(self) -> pygame.Surface:
        """Create a retro 8-bit AWS-themed power-up sprite."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # AWS Orange
        AWS_ORANGE = (255, 153, 0)
        AWS_DARK = (200, 100, 0)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GOLD = (255, 215, 0)

        # Type-specific colors
        colors = {
            PowerUpType.STAR_POWER: ((255, 215, 0), (200, 170, 0)),         # Gold star (best power)
            PowerUpType.LAMBDA_SPEED: ((255, 153, 0), (200, 120, 0)),       # Orange (serverless)
            PowerUpType.LASER_BEAM: ((255, 0, 0), (180, 0, 0)),             # Red (laser)
            PowerUpType.BURST_SHOT: ((138, 43, 226), (100, 30, 180)),       # Purple (burst)
        }

        primary_color, shadow_color = colors.get(self.powerup_type, (AWS_ORANGE, AWS_DARK))

        # Star power gets special 5-pointed star shape
        if self.powerup_type == PowerUpType.STAR_POWER:
            # Draw a 5-pointed star
            import math
            center_x, center_y = 16, 16
            outer_radius = 14
            inner_radius = 6

            # Draw star outline
            star_points = []
            for i in range(10):
                angle = (i * 36 - 90) * math.pi / 180  # 36 degrees per point, start at top
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                star_points.append((x, y))

            # Draw filled star
            pygame.draw.polygon(sprite, shadow_color, star_points)
            pygame.draw.polygon(sprite, primary_color, [(x-1, y-1) for x, y in star_points])
            pygame.draw.polygon(sprite, BLACK, star_points, 2)

            # Add sparkle effect
            sparkle_positions = [(4, 4), (28, 4), (4, 28), (28, 28), (16, 2)]
            for sx, sy in sparkle_positions:
                pygame.draw.circle(sprite, WHITE, (sx, sy), 2)
        else:
            # Draw AWS-style badge/token for other power-ups
            # Outer ring
            pygame.draw.circle(sprite, shadow_color, (16, 16), 14)
            pygame.draw.circle(sprite, primary_color, (16, 16), 12)
            pygame.draw.circle(sprite, BLACK, (16, 16), 12, 2)

            # Type-specific icons
            font = pygame.font.Font(None, 16)
            icons = {
                PowerUpType.LAMBDA_SPEED: "λ",
                PowerUpType.LASER_BEAM: "⚡",
                PowerUpType.BURST_SHOT: "💥",
            }

            icon_text = icons.get(self.powerup_type, "?")
            text_surface = font.render(icon_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(16, 16))
            sprite.blit(text_surface, text_rect)

            # Sparkle effect (small dots around badge)
            sparkle_positions = [(4, 6), (28, 6), (4, 26), (28, 26)]
            for sx, sy in sparkle_positions:
                pygame.draw.circle(sprite, GOLD, (sx, sy), 2)

        return sprite

    def update(self, delta_time: float) -> None:
        """
        Update power-up animation.

        Args:
            delta_time: Time elapsed since last frame
        """
        # Bounce animation
        self.bounce_offset += self.bounce_speed * delta_time
        if self.bounce_offset > 6.28:  # 2*pi
            self.bounce_offset = 0

    def get_bounds(self) -> pygame.Rect:
        """Get bounding rectangle for collision detection."""
        import math
        bounce_y = int(math.sin(self.bounce_offset * 2) * 5)
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y + bounce_y),
            self.width,
            self.height
        )

    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render the power-up with bounce animation.

        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if self.collected:
            return

        import math
        bounce_y = int(math.sin(self.bounce_offset * 2) * 5)

        screen_x = int(self.position.x - camera_x)
        screen_y = int(self.position.y - camera_y + bounce_y)

        screen.blit(self.sprite, (screen_x, screen_y))


class PowerUpManager:
    """Manages active power-up effects on the player."""

    def __init__(self):
        """Initialize the power-up manager."""
        self.active_effects = {}  # {PowerUpType: (remaining_time, effect_value)}

    def activate(self, powerup: PowerUp) -> None:
        """
        Activate a power-up effect.

        Args:
            powerup: The power-up that was collected
        """
        if powerup.duration > 0:
            # Timed effect - store in active effects
            self.active_effects[powerup.powerup_type] = {
                'time_remaining': powerup.duration,
                'value': powerup.effect_value
            }

        # Instant effects are handled immediately by the game engine
        # (e.g., SECURITY_GROUP adds health directly)

    def update(self, delta_time: float) -> None:
        """
        Update active power-up timers.

        Args:
            delta_time: Time elapsed since last frame
        """
        # Update timers and remove expired effects
        expired = []
        for powerup_type, effect in self.active_effects.items():
            effect['time_remaining'] -= delta_time
            if effect['time_remaining'] <= 0:
                expired.append(powerup_type)

        for powerup_type in expired:
            del self.active_effects[powerup_type]

    def is_active(self, powerup_type: PowerUpType) -> bool:
        """Check if a power-up effect is currently active."""
        return powerup_type in self.active_effects

    def get_effect_value(self, powerup_type: PowerUpType) -> Optional[float]:
        """Get the effect value of an active power-up."""
        if powerup_type in self.active_effects:
            return self.active_effects[powerup_type]['value']
        return None

    def get_remaining_time(self, powerup_type: PowerUpType) -> float:
        """Get remaining time for an active power-up effect."""
        if powerup_type in self.active_effects:
            return self.active_effects[powerup_type]['time_remaining']
        return 0.0


def spawn_random_powerups(level_width: int, ground_y: int, count: int = 5, arcade_mode: bool = False) -> list[PowerUp]:
    """
    Spawn random power-ups across the level.

    Args:
        level_width: Width of the level
        ground_y: Y position of the ground
        count: Number of power-ups to spawn
        arcade_mode: If True, favor arcade power-ups (LASER_BEAM, BURST_SHOT)

    Returns:
        List of PowerUp instances
    """
    powerups = []
    
    if arcade_mode:
        # Arcade mode: higher chance of LASER_BEAM and BURST_SHOT
        arcade_types = [PowerUpType.LASER_BEAM, PowerUpType.BURST_SHOT, PowerUpType.STAR_POWER]
        powerup_types = arcade_types
    else:
        # Normal mode: all power-ups
        powerup_types = list(PowerUpType)

    for i in range(count):
        # Distribute power-ups across the level width
        x = random.randint(100, level_width - 100)
        y = ground_y - 100  # Spawn above ground level

        # Random power-up type
        powerup_type = random.choice(powerup_types)

        powerup = PowerUp(Vector2(x, y), powerup_type)
        powerups.append(powerup)

    return powerups
