"""Tests for controller input handling - specifically button press behavior."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2
from zombie import Zombie


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
    return client


@pytest.fixture
def game_engine(mock_pygame, mock_api_client):
    """Create a game engine instance for testing."""
    zombies = []
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=zombies,
        screen_width=1280,
        screen_height=720,
        use_map=False,
        account_data={},
        third_party_data={}
    )
    engine.start()
    
    # Mock a joystick so controller events are processed
    engine.joystick = Mock()
    engine.joystick.get_name.return_value = "Test Controller"
    engine.joystick.get_numbuttons.return_value = 12  # Standard controller button count
    engine.joystick.get_numhats.return_value = 1  # Has D-pad
    engine.joystick.get_numaxes.return_value = 4  # Has analog sticks
    engine.joystick.get_hat.return_value = (0, 0)  # D-pad neutral
    engine.joystick.get_axis.return_value = 0.0  # Analog sticks neutral
    
    return engine


class TestControllerButtonMessageDismissal:
    """Tests for controller button handling when messages are displayed."""

    def test_a_button_dismisses_message_when_paused(self, game_engine):
        """Test that A button (0) dismisses congratulations message when paused."""
        # Setup: Show a congratulations message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Create A button press event (button 0)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=0
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify message was dismissed
        assert game_engine.game_state.congratulations_message is None
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_b_button_dismisses_message_when_paused(self, game_engine):
        """Test that B button (1) dismisses congratulations message when paused."""
        # Setup: Show a congratulations message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Create B button press event (button 1)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=1
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify message was dismissed
        assert game_engine.game_state.congratulations_message is None
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_a_button_fires_when_no_message(self, game_engine):
        """Test that A button fires projectile when no message is showing."""
        # Setup: Playing mode, no message
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.congratulations_message = None
        initial_projectile_count = len(game_engine.projectiles)
        
        # Create A button press event (button 0)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=0
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify projectile was fired
        assert len(game_engine.projectiles) == initial_projectile_count + 1

    def test_b_button_jumps_when_no_message(self, game_engine):
        """Test that B button makes player jump when no message is showing."""
        # Setup: Playing mode, no message
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.congratulations_message = None
        
        # Mock player jump method
        with patch.object(game_engine.player, 'jump') as mock_jump:
            # Create B button press event (button 1)
            button_event = pygame.event.Event(
                pygame.JOYBUTTONDOWN,
                joy=0,
                button=1
            )
            
            # Handle the input
            game_engine.handle_input([button_event])
            
            # Verify jump was called (at least once)
            assert mock_jump.call_count >= 1, "Jump should be called when B button pressed"

    def test_a_button_does_not_fire_when_message_showing(self, game_engine):
        """Test that A button dismisses message instead of firing when message is showing."""
        # Setup: Paused with message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        initial_projectile_count = len(game_engine.projectiles)
        
        # Create A button press event (button 0)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=0
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify no projectile was fired (message was dismissed instead)
        assert len(game_engine.projectiles) == initial_projectile_count
        assert game_engine.game_state.congratulations_message is None

    def test_b_button_does_not_jump_when_message_showing(self, game_engine):
        """Test that B button dismisses message instead of jumping when message is showing."""
        # Setup: Paused with message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Track initial state
        initial_status = game_engine.game_state.status
        
        # Create B button press event (button 1)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=1
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify message was dismissed (primary behavior)
        assert game_engine.game_state.congratulations_message is None
        # Verify status changed from PAUSED to PLAYING (message dismissed)
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert initial_status == GameStatus.PAUSED

    def test_start_button_still_dismisses_message(self, game_engine):
        """Test that Start button (7) still dismisses messages as before."""
        # Setup: Paused with message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Create Start button press event (button 7)
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=7
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify message was dismissed
        assert game_engine.game_state.congratulations_message is None
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_message_dismissal_restores_previous_status(self, game_engine):
        """Test that dismissing message restores the correct previous status."""
        # Setup: Paused from BOSS_BATTLE with message
        game_engine.game_state.previous_status = GameStatus.BOSS_BATTLE
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Boss Defeated!"
        
        # Create A button press event
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=0
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify status was restored to BOSS_BATTLE
        assert game_engine.game_state.status == GameStatus.BOSS_BATTLE
        assert game_engine.game_state.congratulations_message is None

    def test_a_button_fires_in_lobby_when_no_message(self, game_engine):
        """Test that A button fires projectile in lobby mode when no message."""
        # Setup: Lobby mode, no message
        game_engine.game_state.status = GameStatus.LOBBY
        game_engine.game_state.congratulations_message = None
        initial_projectile_count = len(game_engine.projectiles)
        
        # Create A button press event
        button_event = pygame.event.Event(
            pygame.JOYBUTTONDOWN,
            joy=0,
            button=0
        )
        
        # Handle the input
        game_engine.handle_input([button_event])
        
        # Verify projectile was fired (A button works in lobby)
        assert len(game_engine.projectiles) == initial_projectile_count + 1

    def test_b_button_does_not_jump_in_lobby(self, game_engine):
        """Test that B button does not jump in lobby mode (only in level mode)."""
        # Setup: Lobby mode, no message
        game_engine.game_state.status = GameStatus.LOBBY
        game_engine.game_state.congratulations_message = None
        
        # Mock player jump method
        with patch.object(game_engine.player, 'jump') as mock_jump:
            # Create B button press event
            button_event = pygame.event.Event(
                pygame.JOYBUTTONDOWN,
                joy=0,
                button=1
            )
            
            # Handle the input
            game_engine.handle_input([button_event])
            
            # Verify jump was NOT called (B button doesn't jump in lobby)
            mock_jump.assert_not_called()


class TestDismissMessageMethod:
    """Tests for the dismiss_message method itself."""

    def test_dismiss_message_clears_congratulations_message(self, game_engine):
        """Test that dismiss_message clears the congratulations message."""
        # Setup
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify
        assert game_engine.game_state.congratulations_message is None

    def test_dismiss_message_restores_previous_status(self, game_engine):
        """Test that dismiss_message restores the previous game status."""
        # Setup
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify
        assert game_engine.game_state.status == GameStatus.PLAYING
        assert game_engine.game_state.previous_status is None

    def test_dismiss_message_clears_pending_elimination(self, game_engine):
        """Test that dismiss_message clears pending elimination."""
        # Setup
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        game_engine.game_state.pending_elimination = "test-zombie-id"
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify
        assert game_engine.game_state.pending_elimination is None

    def test_dismiss_message_fallback_to_playing(self, game_engine):
        """Test that dismiss_message falls back to PLAYING if no previous_status."""
        # Setup: No previous_status set
        game_engine.game_state.previous_status = None
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = "Test Message"
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify fallback to PLAYING
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_dismiss_message_does_nothing_when_not_paused(self, game_engine):
        """Test that dismiss_message does nothing when not paused."""
        # Setup: Playing mode (not paused)
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.congratulations_message = None
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify status unchanged
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_dismiss_message_does_nothing_when_no_message(self, game_engine):
        """Test that dismiss_message does nothing when no message is showing."""
        # Setup: Paused but no message
        game_engine.game_state.previous_status = GameStatus.PLAYING
        game_engine.game_state.status = GameStatus.PAUSED
        game_engine.game_state.congratulations_message = None
        
        # Call dismiss_message
        game_engine.dismiss_message()
        
        # Verify status unchanged (still paused)
        assert game_engine.game_state.status == GameStatus.PAUSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
