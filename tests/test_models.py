"""Tests for core data models."""

import pytest
from src.models import Vector2, GameState, GameStatus


class TestVector2:
    """Test 2D vector operations."""

    def test_vector2_initialization(self):
        """Test Vector2 creates with x and y coordinates."""
        vec = Vector2(10, 20)
        assert vec.x == 10
        assert vec.y == 20

    def test_vector2_addition(self):
        """Test adding two vectors."""
        vec1 = Vector2(10, 20)
        vec2 = Vector2(5, 15)
        result = vec1 + vec2
        assert result.x == 15
        assert result.y == 35

    def test_vector2_subtraction(self):
        """Test subtracting two vectors."""
        vec1 = Vector2(10, 20)
        vec2 = Vector2(5, 15)
        result = vec1 - vec2
        assert result.x == 5
        assert result.y == 5

    def test_vector2_scalar_multiplication(self):
        """Test multiplying vector by scalar."""
        vec = Vector2(10, 20)
        result = vec * 2
        assert result.x == 20
        assert result.y == 40


class TestGameState:
    """Test game state management."""

    def test_game_state_initializes_with_required_fields(self):
        """Test GameState creates with required fields."""
        state = GameState(
            status=GameStatus.LOBBY,
            zombies_remaining=10,
            zombies_quarantined=0,
            total_zombies=10
        )
        assert state.status == GameStatus.LOBBY
        assert state.zombies_remaining == 10
        assert state.zombies_quarantined == 0
        assert state.total_zombies == 10

    def test_game_state_tracks_zombie_counts(self):
        """Test game state tracks zombie elimination progress."""
        state = GameState(
            status=GameStatus.PLAYING,
            zombies_remaining=5,
            zombies_quarantined=5,
            total_zombies=10
        )
        assert state.zombies_remaining == 5
        assert state.zombies_quarantined == 5
        assert state.total_zombies == 10

    def test_game_state_tracks_third_parties(self):
        """Test game state tracks third party blocking."""
        state = GameState(
            status=GameStatus.LOBBY,
            zombies_remaining=0,
            zombies_quarantined=0,
            total_zombies=0,
            third_parties_blocked=2,
            total_third_parties=5
        )
        assert state.third_parties_blocked == 2
        assert state.total_third_parties == 5
