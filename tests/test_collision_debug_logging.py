"""Tests for collision detection debug logging."""

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
from projectile import Projectile


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


class TestCollisionDebugLogging:
    """Tests for collision detection debug logging."""

    def test_debug_logging_with_projectiles_and_zombies(self, game_engine, caplog):
        """Test that debug logging works when projectiles and zombies exist."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a zombie
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_hidden = False
        zombie.is_quarantining = False
        game_engine.zombies = [zombie]
        
        # Create a projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game (this should trigger collision detection with logging)
        game_engine.update(0.016)
        
        # Verify debug logs were created
        log_messages = [record.message for record in caplog.records]
        
        # Should have collision check log
        collision_check_logs = [msg for msg in log_messages if "COLLISION CHECK" in msg]
        assert len(collision_check_logs) > 0, "Should log collision check"
        
        # Should have collision result log
        collision_result_logs = [msg for msg in log_messages if "COLLISION RESULT" in msg]
        assert len(collision_result_logs) > 0, "Should log collision result"

    def test_debug_logging_with_no_projectiles(self, game_engine, caplog):
        """Test that debug logging doesn't crash when no projectiles exist."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a zombie but no projectiles
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_hidden = False
        game_engine.zombies = [zombie]
        game_engine.projectiles = []
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game (should not crash)
        game_engine.update(0.016)
        
        # Should not have collision logs (no projectiles)
        log_messages = [record.message for record in caplog.records]
        collision_logs = [msg for msg in log_messages if "COLLISION CHECK" in msg]
        assert len(collision_logs) == 0, "Should not log when no projectiles"

    def test_debug_logging_with_no_zombies(self, game_engine, caplog):
        """Test that debug logging doesn't crash when no zombies exist."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a projectile but no zombies
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        game_engine.zombies = []
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game (should not crash)
        game_engine.update(0.016)
        
        # Should have collision result log (projectiles exist)
        log_messages = [record.message for record in caplog.records]
        collision_result_logs = [msg for msg in log_messages if "COLLISION RESULT" in msg]
        assert len(collision_result_logs) > 0, "Should log collision result even with no zombies"

    def test_debug_logging_shows_quarantine_flag(self, game_engine, caplog):
        """Test that debug logging shows is_quarantining flag."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create a zombie with is_quarantining=True
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_hidden = False
        zombie.is_quarantining = True  # This is the bug we're debugging
        game_engine.zombies = [zombie]
        
        # Create a projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game
        game_engine.update(0.016)
        
        # Verify is_quarantining flag is logged
        log_messages = [record.message for record in caplog.records]
        quarantine_logs = [msg for msg in log_messages if "is_quarantining=True" in msg]
        assert len(quarantine_logs) > 0, "Should log is_quarantining flag"

    def test_debug_logging_in_boss_battle_mode(self, game_engine, caplog):
        """Test that debug logging doesn't run in boss battle mode."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create zombie and projectile
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_hidden = False
        game_engine.zombies = [zombie]
        
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to boss battle mode
        game_engine.game_state.status = GameStatus.BOSS_BATTLE
        
        # Update game
        game_engine.update(0.016)
        
        # Should not have collision logs (boss battle mode skips zombie collision)
        log_messages = [record.message for record in caplog.records]
        collision_logs = [msg for msg in log_messages if "COLLISION CHECK" in msg]
        assert len(collision_logs) == 0, "Should not log in boss battle mode"


class TestEnhancedCollisionDebugLogging:
    """Tests for enhanced collision debug logging features."""

    def _setup_mock_game_map(self, game_engine, is_on_screen_return=True):
        """Helper to set up a properly mocked game_map."""
        mock_map = Mock()
        if callable(is_on_screen_return):
            mock_map.is_on_screen = Mock(side_effect=is_on_screen_return)
        else:
            mock_map.is_on_screen = Mock(return_value=is_on_screen_return)
        mock_map.resource_nodes = []
        mock_map.doors = []
        mock_map.third_parties = []
        mock_map.tile_size = 32
        mock_map.tiles = []
        mock_map.tiles_wide = 100
        mock_map.tiles_high = 100
        mock_map.tile_map = [[0] * 100 for _ in range(100)]  # Empty map (no walls)
        mock_map.map_width = 3200  # 100 tiles * 32 pixels
        mock_map.map_height = 3200
        game_engine.game_map = mock_map
        game_engine.use_map = True

    def test_debug_logging_always_runs_when_projectiles_exist(self, game_engine, caplog):
        """Test that debug logging runs even when no visible zombies exist."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create projectile but NO zombies
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        game_engine.zombies = []  # No zombies at all
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game
        game_engine.update(0.016)
        
        # Should have collision check log even with no zombies
        log_messages = [record.message for record in caplog.records]
        collision_check_logs = [msg for msg in log_messages if "COLLISION CHECK" in msg]
        assert len(collision_check_logs) > 0, "Should log collision check when projectiles exist"
        
        # Verify log shows 0 visible zombies
        assert any("0 visible zombies" in msg for msg in collision_check_logs)

    def test_debug_logging_shows_filtering_details_when_all_filtered(self, game_engine, caplog):
        """Test that debug logging shows why zombies are filtered out."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Create zombies that will be filtered out (hidden)
        zombie1 = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie1",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie1.is_hidden = True  # Hidden - will be filtered
        
        zombie2 = Zombie(
            identity_id="zombie-2",
            identity_name="TestZombie2",
            position=Vector2(200, 100),
            account="577945324761"
        )
        zombie2.is_hidden = True  # Hidden - will be filtered
        
        game_engine.zombies = [zombie1, zombie2]
        
        # Create projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode with map
        game_engine.game_state.status = GameStatus.PLAYING
        self._setup_mock_game_map(game_engine)
        
        # Update game
        game_engine.update(0.016)
        
        # Should have warning about all zombies filtered out
        log_messages = [record.message for record in caplog.records]
        filter_warnings = [msg for msg in log_messages if "ALL ZOMBIES FILTERED OUT" in msg]
        assert len(filter_warnings) > 0, "Should warn when all zombies are filtered"
        
        # Should show breakdown of why zombies are filtered
        breakdown_logs = [msg for msg in log_messages if "Hidden:" in msg]
        assert len(breakdown_logs) > 0, "Should show breakdown of filtered zombies"
        assert any("Hidden: 2" in msg for msg in breakdown_logs)

    def test_debug_logging_shows_hidden_flag_in_zombie_details(self, game_engine, caplog):
        """Test that debug logging includes is_hidden flag in zombie details."""
        import logging
        caplog.set_level(logging.INFO)
        
        # Create zombie with is_hidden=True
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_hidden = False  # Not hidden so it shows up in visible_zombies
        zombie.is_quarantining = False
        game_engine.zombies = [zombie]
        
        # Create projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Update game
        game_engine.update(0.016)
        
        # Verify is_hidden flag is logged in zombie details
        log_messages = [record.message for record in caplog.records]
        zombie_detail_logs = [msg for msg in log_messages if "Zombie[0]:" in msg]
        assert len(zombie_detail_logs) > 0, "Should log zombie details"
        assert any("is_hidden=False" in msg for msg in zombie_detail_logs)

    def test_debug_logging_counts_offscreen_zombies_separately(self, game_engine, caplog):
        """Test that debug logging distinguishes between hidden and off-screen zombies."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Create mix of hidden and off-screen zombies
        zombie1 = Zombie(
            identity_id="zombie-1",
            identity_name="HiddenZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie1.is_hidden = True  # Hidden
        
        zombie2 = Zombie(
            identity_id="zombie-2",
            identity_name="OffscreenZombie",
            position=Vector2(99999, 100),  # Way off screen
            account="577945324761"
        )
        zombie2.is_hidden = False  # Not hidden, but off-screen
        
        game_engine.zombies = [zombie1, zombie2]
        
        # Create projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode with map
        game_engine.game_state.status = GameStatus.PLAYING
        
        # Mock game_map with is_on_screen that returns False for off-screen zombie
        def is_on_screen_mock(x, y, w, h):
            return x < 10000  # Off-screen zombie at x=99999 returns False
        self._setup_mock_game_map(game_engine, is_on_screen_return=is_on_screen_mock)
        
        # Update game
        game_engine.update(0.016)
        
        # Should show breakdown with both hidden and off-screen counts
        log_messages = [record.message for record in caplog.records]
        breakdown_logs = [msg for msg in log_messages if "Hidden:" in msg and "Off-screen:" in msg]
        assert len(breakdown_logs) > 0, "Should show breakdown of hidden vs off-screen"
        assert any("Hidden: 1" in msg for msg in breakdown_logs)
        assert any("Off-screen: 1" in msg for msg in breakdown_logs)

    def test_debug_logging_no_warning_when_some_zombies_visible(self, game_engine, caplog):
        """Test that no warning is logged when some zombies are visible."""
        import logging
        caplog.set_level(logging.WARNING)
        
        # Create mix of visible and hidden zombies
        zombie1 = Zombie(
            identity_id="zombie-1",
            identity_name="VisibleZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie1.is_hidden = False  # Visible
        
        zombie2 = Zombie(
            identity_id="zombie-2",
            identity_name="HiddenZombie",
            position=Vector2(200, 100),
            account="577945324761"
        )
        zombie2.is_hidden = True  # Hidden
        
        game_engine.zombies = [zombie1, zombie2]
        
        # Create projectile
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        game_engine.projectiles = [projectile]
        
        # Set game to playing mode with map
        game_engine.game_state.status = GameStatus.PLAYING
        self._setup_mock_game_map(game_engine)
        
        # Update game
        game_engine.update(0.016)
        
        # Should NOT have warning about all zombies filtered (some are visible)
        log_messages = [record.message for record in caplog.records]
        filter_warnings = [msg for msg in log_messages if "ALL ZOMBIES FILTERED OUT" in msg]
        assert len(filter_warnings) == 0, "Should not warn when some zombies are visible"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
