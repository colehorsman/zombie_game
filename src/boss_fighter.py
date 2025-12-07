"""Boss fighter for Mortal Kombat-style boss battles.

Each boss is a unique humanoid character with themed attacks and visual design.

**Feature: multi-genre-levels**
"""

import logging
import math
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
    effect_color: tuple = (255, 255, 255)  # Visual effect color


@dataclass
class BossDesign:
    """Visual design for a boss character."""

    name: str
    body_color: tuple  # Main body color
    accent_color: tuple  # Secondary color
    eye_color: tuple  # Eye color
    effect_color: tuple  # Attack effect color
    height: int = 80
    width: int = 40


# Boss designs - humanoid characters for each threat type
BOSS_DESIGNS = {
    # Level 1 - Sandbox: Script Kiddie (green hoodie hacker)
    "script_kiddie": BossDesign(
        name="SCRIPT KIDDIE",
        body_color=(50, 150, 50),  # Green hoodie
        accent_color=(30, 100, 30),
        eye_color=(255, 255, 0),  # Yellow eyes
        effect_color=(0, 255, 0),  # Green effects
    ),
    # Level 2 - Stage: Phishing Master (blue suit, fish-like)
    "phishing_master": BossDesign(
        name="PHISHING MASTER",
        body_color=(30, 100, 180),  # Blue suit
        accent_color=(20, 70, 140),
        eye_color=(0, 255, 255),  # Cyan eyes
        effect_color=(0, 200, 255),  # Blue effects
    ),
    # Level 3 - Automation: Bot Herder (gray/silver robotic)
    "bot_herder": BossDesign(
        name="BOT HERDER",
        body_color=(120, 120, 130),  # Metallic gray
        accent_color=(80, 80, 90),
        eye_color=(255, 0, 0),  # Red eyes
        effect_color=(200, 200, 220),  # Silver effects
    ),
    # Level 4 - WebApp: SQL Injector (purple hacker)
    "sql_injector": BossDesign(
        name="SQL INJECTOR",
        body_color=(100, 50, 150),  # Purple
        accent_color=(70, 30, 110),
        eye_color=(255, 0, 255),  # Magenta eyes
        effect_color=(200, 100, 255),  # Purple effects
    ),
    # Level 5 - Production Data: Heartbleed (red, bleeding heart theme)
    "heartbleed": BossDesign(
        name="HEARTBLEED",
        body_color=(180, 30, 30),  # Dark red
        accent_color=(120, 20, 20),
        eye_color=(255, 200, 200),  # Pink eyes
        effect_color=(255, 0, 0),  # Red blood effects
    ),
    # Level 6 - Production: Scattered Spider (all black, spider theme)
    "scattered_spider": BossDesign(
        name="SCATTERED SPIDER",
        body_color=(20, 20, 25),  # Near black
        accent_color=(40, 40, 50),
        eye_color=(255, 0, 0),  # Red spider eyes
        effect_color=(100, 0, 100),  # Dark purple web
    ),
    # Level 7 - Org: WannaCry (blue, crying/water theme)
    "wannacry": BossDesign(
        name="WANNACRY",
        body_color=(50, 100, 200),  # Blue
        accent_color=(30, 70, 150),
        eye_color=(150, 200, 255),  # Light blue teary eyes
        effect_color=(100, 180, 255),  # Water/tear effects
    ),
    "default": BossDesign(
        name="CYBER THREAT",
        body_color=(150, 50, 50),
        accent_color=(100, 30, 30),
        eye_color=(255, 255, 0),
        effect_color=(255, 100, 0),
    ),
}

