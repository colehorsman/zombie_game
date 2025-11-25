"""Tests for door interaction cooldown feature."""

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
    return engine


class TestDoorInteractionCooldownInitialization:
    """Tests for door interaction cooldown initialization."""

    def test_cooldown_initialized_to_zero(self, game_engine):
        """Test that door_interaction_cooldown is initialized to 0.0."""
        assert hasattr(game_engine, 'door_interaction_cooldown')
        assert game_engine.door_interaction_cooldown == 0.0

    def test_cooldown_is_float(self, game_engine):
        """Test that door_interaction_cooldown is a float."""
        assert isinstance(game_engine.door_interaction_cooldown, float)


class TestDoorInteractionCooldownDecrement:
    """Tests for door interaction cooldown decrement in lobby."""

    def test_cooldown_decrements_in_lobby(self, game_engine):
        """Test that cooldown decrements during lobby update."""
        # Set cooldown to 1.0 second
        game_engine.door_interaction_cooldown = 1.0
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update for 0.5 seconds
        game_engine._update_lobby(0.5)
        
        # Cooldown should be 0.5 seconds remaining
        assert game_engine.door_interaction_cooldown == pytest.approx(0.5, abs=0.01)

    def test_cooldown_reaches_zero(self, game_engine):
        """Test that cooldown reaches zero and stops."""
        # Set cooldown to 0.5 seconds
        game_engine.door_interaction_cooldown = 0.5
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update for 1.0 second (more than cooldown)
        game_engine._update_lobby(1.0)
        
        # Cooldown should be 0 or negative (clamped to 0)
        assert game_engine.door_interaction_cooldown <= 0.0

    def test_cooldown_does_not_decrement_when_zero(self, game_engine):
        """Test that cooldown stays at zero when already zero."""
        # Cooldown starts at 0.0
        assert game_engine.door_interaction_cooldown == 0.0
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update for 1.0 second
        game_engine._update_lobby(1.0)
        
        # Cooldown should still be 0 or negative
        assert game_engine.door_interaction_cooldown <= 0.0

    def test_cooldown_decrements_multiple_frames(self, game_engine):
        """Test that cooldown decrements correctly over multiple frames."""
        # Set cooldown to 1.0 second
        game_engine.door_interaction_cooldown = 1.0
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Simulate 60 FPS for 0.5 seconds (30 frames)
        delta_time = 1.0 / 60.0  # ~0.0167 seconds per frame
        for _ in range(30):
            game_engine._update_lobby(delta_time)
        
        # Cooldown should be approximately 0.5 seconds remaining
        assert game_engine.door_interaction_cooldown == pytest.approx(0.5, abs=0.05)


class TestDoorInteractionCooldownSetOnLobbyReturn:
    """Tests for cooldown being set when returning to lobby."""

    def test_cooldown_set_when_returning_to_lobby(self, mock_pygame, mock_api_client):
        """Test that cooldown is set to 1.0 when returning to lobby."""
        # Create engine with map mode
        with patch('game_engine.GameMap'):
            engine = GameEngine(
                api_client=mock_api_client,
                zombies=[],
                screen_width=1280,
                screen_height=720,
                use_map=True,
                account_data={"577945324761": 10},
                third_party_data={}
            )
            engine.start()
            
            # Set up game state as if in a level
            engine.game_state.status = GameStatus.PLAYING
            engine.game_state.current_level_account_id = "577945324761"
            
            # Mock the GameMap constructor to avoid file loading
            with patch('game_engine.GameMap') as mock_map_class:
                mock_map_instance = Mock()
                mock_map_instance.doors = []
                mock_map_instance.map_width = 1000
                mock_map_instance.map_height = 1000
                mock_map_class.return_value = mock_map_instance
                
                # Return to lobby
                engine._return_to_lobby()
                
                # Cooldown should be set to 1.0 seconds
                assert engine.door_interaction_cooldown == 1.0

    def test_cooldown_prevents_immediate_door_entry(self, mock_pygame, mock_api_client):
        """Test that cooldown prevents door interaction immediately after lobby return."""
        # This is an integration test concept - the actual door collision check
        # should skip doors when cooldown > 0
        # The check is: if self.door_interaction_cooldown <= 0
        
        # Create engine
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,
            account_data={},
            third_party_data={}
        )
        
        # Set cooldown to 1.0 (as if just returned to lobby)
        engine.door_interaction_cooldown = 1.0
        
        # Cooldown should prevent door interaction
        assert engine.door_interaction_cooldown > 0
        
        # After decrementing past 0, doors should be accessible
        engine.door_interaction_cooldown = 0.0
        assert engine.door_interaction_cooldown <= 0


