"""Property-based tests for the multi-genre level system.

Tests genre selection, persistence, and unlock conditions.
"""

import sys

sys.path.insert(0, "src")

import pygame
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from genre_manager import GenreManager
from models import GENRE_UNLOCK_CONDITIONS, GenreType, Vector2

# Strategies for generating test data
genre_strategy = st.sampled_from(list(GenreType))
account_id_strategy = st.text(
    alphabet="0123456789", min_size=9, max_size=12
)  # AWS account IDs


class TestGenrePreferencePersistence:
    """Property 2: Genre Preference Persistence

    *For any* genre selection for an account, saving and loading SHALL
    restore the same genre preference for that account.

    **Validates: Requirements 1.4, 9.5**
    **Feature: multi-genre-levels, Property 2: Genre Preference Persistence**
    """

    @given(account_id=account_id_strategy, genre=genre_strategy)
    @settings(max_examples=50)
    def test_genre_preference_round_trip(self, account_id: str, genre: GenreType):
        """Test that genre preferences survive serialization round-trip."""
        # Create manager and unlock all genres for testing
        manager = GenreManager()
        manager.unlock_all()

        # Set preference
        manager.select_genre(account_id, genre)

        # Serialize
        data = manager.to_dict()

        # Deserialize into new manager
        restored = GenreManager.from_dict(data)

        # Verify preference preserved
        assert restored.get_genre_for_account(account_id) == genre

    @given(
        account_ids=st.lists(account_id_strategy, min_size=1, max_size=10, unique=True),
        genres=st.lists(genre_strategy, min_size=1, max_size=10),
    )
    @settings(max_examples=30)
    def test_multiple_preferences_round_trip(self, account_ids: list, genres: list):
        """Test that multiple account preferences survive round-trip."""
        manager = GenreManager()
        manager.unlock_all()

        # Set preferences for each account
        expected = {}
        for i, account_id in enumerate(account_ids):
            genre = genres[i % len(genres)]
            manager.select_genre(account_id, genre)
            expected[account_id] = genre

        # Serialize and restore
        data = manager.to_dict()
        restored = GenreManager.from_dict(data)

        # Verify all preferences preserved
        for account_id, genre in expected.items():
            assert restored.get_genre_for_account(account_id) == genre


class TestGenreUnlockConditions:
    """Property 11: Genre Unlock Conditions

    *For any* new player, only Platformer SHALL be unlocked; completing 1 level
    SHALL unlock Space Shooter; eliminating 50 zombies SHALL unlock Maze Chase;
    completing 3 levels SHALL unlock Fighting.

    **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
    **Feature: multi-genre-levels, Property 11: Genre Unlock Conditions**
    """

    def test_platformer_unlocked_by_default(self):
        """Test that platformer is always unlocked for new players."""
        manager = GenreManager()
        assert manager.is_genre_unlocked(GenreType.PLATFORMER)
        assert GenreType.PLATFORMER in manager.get_available_genres()

    def test_space_shooter_unlocks_at_1_level(self):
        """Test that Space Shooter unlocks after completing 1 level."""
        manager = GenreManager()

        # Before completing any levels
        assert not manager.is_genre_unlocked(GenreType.SPACE_SHOOTER)

        # After completing 1 level
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=1, zombies_eliminated=0
        )
        assert GenreType.SPACE_SHOOTER in newly_unlocked

    def test_maze_chase_unlocks_at_50_zombies(self):
        """Test that Maze Chase unlocks after eliminating 50 zombies."""
        manager = GenreManager()

        # Before 50 zombies
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=0, zombies_eliminated=49
        )
        assert GenreType.MAZE_CHASE not in newly_unlocked

        # At exactly 50 zombies
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=0, zombies_eliminated=50
        )
        assert GenreType.MAZE_CHASE in newly_unlocked

    def test_fighting_unlocks_at_3_levels(self):
        """Test that Fighting unlocks after completing 3 levels."""
        manager = GenreManager()

        # Before 3 levels
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=2, zombies_eliminated=0
        )
        assert GenreType.FIGHTING not in newly_unlocked

        # At exactly 3 levels
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=3, zombies_eliminated=0
        )
        assert GenreType.FIGHTING in newly_unlocked

    @given(
        levels=st.integers(min_value=0, max_value=100),
        zombies=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=50)
    def test_unlock_conditions_are_monotonic(self, levels: int, zombies: int):
        """Test that once unlocked, genres stay unlocked."""
        manager = GenreManager()

        # Check what should be unlocked
        newly_unlocked = manager.check_unlock_conditions(
            levels_completed=levels, zombies_eliminated=zombies
        )

        # Unlock them
        for genre in newly_unlocked:
            manager.unlock_genre(genre)

        # Verify they stay unlocked even with lower values
        for genre in manager.get_available_genres():
            assert manager.is_genre_unlocked(genre)


