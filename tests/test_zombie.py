"""Tests for zombie entity behavior."""

import pytest
from src.models import Vector2
from src.zombie import Zombie


class TestZombieInitialization:
    """Test zombie creation and initialization."""

    def test_zombie_creates_with_required_fields(self):
        """Test zombie initializes with all required fields."""
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-user-1",
            position=Vector2(100, 200),
            account="123456789012"
        )
        
        assert zombie.identity_id == "test-123"
        assert zombie.identity_name == "test-user-1"
        assert zombie.position.x == 100
        assert zombie.position.y == 200
        assert zombie.account == "123456789012"

    def test_zombie_has_default_health(self):
        """Test zombie starts with default health points."""
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-user-1",
            position=Vector2(0, 0),
            account="123456789012"
        )
        
        assert zombie.health > 0
        assert zombie.max_health > 0
        assert zombie.health == zombie.max_health


class TestZombieDamage:
    """Test zombie damage and health system."""

    def test_zombie_takes_damage(self):
        """Test zombie health decreases when taking damage."""
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-user-1",
            position=Vector2(0, 0),
            account="123456789012"
        )
        initial_health = zombie.health
        
        zombie.take_damage(1)
        
        assert zombie.health == initial_health - 1

    def test_zombie_dies_at_zero_health(self):
        """Test zombie is marked dead when health reaches zero."""
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-user-1",
            position=Vector2(0, 0),
            account="123456789012"
        )
        
        # Deal enough damage to kill zombie
        zombie.take_damage(zombie.health)
        
        assert zombie.health <= 0
        assert zombie.is_dead


class TestZombieMovement:
    """Test zombie movement behavior."""

    def test_zombie_updates_position(self):
        """Test zombie position updates based on velocity."""
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-user-1",
            position=Vector2(0, 0),
            account="123456789012"
        )
        zombie.velocity = Vector2(100, 0)  # 100 pixels/second right
        
        zombie.update(delta_time=1.0)  # 1 second
        
        assert zombie.position.x == 100
        assert zombie.position.y == 0