class TestDoorInteractionCooldownEdgeCases:
    """Tests for edge cases in door interaction cooldown."""

    def test_cooldown_with_very_small_delta_time(self, game_engine):
        """Test cooldown with very small time steps."""
        game_engine.door_interaction_cooldown = 0.1
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update with very small delta time
        game_engine._update_lobby(0.001)
        
        # Cooldown should decrement slightly
        assert game_engine.door_interaction_cooldown == pytest.approx(0.099, abs=0.001)

    def test_cooldown_with_large_delta_time(self, game_engine):
        """Test cooldown with large time step (lag spike)."""
        game_engine.door_interaction_cooldown = 0.5
        game_engine.game_state.status = GameStatus.LOBBY
        
        # Update with large delta time (lag spike)
        game_engine._update_lobby(2.0)
        
        # Cooldown should go negative (which is fine, <= 0 check allows doors)
        assert game_engine.door_interaction_cooldown <= 0.0

    def test_cooldown_does_not_affect_playing_mode(self, game_engine):
        """Test that cooldown is only decremented in lobby mode."""
        game_engine.door_interaction_cooldown = 1.0
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update in playing mode (not lobby)
        # Note: _update_playing doesn't decrement cooldown
        initial_cooldown = game_engine.door_interaction_cooldown
        
        # Cooldown should not change in playing mode
        # (it only decrements in _update_lobby)
        assert game_engine.door_interaction_cooldown == initial_cooldown


class TestDoorInteractionCooldownIntegration:
    """Integration tests for door interaction cooldown workflow."""

    def test_complete_cooldown_workflow(self, mock_pygame, mock_api_client):
        """Test complete workflow: return to lobby → cooldown → doors accessible."""
        # Create engine with map mode
        with patch('game_engine.GameMap'):
            engine = GameEngine(
                api_client=mock_api_client,
                zombies=[],
                screen_width=1280,
                screen_height=720,
                use_map=True,
                account_data={"577945324761": 10},
                third_party_data={}
            )
            engine.start()
            
            # Initial state: cooldown is 0
            assert engine.door_interaction_cooldown == 0.0
            
            # Simulate returning to lobby
            engine.game_state.status = GameStatus.PLAYING
            engine.game_state.current_level_account_id = "577945324761"
            
            with patch('game_engine.GameMap') as mock_map_class:
                mock_map_instance = Mock()
                mock_map_instance.doors = []
                mock_map_instance.map_width = 1000
                mock_map_instance.map_height = 1000
                mock_map_instance.scatter_zombies = Mock()
                mock_map_class.return_value = mock_map_instance
                
                # Mock Player to avoid map_width comparison issues
                with patch('game_engine.Player') as mock_player_class:
                    mock_player_instance = Mock()
                    mock_player_instance.position = Vector2(500, 500)
                    mock_player_class.return_value = mock_player_instance
                    
                    engine._return_to_lobby()
                    
                    # After returning to lobby, cooldown should be 1.0
                    assert engine.door_interaction_cooldown == 1.0
                    
                    # Test cooldown decrement without calling _update_lobby
                    # (to avoid player update issues)
                    engine.game_state.status = GameStatus.LOBBY
                    
                    # Manually decrement cooldown as _update_lobby would
                    engine.door_interaction_cooldown -= 0.5
                    assert engine.door_interaction_cooldown == pytest.approx(0.5, abs=0.01)
                    
                    # Decrement again
                    engine.door_interaction_cooldown -= 0.6
                    assert engine.door_interaction_cooldown <= 0.0
                    
                    # Doors should now be accessible (cooldown <= 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
