"""Tests for AWS-themed power-up system."""

import pytest
from unittest.mock import Mock, patch
import pygame

from powerup import PowerUp, PowerUpType, PowerUpManager, spawn_random_powerups
from models import Vector2


@pytest.fixture
def mock_pygame():
    """Mock pygame to avoid GUI dependencies."""
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for sprite creation


class TestPowerUpType:
    """Tests for PowerUpType enum."""

    def test_powerup_types_exist(self):
        """Test that all power-up types are defined."""
        assert PowerUpType.STAR_POWER.value == "Star Power"
        assert PowerUpType.LAMBDA_SPEED.value == "Lambda Speedup"
        assert PowerUpType.LASER_BEAM.value == "Laser Beam"
        assert PowerUpType.BURST_SHOT.value == "Burst Shot"

    def test_powerup_types_are_unique(self):
        """Test that all power-up type values are unique."""
        types = [pt.value for pt in PowerUpType]
        assert len(types) == len(set(types))


class TestPowerUpInitialization:
    """Tests for PowerUp initialization."""

    def test_powerup_creates_with_position_and_type(self, mock_pygame):
        """Test power-up is created with correct position and type."""
        position = Vector2(100, 200)
        powerup = PowerUp(position, PowerUpType.STAR_POWER)

        assert powerup.position == position
        assert powerup.powerup_type == PowerUpType.STAR_POWER
        assert powerup.width == 32
        assert powerup.height == 32
        assert powerup.collected is False

    def test_star_power_has_correct_duration(self, mock_pygame):
        """Test Star Power has 10 second duration."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        assert powerup.duration == 10.0

    def test_lambda_speed_has_correct_duration(self, mock_pygame):
        """Test Lambda Speed has 12 second duration."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)
        assert powerup.duration == 12.0

    def test_laser_beam_has_correct_duration(self, mock_pygame):
        """Test Laser Beam has 10 second duration."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LASER_BEAM)
        assert powerup.duration == 10.0

    def test_burst_shot_has_zero_duration(self, mock_pygame):
        """Test Burst Shot is instant (0 duration)."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.BURST_SHOT)
        assert powerup.duration == 0.0

    def test_star_power_has_correct_effect_value(self, mock_pygame):
        """Test Star Power effect value."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        assert powerup.effect_value == 1.0

    def test_lambda_speed_has_correct_effect_value(self, mock_pygame):
        """Test Lambda Speed has 2x multiplier."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)
        assert powerup.effect_value == 2.0

    def test_burst_shot_has_correct_effect_value(self, mock_pygame):
        """Test Burst Shot has 3 charges."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.BURST_SHOT)
        assert powerup.effect_value == 3.0

    def test_powerup_creates_sprite(self, mock_pygame):
        """Test that power-up creates a sprite surface."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        assert powerup.sprite is not None
        assert isinstance(powerup.sprite, pygame.Surface)

    def test_powerup_initializes_bounce_animation(self, mock_pygame):
        """Test that power-up initializes bounce animation properties."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        assert powerup.bounce_offset == 0
        assert powerup.bounce_speed == 2.0


class TestPowerUpDescriptions:
    """Tests for power-up descriptions."""

    def test_star_power_description(self, mock_pygame):
        """Test Star Power description."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        desc = powerup.get_description()
        assert "10 seconds" in desc
        assert "untouchable" in desc
        assert "quarantined" in desc

    def test_lambda_speed_description(self, mock_pygame):
        """Test Lambda Speed description."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)
        desc = powerup.get_description()
        assert "2x faster" in desc
        assert "12 seconds" in desc
        assert "Lambda" in desc

    def test_laser_beam_description(self, mock_pygame):
        """Test that Laser Beam has a description."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LASER_BEAM)
        desc = powerup.get_description()
        assert "10 seconds" in desc
        assert "laser" in desc.lower()
        assert "no reload" in desc.lower()

    def test_burst_shot_description(self, mock_pygame):
        """Test that Burst Shot has a description."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.BURST_SHOT)
        desc = powerup.get_description()
        assert "3 one-shot" in desc
        assert "instant kills" in desc.lower()


class TestPowerUpUpdate:
    """Tests for power-up update logic."""

    def test_powerup_updates_bounce_offset(self, mock_pygame):
        """Test that power-up updates bounce animation."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        initial_offset = powerup.bounce_offset

        powerup.update(1.0)  # 1 second

        assert powerup.bounce_offset != initial_offset
        assert powerup.bounce_offset == 2.0  # bounce_speed * delta_time

    def test_powerup_bounce_wraps_at_2pi(self, mock_pygame):
        """Test that bounce offset wraps at 2*pi."""
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        powerup.bounce_offset = 6.0

        powerup.update(0.5)  # Will exceed 6.28 (2*pi)

        assert powerup.bounce_offset < 6.28


