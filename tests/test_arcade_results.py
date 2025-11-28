"""Tests for Arcade Mode Results Screen."""

import pytest
from unittest.mock import Mock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2, ArcadeStats
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
    return engine


class TestArcadeResultsScreen:
    """Tests for arcade mode results screen display."""

    def test_show_arcade_results_displays_statistics(self, game_engine):
        """Test that arcade results screen displays correct statistics."""
        # Set up arcade mode with some eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)  # Complete countdown
        
        # Add eliminations
        for i in range(10):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Record power-ups
        from powerup import PowerUpType
        game_engine.arcade_manager.record_powerup_collection(PowerUpType.STAR_POWER)
        game_engine.arcade_manager.record_powerup_collection(PowerUpType.LAMBDA_SPEED)
        
        # Simulate time passing
        game_engine.arcade_manager.update(5.0)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Verify game is paused
        assert game_engine.game_state.status == GameStatus.PAUSED
        
        # Verify message contains statistics
        message = game_engine.game_state.congratulations_message
        assert "ARCADE MODE COMPLETE" in message
        assert "Zombies Eliminated: 10" in message
        assert "Highest Combo: 10x" in message
        assert "Power-ups Collected: 2" in message
        assert "Eliminations/Second:" in message

    def test_show_arcade_results_with_eliminations_shows_quarantine_options(self, game_engine):
        """Test that results screen shows quarantine options when eliminations exist."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add 5 eliminations
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify quarantine options are shown
        assert "5 identities queued for quarantine" in message
        assert "Quarantine all eliminated identities?" in message
        assert "Yes - Quarantine All" in message
        assert "No - Discard Queue" in message
        assert "Replay - Try Again" in message
        
        # Verify menu options are set correctly
        assert len(game_engine.arcade_results_options) == 3
        assert "Yes - Quarantine All" in game_engine.arcade_results_options
        assert "No - Discard Queue" in game_engine.arcade_results_options
        assert "Replay - Try Again" in game_engine.arcade_results_options

    def test_show_arcade_results_without_eliminations_shows_replay_options(self, game_engine):
        """Test that results screen shows replay options when no eliminations exist."""
        # Set up arcade mode with no eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Show results (no eliminations)
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify no quarantine options
        assert "No eliminations to quarantine" in message
        assert "Replay - Try Again" in message
        assert "Exit - Return to Lobby" in message
        
        # Verify quarantine options are NOT shown
        assert "Quarantine all eliminated identities?" not in message
        assert "Yes - Quarantine All" not in message
        assert "No - Discard Queue" not in message
        
        # Verify menu options are set correctly
        assert len(game_engine.arcade_results_options) == 2
        assert "Replay - Try Again" in game_engine.arcade_results_options
        assert "Exit - Return to Lobby" in game_engine.arcade_results_options

    def test_show_arcade_results_initializes_menu_state(self, game_engine):
        """Test that results screen initializes menu state correctly."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add some eliminations
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Verify menu state is initialized
        assert game_engine.arcade_results_selected_index == 0
        assert len(game_engine.arcade_results_options) > 0

    def test_show_arcade_results_shows_keyboard_controls(self, game_engine):
        """Test that results screen shows keyboard controls when no controller."""
        # Ensure no controller
        game_engine.joystick = None
        
        # Set up and show results
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify keyboard controls are shown
        assert "↑/↓ or W/S = Select" in message
        assert "ENTER or SPACE = Confirm" in message

    def test_show_arcade_results_shows_controller_controls(self, game_engine):
        """Test that results screen shows controller controls when controller present."""
        # Mock controller
        game_engine.joystick = Mock()
        
        # Set up and show results
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify controller controls are shown
        assert game_engine.controller_labels['up'] in message
        assert game_engine.controller_labels['down'] in message
        assert game_engine.controller_labels['confirm'] in message

    def test_show_arcade_results_preserves_previous_status(self, game_engine):
        """Test that results screen preserves previous game status."""
        # Set game to PLAYING
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Set up and show results
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        game_engine._show_arcade_results()
        
        # Verify previous status is preserved
        assert game_engine.game_state.previous_status == GameStatus.PLAYING
        assert game_engine.game_state.status == GameStatus.PAUSED

    def test_show_arcade_results_with_zero_eliminations(self, game_engine):
        """Test results screen with exactly zero eliminations."""
        # Set up arcade mode with no eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify statistics show zero
        assert "Zombies Eliminated: 0" in message
        assert "Highest Combo: 0x" in message
        
        # Verify no quarantine options
        assert "No eliminations to quarantine" in message

    def test_show_arcade_results_with_high_combo(self, game_engine):
        """Test results screen displays high combo correctly."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Build a high combo (25 eliminations)
        for i in range(25):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify high combo is shown
        assert "Highest Combo: 25x" in message
        assert "Zombies Eliminated: 25" in message

    def test_show_arcade_results_formats_eliminations_per_second(self, game_engine):
        """Test that eliminations per second is formatted correctly."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add eliminations
        for i in range(10):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Simulate 5 seconds
        game_engine.arcade_manager.update(5.0)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify format (should be 2 decimal places)
        assert "Eliminations/Second: 2.00" in message