# Boss attacks - themed for each character
BOSS_ATTACKS = {
    "script_kiddie": [
        BossAttackData("Copy Paste", 8, 60, 0.4, "Copies your moves", (0, 255, 0)),
        BossAttackData(
            "Stack Overflow", 15, 80, 0.8, "Throws code snippets", (100, 255, 100)
        ),
        BossAttackData("GitHub Leak", 25, 120, 2.0, "Exposes secrets", (0, 200, 0)),
    ],
    "phishing_master": [
        BossAttackData("Bait Hook", 10, 70, 0.5, "Throws phishing hook", (0, 200, 255)),
        BossAttackData(
            "Fake Email", 18, 90, 1.0, "Sends malicious email", (0, 150, 255)
        ),
        BossAttackData(
            "Identity Theft", 30, 100, 2.5, "Steals your identity", (0, 255, 255)
        ),
    ],
    "bot_herder": [
        BossAttackData("Bot Swarm", 12, 100, 0.6, "Sends bot army", (200, 200, 220)),
        BossAttackData(
            "DDoS Blast", 20, 150, 1.2, "Overwhelming traffic", (255, 255, 255)
        ),
        BossAttackData(
            "Zombie Horde", 35, 200, 3.0, "Massive bot attack", (180, 180, 200)
        ),
    ],
    "sql_injector": [
        BossAttackData("DROP TABLE", 15, 80, 0.5, "Deletes your data", (200, 100, 255)),
        BossAttackData(
            "UNION SELECT", 22, 100, 1.0, "Extracts secrets", (150, 50, 200)
        ),
        BossAttackData("'; --", 40, 120, 2.5, "Ultimate injection", (255, 0, 255)),
    ],
    "heartbleed": [
        BossAttackData(
            "Memory Bleed", 12, 70, 0.4, "Drains your memory", (255, 100, 100)
        ),
        BossAttackData(
            "Data Hemorrhage", 20, 90, 0.8, "Massive data leak", (255, 50, 50)
        ),
        BossAttackData(
            "Heart Attack", 35, 120, 2.0, "Critical system failure", (255, 0, 0)
        ),
    ],
    "scattered_spider": [
        BossAttackData("Web Trap", 10, 80, 0.5, "Throws sticky web", (100, 0, 100)),
        BossAttackData(
            "Spider Swarm", 18, 100, 1.0, "Spawns mini spiders", (80, 0, 80)
        ),
        BossAttackData("Venom Strike", 30, 60, 2.0, "Poisonous bite", (150, 0, 150)),
    ],
    "wannacry": [
        BossAttackData("Tear Drop", 10, 70, 0.4, "Throws tears", (100, 180, 255)),
        BossAttackData(
            "Encrypt Wave", 20, 100, 1.0, "Encrypts your files", (50, 150, 255)
        ),
        BossAttackData(
            "Ransom Flood", 35, 150, 2.5, "Drowns in ransomware", (0, 100, 255)
        ),
    ],
    "default": [
        BossAttackData("Punch", 10, 50, 0.3, "Basic punch", (255, 100, 0)),
        BossAttackData("Kick", 15, 70, 0.5, "Basic kick", (255, 150, 0)),
        BossAttackData("Special", 25, 100, 2.0, "Special attack", (255, 200, 0)),
    ],
}

# Map level numbers to boss types
LEVEL_BOSS_MAP = {
    1: "script_kiddie",
    2: "phishing_master",
    3: "bot_herder",
    4: "sql_injector",
    5: "heartbleed",
    6: "scattered_spider",
    7: "wannacry",
}


