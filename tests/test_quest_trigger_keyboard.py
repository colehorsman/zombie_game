"""Tests for keyboard-based quest triggering (ENTER/SPACE keys)."""

import pytest
from unittest.mock import Mock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2, QuestStatus
from service_protection_quest import ServiceProtectionQuestManager, create_bedrock_protection_quest
from hacker import Hacker


@pytest.fixture
def mock_pygame():
    """Mock pygame to avoid GUI dependencies."""
    with patch('pygame.init'), \
         patch('pygame.display.set_mode'), \
         patch('pygame.font.Font'), \
         patch('pygame.time.Clock'), \
         patch('pygame.joystick.init'), \
         patch('pygame.joystick.get_count', return_value=0):
        yield


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = Mock()
    client.fetch_accounts_with_unused_identities.return_value = {}
    client.fetch_third_parties_by_account.return_value = {}
    client.get_unprotected_services.return_value = ["bedrock-agentcore"]
    return client


@pytest.fixture
def game_engine_with_quest(mock_pygame, mock_api_client):
    """Create a game engine with a triggered quest."""
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=[],
        screen_width=1280,
        screen_height=720,
        use_map=False,
        account_data={},
        third_party_data={}
    )
    engine.start()
    
    # Create quest manager and quest
    engine.quest_manager = ServiceProtectionQuestManager()
    quest = create_bedrock_protection_quest(
        quest_id="test_quest",
        level=1,
        trigger_pos=Vector2(200, 400),
        service_pos=Vector2(5000, 400)
    )
    engine.quest_manager.add_quest(quest)
    
    # Set quest to TRIGGERED state (warning dialog showing)
    quest.status = QuestStatus.TRIGGERED
    engine.game_state.quest_message = "⚠️ WARNING! ⚠️\n\nYou have 60 SECONDS..."
    engine.game_state.current_level = 1
    
    return engine


class TestQuestTriggerWithEnterKey:
    """Tests for ENTER key triggering quest start."""

    def test_enter_key_dismisses_quest_dialog_and_spawns_hacker(self, game_engine_with_quest):
        """Test that ENTER key dismisses quest dialog and spawns hacker."""
        engine = game_engine_with_quest
        quest = engine.quest_manager.get_quest_for_level(1)
        
        # Verify initial state
        assert quest.status == QuestStatus.TRIGGERED
        assert engine.game_state.quest_message is not None
        assert engine.hacker is None
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        
        # Handle the input
        engine.handle_input([enter_event])
        
        # Verify quest dialog dismissed
        assert engine.game_state.quest_message is None
        
        # Verify hacker spawned
        assert engine.hacker is not None
        assert isinstance(engine.hacker, Hacker)
        
        # Verify quest status changed to ACTIVE
        assert quest.status == QuestStatus.ACTIVE
        assert quest.hacker_spawned is True

    def test_enter_key_spawns_hacker_near_player(self, game_engine_with_quest):
        """Test that hacker spawns near player position."""
        engine = game_engine_with_quest
        
        # Set player position
        engine.player.position.x = 300
        engine.player.position.y = 400
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify hacker spawned near player
        assert engine.hacker is not None
        # Hacker should spawn slightly behind player (x - 50)
        assert engine.hacker.position.x == engine.player.position.x - 50
        # Hacker should spawn on ground (832 - 32)
        assert engine.hacker.position.y == 832 - 32

    def test_enter_key_sets_hacker_target_to_service_position(self, game_engine_with_quest):
        """Test that hacker's target is set to service position."""
        engine = game_engine_with_quest
        quest = engine.quest_manager.get_quest_for_level(1)
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify hacker target matches quest service position
        assert engine.hacker.target_position.x == quest.service_position.x
        assert engine.hacker.target_position.y == quest.service_position.y

    def test_enter_key_does_nothing_when_no_quest_message(self, game_engine_with_quest):
        """Test that ENTER key does nothing when no quest message is showing."""
        engine = game_engine_with_quest
        
        # Clear quest message
        engine.game_state.quest_message = None
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify hacker not spawned
        assert engine.hacker is None

    def test_enter_key_does_nothing_when_quest_not_triggered(self, game_engine_with_quest):
        """Test that ENTER key does nothing when quest is not in TRIGGERED state."""
        engine = game_engine_with_quest
        quest = engine.quest_manager.get_quest_for_level(1)
        
        # Set quest to NOT_STARTED
        quest.status = QuestStatus.NOT_STARTED
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify hacker not spawned
        assert engine.hacker is None
        # Quest should still be NOT_STARTED
        assert quest.status == QuestStatus.NOT_STARTED