class TestArcadeModeIntegration:
    """Integration tests for arcade mode workflow with results screen."""

    def test_arcade_mode_ends_and_shows_results(self, game_engine):
        """Test that arcade mode ending triggers results screen."""
        # Start arcade mode
        game_engine.arcade_manager.start_session()
        
        # Complete countdown
        game_engine.arcade_manager.update(3.1)
        
        # Add some eliminations
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Verify arcade is active
        assert game_engine.arcade_manager.is_active() is True
        
        # Update past 60 seconds to end session
        game_engine.arcade_manager.update(60.0)
        
        # Verify arcade ended
        assert game_engine.arcade_manager.is_active() is False
        
        # Call _update_arcade_mode which should show results
        game_engine._update_arcade_mode(0.016)
        
        # Verify results screen is shown
        assert game_engine.game_state.status == GameStatus.PAUSED
        assert "ARCADE MODE COMPLETE" in game_engine.game_state.congratulations_message

    def test_arcade_results_queue_size_matches_eliminations(self, game_engine):
        """Test that queue size in results matches actual eliminations."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add 15 eliminations
        for i in range(15):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify queue size matches
        assert "15 identities queued for quarantine" in message
        
        # Verify actual queue size
        queue = game_engine.arcade_manager.get_elimination_queue()
        assert len(queue) == 15


class TestArcadeResultsEdgeCases:
    """Edge case tests for arcade results screen."""

    def test_show_arcade_results_with_no_powerups(self, game_engine):
        """Test results screen with zero power-ups collected."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add eliminations but no power-ups
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Verify power-ups show zero
        assert "Power-ups Collected: 0" in message

    def test_show_arcade_results_multiple_times(self, game_engine):
        """Test that results screen can be shown multiple times."""
        # First session
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        zombie1 = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie1)
        game_engine._show_arcade_results()
        
        first_message = game_engine.game_state.congratulations_message
        assert "Zombies Eliminated: 1" in first_message
        
        # Second session
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        game_engine._show_arcade_results()
        
        second_message = game_engine.game_state.congratulations_message
        assert "Zombies Eliminated: 5" in second_message

    def test_show_arcade_results_with_very_short_session(self, game_engine):
        """Test results screen with very short session duration."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Add eliminations quickly
        for i in range(10):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Very short time (0.5 seconds)
        game_engine.arcade_manager.update(0.5)
        
        # Show results
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        
        # Should show high eliminations per second
        assert "Eliminations/Second:" in message
        # Rate should be 10 / 0.5 = 20.00
        assert "20.00" in message


class TestArcadeResultsMenuNavigation:
    """Tests for arcade results menu navigation."""

    def test_navigate_arcade_results_menu_down(self, game_engine):
        """Test navigating down in arcade results menu."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Initial selection should be 0
        assert game_engine.arcade_results_selected_index == 0
        
        # Navigate down
        game_engine._navigate_arcade_results_menu(1)
        
        # Should be at index 1
        assert game_engine.arcade_results_selected_index == 1

    def test_navigate_arcade_results_menu_up(self, game_engine):
        """Test navigating up in arcade results menu."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Navigate down twice
        game_engine._navigate_arcade_results_menu(1)
        game_engine._navigate_arcade_results_menu(1)
        assert game_engine.arcade_results_selected_index == 2
        
        # Navigate up
        game_engine._navigate_arcade_results_menu(-1)
        
        # Should be at index 1
        assert game_engine.arcade_results_selected_index == 1

    def test_navigate_arcade_results_menu_wraps_around(self, game_engine):
        """Test that menu navigation wraps around at boundaries."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results (3 options: Yes, No, Replay)
        game_engine._show_arcade_results()
        
        # Navigate up from index 0 (should wrap to last option)
        game_engine._navigate_arcade_results_menu(-1)
        
        # Should wrap to last index (2)
        assert game_engine.arcade_results_selected_index == 2
        
        # Navigate down from last index (should wrap to 0)
        game_engine._navigate_arcade_results_menu(1)
        
        # Should wrap to 0
        assert game_engine.arcade_results_selected_index == 0

    def test_navigate_arcade_results_menu_with_no_options(self, game_engine):
        """Test navigation when no options are set."""
        # Clear options
        game_engine.arcade_results_options = []
        
        # Should not crash
        game_engine._navigate_arcade_results_menu(1)
        game_engine._navigate_arcade_results_menu(-1)

    def test_navigate_arcade_results_menu_updates_display(self, game_engine):
        """Test that navigation updates the display message."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Get initial message
        initial_message = game_engine.game_state.congratulations_message
        
        # Navigate down
        game_engine._navigate_arcade_results_menu(1)
        
        # Message should be updated
        updated_message = game_engine.game_state.congratulations_message
        assert updated_message != initial_message
        
        # Should show different selection indicator
        assert "▶" in updated_message


class TestArcadeResultsDisplayUpdate:
    """Tests for arcade results display update."""

    def test_update_arcade_results_display_shows_selection_indicator(self, game_engine):
        """Test that display update shows selection indicator on current option."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Set selection to index 1
        game_engine.arcade_results_selected_index = 1
        
        # Update display
        game_engine._update_arcade_results_display()
        
        message = game_engine.game_state.congratulations_message
        
        # Should show selection indicator on second option
        lines = message.split('\n')
        option_lines = [line for line in lines if 'Quarantine' in line or 'Discard' in line or 'Replay' in line]
        
        # Second option should have indicator
        assert any('▶' in line and 'No - Discard Queue' in line for line in option_lines)

    def test_update_arcade_results_display_with_queue(self, game_engine):
        """Test display update with elimination queue."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Update display
        game_engine._update_arcade_results_display()
        
        message = game_engine.game_state.congratulations_message
        
        # Should show queue size
        assert "5 identities queued for quarantine" in message
        assert "Quarantine all eliminated identities?" in message

    def test_update_arcade_results_display_without_queue(self, game_engine):
        """Test display update without elimination queue."""
        # Set up arcade mode without eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Update display
        game_engine._update_arcade_results_display()
        
        message = game_engine.game_state.congratulations_message
        
        # Should show no eliminations message
        assert "No eliminations to quarantine" in message
        assert "Quarantine all eliminated identities?" not in message


class TestArcadeResultsOptionExecution:
    """Tests for arcade results option execution."""

    def test_execute_yes_quarantine_all_option(self, game_engine):
        """Test executing 'Yes - Quarantine All' option."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Select "Yes - Quarantine All" (index 0)
        game_engine.arcade_results_selected_index = 0
        
        # Execute option
        game_engine._execute_arcade_results_option()
        
        # Should clear queue (batch quarantine not yet implemented)
        queue = game_engine.arcade_manager.get_elimination_queue()
        assert len(queue) == 0
        
        # Should return to lobby
        assert game_engine.game_state.status == GameStatus.LOBBY

    def test_execute_no_discard_queue_option(self, game_engine):
        """Test executing 'No - Discard Queue' option."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Select "No - Discard Queue" (index 1)
        game_engine.arcade_results_selected_index = 1
        
        # Execute option
        game_engine._execute_arcade_results_option()
        
        # Should clear queue
        queue = game_engine.arcade_manager.get_elimination_queue()
        assert len(queue) == 0
        
        # Should return to lobby
        assert game_engine.game_state.status == GameStatus.LOBBY

    def test_execute_replay_try_again_option(self, game_engine):
        """Test executing 'Replay - Try Again' option."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Select "Replay - Try Again" (index 2)
        game_engine.arcade_results_selected_index = 2
        
        # Execute option
        game_engine._execute_arcade_results_option()
        
        # Should restart arcade mode
        assert game_engine.arcade_manager.is_active() is True
        
        # Should clear menu state
        assert len(game_engine.arcade_results_options) == 0
        assert game_engine.arcade_results_selected_index == 0
        
        # Should resume game
        assert game_engine.game_state.congratulations_message is None
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_execute_exit_return_to_lobby_option(self, game_engine):
        """Test executing 'Exit - Return to Lobby' option."""
        # Set up arcade mode without eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        # Show results (no eliminations)
        game_engine._show_arcade_results()
        
        # Select "Exit - Return to Lobby" (index 1 when no eliminations)
        game_engine.arcade_results_selected_index = 1
        
        # Execute option
        game_engine._execute_arcade_results_option()
        
        # Should return to lobby
        assert game_engine.game_state.status == GameStatus.LOBBY

    def test_execute_option_with_no_options(self, game_engine):
        """Test executing option when no options are set."""
        # Clear options
        game_engine.arcade_results_options = []
        
        # Should not crash
        game_engine._execute_arcade_results_option()

    def test_execute_option_with_invalid_index(self, game_engine):
        """Test executing option with invalid index."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Set invalid index
        game_engine.arcade_results_selected_index = 999
        
        # Should not crash
        game_engine._execute_arcade_results_option()

    def test_execute_replay_clears_previous_queue(self, game_engine):
        """Test that replay option doesn't carry over previous elimination queue."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        
        # Select "Replay - Try Again"
        game_engine.arcade_results_selected_index = 2
        
        # Execute option
        game_engine._execute_arcade_results_option()
        
        # New session should have empty queue
        queue = game_engine.arcade_manager.get_elimination_queue()
        assert len(queue) == 0


