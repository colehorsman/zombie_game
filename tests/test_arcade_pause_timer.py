"""Tests for arcade mode timer pause functionality during game pause."""

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
def game_engine_with_arcade(mock_pygame, mock_api_client):
    """Create a game engine with arcade mode active."""
    zombies = [
        Zombie(
            identity_id=f"zombie-{i}",
            identity_name=f"TestZombie{i}",
            position=Vector2(1000 + i * 100, 400),
            account="577945324761"
        )
        for i in range(30)
    ]
    
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=zombies,
        screen_width=1280,
        screen_height=720,
        use_map=False,
        account_data={"577945324761": 30},
        third_party_data={}
    )
    engine.start()
    
    # Start arcade mode
    engine.arcade_manager.start_session()
    
    # Complete countdown
    engine.arcade_manager.update(3.1)
    
    # Set game to PLAYING
    engine.game_state.status = GameStatus.PLAYING
    
    return engine


class TestArcadeTimerPauseBehavior:
    """Tests for arcade mode timer pause behavior."""

    def test_arcade_timer_updates_during_playing_status(self, game_engine_with_arcade):
        """Test that arcade timer updates when game status is PLAYING."""
        engine = game_engine_with_arcade
        
        # Verify arcade mode is active
        assert engine.arcade_manager.is_active()
        assert engine.game_state.status == GameStatus.PLAYING
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Update game (should update arcade timer)
        engine.update(1.0)
        
        # Timer should have decreased
        assert engine.arcade_manager.time_remaining < initial_time
        assert engine.arcade_manager.time_remaining == pytest.approx(initial_time - 1.0, abs=0.01)

    def test_arcade_timer_pauses_during_paused_status(self, game_engine_with_arcade):
        """Test that arcade timer does NOT update when game status is PAUSED."""
        engine = game_engine_with_arcade
        
        # Verify arcade mode is active
        assert engine.arcade_manager.is_active()
        
        # Pause the game
        engine.game_state.status = GameStatus.PAUSED
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Update game (should NOT update arcade timer)
        engine.update(1.0)
        
        # Timer should NOT have changed
        assert engine.arcade_manager.time_remaining == initial_time

    def test_arcade_timer_resumes_after_unpause(self, game_engine_with_arcade):
        """Test that arcade timer resumes updating after unpausing."""
        engine = game_engine_with_arcade
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Pause the game
        engine.game_state.status = GameStatus.PAUSED
        engine.update(2.0)
        
        # Timer should not have changed during pause
        assert engine.arcade_manager.time_remaining == initial_time
        
        # Resume the game
        engine.game_state.status = GameStatus.PLAYING
        engine.update(1.0)
        
        # Timer should now have decreased
        assert engine.arcade_manager.time_remaining < initial_time
        assert engine.arcade_manager.time_remaining == pytest.approx(initial_time - 1.0, abs=0.01)

    def test_arcade_state_synced_during_pause(self, game_engine_with_arcade):
        """Test that arcade state is synced to game_state during pause for rendering."""
        engine = game_engine_with_arcade
        
        # Pause the game
        engine.game_state.status = GameStatus.PAUSED
        
        # Update game
        engine.update(0.016)
        
        # Arcade state should be synced for rendering
        assert engine.game_state.arcade_mode is not None
        assert engine.game_state.arcade_mode.active is True
        assert engine.game_state.arcade_mode.time_remaining == engine.arcade_manager.time_remaining

    def test_arcade_state_not_synced_when_inactive(self, game_engine_with_arcade):
        """Test that arcade state is None when arcade mode is not active."""
        engine = game_engine_with_arcade
        
        # Cancel arcade mode
        engine.arcade_manager.cancel_session()
        
        # Update game
        engine.update(0.016)
        
        # Arcade state should be None
        assert engine.game_state.arcade_mode is None

    def test_arcade_timer_only_updates_in_playing_not_lobby(self, game_engine_with_arcade):
        """Test that arcade timer only updates during PLAYING status, not LOBBY."""
        engine = game_engine_with_arcade
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Set to LOBBY status
        engine.game_state.status = GameStatus.LOBBY
        
        # Update game
        engine.update(1.0)
        
        # Timer should NOT have changed (arcade only updates in PLAYING)
        assert engine.arcade_manager.time_remaining == initial_time

    def test_arcade_timer_only_updates_in_playing_not_boss_battle(self, game_engine_with_arcade):
        """Test that arcade timer only updates during PLAYING status, not BOSS_BATTLE."""
        engine = game_engine_with_arcade
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Set to BOSS_BATTLE status
        engine.game_state.status = GameStatus.BOSS_BATTLE
        
        # Update game
        engine.update(1.0)
        
        # Timer should NOT have changed (arcade only updates in PLAYING)
        assert engine.arcade_manager.time_remaining == initial_time


