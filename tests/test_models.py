"""Tests for core data models."""

import pytest
from models import (
    Vector2,
    GameState,
    GameStatus,
    ArcadeModeState,
    ArcadeStats,
    QuarantineReport,
)


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
            total_zombies=10,
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
            total_zombies=10,
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
            total_third_parties=5,
        )
        assert state.third_parties_blocked == 2
        assert state.total_third_parties == 5


class TestArcadeModeState:
    """Test arcade mode state management."""

    def test_arcade_mode_state_initialization(self):
        """Test ArcadeModeState initializes with default values."""
        state = ArcadeModeState()
        assert state.active is False
        assert state.in_countdown is False
        assert state.countdown_time == 3.0
        assert state.time_remaining == 60.0
        assert state.session_duration == 0.0
        assert state.eliminations_count == 0
        assert state.combo_count == 0
        assert state.combo_multiplier == 1.0
        assert state.highest_combo == 0
        assert state.powerups_collected == 0

    def test_arcade_mode_state_active_session(self):
        """Test arcade mode state during active session."""
        state = ArcadeModeState(
            active=True,
            in_countdown=False,
            countdown_time=0.0,
            time_remaining=45.5,
            session_duration=14.5,
            eliminations_count=25,
            combo_count=5,
            combo_multiplier=2.5,
            highest_combo=8,
            powerups_collected=3,
        )
        assert state.active is True
        assert state.in_countdown is False
        assert state.countdown_time == 0.0
        assert state.time_remaining == 45.5
        assert state.session_duration == 14.5
        assert state.eliminations_count == 25
        assert state.combo_count == 5
        assert state.combo_multiplier == 2.5
        assert state.highest_combo == 8
        assert state.powerups_collected == 3

    def test_arcade_mode_state_countdown_phase(self):
        """Test arcade mode state during countdown phase."""
        state = ArcadeModeState(
            active=True, in_countdown=True, countdown_time=2.5, time_remaining=60.0
        )
        assert state.active is True
        assert state.in_countdown is True
        assert state.countdown_time == 2.5
        assert state.time_remaining == 60.0

    def test_arcade_mode_state_combo_tracking(self):
        """Test arcade mode tracks combo count and multiplier."""
        state = ArcadeModeState(
            active=True, combo_count=10, combo_multiplier=3.0, highest_combo=12
        )
        assert state.combo_count == 10
        assert state.combo_multiplier == 3.0
        assert state.highest_combo == 12


class TestArcadeStats:
    """Test arcade mode statistics."""

    def test_arcade_stats_initialization(self):
        """Test ArcadeStats initializes with default values."""
        stats = ArcadeStats()
        assert stats.total_eliminations == 0
        assert stats.eliminations_per_second == 0.0
        assert stats.highest_combo == 0
        assert stats.powerups_collected == 0

    def test_arcade_stats_with_values(self):
        """Test arcade stats with actual session data."""
        stats = ArcadeStats(
            total_eliminations=50,
            eliminations_per_second=2.5,
            highest_combo=15,
            powerups_collected=8,
        )
        assert stats.total_eliminations == 50
        assert stats.eliminations_per_second == 2.5
        assert stats.highest_combo == 15
        assert stats.powerups_collected == 8

    def test_arcade_stats_calculates_rate(self):
        """Test arcade stats can represent elimination rate."""
        # Simulate 60 eliminations in 30 seconds = 2.0 per second
        stats = ArcadeStats(total_eliminations=60, eliminations_per_second=2.0)
        assert stats.total_eliminations == 60
        assert stats.eliminations_per_second == 2.0


class TestQuarantineReport:
    """Test quarantine batch operation reporting."""

    def test_quarantine_report_initialization(self):
        """Test QuarantineReport initializes with default values."""
        report = QuarantineReport()
        assert report.total_queued == 0
        assert report.successful == 0
        assert report.failed == 0
        assert report.error_messages == []

    def test_quarantine_report_all_successful(self):
        """Test quarantine report with all successful operations."""
        report = QuarantineReport(
            total_queued=10, successful=10, failed=0, error_messages=[]
        )
        assert report.total_queued == 10
        assert report.successful == 10
        assert report.failed == 0
        assert len(report.error_messages) == 0

    def test_quarantine_report_with_failures(self):
        """Test quarantine report with some failures."""
        report = QuarantineReport(
            total_queued=10,
            successful=7,
            failed=3,
            error_messages=[
                "Failed to quarantine zombie-1: API timeout",
                "Failed to quarantine zombie-5: Invalid scope",
                "Failed to quarantine zombie-8: Network error",
            ],
        )
        assert report.total_queued == 10
        assert report.successful == 7
        assert report.failed == 3
        assert len(report.error_messages) == 3
        assert "API timeout" in report.error_messages[0]
        assert "Invalid scope" in report.error_messages[1]
        assert "Network error" in report.error_messages[2]

    def test_quarantine_report_tracks_success_rate(self):
        """Test quarantine report can calculate success rate."""
        report = QuarantineReport(total_queued=100, successful=95, failed=5)
        # Success rate = 95/100 = 95%
        success_rate = (report.successful / report.total_queued) * 100
        assert success_rate == 95.0
        assert report.successful + report.failed == report.total_queued
