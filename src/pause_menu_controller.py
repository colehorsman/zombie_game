"""Pause menu controller - handles pause menu state and navigation."""

import logging
from enum import Enum, auto
from typing import List, Optional, Callable

logger = logging.getLogger(__name__)


class PauseMenuAction(Enum):
    """Actions that can be triggered from the pause menu."""

    NONE = auto()
    RESUME = auto()
    START_ARCADE = auto()
    RETURN_TO_LOBBY = auto()
    SAVE_GAME = auto()
    QUIT_GAME = auto()


class PauseMenuController:
    """
    Manages pause menu state and navigation.

    Extracted from GameEngine to reduce complexity and improve testability.
    """

    # Base options that are always available
    BASE_OPTIONS = ["Return to Game", "Return to Lobby", "Save Game", "Quit Game"]

    # Options with arcade mode included
    ARCADE_OPTIONS = [
        "Return to Game",
        "🎮 Arcade Mode",
        "Return to Lobby",
        "Save Game",
        "Quit Game",
    ]

    def __init__(self):
        """Initialize the pause menu controller."""
        self.options: List[str] = self.BASE_OPTIONS.copy()
        self.selected_index: int = 0
        self.is_visible: bool = False
        self.show_save_confirmation: bool = False

        # Controller labels (can be updated based on connected controller)
        self.controller_labels = {
            "confirm": "A",
            "back": "B",
            "pause": "Start",
            "lobby": "Select",
            "up": "D-Pad ↑",
            "down": "D-Pad ↓",
        }

    def show(self, include_arcade_option: bool = False) -> None:
        """
        Show the pause menu.

        Args:
            include_arcade_option: Whether to include the arcade mode option
        """
        if include_arcade_option:
            self.options = self.ARCADE_OPTIONS.copy()
        else:
            self.options = self.BASE_OPTIONS.copy()

        self.selected_index = 0
        self.is_visible = True
        self.show_save_confirmation = False
        logger.info(f"⏸️  Pause menu shown - options: {self.options}")

    def hide(self) -> None:
        """Hide the pause menu."""
        self.is_visible = False
        self.show_save_confirmation = False
        logger.info("⏸️  Pause menu hidden")

    def navigate(self, direction: int) -> None:
        """
        Navigate the menu up or down.

        Args:
            direction: -1 for up, 1 for down
        """
        if not self.is_visible:
            return

        old_index = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(self.options)
        self.show_save_confirmation = False  # Clear save confirmation on navigation
        logger.info(
            f"Menu navigation: {old_index} → {self.selected_index} ({self.options[self.selected_index]})"
        )

    def select(self) -> PauseMenuAction:
        """
        Execute the currently selected option.

        Returns:
            PauseMenuAction indicating what action the game engine should take
        """
        if not self.is_visible:
            return PauseMenuAction.NONE

        selected_option = self.options[self.selected_index]
        logger.info(
            f"Executing menu option: {selected_option} (index: {self.selected_index})"
        )

        if selected_option == "Return to Game":
            self.hide()
            return PauseMenuAction.RESUME
        elif selected_option == "🎮 Arcade Mode":
            self.hide()
            return PauseMenuAction.START_ARCADE
        elif selected_option == "Return to Lobby":
            self.hide()
            return PauseMenuAction.RETURN_TO_LOBBY
        elif selected_option == "Save Game":
            self.show_save_confirmation = True
            return PauseMenuAction.SAVE_GAME
        elif selected_option == "Quit Game":
            self.hide()
            return PauseMenuAction.QUIT_GAME

        return PauseMenuAction.NONE

    def build_message(self, has_controller: bool = False) -> str:
        """
        Build the pause menu message with current selection highlighted.

        Args:
            has_controller: Whether a controller is connected

        Returns:
            Formatted menu message string
        """
        menu_message = "⏸️  PAUSED\n\n"

        if self.show_save_confirmation:
            menu_message += "✅ Game Saved!\n\n"

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                menu_message += f"▶ {option}\n"
            else:
                menu_message += f"  {option}\n"

        # Add controller/keyboard instructions
        if has_controller:
            menu_message += f"\n{self.controller_labels['up']}/{self.controller_labels['down']} = Select"
            menu_message += f"\n{self.controller_labels['confirm']} = Confirm"
            menu_message += f"\n{self.controller_labels['back']} = Cancel"
            menu_message += f"\n{self.controller_labels['lobby']} = Quick Lobby"
        else:
            menu_message += "\n↑↓ = Select, ENTER = Confirm, ESC = Cancel"
            menu_message += "\nL = Quick Return to Lobby"

        return menu_message

    def get_selected_option(self) -> str:
        """Get the currently selected option text."""
        return self.options[self.selected_index]
