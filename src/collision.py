"""Collision detection utilities."""

import pygame
from typing import List, Optional, Tuple

from projectile import Projectile
from zombie import Zombie


def check_collision(projectile: Projectile, zombie: Zombie) -> bool:
    """
    Check if a projectile collides with a zombie using bounding box collision.

    Args:
        projectile: The projectile to check
        zombie: The zombie to check

    Returns:
        True if collision detected, False otherwise
    """
    proj_bounds = projectile.get_bounds()
    zombie_bounds = zombie.get_bounds()

    return proj_bounds.colliderect(zombie_bounds)


def check_projectile_zombie_collisions(
    projectiles: List[Projectile],
    zombies: List[Zombie]
) -> List[Tuple[Projectile, Zombie]]:
    """
    Check for collisions between all projectiles and zombies.

    Args:
        projectiles: List of active projectiles
        zombies: List of active zombies

    Returns:
        List of (projectile, zombie) tuples that collided
    """
    collisions = []

    for projectile in projectiles:
        for zombie in zombies:
            # Skip zombies that are already being quarantined
            if zombie.is_quarantining:
                continue

            if check_collision(projectile, zombie):
                collisions.append((projectile, zombie))
                # Mark zombie as quarantining to prevent multiple hits
                zombie.mark_for_quarantine()
                break  # Each projectile can only hit one zombie

    return collisions


class SpatialGrid:
    """
    Spatial partitioning grid for efficient collision detection with many zombies.
    """

    def __init__(self, width: int, height: int, cell_size: int = 50):
        """
        Initialize the spatial grid.

        Args:
            width: Width of the game area
            height: Height of the game area
            cell_size: Size of each grid cell in pixels
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = (width + cell_size - 1) // cell_size
        self.rows = (height + cell_size - 1) // cell_size
        self.grid: List[List[List[Zombie]]] = [
            [[] for _ in range(self.cols)] for _ in range(self.rows)
        ]

    def clear(self) -> None:
        """Clear all zombies from the grid."""
        for row in self.grid:
            for cell in row:
                cell.clear()

    def add_zombie(self, zombie: Zombie) -> None:
        """
        Add a zombie to the appropriate grid cell(s).

        Args:
            zombie: The zombie to add
        """
        bounds = zombie.get_bounds()

        # Calculate which cells the zombie occupies
        min_col = max(0, int(bounds.left // self.cell_size))
        max_col = min(self.cols - 1, int(bounds.right // self.cell_size))
        min_row = max(0, int(bounds.top // self.cell_size))
        max_row = min(self.rows - 1, int(bounds.bottom // self.cell_size))

        # Add zombie to all cells it occupies
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                self.grid[row][col].append(zombie)

    def get_nearby_zombies(self, projectile: Projectile) -> List[Zombie]:
        """
        Get zombies near a projectile's position.

        Args:
            projectile: The projectile to check

        Returns:
            List of zombies in nearby cells
        """
        bounds = projectile.get_bounds()

        # Calculate which cells to check
        min_col = max(0, int(bounds.left // self.cell_size))
        max_col = min(self.cols - 1, int(bounds.right // self.cell_size))
        min_row = max(0, int(bounds.top // self.cell_size))
        max_row = min(self.rows - 1, int(bounds.bottom // self.cell_size))

        # Collect zombies from nearby cells
        nearby = []
        seen = set()  # Avoid duplicates

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                for zombie in self.grid[row][col]:
                    if id(zombie) not in seen:
                        nearby.append(zombie)
                        seen.add(id(zombie))

        return nearby


def check_collisions_with_spatial_grid(
    projectiles: List[Projectile],
    zombies: List[Zombie],
    grid: SpatialGrid
) -> List[Tuple[Projectile, Zombie]]:
    """
    Check for collisions using spatial partitioning for better performance.

    Args:
        projectiles: List of active projectiles
        zombies: List of active zombies
        grid: Spatial grid for partitioning

    Returns:
        List of (projectile, zombie) tuples that collided
    """
    # Rebuild grid with current zombie positions
    grid.clear()
    for zombie in zombies:
        if not zombie.is_quarantining:
            grid.add_zombie(zombie)

    collisions = []

    for projectile in projectiles:
        # Only check zombies in nearby cells
        nearby_zombies = grid.get_nearby_zombies(projectile)

        for zombie in nearby_zombies:
            if zombie.is_quarantining:
                continue

            if check_collision(projectile, zombie):
                collisions.append((projectile, zombie))
                zombie.mark_for_quarantine()
                break  # Each projectile can only hit one zombie

    return collisions