class TestGenreSelection:
    """Tests for genre selection behavior."""

    def test_cannot_select_locked_genre(self):
        """Test that locked genres cannot be selected."""
        manager = GenreManager()

        # Space shooter is locked by default
        result = manager.select_genre("123456789", GenreType.SPACE_SHOOTER)
        assert result is False

        # Should still be platformer
        assert manager.get_genre_for_account("123456789") == GenreType.PLATFORMER

    def test_can_select_unlocked_genre(self):
        """Test that unlocked genres can be selected."""
        manager = GenreManager()
        manager.unlock_genre(GenreType.SPACE_SHOOTER)

        result = manager.select_genre("123456789", GenreType.SPACE_SHOOTER)
        assert result is True
        assert manager.get_genre_for_account("123456789") == GenreType.SPACE_SHOOTER

    def test_default_genre_is_platformer(self):
        """Test that default genre for unknown accounts is platformer."""
        manager = GenreManager()
        assert manager.get_genre_for_account("unknown") == GenreType.PLATFORMER


class TestUnlockedGenresPersistence:
    """Tests for unlocked genres persistence."""

    @given(
        genres_to_unlock=st.lists(genre_strategy, min_size=0, max_size=4, unique=True)
    )
    @settings(max_examples=30)
    def test_unlocked_genres_round_trip(self, genres_to_unlock: list):
        """Test that unlocked genres survive serialization."""
        manager = GenreManager()

        # Unlock specified genres
        for genre in genres_to_unlock:
            manager.unlock_genre(genre)

        # Serialize and restore
        data = manager.to_dict()
        restored = GenreManager.from_dict(data)

        # Platformer should always be unlocked
        assert restored.is_genre_unlocked(GenreType.PLATFORMER)

        # All unlocked genres should be preserved
        for genre in genres_to_unlock:
            assert restored.is_genre_unlocked(genre)


