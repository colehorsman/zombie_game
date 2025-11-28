"""Tests for combo tracking system."""

import pytest
from hypothesis import given, strategies as st

from src.combo_tracker import ComboTracker


class TestComboTrackerBasics:
    """Basic unit tests for combo tracker."""

    def test_combo_tracker_initialization(self):
        """Test combo tracker initializes with correct defaults."""
        tracker = ComboTracker()
        assert tracker.combo_count == 0
        assert tracker.combo_timer == 0.0
        assert tracker.combo_window == 3.0
        assert tracker.highest_combo == 0
        assert tracker.combo_multiplier_threshold == 5
        assert tracker.combo_multiplier == 1.5

    def test_add_elimination_increments_combo(self):
        """Test adding elimination increments combo count."""
        tracker = ComboTracker()
        tracker.add_elimination()
        assert tracker.combo_count == 1
        assert tracker.combo_timer == 3.0

    def test_add_multiple_eliminations(self):
        """Test adding multiple eliminations."""
        tracker = ComboTracker()
        tracker.add_elimination()
        tracker.add_elimination()
        tracker.add_elimination()
        assert tracker.combo_count == 3
        assert tracker.combo_timer == 3.0  # Timer resets on each elimination

    def test_combo_expires_after_window(self):
        """Test combo expires after 3-second window."""
        tracker = ComboTracker()
        tracker.add_elimination()
        assert tracker.combo_count == 1
        
        # Update for 3.1 seconds (past window)
        tracker.update(3.1)
        
        assert tracker.combo_count == 0
        assert tracker.combo_timer == 0.0

    def test_combo_maintained_within_window(self):
        """Test combo is maintained if elimination added within window."""
        tracker = ComboTracker()
        tracker.add_elimination()
        
        # Update for 2 seconds (within window)
        tracker.update(2.0)
        assert tracker.combo_count == 1
        assert tracker.combo_timer == 1.0
        
        # Add another elimination before expiry
        tracker.add_elimination()
        assert tracker.combo_count == 2
        assert tracker.combo_timer == 3.0

    def test_multiplier_inactive_below_threshold(self):
        """Test multiplier is 1.0 below threshold."""
        tracker = ComboTracker()
        tracker.add_elimination()
        tracker.add_elimination()
        tracker.add_elimination()
        tracker.add_elimination()
        
        assert tracker.combo_count == 4
        assert tracker.get_combo_multiplier() == 1.0
        assert tracker.is_multiplier_active() is False

    def test_multiplier_active_at_threshold(self):
        """Test multiplier is 1.5 at threshold."""
        tracker = ComboTracker()
        for _ in range(5):
            tracker.add_elimination()
        
        assert tracker.combo_count == 5
        assert tracker.get_combo_multiplier() == 1.5
        assert tracker.is_multiplier_active() is True

    def test_multiplier_active_above_threshold(self):
        """Test multiplier remains 1.5 above threshold."""
        tracker = ComboTracker()
        for _ in range(10):
            tracker.add_elimination()
        
        assert tracker.combo_count == 10
        assert tracker.get_combo_multiplier() == 1.5
        assert tracker.is_multiplier_active() is True

    def test_highest_combo_tracking(self):
        """Test highest combo is tracked."""
        tracker = ComboTracker()
        
        # First combo
        for _ in range(5):
            tracker.add_elimination()
        assert tracker.highest_combo == 5
        
        # Let it expire
        tracker.update(3.1)
        assert tracker.combo_count == 0
        assert tracker.highest_combo == 5  # Highest preserved
        
        # Second combo (lower)
        for _ in range(3):
            tracker.add_elimination()
        assert tracker.combo_count == 3
        assert tracker.highest_combo == 5  # Still 5
        
        # Let it expire
        tracker.update(3.1)
        
        # Third combo (higher)
        for _ in range(8):
            tracker.add_elimination()
        assert tracker.combo_count == 8
        assert tracker.highest_combo == 8  # Updated to 8

    def test_reset_clears_all_state(self):
        """Test reset clears all combo state."""
        tracker = ComboTracker()
        for _ in range(10):
            tracker.add_elimination()
        
        assert tracker.combo_count == 10
        assert tracker.highest_combo == 10
        
        tracker.reset()
        
        assert tracker.combo_count == 0
        assert tracker.combo_timer == 0.0
        assert tracker.highest_combo == 0


