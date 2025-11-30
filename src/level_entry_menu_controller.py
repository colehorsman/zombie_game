"""
Level Entry Menu Controller for Sonrai Zombie Blaster.

Manages the mode selection menu when entering levels, allowing players
to choose between Arcade Mode (API-light) and Story Mode (standard gameplay).

This feature is critical for AWS re:Invent 2025 to reduce Sonrai API load
by encouraging Arcade Mode play during high-traffic booth sessions.
"""

import logging
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger(__name__)


class LevelEntryAction(Enum):
    """Actions that can be triggered from the level entry menu."""

    NONE = auto()
    ARCADE_MODE = auto()
    STORY_MODE = auto()
    CANCEL = auto()


class LevelEntryMenuController:
    """
    Manages level entry mode selection menu.

    Responsibilities:
    - Track menu selection state
    - Build menu display messages with descriptions
    - Handle navigation (up/down)
    - Return selected action for GameEngine to execute

    Configuration:
    - enabled: Whether the menu is shown (default: True)
    - default_mode: Which mode is highlighted by default ("arcade" or "story")
    """

    # Menu options with emoji indicators
    OPTIONS = ["🕹️ ARCADE MODE", "📖 STORY MODE"]

    # Descriptions for each mode
    DESCRIPTIONS = {
        0: "60-second timed challenge! Eliminate zombies for points.\nChoose to quarantine at the end.",
        1: "Standard gameplay. Each elimination triggers\nreal-time quarantine via Sonrai API.",
    }

    def __init__(self, enabled: bool = True, default_mode: str = "arcade"):
        """
        Initialize the level entry menu controller.

        Args:
            enabled: Whether the menu is enabled (if False, skip menu entirely)
            default_mode: Default highlighted mode ("arcade" or "story")
        """
        self._enabled = enabled
        self._default_mode = default_mode.lower() if default_mode else "arcade"
        self._active = False
        self._selected_index = self._get_default_index()
        self._level_name: Optional[str] = None

        logger.info(
            f"LevelEntryMenuController initialized: enabled={enabled}, default_mode={default_mode}"
        )

    def _get_default_index(self) -> int:
        """Get the default selection index based on configuration."""
        if self._default_mode == "story":
            return 1
        return 0  # Default to arcade

    @property
    def enabled(self) -> bool:
        """Check if the menu is enabled via configuration."""
        return self._enabled

    @property
    def active(self) -> bool:
        """Check if the menu is currently active."""
        return self._active

    @property
    def selected_index(self) -> int:
        """Get the currently selected menu index."""
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """Set the selected menu index (with bounds checking)."""
        self._selected_index = value % len(self.OPTIONS)

    @property
    def options(self) -> list:
        """Get the list of menu options."""
        return self.OPTIONS.copy()

    @property
    def level_name(self) -> Optional[str]:
        """Get the current level name being entered."""
        return self._level_name

    def show(self, level_name: str) -> str:
        """
        Activate the level entry menu and return the initial message.

        Args:
            level_name: Name of the level being entered (e.g., "SANDBOX")

        Returns:
            The formatted menu message string
        """
        self._active = True
        self._selected_index = self._get_default_index()
        self._level_name = level_name
        logger.info(f"🚪 Level entry menu shown for: {level_name}")
        return self.build_message(level_name)

    def hide(self) -> None:
        """Deactivate the level entry menu."""
        self._active = False
        self._level_name = None
        logger.debug("Level entry menu hidden")

    def navigate(self, direction: int) -> str:
        """
        Navigate the menu selection.

        Args:
            direction: -1 for up, 1 for down

        Returns:
            Updated menu message string
        """
        if not self._active:
            return ""

        self._selected_index = (self._selected_index + direction) % len(self.OPTIONS)
        logger.debug(f"Level entry menu navigation: index={self._selected_index}")
        return self.build_message(self._level_name or "")

    def select(self) -> LevelEntryAction:
        """
        Execute the currently selected option.

        Returns:
            LevelEntryAction indicating what action to take
        """
        if not self._active:
            return LevelEntryAction.NONE

        if self._selected_index == 0:
            logger.info("🕹️ Level entry menu: ARCADE MODE selected")
            return LevelEntryAction.ARCADE_MODE
        elif self._selected_index == 1:
            logger.info("📖 Level entry menu: STORY MODE selected")
            return LevelEntryAction.STORY_MODE

        return LevelEntryAction.NONE

    def cancel(self) -> LevelEntryAction:
        """
        Cancel the menu and return to lobby.

        Returns:
            LevelEntryAction.CANCEL
        """
        logger.info("❌ Level entry menu: CANCELLED")
        self.hide()
        return LevelEntryAction.CANCEL

    def build_message(self, level_name: str) -> str:
        """
        Build the level entry menu message with current selection highlighted.

        Args:
            level_name: Name of the level being entered

        Returns:
            Formatted menu message string
        """
        # Build header
        header = f"🚪 ENTERING: {level_name.upper()}\n\n"
        header += "Choose your gameplay mode:\n\n"

        # Build option lines with selection indicator
        option_lines = []
        for i, option in enumerate(self.OPTIONS):
            prefix = "▶ " if i == self._selected_index else "  "
            option_lines.append(f"{prefix}{option}")

        # Get description for selected mode
        description = self.DESCRIPTIONS.get(self._selected_index, "")

        # Build footer with controller hints
        footer = "\n\n─────────────────────────────\n"
        footer += "A/ENTER: Select | B/ESC: Cancel"

        # Combine all parts
        message = (
            f"{header}"
            f"{option_lines[0]}\n"
            f"{option_lines[1]}\n\n"
            f"{description}"
            f"{footer}"
        )

        return message