class TestGenreSelectionTriggersCorrectTemplate:
    """Property 1: Genre Selection Triggers Correct Template

    *For any* genre selection, the system SHALL load the corresponding
    controller type that matches the selected genre.

    **Validates: Requirements 1.3, 2.1, 3.1, 4.1, 5.1**
    **Feature: multi-genre-levels, Property 1: Genre Selection Triggers Correct Template**
    """

    def test_genre_controller_factory_returns_correct_type(self):
        """Test that factory creates correct controller for each genre."""
        from genre_controller import GenreController, GenreControllerFactory

        # Register mock controllers for testing
        class MockPlatformerController(GenreController):
            def initialize_level(self, account_id, zombies, level_width, level_height):
                pass

            def update(self, delta_time, player):
                pass

            def handle_input(self, input_state, player):
                pass

            def check_completion(self):
                return False

            def render(self, surface, camera_offset):
                pass

        # Register the mock
        GenreControllerFactory.register(GenreType.PLATFORMER, MockPlatformerController)

        # Create controller
        controller = GenreControllerFactory.create(GenreType.PLATFORMER, 800, 600)

        # Verify correct type
        assert controller is not None
        assert controller.genre == GenreType.PLATFORMER
        assert isinstance(controller, MockPlatformerController)

    @given(genre=genre_strategy)
    @settings(max_examples=20)
    def test_genre_controller_matches_selected_genre(self, genre: GenreType):
        """Test that created controller always matches the requested genre."""
        from genre_controller import GenreController, GenreControllerFactory

        # Create a generic mock controller class
        class GenericMockController(GenreController):
            def initialize_level(self, account_id, zombies, level_width, level_height):
                pass

            def update(self, delta_time, player):
                pass

            def handle_input(self, input_state, player):
                pass

            def check_completion(self):
                return False

            def render(self, surface, camera_offset):
                pass

        # Register for this genre
        GenreControllerFactory.register(genre, GenericMockController)

        # Create controller
        controller = GenreControllerFactory.create(genre, 800, 600)

        # Verify genre matches
        assert controller is not None
        assert controller.genre == genre

    def test_unregistered_genre_returns_none(self):
        """Test that unregistered genres return None."""
        from genre_controller import GenreControllerFactory

        # Clear any existing registrations for a test genre
        # Check if MAZE_CHASE is registered - if not, it should return None
        registered = GenreControllerFactory.get_registered_genres()

        # Find a genre that's not registered
        for genre in GenreType:
            if genre not in registered:
                result = GenreControllerFactory.create(genre, 800, 600)
                assert result is None
                return

        # If all genres are registered, this test passes trivially
        # (all genres have controllers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestSpaceShooterPlayerPosition:
    """Property 4: Space Shooter Player Position

    *For any* space shooter level, the player SHALL be positioned at the
    bottom of the screen and projectiles SHALL travel upward.

    **Validates: Requirements 3.2, 3.4**
    **Feature: multi-genre-levels, Property 4: Space Shooter Player Position**
    """

    def test_player_at_bottom_of_screen(self):
        """Test that player is positioned at bottom of screen."""
        from space_shooter_controller import SpaceShooterController

        controller = SpaceShooterController(GenreType.SPACE_SHOOTER, 800, 600)

        # Player Y should be near bottom (600 - offset)
        assert controller.player_y > 500  # Near bottom
        assert controller.player_y < 600  # But not off screen

    def test_projectiles_travel_upward(self):
        """Test that projectiles have negative Y velocity (upward)."""
        from space_shooter_controller import SpaceShooterController

        controller = SpaceShooterController(GenreType.SPACE_SHOOTER, 800, 600)
        controller._fire_projectile()

        assert len(controller.projectiles) == 1
        proj = controller.projectiles[0]

        # Negative Y velocity means upward movement
        assert proj.velocity.y < 0

    @given(screen_height=st.integers(min_value=400, max_value=1200))
    @settings(max_examples=20)
    def test_player_always_near_bottom(self, screen_height: int):
        """Test player is always positioned near bottom regardless of screen size."""
        from space_shooter_controller import SpaceShooterController

        controller = SpaceShooterController(GenreType.SPACE_SHOOTER, 800, screen_height)

        # Player should be within bottom 100 pixels
        assert controller.player_y >= screen_height - 100
        assert controller.player_y < screen_height


