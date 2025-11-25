"""Tests for Service Protection Quest - specifically the zombie state bug fix."""

import pytest
from unittest.mock import Mock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2, QuarantineResult, QuestStatus
from zombie import Zombie
from service_protection_quest import ServiceProtectionQuestManager, ServiceNode


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
    
    # Mock successful service protection
    client.protect_service.return_value = QuarantineResult(
        success=True,
        identity_id="bedrock-agentcore",
        error_message=None
    )
    
    return client


@pytest.fixture
def game_engine_with_zombies(mock_pygame, mock_api_client):
    """Create a game engine instance with zombies for testing."""
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
    
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=zombies,
        screen_width=1280,
        screen_height=720,
        use_map=False,
        account_data={"577945324761": 5},
        third_party_data={}
    )
    engine.start()
    
    # In classic mode (use_map=False), zombies list is empty by default
    # Manually populate it for testing the bug fix
    engine.zombies = zombies
    
    return engine


class TestServiceProtectionQuestZombieStateBugFix:
    """Tests for the zombie state bug fix when service protection quest succeeds."""

    def test_zombie_quarantine_flags_reset_on_quest_success(self, game_engine_with_zombies):
        """
        Test that zombie is_quarantining AND is_hidden flags are reset when service protection quest succeeds.
        
        This is a regression test for the bug where zombies could have incorrect
        is_quarantining and is_hidden flags set when the quest success message is shown,
        making them unshootable after resuming gameplay.
        """
        engine = game_engine_with_zombies
        
        # Simulate some zombies having incorrect is_quarantining AND is_hidden flags
        # (This happens when zombies are eliminated during quest - they get hidden and marked for quarantine)
        engine.zombies[0].is_quarantining = True
        engine.zombies[0].is_hidden = True
        engine.zombies[2].is_quarantining = True
        engine.zombies[2].is_hidden = True
        
        # Verify zombies have incorrect flags
        assert engine.zombies[0].is_quarantining is True
        assert engine.zombies[0].is_hidden is True
        assert engine.zombies[2].is_quarantining is True
        assert engine.zombies[2].is_hidden is True
        
        # Create a mock quest and service node
        from service_protection_quest import ServiceProtectionQuest
        quest = Mock(spec=ServiceProtectionQuest)
        quest.service_type = "bedrock-agentcore"
        quest.status = QuestStatus.ACTIVE
        
        service_node = Mock(spec=ServiceNode)
        service_node.protected = False
        service_node.position = Vector2(5000, 400)
        
        # Set up game state for quest
        engine.game_state.current_level_account_id = "577945324761"
        engine.game_state.status = GameStatus.PLAYING
        
        # Call the method that protects the service (this triggers the bug fix)
        engine._try_protect_service(quest, service_node)
        
        # Verify the bug fix: all zombies should have BOTH flags reset to False
        for zombie in engine.zombies:
            assert zombie.is_quarantining is False, \
                f"Zombie {zombie.identity_name} should have is_quarantining=False after quest success"
            assert zombie.is_hidden is False, \
                f"Zombie {zombie.identity_name} should have is_hidden=False after quest success (so they're shootable)"
        
        # Verify quest succeeded
        assert quest.status == QuestStatus.COMPLETED
        assert quest.player_won is True
        assert service_node.protected is True
        
        # Verify game was paused to show success message
        assert engine.game_state.status == GameStatus.PAUSED
        assert engine.game_state.congratulations_message is not None
        assert "AGENTCORE PROTECTED" in engine.game_state.congratulations_message

    def test_zombie_state_correct_when_no_incorrect_flags(self, game_engine_with_zombies):
        """
        Test that the bug fix doesn't break normal operation when zombies have correct flags.
        """
        engine = game_engine_with_zombies
        
        # All zombies start with is_quarantining = False (correct state)
        for zombie in engine.zombies:
            assert zombie.is_quarantining is False
        
        # Create a mock quest and service node
        from service_protection_quest import ServiceProtectionQuest
        quest = Mock(spec=ServiceProtectionQuest)
        quest.service_type = "bedrock-agentcore"
        quest.status = QuestStatus.ACTIVE
        
        service_node = Mock(spec=ServiceNode)
        service_node.protected = False
        service_node.position = Vector2(5000, 400)
        
        # Set up game state
        engine.game_state.current_level_account_id = "577945324761"
        engine.game_state.status = GameStatus.PLAYING
        
        # Protect the service
        engine._try_protect_service(quest, service_node)
        
        # Verify all zombies still have correct state
        for zombie in engine.zombies:
            assert zombie.is_quarantining is False
        
        # Verify quest succeeded
        assert quest.status == QuestStatus.COMPLETED
        assert quest.player_won is True

    def test_zombie_count_logged_correctly_on_quest_success(self, game_engine_with_zombies, caplog):
        """
        Test that the debug logging correctly reports zombie counts after bug fix.
        """
        engine = game_engine_with_zombies
        
        # Set some zombies to incorrect state
        engine.zombies[1].is_quarantining = True
        engine.zombies[3].is_quarantining = True
        
        # Create mock quest and service node
        from service_protection_quest import ServiceProtectionQuest
        quest = Mock(spec=ServiceProtectionQuest)
        quest.service_type = "bedrock-agentcore"
        quest.status = QuestStatus.ACTIVE
        
        service_node = Mock(spec=ServiceNode)
        service_node.protected = False
        service_node.position = Vector2(5000, 400)
        
        # Set up game state
        engine.game_state.current_level_account_id = "577945324761"
        engine.game_state.status = GameStatus.PLAYING
        
        # Protect the service
        with caplog.at_level("INFO"):
            engine._try_protect_service(quest, service_node)
        
        # Verify debug log shows correct zombie count
        debug_logs = [record for record in caplog.records if "DEBUG:" in record.message]
        assert len(debug_logs) > 0, "Should have debug log about zombie counts"
        
        # Check that the log shows all zombies are not quarantining
        zombie_count_log = [log for log in debug_logs if "zombies in list" in log.message]
        assert len(zombie_count_log) > 0
        
        # After bug fix, all 5 zombies should be "not quarantining"
        assert "5 not quarantining" in zombie_count_log[0].message

    def test_api_error_does_not_trigger_zombie_reset(self, game_engine_with_zombies):
        """
        Test that zombie flags are NOT reset when API call fails.
        
        The bug fix should only apply when the quest succeeds.
        """
        engine = game_engine_with_zombies
        
        # Set some zombies to quarantining and hidden state
        engine.zombies[0].is_quarantining = True
        engine.zombies[0].is_hidden = True
        engine.zombies[2].is_quarantining = True
        engine.zombies[2].is_hidden = True
        
        # Mock API to return failure
        engine.api_client.protect_service.return_value = QuarantineResult(
            success=False,
            identity_id="",
            error_message="API Error"
        )
        
        # Create mock quest and service node
        from service_protection_quest import ServiceProtectionQuest
        quest = Mock(spec=ServiceProtectionQuest)
        quest.service_type = "bedrock-agentcore"
        quest.status = QuestStatus.ACTIVE
        
        service_node = Mock(spec=ServiceNode)
        service_node.protected = False
        service_node.position = Vector2(5000, 400)
        
        # Set up game state
        engine.game_state.current_level_account_id = "577945324761"
        engine.game_state.status = GameStatus.PLAYING
        
        # Try to protect the service (should fail)
        engine._try_protect_service(quest, service_node)
        
        # Verify zombie flags were NOT reset (because API failed)
        assert engine.zombies[0].is_quarantining is True
        assert engine.zombies[0].is_hidden is True
        assert engine.zombies[2].is_quarantining is True
        assert engine.zombies[2].is_hidden is True
        
        # Verify quest did not succeed
        assert quest.status == QuestStatus.ACTIVE  # Still active, not completed
        assert service_node.protected is False
        
        # Verify game was NOT paused (no success message)
        assert engine.game_state.status == GameStatus.PLAYING


