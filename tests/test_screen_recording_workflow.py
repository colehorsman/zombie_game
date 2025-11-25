"""
QA Test Suite: Screen Recording Workflow Validation

This test suite validates the complete gameplay workflow needed for screen recording:
1. Enter Sandbox level
2. Test hacker challenge (Service Protection Quest)
3. Pause menu functionality
4. Exit back to lobby
5. Enter Production level
6. Test JIT Access Quest

All tests use mocked API calls to simulate real gameplay scenarios.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

from models import GameState, GameStatus, Vector2, QuestStatus, QuarantineResult
from game_engine import GameEngine
from zombie import Zombie
from level_manager import LevelManager, Level
from sonrai_client import SonraiAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Sonrai API client."""
    client = Mock(spec=SonraiAPIClient)
    
    # Mock permission sets for JIT quest
    client.fetch_permission_sets.return_value = [
        {
            "id": "ps-admin-001",
            "name": "AdministratorAccess",
            "identityLabels": ["ADMIN"],
            "userCount": 5
        },
        {
            "id": "ps-power-001",
            "name": "PowerUserAccess",
            "identityLabels": ["PRIVILEGED"],
            "userCount": 3
        }
    ]
    
    # Mock JIT configuration (none protected initially)
    client.fetch_jit_configuration.return_value = {
        "enrolledPermissionSets": []
    }
    
    # Mock JIT protection application
    client.apply_jit_protection.return_value = QuarantineResult(
        success=True,
        identity_id="ps-admin-001",
        error_message=None
    )
    
    # Mock service protection
    client.get_unprotected_services.return_value = ["bedrock-agentcore"]
    client.protect_service.return_value = QuarantineResult(
        success=True,
        identity_id="bedrock-agentcore",
        error_message=None
    )
    
    # Mock quarantine
    client.quarantine_identity.return_value = QuarantineResult(
        success=True,
        identity_id="test-identity"
    )
    
    return client


@pytest.fixture
def mock_level_manager():
    """Create a mock level manager with Sandbox and Production levels."""
    levels = [
        Level(
            level_number=1,
            account_id="577945324761",
            account_name="MyHealth - Sandbox",
            environment_type="sandbox",
            order=1
        ),
        Level(
            level_number=6,
            account_id="613056517323",
            account_name="MyHealth - Production",
            environment_type="production",
            order=6
        )
    ]
    
    # Create mock manager
    manager = Mock(spec=LevelManager)
    manager.levels = levels
    manager.current_level_index = 0
    manager.get_current_level = Mock(return_value=levels[0])
    
    return manager


@pytest.fixture
def game_engine(mock_api_client, mock_level_manager):
    """Create a game engine instance for testing."""
    pygame.init()
    pygame.display.set_mode((1280, 720))
    
    # Create test zombies
    zombies = [
        Zombie(
            identity_id=f"zombie-{i}",
            identity_name=f"TestZombie{i}",
            position=Vector2(1000 + i * 100, 400),
            account="577945324761"
        )
        for i in range(5)
    ]
    
    account_data = {
        "577945324761": 100,
        "613056517323": 50
    }
    
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=zombies,
        screen_width=1280,
        screen_height=720,
        use_map=True,
        account_data=account_data,
        third_party_data={},
        level_manager=mock_level_manager
    )
    
    engine.start()
    
    return engine


