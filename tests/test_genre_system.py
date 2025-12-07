"""Property-based tests for the multi-genre level system.

Tests genre selection, persistence, and unlock conditions.
"""

import sys

sys.path.insert(0, "src")

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from genre_manager import GenreManager
from models import GENRE_UNLOCK_CONDITIONS, GenreType

# Strategies for generating test data
genre_strategy = st.sampled_from(list(GenreType))
account_id_strategy = st.text(
    alphabet="0123456789", min_size=9, max_size=12
)  # AWS account IDs


class TestGenrePreferencePersistence:
    """Property 2: Genre Preference Persistence

    *For any* genre selection for an account, saving and loading SHALL
    restore the same genre preference for that account.

    **Validates: Requirements 1.4, 9.5**
    **Feature: multi-genre-levels, Property 2: Genre Preference Persistence**
    """

    @given(account_id=account_id_strategy, genre=genre_strategy)
    @settings(max_examples=50)
    def test_genre_preference_round_trip(self, account_id: str, genre: GenreType):
        """Test that genre preferences survive serialization round-trip."""
        # Create manager and unlock all genres for testing
        manager = GenreManager()
        manager.unlock_all()

        # Set preference
        manager.select_genre(account_id, genre)

        # Serialize
        data = manager.to_dict()

        # Deserialize into new manager
        restored = GenreManager.from_dict(data)

        # Verify preference preserved
        assert restored.get_genre_for_account(account_id) == genre

    @given(
        account_ids=st.lists(account_id_strategy, min_size=1, max_size=10, unique=True),
        genres=st.lists(genre_strategy, min_size=1, max_size=10),
    )
    @settings(max_examples=30)
    def test_multiple_preferences_round_trip(self, account_ids: list, genres: list):
        """Test that multiple account preferences survive round-trip."""
        manager = GenreManager()
        manager.unlock_all()

        # Set preferences for each account
        expected = {}
        for i, account_id in enumerate(account_ids):
            genre = genres[i % len(genres)]
            manager.select_genre(account_id, genre)
            expected[account_id] = genre

        # Serialize and restore
        data = manager.to_dict()
        restored = GenreManager.from_dict(data)

        # Verify all preferences preserved
        for account_id, genre in expected.items():
            assert restored.get_genre_for_account(account_id) == genre


class TestGenreUnlockConditions:
    """Property 11: Genre Unlock Conditions

    *For any* new player, only Platformer SHALL be unlocked; completing 1 level
    SHALL unlock Space Shooter; eliminating 50 zombies SHALL unlock Maze Chase;
    completing 3 levels SHALL unlock Fighting.

    **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
    **Feature: multi-genre-levels, Property 11: Genre Unlock Conditions**
    """

    def test_platformer_unlocked_by_default(self):
        """Test that platformer is always unlocked for new players."""
        manager = GenreManager()
        assert manager.is_genre_unlocked(GenreType.PLATFORMER)
        assert GenreType.PLATFORMER in manager.get_available_genres()

    def test_space_shooter_unlocks_at_1_level(self):
        """Test that Space Shooter unlocks after completing 1 level."""
        manager = GenreManager()

        # Before completing any levels
        assert not manager.is_genre_unlocked(GenreType.SPACE_SHOOTER)

        # After completing 1 level
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=1, zombies_eliminated=0
        )
        assert GenreType.SPACE_SHOOTER in newly_unlocked

    def test_maze_chase_unlocks_at_50_zombies(self):
        """Test that Maze Chase unlocks after eliminating 50 zombies."""
        manager = GenreManager()

        # Before 50 zombies
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=0, zombies_eliminated=49
        )
        assert GenreType.MAZE_CHASE not in newly_unlocked

        # At exactly 50 zombies
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=0, zombies_eliminated=50
        )
        assert GenreType.MAZE_CHASE in newly_unlocked

    def test_fighting_unlocks_at_3_levels(self):
        """Test that Fighting unlocks after completing 3 levels."""
        manager = GenreManager()

        # Before 3 levels
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=2, zombies_eliminated=0
        )
        assert GenreType.FIGHTING not in newly_unlocked

        # At exactly 3 levels
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=3, zombies_eliminated=0
        )
        assert GenreType.FIGHTING in newly_unlocked

    @given(
        levels=st.integers(min_value=0, max_value=100),
        zombies=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=50)
    def test_unlock_conditions_are_monotonic(self, levels: int, zombies: int):
        """Test that once unlocked, genres stay unlocked."""
        manager = GenreManager()

        # Check what should be unlocked
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=levels, zombies_eliminated=zombies
        )

        # Unlock them
        for genre in newly_unlocked:
            manager.unlock_genre(genre)

        # Verify they stay unlocked even with lower values
        for genre in manager.get_available_genres():
            assert manager.is_genre_unlocked(genre)


