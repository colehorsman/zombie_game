"""Tests for arcade mode dynamic zombie spawning."""

import pytest
from unittest.mock import Mock

from src.arcade_mode import ArcadeModeManager
from src.zombie import Zombie
from src.models import Vector2


@pytest.fixture
def arcade_manager():
    """Create an arcade mode manager for testing."""
    return ArcadeModeManager()


@pytest.fixture
def sample_zombie():
    """Create a sample zombie for testing."""
    return Zombie(
        identity_id="test-zombie-1",
        identity_name="test-user-1",
        position=Vector2(100, 100),
        account="123456789012",
    )


class TestInitialZombieCount:
    """Test initial zombie count calculation."""

    def test_minimum_zombie_count(self, arcade_manager):
        """Should enforce minimum of 20 zombies."""
        # Small level (500 pixels = 5 zombies by density)
        count = arcade_manager.calculate_initial_zombie_count(500)
        assert count == 20  # Minimum enforced

    def test_density_based_count(self, arcade_manager):
        """Should calculate 1 zombie per 100 pixels."""
        # Large level (5000 pixels = 50 zombies)
        count = arcade_manager.calculate_initial_zombie_count(5000)
        assert count == 50

    def test_exact_density(self, arcade_manager):
        """Should handle exact multiples of 100."""
        count = arcade_manager.calculate_initial_zombie_count(2000)
        assert count == 20  # 2000/100 = 20

    def test_very_large_level(self, arcade_manager):
        """Should scale with very large levels."""
        # 10,000 pixels = 100 zombies
        count = arcade_manager.calculate_initial_zombie_count(10000)
        assert count == 100


class TestRespawnQueue:
    """Test zombie respawn queue management."""

    def test_queue_zombie_for_respawn(self, arcade_manager, sample_zombie):
        """Should queue zombie with 2-second timer."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        assert sample_zombie in arcade_manager.respawn_queue
        assert sample_zombie.identity_id in arcade_manager.respawn_timers
        assert arcade_manager.respawn_timers[sample_zombie.identity_id] == 2.0

    def test_no_queue_during_countdown(self, arcade_manager, sample_zombie):
        """Should not queue zombies during countdown."""
        arcade_manager.active = True
        arcade_manager.in_countdown = True

        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        assert sample_zombie not in arcade_manager.respawn_queue
        assert sample_zombie.identity_id not in arcade_manager.respawn_timers

    def test_no_queue_when_inactive(self, arcade_manager, sample_zombie):
        """Should not queue zombies when arcade mode inactive."""
        arcade_manager.active = False

        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        assert sample_zombie not in arcade_manager.respawn_queue

    def test_no_duplicate_queue(self, arcade_manager, sample_zombie):
        """Should not queue same zombie twice."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        arcade_manager.queue_zombie_for_respawn(sample_zombie)
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        # Should only be queued once
        assert arcade_manager.respawn_queue.count(sample_zombie) == 1


