"""Tests for Arcade Mode Results Screen Input Handling."""

import pytest
from unittest.mock import Mock, patch
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
def game_engine_with_results(mock_pygame, mock_api_client):
    """Create a game engine with arcade results showing."""
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
    
    # Set up arcade mode with eliminations
    engine.arcade_manager.start_session()
    engine.arcade_manager.update(3.1)  # Complete countdown
    
    # Add some eliminations
    for i in range(5):
        zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
        engine.arcade_manager.queue_elimination(zombie)
    
    # Show results
    engine._show_arcade_results()
    
    return engine


class TestArcadeResultsMenuNavigation:
    """Tests for arcade results menu navigation."""

    def test_navigate_menu_down(self, game_engine_with_results):
        """Test navigating down in arcade results menu."""
        engine = game_engine_with_results
        
        # Initial selection should be 0
        assert engine.arcade_results_selected_index == 0
        
        # Navigate down
        engine._navigate_arcade_results_menu(1)
        
        # Selection should move to 1
        assert engine.arcade_results_selected_index == 1

    def test_navigate_menu_up(self, game_engine_with_results):
        """Test navigating up in arcade results menu."""
        engine = game_engine_with_results
        
        # Start at index 1
        engine.arcade_results_selected_index = 1
        
        # Navigate up
        engine._navigate_arcade_results_menu(-1)
        
        # Selection should move to 0
        assert engine.arcade_results_selected_index == 0

    def test_navigate_menu_wraps_at_bottom(self, game_engine_with_results):
        """Test menu navigation wraps from bottom to top."""
        engine = game_engine_with_results
        
        # Move to last option
        num_options = len(engine.arcade_results_options)
        engine.arcade_results_selected_index = num_options - 1
        
        # Navigate down (should wrap to 0)
        engine._navigate_arcade_results_menu(1)
        
        assert engine.arcade_results_selected_index == 0

    def test_navigate_menu_wraps_at_top(self, game_engine_with_results):
        """Test menu navigation wraps from top to bottom."""
        engine = game_engine_with_results
        
        # Start at 0
        assert engine.arcade_results_selected_index == 0
        
        # Navigate up (should wrap to last)
        engine._navigate_arcade_results_menu(-1)
        
        num_options = len(engine.arcade_results_options)
        assert engine.arcade_results_selected_index == num_options - 1

    def test_navigate_updates_display(self, game_engine_with_results):
        """Test that navigation updates the display message."""
        engine = game_engine_with_results
        
        initial_message = engine.game_state.congratulations_message
        
        # Navigate down
        engine._navigate_arcade_results_menu(1)
        
        # Message should be updated
        assert engine.game_state.congratulations_message != initial_message
        
        # Should show selection indicator on second option
        assert "▶ No - Discard Queue" in engine.game_state.congratulations_message


class TestArcadeResultsKeyboardInput:
    """Tests for keyboard input handling in arcade results."""

    def test_up_arrow_navigates_up(self, game_engine_with_results):
        """Test UP arrow key navigates up."""
        engine = game_engine_with_results
        engine.arcade_results_selected_index = 1
        
        # Create UP key event
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        engine.handle_input([up_event])
        
        assert engine.arcade_results_selected_index == 0

    def test_down_arrow_navigates_down(self, game_engine_with_results):
        """Test DOWN arrow key navigates down."""
        engine = game_engine_with_results
        
        # Create DOWN key event
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        engine.handle_input([down_event])
        
        assert engine.arcade_results_selected_index == 1

    def test_w_key_navigates_up(self, game_engine_with_results):
        """Test W key navigates up."""
        engine = game_engine_with_results
        engine.arcade_results_selected_index = 1
        
        # Create W key event
        w_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
        engine.handle_input([w_event])
        
        assert engine.arcade_results_selected_index == 0

    def test_s_key_navigates_down(self, game_engine_with_results):
        """Test S key navigates down."""
        engine = game_engine_with_results
        
        # Create S key event
        s_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
        engine.handle_input([s_event])
        
        assert engine.arcade_results_selected_index == 1

    def test_enter_key_executes_option(self, game_engine_with_results):
        """Test ENTER key executes selected option."""
        engine = game_engine_with_results
        
        # Select "No - Discard Queue" option
        engine.arcade_results_selected_index = 1
        
        # Create ENTER key event
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        engine.handle_input([enter_event])
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY

    def test_space_key_executes_option(self, game_engine_with_results):
        """Test SPACE key executes selected option."""
        engine = game_engine_with_results
        
        # Select "No - Discard Queue" option
        engine.arcade_results_selected_index = 1
        
        # Create SPACE key event
        space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        engine.handle_input([space_event])
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY


