"""Tests for arcade mode power-ups."""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import patch
import pygame

from src.powerup import PowerUp, PowerUpType, PowerUpManager, spawn_random_powerups
from src.models import Vector2


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame for all tests in this module."""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


class TestArcadePowerUps:
    """Tests for arcade-specific power-ups."""

    def test_laser_beam_duration(self):
        """Test LASER_BEAM has 10 second duration."""
        powerup = PowerUp(Vector2(100, 100), PowerUpType.LASER_BEAM)
        assert powerup.duration == 10.0

    def test_burst_shot_instant(self):
        """Test BURST_SHOT is instant (0 duration)."""
        powerup = PowerUp(Vector2(100, 100), PowerUpType.BURST_SHOT)
        assert powerup.duration == 0.0

    def test_burst_shot_charges(self):
        """Test BURST_SHOT has 3 charges."""
        powerup = PowerUp(Vector2(100, 100), PowerUpType.BURST_SHOT)
        assert powerup.effect_value == 3.0

    def test_laser_beam_description(self):
        """Test LASER_BEAM has correct description."""
        powerup = PowerUp(Vector2(100, 100), PowerUpType.LASER_BEAM)
        assert "continuous laser fire" in powerup.get_description().lower()

    def test_burst_shot_description(self):
        """Test BURST_SHOT has correct description."""
        powerup = PowerUp(Vector2(100, 100), PowerUpType.BURST_SHOT)
        assert "one-shot" in powerup.get_description().lower()


class TestArcadePowerUpSpawning:
    """Tests for arcade mode power-up spawning."""

    def test_spawn_arcade_powerups_count(self):
        """Test spawning correct number of arcade power-ups."""
        powerups = spawn_random_powerups(
            level_width=1000, ground_y=500, count=5, arcade_mode=True
        )
        assert len(powerups) == 5

    def test_spawn_arcade_powerups_types(self):
        """Test arcade mode spawns arcade power-up types."""
        powerups = spawn_random_powerups(
            level_width=1000, ground_y=500, count=20, arcade_mode=True
        )

        # All should be arcade types
        arcade_types = {
            PowerUpType.LASER_BEAM,
            PowerUpType.BURST_SHOT,
            PowerUpType.STAR_POWER,
        }
        for powerup in powerups:
            assert powerup.powerup_type in arcade_types

    def test_spawn_normal_powerups_all_types(self):
        """Test normal mode can spawn all power-up types."""
        powerups = spawn_random_powerups(
            level_width=1000, ground_y=500, count=50, arcade_mode=False
        )

        # Should have variety of types (with 50 spawns, very likely to get all 4)
        types_spawned = {p.powerup_type for p in powerups}
        assert len(types_spawned) >= 2  # At least 2 different types

    @given(st.integers(min_value=1, max_value=20))
    def test_property_9_arcade_powerup_spawning(self, count):
        """
        Property 9: Arcade power-up spawning

        Given: Arcade mode is active
        When: Power-ups are spawned
        Then: Only arcade types (LASER_BEAM, BURST_SHOT, STAR_POWER) spawn

        Validates: Requirements 4.1, 4.2, 4.3
        """
        powerups = spawn_random_powerups(
            level_width=1000, ground_y=500, count=count, arcade_mode=True
        )

        assert len(powerups) == count

        arcade_types = {
            PowerUpType.LASER_BEAM,
            PowerUpType.BURST_SHOT,
            PowerUpType.STAR_POWER,
        }
        for powerup in powerups:
            assert powerup.powerup_type in arcade_types


class TestPowerUpManager:
    """Tests for PowerUpManager with arcade power-ups."""

    def test_activate_laser_beam(self):
        """Test activating LASER_BEAM power-up."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(100, 100), PowerUpType.LASER_BEAM)

        manager.activate(powerup)

        assert manager.is_active(PowerUpType.LASER_BEAM)
        assert manager.get_remaining_time(PowerUpType.LASER_BEAM) == 10.0

    def test_activate_burst_shot(self):
        """Test activating BURST_SHOT power-up."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(100, 100), PowerUpType.BURST_SHOT)

        manager.activate(powerup)

        # Burst shot is instant, so not in active effects
        assert not manager.is_active(PowerUpType.BURST_SHOT)

    def test_laser_beam_expires(self):
        """Test LASER_BEAM expires after duration."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(100, 100), PowerUpType.LASER_BEAM)

        manager.activate(powerup)
        assert manager.is_active(PowerUpType.LASER_BEAM)

        # Update past duration
        manager.update(10.1)

        assert not manager.is_active(PowerUpType.LASER_BEAM)

    @given(st.floats(min_value=0.1, max_value=9.9))
    def test_property_10_powerup_activation(self, time_elapsed):
        """
        Property 10: Power-up activation

        Given: A power-up is activated
        When: Time elapses less than duration
        Then: Power-up remains active

        Validates: Requirements 4.4
        """
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(100, 100), PowerUpType.LASER_BEAM)

        manager.activate(powerup)
        manager.update(time_elapsed)

        # Should still be active
        assert manager.is_active(PowerUpType.LASER_BEAM)
        assert manager.get_remaining_time(PowerUpType.LASER_BEAM) == pytest.approx(
            10.0 - time_elapsed, abs=0.1
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