class TestComboTrackerProperties:
    """Property-based tests for combo tracker."""

    @given(st.integers(min_value=1, max_value=100))
    def test_property_15_combo_chaining(self, elimination_count):
        """
        Property 15: Combo chaining
        
        Given: A series of eliminations within the 3-second window
        When: Each elimination is added before the timer expires
        Then: Combo count equals the number of eliminations
        
        Validates: Requirements 7.2
        """
        tracker = ComboTracker()
        
        for i in range(elimination_count):
            tracker.add_elimination()
            # Update for 2 seconds (within 3-second window)
            tracker.update(2.0)
        
        # Final combo count should equal eliminations
        # (minus 1 because last update might expire it)
        # Actually, we need to be more careful here
        # Let's not update after the last elimination
        tracker2 = ComboTracker()
        for i in range(elimination_count):
            tracker2.add_elimination()
            if i < elimination_count - 1:  # Don't update after last
                tracker2.update(2.0)
        
        assert tracker2.combo_count == elimination_count

    @given(st.floats(min_value=3.1, max_value=10.0))
    def test_property_16_combo_expiration(self, expiry_time):
        """
        Property 16: Combo expiration
        
        Given: A combo is active
        When: Time exceeds the 3-second window without new eliminations
        Then: Combo count resets to 0
        
        Validates: Requirements 7.3
        """
        tracker = ComboTracker()
        tracker.add_elimination()
        tracker.add_elimination()
        tracker.add_elimination()
        
        initial_combo = tracker.combo_count
        assert initial_combo == 3
        
        # Update past the window
        tracker.update(expiry_time)
        
        # Combo should be expired
        assert tracker.combo_count == 0
        assert tracker.combo_timer == 0.0

    @given(st.integers(min_value=5, max_value=50))
    def test_property_17_combo_multiplier_activation(self, combo_count):
        """
        Property 17: Combo multiplier activation
        
        Given: A combo count >= 5
        When: Checking the multiplier
        Then: Multiplier is 1.5x
        
        Validates: Requirements 7.5
        """
        tracker = ComboTracker()
        
        for _ in range(combo_count):
            tracker.add_elimination()
        
        assert tracker.combo_count == combo_count
        assert tracker.get_combo_multiplier() == 1.5
        assert tracker.is_multiplier_active() is True

    @given(st.integers(min_value=1, max_value=4))
    def test_property_combo_multiplier_inactive_below_threshold(self, combo_count):
        """
        Property: Combo multiplier inactive below threshold
        
        Given: A combo count < 5
        When: Checking the multiplier
        Then: Multiplier is 1.0x
        """
        tracker = ComboTracker()
        
        for _ in range(combo_count):
            tracker.add_elimination()
        
        assert tracker.combo_count == combo_count
        assert tracker.get_combo_multiplier() == 1.0
        assert tracker.is_multiplier_active() is False

    @given(
        st.integers(min_value=1, max_value=20),
        st.floats(min_value=0.1, max_value=2.9)
    )
    def test_property_combo_timer_resets_on_elimination(self, eliminations, time_elapsed):
        """
        Property: Combo timer resets on elimination
        
        Given: A combo with some time elapsed
        When: A new elimination is added
        Then: Timer resets to 3.0 seconds
        """
        tracker = ComboTracker()
        
        for _ in range(eliminations):
            tracker.add_elimination()
            tracker.update(time_elapsed)
        
        # Add one more elimination
        tracker.add_elimination()
        
        # Timer should be reset to full window
        assert tracker.combo_timer == 3.0

    @given(st.lists(st.integers(min_value=1, max_value=20), min_size=1, max_size=10))
    def test_property_highest_combo_monotonic(self, combo_sequences):
        """
        Property: Highest combo is monotonically increasing
        
        Given: Multiple combo sequences
        When: Each sequence is completed
        Then: Highest combo never decreases
        """
        tracker = ComboTracker()
        previous_highest = 0
        
        for combo_size in combo_sequences:
            # Build combo
            for _ in range(combo_size):
                tracker.add_elimination()
            
            # Check highest is monotonic
            assert tracker.highest_combo >= previous_highest
            previous_highest = tracker.highest_combo
            
            # Let combo expire
            tracker.update(3.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
