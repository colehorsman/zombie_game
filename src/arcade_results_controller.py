"""Arcade results menu controller - handles arcade mode results screen state and navigation."""

import logging
from enum import Enum, auto
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ArcadeResultsAction(Enum):
    """Actions that can be triggered from the arcade results menu."""

    NONE = auto()
    QUARANTINE_ALL = auto()
    DISCARD_QUEUE = auto()
    REPLAY = auto()
    EXIT_TO_LOBBY = auto()


@dataclass
class ArcadeStatsSnapshot:
    """Snapshot of arcade stats for display."""

    total_eliminations: int
    highest_combo: int
    powerups_collected: int
    eliminations_per_second: float
    queue_size: int


class ArcadeResultsController:
    """
    Manages arcade results menu state and navigation.

    Extracted from GameEngine to reduce complexity and improve testability.
    """

    # Options when there are zombies to quarantine
    QUARANTINE_OPTIONS = [
        "Yes - Quarantine All",
        "No - Discard Queue",
        "Replay - Try Again",
    ]

    # Options when there are no zombies to quarantine
    NO_QUARANTINE_OPTIONS = ["Replay - Try Again", "Exit - Return to Lobby"]

    def __init__(self):
        """Initialize the arcade results controller."""
        self.options: List[str] = []
        self.selected_index: int = 0
        self.is_visible: bool = False
        self.stats: Optional[ArcadeStatsSnapshot] = None

        # Controller labels (can be updated based on connected controller)
        self.controller_labels = {
            "confirm": "A",
            "back": "B",
            "up": "D-Pad ↑",
            "down": "D-Pad ↓",
        }

    def show(self, stats: ArcadeStatsSnapshot) -> None:
        """
        Show the arcade results menu.

        Args:
            stats: Snapshot of arcade statistics including queue size
        """
        self.stats = stats
        self.selected_index = 0

        if stats.queue_size > 0:
            self.options = self.QUARANTINE_OPTIONS.copy()
        else:
            self.options = self.NO_QUARANTINE_OPTIONS.copy()

        self.is_visible = True
        logger.info(
            f"🎮 Arcade results shown: {stats.total_eliminations} eliminations, {stats.queue_size} queued"
        )

    def hide(self) -> None:
        """Hide the arcade results menu and reset state."""
        self.is_visible = False
        self.options = []
        self.stats = None
        self.selected_index = 0
        logger.info("🎮 Arcade results hidden")

    def navigate(self, direction: int) -> None:
        """
        Navigate the menu up or down.

        Args:
            direction: -1 for up, 1 for down
        """
        if not self.is_visible or not self.options:
            return

        old_index = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(self.options)
        logger.debug(
            f"🎮 Arcade menu: {old_index} → {self.selected_index}: {self.options[self.selected_index]}"
        )

    def select(self) -> ArcadeResultsAction:
        """
        Execute the currently selected option.

        Returns:
            ArcadeResultsAction indicating what action the game engine should take
        """
        if not self.is_visible or not self.options:
            return ArcadeResultsAction.NONE

        # Bounds check for invalid index
        if self.selected_index < 0 or self.selected_index >= len(self.options):
            return ArcadeResultsAction.NONE

        selected_option = self.options[self.selected_index]
        logger.info(f"🎮 Arcade results: executing option '{selected_option}'")

        if selected_option == "Yes - Quarantine All":
            self.hide()
            return ArcadeResultsAction.QUARANTINE_ALL
        elif selected_option == "No - Discard Queue":
            self.hide()
            return ArcadeResultsAction.DISCARD_QUEUE
        elif selected_option == "Replay - Try Again":
            self.hide()
            return ArcadeResultsAction.REPLAY
        elif selected_option == "Exit - Return to Lobby":
            self.hide()
            return ArcadeResultsAction.EXIT_TO_LOBBY

        return ArcadeResultsAction.NONE

    def build_message(self, has_controller: bool = False) -> str:
        """
        Build the arcade results message with current selection highlighted.

        Args:
            has_controller: Whether a controller is connected

        Returns:
            Formatted results message string
        """
        if not self.stats:
            return "🎮 ARCADE MODE COMPLETE! 🎮"

        stats = self.stats

        # Build header
        message = "🎮 ARCADE MODE COMPLETE! 🎮\n\n"
        message += "═══════════════════════════\n\n"
        message += f"Zombies Eliminated: {stats.total_eliminations}\n"
        message += f"Highest Combo: {stats.highest_combo}x\n"
        message += f"Power-ups Collected: {stats.powerups_collected}\n"
        message += f"Eliminations/Second: {stats.eliminations_per_second:.2f}\n\n"
        message += "═══════════════════════════\n\n"

        # Add queue info and options
        if stats.queue_size > 0:
            message += f"💾 {stats.queue_size} identities queued for quarantine\n\n"
            message += "Quarantine all eliminated identities?\n\n"
        else:
            message += "No eliminations to quarantine.\n\n"

        # Add menu options with selection indicator
        for i, option in enumerate(self.options):
            if i == self.selected_index:
                message += f"▶ {option}\n"
            else:
                message += f"  {option}\n"
        message += "\n"

        # Add input instructions
        if has_controller:
            message += f"{self.controller_labels['up']}/{self.controller_labels['down']} = Select\n"
            message += f"{self.controller_labels['confirm']} = Confirm"
        else:
            message += "↑/↓ or W/S = Select\n"
            message += "ENTER or SPACE = Confirm"

        return message

    def get_selected_option(self) -> str:
        """Get the currently selected option text."""
        if not self.options:
            return ""
        return self.options[self.selected_index]

    def has_quarantine_options(self) -> bool:
        """Check if the menu is showing quarantine options (vs just replay/exit)."""
        return self.stats is not None and self.stats.queue_size > 0
