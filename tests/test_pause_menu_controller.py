"""Tests for PauseMenuController."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pause_menu_controller import PauseMenuController, PauseMenuAction


class TestPauseMenuController:
    """Tests for the PauseMenuController class."""

    def test_initial_state(self):
        """Controller starts in hidden state."""
        controller = PauseMenuController()
        assert not controller.is_visible
        assert controller.selected_index == 0

    def test_show_basic_menu(self):
        """Show displays basic menu without arcade option."""
        controller = PauseMenuController()
        controller.show(include_arcade_option=False)

        assert controller.is_visible
        assert controller.selected_index == 0
        assert len(controller.options) == 4
        assert "🎮 Arcade Mode" not in controller.options

    def test_show_arcade_menu(self):
        """Show with arcade option includes arcade mode."""
        controller = PauseMenuController()
        controller.show(include_arcade_option=True)

        assert controller.is_visible
        assert len(controller.options) == 5
        assert "🎮 Arcade Mode" in controller.options

    def test_hide(self):
        """Hide clears visibility."""
        controller = PauseMenuController()
        controller.show()
        controller.hide()

        assert not controller.is_visible

    def test_navigate_down(self):
        """Navigate down increments selection."""
        controller = PauseMenuController()
        controller.show()
        assert controller.selected_index == 0

        controller.navigate(1)  # Down
        assert controller.selected_index == 1

        controller.navigate(1)  # Down again
        assert controller.selected_index == 2

    def test_navigate_up(self):
        """Navigate up decrements selection."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Go to index 1
        controller.navigate(1)  # Go to index 2

        controller.navigate(-1)  # Up
        assert controller.selected_index == 1

    def test_navigate_wraps_around(self):
        """Navigation wraps from last to first and vice versa."""
        controller = PauseMenuController()
        controller.show()  # 4 options

        # Wrap forward: 0 -> 3 -> 0
        controller.navigate(-1)  # Up from 0 wraps to 3
        assert controller.selected_index == 3

        controller.navigate(1)  # Down from 3 wraps to 0
        assert controller.selected_index == 0

    def test_navigate_when_hidden_does_nothing(self):
        """Navigation is ignored when menu is hidden."""
        controller = PauseMenuController()
        # Don't show the menu
        controller.navigate(1)
        assert controller.selected_index == 0

    def test_select_return_to_game(self):
        """Selecting Return to Game returns RESUME action."""
        controller = PauseMenuController()
        controller.show()
        # First option is "Return to Game"

        action = controller.select()

        assert action == PauseMenuAction.RESUME
        assert not controller.is_visible

    def test_select_arcade_mode(self):
        """Selecting Arcade Mode returns START_ARCADE action."""
        controller = PauseMenuController()
        controller.show(include_arcade_option=True)
        controller.navigate(1)  # Move to "🎮 Arcade Mode"

        action = controller.select()

        assert action == PauseMenuAction.START_ARCADE
        assert not controller.is_visible

    def test_select_return_to_lobby(self):
        """Selecting Return to Lobby returns RETURN_TO_LOBBY action."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Move to "Return to Lobby"

        action = controller.select()

        assert action == PauseMenuAction.RETURN_TO_LOBBY
        assert not controller.is_visible

    def test_select_save_game(self):
        """Selecting Save Game returns SAVE_GAME and shows confirmation."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Return to Lobby
        controller.navigate(1)  # Save Game

        action = controller.select()

        assert action == PauseMenuAction.SAVE_GAME
        assert controller.show_save_confirmation
        assert controller.is_visible  # Menu stays visible after save

    def test_select_quit_game(self):
        """Selecting Quit Game returns QUIT_GAME action."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Return to Lobby
        controller.navigate(1)  # Save Game
        controller.navigate(1)  # Quit Game

        action = controller.select()

        assert action == PauseMenuAction.QUIT_GAME
        assert not controller.is_visible

    def test_select_when_hidden_returns_none(self):
        """Select returns NONE when menu is hidden."""
        controller = PauseMenuController()
        action = controller.select()
        assert action == PauseMenuAction.NONE

    def test_build_message_keyboard(self):
        """Build message includes keyboard instructions."""
        controller = PauseMenuController()
        controller.show()

        message = controller.build_message(has_controller=False)

        assert "PAUSED" in message
        assert "Return to Game" in message
        assert "↑↓ = Select" in message
        assert "▶" in message  # Selection indicator

    def test_build_message_controller(self):
        """Build message includes controller instructions."""
        controller = PauseMenuController()
        controller.show()

        message = controller.build_message(has_controller=True)

        assert "PAUSED" in message
        assert "D-Pad" in message
        assert "Confirm" in message

    def test_build_message_with_save_confirmation(self):
        """Build message shows save confirmation."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Return to Lobby
        controller.navigate(1)  # Save Game
        controller.select()  # This sets show_save_confirmation

        message = controller.build_message()

        assert "Game Saved!" in message

    def test_navigate_clears_save_confirmation(self):
        """Navigating after save clears the confirmation message."""
        controller = PauseMenuController()
        controller.show()
        controller.navigate(1)  # Return to Lobby
        controller.navigate(1)  # Save Game
        controller.select()  # Sets confirmation
        assert controller.show_save_confirmation

        controller.navigate(1)  # Navigate

        assert not controller.show_save_confirmation

    def test_get_selected_option(self):
        """get_selected_option returns current selection text."""
        controller = PauseMenuController()
        controller.show()

        assert controller.get_selected_option() == "Return to Game"

        controller.navigate(1)
        assert controller.get_selected_option() == "Return to Lobby"