class TestArcadeResultsMenuIntegration:
    """Integration tests for arcade results menu workflow."""

    def test_complete_menu_navigation_workflow(self, game_engine):
        """Test complete workflow: show results → navigate → execute."""
        # Set up arcade mode with eliminations
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        for i in range(3):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            game_engine.arcade_manager.queue_elimination(zombie)
        
        # Show results
        game_engine._show_arcade_results()
        assert game_engine.arcade_results_selected_index == 0
        
        # Navigate down twice
        game_engine._navigate_arcade_results_menu(1)
        assert game_engine.arcade_results_selected_index == 1
        
        game_engine._navigate_arcade_results_menu(1)
        assert game_engine.arcade_results_selected_index == 2
        
        # Execute "Replay - Try Again"
        game_engine._execute_arcade_results_option()
        
        # Should restart arcade mode
        assert game_engine.arcade_manager.is_active() is True
        assert game_engine.game_state.status == GameStatus.PLAYING

    def test_menu_navigation_with_keyboard_and_controller(self, game_engine):
        """Test that menu navigation works with both keyboard and controller."""
        # Set up arcade mode
        game_engine.arcade_manager.start_session()
        game_engine.arcade_manager.update(3.1)
        
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        game_engine.arcade_manager.queue_elimination(zombie)
        
        # Test with keyboard (no controller)
        game_engine.joystick = None
        game_engine._show_arcade_results()
        
        message = game_engine.game_state.congratulations_message
        assert "↑/↓ or W/S = Select" in message
        
        # Navigate
        game_engine._navigate_arcade_results_menu(1)
        assert game_engine.arcade_results_selected_index == 1
        
        # Test with controller
        game_engine.joystick = Mock()
        game_engine._update_arcade_results_display()
        
        message = game_engine.game_state.congratulations_message
        assert game_engine.controller_labels['up'] in message
        assert game_engine.controller_labels['down'] in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
