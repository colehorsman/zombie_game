"""Cheat code controller - handles detection of various cheat codes."""

import logging
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

import pygame

logger = logging.getLogger(__name__)


class CheatCodeAction(Enum):
    """Actions that can be triggered by cheat codes."""

    NONE = auto()
    UNLOCK_ALL_LEVELS = auto()
    SKIP_LEVEL = auto()
    SPAWN_BOSS = auto()  # Konami code
    START_ARCADE = auto()  # Arcade cheat code


@dataclass
class CheatCodeResult:
    """Result of processing a key input for cheat codes."""

    action: CheatCodeAction
    message: Optional[str] = None


class CheatCodeController:
    """
    Manages cheat code detection and activation.

    Extracted from GameEngine to reduce complexity and improve testability.
    Handles:
    - UNLOCK code (unlocks all levels)
    - SKIP code (skips current level)
    - Konami code (spawns boss)
    - Arcade code (starts arcade mode)
    """

    # Cheat code definitions
    UNLOCK_CODE = [
        pygame.K_u,
        pygame.K_n,
        pygame.K_l,
        pygame.K_o,
        pygame.K_c,
        pygame.K_k,
    ]
    SKIP_CODE = [pygame.K_s, pygame.K_k, pygame.K_i, pygame.K_p]
    KONAMI_CODE = [
        pygame.K_UP,
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_DOWN,
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_LEFT,
        pygame.K_RIGHT,
    ]
    ARCADE_CODE = [
        pygame.K_UP,
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_DOWN,
        pygame.K_a,
        pygame.K_b,
    ]

    # Timeout for resetting input sequences (seconds)
    INPUT_TIMEOUT = 2.0

    # Controller D-pad button mappings
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14

    # Controller Konami sequence (D-pad buttons)
    CONTROLLER_KONAMI = [11, 11, 12, 12, 13, 14, 13, 14]  # UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT

    def __init__(self):
        """Initialize the cheat code controller."""
        # Text cheat buffer (UNLOCK, SKIP)
        self.cheat_buffer: List[int] = []

        # Konami code buffer (keyboard)
        self.konami_buffer: List[int] = []
        self.last_konami_time: float = 0.0

        # Controller Konami buffer
        self.controller_konami_buffer: List[int] = []
        self.last_controller_konami_time: float = 0.0

        # Arcade code buffer
        self.arcade_buffer: List[int] = []
        self.last_arcade_time: float = 0.0

        # State
        self.unlock_enabled: bool = False

    def process_key(self, key: int, current_time: Optional[float] = None) -> CheatCodeResult:
        """
        Process a key press and check for cheat code activation.

        Args:
            key: pygame key code
            current_time: Current time in seconds (defaults to time.time())

        Returns:
            CheatCodeResult with action and optional message
        """
        if current_time is None:
            current_time = time.time()

        # Check for timeout on sequence codes
        if current_time - self.last_konami_time > self.INPUT_TIMEOUT:
            self.konami_buffer = []
        if current_time - self.last_arcade_time > self.INPUT_TIMEOUT:
            self.arcade_buffer = []

        # Update timestamps
        self.last_konami_time = current_time
        self.last_arcade_time = current_time

        # Add to buffers
        self.cheat_buffer.append(key)
        self.konami_buffer.append(key)
        self.arcade_buffer.append(key)

        # Trim buffers to max code length
        if len(self.cheat_buffer) > 6:  # UNLOCK is longest at 6
            self.cheat_buffer = self.cheat_buffer[-6:]
        if len(self.konami_buffer) > 8:
            self.konami_buffer = self.konami_buffer[-8:]
        if len(self.arcade_buffer) > 6:
            self.arcade_buffer = self.arcade_buffer[-6:]

        # Check UNLOCK code
        if self.cheat_buffer == self.UNLOCK_CODE:
            self.unlock_enabled = True
            self.cheat_buffer = []
            logger.info("🔓 CHEAT: All levels unlocked!")
            return CheatCodeResult(
                action=CheatCodeAction.UNLOCK_ALL_LEVELS,
                message="🔓 CHEAT ACTIVATED\n\nAll Levels Unlocked!\n\nPress ESC to continue",
            )

        # Check SKIP code
        if self.cheat_buffer == self.SKIP_CODE:
            self.cheat_buffer = []
            logger.info("🔓 CHEAT: Skip level activated!")
            return CheatCodeResult(
                action=CheatCodeAction.SKIP_LEVEL,
                message=None,  # Message handled by GameEngine based on current level
            )

        # Check Konami code
        if len(self.konami_buffer) >= 8 and self.konami_buffer[-8:] == self.KONAMI_CODE:
            self.konami_buffer = []
            logger.info("🎮 KONAMI CODE ACTIVATED!")
            return CheatCodeResult(
                action=CheatCodeAction.SPAWN_BOSS,
                message=None,  # Boss spawn handled by GameEngine
            )

        # Check Arcade code
        if len(self.arcade_buffer) >= 6 and self.arcade_buffer[-6:] == self.ARCADE_CODE:
            self.arcade_buffer = []
            logger.info("🎮 ARCADE CODE ACTIVATED!")
            return CheatCodeResult(
                action=CheatCodeAction.START_ARCADE,
                message=None,  # Arcade start handled by GameEngine
            )

        return CheatCodeResult(action=CheatCodeAction.NONE)

    def process_controller_button(
        self, button: int, current_time: Optional[float] = None
    ) -> CheatCodeResult:
        """
        Process a controller button press for cheat codes (D-pad only).

        Args:
            button: Controller button number
            current_time: Current time in seconds (defaults to time.time())

        Returns:
            CheatCodeResult with action and optional message
        """
        if current_time is None:
            current_time = time.time()

        # Only process D-pad buttons
        if button not in [self.DPAD_UP, self.DPAD_DOWN, self.DPAD_LEFT, self.DPAD_RIGHT]:
            return CheatCodeResult(action=CheatCodeAction.NONE)

        # Check for timeout
        if current_time - self.last_controller_konami_time > self.INPUT_TIMEOUT:
            self.controller_konami_buffer = []

        self.last_controller_konami_time = current_time

        # Add to buffer
        self.controller_konami_buffer.append(button)

        # Trim buffer
        if len(self.controller_konami_buffer) > 8:
            self.controller_konami_buffer = self.controller_konami_buffer[-8:]

        # Check controller Konami code
        if (
            len(self.controller_konami_buffer) >= 8
            and self.controller_konami_buffer[-8:] == self.CONTROLLER_KONAMI
        ):
            self.controller_konami_buffer = []
            logger.info("🎮 CONTROLLER KONAMI CODE ACTIVATED!")
            return CheatCodeResult(
                action=CheatCodeAction.SPAWN_BOSS,
                message="🎮 KONAMI CODE!\n\nBoss incoming...\n\nPress A to continue",
            )

        return CheatCodeResult(action=CheatCodeAction.NONE)

    def reset(self) -> None:
        """Reset all cheat code buffers."""
        self.cheat_buffer = []
        self.konami_buffer = []
        self.controller_konami_buffer = []
        self.arcade_buffer = []

    def is_unlock_enabled(self) -> bool:
        """Check if unlock cheat has been activated."""
        return self.unlock_enabled

    def enable_unlock(self) -> None:
        """Manually enable unlock (e.g., from saved state)."""
        self.unlock_enabled = True

    def disable_unlock(self) -> None:
        """Disable unlock cheat."""
        self.unlock_enabled = False
