"""Tests for pause menu arcade mode integration."""

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
from level_manager import LevelManager, Level


@pytest.fixture
def mock_pygame():
    """Mock pygame to avoid GUI dependencies."""
    with patch("pygame.init"), patch("pygame.display.set_mode"), patch(
        "pygame.font.Font"
    ), patch("pygame.time.Clock"), patch("pygame.joystick.init"), patch(
        "pygame.joystick.get_count", return_value=0
    ):
        yield


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = Mock()
    client.fetch_accounts_with_unused_identities.return_value = {}
    client.fetch_third_parties_by_account.return_value = {}
    client.get_unprotected_services.return_value = []  # No unprotected services
    return client


@pytest.fixture
def mock_level_manager():
    """Create a mock level manager with Sandbox level."""
    levels = [
        Level(
            level_number=1,
            account_id="577945324761",
            account_name="MyHealth - Sandbox",
            environment_type="sandbox",
            order=1,
        )
    ]

    manager = Mock(spec=LevelManager)
    manager.levels = levels
    manager.current_level_index = 0
    manager.get_current_level = Mock(return_value=levels[0])

    return manager


@pytest.fixture
def game_engine_in_sandbox(mock_pygame, mock_api_client, mock_level_manager):
    """Create a game engine in Sandbox level."""
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=[],
        screen_width=1280,
        screen_height=720,
        use_map=True,
        account_data={"577945324761": 10},
        third_party_data={},
        level_manager=mock_level_manager,
    )
    engine.start()

    # Enter Sandbox level
    engine.game_state.status = GameStatus.PLAYING
    engine.game_state.current_level = 1
    engine.game_state.current_level_account_id = "577945324761"

    return engine


