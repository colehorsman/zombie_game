"""Fighting arena for Mortal Kombat-style boss battles.

Handles arena rendering, health bars, and round timer display.

**Feature: multi-genre-levels**
**Validates: Requirements 11.1, 11.2, 11.3**
"""

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

logger = logging.getLogger(__name__)


@dataclass
class ArenaTheme:
    """Visual theme for a boss arena."""

    name: str
    background_color: Tuple[int, int, int]
    floor_color: Tuple[int, int, int]
    accent_color: Tuple[int, int, int]
    description: str


# Arena themes for different boss types
ARENA_THEMES = {
    "scattered_spider": ArenaTheme(
        name="Dark Web",
        background_color=(20, 10, 30),
        floor_color=(40, 20, 60),
        accent_color=(128, 0, 255),
        description="A shadowy digital realm",
    ),
    "heartbleed": ArenaTheme(
        name="Memory Leak",
        background_color=(30, 0, 0),
        floor_color=(60, 10, 10),
        accent_color=(255, 0, 0),
        description="A corrupted memory space",
    ),
    "wannacry": ArenaTheme(
        name="Ransomware Vault",
        background_color=(10, 20, 10),
        floor_color=(20, 40, 20),
        accent_color=(0, 255, 0),
        description="An encrypted prison",
    ),
    "default": ArenaTheme(
        name="Cyber Arena",
        background_color=(10, 10, 30),
        floor_color=(30, 30, 60),
        accent_color=(0, 200, 255),
        description="A digital battleground",
    ),
}


