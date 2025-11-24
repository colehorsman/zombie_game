"""Tests for collision detection system."""

import pytest
from src.models import Vector2
from src.collision import SpatialGrid, check_collisions_with_spatial_grid
from src.zombie import Zombie
from src.projectile import Projectile


class TestSpatialGrid:
    """Test spatial grid for collision optimization."""

    def test_spatial_grid_initialization(self):
        """Test that spatial grid initializes with correct dimensions."""
        grid = SpatialGrid(800, 600, cell_size=100)
        assert grid.width == 800
        assert grid.height == 600
        assert grid.cell_size == 100

    def test_insert_entity(self):
        """Test inserting entity into spatial grid."""
        grid = SpatialGrid(800, 600)
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-zombie",
            position=Vector2(100, 100),
            account="123456789012"
        )
        grid.insert(zombie)
        # Entity should be retrievable from grid
        assert len(grid.cells) > 0


class TestProjectileCollision:
    """Test projectile collision detection."""

    def test_projectile_hits_zombie_at_same_position(self):
        """Test that projectile at same position as zombie collides."""
        projectile = Projectile(
            position=Vector2(100, 100),
            velocity=Vector2(200, 0),
            damage=1
        )
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-zombie",
            position=Vector2(100, 100),
            account="123456789012"
        )
        
        # Check bounds overlap
        proj_bounds = projectile.get_bounds()
        zombie_bounds = zombie.get_bounds()
        assert proj_bounds.colliderect(zombie_bounds)

    def test_projectile_misses_distant_zombie(self):
        """Test that projectile far from zombie does not collide."""
        projectile = Projectile(
            position=Vector2(100, 100),
            velocity=Vector2(200, 0),
            damage=1
        )
        zombie = Zombie(
            identity_id="test-123",
            identity_name="test-zombie",
            position=Vector2(500, 500),
            account="123456789012"
        )
        
        # Check bounds don't overlap
        proj_bounds = projectile.get_bounds()
        zombie_bounds = zombie.get_bounds()
        assert not proj_bounds.colliderect(zombie_bounds)