class TestServiceProtectionQuestIntegration:
    """Integration tests for service protection quest workflow."""

    def test_complete_quest_workflow_with_zombie_state_fix(self, game_engine_with_zombies):
        """
        Test complete workflow: quest active → player protects service → zombies reset → success.
        """
        engine = game_engine_with_zombies
        
        # Simulate quest in progress with some zombies in incorrect state (hidden + quarantining)
        engine.zombies[1].is_quarantining = True
        engine.zombies[1].is_hidden = True
        
        # Create quest manager and quest
        from service_protection_quest import create_bedrock_protection_quest
        quest = create_bedrock_protection_quest(
            quest_id="test_quest",
            level=1,
            trigger_pos=Vector2(200, 400),
            service_pos=Vector2(5000, 400)
        )
        quest.status = QuestStatus.ACTIVE
        
        # Create service node
        from service_protection_quest import create_service_node
        service_node = create_service_node(
            service_type="bedrock-agentcore",
            position=Vector2(5000, 400)
        )
        
        # Set up game state
        engine.game_state.current_level_account_id = "577945324761"
        engine.game_state.status = GameStatus.PLAYING
        engine.service_nodes = [service_node]
        
        # Protect the service
        engine._try_protect_service(quest, service_node)
        
        # Verify complete workflow
        assert quest.status == QuestStatus.COMPLETED
        assert quest.player_won is True
        assert service_node.protected is True
        
        # Verify zombie state fix applied (both flags reset)
        for zombie in engine.zombies:
            assert zombie.is_quarantining is False
            assert zombie.is_hidden is False
        
        # Verify success message shown
        assert engine.game_state.status == GameStatus.PAUSED
        assert "AGENTCORE PROTECTED" in engine.game_state.congratulations_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
