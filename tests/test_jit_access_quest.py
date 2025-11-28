"""Tests for JIT Access Quest entities and logic."""

import pytest
from unittest.mock import Mock, patch
import pygame

# Add src to path
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from jit_access_quest import Auditor, AdminRole, create_jit_quest_entities
from models import PermissionSet, Vector2


@pytest.fixture
def sample_permission_set():
    """Create a sample permission set for testing."""
    return PermissionSet(
        id="ps-admin-123",
        name="AdministratorAccess",
        identity_labels=["ADMIN"],
        user_count=5,
        has_jit=False,
    )


@pytest.fixture
def protected_permission_set():
    """Create a permission set with JIT already enabled."""
    return PermissionSet(
        id="ps-priv-456",
        name="PowerUserAccess",
        identity_labels=["PRIVILEGED"],
        user_count=10,
        has_jit=True,
    )


class TestAuditor:
    """Tests for Auditor entity."""

    def test_auditor_initialization(self):
        """Test auditor is initialized with correct properties."""
        auditor = Auditor(x=100, y=200, patrol_width=400)

        assert auditor.position.x == 100
        assert auditor.position.y == 200
        assert auditor.patrol_start == 100
        assert auditor.patrol_end == 500  # 100 + 400
        assert auditor.width == 40
        assert auditor.height == 60
        assert auditor.facing_right is True
        assert auditor.velocity.x == 50

    def test_auditor_patrol_right(self):
        """Test auditor moves right during patrol."""
        auditor = Auditor(x=100, y=200, patrol_width=400)
        initial_x = auditor.position.x

        auditor.update(dt=1.0)  # 1 second

        assert auditor.position.x == initial_x + 50  # Moved 50 pixels right
        assert auditor.facing_right is True

    def test_auditor_patrol_reverses_at_end(self):
        """Test auditor reverses direction at patrol boundary."""
        auditor = Auditor(x=100, y=200, patrol_width=400)

        # Move to end of patrol
        auditor.position.x = 500
        auditor.update(dt=1.0)

        assert auditor.position.x == 500  # Clamped at boundary
        assert auditor.velocity.x < 0  # Now moving left
        assert auditor.facing_right is False

    def test_auditor_patrol_reverses_at_start(self):
        """Test auditor reverses direction at patrol start."""
        auditor = Auditor(x=100, y=200, patrol_width=400)
        auditor.velocity.x = -50  # Moving left
        auditor.facing_right = False

        # Move to start of patrol
        auditor.position.x = 100
        auditor.update(dt=1.0)

        assert auditor.position.x == 100  # Clamped at boundary
        assert auditor.velocity.x > 0  # Now moving right
        assert auditor.facing_right is True

    def test_auditor_get_bounds(self):
        """Test auditor collision bounds are correct."""
        auditor = Auditor(x=100, y=200, patrol_width=400)
        bounds = auditor.get_bounds()

        assert isinstance(bounds, pygame.Rect)
        assert bounds.x == 100 - 20  # x - width/2
        assert bounds.y == 200 - 30  # y - height/2
        assert bounds.width == 40
        assert bounds.height == 60


class TestAdminRole:
    """Tests for AdminRole entity."""

    def test_admin_role_initialization(self, sample_permission_set):
        """Test admin role is initialized with correct properties."""
        admin_role = AdminRole(sample_permission_set, x=300, y=400)

        assert admin_role.permission_set == sample_permission_set
        assert admin_role.position.x == 300
        assert admin_role.position.y == 400
        assert admin_role.width == 40
        assert admin_role.height == 50
        assert admin_role.has_jit is False
        assert admin_role.interacting is False

    def test_admin_role_with_jit_protection(self, protected_permission_set):
        """Test admin role with JIT already enabled."""
        admin_role = AdminRole(protected_permission_set, x=300, y=400)

        assert admin_role.has_jit is True
        assert admin_role.permission_set.has_jit is True

    def test_admin_role_update(self, sample_permission_set):
        """Test admin role update (currently stationary)."""
        admin_role = AdminRole(sample_permission_set, x=300, y=400)
        initial_x = admin_role.position.x
        initial_y = admin_role.position.y

        admin_role.update(dt=1.0)

        # Admin roles are stationary
        assert admin_role.position.x == initial_x
        assert admin_role.position.y == initial_y

    def test_admin_role_get_bounds(self, sample_permission_set):
        """Test admin role collision bounds are correct."""
        admin_role = AdminRole(sample_permission_set, x=300, y=400)
        bounds = admin_role.get_bounds()

        assert isinstance(bounds, pygame.Rect)
        assert bounds.x == 300 - 20  # x - width/2
        assert bounds.y == 400 - 25  # y - height/2
        assert bounds.width == 40
        assert bounds.height == 50

    def test_apply_jit_protection(self, sample_permission_set):
        """Test applying JIT protection to admin role."""
        admin_role = AdminRole(sample_permission_set, x=300, y=400)

        assert admin_role.has_jit is False
        assert admin_role.permission_set.has_jit is False

        admin_role.apply_jit_protection()

        assert admin_role.has_jit is True
        assert admin_role.permission_set.has_jit is True


