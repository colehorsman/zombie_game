"""Boss fighter for Mortal Kombat-style boss battles.

Implements boss-specific attacks and AI behavior.

**Feature: multi-genre-levels**
**Validates: Requirements 12.1, 12.2, 12.3, 12.5, 14.1-14.6**
"""

import logging
import random
from dataclasses import dataclass
from typing import List, Optional

import pygame

from models import Attack, BossAIState, FighterState, Vector2

logger = logging.getLogger(__name__)


@dataclass
class BossAttackData:
    """Data for a boss-specific attack."""

    name: str
    damage: int
    range: int
    cooldown: float
    description: str


# Boss attack definitions
BOSS_ATTACKS = {
    "scattered_spider": [
        BossAttackData("Web Strike", 15, 80, 0.5, "Shoots web projectile"),
        BossAttackData("Credential Theft", 25, 60, 1.0, "Steals credentials"),
        BossAttackData("Social Engineering", 35, 100, 2.0, "Manipulates target"),
    ],
    "heartbleed": [
        BossAttackData("Memory Leak", 12, 70, 0.4, "Drains memory"),
        BossAttackData("Data Bleed", 20, 90, 0.8, "Extracts data"),
        BossAttackData("Buffer Overflow", 40, 120, 2.5, "Crashes systems"),
    ],
    "wannacry": [
        BossAttackData("Encrypt Strike", 18, 75, 0.6, "Encrypts files"),
        BossAttackData("Ransom Demand", 22, 85, 1.2, "Demands payment"),
        BossAttackData("Worm Spread", 30, 150, 3.0, "Spreads to others"),
    ],
    "default": [
        BossAttackData("Punch", 10, 50, 0.3, "Basic punch"),
        BossAttackData("Kick", 15, 70, 0.5, "Basic kick"),
        BossAttackData("Special", 25, 100, 2.0, "Special attack"),
    ],
}


