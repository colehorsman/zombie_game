"""Rendering system for the game."""

import logging
import math
import pygame
from typing import List, Optional

from models import GameState, GameStatus, Vector2, QuestStatus
from player import Player
from zombie import Zombie
from projectile import Projectile
from game_map import GameMap
from door import Door
from collectible import Collectible
from boss import Boss


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
                    
                    # Apply flash effect if active
                    if zombie.is_flashing:
                        flash_sprite = zombie.sprite.copy()
                        flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                        self.screen.blit(flash_sprite, (screen_x, screen_y))
                    else:
                        self.screen.blit(zombie.sprite, (screen_x, screen_y))
                    
                    rendered_count += 1
            else:
                # Classic mode: only render zombies that are on or near the screen
                if -100 < zombie.position.x < self.width + 100:
                    # Apply flash effect if active
                    if zombie.is_flashing:
                        flash_sprite = zombie.sprite.copy()
                        flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                        self.screen.blit(flash_sprite, (int(zombie.position.x), int(zombie.position.y)))
                    else:
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

    def render_third_parties(self, third_parties: List, game_map: Optional[GameMap] = None) -> None:
        """
        Render all 3rd party entities.

        Args:
            third_parties: List of 3rd parties to render
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        for third_party in third_parties:
            # 3rd parties are never hidden
            if game_map:
                # Map mode: check if 3rd party is visible on screen and render at screen position
                if game_map.is_on_screen(third_party.position.x, third_party.position.y, third_party.width, third_party.height):
                    screen_x, screen_y = game_map.world_to_screen(third_party.position.x, third_party.position.y)
                    
                    # Apply flash effect if active
                    if third_party.is_flashing:
                        flash_sprite = third_party.sprite.copy()
                        flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                        self.screen.blit(flash_sprite, (screen_x, screen_y))
                    else:
                        self.screen.blit(third_party.sprite, (screen_x, screen_y))
            else:
                # Classic mode: only render 3rd parties that are on or near the screen
                if -100 < third_party.position.x < self.width + 100:
                    # Apply flash effect if active
                    if third_party.is_flashing:
                        flash_sprite = third_party.sprite.copy()
                        flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                        self.screen.blit(flash_sprite, (int(third_party.position.x), int(third_party.position.y)))
                    else:
                        self.screen.blit(
                            third_party.sprite,
                            (int(third_party.position.x), int(third_party.position.y))
                        )

    def render_doors(self, doors: List[Door], game_map: GameMap) -> None:
        """
        Render all pipe-style doors.

        Args:
            doors: List of doors to render
            game_map: Game map for coordinate conversion
        """
        for door in doors:
            if game_map.is_on_screen(door.position.x, door.position.y, door.width, door.height):
                door.render(self.screen, game_map.camera_x, game_map.camera_y)
                
                # Render completion indicator if door leads to completed level
                if door.is_completed:
                    screen_x = int(door.position.x - game_map.camera_x)
                    screen_y = int(door.position.y - game_map.camera_y)
                    
                    # Draw green checkmark or "COMPLETED" text above door
                    try:
                        font = pygame.font.Font(None, 14)
                        text = font.render("✓ COMPLETED", True, (0, 255, 0))  # Green
                        text_rect = text.get_rect(center=(screen_x + door.width // 2, screen_y - 20))
                        self.screen.blit(text, text_rect)
                    except:
                        pass  # Font rendering failed, skip

    def render_collectibles(self, collectibles: List[Collectible], game_map: GameMap) -> None:
        """
        Render all question block collectibles.

        Args:
            collectibles: List of collectibles to render
            game_map: Game map for coordinate conversion
        """
        for collectible in collectibles:
            if not collectible.collected and game_map.is_on_screen(collectible.position.x, collectible.position.y, collectible.width, collectible.height):
                collectible.render(self.screen, game_map.camera_x, game_map.camera_y)

    def render_powerups(self, powerups: List, game_map: GameMap) -> None:
        """
        Render all AWS-themed power-ups.

        Args:
            powerups: List of power-ups to render
            game_map: Game map for coordinate conversion
        """
        for powerup in powerups:
            if not powerup.collected and game_map.is_on_screen(powerup.position.x, powerup.position.y, powerup.width, powerup.height):
                powerup.render(self.screen, game_map.camera_x, game_map.camera_y)

    def render_minimap(self, game_map: GameMap, player_position: Vector2, zombies: List[Zombie]) -> None:
        """
        Render a Mario-style minimap showing rooms and player position.

        Args:
            game_map: Game map instance
            player_position: Player's current position
            zombies: List of zombies for radar display
        """
        # Minimap dimensions and position (bottom-right corner)
        minimap_width = 150
        minimap_height = 120
        minimap_x = self.width - minimap_width - 10
        minimap_y = self.height - minimap_height - 10

        # Background
        bg_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 30, 200))  # Semi-transparent dark background
        self.screen.blit(bg_surface, (minimap_x, minimap_y))

        # Purple border (retro theme)
        pygame.draw.rect(self.screen, (120, 60, 180), (minimap_x, minimap_y, minimap_width, minimap_height), 2)

        # Calculate scale to fit map in minimap
        scale_x = (minimap_width - 20) / game_map.map_width
        scale_y = (minimap_height - 20) / game_map.map_height
        scale = min(scale_x, scale_y)

        # Draw rooms as rectangles
        if hasattr(game_map, 'rooms'):
            for i, (rx, ry, rw, rh) in enumerate(game_map.rooms):
                # Convert room coordinates to minimap coordinates
                room_x = minimap_x + 10 + int(rx * game_map.tile_size * scale)
                room_y = minimap_y + 10 + int(ry * game_map.tile_size * scale)
                room_w = int(rw * game_map.tile_size * scale)
                room_h = int(rh * game_map.tile_size * scale)

                # Draw room outline (purple)
                pygame.draw.rect(self.screen, (100, 60, 140), (room_x, room_y, room_w, room_h), 1)

        # Draw player position (purple circle)
        player_minimap_x = minimap_x + 10 + int(player_position.x * scale)
        player_minimap_y = minimap_y + 10 + int(player_position.y * scale)
        pygame.draw.circle(self.screen, (180, 100, 255), (player_minimap_x, player_minimap_y), 3)

        # Draw revealed zombies (small red dots)
        for zombie in zombies:
            if not zombie.is_hidden:
                zombie_minimap_x = minimap_x + 10 + int(zombie.position.x * scale)
                zombie_minimap_y = minimap_y + 10 + int(zombie.position.y * scale)
                # Only draw if within minimap bounds
                if minimap_x < zombie_minimap_x < minimap_x + minimap_width and minimap_y < zombie_minimap_y < minimap_y + minimap_height:
                    pygame.draw.circle(self.screen, (255, 0, 0), (zombie_minimap_x, zombie_minimap_y), 1)

        # Draw label
        try:
            label_text = self.label_font.render("MAP", True, (255, 153, 0))  # AWS Orange
            self.screen.blit(label_text, (minimap_x + 5, minimap_y - 18))
        except:
            pass

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

    def render_third_party_labels(self, third_parties: List, game_map: Optional[GameMap] = None) -> None:
        """
        Render name labels above 3rd party entities.

        Args:
            third_parties: List of 3rd parties to render labels for
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        for third_party in third_parties:
            # Check visibility based on mode
            is_visible = False
            screen_x, screen_y = 0, 0

            if game_map:
                # Map mode: convert world to screen coordinates
                is_visible = game_map.is_on_screen(third_party.position.x, third_party.position.y, third_party.width, third_party.height)
                if is_visible:
                    screen_x, screen_y = game_map.world_to_screen(third_party.position.x, third_party.position.y)
            else:
                # Classic mode: check screen bounds
                is_visible = -100 < third_party.position.x < self.width + 100
                screen_x = int(third_party.position.x)
                screen_y = int(third_party.position.y)

            if is_visible:
                # Render 3rd party name (e.g., "nOps", "CrowdStrike")
                label_text = third_party.name

                label_surface = self.label_font.render(
                    label_text,
                    True,
                    (255, 215, 0)  # Gold color for 3rd parties
                )

                # Position above the 3rd party
                label_x = int(screen_x + third_party.width // 2 - label_surface.get_width() // 2)
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

    def render_shield(self, entity, game_map: Optional[GameMap] = None, pulse_time: float = 0.0) -> None:
        """
        Render a Zelda-style purple shield around a protected entity.

        Args:
            entity: The protected entity to render shield for
            game_map: Game map for coordinate conversion (None for screen coordinates)
            pulse_time: Time value for pulsing animation
        """
        from shield import render_shield
        
        # Check visibility and get screen position
        is_visible = False
        camera_offset = (0, 0)

        if game_map:
            # Map mode: convert world to screen coordinates
            is_visible = game_map.is_on_screen(entity.position.x, entity.position.y, entity.width, entity.height)
            if is_visible:
                camera_offset = (game_map.camera_x, game_map.camera_y)
        else:
            # Classic mode: check screen bounds
            is_visible = -100 < entity.position.x < self.width + 100

        if not is_visible:
            return

        # Use the shield module to render the small shield accessory
        render_shield(self.screen, entity, camera_offset, pulse_time)

    def render_health_bar(self, entity, game_map: Optional[GameMap] = None) -> None:
        """
        Render a retro-style health bar above an entity.

        Args:
            entity: The entity (zombie or third party) to render health bar for
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        # Only show health bar if entity has taken damage
        if entity.health >= entity.max_health:
            return

        # Check visibility and get screen position
        is_visible = False
        screen_x, screen_y = 0, 0

        if game_map:
            # Map mode: convert world to screen coordinates
            is_visible = game_map.is_on_screen(entity.position.x, entity.position.y, entity.width, entity.height)
            if is_visible:
                screen_x, screen_y = game_map.world_to_screen(entity.position.x, entity.position.y)
        else:
            # Classic mode: check screen bounds
            is_visible = -100 < entity.position.x < self.width + 100
            screen_x = int(entity.position.x)
            screen_y = int(entity.position.y)

        if not is_visible:
            return

        # Health bar dimensions (retro pixel style)
        bar_width = 30
        bar_height = 4
        bar_x = int(screen_x + entity.width // 2 - bar_width // 2)
        bar_y = int(screen_y - 8)  # Position above entity, below label

        # Calculate health percentage
        health_percent = entity.health / entity.max_health

        # Draw background (gray)
        pygame.draw.rect(
            self.screen,
            (128, 128, 128),
            (bar_x, bar_y, bar_width, bar_height)
        )

        # Draw health (red)
        health_width = int(bar_width * health_percent)
        if health_width > 0:
            pygame.draw.rect(
                self.screen,
                (220, 20, 20),
                (bar_x, bar_y, health_width, bar_height)
            )

        # Draw border (black, retro pixel style)
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (bar_x, bar_y, bar_width, bar_height),
            1
        )

    def render_boss(self, boss: Boss, game_map: Optional[GameMap] = None) -> None:
        """
        Render the boss entity with cloud if on cloud.

        Args:
            boss: Boss to render
            game_map: Game map for coordinate conversion (None for screen coordinates)
        """
        if not boss or boss.is_defeated:
            return

        if game_map:
            # Map mode: always render boss if in boss battle (even if slightly off-screen during drop)
            # Check with larger bounds to catch boss during sky drop
            if game_map.is_on_screen(boss.position.x, boss.position.y - 200, boss.width, boss.height + 300):
                screen_x, screen_y = game_map.world_to_screen(boss.position.x, boss.position.y)
                
                # Render cloud if boss is on cloud (during entrance)
                if boss.on_cloud and hasattr(boss, 'cloud_sprite'):
                    cloud_screen_y = screen_y + boss.height + int(boss.cloud_y_offset)
                    cloud_screen_x = screen_x - (boss.cloud_sprite.get_width() - boss.width) // 2
                    self.screen.blit(boss.cloud_sprite, (cloud_screen_x, cloud_screen_y))
                
                # Apply flash effect if active
                if boss.is_flashing:
                    flash_sprite = boss.sprite.copy()
                    flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                    self.screen.blit(flash_sprite, (screen_x, screen_y))
                else:
                    self.screen.blit(boss.sprite, (screen_x, screen_y))
        else:
            # Classic mode: render if on screen
            if -100 < boss.position.x < self.width + 100:
                # Render cloud if boss is on cloud
                if boss.on_cloud and hasattr(boss, 'cloud_sprite'):
                    cloud_y = int(boss.position.y) + boss.height + int(boss.cloud_y_offset)
                    cloud_x = int(boss.position.x) - (boss.cloud_sprite.get_width() - boss.width) // 2
                    self.screen.blit(boss.cloud_sprite, (cloud_x, cloud_y))
                
                if boss.is_flashing:
                    flash_sprite = boss.sprite.copy()
                    flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                    self.screen.blit(flash_sprite, (int(boss.position.x), int(boss.position.y)))
                else:
                    self.screen.blit(boss.sprite, (int(boss.position.x), int(boss.position.y)))

    def render_boss_health_bar(self, boss: Boss, game_map: Optional[GameMap] = None) -> None:
        """
        Render boss health bar at top of screen.

        Args:
            boss: Boss to render health bar for
            game_map: Game map (for coordinate conversion, not used here)
        """
        if not boss or boss.is_defeated:
            return

        # Health bar at top center of screen
        bar_width = 400
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = 20

        # Background (dark gray)
        pygame.draw.rect(self.screen, (64, 64, 64), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill (red gradient)
        health_percent = boss.health / boss.max_health
        health_width = int(bar_width * health_percent)
        if health_width > 0:
            # Red gradient
            for i in range(health_width):
                r = int(255 - (i / health_width) * 75)  # 255 to 180
                color = (r, 0, 0)
                pygame.draw.rect(self.screen, color, (bar_x + i, bar_y, 1, bar_height))
        
        # Gold border
        pygame.draw.rect(self.screen, (255, 215, 0), (bar_x, bar_y, bar_width, bar_height), 2)

        # Boss name above health bar
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(boss.name, True, (255, 215, 0))
        name_x = (self.width - name_text.get_width()) // 2
        name_y = bar_y - 25
        self.screen.blit(name_text, (name_x, name_y))

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
        # Zombies quarantined count
        zombies_text = f"Zombies: Quarantined {game_state.zombies_quarantined}/{game_state.total_zombies}"
        zombies_surface = self.ui_font.render(zombies_text, True, self.ui_text_color)
        self.screen.blit(zombies_surface, (10, 10))

        # 3rd parties blocked count
        third_parties_text = f"3rd Parties: Blocked {game_state.third_parties_blocked}/{game_state.total_third_parties}"
        third_parties_surface = self.ui_font.render(third_parties_text, True, self.ui_text_color)
        self.screen.blit(third_parties_surface, (10, 45))

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

    def render_service_nodes(self, service_nodes: List, game_map: GameMap, pulse_time: float = 0.0) -> None:
        """
        Render AWS service icons with pulsing animation.

        Args:
            service_nodes: List of ServiceNode instances to render
            game_map: Game map for coordinate conversion
            pulse_time: Time value for pulsing animation
        """
        for service_node in service_nodes:
            if game_map.is_on_screen(service_node.position.x, service_node.position.y, 48, 48):
                screen_x = int(service_node.position.x - game_map.camera_x)
                screen_y = int(service_node.position.y - game_map.camera_y)

                # Get appropriate sprite based on protection state
                sprite = service_node.get_current_sprite()

                # Apply pulsing animation if not protected
                if not service_node.protected:
                    # Pulse scale: 1.0 to 1.05 (subtle pulsing effect)
                    pulse_scale = 1.0 + 0.05 * abs(math.sin(pulse_time * 2))

                    # Scale sprite for pulsing effect
                    scaled_size = int(48 * pulse_scale)
                    scaled_sprite = pygame.transform.scale(sprite, (scaled_size, scaled_size))

                    # Center the scaled sprite
                    offset = (scaled_size - 48) // 2
                    self.screen.blit(scaled_sprite, (screen_x - offset, screen_y - offset))
                else:
                    # No animation for protected services
                    self.screen.blit(sprite, (screen_x, screen_y))

    def render_race_timer(self, time_remaining: float, quest_status) -> None:
        """
        Render countdown timer during active race.

        Args:
            time_remaining: Seconds remaining in the race
            quest_status: Current quest status (only show if ACTIVE)
        """
        if quest_status != QuestStatus.ACTIVE:
            return

        # Timer position (top left, under zombie/3rd party counters)
        timer_text = f"⏱  Race Timer: {int(time_remaining)}s"

        # Color based on urgency (red if < 10s, yellow if < 30s, white otherwise)
        if time_remaining < 10:
            color = (255, 50, 50)  # Red
        elif time_remaining < 30:
            color = (255, 200, 0)  # Yellow
        else:
            color = (255, 255, 255)  # White

        timer_surface = self.ui_font.render(timer_text, True, color)

        # Position at top left, under 3rd party counter (y=80)
        timer_x = 10
        timer_y = 80

        # Draw the timer
        self.screen.blit(timer_surface, (timer_x, timer_y))

    def render_hacker(self, hacker, game_map: GameMap) -> None:
        """
        Render the hacker character.

        Args:
            hacker: Hacker instance to render
            game_map: Game map for coordinate conversion
        """
        if not hacker:
            return

        # Check if hacker is on screen
        if game_map.is_on_screen(hacker.position.x, hacker.position.y, hacker.width, hacker.height):
            camera_offset = Vector2(game_map.camera_x, game_map.camera_y)
            hacker.render(self.screen, camera_offset)

    def render_service_hint(self, hint_message: str, hint_timer: float) -> None:
        """
        Render hint message near service icon.

        Args:
            hint_message: The hint text to display
            hint_timer: Timer value (message fades after timer expires)
        """
        if hint_timer <= 0 or not hint_message:
            return

        # Render hint at bottom center of screen
        hint_font = pygame.font.Font(None, 24)
        hint_surface = hint_font.render(hint_message, True, (255, 200, 100))  # Light orange

        hint_x = (self.width - hint_surface.get_width()) // 2
        hint_y = self.height - 80

        # Black outline for readability
        outline_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in outline_offsets:
            outline_surface = hint_font.render(hint_message, True, (0, 0, 0))
            self.screen.blit(outline_surface, (hint_x + dx, hint_y + dy))

        # Draw the hint
        self.screen.blit(hint_surface, (hint_x, hint_y))

    def render_auditor(self, auditor, game_map: GameMap) -> None:
        """
        Render the auditor character with suit appearance.

        Args:
            auditor: Auditor entity
            game_map: Game map for coordinate conversion
        """
        if not auditor:
            return

        # Check if auditor is on screen
        if not game_map.is_on_screen(auditor.position.x, auditor.position.y, auditor.width, auditor.height):
            return

        # Get screen position
        screen_x, screen_y = game_map.world_to_screen(auditor.position.x, auditor.position.y)

        # Draw auditor body (gray suit)
        body_rect = pygame.Rect(
            int(screen_x - auditor.width // 2),
            int(screen_y - auditor.height // 2),
            auditor.width,
            auditor.height
        )
        pygame.draw.rect(self.screen, (80, 80, 80), body_rect)  # Dark gray suit

        # Draw head (lighter gray)
        head_size = auditor.width // 2
        head_x = int(screen_x)
        head_y = int(screen_y - auditor.height // 2 - head_size // 2)
        pygame.draw.circle(self.screen, (120, 120, 120), (head_x, head_y), head_size // 2)

        # Draw clipboard (white rectangle)
        clipboard_width = 12
        clipboard_height = 16
        clipboard_x = int(screen_x + auditor.width // 4)
        clipboard_y = int(screen_y)
        pygame.draw.rect(
            self.screen,
            (240, 240, 240),
            (clipboard_x, clipboard_y, clipboard_width, clipboard_height)
        )
        # Clipboard border
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (clipboard_x, clipboard_y, clipboard_width, clipboard_height),
            1
        )

    def render_admin_roles(self, admin_roles: List, game_map: GameMap, pulse_time: float = 0.0) -> None:
        """
        Render admin role characters with crowns.

        Args:
            admin_roles: List of AdminRole entities
            game_map: Game map for coordinate conversion
            pulse_time: Time value for shield pulsing animation
        """
        for admin_role in admin_roles:
            # Check if on screen
            if not game_map.is_on_screen(admin_role.position.x, admin_role.position.y, admin_role.width, admin_role.height):
                continue

            # Get screen position
            screen_x, screen_y = game_map.world_to_screen(admin_role.position.x, admin_role.position.y)

            # Draw character body (similar to player/zombie)
            body_width = admin_role.width
            body_height = admin_role.height
            
            # Draw legs
            leg_width = body_width // 3
            leg_height = body_height // 2
            left_leg = pygame.Rect(
                int(screen_x - body_width // 4),
                int(screen_y + body_height // 4),
                leg_width,
                leg_height
            )
            right_leg = pygame.Rect(
                int(screen_x - body_width // 4 + leg_width),
                int(screen_y + body_height // 4),
                leg_width,
                leg_height
            )
            
            # Color based on JIT status
            if admin_role.has_jit:
                body_color = (100, 200, 100)  # Green if protected
            else:
                body_color = (180, 140, 60)  # Brown/tan if unprotected
            
            pygame.draw.rect(self.screen, body_color, left_leg)
            pygame.draw.rect(self.screen, body_color, right_leg)
            
            # Draw torso
            torso_rect = pygame.Rect(
                int(screen_x - body_width // 2),
                int(screen_y - body_height // 4),
                body_width,
                body_height // 2
            )
            pygame.draw.rect(self.screen, body_color, torso_rect)
            
            # Draw head
            head_size = body_width // 2
            head_x = int(screen_x)
            head_y = int(screen_y - body_height // 2)
            pygame.draw.circle(self.screen, (220, 180, 140), (head_x, head_y), head_size // 2)  # Skin tone

            # Draw small crown on top of head
            crown_y = int(screen_y - body_height // 2 - head_size // 2 - 2)
            crown_x = int(screen_x)
            
            # Smaller crown (half the previous size)
            crown_points = [
                (crown_x - 6, crown_y),
                (crown_x - 4, crown_y - 4),
                (crown_x - 2, crown_y - 1),
                (crown_x, crown_y - 5),
                (crown_x + 2, crown_y - 1),
                (crown_x + 4, crown_y - 4),
                (crown_x + 6, crown_y),
            ]
            pygame.draw.polygon(self.screen, (255, 215, 0), crown_points)  # Gold
            pygame.draw.polygon(self.screen, (0, 0, 0), crown_points, 1)  # Black outline

            # Draw purple shield if JIT protected
            if admin_role.has_jit:
                from shield import render_shield
                camera_offset = (game_map.camera_x, game_map.camera_y)
                render_shield(self.screen, admin_role, camera_offset, pulse_time)

            # Draw label with permission set name
            try:
                font = pygame.font.Font(None, 16)
                label_text = admin_role.permission_set.name[:20]  # Truncate long names
                label_surface = font.render(label_text, True, (255, 255, 255))
                label_x = int(screen_x - label_surface.get_width() // 2)
                label_y = int(screen_y - admin_role.height // 2 - 25)
                
                # Black outline
                outline_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dx, dy in outline_offsets:
                    outline_surface = font.render(label_text, True, (0, 0, 0))
                    self.screen.blit(outline_surface, (label_x + dx, label_y + dy))
                
                self.screen.blit(label_surface, (label_x, label_y))
            except:
                pass  # Font rendering failed

    def render_jit_quest_message(self, jit_quest_state) -> None:
        """
        Render JIT quest messages.

        Args:
            jit_quest_state: JitQuestState object
        """
        if not jit_quest_state or not jit_quest_state.quest_message:
            return

        if jit_quest_state.quest_message_timer <= 0:
            return

        # Render message bubble
        self.render_message_bubble(jit_quest_state.quest_message)