class TestCreateJitQuestEntities:
    """Tests for create_jit_quest_entities function."""

    def test_create_entities_single_permission_set(self, sample_permission_set):
        """Test creating quest entities with one permission set."""
        permission_sets = [sample_permission_set]
        level_width = 1000
        ground_y = 500

        auditor, admin_roles = create_jit_quest_entities(
            permission_sets, level_width, ground_y
        )

        # Check auditor
        assert isinstance(auditor, Auditor)
        assert auditor.position.x == level_width // 2  # Middle of level
        assert auditor.position.y == ground_y - 30

        # Check admin roles
        assert len(admin_roles) == 1
        assert isinstance(admin_roles[0], AdminRole)
        assert admin_roles[0].permission_set == sample_permission_set

    def test_create_entities_multiple_permission_sets(
        self, sample_permission_set, protected_permission_set
    ):
        """Test creating quest entities with multiple permission sets."""
        permission_sets = [sample_permission_set, protected_permission_set]
        level_width = 1000
        ground_y = 500

        auditor, admin_roles = create_jit_quest_entities(
            permission_sets, level_width, ground_y
        )

        # Check auditor
        assert isinstance(auditor, Auditor)

        # Check admin roles
        assert len(admin_roles) == 2
        assert all(isinstance(role, AdminRole) for role in admin_roles)

        # Check spacing (should be evenly distributed)
        spacing = level_width // (len(permission_sets) + 1)
        assert admin_roles[0].position.x == spacing * 1
        assert admin_roles[1].position.x == spacing * 2

    def test_create_entities_admin_roles_on_ground(self, sample_permission_set):
        """Test admin roles are positioned on the ground."""
        permission_sets = [sample_permission_set]
        level_width = 1000
        ground_y = 500

        auditor, admin_roles = create_jit_quest_entities(
            permission_sets, level_width, ground_y
        )

        # Admin roles should be on ground (positioned at ground_y - 16)
        assert admin_roles[0].position.y == ground_y - 16

    def test_create_entities_preserves_jit_status(
        self, sample_permission_set, protected_permission_set
    ):
        """Test that JIT protection status is preserved from permission sets."""
        permission_sets = [sample_permission_set, protected_permission_set]
        level_width = 1000
        ground_y = 500

        auditor, admin_roles = create_jit_quest_entities(
            permission_sets, level_width, ground_y
        )

        # First role should not have JIT
        assert admin_roles[0].has_jit is False

        # Second role should have JIT
        assert admin_roles[1].has_jit is True

    def test_create_entities_empty_permission_sets(self):
        """Test creating entities with no permission sets."""
        permission_sets = []
        level_width = 1000
        ground_y = 500

        auditor, admin_roles = create_jit_quest_entities(
            permission_sets, level_width, ground_y
        )

        # Auditor should still be created
        assert isinstance(auditor, Auditor)

        # No admin roles
        assert len(admin_roles) == 0


class TestJitQuestIntegration:
    """Integration tests for JIT quest workflow."""

    def test_quest_workflow_protect_all_roles(
        self, sample_permission_set, protected_permission_set
    ):
        """Test complete workflow: create entities, protect unprotected roles."""
        # Setup
        unprotected_ps = PermissionSet(
            id="ps-admin-789",
            name="SecurityAudit",
            identity_labels=["ADMIN"],
            user_count=3,
            has_jit=False,
        )
        permission_sets = [
            sample_permission_set,
            protected_permission_set,
            unprotected_ps,
        ]

        auditor, admin_roles = create_jit_quest_entities(permission_sets, 1000, 500)

        # Count unprotected roles
        unprotected_count = sum(1 for role in admin_roles if not role.has_jit)
        assert unprotected_count == 2  # sample_permission_set and unprotected_ps

        # Protect all unprotected roles
        for role in admin_roles:
            if not role.has_jit:
                role.apply_jit_protection()

        # Verify all roles are now protected
        assert all(role.has_jit for role in admin_roles)
        assert all(role.permission_set.has_jit for role in admin_roles)

    def test_auditor_patrol_during_quest(self):
        """Test auditor continues patrolling during quest."""
        auditor = Auditor(x=500, y=400, patrol_width=600)

        # Simulate 10 seconds of patrol
        for _ in range(10):
            auditor.update(dt=1.0)

        # Auditor should have moved but stayed within patrol bounds
        assert auditor.patrol_start <= auditor.position.x <= auditor.patrol_end
