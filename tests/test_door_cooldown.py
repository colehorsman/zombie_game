"""Tests for door interaction cooldown bug fix."""

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
from level_manager import LevelManager


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
        use_map=True,
        account_data={},
        third_party_data={}
    )
    engine.start()
    return engine


class TestDoorInteractionCooldown:
    """Tests for door interaction cooldown to prevent immediate re-entry."""

    def test_cooldown_initialized_to_zero(self, game_engine):
        """Test that door cooldown starts at zero."""
        assert game_engine.door_interaction_cooldown == 0.0

    def test_cooldown_set_when_returning_to_lobby(self, game_engine):
        """Test that cooldown is set when returning to lobby."""
        # Simulate being in a level
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.current_level_account_id = "577945324761"
        
        # Return to lobby
        game_engine._return_to_lobby()
        
        # Verify cooldown was set to 2.0 seconds (increased from 1.0 to prevent immediate re-entry)
        assert game_engine.door_interaction_cooldown == 2.0
        assert game_engine.game_state.status == GameStatus.LOBBY

    def test_cooldown_decrements_during_lobby_update(self, game_engine):
        """Test that cooldown decrements during lobby updates."""
        # Set cooldown
        game_engine.door_interaction_cooldown = 1.0
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update lobby for 0.5 seconds
        game_engine._update_lobby(0.5)
        
        # Verify cooldown decreased
        assert game_engine.door_interaction_cooldown == 0.5

    def test_cooldown_reaches_zero(self, game_engine):
        """Test that cooldown reaches zero and stops."""
        # Set cooldown
        game_engine.door_interaction_cooldown = 0.3
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update lobby for 0.5 seconds (more than cooldown)
        game_engine._update_lobby(0.5)
        
        # Verify cooldown is at or below zero
        assert game_engine.door_interaction_cooldown <= 0.0

    def test_doors_blocked_during_cooldown(self, game_engine):
        """Test that door collisions are ignored during cooldown."""
        # Set cooldown
        game_engine.door_interaction_cooldown = 1.0
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Create a mock door near player
        mock_door = Mock()
        mock_door.destination_room_name = "Test Room"
        mock_door.position = Vector2(game_engine.player.position.x, game_engine.player.position.y)
        mock_door.check_collision = Mock(return_value=True)  # Door would collide
        
        # Add door to game map
        if game_engine.game_map:
            game_engine.game_map.doors = [mock_door]
        
        # Update lobby (should NOT enter door due to cooldown)
        initial_status = game_engine.game_state.status
        game_engine._update_lobby(0.1)
        
        # Verify we're still in lobby (door was blocked)
        assert game_engine.game_state.status == GameStatus.LOBBY
        assert game_engine.game_state.status == initial_status

    def test_doors_work_after_cooldown_expires(self, game_engine):
        """Test that doors work normally after cooldown expires."""
        # Set cooldown to very small value
        game_engine.door_interaction_cooldown = 0.01
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update lobby to expire cooldown
        game_engine._update_lobby(0.1)
        
        # Verify cooldown expired
        assert game_engine.door_interaction_cooldown <= 0.0
        
        # Now doors should work (tested by checking cooldown is not blocking)
        # The actual door entry logic is tested elsewhere

    def test_multiple_lobby_returns_reset_cooldown(self, game_engine):
        """Test that returning to lobby multiple times resets cooldown each time."""
        # First return
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine._return_to_lobby()
        assert game_engine.door_interaction_cooldown == 2.0
        
        # Simulate time passing
        game_engine._update_lobby(0.5)
        assert game_engine.door_interaction_cooldown == 1.5
        
        # Enter level again (simulate)
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Return to lobby again
        game_engine._return_to_lobby()
        
        # Verify cooldown was reset to full 2.0 seconds
        assert game_engine.door_interaction_cooldown == 2.0

    def test_cooldown_prevents_immediate_sandbox_re_entry(self, game_engine):
        """Test the specific bug: returning from Sandbox doesn't immediately re-enter."""
        # Simulate being in Sandbox level
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.current_level_account_id = "577945324761"
        
        # Return to lobby (this was causing immediate re-entry)
        game_engine._return_to_lobby()
        
        # Verify:
        # 1. We're in lobby
        assert game_engine.game_state.status == GameStatus.LOBBY
        
        # 2. Cooldown is active
        assert game_engine.door_interaction_cooldown > 0
        
        # 3. Player is at landing zone (center of map)
        assert game_engine.player.position.x == game_engine.landing_zone.x
        assert game_engine.player.position.y == game_engine.landing_zone.y
        
        # 4. Even if we update immediately, we stay in lobby
        game_engine._update_lobby(0.01)
        assert game_engine.game_state.status == GameStatus.LOBBY


class TestDoorCooldownIntegration:
    """Integration tests for door cooldown with pause menu."""

    def test_pause_menu_return_to_lobby_sets_cooldown(self, game_engine):
        """Test that using pause menu to return to lobby sets cooldown."""
        # Simulate being in a level
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.current_level_account_id = "577945324761"

        # Show pause menu
        game_engine._show_pause_menu()
        assert game_engine.game_state.status == GameStatus.PAUSED

        # Select "Return to Lobby" option (index 2 when arcade option is included)
        # Menu: ["Return to Game", "Arcade Mode", "Return to Lobby", ...]
        game_engine.pause_menu_selected_index = 2
        game_engine._execute_pause_menu_option()
        
        # Verify we're in lobby with cooldown (2.0 seconds to prevent immediate re-entry)
        assert game_engine.game_state.status == GameStatus.LOBBY
        assert game_engine.door_interaction_cooldown == 2.0

    def test_l_key_return_to_lobby_sets_cooldown(self, game_engine):
        """Test that L key return to lobby sets cooldown."""
        # Simulate being in a level
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.current_level_account_id = "577945324761"
        
        # Press L key to return to lobby
        game_engine._return_to_lobby()
        
        # Verify we're in lobby with cooldown (2.0 seconds to prevent immediate re-entry)
        assert game_engine.game_state.status == GameStatus.LOBBY
        assert game_engine.door_interaction_cooldown == 2.0

    def test_select_button_return_to_lobby_sets_cooldown(self, game_engine):
        """Test that controller Select button return to lobby sets cooldown."""
        # Simulate being in a level
        game_engine.game_state.status = GameStatus.PLAYING
        game_engine.game_state.current_level_account_id = "577945324761"
        
        # Simulate Select button press (calls _return_to_lobby)
        game_engine._return_to_lobby()
        
        # Verify we're in lobby with cooldown (2.0 seconds to prevent immediate re-entry)
        assert game_engine.game_state.status == GameStatus.LOBBY
        assert game_engine.door_interaction_cooldown == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
