"""Tests for Arcade Mode Manager."""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock

from src.arcade_mode import ArcadeModeManager
from src.models import ArcadeStats, ArcadeModeState, Vector2
from src.zombie import Zombie
from src.powerup import PowerUpType
from dataclasses import is_dataclass


class TestArcadeModeManagerBasics:
    """Basic unit tests for arcade mode manager."""

    def test_arcade_mode_manager_initialization(self):
        """Test arcade mode manager initializes correctly."""
        manager = ArcadeModeManager()
        assert manager.active is False
        assert manager.time_remaining == 60.0
        assert manager.countdown_time == 3.0
        assert manager.in_countdown is False
        assert len(manager.elimination_queue) == 0
        assert manager.eliminations_count == 0
        assert manager.powerups_collected == 0
        assert manager.highest_combo == 0
        assert manager.session_duration == 0.0

    def test_start_session_activates_countdown(self):
        """Test starting session activates countdown."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        assert manager.active is True
        assert manager.in_countdown is True
        assert manager.countdown_time == 3.0
        assert manager.time_remaining == 60.0

    def test_start_session_resets_statistics(self):
        """Test starting session resets all statistics."""
        manager = ArcadeModeManager()
        
        # Simulate previous session
        manager.eliminations_count = 50
        manager.powerups_collected = 10
        manager.highest_combo = 15
        manager.elimination_queue.append(Mock())
        
        # Start new session
        manager.start_session()
        
        assert manager.eliminations_count == 0
        assert manager.powerups_collected == 0
        assert manager.highest_combo == 0
        assert len(manager.elimination_queue) == 0

    def test_countdown_phase_decrements_countdown_timer(self):
        """Test countdown phase decrements countdown timer."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        assert manager.in_countdown is True
        assert manager.countdown_time == 3.0
        
        # Update for 1 second
        manager.update(1.0)
        
        assert manager.in_countdown is True
        assert manager.countdown_time == 2.0
        assert manager.time_remaining == 60.0  # Main timer not started

    def test_countdown_completes_and_starts_main_timer(self):
        """Test countdown completion starts main timer."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Update past countdown
        manager.update(3.1)
        
        assert manager.in_countdown is False
        assert manager.countdown_time == 0.0
        
        # Now main timer should update
        manager.update(1.0)
        assert manager.time_remaining == 59.0

    def test_main_timer_decrements_after_countdown(self):
        """Test main timer decrements after countdown."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Complete countdown
        manager.update(3.1)
        
        # Update main timer
        manager.update(10.0)
        
        assert manager.time_remaining == 50.0
        assert manager.session_duration == 10.0

    def test_session_ends_when_timer_reaches_zero(self):
        """Test session ends when timer reaches zero."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Complete countdown
        manager.update(3.1)
        
        # Update past 60 seconds
        manager.update(60.1)
        
        assert manager.active is False
        assert manager.time_remaining == 0.0

    def test_queue_elimination_adds_to_queue(self):
        """Test queueing elimination adds zombie to queue."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="123456789012"
        )
        
        manager.queue_elimination(zombie)
        
        assert len(manager.elimination_queue) == 1
        assert manager.eliminations_count == 1
        assert zombie in manager.elimination_queue

    def test_queue_elimination_prevents_duplicates(self):
        """Test queueing same zombie twice doesn't duplicate."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="123456789012"
        )
        
        manager.queue_elimination(zombie)
        manager.queue_elimination(zombie)  # Try to add again
        
        assert len(manager.elimination_queue) == 1
        assert manager.eliminations_count == 1  # Count should still be 1

    def test_queue_elimination_updates_combo(self):
        """Test queueing elimination updates combo tracker."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        zombie1 = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        zombie2 = Zombie("z2", "Z2", Vector2(200, 100), "123456789012")
        
        manager.queue_elimination(zombie1)
        manager.queue_elimination(zombie2)
        
        assert manager.get_combo_count() == 2

    def test_queue_elimination_tracks_highest_combo(self):
        """Test queueing eliminations tracks highest combo."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Build combo of 5
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        assert manager.highest_combo == 5
        
        # Complete countdown and let combo expire
        manager.update(3.1)  # Complete countdown
        manager.update(3.1)  # Expire combo
        
        # Build combo of 3
        for i in range(3):
            zombie = Zombie(f"z2-{i}", f"Z2-{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        # Highest should still be 5
        assert manager.highest_combo == 5

    def test_record_powerup_collection(self):
        """Test recording power-up collection."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        manager.record_powerup_collection(PowerUpType.STAR_POWER)
        manager.record_powerup_collection(PowerUpType.LAMBDA_SPEED)
        
        assert manager.powerups_collected == 2

    def test_clear_elimination_queue(self):
        """Test clearing elimination queue."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Add some zombies
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        assert len(manager.elimination_queue) == 5
        
        manager.clear_elimination_queue()
        
        assert len(manager.elimination_queue) == 0

    def test_get_elimination_queue_returns_copy(self):
        """Test get_elimination_queue returns a copy."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        manager.queue_elimination(zombie)
        
        queue_copy = manager.get_elimination_queue()
        queue_copy.clear()
        
        # Original queue should be unchanged
        assert len(manager.elimination_queue) == 1

    def test_get_stats_calculates_eliminations_per_second(self):
        """Test get_stats calculates eliminations per second."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Complete countdown
        manager.update(3.1)
        
        # Add 10 eliminations
        for i in range(10):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        # Simulate 5 seconds elapsed
        manager.update(5.0)
        
        stats = manager.get_stats()
        
        assert stats.total_eliminations == 10
        assert stats.eliminations_per_second == pytest.approx(2.0, abs=0.1)

    def test_get_stats_returns_correct_values(self):
        """Test get_stats returns all correct values."""
        manager = ArcadeModeManager()
        manager.start_session()
        manager.update(3.1)  # Complete countdown
        
        # Add eliminations and power-ups
        for i in range(8):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        manager.record_powerup_collection(PowerUpType.STAR_POWER)
        manager.record_powerup_collection(PowerUpType.LAMBDA_SPEED)
        manager.record_powerup_collection(PowerUpType.LASER_BEAM)
        
        manager.update(10.0)
        
        stats = manager.get_stats()
        
        assert stats.total_eliminations == 8
        assert stats.highest_combo == 8
        assert stats.powerups_collected == 3
        assert stats.eliminations_per_second > 0

    def test_get_state_returns_current_state(self):
        """Test get_state returns current arcade mode state."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        state = manager.get_state()
        
        # Check it's a dataclass with the right fields
        assert is_dataclass(state)
        assert state.active is True
        assert state.in_countdown is True
        assert state.countdown_time == 3.0
        assert state.time_remaining == 60.0

    def test_cancel_session_stops_arcade_mode(self):
        """Test cancel_session stops arcade mode."""
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Add some eliminations
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        manager.queue_elimination(zombie)
        
        manager.cancel_session()
        
        assert manager.active is False
        assert manager.in_countdown is False
        assert len(manager.elimination_queue) == 0