class TestQuestTriggerWithSpaceKey:
    """Tests for SPACE key triggering quest start."""

    def test_space_key_dismisses_quest_dialog_and_spawns_hacker(self, game_engine_with_quest):
        """Test that SPACE key dismisses quest dialog and spawns hacker."""
        engine = game_engine_with_quest
        quest = engine.quest_manager.get_quest_for_level(1)
        
        # Verify initial state
        assert quest.status == QuestStatus.TRIGGERED
        assert engine.game_state.quest_message is not None
        assert engine.hacker is None
        
        # Create SPACE key press event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        
        # Handle the input
        engine.handle_input([space_event])
        
        # Verify quest dialog dismissed
        assert engine.game_state.quest_message is None
        
        # Verify hacker spawned
        assert engine.hacker is not None
        assert isinstance(engine.hacker, Hacker)
        
        # Verify quest status changed to ACTIVE
        assert quest.status == QuestStatus.ACTIVE
        assert quest.hacker_spawned is True

    def test_space_key_spawns_hacker_on_ground(self, game_engine_with_quest):
        """Test that SPACE key spawns hacker on ground level."""
        engine = game_engine_with_quest
        
        # Create SPACE key press event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine.handle_input([space_event])
        
        # Verify hacker spawned on ground (y = 832 - 32 = 800)
        assert engine.hacker is not None
        assert engine.hacker.position.y == 800

    def test_space_key_does_nothing_when_no_quest_manager(self, mock_pygame, mock_api_client):
        """Test that SPACE key does nothing when no quest manager exists."""
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        engine.start()
        
        # No quest manager
        engine.quest_manager = None
        engine.game_state.quest_message = "Some message"
        
        # Create SPACE key press event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine.handle_input([space_event])
        
        # Verify hacker not spawned
        assert engine.hacker is None


class TestQuestTriggerPauseMessageDismissal:
    """Tests for ENTER/SPACE key dismissing pause messages."""

    def test_enter_key_dismisses_pause_message_when_no_quest(self, mock_pygame, mock_api_client):
        """Test that ENTER key dismisses pause message when no quest is active."""
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        engine.start()
        
        # Set up pause state
        engine.game_state.previous_status = GameStatus.PLAYING
        engine.game_state.status = GameStatus.PAUSED
        engine.game_state.congratulations_message = "Game Paused"
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify pause message dismissed
        assert engine.game_state.congratulations_message is None
        assert engine.game_state.status == GameStatus.PLAYING

    def test_space_key_dismisses_pause_message_when_no_quest(self, mock_pygame, mock_api_client):
        """Test that SPACE key dismisses pause message when no quest is active."""
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        engine.start()
        
        # Set up pause state
        engine.game_state.previous_status = GameStatus.PLAYING
        engine.game_state.status = GameStatus.PAUSED
        engine.game_state.congratulations_message = "Game Paused"
        
        # Create SPACE key press event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine.handle_input([space_event])
        
        # Verify pause message dismissed
        assert engine.game_state.congratulations_message is None
        assert engine.game_state.status == GameStatus.PLAYING

    def test_quest_trigger_takes_priority_over_pause_dismissal(self, game_engine_with_quest):
        """Test that quest triggering takes priority over pause message dismissal."""
        engine = game_engine_with_quest
        quest = engine.quest_manager.get_quest_for_level(1)
        
        # Set up both quest message and pause state
        engine.game_state.status = GameStatus.PAUSED
        engine.game_state.congratulations_message = "Some pause message"
        quest.status = QuestStatus.TRIGGERED
        engine.game_state.quest_message = "Quest warning"
        
        # Create ENTER key press event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Verify quest was triggered (not pause dismissed)
        assert engine.hacker is not None
        assert quest.status == QuestStatus.ACTIVE
        # Pause message should still be there (quest trigger took priority)
        assert engine.game_state.status == GameStatus.PAUSED


class TestQuestTriggerEdgeCases:
    """Tests for edge cases in quest triggering."""

    def test_multiple_enter_presses_only_spawn_one_hacker(self, game_engine_with_quest):
        """Test that multiple ENTER presses don't spawn multiple hackers."""
        engine = game_engine_with_quest
        
        # Press ENTER twice
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        first_hacker = engine.hacker
        assert first_hacker is not None
        
        # Press ENTER again
        engine.handle_input([enter_event])
        
        # Should still be the same hacker (or None if quest message cleared)
        # Quest is now ACTIVE, so second press should do nothing
        assert engine.game_state.quest_message is None

    def test_enter_and_space_both_work_for_same_quest(self, mock_pygame, mock_api_client):
        """Test that both ENTER and SPACE can trigger the same quest."""
        # Test with ENTER
        engine1 = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        engine1.start()
        engine1.quest_manager = ServiceProtectionQuestManager()
        quest1 = create_bedrock_protection_quest("test1", 1, Vector2(200, 400), Vector2(5000, 400))
        engine1.quest_manager.add_quest(quest1)
        quest1.status = QuestStatus.TRIGGERED
        engine1.game_state.quest_message = "Warning"
        engine1.game_state.current_level = 1
        
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine1.handle_input([enter_event])
        assert engine1.hacker is not None
        
        # Test with SPACE
        engine2 = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        engine2.start()
        engine2.quest_manager = ServiceProtectionQuestManager()
        quest2 = create_bedrock_protection_quest("test2", 1, Vector2(200, 400), Vector2(5000, 400))
        engine2.quest_manager.add_quest(quest2)
        quest2.status = QuestStatus.TRIGGERED
        engine2.game_state.quest_message = "Warning"
        engine2.game_state.current_level = 1
        
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine2.handle_input([space_event])
        assert engine2.hacker is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
