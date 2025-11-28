"""Tests for ArcadeResultsController."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from arcade_results_controller import (
    ArcadeResultsController,
    ArcadeResultsAction,
    ArcadeStatsSnapshot
)


@pytest.fixture
def stats_with_queue():
    """Stats snapshot with zombies in queue."""
    return ArcadeStatsSnapshot(
        total_eliminations=50,
        highest_combo=8,
        powerups_collected=5,
        eliminations_per_second=0.83,
        queue_size=42
    )


@pytest.fixture
def stats_empty_queue():
    """Stats snapshot with empty queue."""
    return ArcadeStatsSnapshot(
        total_eliminations=0,
        highest_combo=0,
        powerups_collected=0,
        eliminations_per_second=0.0,
        queue_size=0
    )


class TestArcadeResultsController:
    """Tests for the ArcadeResultsController class."""

    def test_initial_state(self):
        """Controller starts in hidden state."""
        controller = ArcadeResultsController()
        assert not controller.is_visible
        assert controller.selected_index == 0
        assert controller.options == []

    def test_show_with_quarantine_options(self, stats_with_queue):
        """Show with queue displays quarantine options."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        assert controller.is_visible
        assert controller.selected_index == 0
        assert len(controller.options) == 3
        assert "Yes - Quarantine All" in controller.options
        assert "No - Discard Queue" in controller.options
        assert "Replay - Try Again" in controller.options

    def test_show_without_quarantine_options(self, stats_empty_queue):
        """Show without queue displays only replay/exit options."""
        controller = ArcadeResultsController()
        controller.show(stats_empty_queue)

        assert controller.is_visible
        assert len(controller.options) == 2
        assert "Replay - Try Again" in controller.options
        assert "Exit - Return to Lobby" in controller.options
        assert "Yes - Quarantine All" not in controller.options

    def test_hide(self, stats_with_queue):
        """Hide clears visibility and state."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.hide()

        assert not controller.is_visible
        assert controller.options == []
        assert controller.stats is None

    def test_navigate_down(self, stats_with_queue):
        """Navigate down increments selection."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        assert controller.selected_index == 0

        controller.navigate(1)
        assert controller.selected_index == 1

        controller.navigate(1)
        assert controller.selected_index == 2

    def test_navigate_up(self, stats_with_queue):
        """Navigate up decrements selection."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # Go to 1
        controller.navigate(1)  # Go to 2

        controller.navigate(-1)
        assert controller.selected_index == 1

    def test_navigate_wraps_around(self, stats_with_queue):
        """Navigation wraps from last to first and vice versa."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)  # 3 options

        controller.navigate(-1)  # Up from 0 wraps to 2
        assert controller.selected_index == 2

        controller.navigate(1)  # Down from 2 wraps to 0
        assert controller.selected_index == 0

    def test_navigate_when_hidden_does_nothing(self):
        """Navigation is ignored when menu is hidden."""
        controller = ArcadeResultsController()
        controller.navigate(1)
        assert controller.selected_index == 0

    def test_select_quarantine_all(self, stats_with_queue):
        """Selecting Quarantine All returns QUARANTINE_ALL action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        # First option is "Yes - Quarantine All"

        action = controller.select()

        assert action == ArcadeResultsAction.QUARANTINE_ALL
        assert not controller.is_visible

    def test_select_discard_queue(self, stats_with_queue):
        """Selecting Discard Queue returns DISCARD_QUEUE action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # Move to "No - Discard Queue"

        action = controller.select()

        assert action == ArcadeResultsAction.DISCARD_QUEUE
        assert not controller.is_visible

    def test_select_replay(self, stats_with_queue):
        """Selecting Replay returns REPLAY action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # No - Discard Queue
        controller.navigate(1)  # Replay - Try Again

        action = controller.select()

        assert action == ArcadeResultsAction.REPLAY
        assert not controller.is_visible

    def test_select_exit_to_lobby(self, stats_empty_queue):
        """Selecting Exit returns EXIT_TO_LOBBY action."""
        controller = ArcadeResultsController()
        controller.show(stats_empty_queue)
        controller.navigate(1)  # Move to "Exit - Return to Lobby"

        action = controller.select()

        assert action == ArcadeResultsAction.EXIT_TO_LOBBY
        assert not controller.is_visible

    def test_select_when_hidden_returns_none(self):
        """Select returns NONE when menu is hidden."""
        controller = ArcadeResultsController()
        action = controller.select()
        assert action == ArcadeResultsAction.NONE

    def test_build_message_keyboard(self, stats_with_queue):
        """Build message includes keyboard instructions."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        message = controller.build_message(has_controller=False)

        assert "ARCADE MODE COMPLETE" in message
        assert "Zombies Eliminated: 50" in message
        assert "Highest Combo: 8x" in message
        assert "42 identities queued" in message
        assert "↑/↓ or W/S = Select" in message
        assert "▶" in message

    def test_build_message_controller(self, stats_with_queue):
        """Build message includes controller instructions."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        message = controller.build_message(has_controller=True)

        assert "ARCADE MODE COMPLETE" in message
        assert "D-Pad" in message
        assert "Confirm" in message

    def test_build_message_no_queue(self, stats_empty_queue):
        """Build message shows no quarantine message when queue empty."""
        controller = ArcadeResultsController()
        controller.show(stats_empty_queue)

        message = controller.build_message()

        assert "No eliminations to quarantine" in message
        assert "queued for quarantine" not in message

    def test_build_message_shows_selection(self, stats_with_queue):
        """Build message highlights current selection."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # Move to second option

        message = controller.build_message()

        # First option should NOT have arrow
        assert "▶ Yes - Quarantine All" not in message
        # Second option should have arrow
        assert "▶ No - Discard Queue" in message

    def test_get_selected_option(self, stats_with_queue):
        """get_selected_option returns current selection text."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        assert controller.get_selected_option() == "Yes - Quarantine All"

        controller.navigate(1)
        assert controller.get_selected_option() == "No - Discard Queue"

    def test_get_selected_option_when_empty(self):
        """get_selected_option returns empty string when no options."""
        controller = ArcadeResultsController()
        assert controller.get_selected_option() == ""

    def test_has_quarantine_options_true(self, stats_with_queue):
        """has_quarantine_options returns True when queue has items."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        assert controller.has_quarantine_options()

    def test_has_quarantine_options_false(self, stats_empty_queue):
        """has_quarantine_options returns False when queue is empty."""
        controller = ArcadeResultsController()
        controller.show(stats_empty_queue)
        assert not controller.has_quarantine_options()

    def test_stats_preserved(self, stats_with_queue):
        """Stats snapshot is preserved after show."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        assert controller.stats.total_eliminations == 50
        assert controller.stats.highest_combo == 8
        assert controller.stats.queue_size == 42