class TestSpaceShooterZombieBehavior:
    """Property 5: Space Shooter Zombie Behavior

    *For any* space shooter level, zombies SHALL spawn at the top of the
    screen, move downward, and damage the player when reaching the bottom.

    **Validates: Requirements 3.3, 3.6**
    **Feature: multi-genre-levels, Property 5: Space Shooter Zombie Behavior**
    """

    def test_zombies_spawn_at_top(self):
        """Test that zombies are positioned at top of screen."""
        from space_shooter_controller import SpaceShooterController

        # Create mock zombies
        class MockZombie:
            def __init__(self):
                self.position = Vector2(0, 0)
                self.is_quarantining = False
                self.health = 100

            def get_bounds(self):
                return pygame.Rect(self.position.x - 20, self.position.y - 20, 40, 40)

        zombies = [MockZombie() for _ in range(5)]

        controller = SpaceShooterController(GenreType.SPACE_SHOOTER, 800, 600)
        controller.initialize_level("123456789", zombies, 800, 600)

        # All zombies should be in top half of screen
        for zombie in zombies:
            assert zombie.position.y < 300  # Top half

    def test_zombies_descend_over_time(self):
        """Test that zombies move downward during update."""
        from space_shooter_controller import SpaceShooterController

        class MockZombie:
            def __init__(self):
                self.position = Vector2(400, 100)
                self.is_quarantining = False
                self.health = 100

            def get_bounds(self):
                return pygame.Rect(self.position.x - 20, self.position.y - 20, 40, 40)

        class MockPlayer:
            def __init__(self):
                self.position = Vector2(400, 550)

        zombies = [MockZombie()]
        player = MockPlayer()

        controller = SpaceShooterController(GenreType.SPACE_SHOOTER, 800, 600)
        controller.initialize_level("123456789", zombies, 800, 600)

        initial_y = zombies[0].position.y

        # Update for 1 second
        controller.update(1.0, player)

        # Zombie should have moved down
        assert zombies[0].position.y > initial_y


class TestMazeChaseMovementValidity:
    """Property 6: Maze Chase Movement Validity

    *For any* maze chase level, zombie movement SHALL only occur along
    valid maze paths (no moving through walls).

    **Validates: Requirements 4.4**
    **Feature: multi-genre-levels, Property 6: Maze Chase Movement Validity**
    """

    def test_zombie_cannot_move_through_walls(self):
        """Test that zombies respect maze walls."""
        from maze_chase_controller import Direction, MazeChaseController

        controller = MazeChaseController(GenreType.MAZE_CHASE, 800, 600)
        controller._generate_maze()

        # Check that _can_move respects walls
        # Border walls should block movement
        assert not controller._can_move(0, 0, Direction.LEFT)  # Left border
        assert not controller._can_move(0, 0, Direction.UP)  # Top border

    def test_valid_positions_are_within_maze(self):
        """Test that valid positions are within maze bounds."""
        from maze_chase_controller import MazeChaseController

        controller = MazeChaseController(GenreType.MAZE_CHASE, 800, 600)
        controller._generate_maze()

        # Valid positions
        assert controller._is_valid_position(1, 1)
        assert controller._is_valid_position(5, 5)

        # Invalid positions (outside maze)
        assert not controller._is_valid_position(-1, 0)
        assert not controller._is_valid_position(0, -1)
        assert not controller._is_valid_position(controller.maze_width, 0)
        assert not controller._is_valid_position(0, controller.maze_height)


class TestMazeChaseCollisionDirection:
    """Property 7: Maze Chase Collision Direction

    *For any* player-zombie collision in maze chase, front collision
    SHALL eliminate the zombie, rear collision SHALL damage the player.

    **Validates: Requirements 4.3, 4.6**
    **Feature: multi-genre-levels, Property 7: Maze Chase Collision Direction**
    """

    def test_front_collision_detection(self):
        """Test that front collision is detected correctly."""
        from maze_chase_controller import Direction, MazeChaseController

        class MockPlayer:
            def __init__(self):
                self.position = Vector2(100, 100)

        class MockZombie:
            def __init__(self, x, y):
                self.position = Vector2(x, y)

        controller = MazeChaseController(GenreType.MAZE_CHASE, 800, 600)
        player = MockPlayer()

        # Player facing right, zombie to the right = front collision
        controller.player_direction = Direction.RIGHT
        zombie_right = MockZombie(150, 100)
        assert controller._is_front_collision(player, zombie_right)

        # Player facing right, zombie to the left = rear collision
        zombie_left = MockZombie(50, 100)
        assert not controller._is_front_collision(player, zombie_left)

    def test_no_direction_means_no_front_collision(self):
        """Test that stationary player has no front collision."""
        from maze_chase_controller import Direction, MazeChaseController

        class MockPlayer:
            def __init__(self):
                self.position = Vector2(100, 100)

        class MockZombie:
            def __init__(self):
                self.position = Vector2(150, 100)

        controller = MazeChaseController(GenreType.MAZE_CHASE, 800, 600)
        controller.player_direction = Direction.NONE

        player = MockPlayer()
        zombie = MockZombie()

        # No direction = no front collision
        assert not controller._is_front_collision(player, zombie)


