"""Tests for projectile system."""

import pytest
from src.models import Vector2
from src.projectile import Projectile


class TestProjectileInitialization:
    """Test projectile creation."""

    def test_projectile_creates_with_position_and_velocity(self):
        """Test projectile initializes with position and velocity."""
        projectile = Projectile(
            position=Vector2(100, 200),
            velocity=Vector2(300, 0),
            damage=1
        )
        
        assert projectile.position.x == 100
        assert projectile.position.y == 200
        assert projectile.velocity.x == 300
        assert projectile.velocity.y == 0
        assert projectile.damage == 1


class TestProjectileMovement:
    """Test projectile physics and movement."""

    def test_projectile_moves_based_on_velocity(self):
        """Test projectile position updates based on velocity and time."""
        projectile = Projectile(
            position=Vector2(0, 100),
            velocity=Vector2(200, 0),  # 200 pixels/second right
            damage=1
        )
        
        projectile.update(delta_time=1.0)  # 1 second
        
        assert projectile.position.x == 200
        assert projectile.position.y == 100

    def test_projectile_moves_diagonally(self):
        """Test projectile can move in diagonal direction."""
        projectile = Projectile(
            position=Vector2(0, 0),
            velocity=Vector2(100, 100),  # Diagonal movement
            damage=1
        )
        
        projectile.update(delta_time=1.0)
        
        assert projectile.position.x == 100
        assert projectile.position.y == 100

    def test_projectile_moves_incrementally(self):
        """Test projectile moves correctly with small time steps."""
        projectile = Projectile(
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),
            damage=1
        )
        
        # Move in small increments
        projectile.update(delta_time=0.1)  # 0.1 seconds
        assert projectile.position.x == 10
        
        projectile.update(delta_time=0.1)
        assert projectile.position.x == 20
