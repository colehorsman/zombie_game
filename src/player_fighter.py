"""Player fighter for Mortal Kombat-style boss battles.

Handles player combat mechanics including punches, kicks, specials, and blocking.

**Feature: multi-genre-levels**
**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6**
"""

import logging
from dataclasses import dataclass
from typing import Optional

import pygame

from models import Attack, FighterState, Vector2

logger = logging.getLogger(__name__)


@dataclass
class FighterStats:
    """Combat statistics for a fighter."""

    max_health: int = 100
    punch_damage: int = 10
    kick_damage: int = 15
    special_damage: int = 30
    punch_range: int = 50
    kick_range: int = 70
    special_range: int = 100
    move_speed: int = 200
    block_reduction: float = 0.5  # 50% damage reduction when blocking


class PlayerFighter:
    """Player character for boss battles.

    **Property 16: Attack Damage Application**
    Successful attacks reduce target health by damage value.
    **Validates: Requirements 5.4, 5.5**

    **Property 17: Block Damage Reduction**
    Blocking reduces incoming damage by at least 50%.
    **Validates: Requirements 13.3**
    """

    def __init__(self, x: float, y: float, stats: Optional[FighterStats] = None):
        """Initialize the player fighter.

        Args:
            x: Initial X position
            y: Initial Y position
            stats: Combat statistics (uses defaults if None)
        """
        self.position = Vector2(x, y)
        self.stats = stats or FighterStats()

        # Health
        self.health = self.stats.max_health
        self.max_health = self.stats.max_health

        # State
        self.state = FighterState.IDLE
        self.facing_right = True

        # Attack cooldowns
        self.punch_cooldown = 0
        self.kick_cooldown = 0
        self.special_cooldown = 0

        # State timers
        self.state_timer = 0
        self.hit_stun = 0

        # Current attack (for collision detection)
        self.current_attack: Optional[Attack] = None

        logger.info("PlayerFighter initialized")

    def update(self, delta_time: float) -> None:
        """Update fighter state.

        Args:
            delta_time: Time since last frame
        """
        # Update cooldowns
        if self.punch_cooldown > 0:
            self.punch_cooldown -= delta_time
        if self.kick_cooldown > 0:
            self.kick_cooldown -= delta_time
        if self.special_cooldown > 0:
            self.special_cooldown -= delta_time

        # Update hit stun
        if self.hit_stun > 0:
            self.hit_stun -= delta_time
            if self.hit_stun <= 0:
                self.state = FighterState.IDLE

        # Update state timer
        if self.state_timer > 0:
            self.state_timer -= delta_time
            if self.state_timer <= 0:
                self._end_action()

    def _end_action(self) -> None:
        """End current action and return to idle."""
        self.current_attack = None
        if self.state not in (FighterState.HIT, FighterState.KO):
            self.state = FighterState.IDLE

    def move(self, direction: int, delta_time: float, arena_bounds: tuple) -> None:
        """Move the fighter.

        Args:
            direction: -1 for left, 1 for right, 0 for stop
            delta_time: Time since last frame
            arena_bounds: (left, right) boundaries
        """
        if self.state in (FighterState.HIT, FighterState.KO):
            return

        if direction != 0:
            self.state = FighterState.WALKING
            self.facing_right = direction > 0

            new_x = self.position.x + direction * self.stats.move_speed * delta_time
            left, right = arena_bounds
            self.position.x = max(left, min(right, new_x))
        elif self.state == FighterState.WALKING:
            self.state = FighterState.IDLE

    def punch(self) -> Optional[Attack]:
        """Execute a punch attack.

        Returns:
            Attack data if successful, None if on cooldown
        """
        if self.punch_cooldown > 0 or self.state in (FighterState.HIT, FighterState.KO):
            return None

        self.state = FighterState.PUNCHING
        self.state_timer = 0.2  # Punch duration
        self.punch_cooldown = 0.3

        attack = Attack(
            damage=self.stats.punch_damage,
            range=self.stats.punch_range,
            type="punch",
            cooldown=0.3,
        )
        self.current_attack = attack
        return attack

    def kick(self) -> Optional[Attack]:
        """Execute a kick attack.

        Returns:
            Attack data if successful, None if on cooldown
        """
        if self.kick_cooldown > 0 or self.state in (FighterState.HIT, FighterState.KO):
            return None

        self.state = FighterState.KICKING
        self.state_timer = 0.3  # Kick duration
        self.kick_cooldown = 0.5

        attack = Attack(
            damage=self.stats.kick_damage,
            range=self.stats.kick_range,
            type="kick",
            cooldown=0.5,
        )
        self.current_attack = attack
        return attack

    def special_move(self) -> Optional[Attack]:
        """Execute a special move.

        Returns:
            Attack data if successful, None if on cooldown
        """
        if self.special_cooldown > 0 or self.state in (
            FighterState.HIT,
            FighterState.KO,
        ):
            return None

        self.state = FighterState.SPECIAL
        self.state_timer = 0.5  # Special duration
        self.special_cooldown = 2.0  # Long cooldown

        attack = Attack(
            damage=self.stats.special_damage,
            range=self.stats.special_range,
            type="special",
            cooldown=2.0,
        )
        self.current_attack = attack
        return attack

    def block(self) -> None:
        """Start blocking."""
        if self.state not in (FighterState.HIT, FighterState.KO):
            self.state = FighterState.BLOCKING

    def stop_block(self) -> None:
        """Stop blocking."""
        if self.state == FighterState.BLOCKING:
            self.state = FighterState.IDLE

    def take_damage(self, damage: int) -> int:
        """Take damage, applying block reduction if blocking.

        Args:
            damage: Incoming damage amount

        Returns:
            Actual damage taken after reductions
        """
        if self.state == FighterState.KO:
            return 0

        # Apply block reduction
        if self.state == FighterState.BLOCKING:
            actual_damage = int(damage * (1 - self.stats.block_reduction))
        else:
            actual_damage = damage
            self.state = FighterState.HIT
            self.hit_stun = 0.3

        self.health -= actual_damage
        self.health = max(0, self.health)

        if self.health <= 0:
            self.state = FighterState.KO

        return actual_damage

    def is_attacking(self) -> bool:
        """Check if currently attacking."""
        return self.state in (
            FighterState.PUNCHING,
            FighterState.KICKING,
            FighterState.SPECIAL,
        )

    def is_blocking(self) -> bool:
        """Check if currently blocking."""
        return self.state == FighterState.BLOCKING

    def is_ko(self) -> bool:
        """Check if knocked out."""
        return self.state == FighterState.KO

    def reset(self, x: float, y: float) -> None:
        """Reset fighter for new round.

        Args:
            x: New X position
            y: New Y position
        """
        self.position = Vector2(x, y)
        self.health = self.max_health
        self.state = FighterState.IDLE
        self.punch_cooldown = 0
        self.kick_cooldown = 0
        self.special_cooldown = 0
        self.hit_stun = 0
        self.current_attack = None

    def get_attack_hitbox(self) -> Optional[pygame.Rect]:
        """Get the hitbox for current attack.

        Returns:
            Rect for attack hitbox, or None if not attacking
        """
        if not self.current_attack:
            return None

        attack_range = self.current_attack.range
        if self.facing_right:
            return pygame.Rect(
                self.position.x,
                self.position.y - 30,
                attack_range,
                60,
            )
        else:
            return pygame.Rect(
                self.position.x - attack_range,
                self.position.y - 30,
                attack_range,
                60,
            )

    def get_bounds(self) -> pygame.Rect:
        """Get fighter collision bounds."""
        return pygame.Rect(
            self.position.x - 20,
            self.position.y - 60,
            40,
            60,
        )

    def render(self, surface: pygame.Surface) -> None:
        """Render the fighter.

        Args:
            surface: Surface to render on
        """
        # Body color based on state
        if self.state == FighterState.BLOCKING:
            color = (100, 100, 255)  # Blue when blocking
        elif self.state == FighterState.HIT:
            color = (255, 100, 100)  # Red when hit
        elif self.state == FighterState.KO:
            color = (100, 100, 100)  # Gray when KO
        else:
            color = (0, 200, 100)  # Green normally

        # Draw body
        body_rect = self.get_bounds()
        pygame.draw.rect(surface, color, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 2)

        # Draw attack effect
        if self.is_attacking() and self.current_attack:
            attack_hitbox = self.get_attack_hitbox()
            if attack_hitbox:
                attack_color = (255, 255, 0, 128)  # Yellow
                pygame.draw.rect(surface, (255, 255, 0), attack_hitbox, 2)

        # Draw facing indicator
        indicator_x = self.position.x + (10 if self.facing_right else -10)
        pygame.draw.circle(
            surface, (255, 255, 255), (int(indicator_x), int(self.position.y - 50)), 5
        )
