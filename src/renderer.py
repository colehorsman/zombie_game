"""Rendering system for the game."""

import logging
import pygame
from typing import List, Optional

from models import GameState, GameStatus
from player import Player
from zombie import Zombie
from projectile import Projectile
from game_map import GameMap


logger = logging.getLogger(__name__)


class Renderer:
    """Manages all visual output using Pygame."""

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.

        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Initialize fonts
        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 32)
        self.label_font = pygame.font.Font(None, 20)
        self.message_font = pygame.font.Font(None, 24)

        # Background scroll offset
        self.scroll_offset = 0

        # Colors
        self.bg_color = (40, 40, 40)
        self.grid_color = (60, 60, 60)
        self.ui_text_color = (255, 255, 255)
        self.error_color = (255, 100, 100)

    def clear_screen(self) -> None:
        """Clear the screen to background color."""
        self.screen.fill(self.bg_color)

    def render_background(self, game_map: Optional[GameMap] = None) -> None:
        """
        Render the background (map or grid).

        Args:
            game_map: Game map instance (None for classic grid background)
        """
        if game_map:
            # Render the floorplan map
            game_map.render(self.screen)
        else:
            # Classic scrolling grid background
            grid_size = 50

            # Draw vertical lines
            for x in range(0, self.width + grid_size, grid_size):
                offset_x = (x - int(self.scroll_offset) % grid_size)
                pygame.draw.line(
                    self.screen,
                    self.grid_color,
                    (offset_x, 0),
                    (offset_x, self.height),
                    1
                )

            # Draw horizontal lines
            for y in range(0, self.height + grid_size, grid_size):
                pygame.draw.line(
                    self.screen,
                    self.grid_color,
                    (0, y),
                    (self.width, y),
                    1
                )

    def render_player(self, player: Player, game_map: Optional[GameMap] = None) -> None:
        """
        Render the player character.

        Args:
            player: The player to render
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        if game_map:
            # Convert world coordinates to screen coordinates
            screen_x, screen_y = game_map.world_to_screen(player.position.x, player.position.y)
            self.screen.blit(player.sprite, (screen_x, screen_y))
        else:
            # Use screen coordinates directly
            self.screen.blit(
                player.sprite,
                (int(player.position.x), int(player.position.y))
            )

    def render_zombies(self, zombies: List[Zombie], game_map: Optional[GameMap] = None) -> None:
        """
        Render all zombie entities.

        Args:
            zombies: List of zombies to render
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        rendered_count = 0
        for zombie in zombies:
            # Skip hidden zombies
            if zombie.is_hidden:
                continue

            if game_map:
                # Map mode: check if zombie is visible on screen and render at screen position
                if game_map.is_on_screen(zombie.position.x, zombie.position.y, zombie.width, zombie.height):
                    screen_x, screen_y = game_map.world_to_screen(zombie.position.x, zombie.position.y)
                    self.screen.blit(zombie.sprite, (screen_x, screen_y))
                    rendered_count += 1
            else:
                # Classic mode: only render zombies that are on or near the screen
                if -100 < zombie.position.x < self.width + 100:
                    self.screen.blit(
                        zombie.sprite,
                        (int(zombie.position.x), int(zombie.position.y))
                    )
                    rendered_count += 1

        # Debug log on first few frames
        if rendered_count > 0 and hasattr(self, '_first_render'):
            logger.info(f"Rendered {rendered_count} zombies on screen")
            delattr(self, '_first_render')
        elif not hasattr(self, '_first_render'):
            self._first_render = True

    def render_zombie_labels(self, zombies: List[Zombie], game_map: Optional[GameMap] = None) -> None:
        """
        Render numeric labels above zombies.

        Args:
            zombies: List of zombies to render labels for
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        for zombie in zombies:
            # Skip hidden zombies
            if zombie.is_hidden:
                continue

            # Check visibility based on mode
            is_visible = False
            screen_x, screen_y = 0, 0

            if game_map:
                # Map mode: convert world to screen coordinates
                is_visible = game_map.is_on_screen(zombie.position.x, zombie.position.y, zombie.width, zombie.height)
                if is_visible:
                    screen_x, screen_y = game_map.world_to_screen(zombie.position.x, zombie.position.y)
            else:
                # Classic mode: check screen bounds
                is_visible = -100 < zombie.position.x < self.width + 100
                screen_x = int(zombie.position.x)
                screen_y = int(zombie.position.y)

            if is_visible:
                # Use display number if available, otherwise show first few chars of name
                if zombie.display_number is not None:
                    label_text = str(zombie.display_number)
                else:
                    # Fallback: show part of the name
                    label_text = zombie.identity_name[:8]

                label_surface = self.label_font.render(
                    label_text,
                    True,
                    (255, 255, 255)
                )

                # Position above the zombie
                label_x = int(screen_x + zombie.width // 2 - label_surface.get_width() // 2)
                label_y = int(screen_y - 20)

                # Draw black outline for readability
                outline_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dx, dy in outline_offsets:
                    outline_surface = self.label_font.render(
                        label_text,
                        True,
                        (0, 0, 0)
                    )
                    self.screen.blit(outline_surface, (label_x + dx, label_y + dy))

                # Draw the label
                self.screen.blit(label_surface, (label_x, label_y))

    def render_projectiles(self, projectiles: List[Projectile], game_map: Optional[GameMap] = None) -> None:
        """
        Render all projectiles.

        Args:
            projectiles: List of projectiles to render
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        for projectile in projectiles:
            if game_map:
                # Map mode: convert world to screen coordinates
                if game_map.is_on_screen(projectile.position.x, projectile.position.y, projectile.radius * 2, projectile.radius * 2):
                    screen_x, screen_y = game_map.world_to_screen(projectile.position.x, projectile.position.y)
                    self.screen.blit(
                        projectile.sprite,
                        (int(screen_x - projectile.radius), int(screen_y - projectile.radius))
                    )
            else:
                # Classic mode: use screen coordinates directly
                self.screen.blit(
                    projectile.sprite,
                    (int(projectile.position.x - projectile.radius),
                     int(projectile.position.y - projectile.radius))
                )

    def render_ui(self, game_state: GameState) -> None:
        """
        Render the UI overlay with game statistics.

        Args:
            game_state: Current game state
        """
        # Zombies remaining
        zombies_text = f"Remaining: {game_state.zombies_remaining}"
        zombies_surface = self.ui_font.render(zombies_text, True, self.ui_text_color)
        self.screen.blit(zombies_surface, (10, 10))

        # Quarantined count
        quarantined_text = f"Quarantined: {game_state.zombies_quarantined}"
        quarantined_surface = self.ui_font.render(quarantined_text, True, self.ui_text_color)
        self.screen.blit(quarantined_surface, (10, 45))

        # Error message if present
        if game_state.error_message:
            error_surface = self.ui_font.render(
                game_state.error_message,
                True,
                self.error_color
            )
            error_x = self.width // 2 - error_surface.get_width() // 2
            self.screen.blit(error_surface, (error_x, self.height - 50))

        # Victory screen
        if game_state.status == GameStatus.VICTORY:
            self._render_victory_screen(game_state)

    def _render_victory_screen(self, game_state: GameState) -> None:
        """
        Render the victory screen.

        Args:
            game_state: Current game state
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Victory message
        victory_font = pygame.font.Font(None, 64)
        victory_text = "VICTORY!"
        victory_surface = victory_font.render(victory_text, True, (0, 255, 0))
        victory_x = self.width // 2 - victory_surface.get_width() // 2
        victory_y = self.height // 2 - 100
        self.screen.blit(victory_surface, (victory_x, victory_y))

        # Statistics
        stats_text = f"All {game_state.total_zombies} zombies quarantined!"
        stats_surface = self.ui_font.render(stats_text, True, self.ui_text_color)
        stats_x = self.width // 2 - stats_surface.get_width() // 2
        stats_y = victory_y + 80
        self.screen.blit(stats_surface, (stats_x, stats_y))

        time_text = f"Time: {game_state.play_time:.1f}s"
        time_surface = self.ui_font.render(time_text, True, self.ui_text_color)
        time_x = self.width // 2 - time_surface.get_width() // 2
        time_y = stats_y + 40
        self.screen.blit(time_surface, (time_x, time_y))

    def render_message_bubble(self, message: str) -> None:
        """
        Render a retro Game Boy-style message bubble.

        Args:
            message: The message text to display
        """
        # Calculate bubble dimensions
        padding = 20
        line_height = 30
        max_width = self.width - 100

        # Word wrap the message
        words = message.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.message_font.render(test_line, True, (0, 0, 0))

            if test_surface.get_width() <= max_width - padding * 2:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Calculate bubble size
        bubble_width = max_width
        bubble_height = len(lines) * line_height + padding * 2

        # Position in center of screen
        bubble_x = (self.width - bubble_width) // 2
        bubble_y = (self.height - bubble_height) // 2

        # Draw bubble background (white with black border, Game Boy style)
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Black border (thick for retro look)
        pygame.draw.rect(self.screen, (0, 0, 0), bubble_rect, 0)
        # White interior
        inner_rect = pygame.Rect(
            bubble_x + 4,
            bubble_y + 4,
            bubble_width - 8,
            bubble_height - 8
        )
        pygame.draw.rect(self.screen, (255, 255, 255), inner_rect, 0)

        # Render text lines
        text_y = bubble_y + padding
        for line in lines:
            text_surface = self.message_font.render(line, True, (0, 0, 0))
            text_x = bubble_x + (bubble_width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (text_x, text_y))
            text_y += line_height

        # Render "Press ENTER to continue" at bottom
        continue_text = "Press ENTER to continue"
        continue_surface = self.label_font.render(continue_text, True, (100, 100, 100))
        continue_x = bubble_x + (bubble_width - continue_surface.get_width()) // 2
        continue_y = bubble_y + bubble_height - padding - 5
        self.screen.blit(continue_surface, (continue_x, continue_y))

    def update_scroll(self, delta: float) -> None:
        """
        Update background scroll offset.

        Args:
            delta: Amount to scroll
        """
        self.scroll_offset += delta