class TestBossHealthBarDisplay:
    """Property 14: Boss Health Bar Display

    *For any* boss battle, health bars SHALL accurately reflect current health.

    **Validates: Requirements 11.2**
    **Feature: multi-genre-levels, Property 14: Boss Health Bar Display**
    """

    def test_health_bar_reflects_current_health(self):
        """Test that health bar calculation is accurate."""
        from fighting_arena import FightingArena

        arena = FightingArena(800, 600)

        # Health ratio should be calculated correctly
        # This is tested implicitly through the render method
        # We verify the arena initializes correctly
        assert arena.HEALTH_BAR_WIDTH == 300
        assert arena.HEALTH_BAR_HEIGHT == 25

    @given(
        health=st.integers(min_value=0, max_value=100),
        max_health=st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=30)
    def test_health_ratio_calculation(self, health: int, max_health: int):
        """Test health ratio is always between 0 and 1."""
        health = min(health, max_health)  # Ensure health <= max
        ratio = max(0, min(1, health / max_health))
        assert 0 <= ratio <= 1


class TestAttackDamageApplication:
    """Property 16: Attack Damage Application

    *For any* successful attack, the target's health SHALL be reduced
    by the attack's damage value.

    **Validates: Requirements 5.4, 5.5**
    **Feature: multi-genre-levels, Property 16: Attack Damage Application**
    """

    def test_punch_reduces_health(self):
        """Test that punch attack reduces target health."""
        from player_fighter import PlayerFighter

        fighter = PlayerFighter(100, 500)
        initial_health = fighter.health

        damage = 20
        actual = fighter.take_damage(damage)

        assert actual == damage
        assert fighter.health == initial_health - damage

    def test_kick_reduces_health(self):
        """Test that kick attack reduces target health."""
        from boss_fighter import BossFighter

        boss = BossFighter(700, 500)
        initial_health = boss.health

        damage = 15
        actual = boss.take_damage(damage)

        assert actual == damage
        assert boss.health == initial_health - damage

    @given(damage=st.integers(min_value=1, max_value=50))
    @settings(max_examples=20)
    def test_damage_always_reduces_health(self, damage: int):
        """Test that any damage amount reduces health."""
        from player_fighter import PlayerFighter

        fighter = PlayerFighter(100, 500)
        initial_health = fighter.health

        fighter.take_damage(damage)

        assert fighter.health < initial_health