class TestPowerUpCollision:
    """Tests for power-up collision detection."""

    def test_get_bounds_returns_rect(self, mock_pygame):
        """Test that get_bounds returns a pygame Rect."""
        powerup = PowerUp(Vector2(100, 200), PowerUpType.STAR_POWER)
        bounds = powerup.get_bounds()

        assert isinstance(bounds, pygame.Rect)
        assert bounds.width == 32
        assert bounds.height == 32

    def test_get_bounds_includes_bounce_offset(self, mock_pygame):
        """Test that bounds include bounce animation offset."""
        powerup = PowerUp(Vector2(100, 200), PowerUpType.STAR_POWER)

        # Set bounce offset to known value
        powerup.bounce_offset = 1.57  # pi/2, sin = 1

        bounds = powerup.get_bounds()

        # Y position should be affected by bounce (sin(pi/2 * 2) * 5 = 0)
        assert bounds.x == 100
        # Y will vary based on bounce calculation


class TestPowerUpRendering:
    """Tests for power-up rendering."""

    def test_render_does_not_draw_when_collected(self, mock_pygame):
        """Test that collected power-ups are not rendered."""
        powerup = PowerUp(Vector2(100, 200), PowerUpType.STAR_POWER)
        powerup.collected = True

        screen = pygame.Surface((800, 600))

        # Should not raise exception and should return early
        powerup.render(screen, 0, 0)

    def test_render_draws_when_not_collected(self, mock_pygame):
        """Test that uncollected power-ups are rendered."""
        powerup = PowerUp(Vector2(100, 200), PowerUpType.STAR_POWER)
        powerup.collected = False

        screen = pygame.Surface((800, 600))

        # Should not raise exception
        powerup.render(screen, 0, 0)

    def test_render_applies_camera_offset(self, mock_pygame):
        """Test that rendering applies camera offset correctly."""
        powerup = PowerUp(Vector2(500, 400), PowerUpType.STAR_POWER)
        screen = pygame.Surface((800, 600))

        # Should not raise exception with camera offset
        powerup.render(screen, 200, 100)


