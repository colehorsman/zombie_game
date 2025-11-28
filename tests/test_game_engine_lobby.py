"""Tests for GameEngine lobby initialization."""

import pytest
from unittest.mock import Mock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from game_engine import GameEngine
from models import GameStatus, Vector2
from zombie import Zombie


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
    return client


class TestLobbyInitialization:
    """Tests for lobby mode initialization."""

    def test_player_spawns_at_center_of_map(self, mock_pygame, mock_api_client):
        """Test that player spawns at center of map in lobby mode."""
        # Create game engine with map enabled (lobby mode)
        zombies = []
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=zombies,
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={},
            third_party_data={},
        )

        # Verify player spawned at center
        expected_x = engine.game_map.map_width // 2
        expected_y = engine.game_map.map_height // 2

        assert engine.player.position.x == expected_x
        assert engine.player.position.y == expected_y

        # Verify landing zone is also at center
        assert engine.landing_zone.x == expected_x
        assert engine.landing_zone.y == expected_y

    def test_lobby_starts_in_lobby_status(self, mock_pygame, mock_api_client):
        """Test that game starts in LOBBY status."""
        zombies = []
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=zombies,
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={},
            third_party_data={},
        )

        assert engine.game_state.status == GameStatus.LOBBY

    def test_zombies_visible_in_lobby(self, mock_pygame, mock_api_client):
        """Test that zombies are visible in lobby mode."""
        # Create some test zombies
        zombies = [
            Zombie(
                identity_id=f"zombie-{i}",
                identity_name=f"TestZombie{i}",
                position=Vector2(100 + i * 50, 100),
                account="577945324761",
            )
            for i in range(5)
        ]

        engine = GameEngine(
            api_client=mock_api_client,
            zombies=zombies,
            screen_width=1280,
            screen_height=720,
            use_map=True,
            account_data={"577945324761": 5},
            third_party_data={},
        )

        # Verify zombies are visible (not hidden)
        assert len(engine.zombies) == 5
        for zombie in engine.zombies:
            assert zombie.is_hidden is False

    def test_classic_mode_uses_different_spawn(self, mock_pygame, mock_api_client):
        """Test that classic mode (no map) uses different spawn position."""
        zombies = []
        engine = GameEngine(
            api_client=mock_api_client,
            zombies=zombies,
            screen_width=1280,
            screen_height=720,
            use_map=False,  # Classic mode
            account_data={},
            third_party_data={},
        )

        # Classic mode spawns at left side of screen
        assert engine.player.position.x == 50
        assert engine.player.position.y == 720 // 2 - 16

        # Landing zone is at screen center in classic mode
        assert engine.landing_zone.x == 1280 // 2
        assert engine.landing_zone.y == 720 // 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