class TestArcadeResultsControllerInput:
    """Tests for controller input handling in arcade results."""

    def test_dpad_up_navigates_up(self, game_engine_with_results):
        """Test D-pad UP navigates up."""
        engine = game_engine_with_results
        engine.joystick = Mock()  # Enable controller
        engine.arcade_results_selected_index = 1
        
        # Create D-pad UP event (button 11)
        dpad_up_event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=11)
        engine.handle_input([dpad_up_event])
        
        assert engine.arcade_results_selected_index == 0

    def test_dpad_down_navigates_down(self, game_engine_with_results):
        """Test D-pad DOWN navigates down."""
        engine = game_engine_with_results
        engine.joystick = Mock()  # Enable controller
        
        # Create D-pad DOWN event (button 12)
        dpad_down_event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=12)
        engine.handle_input([dpad_down_event])
        
        assert engine.arcade_results_selected_index == 1

    def test_a_button_executes_option(self, game_engine_with_results):
        """Test A button executes selected option."""
        engine = game_engine_with_results
        # Enable controller with proper mock
        engine.joystick = Mock()
        engine.joystick.get_numbuttons.return_value = 15
        engine.joystick.get_numhats.return_value = 1
        engine.joystick.get_hat.return_value = (0, 0)
        engine.joystick.get_numaxes.return_value = 2
        engine.joystick.get_axis.return_value = 0.0
        
        # Select "No - Discard Queue" option
        engine.arcade_results_selected_index = 1
        
        # Create A button event (button 0)
        a_button_event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=0)
        engine.handle_input([a_button_event])
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY

    def test_b_button_executes_option(self, game_engine_with_results):
        """Test B button executes selected option."""
        engine = game_engine_with_results
        # Enable controller with proper mock
        engine.joystick = Mock()
        engine.joystick.get_numbuttons.return_value = 15
        engine.joystick.get_numhats.return_value = 1
        engine.joystick.get_hat.return_value = (0, 0)
        engine.joystick.get_numaxes.return_value = 2
        engine.joystick.get_axis.return_value = 0.0
        
        # Select "No - Discard Queue" option
        engine.arcade_results_selected_index = 1
        
        # Create B button event (button 1)
        b_button_event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=1)
        engine.handle_input([b_button_event])
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY


class TestArcadeResultsOptionExecution:
    """Tests for executing arcade results menu options."""

    def test_execute_discard_queue_option(self, game_engine_with_results):
        """Test executing 'No - Discard Queue' option."""
        engine = game_engine_with_results
        
        # Verify queue has eliminations
        assert len(engine.arcade_manager.get_elimination_queue()) == 5
        
        # Select "No - Discard Queue" (index 1)
        engine.arcade_results_selected_index = 1
        engine._execute_arcade_results_option()
        
        # Queue should be cleared
        assert len(engine.arcade_manager.get_elimination_queue()) == 0
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY

    def test_execute_replay_option(self, game_engine_with_results):
        """Test executing 'Replay - Try Again' option."""
        engine = game_engine_with_results
        
        # Select "Replay - Try Again" (index 2)
        engine.arcade_results_selected_index = 2
        engine._execute_arcade_results_option()
        
        # Arcade mode should restart
        assert engine.arcade_manager.is_active() is True
        assert engine.arcade_manager.is_in_countdown() is True
        
        # Should resume playing
        assert engine.game_state.status == GameStatus.PLAYING
        
        # Menu state should be cleared
        assert len(engine.arcade_results_options) == 0

    def test_execute_exit_option_no_eliminations(self, mock_pygame, mock_api_client):
        """Test executing 'Exit - Return to Lobby' when no eliminations."""
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
        
        # Set up arcade mode with NO eliminations
        engine.arcade_manager.start_session()
        engine.arcade_manager.update(3.1)
        
        # Show results (no eliminations)
        engine._show_arcade_results()
        
        # Should have "Exit - Return to Lobby" option
        assert "Exit - Return to Lobby" in engine.arcade_results_options
        
        # Select "Exit - Return to Lobby" (index 1 when no eliminations)
        engine.arcade_results_selected_index = 1
        engine._execute_arcade_results_option()
        
        # Should return to lobby
        assert engine.game_state.status == GameStatus.LOBBY

    def test_execute_quarantine_all_option_placeholder(self, game_engine_with_results):
        """Test executing 'Yes - Quarantine All' option (batch quarantine implemented)."""
        engine = game_engine_with_results
        
        # Select "Yes - Quarantine All" (index 0)
        engine.arcade_results_selected_index = 0
        engine._execute_arcade_results_option()
        
        # Batch quarantine is now implemented
        # Should clear queue after batch operation
        assert len(engine.arcade_manager.get_elimination_queue()) == 0
        
        # Should show results message (not immediately return to lobby)
        assert engine.game_state.status == GameStatus.PAUSED
        assert "Batch Quarantine Complete" in engine.game_state.congratulations_message