class TestRespawnTimers:
    """Test respawn timer updates."""

    def test_timer_countdown(self, arcade_manager, sample_zombie):
        """Should countdown respawn timer."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        # Update for 1 second
        arcade_manager._update_respawn_timers(1.0)

        assert arcade_manager.respawn_timers[sample_zombie.identity_id] == 1.0

    def test_timer_expiration(self, arcade_manager, sample_zombie):
        """Should remove timer when it expires."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        # Update for 2.5 seconds (past expiration)
        arcade_manager._update_respawn_timers(2.5)

        assert sample_zombie.identity_id not in arcade_manager.respawn_timers

    def test_multiple_timers(self, arcade_manager):
        """Should handle multiple zombie timers."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        zombie1 = Zombie("id1", "user1", Vector2(100, 100), "123")
        zombie2 = Zombie("id2", "user2", Vector2(200, 100), "123")

        arcade_manager.queue_zombie_for_respawn(zombie1)
        arcade_manager.queue_zombie_for_respawn(zombie2)

        # Update for 1 second
        arcade_manager._update_respawn_timers(1.0)

        assert arcade_manager.respawn_timers["id1"] == 1.0
        assert arcade_manager.respawn_timers["id2"] == 1.0


class TestReadyToRespawn:
    """Test getting zombies ready to respawn."""

    def test_get_ready_zombies(self, arcade_manager, sample_zombie):
        """Should return zombies with expired timers."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        # Expire the timer
        arcade_manager._update_respawn_timers(2.5)

        ready = arcade_manager.get_zombies_ready_to_respawn()

        assert sample_zombie in ready
        assert sample_zombie not in arcade_manager.respawn_queue

    def test_no_ready_zombies(self, arcade_manager, sample_zombie):
        """Should return empty list when no zombies ready."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        # Timer still active
        arcade_manager._update_respawn_timers(1.0)

        ready = arcade_manager.get_zombies_ready_to_respawn()

        assert len(ready) == 0
        assert sample_zombie in arcade_manager.respawn_queue

    def test_partial_ready(self, arcade_manager):
        """Should return only zombies with expired timers."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        zombie1 = Zombie("id1", "user1", Vector2(100, 100), "123")
        zombie2 = Zombie("id2", "user2", Vector2(200, 100), "123")

        arcade_manager.queue_zombie_for_respawn(zombie1)
        arcade_manager._update_respawn_timers(1.0)  # zombie1 at 1.0s remaining
        arcade_manager.queue_zombie_for_respawn(zombie2)  # zombie2 at 2.0s

        # Expire zombie1 only
        arcade_manager._update_respawn_timers(1.5)

        ready = arcade_manager.get_zombies_ready_to_respawn()

        assert zombie1 in ready
        assert zombie2 not in ready


class TestZombieRespawn:
    """Test zombie respawn positioning."""

    def test_respawn_left_of_player(self, arcade_manager, sample_zombie):
        """Should respawn zombie 500 pixels left of player."""
        player_pos = Vector2(1000, 300)
        level_width = 5000
        ground_y = 500

        # Mock random to always choose left
        import random

        random.choice = lambda x: True  # Always spawn left

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should be 500 pixels left
        assert sample_zombie.position.x == 500  # 1000 - 500

    def test_respawn_right_of_player(self, arcade_manager, sample_zombie):
        """Should respawn zombie 500 pixels right of player."""
        player_pos = Vector2(1000, 300)
        level_width = 5000
        ground_y = 500

        # Mock random to always choose right
        import random

        random.choice = lambda x: False  # Always spawn right

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should be 500 pixels right
        assert sample_zombie.position.x == 1500  # 1000 + 500

    def test_respawn_clamp_left_edge(self, arcade_manager, sample_zombie):
        """Should clamp spawn position to left edge."""
        player_pos = Vector2(200, 300)  # Near left edge
        level_width = 5000
        ground_y = 500

        # Mock random to spawn left
        import random

        random.choice = lambda x: True

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should clamp to minimum 50
        assert sample_zombie.position.x >= 50

    def test_respawn_clamp_right_edge(self, arcade_manager, sample_zombie):
        """Should clamp spawn position to right edge."""
        player_pos = Vector2(4800, 300)  # Near right edge
        level_width = 5000
        ground_y = 500

        # Mock random to spawn right
        import random

        random.choice = lambda x: False

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should clamp to maximum (level_width - 50)
        assert sample_zombie.position.x <= 4950

    def test_respawn_resets_zombie_state(self, arcade_manager, sample_zombie):
        """Should reset zombie health and state."""
        # Damage the zombie
        sample_zombie.health = 1
        sample_zombie.is_flashing = True
        sample_zombie.flash_timer = 0.5
        sample_zombie.velocity = Vector2(100, 200)
        sample_zombie.is_hidden = True

        player_pos = Vector2(1000, 300)
        level_width = 5000
        ground_y = 500

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should reset state
        assert sample_zombie.health == sample_zombie.max_health
        assert not sample_zombie.is_flashing
        assert sample_zombie.flash_timer == 0.0
        assert sample_zombie.velocity.x == 0
        assert sample_zombie.velocity.y == 0
        assert sample_zombie.on_ground
        assert not sample_zombie.is_hidden

    def test_respawn_ground_position(self, arcade_manager, sample_zombie):
        """Should position zombie on ground."""
        player_pos = Vector2(1000, 300)
        level_width = 5000
        ground_y = 500

        arcade_manager.respawn_zombie(sample_zombie, player_pos, level_width, ground_y)

        # Should be on ground (ground_y - zombie height)
        expected_y = ground_y - sample_zombie.height
        assert sample_zombie.position.y == expected_y


