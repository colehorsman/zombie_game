"""Maze Chase genre controller for Pac-Man style gameplay.

Implements maze navigation with the player as Wally AI agent
and zombies as ghost-like entities.

**Feature: multi-genre-levels**
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.6**
"""

import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Tuple

import pygame

from genre_controller import GenreController, GenreControllerFactory, InputState
from models import GenreType, Vector2

logger = logging.getLogger(__name__)


class Direction(Enum):
    """Movement directions in the maze."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


@dataclass
class MazeCell:
    """A cell in the maze grid."""

    x: int
    y: int
    walls: Set[Direction]  # Which directions have walls
    is_path: bool = True


class MazeChaseController(GenreController):
    """Controller for Pac-Man style maze chase gameplay.

    Features:
    - Grid-based maze navigation
    - 4-directional movement (no shooting)
    - Front collision eliminates zombies (chomp)
    - Rear collision damages player
    - Ghost-like zombie AI with pathfinding

    **Property 6: Maze Chase Movement Validity**
    Zombie movement only along valid maze paths.
    **Validates: Requirements 4.4**

    **Property 7: Maze Chase Collision Direction**
    Front collision eliminates, rear collision damages.
    **Validates: Requirements 4.3, 4.6**
    """

    # Maze constants
    CELL_SIZE = 40
    PLAYER_SPEED = 150
    ZOMBIE_SPEED = 100
    CHOMP_RANGE = 30  # Distance for front collision

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the maze chase controller.

        Args:
            genre: Should be GenreType.MAZE_CHASE
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        super().__init__(genre, screen_width, screen_height)

        # Maze grid
        self.maze_width = screen_width // self.CELL_SIZE
        self.maze_height = screen_height // self.CELL_SIZE
        self.maze: List[List[MazeCell]] = []

        # Player state
        self.player_direction = Direction.NONE
        self.player_grid_pos = (1, 1)

        # Zombie tracking
        self.zombie_directions: dict = {}  # zombie -> Direction
        self.zombie_grid_positions: dict = {}  # zombie -> (x, y)

        logger.info("MazeChaseController initialized")

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up maze level.

        Args:
            account_id: AWS account ID for this level
            zombies: List of zombie entities to place
            level_width: Width of the level
            level_height: Height of the level
        """
        self.zombies = zombies

        # Generate maze
        self._generate_maze()

        # Position player at start
        self.player_grid_pos = (1, 1)

        # Position zombies in maze
        self._position_zombies_in_maze()

        self.is_initialized = True
        logger.info(f"Maze chase level initialized with {len(zombies)} zombies")

    def _generate_maze(self) -> None:
        """Generate a simple maze layout."""
        self.maze = []

        for y in range(self.maze_height):
            row = []
            for x in range(self.maze_width):
                # Create cell with walls on edges
                walls = set()

                # Border walls
                if x == 0:
                    walls.add(Direction.LEFT)
                if x == self.maze_width - 1:
                    walls.add(Direction.RIGHT)
                if y == 0:
                    walls.add(Direction.UP)
                if y == self.maze_height - 1:
                    walls.add(Direction.DOWN)

                # Add some internal walls for maze structure
                # Simple pattern: walls every 4 cells with gaps
                if x > 0 and x < self.maze_width - 1:
                    if x % 4 == 0 and y % 2 == 0 and y > 0 and y < self.maze_height - 1:
                        walls.add(Direction.UP)
                        walls.add(Direction.DOWN)

                if y > 0 and y < self.maze_height - 1:
                    if y % 4 == 0 and x % 2 == 0 and x > 0 and x < self.maze_width - 1:
                        walls.add(Direction.LEFT)
                        walls.add(Direction.RIGHT)

                cell = MazeCell(x=x, y=y, walls=walls)
                row.append(cell)
            self.maze.append(row)

    def _position_zombies_in_maze(self) -> None:
        """Position zombies at valid maze locations."""
        if not self.zombies:
            return

        # Find valid positions (not near player start)
        valid_positions = []
        for y in range(2, self.maze_height - 1):
            for x in range(2, self.maze_width - 1):
                if self._is_valid_position(x, y):
                    valid_positions.append((x, y))

        random.shuffle(valid_positions)

        for i, zombie in enumerate(self.zombies):
            if i < len(valid_positions):
                gx, gy = valid_positions[i]
            else:
                gx, gy = random.randint(2, self.maze_width - 2), random.randint(
                    2, self.maze_height - 2
                )

            self.zombie_grid_positions[zombie] = (gx, gy)
            self.zombie_directions[zombie] = random.choice(
                [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            )

            # Set pixel position
            zombie.position = Vector2(
                gx * self.CELL_SIZE + self.CELL_SIZE // 2,
                gy * self.CELL_SIZE + self.CELL_SIZE // 2,
            )

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if a grid position is valid for movement."""
        if x < 0 or x >= self.maze_width or y < 0 or y >= self.maze_height:
            return False
        return True

    def _can_move(self, x: int, y: int, direction: Direction) -> bool:
        """Check if movement in a direction is allowed."""
        if not self._is_valid_position(x, y):
            return False

        cell = self.maze[y][x]
        if direction in cell.walls:
            return False

        # Check destination is valid
        dx, dy = direction.value
        new_x, new_y = x + dx, y + dy
        return self._is_valid_position(new_x, new_y)

    def update(self, delta_time: float, player) -> None:
        """Update maze chase game logic.

        Args:
            delta_time: Time since last frame in seconds
            player: Player entity
        """
        if not self.is_initialized:
            return

        # Update player movement
        self._update_player_movement(delta_time, player)

        # Update zombie movement
        self._update_zombie_movement(delta_time)

        # Check collisions
        self._check_collisions(player)

        # Check completion
        if self.get_active_zombie_count() == 0:
            self.is_complete = True

    def _update_player_movement(self, delta_time: float, player) -> None:
        """Update player position based on direction."""
        if self.player_direction == Direction.NONE:
            return

        dx, dy = self.player_direction.value
        speed = self.PLAYER_SPEED * delta_time

        new_x = player.position.x + dx * speed
        new_y = player.position.y + dy * speed

        # Check if movement is valid
        grid_x = int(new_x // self.CELL_SIZE)
        grid_y = int(new_y // self.CELL_SIZE)

        if self._is_valid_position(grid_x, grid_y):
            player.position.x = new_x
            player.position.y = new_y
            self.player_grid_pos = (grid_x, grid_y)

    def _update_zombie_movement(self, delta_time: float) -> None:
        """Update zombie positions with ghost-like AI."""
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            if zombie not in self.zombie_directions:
                continue

            direction = self.zombie_directions[zombie]
            gx, gy = self.zombie_grid_positions.get(zombie, (0, 0))

            # Occasionally change direction
            if random.random() < 0.02:  # 2% chance per frame
                possible = [
                    d
                    for d in [
                        Direction.UP,
                        Direction.DOWN,
                        Direction.LEFT,
                        Direction.RIGHT,
                    ]
                    if self._can_move(gx, gy, d)
                ]
                if possible:
                    direction = random.choice(possible)
                    self.zombie_directions[zombie] = direction

            # Move in current direction
            if self._can_move(gx, gy, direction):
                dx, dy = direction.value
                speed = self.ZOMBIE_SPEED * delta_time

                zombie.position.x += dx * speed
                zombie.position.y += dy * speed

                # Update grid position
                new_gx = int(zombie.position.x // self.CELL_SIZE)
                new_gy = int(zombie.position.y // self.CELL_SIZE)
                self.zombie_grid_positions[zombie] = (new_gx, new_gy)
            else:
                # Hit wall, change direction
                possible = [
                    d
                    for d in [
                        Direction.UP,
                        Direction.DOWN,
                        Direction.LEFT,
                        Direction.RIGHT,
                    ]
                    if self._can_move(gx, gy, d) and d != direction
                ]
                if possible:
                    self.zombie_directions[zombie] = random.choice(possible)

    def _check_collisions(self, player) -> None:
        """Check player-zombie collisions with direction-based outcome."""
        player_rect = player.get_bounds()

        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            zombie_rect = zombie.get_bounds()

            if player_rect.colliderect(zombie_rect):
                # Determine collision direction
                is_front_collision = self._is_front_collision(player, zombie)

                if is_front_collision:
                    # Chomp! Eliminate zombie
                    zombie.take_damage(100)
                    if zombie.health <= 0:
                        self.on_zombie_eliminated(zombie)
                else:
                    # Rear collision - damage player
                    if hasattr(player, "take_damage"):
                        player.take_damage(10)

    def _is_front_collision(self, player, zombie) -> bool:
        """Determine if collision is from the front (player facing zombie)."""
        if self.player_direction == Direction.NONE:
            return False

        dx, dy = self.player_direction.value

        # Vector from player to zombie
        to_zombie_x = zombie.position.x - player.position.x
        to_zombie_y = zombie.position.y - player.position.y

        # Dot product to check if zombie is in front
        dot = dx * to_zombie_x + dy * to_zombie_y

        return dot > 0  # Positive means zombie is in front

    def handle_input(self, input_state: InputState, player) -> None:
        """Process maze chase input (4-directional, no shooting).

        Args:
            input_state: Current input state
            player: Player entity
        """
        # 4-directional movement
        if input_state.up:
            self.player_direction = Direction.UP
        elif input_state.down:
            self.player_direction = Direction.DOWN
        elif input_state.left:
            self.player_direction = Direction.LEFT
        elif input_state.right:
            self.player_direction = Direction.RIGHT
        else:
            self.player_direction = Direction.NONE

    def check_completion(self) -> bool:
        """Check if all zombies are eliminated.

        Returns:
            True if level is complete
        """
        return self.is_complete or self.get_active_zombie_count() == 0

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render maze elements.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (ignored for maze)
        """
        # Render maze walls
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                # Draw cell background
                pygame.draw.rect(
                    surface,
                    (20, 20, 40),  # Dark blue background
                    (px, py, self.CELL_SIZE, self.CELL_SIZE),
                )

                # Draw walls
                wall_color = (0, 100, 200)  # Blue walls
                wall_width = 3

                if Direction.UP in cell.walls:
                    pygame.draw.line(
                        surface,
                        wall_color,
                        (px, py),
                        (px + self.CELL_SIZE, py),
                        wall_width,
                    )
                if Direction.DOWN in cell.walls:
                    pygame.draw.line(
                        surface,
                        wall_color,
                        (px, py + self.CELL_SIZE),
                        (px + self.CELL_SIZE, py + self.CELL_SIZE),
                        wall_width,
                    )
                if Direction.LEFT in cell.walls:
                    pygame.draw.line(
                        surface,
                        wall_color,
                        (px, py),
                        (px, py + self.CELL_SIZE),
                        wall_width,
                    )
                if Direction.RIGHT in cell.walls:
                    pygame.draw.line(
                        surface,
                        wall_color,
                        (px + self.CELL_SIZE, py),
                        (px + self.CELL_SIZE, py + self.CELL_SIZE),
                        wall_width,
                    )


# Register the maze chase controller with the factory
GenreControllerFactory.register(GenreType.MAZE_CHASE, MazeChaseController)
