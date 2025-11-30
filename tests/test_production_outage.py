"""Tests for the Production Outage system."""

import os
import sys

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from production_outage import ERROR_MESSAGES, OutageState, ProductionOutageManager


class TestOutageState:
    """Tests for OutageState dataclass."""

    def test_default_state(self):
        """Test default OutageState values."""
        state = OutageState()
        assert state.active is False
        assert state.time_remaining == 0.0
        assert state.total_duration == 5.0
        assert state.error_message == ""
        assert state.flash_timer == 0.0

    def test_active_state(self):
        """Test OutageState with active outage."""
        state = OutageState(
            active=True,
            time_remaining=3.5,
            total_duration=5.0,
            error_message="Test error",
            flash_timer=1.5,
        )
        assert state.active is True
        assert state.time_remaining == 3.5
        assert state.error_message == "Test error"


class TestProductionOutageManager:
    """Tests for ProductionOutageManager."""

    def test_initialization(self):
        """Test manager initialization with defaults."""
        manager = ProductionOutageManager()
        assert manager.is_active() is False
        assert manager.trigger_chance_per_second == 0.005
        assert manager.cooldown_seconds == 30.0
        assert manager.outage_duration == 5.0

    def test_custom_initialization(self):
        """Test manager with custom parameters."""
        manager = ProductionOutageManager(
            trigger_chance_per_second=0.01,
            cooldown_seconds=60.0,
            outage_duration=10.0,
        )
        assert manager.trigger_chance_per_second == 0.01
        assert manager.cooldown_seconds == 60.0
        assert manager.outage_duration == 10.0

    def test_manual_trigger(self):
        """Test manually triggering an outage."""
        manager = ProductionOutageManager()
        assert manager.is_active() is False

        manager.trigger()

        assert manager.is_active() is True
        state = manager.get_state()
        assert state.active is True
        assert state.time_remaining == 5.0
        assert state.error_message in ERROR_MESSAGES

    def test_trigger_while_active(self):
        """Test that triggering while active does nothing."""
        manager = ProductionOutageManager()
        manager.trigger()
        original_message = manager.get_state().error_message

        # Try to trigger again
        manager.trigger()

        # Should still have original message (not re-triggered)
        assert manager.get_state().error_message == original_message

    def test_update_decreases_time(self):
        """Test that update decreases time remaining."""
        manager = ProductionOutageManager()
        manager.trigger()

        initial_time = manager.get_state().time_remaining
        manager.update(1.0)  # 1 second elapsed

        assert manager.get_state().time_remaining == initial_time - 1.0

    def test_outage_ends_after_duration(self):
        """Test that outage ends after duration expires."""
        manager = ProductionOutageManager(outage_duration=2.0)
        manager.trigger()

        assert manager.is_active() is True

        # Update past duration
        manager.update(2.5)

        assert manager.is_active() is False

    def test_cooldown_prevents_immediate_retrigger(self):
        """Test that cooldown prevents immediate re-triggering."""
        manager = ProductionOutageManager(cooldown_seconds=10.0, outage_duration=1.0)
        manager.trigger()

        # End the outage
        manager.update(2.0)
        assert manager.is_active() is False

        # Should be in cooldown now - manual trigger still works
        manager.trigger()
        assert manager.is_active() is True

    def test_should_trigger_respects_cooldown(self):
        """Test that should_trigger returns False during cooldown."""
        manager = ProductionOutageManager(
            cooldown_seconds=10.0,
            outage_duration=1.0,
            trigger_chance_per_second=1.0,  # 100% chance
        )
        manager.trigger()
        manager.update(2.0)  # End outage, start cooldown

        # Even with 100% chance, should_trigger should return False during cooldown
        assert manager.should_trigger(1.0) is False

    def test_enable_disable(self):
        """Test enabling and disabling the manager."""
        manager = ProductionOutageManager(trigger_chance_per_second=1.0)

        manager.disable()
        assert manager.should_trigger(1.0) is False

        manager.enable()
        # With 100% chance, should trigger
        assert manager.should_trigger(1.0) is True

    def test_get_progress(self):
        """Test progress calculation."""
        manager = ProductionOutageManager(outage_duration=10.0)

        # Not active - no progress
        assert manager.get_progress() == 0.0

        manager.trigger()
        assert manager.get_progress() == 0.0  # Just started

        manager.update(5.0)  # Half way through
        assert abs(manager.get_progress() - 0.5) < 0.01

        manager.update(5.0)  # Complete
        assert manager.get_progress() == 0.0  # Ended

    def test_reset(self):
        """Test reset clears all state."""
        manager = ProductionOutageManager()
        manager.trigger()
        manager.update(1.0)

        manager.reset()

        assert manager.is_active() is False
        state = manager.get_state()
        assert state.active is False
        assert state.time_remaining == 0.0
        assert state.error_message == ""

    def test_flash_timer_updates(self):
        """Test that flash timer increases during outage."""
        manager = ProductionOutageManager()
        manager.trigger()

        initial_flash = manager.get_state().flash_timer
        manager.update(0.5)
        new_flash = manager.get_state().flash_timer

        assert new_flash > initial_flash

    def test_update_returns_true_when_outage_ends(self):
        """Test that update returns True when outage just ended."""
        manager = ProductionOutageManager(outage_duration=1.0)
        manager.trigger()

        # Before ending
        ended = manager.update(0.5)
        assert ended is False

        # When ending
        ended = manager.update(1.0)
        assert ended is True

        # After ended
        ended = manager.update(0.5)
        assert ended is False


class TestErrorMessages:
    """Tests for error messages."""

    def test_error_messages_exist(self):
        """Test that error messages list is populated."""
        assert len(ERROR_MESSAGES) > 0

    def test_error_messages_are_strings(self):
        """Test that all error messages are strings."""
        for msg in ERROR_MESSAGES:
            assert isinstance(msg, str)
            assert len(msg) > 0

    def test_random_message_selection(self):
        """Test that different messages can be selected."""
        manager = ProductionOutageManager()
        messages_seen = set()

        # Trigger multiple times and collect unique messages
        for _ in range(50):
            manager.trigger()
            messages_seen.add(manager.get_state().error_message)
            manager.reset()

        # Should see at least a few different messages
        assert len(messages_seen) > 1
