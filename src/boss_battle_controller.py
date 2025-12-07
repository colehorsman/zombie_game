"""Boss Battle Controller for Mortal Kombat-style fighting.

Manages the complete boss battle flow including VS screen, rounds,
combat, and victory/defeat handling.

**Feature: multi-genre-levels**
**Validates: Requirements 5.1, 5.2, 5.6, 5.7, 5.8, 11.1, 11.3, 11.4**
"""

import logging
from typing import Callable, Optional

import pygame

from boss_fighter import BossFighter
from fighting_arena import FightingArena
from genre_controller import GenreController, GenreControllerFactory, InputState
from models import CombatState, GenreType, Vector2
from player_fighter import PlayerFighter

logger = logging.getLogger(__name__)


class BossBattleController(GenreController):
    """Controller for Mortal Kombat-style boss battles.

    **Property 13: Boss Arena Transition**
    Transition to arena and return to original level.
    **Validates: Requirements 5.1, 5.8, 11.1**

    **Property 15: Boss Timer Behavior**
    Timer counts down from 99, zero determines winner by health.
    **Validates: Requirements 11.3, 11.4**

    **Property 19: Victory Quarantine Trigger**
    Boss defeat triggers quarantine animation and API call.
    **Validates: Requirements 5.6**

    **Property 20: Defeat Retry Option**
    Player defeat shows retry option.
    **Validates: Requirements 5.7**
    """

    # Battle constants
    ROUNDS_TO_WIN = 2
    VS_SCREEN_DURATION = 2.0
    ROUND_START_DURATION = 1.5
    ROUND_END_DURATION = 2.0
    VICTORY_DURATION = 3.0

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the boss battle controller.

        Args:
            genre: Should be GenreType.FIGHTING
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        super().__init__(genre, screen_width, screen_height)

        # Arena
        self.arena: Optional[FightingArena] = None

        # Fighters
        self.player_fighter: Optional[PlayerFighter] = None
        self.boss_fighter: Optional[BossFighter] = None

        # Battle state
        self.combat_state = CombatState.VS_SCREEN
        self.state_timer = 0

        # Round tracking
        self.current_round = 1
        self.player_rounds_won = 0
        self.boss_rounds_won = 0

        # Boss info
        self.boss_type = "default"
        self.boss_name = "BOSS"
        self.boss_srn: Optional[str] = None

        # Callbacks
        self.on_victory: Optional[Callable] = None
        self.on_defeat: Optional[Callable] = None
        self.on_return: Optional[Callable] = None

        # Return level info
        self.return_level_id: Optional[str] = None

        logger.info("BossBattleController initialized")

    def initialize_level(
        self, account_id: str, zombies: list, level_width: int, level_height: int
    ) -> None:
        """Initialize is not used for boss battles - use start_boss_battle instead."""
        pass

    def start_boss_battle(
        self,
        boss_type: str,
        boss_name: str,
        boss_srn: Optional[str] = None,
        return_level_id: Optional[str] = None,
    ) -> None:
        """Start a boss battle.

        Args:
            boss_type: Type of boss (scattered_spider, heartbleed, wannacry)
            boss_name: Display name for the boss
            boss_srn: Sonrai Resource Name for quarantine
            return_level_id: Level to return to after battle
        """
        self.boss_type = boss_type
        self.boss_name = boss_name
        self.boss_srn = boss_srn
        self.return_level_id = return_level_id

        # Create arena
        self.arena = FightingArena(self.screen_width, self.screen_height, boss_type)

        # Create fighters
        floor_y = self.arena.get_floor_y()
        arena_left, arena_right = self.arena.get_arena_bounds()

        self.player_fighter = PlayerFighter(arena_left + 50, floor_y)
        self.boss_fighter = BossFighter(arena_right - 50, floor_y, boss_type)

        # Reset state
        self.combat_state = CombatState.VS_SCREEN
        self.state_timer = self.VS_SCREEN_DURATION
        self.current_round = 1
        self.player_rounds_won = 0
        self.boss_rounds_won = 0

        self.is_initialized = True
        logger.info(f"Boss battle started: {boss_name} ({boss_type})")

    def update(self, delta_time: float, player) -> None:
        """Update boss battle state.

        Args:
            delta_time: Time since last frame
            player: Player entity (not used, we have player_fighter)
        """
        if not self.is_initialized:
            return

        # Update state timer
        self.state_timer -= delta_time

        if self.combat_state == CombatState.VS_SCREEN:
            if self.state_timer <= 0:
                self._start_round()

        elif self.combat_state == CombatState.ROUND_START:
            if self.state_timer <= 0:
                self.combat_state = CombatState.FIGHTING
                self.arena.start_round()

        elif self.combat_state == CombatState.FIGHTING:
            self._update_combat(delta_time)

        elif self.combat_state == CombatState.ROUND_END:
            if self.state_timer <= 0:
                self._check_battle_end()

        elif self.combat_state in (CombatState.VICTORY, CombatState.DEFEAT):
            if self.state_timer <= 0:
                self._handle_battle_end()

    def _start_round(self) -> None:
        """Start a new round."""
        self.combat_state = CombatState.ROUND_START
        self.state_timer = self.ROUND_START_DURATION

        # Reset fighters
        floor_y = self.arena.get_floor_y()
        arena_left, arena_right = self.arena.get_arena_bounds()

        self.player_fighter.reset(arena_left + 50, floor_y)
        self.boss_fighter.reset(arena_right - 50, floor_y)

        logger.info(f"Round {self.current_round} starting")

    def _update_combat(self, delta_time: float) -> None:
        """Update combat during fighting state."""
        # Update arena timer
        timer_result = self.arena.update(delta_time)

        # Update fighters
        self.player_fighter.update(delta_time)
        self.boss_fighter.update(delta_time, self.player_fighter.position)

        # Check attack collisions
        self._check_attack_collisions()

        # Check round end conditions
        if self.player_fighter.is_ko():
            self._end_round(player_won=False)
        elif self.boss_fighter.is_ko():
            self._end_round(player_won=True)
        elif timer_result == "timeout":
            # Time out - winner by health
            player_won = self.player_fighter.health > self.boss_fighter.health
            self._end_round(player_won=player_won)

    def _check_attack_collisions(self) -> None:
        """Check for attack-fighter collisions."""
        # Player attacking boss
        if self.player_fighter.is_attacking():
            attack_hitbox = self.player_fighter.get_attack_hitbox()
            boss_bounds = self.boss_fighter.get_bounds()

            if attack_hitbox and attack_hitbox.colliderect(boss_bounds):
                if self.player_fighter.current_attack:
                    damage = self.player_fighter.current_attack.damage
                    self.boss_fighter.take_damage(damage)
                    self.player_fighter.current_attack = None  # Prevent multi-hit

        # Boss attacking player
        if self.boss_fighter.is_attacking():
            attack_hitbox = self.boss_fighter.get_attack_hitbox()
            player_bounds = self.player_fighter.get_bounds()

            if attack_hitbox and attack_hitbox.colliderect(player_bounds):
                if self.boss_fighter.current_attack:
                    damage = self.boss_fighter.current_attack.damage
                    self.player_fighter.take_damage(damage)
                    self.boss_fighter.current_attack = None

    def _end_round(self, player_won: bool) -> None:
        """End the current round.

        Args:
            player_won: Whether the player won this round
        """
        self.arena.stop_timer()
        self.combat_state = CombatState.ROUND_END
        self.state_timer = self.ROUND_END_DURATION

        if player_won:
            self.player_rounds_won += 1
            self.arena.player_rounds_won = self.player_rounds_won
        else:
            self.boss_rounds_won += 1
            self.arena.boss_rounds_won = self.boss_rounds_won

        logger.info(
            f"Round {self.current_round} ended. "
            f"Player: {self.player_rounds_won}, Boss: {self.boss_rounds_won}"
        )

    def _check_battle_end(self) -> None:
        """Check if battle is over or start next round."""
        if self.player_rounds_won >= self.ROUNDS_TO_WIN:
            self.combat_state = CombatState.VICTORY
            self.state_timer = self.VICTORY_DURATION
            self.is_complete = True
            logger.info("Player wins the battle!")

        elif self.boss_rounds_won >= self.ROUNDS_TO_WIN:
            self.combat_state = CombatState.DEFEAT
            self.state_timer = self.VICTORY_DURATION
            logger.info("Boss wins the battle!")

        else:
            self.current_round += 1
            self._start_round()

    def _handle_battle_end(self) -> None:
        """Handle battle end - trigger callbacks."""
        if self.combat_state == CombatState.VICTORY:
            if self.on_victory:
                self.on_victory(self.boss_srn)
        elif self.combat_state == CombatState.DEFEAT:
            if self.on_defeat:
                self.on_defeat()

        # Transition to returning state
        self.combat_state = CombatState.RETURNING

    def handle_input(self, input_state: InputState, player) -> None:
        """Handle player input during boss battle.

        Args:
            input_state: Current input state
            player: Player entity (not used)
        """
        if self.combat_state != CombatState.FIGHTING:
            return

        if not self.player_fighter:
            return

        # Movement
        direction = 0
        if input_state.left:
            direction = -1
        elif input_state.right:
            direction = 1

        arena_bounds = self.arena.get_arena_bounds()
        self.player_fighter.move(direction, 0.016, arena_bounds)  # Approximate delta

        # Attacks
        if input_state.punch:
            self.player_fighter.punch()
        elif input_state.kick:
            self.player_fighter.kick()
        elif input_state.special:
            self.player_fighter.special_move()

        # Blocking
        if input_state.block:
            self.player_fighter.block()
        else:
            self.player_fighter.stop_block()

    def check_completion(self) -> bool:
        """Check if boss battle is complete."""
        return self.is_complete

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render the boss battle.

        Args:
            surface: Surface to render on
            camera_offset: Camera offset (ignored)
        """
        if not self.is_initialized or not self.arena:
            return

        # Render arena with health bars
        player_health = self.player_fighter.health if self.player_fighter else 0
        player_max = self.player_fighter.max_health if self.player_fighter else 100
        boss_health = self.boss_fighter.health if self.boss_fighter else 0
        boss_max = self.boss_fighter.max_health if self.boss_fighter else 100

        self.arena.render(
            surface,
            player_health,
            player_max,
            boss_health,
            boss_max,
            "PLAYER",
            self.boss_name,
        )

        # Render fighters
        if self.player_fighter:
            self.player_fighter.render(surface)
        if self.boss_fighter:
            self.boss_fighter.render(surface)

        # Render state overlays
        self._render_state_overlay(surface)

    def _render_state_overlay(self, surface: pygame.Surface) -> None:
        """Render state-specific overlays."""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)

        if self.combat_state == CombatState.VS_SCREEN:
            # VS Screen
            vs_text = font_large.render("VS", True, (255, 255, 0))
            vs_rect = vs_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            surface.blit(vs_text, vs_rect)

            # Names
            player_text = font_medium.render("PLAYER", True, (0, 255, 0))
            player_rect = player_text.get_rect(center=(200, self.screen_height // 2))
            surface.blit(player_text, player_rect)

            boss_text = font_medium.render(self.boss_name, True, (255, 0, 0))
            boss_rect = boss_text.get_rect(
                center=(self.screen_width - 200, self.screen_height // 2)
            )
            surface.blit(boss_text, boss_rect)

        elif self.combat_state == CombatState.ROUND_START:
            round_text = font_large.render(
                f"ROUND {self.current_round}", True, (255, 255, 255)
            )
            round_rect = round_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            surface.blit(round_text, round_rect)

            fight_text = font_medium.render("FIGHT!", True, (255, 255, 0))
            fight_rect = fight_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 60)
            )
            surface.blit(fight_text, fight_rect)

        elif self.combat_state == CombatState.ROUND_END:
            if self.player_fighter and self.boss_fighter:
                if self.player_fighter.is_ko():
                    text = "BOSS WINS ROUND"
                    color = (255, 0, 0)
                elif self.boss_fighter.is_ko():
                    text = "PLAYER WINS ROUND"
                    color = (0, 255, 0)
                else:
                    text = "TIME OUT"
                    color = (255, 255, 0)

                result_text = font_large.render(text, True, color)
                result_rect = result_text.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 2)
                )
                surface.blit(result_text, result_rect)

        elif self.combat_state == CombatState.VICTORY:
            victory_text = font_large.render("VICTORY!", True, (0, 255, 0))
            victory_rect = victory_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            surface.blit(victory_text, victory_rect)

            quarantine_text = font_medium.render(
                "QUARANTINING THREAT...", True, (255, 255, 0)
            )
            quarantine_rect = quarantine_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 60)
            )
            surface.blit(quarantine_text, quarantine_rect)

        elif self.combat_state == CombatState.DEFEAT:
            defeat_text = font_large.render("DEFEATED", True, (255, 0, 0))
            defeat_rect = defeat_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            surface.blit(defeat_text, defeat_rect)

            retry_text = font_medium.render(
                "Press ENTER to retry", True, (255, 255, 255)
            )
            retry_rect = retry_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 60)
            )
            surface.blit(retry_text, retry_rect)

    def retry_battle(self) -> None:
        """Retry the boss battle after defeat."""
        if self.combat_state == CombatState.DEFEAT:
            self.start_boss_battle(
                self.boss_type,
                self.boss_name,
                self.boss_srn,
                self.return_level_id,
            )

    def is_returning(self) -> bool:
        """Check if battle is in returning state."""
        return self.combat_state == CombatState.RETURNING

    def is_defeated(self) -> bool:
        """Check if player was defeated."""
        return self.combat_state == CombatState.DEFEAT


# Register the boss battle controller with the factory
GenreControllerFactory.register(GenreType.FIGHTING, BossBattleController)
