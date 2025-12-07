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

        # Callback for zombie elimination (set by game engine)
        self.on_zombie_eliminated_callback = None

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
        """Generate a more restrictive maze layout with clear corridors."""
        self.maze = []

        for y in range(self.maze_height):
            row = []
            for x in range(self.maze_width):
                walls = set()

                # Border walls (always)
                if x == 0:
                    walls.add(Direction.LEFT)
                if x == self.maze_width - 1:
                    walls.add(Direction.RIGHT)
                if y == 0:
                    walls.add(Direction.UP)
                if y == self.maze_height - 1:
                    walls.add(Direction.DOWN)

                # Create a grid pattern with corridors every 3 cells
                # Vertical walls
                if x % 3 == 0 and x > 0 and x < self.maze_width - 1:
                    # Add wall unless it's a corridor row
                    if y % 4 != 2:
                        walls.add(Direction.LEFT)
                if (x + 1) % 3 == 0 and x < self.maze_width - 1:
                    if y % 4 != 2:
                        walls.add(Direction.RIGHT)

                # Horizontal walls
                if y % 4 == 0 and y > 0 and y < self.maze_height - 1:
                    # Add wall unless it's a corridor column
                    if x % 3 != 1:
                        walls.add(Direction.UP)
                if (y + 1) % 4 == 0 and y < self.maze_height - 1:
                    if x % 3 != 1:
                        walls.add(Direction.DOWN)

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
        """Update zombie positions - all zombies move constantly."""
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            # Initialize direction if not set
            if zombie not in self.zombie_directions:
                self.zombie_directions[zombie] = random.choice(
                    [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
                )

            # Initialize grid position if not set
            if zombie not in self.zombie_grid_positions:
                gx = int(zombie.position.x // self.CELL_SIZE)
                gy = int(zombie.position.y // self.CELL_SIZE)
                self.zombie_grid_positions[zombie] = (gx, gy)

            direction = self.zombie_directions[zombie]
            gx, gy = self.zombie_grid_positions[zombie]

            # Higher chance to change direction for more erratic movement
            if random.random() < 0.05:  # 5% chance per frame
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

            # Always try to move
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
                # Hit wall - immediately find new direction
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
                    self.zombie_directions[zombie] = random.choice(possible)
                else:
                    # Stuck - try to unstick by moving to center of cell
                    zombie.position.x = gx * self.CELL_SIZE + self.CELL_SIZE // 2
                    zombie.position.y = gy * self.CELL_SIZE + self.CELL_SIZE // 2

    def _check_collisions(self, player) -> None:
        """Check player-zombie collisions with direction-based outcome."""
        # Skip if player is invincible (just took damage)
        if getattr(player, "is_invincible", False):
            return

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
                    # Rear collision - damage player (1 heart = 1 damage)
                    if hasattr(player, "take_damage"):
                        player.take_damage(1)  # One heart of damage
                    # Only process one collision per frame
                    break

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

    def on_zombie_eliminated(self, zombie) -> None:
        """Called when a zombie is eliminated (chomped).

        Args:
            zombie: The eliminated zombie
        """
        logger.info(f"👻 Ghost chomped in maze chase: {zombie.identity_name}")

        # Call the callback to trigger quarantine API
        if self.on_zombie_eliminated_callback:
            self.on_zombie_eliminated_callback(zombie)

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

    def render(self, surface, camera_offset: Vector2, player=None) -> None:
        """Render maze elements including WALLy player.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (ignored for maze)
            player: Optional player entity to render as WALLy
        """
        # Render maze walls
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                # Draw cell background
                pygame.draw.rect(
                    surface,
                    (15, 15, 35),  # Darker blue background
                    (px, py, self.CELL_SIZE, self.CELL_SIZE),
                )

                # Draw walls (thicker, more visible)
                wall_color = (0, 120, 220)  # Brighter blue walls
                wall_width = 4

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

        # Render zombies
        self._render_zombies(surface, camera_offset)

        # Render player as WALLy
        if player:
            self.render_player(surface, player, camera_offset)
            # Render danger indicators for nearby zombies
            self._render_danger_indicators(surface, player, camera_offset)

        # Render HUD instructions
        self._render_hud(surface)

    def _render_danger_indicators(self, surface, player, camera_offset: Vector2) -> None:
        """Show red warning when zombies are behind player (will damage you)."""
        px = int(player.position.x - camera_offset.x)
        py = int(player.position.y - camera_offset.y)

        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False):
                continue

            # Check distance
            dist_x = zombie.position.x - player.position.x
            dist_y = zombie.position.y - player.position.y
            distance = (dist_x**2 + dist_y**2) ** 0.5

            if distance < 80:  # Close enough to show indicator
                zx = int(zombie.position.x - camera_offset.x)
                zy = int(zombie.position.y - camera_offset.y)

                is_front = self._is_front_collision(player, zombie)

                if is_front and self.player_direction != Direction.NONE:
                    # Green - safe to attack
                    pygame.draw.circle(surface, (0, 255, 0), (zx, zy - 20), 5)
                else:
                    # Red - danger! Will take damage
                    pygame.draw.circle(surface, (255, 0, 0), (zx, zy - 20), 6)
                    pygame.draw.circle(surface, (255, 100, 100), (zx, zy - 20), 3)

    def _render_hud(self, surface) -> None:
        """Render instructions HUD."""
        font = pygame.font.Font(None, 20)

        # Instructions at top
        instructions = [
            "MAZE CHASE - Chomp the Zombies!",
            "GREEN dot = Safe to attack (move toward zombie)",
            "RED dot = DANGER! (zombie behind you - will hurt!)",
            "Arrow Keys to move - Face zombies to eliminate them!",
        ]

        y = 10
        for text in instructions:
            label = font.render(text, True, (200, 200, 255))
            surface.blit(label, (10, y))
            y += 18

    def _render_zombies(self, surface, camera_offset: Vector2) -> None:
        """Render zombies as actual zombie characters (green, shambling)."""
        for zombie in self.zombies:
            if getattr(zombie, "is_quarantining", False) or getattr(zombie, "is_hidden", False):
                continue

            px = int(zombie.position.x - camera_offset.x)
            py = int(zombie.position.y - camera_offset.y)

            size = 28

            # Zombie body (green, decayed look)
            body_color = (80, 140, 80)  # Zombie green
            dark_green = (50, 100, 50)

            # Body (oval shape)
            pygame.draw.ellipse(
                surface, body_color, (px - size // 2, py - size // 2, size, size + 4)
            )

            # Tattered clothes (darker patches)
            pygame.draw.ellipse(surface, dark_green, (px - 6, py + 2, 12, 8))

            # Head
            pygame.draw.circle(surface, body_color, (px, py - 8), 10)

            # Zombie eyes (red, glowing)
            pygame.draw.circle(surface, (200, 50, 50), (px - 4, py - 10), 3)
            pygame.draw.circle(surface, (200, 50, 50), (px + 4, py - 10), 3)
            # Eye glow
            pygame.draw.circle(surface, (255, 100, 100), (px - 4, py - 10), 1)
            pygame.draw.circle(surface, (255, 100, 100), (px + 4, py - 10), 1)

            # Zombie mouth (jagged)
            pygame.draw.line(surface, (40, 60, 40), (px - 4, py - 4), (px + 4, py - 4), 2)

            # Arms reaching out
            pygame.draw.line(surface, body_color, (px - 10, py - 2), (px - 16, py - 6), 3)
            pygame.draw.line(surface, body_color, (px + 10, py - 2), (px + 16, py - 6), 3)

            # Name label
            font = pygame.font.Font(None, 14)
            name = zombie.identity_name[:8] if hasattr(zombie, "identity_name") else "Zombie"
            label = font.render(name, True, (200, 255, 200))
            surface.blit(label, (px - label.get_width() // 2, py + size // 2 + 2))

    def render_player(self, surface, player, camera_offset: Vector2) -> None:
        """Render the player as WALLy robot - simple cute robot design.

        Args:
            surface: Pygame surface to render on
            player: Player entity with position
            camera_offset: Camera offset for rendering
        """
        px = int(player.position.x - camera_offset.x)
        py = int(player.position.y - camera_offset.y)

        size = 30

        # Colors
        body_color = (220, 220, 235)  # Light gray/white
        screen_color = (100, 60, 160)  # Purple screen
        eye_color = (255, 255, 255)

        # === BODY (simple rounded square) ===
        pygame.draw.rect(
            surface,
            body_color,
            (px - size // 2, py - size // 2, size, size),
            border_radius=6,
        )

        # === SCREEN/FACE (purple rectangle) ===
        pygame.draw.rect(
            surface,
            screen_color,
            (px - size // 2 + 4, py - size // 2 + 4, size - 8, size - 10),
            border_radius=4,
        )

        # === TWO SIMPLE EYES ===
        pygame.draw.circle(surface, eye_color, (px - 6, py - 4), 4)
        pygame.draw.circle(surface, eye_color, (px + 6, py - 4), 4)

        # === ANTENNA (small, not ears) ===
        pygame.draw.line(
            surface, (180, 180, 190), (px, py - size // 2), (px, py - size // 2 - 6), 2
        )
        pygame.draw.circle(surface, (255, 200, 100), (px, py - size // 2 - 6), 3)

        # === DIRECTION INDICATOR (arrow showing attack direction) ===
        if self.player_direction != Direction.NONE:
            dx, dy = self.player_direction.value
            # Draw attack indicator (green arrow in movement direction)
            arrow_x = px + dx * 20
            arrow_y = py + dy * 20
            pygame.draw.circle(surface, (100, 255, 100), (arrow_x, arrow_y), 6)
            pygame.draw.circle(surface, (50, 200, 50), (arrow_x, arrow_y), 4)
            # "CHOMP" text when moving
            font = pygame.font.Font(None, 14)
            chomp_label = font.render("CHOMP!", True, (100, 255, 100))
            surface.blit(chomp_label, (px - chomp_label.get_width() // 2, py - size // 2 - 18))
        else:
            # Show "MOVE TO ATTACK" hint when stationary
            font = pygame.font.Font(None, 12)
            hint = font.render("Move to attack!", True, (200, 200, 100))
            surface.blit(hint, (px - hint.get_width() // 2, py - size // 2 - 14))


# Register the maze chase controller with the factory
GenreControllerFactory.register(GenreType.MAZE_CHASE, MazeChaseController)
