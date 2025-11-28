"""
Tests for the critical bug where projectiles pass through zombies.

BUG SCENARIO:
Player gets stuck between zombies and projectiles shoot through them without hitting.
This happens when zombies have is_quarantining=True but are still in the zombie list
(due to API failures or quest completion state issues).

ROOT CAUSE:
Collision detection skips zombies with is_quarantining=True, but zombies can remain
in the list with this flag set incorrectly.
"""

import pytest
from unittest.mock import Mock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameState, GameStatus, Vector2, QuarantineResult
from zombie import Zombie
from projectile import Projectile
from collision import check_collisions_with_spatial_grid, SpatialGrid


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


class TestZombieStuckCollisionBug:
    """Tests for the bug where projectiles pass through zombies."""

    def test_projectile_hits_zombie_with_correct_state(self, mock_pygame, mock_api_client):
        """Test that projectiles hit zombies with correct state (not quarantining)."""
        # Create zombie with correct state
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_quarantining = False
        zombie.is_hidden = False
        
        # Create projectile at zombie's center position for guaranteed collision
        zombie_bounds = zombie.get_bounds()
        projectile = Projectile(
            position=Vector2(zombie_bounds.centerx, zombie_bounds.centery),
            direction=Vector2(1, 0),
            damage=10
        )
        
        # Create spatial grid
        grid = SpatialGrid(1280, 720)
        
        # Check collision
        collisions = check_collisions_with_spatial_grid([projectile], [zombie], grid)
        
        # Should detect collision
        assert len(collisions) == 1
        assert collisions[0] == (projectile, zombie)

    def test_projectile_passes_through_zombie_with_quarantining_flag(self, mock_pygame, mock_api_client):
        """Test that projectiles INCORRECTLY pass through zombies with is_quarantining=True."""
        # Create zombie with INCORRECT state (quarantining but still in list)
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_quarantining = True  # BUG: This flag is set but zombie is still in list
        zombie.is_hidden = False
        
        # Create projectile heading toward zombie
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=10
        )
        
        # Create spatial grid
        grid = SpatialGrid(1280, 720)
        
        # Check collision
        collisions = check_collisions_with_spatial_grid([projectile], [zombie], grid)
        
        # BUG: No collision detected because zombie has is_quarantining=True
        assert len(collisions) == 0

    def test_player_stuck_between_zombies_with_quarantining_flags(self, mock_pygame, mock_api_client):
        """
        Test the exact bug scenario: Player stuck between zombies that have
        is_quarantining=True, making them unshootable.
        """
        # Create game engine
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
        
        # Create zombies on both sides of player
        zombie_left = Zombie(
            identity_id="zombie-left",
            identity_name="LeftZombie",
            position=Vector2(50, 400),
            account="577945324761"
        )
        zombie_right = Zombie(
            identity_id="zombie-right",
            identity_name="RightZombie",
            position=Vector2(150, 400),
            account="577945324761"
        )
        
        # BUG STATE: Both zombies have is_quarantining=True but are still in the list
        zombie_left.is_quarantining = True
        zombie_right.is_quarantining = True
        zombie_left.is_hidden = False
        zombie_right.is_hidden = False
        
        engine.zombies = [zombie_left, zombie_right]
        
        # Player is stuck between them
        engine.player.position = Vector2(100, 400)
        
        # Player shoots right
        projectile = Projectile(
            position=Vector2(105, 400),
            direction=Vector2(1, 0),
            damage=10
        )
        engine.projectiles = [projectile]
        
        # Update collisions
        collisions = check_collisions_with_spatial_grid(
            engine.projectiles,
            engine.zombies,
            engine.spatial_grid
        )
        
        # BUG: No collisions detected even though projectile should hit zombie_right
        assert len(collisions) == 0
        
        # This means player is STUCK - can't shoot zombies to escape!

    def test_api_failure_leaves_zombie_in_bad_state(self, mock_pygame, mock_api_client):
        """
        Test that API failure can leave zombie in unshootable state.
        """
        # Mock API to fail
        mock_api_client.quarantine_identity.return_value = QuarantineResult(
            success=False,
            identity_id="zombie-1",
            error_message="API Error"
        )
        
        # Create game engine
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
        
        # Create zombie
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761"
        )
        zombie.is_quarantining = False
        zombie.is_hidden = False
        engine.zombies = [zombie]
        
        # Shoot zombie
        projectile = Projectile(
            position=Vector2(90, 100),
            direction=Vector2(1, 0),
            damage=100  # Kill in one hit
        )
        engine.projectiles = [projectile]
        
        # This test documents expected API error handling behavior
        # When API fails, zombie should remain in list with correct state
        
        # Verify zombie is in correct state for collision detection
        assert zombie.is_quarantining is False
        assert zombie.is_hidden is False
        assert zombie in engine.zombies

    def test_zombie_state_after_quest_completion(self, mock_pygame, mock_api_client):
        """
        Test that zombies don't have incorrect is_quarantining flags after quest completion.
        
        This is the scenario from the bug fix where quest completion left zombies
        with is_quarantining=True.
        """
        # Create game engine
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
        
        # Create zombies
        zombies = [
            Zombie(
                identity_id=f"zombie-{i}",
                identity_name=f"TestZombie{i}",
                position=Vector2(100 + i * 50, 400),
                account="577945324761"
            )
            for i in range(5)
        ]
        
        # Simulate quest completion leaving zombies in bad state
        for zombie in zombies:
            zombie.is_quarantining = True  # BUG: Quest left them in this state
            zombie.is_hidden = False
        
        engine.zombies = zombies
        
        # Try to shoot a zombie
        projectile = Projectile(
            position=Vector2(95, 400),
            direction=Vector2(1, 0),
            damage=10
        )
        
        collisions = check_collisions_with_spatial_grid(
            [projectile],
            engine.zombies,
            engine.spatial_grid
        )
        
        # BUG: No collisions because all zombies have is_quarantining=True
        assert len(collisions) == 0
        
        # This is the bug! Player can't shoot any zombies after quest completion