class TestArcadeModeManagerProperties:
    """Property-based tests for arcade mode manager."""

    @given(st.floats(min_value=0.1, max_value=3.0))
    def test_property_7_timer_countdown(self, delta_time):
        """
        Property 7: Timer countdown
        
        Given: Arcade mode is active (past countdown)
        When: Time elapses
        Then: Timer decreases by elapsed time
        
        Validates: Requirements 3.2
        """
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Complete countdown
        manager.update(3.1)
        
        initial_time = manager.time_remaining
        manager.update(delta_time)
        
        assert manager.time_remaining == pytest.approx(initial_time - delta_time, abs=0.01)

    @given(st.floats(min_value=60.1, max_value=100.0))
    def test_property_8_session_termination(self, elapsed_time):
        """
        Property 8: Session termination
        
        Given: Arcade mode is active
        When: Timer reaches 0
        Then: Session ends (active = False)
        
        Validates: Requirements 3.5
        """
        manager = ArcadeModeManager()
        manager.start_session()
        
        # Complete countdown
        manager.update(3.1)
        
        # Update past 60 seconds
        manager.update(elapsed_time)
        
        assert manager.active is False
        assert manager.time_remaining == 0.0

    @given(st.integers(min_value=1, max_value=100))
    def test_property_4_elimination_queueing(self, zombie_count):
        """
        Property 4: Elimination queueing without API calls
        
        Given: Arcade mode is active
        When: Zombies are eliminated
        Then: They are queued without API calls
        
        Validates: Requirements 2.1
        """
        manager = ArcadeModeManager()
        manager.start_session()
        
        zombies = []
        for i in range(zombie_count):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            zombies.append(zombie)
            manager.queue_elimination(zombie)
        
        assert len(manager.elimination_queue) == zombie_count
        assert manager.eliminations_count == zombie_count

    @given(st.integers(min_value=1, max_value=50))
    def test_property_6_queue_count_accuracy(self, elimination_count):
        """
        Property 6: Queue count accuracy
        
        Given: Eliminations are queued
        When: Checking queue size
        Then: Queue size matches elimination count
        
        Validates: Requirements 2.4, 6.1
        """
        manager = ArcadeModeManager()
        manager.start_session()
        
        for i in range(elimination_count):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        assert len(manager.elimination_queue) == elimination_count
        assert manager.eliminations_count == elimination_count
        
        stats = manager.get_stats()
        assert stats.total_eliminations == elimination_count

    @given(st.integers(min_value=1, max_value=20))
    def test_property_2_arcade_initialization(self, _):
        """
        Property 2: Arcade mode initialization
        
        Given: Arcade mode is started
        When: Checking initial state
        Then: All state is reset correctly
        
        Validates: Requirements 1.3, 1.4, 3.1
        """
        manager = ArcadeModeManager()
        
        # Pollute state
        manager.eliminations_count = 99
        manager.powerups_collected = 99
        manager.highest_combo = 99
        
        # Start fresh session
        manager.start_session()
        
        assert manager.active is True
        assert manager.in_countdown is True
        assert manager.countdown_time == 3.0
        assert manager.time_remaining == 60.0
        assert manager.eliminations_count == 0
        assert manager.powerups_collected == 0
        assert manager.highest_combo == 0
        assert len(manager.elimination_queue) == 0

    @given(
        st.integers(min_value=1, max_value=30),
        st.floats(min_value=1.0, max_value=30.0)
    )
    def test_property_13_statistics_calculation(self, eliminations, time_elapsed):
        """
        Property 13: Statistics calculation
        
        Given: Eliminations and time elapsed
        When: Getting statistics
        Then: Eliminations per second is calculated correctly
        
        Validates: Requirements 6.2
        """
        manager = ArcadeModeManager()
        manager.start_session()
        manager.update(3.1)  # Complete countdown
        
        # Add eliminations
        for i in range(eliminations):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            manager.queue_elimination(zombie)
        
        # Simulate time
        manager.update(time_elapsed)
        
        stats = manager.get_stats()
        
        expected_rate = eliminations / time_elapsed
        assert stats.eliminations_per_second == pytest.approx(expected_rate, abs=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
