"""
Integration tests for Level Entry Mode Selector.

Tests the integration between LevelEntryMenuController and GameEngine.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from level_entry_menu_controller import LevelEntryAction, LevelEntryMenuController


class TestLevelEntryIntegration:
    """Integration tests for level entry mode selector."""

    def test_arcade_mode_selection_returns_correct_action(self):
        """Test that selecting Arcade Mode returns ARCADE_MODE action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")

        # Default selection is Arcade Mode (index 0)
        action = controller.select()

        assert action == LevelEntryAction.ARCADE_MODE

    def test_story_mode_selection_returns_correct_action(self):
        """Test that selecting Story Mode returns STORY_MODE action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.navigate(1)  # Move to Story Mode

        action = controller.select()

        assert action == LevelEntryAction.STORY_MODE

    def test_cancel_returns_cancel_action(self):
        """Test that canceling returns CANCEL action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")

        action = controller.cancel()

        assert action == LevelEntryAction.CANCEL
        assert controller.active is False

    def test_disabled_config_skips_menu(self):
        """Test that disabled configuration means menu won't show."""
        controller = LevelEntryMenuController(enabled=False)

        assert controller.enabled is False
        # When disabled, the calling code should skip showing the menu

    def test_default_mode_arcade(self):
        """Test that default mode 'arcade' selects index 0."""
        controller = LevelEntryMenuController(default_mode="arcade")
        controller.show("Sandbox")

        assert controller.selected_index == 0

    def test_default_mode_story(self):
        """Test that default mode 'story' selects index 1."""
        controller = LevelEntryMenuController(default_mode="story")
        controller.show("Sandbox")

        assert controller.selected_index == 1

    def test_menu_message_contains_level_name(self):
        """Test that menu message includes the level name."""
        controller = LevelEntryMenuController()
        message = controller.show("Sandbox")

        assert "SANDBOX" in message

    def test_menu_message_contains_mode_descriptions(self):
        """Test that menu message includes mode descriptions."""
        controller = LevelEntryMenuController()
        message = controller.show("Sandbox")

        # Arcade mode description
        assert "60-second" in message or "timed" in message.lower()

        # Navigate to story mode
        message = controller.navigate(1)
        assert "quarantine" in message.lower() or "API" in message

    def test_navigation_updates_message(self):
        """Test that navigation updates the displayed message."""
        controller = LevelEntryMenuController()
        message1 = controller.show("Sandbox")

        # Initial state - Arcade selected
        assert "▶ 🕹️ ARCADE MODE" in message1
        assert "  📖 STORY MODE" in message1

        # Navigate to Story Mode
        message2 = controller.navigate(1)

        assert "  🕹️ ARCADE MODE" in message2
        assert "▶ 📖 STORY MODE" in message2

    def test_controller_hints_in_message(self):
        """Test that controller hints are shown in the message."""
        controller = LevelEntryMenuController()
        message = controller.show("Sandbox")

        assert "A/ENTER" in message or "Select" in message
        assert "B/ESC" in message or "Cancel" in message