class TestShouldRespawn:
    """Test respawn trigger logic."""

    def test_should_respawn_below_minimum(self, arcade_manager):
        """Should respawn when below minimum count."""
        assert arcade_manager.should_respawn_zombies(15)  # Below 20

    def test_should_not_respawn_at_minimum(self, arcade_manager):
        """Should not respawn at minimum count."""
        assert not arcade_manager.should_respawn_zombies(20)

    def test_should_not_respawn_above_minimum(self, arcade_manager):
        """Should not respawn above minimum count."""
        assert not arcade_manager.should_respawn_zombies(50)

    def test_should_respawn_at_zero(self, arcade_manager):
        """Should respawn when no zombies remain."""
        assert arcade_manager.should_respawn_zombies(0)


class TestSessionReset:
    """Test that spawning state resets on session start."""

    def test_reset_respawn_queue(self, arcade_manager, sample_zombie):
        """Should clear respawn queue on session start."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False
        arcade_manager.queue_zombie_for_respawn(sample_zombie)

        arcade_manager.start_session()

        assert len(arcade_manager.respawn_queue) == 0
        assert len(arcade_manager.respawn_timers) == 0

    def test_reset_with_multiple_zombies(self, arcade_manager):
        """Should clear all queued zombies on session start."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        for i in range(5):
            zombie = Zombie(f"id{i}", f"user{i}", Vector2(100 * i, 100), "123")
            arcade_manager.queue_zombie_for_respawn(zombie)

        arcade_manager.start_session()

        assert len(arcade_manager.respawn_queue) == 0
        assert len(arcade_manager.respawn_timers) == 0


class TestIntegrationScenario:
    """Test complete spawning workflow."""

    def test_full_respawn_cycle(self, arcade_manager, sample_zombie):
        """Test complete cycle: queue → wait → respawn."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        # 1. Queue zombie for respawn
        arcade_manager.queue_zombie_for_respawn(sample_zombie)
        assert sample_zombie in arcade_manager.respawn_queue

        # 2. Wait 1 second (not ready yet)
        arcade_manager._update_respawn_timers(1.0)
        ready = arcade_manager.get_zombies_ready_to_respawn()
        assert len(ready) == 0

        # 3. Wait another 1.5 seconds (now ready)
        arcade_manager._update_respawn_timers(1.5)
        ready = arcade_manager.get_zombies_ready_to_respawn()
        assert sample_zombie in ready

        # 4. Respawn the zombie
        player_pos = Vector2(1000, 300)
        arcade_manager.respawn_zombie(sample_zombie, player_pos, 5000, 500)
        assert sample_zombie.health == sample_zombie.max_health

    def test_continuous_respawning(self, arcade_manager):
        """Test multiple zombies respawning continuously."""
        arcade_manager.active = True
        arcade_manager.in_countdown = False

        zombies = [
            Zombie(f"id{i}", f"user{i}", Vector2(100 * i, 100), "123")
            for i in range(10)
        ]

        # Queue all zombies at different times
        for i, zombie in enumerate(zombies):
            arcade_manager.queue_zombie_for_respawn(zombie)
            arcade_manager._update_respawn_timers(0.5)  # Stagger by 0.5s

        # Fast forward 3 seconds (all should be ready)
        arcade_manager._update_respawn_timers(3.0)

        ready = arcade_manager.get_zombies_ready_to_respawn()
        assert len(ready) == 10
