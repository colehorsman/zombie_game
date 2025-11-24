"""JIT Access Quest - Internal Audit Challenge

This module implements the JIT (Just-In-Time) Access Quest where players must
apply JIT protection to admin/privileged permission sets to prevent audit deficiencies.
"""

import logging
import random
from typing import Tuple

import pygame

from models import Vector2, PermissionSet


logger = logging.getLogger(__name__)


class Auditor:
    """Auditor character that patrols the level looking for unprotected admin access."""

    def __init__(self, x: float, y: float, patrol_width: float = 400):
        """
        Initialize the Auditor.

        Args:
            x: Starting x position
            y: Starting y position
            patrol_width: Width of patrol area
        """
        self.position = Vector2(x, y)
        self.velocity = Vector2(50, 0)  # Patrol speed (pixels/second)
        self.patrol_start = x
        self.patrol_end = x + patrol_width
        self.width = 40
        self.height = 60
        self.facing_right = True

    def update(self, dt: float):
        """
        Update auditor position (patrol back and forth).

        Args:
            dt: Delta time in seconds
        """
        # Move auditor
        self.position.x += self.velocity.x * dt

        # Reverse direction at patrol boundaries
        if self.position.x >= self.patrol_end:
            self.position.x = self.patrol_end
            self.velocity.x = -abs(self.velocity.x)
            self.facing_right = False
        elif self.position.x <= self.patrol_start:
            self.position.x = self.patrol_start
            self.velocity.x = abs(self.velocity.x)
            self.facing_right = True

    def get_bounds(self) -> pygame.Rect:
        """Get collision bounds for the auditor."""
        return pygame.Rect(
            int(self.position.x - self.width // 2),
            int(self.position.y - self.height // 2),
            self.width,
            self.height
        )


class AdminRole:
    """Admin role character representing a privileged permission set."""

    def __init__(self, permission_set: PermissionSet, x: float, y: float):
        """
        Initialize an AdminRole character.

        Args:
            permission_set: PermissionSet data object
            x: X position in game world
            y: Y position in game world
        """
        self.permission_set = permission_set
        self.position = Vector2(x, y)
        self.width = 40
        self.height = 50
        self.has_jit = permission_set.has_jit
        self.interacting = False  # Whether player is currently interacting

    def update(self, dt: float):
        """
        Update admin role state.

        Args:
            dt: Delta time in seconds
        """
        # Admin roles are stationary, but we can add idle animations later
        pass

    def get_bounds(self) -> pygame.Rect:
        """Get collision bounds for the admin role."""
        return pygame.Rect(
            int(self.position.x - self.width // 2),
            int(self.position.y - self.height // 2),
            self.width,
            self.height
        )

    def apply_jit_protection(self):
        """Mark this admin role as JIT protected."""
        self.has_jit = True
        self.permission_set.has_jit = True
        logger.info(f"Applied JIT protection to {self.permission_set.name}")


def create_jit_quest_entities(permission_sets: list, level_width: int, ground_y: int) -> Tuple[Auditor, list]:
    """
    Create auditor and admin role entities for the JIT quest.

    Args:
        permission_sets: List of PermissionSet objects (admin/privileged roles)
        level_width: Width of the level
        ground_y: Y position of the ground

    Returns:
        Tuple of (Auditor, list of AdminRole entities)
    """
    # Create auditor in the middle of the level
    auditor_x = level_width // 2
    auditor_y = ground_y - 30  # Slightly above ground
    auditor = Auditor(auditor_x, auditor_y, patrol_width=600)

    # Create admin role entities spread across the level at ground level
    admin_roles = []
    spacing = level_width // (len(permission_sets) + 1)
    
    # Admin role height is 50 pixels (defined in AdminRole class)
    admin_role_height = 50

    for i, perm_set in enumerate(permission_sets):
        x = spacing * (i + 1)
        # Position is the CENTER of the character, so to place bottom at ground:
        # y = ground_y - (height / 2)
        # Adjust up by 16 pixels (one tile) to match zombie positioning exactly
        y = ground_y - (admin_role_height // 2) - 16
        admin_role = AdminRole(perm_set, x, y)
        admin_roles.append(admin_role)
        logger.info(f"Created AdminRole for {perm_set.name} at ({x}, {y}), hasJit={perm_set.has_jit}")

    return auditor, admin_roles
