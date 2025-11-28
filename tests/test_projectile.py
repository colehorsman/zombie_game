"""Tests for projectile system."""

import pytest
from models import Vector2
from projectile import Projectile


class TestProjectileInitialization:
    """Test projectile creation."""

    def test_projectile_creates_with_position_and_direction(self):
        """Test projectile initializes with position and direction."""
        projectile = Projectile(
            position=Vector2(100, 200),
            direction=Vector2(1, 0),  # Right direction
            damage=1,
        )

        assert projectile.position.x == 100
        assert projectile.position.y == 200
        assert projectile.velocity.x == 400  # Speed is 400 pixels/sec
        assert projectile.velocity.y == 0
        assert projectile.damage == 1


class TestProjectileMovement:
    """Test projectile physics and movement."""

    def test_projectile_moves_based_on_velocity(self):
        """Test projectile position updates based on velocity and time."""
        projectile = Projectile(
            position=Vector2(0, 100),
            direction=Vector2(1, 0),  # Right direction (normalized to speed 400)
            damage=1,
        )

        projectile.update(delta_time=1.0)  # 1 second

        assert projectile.position.x == 400  # Speed is 400 pixels/sec
        assert projectile.position.y == 100

    def test_projectile_moves_diagonally(self):
        """Test projectile can move in diagonal direction."""
        projectile = Projectile(
            position=Vector2(0, 0),
            direction=Vector2(1, 1),  # Diagonal (will be normalized)
            damage=1,
        )

        projectile.update(delta_time=1.0)

        # Diagonal at speed 400: each component is 400/sqrt(2) ≈ 283
        import math

        expected = 400 / math.sqrt(2)
        assert abs(projectile.position.x - expected) < 1
        assert abs(projectile.position.y - expected) < 1

    def test_projectile_moves_incrementally(self):
        """Test projectile moves correctly with small time steps."""
        projectile = Projectile(
            position=Vector2(0, 0),
            direction=Vector2(1, 0),  # Right at speed 400
            damage=1,
        )

        # Move in small increments
        projectile.update(delta_time=0.1)  # 0.1 seconds
        assert abs(projectile.position.x - 40) < 1  # 400 * 0.1 = 40

        projectile.update(delta_time=0.1)
        assert abs(projectile.position.x - 80) < 1  # 400 * 0.2 = 80