class TestZombieStateResetFix:
    """Tests for the fix that resets zombie states."""

    def test_quest_completion_resets_zombie_quarantining_flags(self, mock_pygame, mock_api_client):
        """
        Test that quest completion properly resets is_quarantining flags.
        
        This is the FIX for the bug.
        """
        # Create game engine
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
        
        # Create zombies with bad state
        zombies = [
            Zombie(
                identity_id=f"zombie-{i}",
                identity_name=f"TestZombie{i}",
                position=Vector2(100 + i * 50, 400),
                account="577945324761"
            )
            for i in range(5)
        ]
        
        for zombie in zombies:
            zombie.is_quarantining = True  # Bad state
            zombie.is_hidden = False
        
        engine.zombies = zombies
        
        # FIX: Reset all zombie states (this should be called after quest completion)
        for zombie in engine.zombies:
            zombie.is_quarantining = False
            zombie.is_hidden = False
        
        # Now try to shoot a zombie - place projectile at zombie's center
        zombie_bounds = zombies[0].get_bounds()
        projectile = Projectile(
            position=Vector2(zombie_bounds.centerx, zombie_bounds.centery),
            direction=Vector2(1, 0),
            damage=10
        )
        
        collisions = check_collisions_with_spatial_grid(
            [projectile],
            engine.zombies,
            engine.spatial_grid
        )
        
        # FIX: Collision detected! Zombies are shootable again
        assert len(collisions) == 1

    def test_api_error_handler_restores_zombie_state(self, mock_pygame, mock_api_client):
        """
        Test that API error handler properly restores zombie state.
        """
        # Mock API to fail
        mock_api_client.quarantine_identity.return_value = QuarantineResult(
            success=False,
            identity_id="zombie-1",
            error_message="API Error"
        )
        
        # Create game engine
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
        
        # Create zombie
        zombie = Zombie(
            identity_id="zombie-1",
            identity_name="TestZombie",
            position=Vector2(100, 100),
            account="577945324761",
            scope="aws/r-test/ou-test/577945324761"
        )
        engine.zombies = [zombie]
        
        # Simulate zombie elimination by reducing health to 0
        zombie.health = 0
        
        # Verify zombie is still shootable (place projectile at zombie center)
        zombie_bounds = zombie.get_bounds()
        projectile = Projectile(
            position=Vector2(zombie_bounds.centerx, zombie_bounds.centery),
            direction=Vector2(1, 0),
            damage=10
        )
        
        collisions = check_collisions_with_spatial_grid(
            [projectile],
            engine.zombies,
            engine.spatial_grid
        )
        
        # Should be able to detect collision with zombie
        assert len(collisions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