class FightingArena:
    """Arena for boss battles with health bars and timer.

    **Property 14: Boss Health Bar Display**
    Health bars accurately reflect current health.
    **Validates: Requirements 11.2**
    """

    # Arena dimensions
    FLOOR_Y = 500  # Y position of the floor
    ARENA_LEFT = 50  # Left boundary
    ARENA_RIGHT = 750  # Right boundary

    # Health bar dimensions
    HEALTH_BAR_WIDTH = 300
    HEALTH_BAR_HEIGHT = 25
    HEALTH_BAR_Y = 30

    # Timer settings
    ROUND_TIME = 99  # Seconds per round

    def __init__(
        self, screen_width: int, screen_height: int, boss_type: str = "default"
    ):
        """Initialize the fighting arena.

        Args:
            screen_width: Width of the screen
            screen_height: Height of the screen
            boss_type: Type of boss for theming
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.theme = ARENA_THEMES.get(boss_type, ARENA_THEMES["default"])

        # Timer state
        self.time_remaining = self.ROUND_TIME
        self.timer_active = False

        # Round state
        self.current_round = 1
        self.player_rounds_won = 0
        self.boss_rounds_won = 0

        logger.info(f"FightingArena initialized with theme: {self.theme.name}")

    def start_round(self) -> None:
        """Start a new round."""
        self.time_remaining = self.ROUND_TIME
        self.timer_active = True
        logger.info(f"Round {self.current_round} started")

    def stop_timer(self) -> None:
        """Stop the round timer."""
        self.timer_active = False

    def update(self, delta_time: float) -> Optional[str]:
        """Update arena state.

        Args:
            delta_time: Time since last frame

        Returns:
            "timeout" if timer reached zero, None otherwise
        """
        if self.timer_active:
            self.time_remaining -= delta_time
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.timer_active = False
                return "timeout"
        return None

    def render(
        self,
        surface: pygame.Surface,
        player_health: int,
        player_max_health: int,
        boss_health: int,
        boss_max_health: int,
        player_name: str = "PLAYER",
        boss_name: str = "BOSS",
    ) -> None:
        """Render the arena with health bars and timer.

        Args:
            surface: Pygame surface to render on
            player_health: Current player health
            player_max_health: Maximum player health
            boss_health: Current boss health
            boss_max_health: Maximum boss health
            player_name: Display name for player
            boss_name: Display name for boss
        """
        # Render background
        self._render_background(surface)

        # Render floor
        self._render_floor(surface)

        # Render health bars
        self._render_health_bar(
            surface,
            50,  # Left side
            self.HEALTH_BAR_Y,
            player_health,
            player_max_health,
            player_name,
            align_left=True,
        )

        self._render_health_bar(
            surface,
            self.screen_width - 50 - self.HEALTH_BAR_WIDTH,  # Right side
            self.HEALTH_BAR_Y,
            boss_health,
            boss_max_health,
            boss_name,
            align_left=False,
        )

        # Render timer
        self._render_timer(surface)

        # Render round indicator
        self._render_round_indicator(surface)

    def _render_background(self, surface: pygame.Surface) -> None:
        """Render arena background."""
        surface.fill(self.theme.background_color)

        # Add some visual effects
        # Grid lines
        for x in range(0, self.screen_width, 50):
            alpha = 30 + (x % 100) // 2
            pygame.draw.line(
                surface,
                (*self.theme.accent_color[:2], alpha),
                (x, 0),
                (x, self.screen_height),
                1,
            )

    def _render_floor(self, surface: pygame.Surface) -> None:
        """Render arena floor."""
        floor_rect = pygame.Rect(
            0, self.FLOOR_Y, self.screen_width, self.screen_height - self.FLOOR_Y
        )
        pygame.draw.rect(surface, self.theme.floor_color, floor_rect)

        # Floor line
        pygame.draw.line(
            surface,
            self.theme.accent_color,
            (0, self.FLOOR_Y),
            (self.screen_width, self.FLOOR_Y),
            3,
        )

    def _render_health_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        health: int,
        max_health: int,
        name: str,
        align_left: bool,
    ) -> None:
        """Render a health bar.

        Args:
            surface: Surface to render on
            x: X position
            y: Y position
            health: Current health
            max_health: Maximum health
            name: Fighter name
            align_left: Whether to align bar to left
        """
        # Background
        bg_rect = pygame.Rect(x, y, self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)

        # Health fill
        health_ratio = max(0, min(1, health / max_health))
        fill_width = int(self.HEALTH_BAR_WIDTH * health_ratio)

        if align_left:
            fill_rect = pygame.Rect(x, y, fill_width, self.HEALTH_BAR_HEIGHT)
        else:
            fill_rect = pygame.Rect(
                x + self.HEALTH_BAR_WIDTH - fill_width,
                y,
                fill_width,
                self.HEALTH_BAR_HEIGHT,
            )

        # Color based on health
        if health_ratio > 0.5:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.25:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red

        pygame.draw.rect(surface, color, fill_rect)

        # Border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

        # Name label
        font = pygame.font.Font(None, 24)
        name_text = font.render(name, True, (255, 255, 255))
        name_rect = name_text.get_rect()

        if align_left:
            name_rect.topleft = (x, y - 20)
        else:
            name_rect.topright = (x + self.HEALTH_BAR_WIDTH, y - 20)

        surface.blit(name_text, name_rect)

    def _render_timer(self, surface: pygame.Surface) -> None:
        """Render the round timer."""
        font = pygame.font.Font(None, 48)
        time_str = str(int(self.time_remaining))
        timer_text = font.render(time_str, True, (255, 255, 255))
        timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 40))

        # Timer background
        bg_rect = timer_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)
        pygame.draw.rect(surface, self.theme.accent_color, bg_rect, 2)

        surface.blit(timer_text, timer_rect)

    def _render_round_indicator(self, surface: pygame.Surface) -> None:
        """Render round win indicators."""
        font = pygame.font.Font(None, 20)

        # Player rounds (left side)
        for i in range(2):
            x = 50 + i * 25
            y = self.HEALTH_BAR_Y + self.HEALTH_BAR_HEIGHT + 10
            color = (255, 255, 0) if i < self.player_rounds_won else (50, 50, 50)
            pygame.draw.circle(surface, color, (x, y), 8)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 8, 1)

        # Boss rounds (right side)
        for i in range(2):
            x = self.screen_width - 50 - i * 25
            y = self.HEALTH_BAR_Y + self.HEALTH_BAR_HEIGHT + 10
            color = (255, 255, 0) if i < self.boss_rounds_won else (50, 50, 50)
            pygame.draw.circle(surface, color, (x, y), 8)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 8, 1)

    def get_floor_y(self) -> int:
        """Get the Y position of the floor."""
        return self.FLOOR_Y

    def get_arena_bounds(self) -> Tuple[int, int]:
        """Get the left and right boundaries of the arena."""
        return (self.ARENA_LEFT, self.ARENA_RIGHT)
