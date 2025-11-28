"""Tests for player health and damage system."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from player import Player
from models import Vector2


class TestPlayerHealth:
    """Tests for player health initialization."""

    def test_player_starts_with_full_health(self):
        """Player starts with 10 HP."""
        player = Player(Vector2(100, 100))
        assert player.current_health == 10
        assert player.max_health == 10

    def test_player_starts_not_invincible(self):
        """Player starts without invincibility."""
        player = Player(Vector2(100, 100))
        assert not player.is_invincible
        assert player.is_visible

    def test_player_is_not_dead_at_full_health(self):
        """Player is not dead at full health."""
        player = Player(Vector2(100, 100))
        assert not player.is_dead


class TestPlayerTakeDamage:
    """Tests for player taking damage."""

    def test_take_damage_reduces_health(self):
        """Taking damage reduces health."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)
        assert player.current_health == 9

    def test_take_damage_returns_true_when_applied(self):
        """take_damage returns True when damage is applied."""
        player = Player(Vector2(100, 100))
        result = player.take_damage(1)
        assert result is True

    def test_take_damage_starts_invincibility(self):
        """Taking damage starts invincibility frames."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)
        assert player.is_invincible
        assert player.invincibility_timer == player.invincibility_duration

    def test_take_damage_blocked_during_invincibility(self):
        """Damage is blocked during invincibility."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)  # First hit - starts invincibility
        result = player.take_damage(1)  # Second hit - should be blocked
        assert result is False
        assert player.current_health == 9  # Health unchanged

    def test_take_damage_custom_amount(self):
        """Can take custom damage amounts."""
        player = Player(Vector2(100, 100))
        player.take_damage(3)
        assert player.current_health == 7

    def test_health_cannot_go_below_zero(self):
        """Health cannot go below zero."""
        player = Player(Vector2(100, 100))
        player.take_damage(20)  # More than max health
        assert player.current_health == 0

    def test_player_is_dead_at_zero_health(self):
        """Player is dead when health reaches zero."""
        player = Player(Vector2(100, 100))
        player.take_damage(10)
        assert player.is_dead


class TestPlayerHealing:
    """Tests for player healing."""

    def test_heal_restores_health(self):
        """Healing restores health."""
        player = Player(Vector2(100, 100))
        player.take_damage(5)
        player.heal(3)
        assert player.current_health == 8

    def test_heal_cannot_exceed_max_health(self):
        """Healing cannot exceed max health."""
        player = Player(Vector2(100, 100))
        player.take_damage(2)
        player.heal(10)  # Try to heal more than missing
        assert player.current_health == player.max_health

    def test_full_heal_restores_to_max(self):
        """full_heal restores to max health."""
        player = Player(Vector2(100, 100))
        player.take_damage(7)
        player.full_heal()
        assert player.current_health == player.max_health


class TestInvincibilityFrames:
    """Tests for invincibility frame system."""

    def test_invincibility_decrements_over_time(self):
        """Invincibility timer decrements over time."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)
        initial_timer = player.invincibility_timer

        player.update_invincibility(0.5)

        assert player.invincibility_timer == initial_timer - 0.5
        assert player.is_invincible  # Still invincible

    def test_invincibility_ends_after_duration(self):
        """Invincibility ends after full duration."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)

        player.update_invincibility(player.invincibility_duration + 0.1)

        assert not player.is_invincible
        assert player.is_visible

    def test_visibility_toggles_during_invincibility(self):
        """Visibility toggles during invincibility for flash effect."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)

        # After flash interval, visibility should toggle
        player.update_invincibility(player.flash_interval + 0.01)
        first_visible = player.is_visible

        player.update_invincibility(player.flash_interval + 0.01)
        second_visible = player.is_visible

        assert first_visible != second_visible  # Should have toggled


class TestHealthReset:
    """Tests for health reset functionality."""

    def test_reset_health_restores_full_health(self):
        """reset_health restores full health."""
        player = Player(Vector2(100, 100))
        player.take_damage(7)
        player.reset_health()
        assert player.current_health == player.max_health

    def test_reset_health_clears_invincibility(self):
        """reset_health clears invincibility."""
        player = Player(Vector2(100, 100))
        player.take_damage(1)  # Triggers invincibility
        player.reset_health()
        assert not player.is_invincible
        assert player.is_visible


class TestHealthPercentage:
    """Tests for health percentage property."""

    def test_full_health_is_100_percent(self):
        """Full health is 100% (1.0)."""
        player = Player(Vector2(100, 100))
        assert player.health_percentage == 1.0

    def test_half_health_is_50_percent(self):
        """Half health is 50% (0.5)."""
        player = Player(Vector2(100, 100))
        player.take_damage(5)
        assert player.health_percentage == 0.5

    def test_zero_health_is_0_percent(self):
        """Zero health is 0%."""
        player = Player(Vector2(100, 100))
        player.take_damage(10)
        assert player.health_percentage == 0.0