class TestArcadeTimerPauseIntegration:
    """Integration tests for arcade timer pause with pause menu."""

    def test_pause_menu_pauses_arcade_timer(self, game_engine_with_arcade):
        """Test that opening pause menu pauses arcade timer."""
        engine = game_engine_with_arcade
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Show pause menu (sets status to PAUSED)
        engine._show_pause_menu()
        
        assert engine.game_state.status == GameStatus.PAUSED
        
        # Update game
        engine.update(2.0)
        
        # Timer should not have changed
        assert engine.arcade_manager.time_remaining == initial_time

    def test_resume_from_pause_menu_resumes_arcade_timer(self, game_engine_with_arcade):
        """Test that resuming from pause menu resumes arcade timer."""
        engine = game_engine_with_arcade
        
        # Show pause menu
        engine._show_pause_menu()
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Resume game (select "Return to Game" option)
        engine.pause_menu_controller.selected_index = 0
        action = engine.pause_menu_controller.select()
        
        # Execute the action
        from pause_menu_controller import PauseMenuAction
        if action == PauseMenuAction.RESUME:
            engine.game_state.status = engine.game_state.previous_status
        
        assert engine.game_state.status == GameStatus.PLAYING
        
        # Update game
        engine.update(1.0)
        
        # Timer should have decreased
        assert engine.arcade_manager.time_remaining < initial_time

    def test_arcade_timer_visible_during_pause(self, game_engine_with_arcade):
        """Test that arcade timer remains visible during pause (for rendering)."""
        engine = game_engine_with_arcade
        
        # Pause the game
        engine.game_state.status = GameStatus.PAUSED
        
        # Update game
        engine.update(0.016)
        
        # Arcade state should be synced for rendering
        assert engine.game_state.arcade_mode is not None
        assert engine.game_state.arcade_mode.time_remaining > 0


class TestArcadeTimerPauseEdgeCases:
    """Edge case tests for arcade timer pause behavior."""

    def test_pause_during_countdown_phase(self, mock_pygame, mock_api_client):
        """Test pausing during countdown phase (before timer starts)."""
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
        
        # Start arcade mode (in countdown)
        engine.arcade_manager.start_session()
        engine.game_state.status = GameStatus.PLAYING
        
        assert engine.arcade_manager.in_countdown is True
        initial_countdown = engine.arcade_manager.countdown_time
        
        # Pause during countdown
        engine.game_state.status = GameStatus.PAUSED
        engine.update(1.0)
        
        # Countdown should NOT have changed
        assert engine.arcade_manager.countdown_time == initial_countdown

    def test_pause_at_end_of_timer(self, game_engine_with_arcade):
        """Test pausing when timer is about to expire."""
        engine = game_engine_with_arcade
        
        # Set timer to almost expired
        engine.arcade_manager.time_remaining = 0.5
        
        # Pause
        engine.game_state.status = GameStatus.PAUSED
        engine.update(1.0)
        
        # Timer should not have expired
        assert engine.arcade_manager.time_remaining == 0.5
        assert engine.arcade_manager.is_active()

    def test_multiple_pause_resume_cycles(self, game_engine_with_arcade):
        """Test multiple pause/resume cycles maintain timer accuracy."""
        engine = game_engine_with_arcade
        
        initial_time = engine.arcade_manager.time_remaining
        
        # Pause for 1 second
        engine.game_state.status = GameStatus.PAUSED
        engine.update(1.0)
        
        # Resume for 0.5 seconds
        engine.game_state.status = GameStatus.PLAYING
        engine.update(0.5)
        
        # Pause for 2 seconds
        engine.game_state.status = GameStatus.PAUSED
        engine.update(2.0)
        
        # Resume for 1.5 seconds
        engine.game_state.status = GameStatus.PLAYING
        engine.update(1.5)
        
        # Total playing time: 0.5 + 1.5 = 2.0 seconds
        # Timer should have decreased by 2.0 seconds
        assert engine.arcade_manager.time_remaining == pytest.approx(initial_time - 2.0, abs=0.01)

    def test_arcade_state_synced_when_session_ends_during_pause(self, game_engine_with_arcade):
        """Test that arcade state is synced even when session ends (shows final stats)."""
        engine = game_engine_with_arcade
        
        # Set timer to almost expired
        engine.arcade_manager.time_remaining = 0.1
        
        # Update to expire timer
        engine.update(0.2)
        
        # Session should have ended
        assert engine.arcade_manager.is_active() is False
        
        # Pause the game
        engine.game_state.status = GameStatus.PAUSED
        engine.update(0.016)
        
        # Arcade state should still be synced (shows final stats with active=False)
        # This allows the results screen to display properly
        assert engine.game_state.arcade_mode is not None
        assert engine.game_state.arcade_mode.active is False
        assert engine.game_state.arcade_mode.time_remaining == 0.0


class TestArcadeTimerPauseWithEliminations:
    """Tests for arcade timer pause with elimination tracking."""

    def test_eliminations_tracked_during_pause(self, game_engine_with_arcade):
        """Test that elimination count is preserved during pause."""
        engine = game_engine_with_arcade
        
        # Add some eliminations
        zombie = Zombie("z1", "Z1", Vector2(100, 100), "123456789012")
        engine.arcade_manager.queue_elimination(zombie)
        
        assert engine.arcade_manager.eliminations_count == 1
        
        # Pause
        engine.game_state.status = GameStatus.PAUSED
        engine.update(1.0)
        
        # Elimination count should be preserved
        assert engine.arcade_manager.eliminations_count == 1

    def test_combo_preserved_during_pause(self, game_engine_with_arcade):
        """Test that combo is preserved during pause."""
        engine = game_engine_with_arcade
        
        # Build a combo
        for i in range(5):
            zombie = Zombie(f"z{i}", f"Z{i}", Vector2(100 + i * 50, 100), "123456789012")
            engine.arcade_manager.queue_elimination(zombie)
        
        combo_before = engine.arcade_manager.get_combo_count()
        assert combo_before == 5
        
        # Pause (combo should not decay during pause)
        engine.game_state.status = GameStatus.PAUSED
        engine.update(1.0)
        
        # Combo should be preserved (not decayed)
        # Note: This test documents current behavior - combo DOES decay during pause
        # because combo_tracker.update() is called in arcade_manager.update()
        # which is NOT called during pause
        combo_after = engine.arcade_manager.get_combo_count()
        assert combo_after == combo_before  # Combo preserved during pause


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