class BossFighter:
    """Humanoid boss character for Mortal Kombat-style battles."""

    def __init__(
        self,
        x: float,
        y: float,
        boss_type: str = "default",
        max_health: int = 150,
    ):
        """Initialize the boss fighter."""
        self.position = Vector2(x, y)
        self.boss_type = boss_type
        self.design = BOSS_DESIGNS.get(boss_type, BOSS_DESIGNS["default"])

        # Health
        self.health = max_health
        self.max_health = max_health

        # State
        self.state = FighterState.IDLE
        self.ai_state = BossAIState.APPROACH
        self.facing_right = False

        # Attacks
        self.attacks = BOSS_ATTACKS.get(boss_type, BOSS_ATTACKS["default"])
        self.attack_cooldowns = {attack.name: 0.0 for attack in self.attacks}
        self.current_attack: Optional[Attack] = None

        # AI parameters
        self.base_aggression = 0.3
        self.move_speed = 150
        self.preferred_distance = 80

        # State timers
        self.state_timer = 0.0
        self.hit_stun = 0.0
        self.ai_decision_timer = 0.0

        # Animation
        self.animation_timer = 0.0
        self.effect_particles: List[dict] = []

        logger.info(f"BossFighter initialized: {self.design.name}")

    def update(self, delta_time: float, player_position: Vector2) -> None:
        """Update boss state and AI."""
        # Update animation
        self.animation_timer += delta_time

        # Update effect particles
        self._update_particles(delta_time)

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
            self.ai_decision_timer = 0.2

    def _update_particles(self, delta_time: float) -> None:
        """Update effect particles."""
        for particle in self.effect_particles[:]:
            particle["life"] -= delta_time
            particle["x"] += particle["vx"] * delta_time
            particle["y"] += particle["vy"] * delta_time
            if particle["life"] <= 0:
                self.effect_particles.remove(particle)

    def _spawn_attack_particles(self) -> None:
        """Spawn particles for current attack."""
        if not self.current_attack:
            return

        color = self.design.effect_color
        direction = 1 if self.facing_right else -1

        for _ in range(5):
            self.effect_particles.append(
                {
                    "x": self.position.x + direction * 30,
                    "y": self.position.y - 40 + random.randint(-20, 20),
                    "vx": direction * random.randint(100, 200),
                    "vy": random.randint(-50, 50),
                    "life": 0.3,
                    "color": color,
                    "size": random.randint(3, 8),
                }
            )

    def _end_action(self) -> None:
        """End current action."""
        self.current_attack = None
        if self.state not in (FighterState.HIT, FighterState.KO):
            self.state = FighterState.IDLE

    def _make_ai_decision(self, player_position: Vector2, delta_time: float) -> None:
        """Make AI decision based on current state."""
        if self.state != FighterState.IDLE:
            return

        distance = abs(self.position.x - player_position.x)
        aggression = self._get_aggression()

        self.facing_right = player_position.x > self.position.x

        if distance > self.preferred_distance + 50:
            self.ai_state = BossAIState.APPROACH
            self._move_toward_player(player_position, delta_time)
        elif distance < self.preferred_distance - 20:
            if random.random() < aggression:
                self._try_attack(distance)
            else:
                self.ai_state = BossAIState.RETREAT
                self._move_away_from_player(player_position, delta_time)
        else:
            if random.random() < aggression:
                self._try_attack(distance)
            elif random.random() < 0.2:
                self.ai_state = BossAIState.BLOCK
                self.state = FighterState.BLOCKING
                self.state_timer = 0.5
            else:
                self.ai_state = BossAIState.TAUNT

    def _get_aggression(self) -> float:
        """Calculate aggression based on health."""
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
        """Try to execute an attack."""
        available = [
            attack
            for attack in self.attacks
            if self.attack_cooldowns[attack.name] <= 0 and attack.range >= distance
        ]

        if not available:
            return None

        if self.health < self.max_health * 0.3:
            attack_data = max(available, key=lambda a: a.damage)
        else:
            attack_data = random.choice(available)

        return self._execute_attack(attack_data)

    def _execute_attack(self, attack_data: BossAttackData) -> Attack:
        """Execute a specific attack."""
        self.state = FighterState.PUNCHING
        self.state_timer = 0.4
        self.attack_cooldowns[attack_data.name] = attack_data.cooldown

        attack = Attack(
            damage=attack_data.damage,
            range=attack_data.range,
            type=attack_data.name,
            cooldown=attack_data.cooldown,
        )
        self.current_attack = attack
        self._spawn_attack_particles()
        return attack

    def take_damage(self, damage: int) -> int:
        """Take damage."""
        if self.state == FighterState.KO:
            return 0

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
            self.attack_cooldowns[name] = 0.0
        self.hit_stun = 0.0
        self.current_attack = None
        self.effect_particles.clear()

    def get_attack_hitbox(self) -> Optional[pygame.Rect]:
        """Get hitbox for current attack."""
        if not self.current_attack:
            return None

        attack_range = self.current_attack.range
        if self.facing_right:
            return pygame.Rect(self.position.x, self.position.y - 40, attack_range, 80)
        return pygame.Rect(
            self.position.x - attack_range, self.position.y - 40, attack_range, 80
        )

    def get_bounds(self) -> pygame.Rect:
        """Get collision bounds."""
        return pygame.Rect(
            self.position.x - self.design.width // 2,
            self.position.y - self.design.height,
            self.design.width,
            self.design.height,
        )

    def render(self, surface: pygame.Surface) -> None:
        """Render the humanoid boss character."""
        x = int(self.position.x)
        y = int(self.position.y)
        design = self.design

        # Determine colors based on state
        if self.state == FighterState.BLOCKING:
            body_color = (100, 100, 200)
        elif self.state == FighterState.HIT:
            body_color = (255, 150, 150)
        elif self.state == FighterState.KO:
            body_color = (80, 80, 80)
        else:
            body_color = design.body_color

        # Animation bob
        bob = int(math.sin(self.animation_timer * 5) * 2)

        # Draw legs
        leg_y = y - 5
        leg_spread = 8 if self.state == FighterState.WALKING else 5
        pygame.draw.rect(
            surface, design.accent_color, (x - leg_spread - 4, leg_y - 25, 8, 25)
        )
        pygame.draw.rect(
            surface, design.accent_color, (x + leg_spread - 4, leg_y - 25, 8, 25)
        )

        # Draw body (torso)
        torso_y = y - 55 + bob
        pygame.draw.rect(surface, body_color, (x - 15, torso_y, 30, 35))

        # Draw arms
        arm_y = torso_y + 5
        arm_offset = 0
        if self.is_attacking():
            arm_offset = 20 if self.facing_right else -20

        # Left arm
        pygame.draw.rect(surface, body_color, (x - 22, arm_y, 8, 25))
        # Right arm (extended if attacking)
        if self.facing_right and self.is_attacking():
            pygame.draw.rect(surface, body_color, (x + 14, arm_y, 8 + arm_offset, 10))
        else:
            pygame.draw.rect(surface, body_color, (x + 14, arm_y, 8, 25))

        # Draw head
        head_y = torso_y - 25 + bob
        pygame.draw.ellipse(surface, body_color, (x - 12, head_y, 24, 28))

        # Draw eyes
        eye_y = head_y + 10
        eye_spacing = 6
        pygame.draw.circle(surface, design.eye_color, (x - eye_spacing, eye_y), 4)
        pygame.draw.circle(surface, design.eye_color, (x + eye_spacing, eye_y), 4)
        # Pupils
        pupil_offset = 2 if self.facing_right else -2
        pygame.draw.circle(
            surface, (0, 0, 0), (x - eye_spacing + pupil_offset, eye_y), 2
        )
        pygame.draw.circle(
            surface, (0, 0, 0), (x + eye_spacing + pupil_offset, eye_y), 2
        )

        # Boss-specific details
        self._render_boss_details(surface, x, y, head_y, bob)

        # Draw attack effect
        if self.is_attacking():
            hitbox = self.get_attack_hitbox()
            if hitbox:
                pygame.draw.rect(surface, design.effect_color, hitbox, 2)

        # Draw effect particles
        for particle in self.effect_particles:
            pygame.draw.circle(
                surface,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

    def _render_boss_details(
        self, surface: pygame.Surface, x: int, y: int, head_y: int, bob: int
    ) -> None:
        """Render boss-specific visual details."""
        design = self.design

        if self.boss_type == "scattered_spider":
            # Spider legs on back
            for i in range(4):
                angle = math.pi / 6 + i * math.pi / 8
                leg_len = 15 + i * 3
                lx = x - 15 - int(math.cos(angle) * leg_len)
                ly = y - 45 + int(math.sin(angle) * leg_len)
                pygame.draw.line(surface, (60, 60, 70), (x - 15, y - 45), (lx, ly), 2)
                # Right side
                rx = x + 15 + int(math.cos(angle) * leg_len)
                pygame.draw.line(surface, (60, 60, 70), (x + 15, y - 45), (rx, ly), 2)

        elif self.boss_type == "wannacry":
            # Tears streaming down
            tear_y = head_y + 18 + int(self.animation_timer * 30) % 20
            pygame.draw.ellipse(surface, (100, 180, 255), (x - 10, tear_y, 4, 6))
            pygame.draw.ellipse(surface, (100, 180, 255), (x + 6, tear_y, 4, 6))

        elif self.boss_type == "heartbleed":
            # Bleeding heart on chest
            heart_y = y - 45 + bob
            pygame.draw.polygon(
                surface,
                (255, 0, 0),
                [
                    (x, heart_y + 10),
                    (x - 8, heart_y),
                    (x - 5, heart_y - 5),
                    (x, heart_y),
                    (x + 5, heart_y - 5),
                    (x + 8, heart_y),
                ],
            )
            # Blood drips
            drip_y = heart_y + 10 + int(self.animation_timer * 20) % 15
            pygame.draw.ellipse(surface, (200, 0, 0), (x - 2, drip_y, 4, 6))

        elif self.boss_type == "bot_herder":
            # Antenna on head
            pygame.draw.line(surface, (200, 200, 220), (x, head_y), (x, head_y - 15), 2)
            pygame.draw.circle(surface, (255, 0, 0), (x, head_y - 15), 4)

        elif self.boss_type == "phishing_master":
            # Fish hook in hand
            hook_x = x + 25 if self.facing_right else x - 25
            pygame.draw.arc(
                surface, (200, 200, 200), (hook_x - 5, y - 50, 10, 15), 0, math.pi, 2
            )

        elif self.boss_type == "sql_injector":
            # Code symbols floating
            font = pygame.font.Font(None, 16)
            symbols = ["';", "--", "OR", "1=1"]
            for i, sym in enumerate(symbols):
                sym_y = (
                    y - 70 - i * 12 + int(math.sin(self.animation_timer * 3 + i) * 5)
                )
                text = font.render(sym, True, design.effect_color)
                surface.blit(text, (x - 10 + i * 5, sym_y))