class TestArcadeResultsEdgeCases:
    """Edge case tests for arcade results input handling."""

    def test_navigation_with_empty_options(self, mock_pygame, mock_api_client):
        """Test navigation doesn't crash with empty options."""
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
        
        # Clear options
        engine.arcade_results_options = []
        
        # Should not crash
        engine._navigate_arcade_results_menu(1)
        engine._navigate_arcade_results_menu(-1)

    def test_execution_with_invalid_index(self, game_engine_with_results):
        """Test execution with invalid index doesn't crash."""
        engine = game_engine_with_results
        
        # Set invalid index
        engine.arcade_results_selected_index = 999
        
        # Should not crash
        engine._execute_arcade_results_option()

    def test_multiple_navigation_cycles(self, game_engine_with_results):
        """Test multiple navigation cycles work correctly."""
        engine = game_engine_with_results
        
        num_options = len(engine.arcade_results_options)
        
        # Navigate through all options twice
        for _ in range(num_options * 2):
            engine._navigate_arcade_results_menu(1)
        
        # Should wrap back to start
        assert engine.arcade_results_selected_index == 0

    def test_rapid_input_handling(self, game_engine_with_results):
        """Test rapid input doesn't cause issues."""
        engine = game_engine_with_results
        
        # Simulate rapid key presses
        for _ in range(10):
            down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            engine.handle_input([down_event])
        
        # Should still be in valid state
        assert 0 <= engine.arcade_results_selected_index < len(engine.arcade_results_options)


class TestArcadeResultsIntegration:
    """Integration tests for complete arcade results workflow."""

    def test_complete_workflow_with_replay(self, game_engine_with_results):
        """Test complete workflow: results → navigate → replay."""
        engine = game_engine_with_results
        
        # Verify we're showing results
        assert "ARCADE MODE COMPLETE" in engine.game_state.congratulations_message
        
        # Navigate to "Replay" option
        engine._navigate_arcade_results_menu(1)  # Move to "No"
        engine._navigate_arcade_results_menu(1)  # Move to "Replay"
        
        # Execute replay
        engine._execute_arcade_results_option()
        
        # Should restart arcade mode
        assert engine.arcade_manager.is_active() is True
        assert engine.game_state.status == GameStatus.PLAYING

    def test_complete_workflow_with_discard(self, game_engine_with_results):
        """Test complete workflow: results → navigate → discard → lobby."""
        engine = game_engine_with_results
        
        initial_queue_size = len(engine.arcade_manager.get_elimination_queue())
        assert initial_queue_size > 0
        
        # Navigate to "No - Discard Queue"
        engine._navigate_arcade_results_menu(1)
        
        # Execute discard
        engine._execute_arcade_results_option()
        
        # Queue should be cleared
        assert len(engine.arcade_manager.get_elimination_queue()) == 0
        
        # Should be in lobby
        assert engine.game_state.status == GameStatus.LOBBY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