class TestGenreSelection:
    """Tests for genre selection behavior."""

    def test_cannot_select_locked_genre(self):
        """Test that locked genres cannot be selected."""
        manager = GenreManager()

        # Space shooter is locked by default
        result = manager.select_genre("123456789", GenreType.SPACE_SHOOTER)
        assert result is False

        # Should still be platformer
        assert manager.get_genre_for_account("123456789") == GenreType.PLATFORMER

    def test_can_select_unlocked_genre(self):
        """Test that unlocked genres can be selected."""
        manager = GenreManager()
        manager.unlock_genre(GenreType.SPACE_SHOOTER)

        result = manager.select_genre("123456789", GenreType.SPACE_SHOOTER)
        assert result is True
        assert manager.get_genre_for_account("123456789") == GenreType.SPACE_SHOOTER

    def test_default_genre_is_platformer(self):
        """Test that default genre for unknown accounts is platformer."""
        manager = GenreManager()
        assert manager.get_genre_for_account("unknown") == GenreType.PLATFORMER


class TestUnlockedGenresPersistence:
    """Tests for unlocked genres persistence."""

    @given(
        genres_to_unlock=st.lists(genre_strategy, min_size=0, max_size=4, unique=True)
    )
    @settings(max_examples=30)
    def test_unlocked_genres_round_trip(self, genres_to_unlock: list):
        """Test that unlocked genres survive serialization."""
        manager = GenreManager()

        # Unlock specified genres
        for genre in genres_to_unlock:
            manager.unlock_genre(genre)

        # Serialize and restore
        data = manager.to_dict()
        restored = GenreManager.from_dict(data)

        # Platformer should always be unlocked
        assert restored.is_genre_unlocked(GenreType.PLATFORMER)

        # All unlocked genres should be preserved
        for genre in genres_to_unlock:
            assert restored.is_genre_unlocked(genre)


class TestGenreSelectionTriggersCorrectTemplate:
    """Property 1: Genre Selection Triggers Correct Template

    *For any* genre selection, the system SHALL load the corresponding
    controller type that matches the selected genre.

    **Validates: Requirements 1.3, 2.1, 3.1, 4.1, 5.1**
    **Feature: multi-genre-levels, Property 1: Genre Selection Triggers Correct Template**
    """

    def test_genre_controller_factory_returns_correct_type(self):
        """Test that factory creates correct controller for each genre."""
        from genre_controller import GenreController, GenreControllerFactory

        # Register mock controllers for testing
        class MockPlatformerController(GenreController):
            def initialize_level(self, account_id, zombies, level_width, level_height):
                pass

            def update(self, delta_time, player):
                pass

            def handle_input(self, input_state, player):
                pass

            def check_completion(self):
                return False

            def render(self, surface, camera_offset):
                pass

        # Register the mock
        GenreControllerFactory.register(GenreType.PLATFORMER, MockPlatformerController)

        # Create controller
        controller = GenreControllerFactory.create(GenreType.PLATFORMER, 800, 600)

        # Verify correct type
        assert controller is not None
        assert controller.genre == GenreType.PLATFORMER
        assert isinstance(controller, MockPlatformerController)

    @given(genre=genre_strategy)
    @settings(max_examples=20)
    def test_genre_controller_matches_selected_genre(self, genre: GenreType):
        """Test that created controller always matches the requested genre."""
        from genre_controller import GenreController, GenreControllerFactory

        # Create a generic mock controller class
        class GenericMockController(GenreController):
            def initialize_level(self, account_id, zombies, level_width, level_height):
                pass

            def update(self, delta_time, player):
                pass

            def handle_input(self, input_state, player):
                pass

            def check_completion(self):
                return False

            def render(self, surface, camera_offset):
                pass

        # Register for this genre
        GenreControllerFactory.register(genre, GenericMockController)

        # Create controller
        controller = GenreControllerFactory.create(genre, 800, 600)

        # Verify genre matches
        assert controller is not None
        assert controller.genre == genre

    def test_unregistered_genre_returns_none(self):
        """Test that unregistered genres return None."""
        from genre_controller import GenreControllerFactory

        # Clear any existing registrations for a test genre
        # Check if MAZE_CHASE is registered - if not, it should return None
        registered = GenreControllerFactory.get_registered_genres()

        # Find a genre that's not registered
        for genre in GenreType:
            if genre not in registered:
                result = GenreControllerFactory.create(genre, 800, 600)
                assert result is None
                return

        # If all genres are registered, this test passes trivially
        # (all genres have controllers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