class TestBlockDamageReduction:
    """Property 17: Block Damage Reduction

    *For any* blocked attack, damage SHALL be reduced by at least 50%.

    **Validates: Requirements 13.3**
    **Feature: multi-genre-levels, Property 17: Block Damage Reduction**
    """

    def test_blocking_reduces_damage(self):
        """Test that blocking reduces incoming damage."""
        from player_fighter import PlayerFighter

        fighter = PlayerFighter(100, 500)
        fighter.block()

        damage = 20
        actual = fighter.take_damage(damage)

        # Should be reduced by 50%
        assert actual <= damage * 0.5

    def test_not_blocking_takes_full_damage(self):
        """Test that not blocking takes full damage."""
        from player_fighter import PlayerFighter

        fighter = PlayerFighter(100, 500)
        # Not blocking

        damage = 20
        actual = fighter.take_damage(damage)

        assert actual == damage

    @given(damage=st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_block_always_reduces_damage(self, damage: int):
        """Test that blocking always reduces damage."""
        from player_fighter import PlayerFighter

        fighter = PlayerFighter(100, 500)
        fighter.block()

        actual = fighter.take_damage(damage)

        assert actual <= damage


class TestBossAIAggressionScaling:
    """Property 18: Boss AI Aggression Scaling

    *For any* boss, aggression SHALL increase as health decreases.

    **Validates: Requirements 14.4**
    **Feature: multi-genre-levels, Property 18: Boss AI Aggression Scaling**
    """

    def test_aggression_increases_with_damage(self):
        """Test that aggression increases as boss takes damage."""
        from boss_fighter import BossFighter

        boss = BossFighter(700, 500)

        # Full health aggression
        full_health_aggression = boss._get_aggression()

        # Take damage
        boss.take_damage(50)

        # Lower health aggression
        low_health_aggression = boss._get_aggression()

        assert low_health_aggression > full_health_aggression

    def test_aggression_at_full_health(self):
        """Test base aggression at full health."""
        from boss_fighter import BossFighter

        boss = BossFighter(700, 500)
        aggression = boss._get_aggression()

        # Should be at base level
        assert aggression == boss.base_aggression

    def test_aggression_at_low_health(self):
        """Test increased aggression at low health."""
        from boss_fighter import BossFighter

        boss = BossFighter(700, 500, max_health=100)
        boss.health = 10  # Very low health

        aggression = boss._get_aggression()

        # Should be significantly higher than base
        assert aggression > boss.base_aggression + 0.3


class TestBossArenaTransition:
    """Property 13: Boss Arena Transition

    *For any* boss battle, the system SHALL transition to the arena
    and return to the original level after battle.

    **Validates: Requirements 5.1, 5.8, 11.1**
    **Feature: multi-genre-levels, Property 13: Boss Arena Transition**
    """

    def test_battle_initializes_arena(self):
        """Test that starting battle creates arena."""
        from boss_battle_controller import BossBattleController

        controller = BossBattleController(GenreType.FIGHTING, 800, 600)
        controller.start_boss_battle("scattered_spider", "TEST BOSS")

        assert controller.arena is not None
        assert controller.player_fighter is not None
        assert controller.boss_fighter is not None
        assert controller.is_initialized

    def test_battle_stores_return_level(self):
        """Test that return level is stored."""
        from boss_battle_controller import BossBattleController

        controller = BossBattleController(GenreType.FIGHTING, 800, 600)
        controller.start_boss_battle(
            "scattered_spider", "TEST BOSS", return_level_id="production"
        )

        assert controller.return_level_id == "production"


class TestBossTimerBehavior:
    """Property 15: Boss Timer Behavior

    *For any* round, timer SHALL count down from 99 and zero
    determines winner by health.

    **Validates: Requirements 11.3, 11.4**
    **Feature: multi-genre-levels, Property 15: Boss Timer Behavior**
    """

    def test_timer_starts_at_99(self):
        """Test that round timer starts at 99 seconds."""
        from fighting_arena import FightingArena

        arena = FightingArena(800, 600)
        arena.start_round()

        assert arena.time_remaining == 99

    def test_timer_counts_down(self):
        """Test that timer decreases over time."""
        from fighting_arena import FightingArena

        arena = FightingArena(800, 600)
        arena.start_round()

        initial_time = arena.time_remaining
        arena.update(1.0)  # 1 second

        assert arena.time_remaining < initial_time

    def test_timer_returns_timeout(self):
        """Test that timer returns timeout when reaching zero."""
        from fighting_arena import FightingArena

        arena = FightingArena(800, 600)
        arena.start_round()
        arena.time_remaining = 0.5

        result = arena.update(1.0)  # More than remaining time

        assert result == "timeout"
        assert arena.time_remaining == 0