class TestPauseMenuArcadeOption:
    """Tests for arcade mode option in pause menu."""

    def test_arcade_option_appears_in_sandbox(self, game_engine_in_sandbox):
        """Test that arcade mode option appears in pause menu when in Sandbox."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()

        # Verify arcade mode option is present
        assert "🎮 Arcade Mode" in engine.pause_menu_options
        assert len(engine.pause_menu_options) == 5

        # Verify order: Return to Game, Arcade Mode, Return to Lobby, Save Game, Quit Game
        assert engine.pause_menu_options[0] == "Return to Game"
        assert engine.pause_menu_options[1] == "🎮 Arcade Mode"
        assert engine.pause_menu_options[2] == "Return to Lobby"
        assert engine.pause_menu_options[3] == "Save Game"
        assert engine.pause_menu_options[4] == "Quit Game"

    def test_arcade_option_not_in_lobby(self, mock_pygame, mock_api_client):
        """Test that arcade mode option does not appear in lobby."""
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={},
            third_party_data={},
        )
        engine.start()

        # In lobby
        assert engine.game_state.status == GameStatus.LOBBY

        # Show pause menu
        engine._show_pause_menu()

        # Verify arcade mode option is NOT present
        assert "🎮 Arcade Mode" not in engine.pause_menu_options
        assert len(engine.pause_menu_options) == 4

    def test_arcade_option_not_when_arcade_active(self, game_engine_in_sandbox):
        """Test that arcade mode option does not appear when arcade is already active."""
        engine = game_engine_in_sandbox

        # Activate arcade mode
        engine.arcade_manager.active = True

        # Show pause menu
        engine._show_pause_menu()

        # Verify arcade mode option is NOT present
        assert "🎮 Arcade Mode" not in engine.pause_menu_options
        assert len(engine.pause_menu_options) == 4

    def test_arcade_option_only_in_sandbox_account(
        self, mock_pygame, mock_api_client, mock_level_manager
    ):
        """Test that arcade mode option only appears in Sandbox account (577945324761)."""
        # Create engine with different account
        mock_level_manager.levels[0].account_id = "613056517323"  # Production

        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={"613056517323": 10},
            third_party_data={},
            level_manager=mock_level_manager,
        )
        engine.start()

        # Enter Production level
        engine.game_state.status = GameStatus.PLAYING
        engine.game_state.current_level = 6
        engine.game_state.current_level_account_id = "613056517323"

        # Show pause menu
        engine._show_pause_menu()

        # Verify arcade mode option is NOT present (not Sandbox)
        assert "🎮 Arcade Mode" not in engine.pause_menu_options
        assert len(engine.pause_menu_options) == 4


class TestArcadeModeExecution:
    """Tests for executing arcade mode from pause menu."""

    def test_execute_arcade_mode_option(self, game_engine_in_sandbox):
        """Test that selecting arcade mode option starts arcade mode."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()

        # Select arcade mode option (index 1)
        engine.pause_menu_selected_index = 1
        assert engine.pause_menu_options[1] == "🎮 Arcade Mode"

        # Mock _start_arcade_mode to verify it's called
        with patch.object(engine, "_start_arcade_mode") as mock_start_arcade:
            # Execute the option
            engine._execute_pause_menu_option()

            # Verify arcade mode was started
            mock_start_arcade.assert_called_once()

            # Verify message was cleared
            assert engine.game_state.congratulations_message is None

            # Verify status was restored
            assert engine.game_state.status == GameStatus.PLAYING

    def test_arcade_mode_clears_pause_state(self, game_engine_in_sandbox):
        """Test that starting arcade mode properly clears pause state."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()

        # Verify paused
        assert engine.game_state.status == GameStatus.PAUSED
        assert engine.game_state.congratulations_message is not None
        assert engine.game_state.previous_status == GameStatus.PLAYING

        # Select and execute arcade mode
        engine.pause_menu_selected_index = 1

        with patch.object(engine, "_start_arcade_mode"):
            engine._execute_pause_menu_option()

            # Verify pause state cleared
            assert engine.game_state.congratulations_message is None
            assert engine.game_state.status == GameStatus.PLAYING

    def test_arcade_mode_navigation_to_option(self, game_engine_in_sandbox):
        """Test navigating to arcade mode option in pause menu."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()

        # Start at index 0 (Return to Game)
        assert engine.pause_menu_selected_index == 0

        # Navigate down to arcade mode (index 1)
        engine._navigate_pause_menu(1)

        # Verify at arcade mode option
        assert engine.pause_menu_selected_index == 1
        assert engine.pause_menu_options[1] == "🎮 Arcade Mode"

    def test_arcade_mode_option_in_menu_message(self, game_engine_in_sandbox):
        """Test that arcade mode option appears in pause menu message."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()

        # Get menu message
        menu_message = engine.game_state.congratulations_message

        # Verify arcade mode appears in message
        assert "🎮 Arcade Mode" in menu_message
        assert "⏸️  PAUSED" in menu_message


class TestPauseMenuIntegration:
    """Integration tests for pause menu with arcade mode."""

    def test_complete_workflow_pause_to_arcade(self, game_engine_in_sandbox):
        """Test complete workflow: pause → select arcade → start arcade."""
        engine = game_engine_in_sandbox

        # Step 1: Game is playing
        assert engine.game_state.status == GameStatus.PLAYING

        # Step 2: Show pause menu
        engine._show_pause_menu()
        assert engine.game_state.status == GameStatus.PAUSED
        assert "🎮 Arcade Mode" in engine.pause_menu_options

        # Step 3: Navigate to arcade mode
        engine._navigate_pause_menu(1)  # Move to arcade mode
        assert engine.pause_menu_selected_index == 1

        # Step 4: Execute arcade mode
        with patch.object(engine, "_start_arcade_mode") as mock_start:
            engine._execute_pause_menu_option()

            # Verify arcade started
            mock_start.assert_called_once()
            assert engine.game_state.status == GameStatus.PLAYING
            assert engine.game_state.congratulations_message is None

    def test_pause_menu_options_count_in_different_contexts(
        self, mock_pygame, mock_api_client, mock_level_manager
    ):
        """Test that pause menu has correct number of options in different contexts."""
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={"577945324761": 10},
            third_party_data={},
            level_manager=mock_level_manager,
        )
        engine.start()

        # Context 1: Lobby (4 options)
        assert engine.game_state.status == GameStatus.LOBBY
        engine._show_pause_menu()
        assert len(engine.pause_menu_options) == 4
        assert "🎮 Arcade Mode" not in engine.pause_menu_options

        # Context 2: Sandbox level (5 options)
        engine.game_state.status = GameStatus.PLAYING
        engine.game_state.current_level_account_id = "577945324761"
        engine._show_pause_menu()
        assert len(engine.pause_menu_options) == 5
        assert "🎮 Arcade Mode" in engine.pause_menu_options

        # Context 3: Arcade active (4 options)
        engine.arcade_manager.active = True
        engine._show_pause_menu()
        assert len(engine.pause_menu_options) == 4
        assert "🎮 Arcade Mode" not in engine.pause_menu_options

    def test_esc_key_closes_pause_menu_with_arcade_option(self, game_engine_in_sandbox):
        """Test that ESC key closes pause menu even with arcade option present."""
        engine = game_engine_in_sandbox

        # Show pause menu
        engine._show_pause_menu()
        assert engine.game_state.status == GameStatus.PAUSED
        assert "🎮 Arcade Mode" in engine.pause_menu_options

        # Press ESC to close
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        engine.handle_input([esc_event])

        # Verify menu closed
        assert engine.game_state.status == GameStatus.PLAYING
        assert engine.game_state.congratulations_message is None


class TestPauseMenuEdgeCases:
    """Edge case tests for pause menu arcade integration."""

    def test_arcade_option_position_consistent(self, game_engine_in_sandbox):
        """Test that arcade mode option is always at index 1 when present."""
        engine = game_engine_in_sandbox

        # Show pause menu multiple times
        for _ in range(3):
            engine._show_pause_menu()

            if "🎮 Arcade Mode" in engine.pause_menu_options:
                # Verify it's always at index 1
                assert engine.pause_menu_options[1] == "🎮 Arcade Mode"

    def test_menu_navigation_wraps_with_arcade_option(self, game_engine_in_sandbox):
        """Test that menu navigation wraps correctly with 5 options."""
        engine = game_engine_in_sandbox

        # Show pause menu (5 options)
        engine._show_pause_menu()
        assert len(engine.pause_menu_options) == 5

        # Start at index 0
        assert engine.pause_menu_selected_index == 0

        # Navigate up (should wrap to last option)
        engine._navigate_pause_menu(-1)
        assert engine.pause_menu_selected_index == 4  # Quit Game

        # Navigate down (should wrap to first option)
        engine._navigate_pause_menu(1)
        assert engine.pause_menu_selected_index == 0  # Return to Game

    def test_arcade_option_not_duplicated(self, game_engine_in_sandbox):
        """Test that arcade mode option is not duplicated in menu."""
        engine = game_engine_in_sandbox

        # Show pause menu multiple times
        for _ in range(3):
            engine._show_pause_menu()

            # Count arcade mode options
            arcade_count = sum(
                1 for opt in engine.pause_menu_options if opt == "🎮 Arcade Mode"
            )
            assert arcade_count <= 1, "Arcade mode option should appear at most once"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