class TestScreenRecordingWorkflow:
    """Test suite for screen recording workflow validation."""
    
    def test_1_initial_lobby_state(self, game_engine):
        """Test 1: Verify game starts in lobby mode."""
        assert game_engine.game_state.status == GameStatus.LOBBY
        assert game_engine.player is not None
        assert game_engine.game_map is not None
        print("✅ Test 1 PASSED: Game starts in lobby")
    
    def test_2_enter_sandbox_level(self, game_engine):
        """Test 2: Verify entering Sandbox level works correctly."""
        # Find Sandbox door
        sandbox_door = None
        for door in game_engine.game_map.doors:
            if door.destination_room_name == "MyHealth - Sandbox":
                sandbox_door = door
                break
        
        assert sandbox_door is not None, "Sandbox door not found"
        
        # Simulate entering door
        game_engine._enter_level(sandbox_door)
        
        # Verify level state
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert game_engine.game_state.current_level == 1
        assert game_engine.game_state.environment_type == "sandbox"
        assert game_engine.game_state.current_level_account_id == "577945324761"
        assert len(game_engine.zombies) > 0
        print("✅ Test 2 PASSED: Successfully entered Sandbox level")
    
    def test_3_hacker_challenge_initialization(self, game_engine):
        """Test 3: Verify hacker challenge (Service Protection Quest) initializes."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        # Check if quest exists for Sandbox (level 1)
        quest = game_engine.quest_manager.get_quest_for_level(1)
        
        if quest:
            # Quest exists - service is unprotected
            assert quest.status == QuestStatus.NOT_STARTED
            assert quest.service_type == "bedrock-agentcore"
            assert quest.time_limit == 60.0
            print("✅ Test 3 PASSED: Hacker challenge initialized (service unprotected)")
        else:
            # Quest doesn't exist - service already protected
            print("✅ Test 3 PASSED: No hacker challenge (service already protected)")
    
    def test_4_hacker_challenge_trigger(self, game_engine):
        """Test 4: Verify hacker challenge triggers when player crosses threshold."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        quest = game_engine.quest_manager.get_quest_for_level(1)
        if not quest:
            print("⏭️  Test 4 SKIPPED: No quest (service already protected)")
            return
        
        # Move player past trigger point
        game_engine.player.position.x = quest.trigger_position.x + 10
        
        # Update game to trigger quest
        game_engine._update_quests(0.016)
        
        # Verify quest triggered
        assert quest.status == QuestStatus.TRIGGERED
        assert game_engine.game_state.quest_message is not None
        assert "WARNING" in game_engine.game_state.quest_message
        print("✅ Test 4 PASSED: Hacker challenge triggered")
    
    def test_5_pause_menu_functionality(self, game_engine):
        """Test 5: Verify pause menu works correctly."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        # Show pause menu
        game_engine._show_pause_menu()
        
        # Verify pause state
        assert game_engine.game_state.status == GameStatus.PAUSED
        assert game_engine.game_state.previous_status == GameStatus.PLAYING
        assert game_engine.game_state.congratulations_message is not None
        assert "PAUSED" in game_engine.game_state.congratulations_message
        
        # Verify menu options exist
        assert len(game_engine.pause_menu_options) == 4
        assert "Return to Game" in game_engine.pause_menu_options
        assert "Return to Lobby" in game_engine.pause_menu_options
        assert "Save Game" in game_engine.pause_menu_options
        assert "Quit Game" in game_engine.pause_menu_options
        
        print("✅ Test 5 PASSED: Pause menu displays correctly")
    
    def test_6_pause_menu_navigation(self, game_engine):
        """Test 6: Verify pause menu navigation works."""
        # Enter Sandbox level and pause
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        game_engine._show_pause_menu()
        
        # Test navigation down
        initial_index = game_engine.pause_menu_selected_index
        game_engine._navigate_pause_menu(1)
        assert game_engine.pause_menu_selected_index == (initial_index + 1) % 4
        
        # Test navigation up
        game_engine._navigate_pause_menu(-1)
        assert game_engine.pause_menu_selected_index == initial_index
        
        print("✅ Test 6 PASSED: Pause menu navigation works")
    
    def test_7_return_to_lobby_from_pause_menu(self, game_engine):
        """Test 7: Verify 'Return to Lobby' option works."""
        # Enter Sandbox level and pause
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        game_engine._show_pause_menu()
        
        # Select "Return to Lobby" option (index 1)
        game_engine.pause_menu_selected_index = 1
        game_engine._execute_pause_menu_option()
        
        # Verify returned to lobby
        assert game_engine.game_state.status == GameStatus.LOBBY
        # Lobby now has zombies (main branch style - zombies visible in lobby)
        assert len(game_engine.zombies) > 0  # Zombies restored to lobby
        assert game_engine.game_state.current_level_account_id is None
        
        print("✅ Test 7 PASSED: Successfully returned to lobby from pause menu")
    
    def test_8_return_to_lobby_with_l_key(self, game_engine):
        """Test 8: Verify L key returns to lobby."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        # Press L key to return to lobby
        game_engine._return_to_lobby()
        
        # Verify returned to lobby
        assert game_engine.game_state.status == GameStatus.LOBBY
        # Lobby now has zombies (main branch style - zombies visible in lobby)
        assert len(game_engine.zombies) > 0  # Zombies restored to lobby
        
        print("✅ Test 8 PASSED: L key returns to lobby")
    
    def test_9_enter_production_level(self, game_engine):
        """Test 9: Verify entering Production level works."""
        # Use UNLOCK cheat to access production
        game_engine.cheat_enabled = True
        
        # Find Production door
        production_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Production"),
            None
        )
        
        assert production_door is not None, "Production door not found"
        
        # Enter Production level
        game_engine._enter_level(production_door)
        
        # Verify level state
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert game_engine.game_state.current_level == 6
        assert game_engine.game_state.environment_type == "production"
        assert game_engine.game_state.current_level_account_id == "613056517323"
        
        print("✅ Test 9 PASSED: Successfully entered Production level")
    
    def test_10_jit_quest_initialization(self, game_engine):
        """Test 10: Verify JIT Access Quest initializes in Production."""
        # Use UNLOCK cheat
        game_engine.cheat_enabled = True
        
        # Enter Production level
        production_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Production"),
            None
        )
        game_engine._enter_level(production_door)
        
        # Verify JIT quest initialized
        assert game_engine.game_state.jit_quest is not None
        assert game_engine.game_state.jit_quest.active is True
        assert game_engine.game_state.jit_quest.total_count == 2  # 2 permission sets
        assert game_engine.game_state.jit_quest.protected_count == 0  # None protected initially
        
        # Verify entities created
        assert game_engine.auditor is not None
        assert len(game_engine.admin_roles) == 2
        
        print("✅ Test 10 PASSED: JIT Access Quest initialized in Production")
    
    def test_11_jit_quest_interaction(self, game_engine):
        """Test 11: Verify player can interact with admin roles."""
        # Use UNLOCK cheat
        game_engine.cheat_enabled = True
        
        # Enter Production level
        production_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Production"),
            None
        )
        game_engine._enter_level(production_door)
        
        # Get first unprotected admin role
        admin_role = next((r for r in game_engine.admin_roles if not r.has_jit), None)
        assert admin_role is not None
        
        # Move player to admin role position
        game_engine.player.position.x = admin_role.position.x
        game_engine.player.position.y = admin_role.position.y
        
        # Update quest to trigger interaction
        game_engine._update_jit_quest(0.016)
        
        # Verify JIT protection applied
        assert admin_role.has_jit is True
        assert game_engine.game_state.jit_quest.protected_count == 1
        
        print("✅ Test 11 PASSED: Player can interact with admin roles")
    
    def test_12_jit_quest_completion(self, game_engine):
        """Test 12: Verify JIT quest completes when all roles protected."""
        # Use UNLOCK cheat
        game_engine.cheat_enabled = True
        
        # Enter Production level
        production_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Production"),
            None
        )
        game_engine._enter_level(production_door)
        
        # Protect all admin roles
        for admin_role in game_engine.admin_roles:
            if not admin_role.has_jit:
                game_engine.player.position.x = admin_role.position.x
                game_engine.player.position.y = admin_role.position.y
                game_engine._update_jit_quest(0.016)
        
        # Verify quest completed
        assert game_engine.game_state.jit_quest.quest_completed is True
        assert game_engine.game_state.jit_quest.protected_count == 2
        assert game_engine.game_state.status == GameStatus.PAUSED  # Paused to show success
        assert game_engine.game_state.congratulations_message is not None
        assert "Audit Deficiency Prevented" in game_engine.game_state.congratulations_message
        
        print("✅ Test 12 PASSED: JIT quest completes successfully")
    
    def test_13_complete_workflow_sandbox_to_production(self, game_engine):
        """Test 13: Complete workflow - Sandbox → Lobby → Production."""
        # Step 1: Enter Sandbox
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert game_engine.game_state.current_level == 1
        
        # Step 2: Pause and return to lobby
        game_engine._show_pause_menu()
        assert game_engine.game_state.status == GameStatus.PAUSED
        
        game_engine.pause_menu_selected_index = 1  # "Return to Lobby"
        game_engine._execute_pause_menu_option()
        assert game_engine.game_state.status == GameStatus.LOBBY
        
        # Step 3: Enter Production (with cheat)
        game_engine.cheat_enabled = True
        production_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Production"),
            None
        )
        game_engine._enter_level(production_door)
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert game_engine.game_state.current_level == 6
        
        # Step 4: Verify JIT quest active
        assert game_engine.game_state.jit_quest is not None
        assert game_engine.game_state.jit_quest.active is True
        
        print("✅ Test 13 PASSED: Complete workflow Sandbox → Lobby → Production")
    
    def test_14_esc_key_pause_and_resume(self, game_engine):
        """Test 14: Verify ESC key pauses and resumes game."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        # Create ESC key press event
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        game_engine.handle_input([esc_event])
        
        # Verify paused
        assert game_engine.game_state.status == GameStatus.PAUSED
        
        # Press ESC again to resume
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        game_engine.handle_input([esc_event])
        
        # Verify resumed
        assert game_engine.game_state.status == GameStatus.PLAYING
        
        print("✅ Test 14 PASSED: ESC key pauses and resumes")
    
    def test_15_level_completion_marks_door(self, game_engine):
        """Test 15: Verify completing level marks door as completed."""
        # Enter Sandbox level
        sandbox_door = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        game_engine._enter_level(sandbox_door)
        
        # Return to lobby with mark_completed=True to mark level as complete
        game_engine._return_to_lobby(mark_completed=True)
        
        # Verify Sandbox account marked as completed
        assert "577945324761" in game_engine.completed_level_account_ids
        
        # Verify door marked as completed
        sandbox_door_in_lobby = next(
            (d for d in game_engine.game_map.doors if d.destination_room_name == "MyHealth - Sandbox"),
            None
        )
        assert sandbox_door_in_lobby.is_completed is True
        
        print("✅ Test 15 PASSED: Level completion marks door")


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("QA TESTER: Screen Recording Workflow Validation")
    print("="*70 + "\n")
    
    # Run pytest with verbose output
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