class BossFighter:
    """Boss character for boss battles with AI.

    **Property 18: Boss AI Aggression Scaling**
    Aggression increases as boss health decreases.
    **Validates: Requirements 14.4**
    """

    def __init__(
        self,
        x: float,
        y: float,
        boss_type: str = "default",
        max_health: int = 150,
    ):
        """Initialize the boss fighter.

        Args:
            x: Initial X position
            y: Initial Y position
            boss_type: Type of boss for attacks
            max_health: Maximum health
        """
        self.position = Vector2(x, y)
        self.boss_type = boss_type

        # Health
        self.health = max_health
        self.max_health = max_health

        # State
        self.state = FighterState.IDLE
        self.ai_state = BossAIState.APPROACH
        self.facing_right = False  # Boss faces left (toward player)

        # Attacks
        self.attacks = BOSS_ATTACKS.get(boss_type, BOSS_ATTACKS["default"])
        self.attack_cooldowns = {attack.name: 0 for attack in self.attacks}
        self.current_attack: Optional[Attack] = None

        # AI parameters
        self.base_aggression = 0.3  # Base attack frequency
        self.move_speed = 150
        self.preferred_distance = 80  # Distance to maintain from player

        # State timers
        self.state_timer = 0
        self.hit_stun = 0
        self.ai_decision_timer = 0

        logger.info(f"BossFighter initialized: {boss_type}")

    def update(self, delta_time: float, player_position: Vector2) -> None:
        """Update boss state and AI.

        Args:
            delta_time: Time since last frame
            player_position: Player's current position
        """
        # Update cooldowns
        for name in self.attack_cooldowns:
            if self.attack_cooldowns[name] > 0:
                self.attack_cooldowns[name] -= delta_time

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

        # Update AI decision
        self.ai_decision_timer -= delta_time
        if self.ai_decision_timer <= 0 and self.state == FighterState.IDLE:
            self._make_ai_decision(player_position, delta_time)
            self.ai_decision_timer = 0.2  # Decision every 0.2 seconds

    def _end_action(self) -> None:
        """End current action."""
        self.current_attack = None
        if self.state not in (FighterState.HIT, FighterState.KO):
            self.state = FighterState.IDLE

    def _make_ai_decision(self, player_position: Vector2, delta_time: float) -> None:
        """Make AI decision based on current state.

        Args:
            player_position: Player's position
            delta_time: Time since last frame
        """
        if self.state != FighterState.IDLE:
            return

        distance = abs(self.position.x - player_position.x)
        aggression = self._get_aggression()

        # Update facing
        self.facing_right = player_position.x > self.position.x

        # Decision based on distance and aggression
        if distance > self.preferred_distance + 50:
            # Too far - approach
            self.ai_state = BossAIState.APPROACH
            self._move_toward_player(player_position, delta_time)
        elif distance < self.preferred_distance - 20:
            # Too close - retreat or attack
            if random.random() < aggression:
                self._try_attack(distance)
            else:
                self.ai_state = BossAIState.RETREAT
                self._move_away_from_player(player_position, delta_time)
        else:
            # Good distance - attack or block
            if random.random() < aggression:
                self._try_attack(distance)
            elif random.random() < 0.2:
                self.ai_state = BossAIState.BLOCK
                self.state = FighterState.BLOCKING
                self.state_timer = 0.5
            else:
                self.ai_state = BossAIState.TAUNT

    def _get_aggression(self) -> float:
        """Calculate current aggression based on health.

        Returns:
            Aggression value (0.0 to 1.0)
        """
        # Aggression increases as health decreases
        health_ratio = self.health / self.max_health
        aggression = self.base_aggression + (1 - health_ratio) * 0.5
        return min(0.9, aggression)

    def _move_toward_player(self, player_position: Vector2, delta_time: float) -> None:
        """Move toward the player."""
        self.state = FighterState.WALKING
        direction = 1 if player_position.x > self.position.x else -1
        self.position.x += direction * self.move_speed * delta_time

    def _move_away_from_player(
        self, player_position: Vector2, delta_time: float
    ) -> None:
        """Move away from the player."""
        self.state = FighterState.WALKING
        direction = -1 if player_position.x > self.position.x else 1
        self.position.x += direction * self.move_speed * delta_time

    def _try_attack(self, distance: float) -> Optional[Attack]:
        """Try to execute an attack.

        Args:
            distance: Distance to player

        Returns:
            Attack if successful, None otherwise
        """
        # Find available attacks in range
        available = [
            attack
            for attack in self.attacks
            if self.attack_cooldowns[attack.name] <= 0 and attack.range >= distance
        ]

        if not available:
            return None

        # Choose attack (prefer stronger attacks when low health)
        if self.health < self.max_health * 0.3:
            # Low health - use strongest available
            attack_data = max(available, key=lambda a: a.damage)
        else:
            # Normal - random selection weighted by damage
            attack_data = random.choice(available)

        return self._execute_attack(attack_data)

    def _execute_attack(self, attack_data: BossAttackData) -> Attack:
        """Execute a specific attack.

        Args:
            attack_data: Attack to execute

        Returns:
            Attack object
        """
        self.state = FighterState.PUNCHING  # Generic attack state
        self.state_timer = 0.4
        self.attack_cooldowns[attack_data.name] = attack_data.cooldown

        attack = Attack(
            damage=attack_data.damage,
            range=attack_data.range,
            type=attack_data.name,
            cooldown=attack_data.cooldown,
        )
        self.current_attack = attack
        return attack

    def take_damage(self, damage: int) -> int:
        """Take damage.

        Args:
            damage: Incoming damage

        Returns:
            Actual damage taken
        """
        if self.state == FighterState.KO:
            return 0

        # Blocking reduces damage
        if self.state == FighterState.BLOCKING:
            actual_damage = damage // 2
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
        return self.current_attack is not None

    def is_ko(self) -> bool:
        """Check if knocked out."""
        return self.state == FighterState.KO

    def reset(self, x: float, y: float) -> None:
        """Reset boss for new round."""
        self.position = Vector2(x, y)
        self.health = self.max_health
        self.state = FighterState.IDLE
        self.ai_state = BossAIState.APPROACH
        for name in self.attack_cooldowns:
            self.attack_cooldowns[name] = 0
        self.hit_stun = 0
        self.current_attack = None

    def get_attack_hitbox(self) -> Optional[pygame.Rect]:
        """Get hitbox for current attack."""
        if not self.current_attack:
            return None

        attack_range = self.current_attack.range
        if self.facing_right:
            return pygame.Rect(
                self.position.x,
                self.position.y - 40,
                attack_range,
                80,
            )
        else:
            return pygame.Rect(
                self.position.x - attack_range,
                self.position.y - 40,
                attack_range,
                80,
            )

    def get_bounds(self) -> pygame.Rect:
        """Get collision bounds."""
        return pygame.Rect(
            self.position.x - 30,
            self.position.y - 80,
            60,
            80,
        )

    def render(self, surface: pygame.Surface) -> None:
        """Render the boss."""
        # Color based on state
        if self.state == FighterState.BLOCKING:
            color = (100, 100, 255)
        elif self.state == FighterState.HIT:
            color = (255, 100, 100)
        elif self.state == FighterState.KO:
            color = (100, 100, 100)
        else:
            color = (200, 50, 50)  # Red for boss

        # Draw body
        body_rect = self.get_bounds()
        pygame.draw.rect(surface, color, body_rect)
        pygame.draw.rect(surface, (255, 255, 255), body_rect, 2)

        # Draw attack effect
        if self.is_attacking():
            attack_hitbox = self.get_attack_hitbox()
            if attack_hitbox:
                pygame.draw.rect(surface, (255, 100, 0), attack_hitbox, 2)

        # Draw facing indicator
        indicator_x = self.position.x + (15 if self.facing_right else -15)
        pygame.draw.circle(
            surface, (255, 255, 255), (int(indicator_x), int(self.position.y - 70)), 5
        )
