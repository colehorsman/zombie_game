"""Tests for ArcadeResultsController."""

import sys
from pathlib import Path

import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from arcade_results_controller import (
    ArcadeResultsAction,
    ArcadeResultsController,
    ArcadeStatsSnapshot,
)


@pytest.fixture
def stats_with_queue():
    """Stats snapshot with zombies in queue."""
    return ArcadeStatsSnapshot(
        total_eliminations=50,
        highest_combo=8,
        powerups_collected=5,
        eliminations_per_second=0.83,
        queue_size=42,
    )


@pytest.fixture
def stats_empty_queue():
    """Stats snapshot with empty queue."""
    return ArcadeStatsSnapshot(
        total_eliminations=0,
        highest_combo=0,
        powerups_collected=0,
        eliminations_per_second=0.0,
        queue_size=0,
    )


@pytest.fixture
def stats_with_high_score():
    """Stats snapshot with new high score achieved."""
    return ArcadeStatsSnapshot(
        total_eliminations=100,
        highest_combo=15,
        powerups_collected=10,
        eliminations_per_second=1.67,
        queue_size=85,
        is_new_high_score=True,
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
        """Show with queue displays quarantine options, no selection initially."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        assert controller.is_visible
        # Starts with no selection (-1) to prevent accidental button press
        assert controller.selected_index == -1
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
        """Navigate down increments selection, first nav selects first item."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        # Starts with no selection (-1)
        assert controller.selected_index == -1

        # First navigation selects first item (index 0)
        controller.navigate(1)
        assert controller.selected_index == 0

        controller.navigate(1)
        assert controller.selected_index == 1

        controller.navigate(1)
        assert controller.selected_index == 2

    def test_navigate_up(self, stats_with_queue):
        """Navigate up decrements selection."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        # First nav selects first item, then navigate to position 2
        controller.navigate(1)  # -1 -> 0
        controller.navigate(1)  # 0 -> 1
        controller.navigate(1)  # 1 -> 2

        controller.navigate(-1)  # 2 -> 1
        assert controller.selected_index == 1

    def test_navigate_wraps_around(self, stats_with_queue):
        """Navigation wraps from last to first and vice versa."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)  # 3 options, starts at -1

        # First nav from -1 selects first item (0)
        controller.navigate(1)
        assert controller.selected_index == 0

        # Up from 0 wraps to 2
        controller.navigate(-1)
        assert controller.selected_index == 2

        # Down from 2 wraps to 0
        controller.navigate(1)
        assert controller.selected_index == 0

    def test_navigate_when_hidden_does_nothing(self):
        """Navigation is ignored when menu is hidden."""
        controller = ArcadeResultsController()
        controller.navigate(1)
        assert controller.selected_index == 0

    def test_select_without_navigation_returns_none(self, stats_with_queue):
        """Selecting without navigating first returns NONE (prevents accidental selection)."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        # selected_index is -1, no selection yet

        action = controller.select()

        assert action == ArcadeResultsAction.NONE
        assert controller.is_visible  # Menu stays visible

    def test_select_quarantine_all(self, stats_with_queue):
        """Selecting Quarantine All returns QUARANTINE_ALL action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        # Must navigate first to select first option
        controller.navigate(1)  # -1 -> 0 (Yes - Quarantine All)

        action = controller.select()

        assert action == ArcadeResultsAction.QUARANTINE_ALL
        assert not controller.is_visible

    def test_select_discard_queue(self, stats_with_queue):
        """Selecting Discard Queue returns DISCARD_QUEUE action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # -1 -> 0 (Yes - Quarantine All)
        controller.navigate(1)  # 0 -> 1 (No - Discard Queue)

        action = controller.select()

        assert action == ArcadeResultsAction.DISCARD_QUEUE
        assert not controller.is_visible

    def test_select_replay(self, stats_with_queue):
        """Selecting Replay returns REPLAY action."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # -1 -> 0 (Yes - Quarantine All)
        controller.navigate(1)  # 0 -> 1 (No - Discard Queue)
        controller.navigate(1)  # 1 -> 2 (Replay - Try Again)

        action = controller.select()

        assert action == ArcadeResultsAction.REPLAY
        assert not controller.is_visible

    def test_select_exit_to_lobby(self, stats_empty_queue):
        """Selecting Exit returns EXIT_TO_LOBBY action."""
        controller = ArcadeResultsController()
        controller.show(stats_empty_queue)
        controller.navigate(1)  # -1 -> 0 (Replay - Try Again)
        controller.navigate(1)  # 0 -> 1 (Exit - Return to Lobby)

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
        # No selection yet, so shows hint to navigate
        assert "Navigate to select an option" in message

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
        controller.navigate(1)  # -1 -> 0 (first option)
        controller.navigate(1)  # 0 -> 1 (second option)

        message = controller.build_message()

        # First option should NOT have arrow
        assert "▶ Yes - Quarantine All" not in message
        # Second option should have arrow
        assert "▶ No - Discard Queue" in message

    def test_get_selected_option(self, stats_with_queue):
        """get_selected_option returns current selection text."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)
        controller.navigate(1)  # -1 -> 0 (first option)

        assert controller.get_selected_option() == "Yes - Quarantine All"

        controller.navigate(1)  # 0 -> 1 (second option)
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

    def test_is_new_high_score_default_false(self, stats_with_queue):
        """is_new_high_score defaults to False."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        assert controller.stats.is_new_high_score is False

    def test_is_new_high_score_true(self, stats_with_high_score):
        """is_new_high_score can be set to True."""
        controller = ArcadeResultsController()
        controller.show(stats_with_high_score)

        assert controller.stats.is_new_high_score is True
        assert controller.stats.total_eliminations == 100

    def test_build_message_shows_high_score_banner(self, stats_with_high_score):
        """Build message shows NEW HIGH SCORE banner when is_new_high_score is True."""
        controller = ArcadeResultsController()
        controller.show(stats_with_high_score)

        message = controller.build_message()

        assert "NEW HIGH SCORE" in message
        assert "🏆" in message

    def test_build_message_no_high_score_banner(self, stats_with_queue):
        """Build message does not show high score banner when is_new_high_score is False."""
        controller = ArcadeResultsController()
        controller.show(stats_with_queue)

        message = controller.build_message()

        assert "NEW HIGH SCORE" not in message
