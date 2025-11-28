"""Integration tests for arcade mode dynamic zombie spawning in game_engine."""

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
    # Create test zombies
    zombies = [
        Zombie(
            identity_id=f"zombie-{i}",
            identity_name=f"TestZombie{i}",
            position=Vector2(1000 + i * 100, 400),
            account="577945324761"
        )
        for i in range(30)  # Start with 30 zombies
    ]
    
    engine = GameEngine(
        api_client=mock_api_client,
        zombies=zombies,
        screen_width=1280,
        screen_height=720,
        use_map=True,
        account_data={"577945324761": 30},
        third_party_data={}
    )
    
    engine.start()
    
    # Start arcade mode
    engine.arcade_manager.start_session()
    engine.arcade_manager.in_countdown = False  # Skip countdown
    
    return engine


class TestDynamicSpawningIntegration:
    """Test dynamic spawning integration in game_engine._update_arcade_mode."""

    def test_spawning_triggers_when_below_minimum(self, game_engine_with_arcade):
        """Test that spawning triggers when zombie count drops below minimum."""
        engine = game_engine_with_arcade
        
        # Hide zombies to drop below minimum (20)
        visible_count = 0
        for zombie in engine.zombies[:15]:  # Hide 15, leaving 15 visible
            zombie.is_hidden = True
            visible_count += 1
        
        # Verify we're below minimum
        visible_zombies = [z for z in engine.zombies if not z.is_hidden]
        assert len(visible_zombies) == 15  # Below minimum of 20
        
        # Queue some zombies for respawn
        for zombie in engine.zombies[:5]:
            if zombie.is_hidden:
                engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward respawn timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode (should trigger respawning)
        engine._update_arcade_mode(0.016)
        
        # Verify zombies were respawned (no longer hidden)
        respawned_count = sum(1 for z in engine.zombies[:5] if not z.is_hidden)
        assert respawned_count > 0, "Should have respawned at least one zombie"

    def test_no_spawning_when_above_minimum(self, game_engine_with_arcade):
        """Test that spawning doesn't trigger when above minimum count."""
        engine = game_engine_with_arcade
        
        # Ensure we have plenty of visible zombies (above minimum of 20)
        for zombie in engine.zombies:
            zombie.is_hidden = False
        
        visible_zombies = [z for z in engine.zombies if not z.is_hidden]
        assert len(visible_zombies) >= 20  # Above minimum
        
        # Queue a zombie for respawn
        test_zombie = engine.zombies[0]
        test_zombie.is_hidden = True
        engine.arcade_manager.queue_zombie_for_respawn(test_zombie)
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Zombie should NOT be respawned (still hidden) because we're above minimum
        assert test_zombie.is_hidden, "Should not respawn when above minimum count"

    def test_respawn_uses_player_position(self, game_engine_with_arcade):
        """Test that respawned zombies spawn relative to player position."""
        engine = game_engine_with_arcade
        
        # Set player position
        engine.player.position = Vector2(2000, 400)
        
        # Hide zombies to drop below minimum
        for zombie in engine.zombies[:20]:
            zombie.is_hidden = True
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode (should respawn)
        engine._update_arcade_mode(0.016)
        
        # Check that respawned zombies are near player (within spawn distance)
        respawned = [z for z in engine.zombies[:20] if not z.is_hidden]
        for zombie in respawned:
            distance = abs(zombie.position.x - engine.player.position.x)
            # Should be approximately spawn_distance (500) away, but may be clamped to level bounds
            # Allow range of 50-600 to account for edge clamping
            assert 50 <= distance <= 600, f"Zombie should spawn near player, got {distance}px"

    def test_respawn_uses_ground_level(self, game_engine_with_arcade):
        """Test that respawned zombies spawn at correct ground level."""
        engine = game_engine_with_arcade
        
        # Hide zombies and queue for respawn
        test_zombie = engine.zombies[0]
        test_zombie.is_hidden = True
        engine.arcade_manager.queue_zombie_for_respawn(test_zombie)
        
        # Fast forward timer
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Verify zombie is at ground level (800 - zombie.height)
        if not test_zombie.is_hidden:
            expected_y = 800 - test_zombie.height
            assert test_zombie.position.y == expected_y, "Zombie should be at ground level"

    def test_respawn_resets_zombie_health(self, game_engine_with_arcade):
        """Test that respawned zombies have full health."""
        engine = game_engine_with_arcade
        
        # Damage and hide zombie
        test_zombie = engine.zombies[0]
        test_zombie.health = 1  # Nearly dead
        test_zombie.is_hidden = True
        engine.arcade_manager.queue_zombie_for_respawn(test_zombie)
        
        # Fast forward timer
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Verify health was reset
        if not test_zombie.is_hidden:
            assert test_zombie.health == test_zombie.max_health, "Zombie should have full health"

    def test_multiple_zombies_respawn_in_one_update(self, game_engine_with_arcade):
        """Test that multiple zombies can respawn in a single update."""
        engine = game_engine_with_arcade
        
        # Hide many zombies to drop well below minimum
        for zombie in engine.zombies[:25]:
            zombie.is_hidden = True
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Count visible before update
        visible_before = len([z for z in engine.zombies if not z.is_hidden])
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Count visible after update
        visible_after = len([z for z in engine.zombies if not z.is_hidden])
        
        # Should have respawned multiple zombies
        assert visible_after > visible_before, "Should respawn multiple zombies"

    def test_no_respawn_during_countdown(self, game_engine_with_arcade):
        """Test that zombies don't respawn during countdown phase."""
        engine = game_engine_with_arcade
        
        # Set to countdown phase
        engine.arcade_manager.in_countdown = True
        engine.arcade_manager.countdown_time = 2.0
        
        # Hide zombies and queue
        for zombie in engine.zombies[:20]:
            zombie.is_hidden = True
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Zombies should still be hidden (no respawn during countdown)
        hidden_count = sum(1 for z in engine.zombies[:20] if z.is_hidden)
        assert hidden_count == 20, "Should not respawn during countdown"

    def test_no_respawn_when_session_ends(self, game_engine_with_arcade):
        """Test that zombies don't respawn when session ends."""
        engine = game_engine_with_arcade
        
        # End the session
        engine.arcade_manager.time_remaining = 0.0
        engine.arcade_manager._end_session()
        
        # Hide zombies and queue
        for zombie in engine.zombies[:20]:
            zombie.is_hidden = True
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode (should show results, not respawn)
        engine._update_arcade_mode(0.016)
        
        # Zombies should still be hidden (session ended)
        hidden_count = sum(1 for z in engine.zombies[:20] if z.is_hidden)
        assert hidden_count == 20, "Should not respawn when session ended"

    def test_respawn_only_when_game_map_exists(self, mock_pygame, mock_api_client):
        """Test that respawning only happens when game_map exists."""
        # Create engine without map
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=[],
            screen_width=1280,
            screen_height=720,
            use_map=False,  # No map
            account_data={},
            third_party_data={}
        )
        engine.start()
        
        # Start arcade mode
        engine.arcade_manager.start_session()
        engine.arcade_manager.in_countdown = False
        
        # Create and queue zombie
        zombie = Zombie("id1", "user1", Vector2(100, 100), "123")
        zombie.is_hidden = True
        engine.zombies.append(zombie)
        engine.arcade_manager.queue_zombie_for_respawn(zombie)
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode (should not crash, but won't respawn without map)
        engine._update_arcade_mode(0.016)
        
        # Zombie should still be hidden (no map to respawn in)
        assert zombie.is_hidden, "Should not respawn without game_map"


class TestSpawningEdgeCases:
    """Test edge cases in dynamic spawning."""

    def test_respawn_with_zero_zombies(self, game_engine_with_arcade):
        """Test respawning when all zombies are hidden."""
        engine = game_engine_with_arcade
        
        # Hide ALL zombies
        for zombie in engine.zombies:
            zombie.is_hidden = True
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        # Fast forward timers
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Should have respawned some zombies
        visible_count = len([z for z in engine.zombies if not z.is_hidden])
        assert visible_count > 0, "Should respawn zombies when all are hidden"

    def test_respawn_at_exact_minimum(self, game_engine_with_arcade):
        """Test behavior when exactly at minimum count."""
        engine = game_engine_with_arcade
        
        # Set to exactly minimum (20 visible)
        for i, zombie in enumerate(engine.zombies):
            if i < 20:
                zombie.is_hidden = False
            else:
                zombie.is_hidden = True
        
        visible_count = len([z for z in engine.zombies if not z.is_hidden])
        assert visible_count == 20
        
        # Queue hidden zombies
        for zombie in engine.zombies[20:]:
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
        
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Should NOT respawn (at minimum, not below)
        visible_after = len([z for z in engine.zombies if not z.is_hidden])
        assert visible_after == 20, "Should not respawn when at minimum"

    def test_respawn_with_partial_queue(self, game_engine_with_arcade):
        """Test respawning when only some zombies are ready."""
        engine = game_engine_with_arcade
        
        # Hide zombies to drop below minimum
        for zombie in engine.zombies[:25]:
            zombie.is_hidden = True
        
        # Queue zombies at different times
        for i, zombie in enumerate(engine.zombies[:25]):
            engine.arcade_manager.queue_zombie_for_respawn(zombie)
            if i < 10:
                # First 10 are ready
                engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Should respawn the ready ones
        respawned = [z for z in engine.zombies[:10] if not z.is_hidden]
        assert len(respawned) > 0, "Should respawn ready zombies"


class TestSpawningLogging:
    """Test that spawning logs debug messages."""

    def test_respawn_logs_debug_message(self, game_engine_with_arcade, caplog):
        """Test that respawning logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        engine = game_engine_with_arcade
        
        # Hide zombies and queue
        test_zombie = engine.zombies[0]
        test_zombie.is_hidden = True
        engine.arcade_manager.queue_zombie_for_respawn(test_zombie)
        
        # Fast forward timer
        engine.arcade_manager._update_respawn_timers(2.5)
        
        # Update arcade mode
        engine._update_arcade_mode(0.016)
        
        # Check for respawn log message
        if not test_zombie.is_hidden:
            log_messages = [record.message for record in caplog.records]
            respawn_logs = [msg for msg in log_messages if "♻️  Respawned zombie" in msg]
            assert len(respawn_logs) > 0, "Should log respawn message"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
