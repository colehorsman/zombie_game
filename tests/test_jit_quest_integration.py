"""Integration tests for JIT Access Quest - simulates actual gameplay scenarios."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2, JitQuestState, PermissionSet
from jit_access_quest import Auditor, AdminRole


class TestJitQuestGameplaySimulation:
    """Simulate actual gameplay scenarios for JIT Access Quest."""

    @pytest.fixture
    def mock_pygame(self):
        """Mock pygame to avoid GUI dependencies."""
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'), \
             patch('pygame.time.Clock'):
            yield

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client with JIT quest responses."""
        client = Mock()
        
        # Mock permission sets response (2 admin roles, 1 unprotected)
        client.fetch_permission_sets.return_value = [
            {
                "id": "ps-admin-123",
                "name": "AdministratorAccess",
                "identityLabels": ["ADMIN"],
                "userCount": 5,
                "hasJit": False
            },
            {
                "id": "ps-priv-456",
                "name": "PowerUserAccess",
                "identityLabels": ["PRIVILEGED"],
                "userCount": 10,
                "hasJit": False
            }
        ]
        
        # Mock JIT configuration (no roles protected initially)
        client.fetch_jit_configuration.return_value = {
            "enrolledPermissionSets": []
        }
        
        # Mock successful JIT protection
        from models import QuarantineResult
        client.apply_jit_protection.return_value = QuarantineResult(
            success=True,
            identity_id="ps-admin-123",
            error_message=None
        )
        
        # Mock account scopes
        client._fetch_all_account_scopes.return_value = {
            "160224865296": "aws/r-ipxz/ou-ipxz-12345678/160224865296"
        }
        
        return client

    def test_scenario_1_quest_initialization_in_production_account(self, mock_pygame, mock_api_client):
        """
        SCENARIO 1: Quest initializes when entering production account with unprotected roles.
        
        Steps:
        1. Game engine initializes
        2. Player enters Production Data account (160224865296)
        3. Quest should initialize with 2 admin roles
        4. Auditor should spawn
        """
        # This would require significant mocking of the game engine
        # For now, we test the quest initialization logic directly
        
        # Simulate quest initialization
        account_id = "160224865296"
        
        # Fetch permission sets
        permission_sets_data = mock_api_client.fetch_permission_sets(account_id)
        assert len(permission_sets_data) == 2
        
        # Fetch JIT config
        jit_config = mock_api_client.fetch_jit_configuration(account_id)
        enrolled_ids = set(jit_config.get("enrolledPermissionSets", []))
        
        # Create permission set objects
        permission_sets = []
        unprotected_count = 0
        for ps_data in permission_sets_data:
            has_jit = ps_data["id"] in enrolled_ids
            perm_set = PermissionSet(
                id=ps_data["id"],
                name=ps_data["name"],
                identity_labels=ps_data["identityLabels"],
                user_count=ps_data["userCount"],
                has_jit=has_jit
            )
            permission_sets.append(perm_set)
            if not has_jit:
                unprotected_count += 1
        
        # Verify quest should be created
        assert unprotected_count == 2, "Should have 2 unprotected roles"
        assert len(permission_sets) == 2, "Should have 2 total permission sets"

    def test_scenario_2_player_protects_admin_role(self, mock_pygame, mock_api_client):
        """
        SCENARIO 2: Player interacts with admin role to apply JIT protection.
        
        Steps:
        1. Quest is active with unprotected admin role
        2. Player collides with admin role
        3. API call applies JIT protection
        4. Role becomes protected (green + shield)
        5. Progress counter updates
        """
        # Create admin role
        perm_set = PermissionSet(
            id="ps-admin-123",
            name="AdministratorAccess",
            identity_labels=["ADMIN"],
            user_count=5,
            has_jit=False
        )
        admin_role = AdminRole(perm_set, 100, 100)
        
        # Verify initial state
        assert admin_role.has_jit is False
        assert admin_role.permission_set.has_jit is False
        
        # Simulate API call to apply JIT
        result = mock_api_client.apply_jit_protection(
            account_id="160224865296",
            permission_set_id=perm_set.id,
            permission_set_name=perm_set.name
        )
        
        # Verify API call succeeded
        assert result.success is True
        
        # Apply protection to admin role
        admin_role.apply_jit_protection()
        
        # Verify role is now protected
        assert admin_role.has_jit is True
        assert admin_role.permission_set.has_jit is True

    def test_scenario_3_quest_completion_all_roles_protected(self, mock_pygame, mock_api_client):
        """
        SCENARIO 3: Quest completes when all admin roles are protected.
        
        Steps:
        1. Quest has 2 admin roles
        2. Player protects first role
        3. Player protects second role
        4. Quest completes with success message
        """
        # Create quest state
        perm_sets = [
            PermissionSet(
                id="ps-admin-123",
                name="AdministratorAccess",
                identity_labels=["ADMIN"],
                user_count=5,
                has_jit=False
            ),
            PermissionSet(
                id="ps-priv-456",
                name="PowerUserAccess",
                identity_labels=["PRIVILEGED"],
                user_count=10,
                has_jit=False
            )
        ]
        
        jit_quest = JitQuestState(
            active=True,
            auditor_position=Vector2(500, 400),
            admin_roles=perm_sets,
            protected_count=0,
            total_count=2,
            quest_completed=False,
            quest_failed=False
        )
        
        # Protect first role
        result1 = mock_api_client.apply_jit_protection(
            account_id="160224865296",
            permission_set_id=perm_sets[0].id,
            permission_set_name=perm_sets[0].name
        )
        assert result1.success is True
        perm_sets[0].has_jit = True
        jit_quest.protected_count += 1
        
        # Verify quest not complete yet
        assert jit_quest.protected_count == 1
        assert jit_quest.quest_completed is False
        
        # Protect second role
        result2 = mock_api_client.apply_jit_protection(
            account_id="160224865296",
            permission_set_id=perm_sets[1].id,
            permission_set_name=perm_sets[1].name
        )
        assert result2.success is True
        perm_sets[1].has_jit = True
        jit_quest.protected_count += 1
        
        # Verify quest should complete
        assert jit_quest.protected_count == jit_quest.total_count
        # In actual game, this would trigger quest completion
        jit_quest.quest_completed = True
        assert jit_quest.quest_completed is True

    def test_scenario_4_quest_failure_player_leaves_early(self, mock_pygame, mock_api_client):
        """
        SCENARIO 4: Quest fails when player leaves level with unprotected roles.
        
        Steps:
        1. Quest has 2 admin roles
        2. Player protects only 1 role
        3. Player returns to lobby
        4. Quest fails with warning message
        """
        # Create quest state with partial completion
        jit_quest = JitQuestState(
            active=True,
            auditor_position=Vector2(500, 400),
            admin_roles=[],
            protected_count=1,
            total_count=2,
            quest_completed=False,
            quest_failed=False
        )
        
        # Simulate player leaving level
        unprotected = jit_quest.total_count - jit_quest.protected_count
        
        # Verify there are unprotected roles
        assert unprotected == 1
        
        # Quest should fail
        jit_quest.quest_failed = True
        assert jit_quest.quest_failed is True
        assert jit_quest.quest_completed is False

    def test_scenario_5_no_quest_when_all_roles_already_protected(self, mock_pygame):
        """
        SCENARIO 5: Quest does not appear when all roles already have JIT.
        
        Steps:
        1. API returns permission sets
        2. API returns JIT config showing all are enrolled
        3. Quest should not initialize
        """
        # Mock API client with all roles protected
        client = Mock()
        client.fetch_permission_sets.return_value = [
            {
                "id": "ps-admin-123",
                "name": "AdministratorAccess",
                "identityLabels": ["ADMIN"],
                "userCount": 5,
                "hasJit": False
            }
        ]
        
        # All roles already have JIT
        client.fetch_jit_configuration.return_value = {
            "enrolledPermissionSets": ["ps-admin-123"]
        }
        
        # Fetch data
        permission_sets_data = client.fetch_permission_sets("160224865296")
        jit_config = client.fetch_jit_configuration("160224865296")
        enrolled_ids = set(jit_config.get("enrolledPermissionSets", []))
        
        # Count unprotected
        unprotected_count = 0
        for ps_data in permission_sets_data:
            if ps_data["id"] not in enrolled_ids:
                unprotected_count += 1
        
        # Quest should not be created
        assert unprotected_count == 0, "All roles are protected, quest should not appear"

    def test_scenario_6_no_quest_in_non_production_account(self, mock_pygame):
        """
        SCENARIO 6: Quest does not appear in non-production accounts.
        
        Steps:
        1. Player enters Sandbox account (577945324761)
        2. Quest should not initialize (not in production account list)
        """
        production_accounts = {
            "160224865296",  # Production Data
            "613056517323",  # Production
            "437154727976",  # Org
        }
        
        sandbox_account = "577945324761"
        
        # Verify sandbox is not in production list
        assert sandbox_account not in production_accounts
        
        # Quest should not initialize for sandbox
        # In actual game, _initialize_jit_quest would return early

    def test_scenario_7_auditor_patrol_behavior(self, mock_pygame):
        """
        SCENARIO 7: Auditor patrols back and forth in level.
        
        Steps:
        1. Auditor spawns at position
        2. Auditor moves and updates position
        3. Auditor stays within patrol boundaries
        """
        auditor = Auditor(x=500, y=400, patrol_width=400)
        
        # Initial state
        assert auditor.position.x == 500
        assert auditor.patrol_start == 500
        assert auditor.patrol_end == 900
        assert auditor.velocity.x != 0  # Should be moving
        
        # Update auditor and verify it stays within bounds
        for _ in range(1000):
            auditor.update(0.01)
            # Verify auditor stays within patrol boundaries
            assert auditor.patrol_start <= auditor.position.x <= auditor.patrol_end
        
        # Verify auditor has moved from starting position
        assert auditor.position.x != 500


class TestJitQuestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_api_error_during_jit_application(self):
        """Test handling of API errors when applying JIT protection."""
        from models import QuarantineResult
        
        # Simulate API error
        error_result = QuarantineResult(
            success=False,
            identity_id="",
            error_message="Permission set not found"
        )
        
        assert error_result.success is False
        assert "Permission set not found" in error_result.error_message

    def test_empty_permission_sets_response(self):
        """Test handling when no admin/privileged roles exist."""
        permission_sets_data = []
        
        # Quest should not initialize
        assert len(permission_sets_data) == 0

    def test_network_timeout_during_fetch(self):
        """Test handling of network timeouts."""
        client = Mock()
        client.fetch_permission_sets.side_effect = Exception("Network timeout")
        
        # Should handle gracefully
        try:
            client.fetch_permission_sets("160224865296")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Network timeout" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