class TestPowerUpManager:
    """Tests for PowerUpManager."""

    def test_manager_initializes_empty(self):
        """Test that manager starts with no active effects."""
        manager = PowerUpManager()
        assert len(manager.active_effects) == 0

    def test_activate_adds_timed_effect(self, mock_pygame):
        """Test that activating a timed power-up adds it to active effects."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)

        manager.activate(powerup)

        assert PowerUpType.STAR_POWER in manager.active_effects
        assert manager.active_effects[PowerUpType.STAR_POWER]["time_remaining"] == 10.0
        assert manager.active_effects[PowerUpType.STAR_POWER]["value"] == 1.0

    def test_activate_does_not_add_instant_effect(self, mock_pygame):
        """Test that instant power-ups are not added to active effects."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.BURST_SHOT)

        manager.activate(powerup)

        # Burst Shot has 0 duration, should not be in active effects
        assert PowerUpType.BURST_SHOT not in manager.active_effects

    def test_update_decrements_timers(self, mock_pygame):
        """Test that update decrements active effect timers."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        manager.activate(powerup)

        initial_time = manager.active_effects[PowerUpType.STAR_POWER]["time_remaining"]

        manager.update(1.0)  # 1 second

        assert (
            manager.active_effects[PowerUpType.STAR_POWER]["time_remaining"]
            == initial_time - 1.0
        )

    def test_update_removes_expired_effects(self, mock_pygame):
        """Test that expired effects are removed."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        manager.activate(powerup)

        # Update for longer than duration
        manager.update(11.0)

        assert PowerUpType.STAR_POWER not in manager.active_effects

    def test_is_active_returns_true_for_active_effect(self, mock_pygame):
        """Test that is_active returns True for active effects."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        manager.activate(powerup)

        assert manager.is_active(PowerUpType.STAR_POWER) is True

    def test_is_active_returns_false_for_inactive_effect(self, mock_pygame):
        """Test that is_active returns False for inactive effects."""
        manager = PowerUpManager()

        assert manager.is_active(PowerUpType.STAR_POWER) is False

    def test_get_effect_value_returns_value_for_active_effect(self, mock_pygame):
        """Test that get_effect_value returns correct value."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)
        manager.activate(powerup)

        assert manager.get_effect_value(PowerUpType.LAMBDA_SPEED) == 2.0

    def test_get_effect_value_returns_none_for_inactive_effect(self, mock_pygame):
        """Test that get_effect_value returns None for inactive effects."""
        manager = PowerUpManager()

        assert manager.get_effect_value(PowerUpType.STAR_POWER) is None

    def test_get_remaining_time_returns_time_for_active_effect(self, mock_pygame):
        """Test that get_remaining_time returns correct time."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        manager.activate(powerup)

        manager.update(3.0)  # 3 seconds elapsed

        assert manager.get_remaining_time(PowerUpType.STAR_POWER) == 7.0

    def test_get_remaining_time_returns_zero_for_inactive_effect(self, mock_pygame):
        """Test that get_remaining_time returns 0 for inactive effects."""
        manager = PowerUpManager()

        assert manager.get_remaining_time(PowerUpType.STAR_POWER) == 0.0

    def test_multiple_active_effects(self, mock_pygame):
        """Test that multiple power-ups can be active simultaneously."""
        manager = PowerUpManager()
        star = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        speed = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)

        manager.activate(star)
        manager.activate(speed)

        assert manager.is_active(PowerUpType.STAR_POWER) is True
        assert manager.is_active(PowerUpType.LAMBDA_SPEED) is True

    def test_reactivating_same_powerup_resets_timer(self, mock_pygame):
        """Test that reactivating a power-up resets its timer."""
        manager = PowerUpManager()
        powerup = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)

        manager.activate(powerup)
        manager.update(5.0)  # 5 seconds elapsed

        # Reactivate
        manager.activate(powerup)

        # Timer should be reset to full duration
        assert manager.get_remaining_time(PowerUpType.STAR_POWER) == 10.0


class TestSpawnRandomPowerups:
    """Tests for spawn_random_powerups function."""

    def test_spawn_creates_correct_count(self, mock_pygame):
        """Test that spawn creates the requested number of power-ups."""
        # Correct parameter order: level_width, ground_y, count
        powerups = spawn_random_powerups(1000, 600, count=5)

        assert len(powerups) == 5

    def test_spawn_creates_powerup_instances(self, mock_pygame):
        """Test that spawn creates PowerUp instances."""
        powerups = spawn_random_powerups(1000, 600, count=3)

        for powerup in powerups:
            assert isinstance(powerup, PowerUp)

    def test_spawn_distributes_across_map_width(self, mock_pygame):
        """Test that power-ups are distributed across map width."""
        powerups = spawn_random_powerups(1000, 600, count=10)

        # Check that power-ups are within map bounds (100 to level_width - 100)
        for powerup in powerups:
            assert 100 <= powerup.position.x <= 900

    def test_spawn_places_above_ground(self, mock_pygame):
        """Test that power-ups are spawned above ground level."""
        ground_y = 600
        powerups = spawn_random_powerups(1000, ground_y, count=5)

        for powerup in powerups:
            assert powerup.position.y == ground_y - 100

    def test_spawn_creates_random_types(self, mock_pygame):
        """Test that spawn creates random power-up types."""
        powerups = spawn_random_powerups(1000, 600, count=20)

        # With 20 power-ups and 4 types, we should have variety
        types = set(p.powerup_type for p in powerups)
        assert len(types) > 1  # Should have at least 2 different types

    def test_spawn_with_zero_count(self, mock_pygame):
        """Test that spawn with 0 count returns empty list."""
        powerups = spawn_random_powerups(1000, 600, count=0)

        assert len(powerups) == 0
        assert powerups == []

    def test_spawn_arcade_mode_favors_arcade_powerups(self, mock_pygame):
        """Test that arcade mode favors LASER_BEAM and BURST_SHOT."""
        powerups = spawn_random_powerups(1000, 600, count=20, arcade_mode=True)

        # In arcade mode, should only get LASER_BEAM, BURST_SHOT, or STAR_POWER
        arcade_types = {
            PowerUpType.LASER_BEAM,
            PowerUpType.BURST_SHOT,
            PowerUpType.STAR_POWER,
        }
        for powerup in powerups:
            assert powerup.powerup_type in arcade_types

    def test_spawn_normal_mode_includes_all_types(self, mock_pygame):
        """Test that normal mode can spawn all power-up types."""
        powerups = spawn_random_powerups(1000, 600, count=50, arcade_mode=False)

        # With 50 power-ups in normal mode, we should see variety
        types = set(p.powerup_type for p in powerups)
        # Should have at least 2 different types (likely more)
        assert len(types) >= 2


class TestPowerUpIntegration:
    """Integration tests for power-up workflow."""

    def test_complete_powerup_lifecycle(self, mock_pygame):
        """Test complete lifecycle: spawn → collect → activate → expire."""
        # Spawn
        powerup = PowerUp(Vector2(100, 200), PowerUpType.STAR_POWER)
        assert powerup.collected is False

        # Collect
        manager = PowerUpManager()
        manager.activate(powerup)
        powerup.collected = True

        # Verify active
        assert manager.is_active(PowerUpType.STAR_POWER) is True
        assert manager.get_remaining_time(PowerUpType.STAR_POWER) == 10.0

        # Update halfway
        manager.update(5.0)
        assert manager.is_active(PowerUpType.STAR_POWER) is True
        assert manager.get_remaining_time(PowerUpType.STAR_POWER) == 5.0

        # Expire
        manager.update(6.0)
        assert manager.is_active(PowerUpType.STAR_POWER) is False

    def test_multiple_powerups_lifecycle(self, mock_pygame):
        """Test multiple power-ups with different durations."""
        manager = PowerUpManager()

        # Activate Star Power (10s) and Lambda Speed (12s)
        star = PowerUp(Vector2(0, 0), PowerUpType.STAR_POWER)
        speed = PowerUp(Vector2(0, 0), PowerUpType.LAMBDA_SPEED)

        manager.activate(star)
        manager.activate(speed)

        # After 11 seconds, Star Power should expire but Lambda Speed active
        manager.update(11.0)

        assert manager.is_active(PowerUpType.STAR_POWER) is False
        assert manager.is_active(PowerUpType.LAMBDA_SPEED) is True
        assert manager.get_remaining_time(PowerUpType.LAMBDA_SPEED) == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
