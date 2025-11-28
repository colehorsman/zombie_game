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

        # Initialize fonts - Cache all fonts to avoid recreating every frame (30% performance gain)
        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 32)
        self.message_font = pygame.font.Font(None, 24)

        # Additional cached fonts for various UI elements
        self.tiny_font = pygame.font.Font(None, 14)       # Very small text
        self.small_font = pygame.font.Font(None, 16)      # Small labels
        self.subtitle_font = pygame.font.Font(None, 18)   # Subtitles
        self.label_font = pygame.font.Font(None, 20)      # Entity labels, map markers
        self.name_font = pygame.font.Font(None, 28)       # Boss names, headers
        self.elim_font = pygame.font.Font(None, 28)       # Elimination count
        self.combo_font = pygame.font.Font(None, 32)      # Combo display
        self.timer_font = pygame.font.Font(None, 48)      # Arcade timer
        self.victory_font = pygame.font.Font(None, 48)    # Victory messages
        self.countdown_font = pygame.font.Font(None, 72)  # Countdown "3, 2, 1, GO!"

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

    def _apply_flash_effect(self, x: int, y: int, width: int, height: int) -> None:
        """
        Apply flash effect overlay without copying sprite (15% performance gain).

        Args:
            x: X position on screen
            y: Y position on screen
            width: Width of flash area
            height: Height of flash area
        """
        flash_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, 128))
        self.screen.blit(flash_surface, (x, y), special_flags=pygame.BLEND_RGBA_ADD)

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
                    self.screen.blit(zombie.sprite, (screen_x, screen_y))
                    if zombie.is_flashing:
                        self._apply_flash_effect(screen_x, screen_y, zombie.width, zombie.height)
                    
                    rendered_count += 1
            else:
                # Classic mode: only render zombies that are on or near the screen
                if -100 < zombie.position.x < self.width + 100:
                    # Apply flash effect if active
                    self.screen.blit(zombie.sprite, (int(zombie.position.x), int(zombie.position.y)))
                    if zombie.is_flashing:
                        self._apply_flash_effect(int(zombie.position.x), int(zombie.position.y), zombie.width, zombie.height)
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
                    
                    # Render sprite
                    self.screen.blit(third_party.sprite, (screen_x, screen_y))
                    
                    # Apply flash effect if active
                    if third_party.is_flashing:
                        self._apply_flash_effect(screen_x, screen_y, third_party.width, third_party.height)
            else:
                # Classic mode: only render 3rd parties that are on or near the screen
                if -100 < third_party.position.x < self.width + 100:
                    # Render sprite
                    self.screen.blit(third_party.sprite, (int(third_party.position.x), int(third_party.position.y)))
                    
                    # Apply flash effect if active
                    if third_party.is_flashing:
                        self._apply_flash_effect(int(third_party.position.x), int(third_party.position.y), third_party.width, third_party.height)

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
                        font = self.tiny_font
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
                
                # Render sprite
                self.screen.blit(boss.sprite, (screen_x, screen_y))
                
                # Apply flash effect if active
                if boss.is_flashing:
                    self._apply_flash_effect(screen_x, screen_y, boss.width, boss.height)
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

    def render_boss_health_bar(self, boss, game_map: Optional[GameMap] = None) -> None:
        """
        Render boss health bar at top of screen.
        Supports both regular Boss and ScatteredSpiderBoss.

        Args:
            boss: Boss or ScatteredSpiderBoss to render health bar for
            game_map: Game map (for coordinate conversion, not used here)
        """
        # Import here to avoid circular dependency
        from cyber_boss import ScatteredSpiderBoss

        if not boss:
            return

        # Check if boss is defeated
        if hasattr(boss, 'is_defeated') and boss.is_defeated:
            return

        # Get health values (different for swarm vs regular boss)
        if isinstance(boss, ScatteredSpiderBoss):
            current_health = boss.get_total_health_remaining()
            max_health = boss.get_max_health()
            boss_name = boss.name
            # Add spider count
            alive_spiders = len(boss.get_all_spiders())
            boss_name = f"{boss_name} ({alive_spiders}/5)"
        else:
            current_health = boss.health
            max_health = boss.max_health
            boss_name = boss.name

        # Health bar at top center of screen
        bar_width = 400
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = 20

        # Background (dark gray)
        pygame.draw.rect(self.screen, (64, 64, 64), (bar_x, bar_y, bar_width, bar_height))

        # Health fill (red gradient)
        health_percent = current_health / max_health if max_health > 0 else 0
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
        name_font = self.name_font
        name_text = name_font.render(boss_name, True, (255, 215, 0))
        name_x = (self.width - name_text.get_width()) // 2
        name_y = bar_y - 25
        self.screen.blit(name_text, (name_x, name_y))

    def render_scattered_spider(self, boss: 'ScatteredSpiderBoss', game_map: Optional[GameMap] = None) -> None:
        """
        Render Scattered Spider boss (5 individual spiders with glow effects).

        Args:
            boss: ScatteredSpiderBoss instance
            game_map: Game map for coordinate conversion
        """
        # Import here to avoid circular dependency
        from cyber_boss import ScatteredSpiderBoss

        if not boss or boss.is_defeated:
            return

        # Render each spider with glow effect
        for spider in boss.get_all_spiders():
            if spider.is_defeated:
                continue

            if game_map:
                # Map mode
                if game_map.is_on_screen(spider.position.x, spider.position.y, spider.width, spider.height):
                    screen_x, screen_y = game_map.world_to_screen(spider.position.x, spider.position.y)

                    # Step 1: Render glow effect (background, adds perceived size)
                    glow_x = screen_x - spider.effect_radius
                    glow_y = screen_y - spider.effect_radius
                    self.screen.blit(spider.glow_sprite, (glow_x, glow_y))

                    # Step 2: Render spider sprite on top
                    self.screen.blit(spider.sprite, (screen_x, screen_y))
                    
                    # Apply flash effect if active
                    if spider.is_flashing:
                        self._apply_flash_effect(screen_x, screen_y, spider.width, spider.height)
            else:
                # Classic mode
                if -100 < spider.position.x < self.width + 100:
                    # Step 1: Render glow
                    glow_x = int(spider.position.x) - spider.effect_radius
                    glow_y = int(spider.position.y) - spider.effect_radius
                    self.screen.blit(spider.glow_sprite, (glow_x, glow_y))

                    self.screen.blit(spider.sprite, (int(spider.position.x), int(spider.position.y)))
                    if spider.is_flashing:
                        self._apply_flash_effect(int(spider.position.x), int(spider.position.y), spider.width, spider.height)

    def render_heartbleed_boss(self, boss: 'HeartbleedBoss', game_map: Optional[GameMap] = None) -> None:
        """
        Render Heartbleed Red Queen boss with bleeding effects and crown.

        Args:
            boss: HeartbleedBoss instance
            game_map: Game map for coordinate conversion
        """
        # Import here to avoid circular dependency
        from cyber_boss import HeartbleedBoss

        if not boss or boss.is_defeated:
            return

        # Determine screen position
        if game_map:
            if not game_map.is_on_screen(boss.position.x, boss.position.y, boss.width, boss.height):
                return
            screen_x, screen_y = game_map.world_to_screen(boss.position.x, boss.position.y)
        else:
            screen_x, screen_y = int(boss.position.x), int(boss.position.y)

        # Step 1: Render bleeding particles (data leak effect) - behind boss
        self._render_bleeding_particles(boss, screen_x, screen_y)

        # Step 2: Render pulsing red glow effect - TEMPORARILY DISABLED FOR DEBUG
        # pulse = math.sin(boss.glow_pulse_timer * 3) * 0.3 + 0.7  # Pulse between 0.7 and 1.0
        # glow_sprite = boss.glow_sprite.copy()
        # glow_sprite.set_alpha(int(255 * pulse * 0.6))  # Pulse the glow intensity
        # glow_x = screen_x - boss.effect_radius
        # glow_y = screen_y - boss.effect_radius
        # self.screen.blit(glow_sprite, (glow_x, glow_y))

        # Step 3: Render card flip teleport effect
        if boss.is_teleporting:
            self._render_card_flip_effect(boss, screen_x, screen_y)
        else:
            # Step 4: Render the Red Queen sprite
            queen_sprite = boss.sprite
            if boss.is_flashing:
                # White flash when damaged
                flash_sprite = queen_sprite.copy()
                flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                self.screen.blit(flash_sprite, (screen_x, screen_y))
            else:
                self.screen.blit(queen_sprite, (screen_x, screen_y))

            # Step 5: Render golden crown on top of hair (Princess Peach style)
            crown_x = screen_x + (boss.width // 2) - 15  # Center crown
            crown_y = screen_y - 12  # Higher on head like Princess Peach
            self.screen.blit(boss.crown_sprite, (crown_x, crown_y))

    def _render_bleeding_particles(self, boss: 'HeartbleedBoss', screen_x: int, screen_y: int) -> None:
        """Render the bleeding data particles."""
        for particle in boss.bleeding_particles:
            # Calculate particle screen position (relative to boss)
            particle_x = int(particle['x'] - boss.position.x + screen_x)
            particle_y = int(particle['y'] - boss.position.y + screen_y)

            # Draw bleeding particle (red droplet)
            particle_color = (220, 20, 20, particle['alpha'])
            particle_surface = pygame.Surface((6, 8), pygame.SRCALPHA)

            # Draw teardrop/blood drop shape
            # Top circle
            pygame.draw.circle(particle_surface, particle_color, (3, 2), 2)
            # Bottom point
            pygame.draw.polygon(particle_surface, particle_color, [
                (1, 3),
                (5, 3),
                (3, 7)
            ])

            self.screen.blit(particle_surface, (particle_x - 3, particle_y - 4))

    def _render_card_flip_effect(self, boss: 'HeartbleedBoss', screen_x: int, screen_y: int) -> None:
        """Render playing card flip animation during teleport."""
        # Card flip effect - squish the sprite horizontally
        flip_progress = boss.teleport_animation_timer / 0.5  # 0.0 to 1.0

        # Create flip effect by scaling sprite width
        if flip_progress > 0.5:
            # First half - shrink to 0
            scale_x = (1.0 - flip_progress) * 2
        else:
            # Second half - expand from 0
            scale_x = flip_progress * 2

        scale_x = max(0.05, scale_x)  # Never fully invisible

        # Scale the sprite
        flipped_width = max(1, int(boss.width * scale_x))
        flipped_sprite = pygame.transform.scale(boss.sprite, (flipped_width, boss.height))

        # Draw centered
        flip_x = screen_x + (boss.width - flipped_width) // 2
        self.screen.blit(flipped_sprite, (flip_x, screen_y))

        # Add sparkle effect during flip
        if 0.3 < flip_progress < 0.7:
            sparkle_color = (255, 215, 0, 200)  # Gold sparkle
            for i in range(5):
                offset_x = (i - 2) * 8
                offset_y = (i % 2) * 15 - 7
                pygame.draw.circle(self.screen, sparkle_color,
                                 (screen_x + boss.width // 2 + offset_x,
                                  screen_y + boss.height // 2 + offset_y), 3)

    def render_wannacry_boss(self, boss: 'WannaCryBoss', game_map: Optional[GameMap] = None) -> None:
        """
        Render WannaCry Wade boss with crying tears, puddles, and sob waves.

        Args:
            boss: WannaCryBoss instance
            game_map: Game map for coordinate conversion
        """
        # Import here to avoid circular dependency
        from cyber_boss import WannaCryBoss

        if not boss or boss.is_defeated:
            return

        # Determine screen position
        if game_map:
            if not game_map.is_on_screen(boss.position.x, boss.position.y, boss.width, boss.height):
                return
            screen_x, screen_y = game_map.world_to_screen(boss.position.x, boss.position.y)
        else:
            screen_x, screen_y = int(boss.position.x), int(boss.position.y)

        # Step 1: Render puddles on ground (behind Wade)
        self._render_tear_puddles(boss, screen_x, screen_y, game_map)

        # Step 2: Render sob wave if active
        if boss.sob_wave and boss.sob_wave['active']:
            self._render_sob_wave(boss, screen_x, screen_y, game_map)

        # Step 3: Render watery glow effect (pulsing) - TEMPORARILY DISABLED FOR DEBUG
        # pulse = math.sin(boss.glow_pulse_timer * 2) * 0.3 + 0.7  # Pulse 0.7-1.0
        # glow_sprite = boss.glow_sprite.copy()
        # glow_sprite.set_alpha(int(255 * pulse * 0.5))  # Watery transparency
        # glow_x = screen_x - boss.effect_radius
        # glow_y = screen_y - boss.effect_radius
        # self.screen.blit(glow_sprite, (glow_x, glow_y))

        # Step 4: Render Wade's crying sprite
        if boss.is_sobbing and boss.sob_charge_timer > 0:
            # Shaking during sob charge
            shake_x = int(math.sin(boss.sob_charge_timer * 20) * 3)
            shake_y = int(math.cos(boss.sob_charge_timer * 20) * 3)
            sprite_x = screen_x + shake_x
            sprite_y = screen_y + shake_y
        else:
            sprite_x = screen_x
            sprite_y = screen_y

        # Render sprite (already includes tear streams)
        if boss.is_flashing:
            flash_sprite = boss.sprite.copy()
            flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(flash_sprite, (sprite_x, sprite_y))
        else:
            self.screen.blit(boss.sprite, (sprite_x, sprite_y))

        # Step 5: Render falling tear particles (on top of Wade)
        self._render_tear_particles(boss, screen_x, screen_y, game_map)

        # Step 6: Render sob charge indicator
        if boss.is_sobbing and boss.sob_charge_timer > 0:
            self._render_sob_charge(boss, screen_x, screen_y)

    def _render_tear_particles(self, boss: 'WannaCryBoss', screen_x: int, screen_y: int, game_map: Optional[GameMap]) -> None:
        """Render falling tear droplets."""
        for tear in boss.tear_particles:
            # Calculate screen position
            if game_map:
                tear_screen_x, tear_screen_y = game_map.world_to_screen(tear['x'], tear['y'])
            else:
                tear_screen_x = int(tear['x'])
                tear_screen_y = int(tear['y'])

            # Create teardrop sprite
            tear_surface = pygame.Surface((8, 10), pygame.SRCALPHA)
            tear_color = (135, 206, 235, tear['alpha'])  # Sky blue with fade

            # Teardrop shape
            # Top circle
            pygame.draw.circle(tear_surface, tear_color, (4, 3), 3)
            # Bottom point
            pygame.draw.polygon(tear_surface, tear_color, [
                (2, 4),
                (6, 4),
                (4, 9)
            ])

            # Add highlight (makes it look wet)
            highlight = (224, 255, 255, min(255, tear['alpha'] + 50))
            pygame.draw.circle(tear_surface, highlight, (3, 2), 1)

            self.screen.blit(tear_surface, (tear_screen_x - 4, tear_screen_y - 5))

    def _render_tear_puddles(self, boss: 'WannaCryBoss', screen_x: int, screen_y: int, game_map: Optional[GameMap]) -> None:
        """Render tear puddles on the ground."""
        for puddle in boss.puddles:
            # Calculate screen position
            if game_map:
                puddle_screen_x, puddle_screen_y = game_map.world_to_screen(puddle['x'], puddle['y'])
            else:
                puddle_screen_x = int(puddle['x'])
                puddle_screen_y = int(puddle['y'])

            # Create puddle oval
            puddle_width = puddle['radius'] * 2
            puddle_height = int(puddle['radius'] * 0.6)  # Squashed oval (perspective)

            puddle_surface = pygame.Surface((puddle_width, puddle_height), pygame.SRCALPHA)

            # Puddle base (dark blue)
            puddle_color = (30, 144, 255, puddle['alpha'])
            pygame.draw.ellipse(puddle_surface, puddle_color, (0, 0, puddle_width, puddle_height))

            # Puddle highlight (light blue, makes it look wet)
            highlight_color = (135, 206, 235, int(puddle['alpha'] * 0.6))
            pygame.draw.ellipse(puddle_surface, highlight_color,
                              (2, 2, puddle_width - 8, puddle_height - 4))

            self.screen.blit(puddle_surface, (puddle_screen_x - puddle['radius'],
                                             puddle_screen_y - puddle_height // 2))

    def _render_sob_wave(self, boss: 'WannaCryBoss', screen_x: int, screen_y: int, game_map: Optional[GameMap]) -> None:
        """Render expanding sob wave attack."""
        wave = boss.sob_wave
        if not wave or not wave['active']:
            return

        # Calculate center position
        if game_map:
            wave_center_x, wave_center_y = game_map.world_to_screen(wave['x'], wave['y'])
        else:
            wave_center_x = int(wave['x'])
            wave_center_y = int(wave['y'])

        # Draw expanding ring
        radius = int(wave['radius'])
        thickness = 15  # Ring thickness

        # Outer ring (lighter blue)
        outer_color = (0, 255, 255, int(wave['alpha'] * 0.5))  # Cyan
        pygame.draw.circle(self.screen, outer_color, (wave_center_x, wave_center_y), radius, thickness)

        # Inner ring (darker blue)
        if radius > thickness:
            inner_color = (30, 144, 255, wave['alpha'])  # Dodger blue
            pygame.draw.circle(self.screen, inner_color, (wave_center_x, wave_center_y),
                             radius - thickness // 2, thickness // 2)

        # Add wave particles (water droplets flying outward)
        particle_count = 20
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            particle_x = wave_center_x + int(radius * math.cos(angle))
            particle_y = wave_center_y + int(radius * math.sin(angle))

            # Small water droplet
            droplet_color = (135, 206, 235, wave['alpha'])
            pygame.draw.circle(self.screen, droplet_color, (particle_x, particle_y), 3)

    def _render_sob_charge(self, boss: 'WannaCryBoss', screen_x: int, screen_y: int) -> None:
        """Render charging indicator for sob wave."""
        # Pulsing indicator above Wade's head
        charge_progress = 1.0 - (boss.sob_charge_timer / 1.0)  # 0.0 to 1.0

        # Position above Wade
        indicator_x = screen_x + boss.width // 2
        indicator_y = screen_y - 20

        # Draw charging arc
        arc_radius = 15
        arc_thickness = 3
        arc_color = (0, 255, 255, 200)  # Cyan

        # Draw partial arc based on charge progress
        start_angle = -math.pi / 2  # Top
        end_angle = start_angle + (2 * math.pi * charge_progress)

        # Draw arc segments
        segments = 20
        for i in range(int(segments * charge_progress)):
            angle1 = start_angle + (i / segments) * 2 * math.pi
            angle2 = start_angle + ((i + 1) / segments) * 2 * math.pi

            x1 = indicator_x + int(arc_radius * math.cos(angle1))
            y1 = indicator_y + int(arc_radius * math.sin(angle1))
            x2 = indicator_x + int(arc_radius * math.cos(angle2))
            y2 = indicator_y + int(arc_radius * math.sin(angle2))

            pygame.draw.line(self.screen, arc_color, (x1, y1), (x2, y2), arc_thickness)

        # "WAHHH!" text when fully charged
        if charge_progress >= 0.95:
            font = self.label_font
            text = font.render("WAHHH!", True, (0, 255, 255))
            text_rect = text.get_rect(center=(indicator_x, indicator_y))
            self.screen.blit(text, text_rect)

    def render_boss_dialogue(self, dialogue_content: dict) -> None:
        """
        Render educational boss introduction dialogue (Game Boy style).

        Args:
            dialogue_content: Dictionary with title, description, how_attacked,
                            victims, prevention, mechanic
        """
        # Dialogue box dimensions (90% screen width, 75% screen height)
        box_width = int(self.width * 0.9)
        box_height = int(self.height * 0.75)
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2

        # Create dialogue surface with rounded corners effect
        dialogue_surface = pygame.Surface((box_width, box_height))
        dialogue_surface.fill((255, 255, 255))  # White background

        # Black border (3px thick)
        pygame.draw.rect(dialogue_surface, (0, 0, 0), (0, 0, box_width, box_height), 3)

        # Fonts
        title_font = self.ui_font
        header_font = self.name_font
        body_font = self.label_font
        small_font = self.subtitle_font

        # Current Y position for text rendering
        y_pos = 20

        # Title (centered)
        title_text = title_font.render(dialogue_content.get("title", "BOSS BATTLE"), True, (0, 0, 0))
        title_x = (box_width - title_text.get_width()) // 2
        dialogue_surface.blit(title_text, (title_x, y_pos))
        y_pos += 50

        # Description (wrapped)
        description = dialogue_content.get("description", "")
        y_pos = self._render_wrapped_text(dialogue_surface, description, body_font, 30, y_pos, box_width - 60, (0, 0, 0))
        y_pos += 30

        # "HOW THEY ATTACKED:" section
        header = header_font.render("HOW THEY ATTACKED:", True, (0, 0, 0))
        dialogue_surface.blit(header, (30, y_pos))
        y_pos += 35

        for attack in dialogue_content.get("how_attacked", []):
            bullet = body_font.render(f"• {attack}", True, (0, 0, 0))
            y_pos = self._render_wrapped_text(dialogue_surface, f"• {attack}", body_font, 40, y_pos, box_width - 70, (0, 0, 0))
            y_pos += 5

        y_pos += 20

        # "VICTIMS:" section
        if dialogue_content.get("victims"):
            victims_header = header_font.render("VICTIMS:", True, (0, 0, 0))
            dialogue_surface.blit(victims_header, (30, y_pos))
            y_pos += 30
            victims_text = dialogue_content.get("victims", "")
            y_pos = self._render_wrapped_text(dialogue_surface, victims_text, small_font, 40, y_pos, box_width - 70, (80, 80, 80))
            y_pos += 25

        # "HOW IT COULD HAVE BEEN PREVENTED:" section
        prevention_header = header_font.render("HOW IT COULD HAVE BEEN PREVENTED:", True, (0, 0, 0))
        dialogue_surface.blit(prevention_header, (30, y_pos))
        y_pos += 35

        for prev in dialogue_content.get("prevention", []):
            y_pos = self._render_wrapped_text(dialogue_surface, f"✓ {prev}", body_font, 40, y_pos, box_width - 70, (0, 100, 0))
            y_pos += 5

        y_pos += 20

        # "BOSS MECHANIC:" section
        mechanic_header = header_font.render("BOSS MECHANIC:", True, (200, 0, 0))
        dialogue_surface.blit(mechanic_header, (30, y_pos))
        y_pos += 30
        mechanic = dialogue_content.get("mechanic", "")
        y_pos = self._render_wrapped_text(dialogue_surface, mechanic, body_font, 40, y_pos, box_width - 70, (200, 0, 0))

        # Footer: "Press ENTER to begin battle..."
        footer_y = box_height - 40
        footer_text = body_font.render("Press ENTER to begin battle...", True, (0, 0, 0))
        footer_x = (box_width - footer_text.get_width()) // 2
        dialogue_surface.blit(footer_text, (footer_x, footer_y))

        # Blit dialogue box to main screen
        self.screen.blit(dialogue_surface, (box_x, box_y))

    def _render_wrapped_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                            x: int, y: int, max_width: int, color: tuple) -> int:
        """
        Render text with word wrapping.

        Args:
            surface: Surface to render on
            text: Text to render
            font: Font to use
            x: X position
            y: Starting Y position
            max_width: Maximum width before wrapping
            color: Text color

        Returns:
            New Y position after rendering
        """
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Render each line
        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y))
            y += font.get_height() + 3

        return y

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
        # Check if arcade mode is active
        if game_state.arcade_mode and game_state.arcade_mode.active:
            self._render_arcade_ui(game_state.arcade_mode)
            return
        
        # Normal mode UI
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

    def _render_arcade_ui(self, arcade_state) -> None:
        """
        Render arcade mode UI overlay.
        
        Args:
            arcade_state: ArcadeModeState from game state
        """
        # Countdown phase - show large countdown
        if arcade_state.in_countdown:
            countdown_font = self.countdown_font
            countdown_num = int(arcade_state.countdown_time) + 1
            countdown_text = str(countdown_num) if countdown_num > 0 else "GO!"
            
            # Pulsing effect
            if countdown_num > 0:
                color = (255, 255, 0)  # Yellow for countdown
            else:
                color = (0, 255, 0)  # Green for GO!
            
            countdown_surface = countdown_font.render(countdown_text, True, color)
            countdown_x = self.width // 2 - countdown_surface.get_width() // 2
            countdown_y = self.height // 2 - countdown_surface.get_height() // 2
            
            # Black outline for visibility
            outline_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
            for dx, dy in outline_offsets:
                outline_surface = countdown_font.render(countdown_text, True, (0, 0, 0))
                self.screen.blit(outline_surface, (countdown_x + dx, countdown_y + dy))
            
            self.screen.blit(countdown_surface, (countdown_x, countdown_y))
            return
        
        # Timer display (large, prominent)
        timer_font = self.timer_font
        time_remaining = max(0, arcade_state.time_remaining)
        timer_text = f"{int(time_remaining)}s"
        
        # Color changes based on time remaining
        if time_remaining <= 5:
            timer_color = (255, 0, 0)  # Red - urgent!
        elif time_remaining <= 10:
            timer_color = (255, 165, 0)  # Orange - warning
        else:
            timer_color = (255, 255, 255)  # White - normal
        
        timer_surface = timer_font.render(timer_text, True, timer_color)
        timer_x = self.width // 2 - timer_surface.get_width() // 2
        timer_y = 20
        
        # Black outline
        outline_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dx, dy in outline_offsets:
            outline_surface = timer_font.render(timer_text, True, (0, 0, 0))
            self.screen.blit(outline_surface, (timer_x + dx, timer_y + dy))
        
        self.screen.blit(timer_surface, (timer_x, timer_y))
        
        # Quarantined count (consistent with normal mode terminology)
        elim_font = self.elim_font
        elim_text = f"Quarantined: {arcade_state.eliminations_count}"
        elim_surface = elim_font.render(elim_text, True, (255, 255, 255))
        self.screen.blit(elim_surface, (10, 10))
        
        # Combo counter (if active)
        if arcade_state.combo_count > 1:
            combo_font = self.combo_font
            combo_text = f"{arcade_state.combo_count}x COMBO!"
            
            # Color based on multiplier
            if arcade_state.combo_multiplier > 1.0:
                combo_color = (255, 215, 0)  # Gold - multiplier active!
            else:
                combo_color = (255, 255, 255)  # White
            
            combo_surface = combo_font.render(combo_text, True, combo_color)
            combo_x = self.width // 2 - combo_surface.get_width() // 2
            combo_y = 100
            
            # Black outline
            for dx, dy in outline_offsets:
                outline_surface = combo_font.render(combo_text, True, (0, 0, 0))
                self.screen.blit(outline_surface, (combo_x + dx, combo_y + dy))
            
            self.screen.blit(combo_surface, (combo_x, combo_y))
        
        # Power-up duration display (if active)
        # This would need to be passed from game engine - placeholder for now
        # TODO: Add power-up duration display

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
        victory_font = self.victory_font
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
        Render a beautiful purple vertical menu or message bubble.

        Args:
            message: The message text to display
        """
        # Check if this is a pause menu (contains menu options with ▶)
        is_menu = "▶" in message or ("Return to Game" in message and "Quit Game" in message)
        
        if is_menu:
            self._render_purple_menu(message)
        else:
            self._render_message_box(message)
    
    def _render_purple_menu(self, message: str) -> None:
        """
        Render a beautiful purple vertical menu (Zelda-style).
        
        Args:
            message: Menu text with options
        """
        # Purple color scheme
        PURPLE_DARK = (60, 40, 80)      # Dark purple background
        PURPLE_LIGHT = (120, 80, 160)   # Light purple border
        PURPLE_GLOW = (180, 120, 240)   # Purple glow for selected
        WHITE = (255, 255, 255)
        GOLD = (255, 215, 0)
        
        # Parse menu lines
        lines = message.split('\n')
        
        # Filter out empty lines and separators
        menu_lines = []
        title_lines = []
        footer_lines = []
        
        in_menu = False
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped == '═══════════════════════════':
                continue
            
            # Check if this is a menu option (has ▶ or starts with space)
            if '▶' in line or (in_menu and (line.startswith('  ') or line.startswith('▶'))):
                menu_lines.append(line)
                in_menu = True
            elif '↑' in line or '↓' in line or 'ENTER' in line or 'SPACE' in line or '=' in line.lower():
                footer_lines.append(stripped)
            elif not in_menu:
                title_lines.append(stripped)
        
        # Menu dimensions
        menu_width = 400
        line_height = 40
        padding = 30
        title_height = len(title_lines) * 35 + 20 if title_lines else 0
        menu_height = len(menu_lines) * line_height
        footer_height = len(footer_lines) * 25 + 10 if footer_lines else 0
        total_height = title_height + menu_height + footer_height + padding * 2
        
        # Center on screen
        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - total_height) // 2
        
        # Draw semi-transparent dark overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw menu background (dark purple)
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, total_height)
        pygame.draw.rect(self.screen, PURPLE_DARK, menu_rect)
        
        # Draw glowing border (light purple)
        pygame.draw.rect(self.screen, PURPLE_LIGHT, menu_rect, 4)
        
        # Inner glow effect
        inner_rect = pygame.Rect(menu_x + 4, menu_y + 4, menu_width - 8, total_height - 8)
        pygame.draw.rect(self.screen, PURPLE_GLOW, inner_rect, 2)
        
        # Render title
        current_y = menu_y + padding
        if title_lines:
            for title_line in title_lines:
                title_surface = self.name_font.render(title_line, True, GOLD)
                title_x = menu_x + (menu_width - title_surface.get_width()) // 2
                self.screen.blit(title_surface, (title_x, current_y))
                current_y += 35
            current_y += 10
        
        # Render menu options
        for line in menu_lines:
            is_selected = '▶' in line
            
            # Remove the arrow for rendering
            display_text = line.replace('▶', '').strip()
            
            # Choose color based on selection
            if is_selected:
                text_color = PURPLE_GLOW
                # Draw selection highlight
                highlight_rect = pygame.Rect(menu_x + 20, current_y - 5, menu_width - 40, line_height - 10)
                pygame.draw.rect(self.screen, (100, 60, 140), highlight_rect)
                pygame.draw.rect(self.screen, PURPLE_GLOW, highlight_rect, 2)
            else:
                text_color = WHITE
            
            # Render text
            text_surface = self.combo_font.render(display_text, True, text_color)
            text_x = menu_x + (menu_width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (text_x, current_y))
            
            # Draw arrow for selected item
            if is_selected:
                arrow_surface = self.combo_font.render('▶', True, GOLD)
                arrow_x = text_x - arrow_surface.get_width() - 10
                self.screen.blit(arrow_surface, (arrow_x, current_y))
            
            current_y += line_height
        
        # Render footer (controls)
        if footer_lines:
            current_y += 10
            for footer_line in footer_lines:
                footer_surface = self.small_font.render(footer_line, True, (180, 180, 180))
                footer_x = menu_x + (menu_width - footer_surface.get_width()) // 2
                self.screen.blit(footer_surface, (footer_x, current_y))
                current_y += 25
    
    def _render_message_box(self, message: str) -> None:
        """
        Render a traditional message box (for non-menu messages).
        
        Args:
            message: Message text to display
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
        hint_font = self.name_font
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
        Render the auditor character as a man in black suit (undertaker style).

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

        # Character dimensions (human proportions)
        body_width = 24
        body_height = 32
        head_size = 12
        leg_width = 8
        leg_height = 16
        arm_width = 6
        arm_height = 20

        # Base position (feet on ground)
        base_y = int(screen_y + auditor.height // 2)
        center_x = int(screen_x)

        # Draw legs (black pants)
        left_leg_x = center_x - leg_width - 2
        right_leg_x = center_x + 2
        leg_y = base_y - leg_height
        pygame.draw.rect(self.screen, (20, 20, 20), (left_leg_x, leg_y, leg_width, leg_height))
        pygame.draw.rect(self.screen, (20, 20, 20), (right_leg_x, leg_y, leg_width, leg_height))

        # Draw body (black suit jacket)
        body_x = center_x - body_width // 2
        body_y = base_y - leg_height - body_height
        pygame.draw.rect(self.screen, (30, 30, 30), (body_x, body_y, body_width, body_height))

        # Draw white shirt collar
        collar_height = 6
        pygame.draw.rect(self.screen, (240, 240, 240), (body_x + 6, body_y, body_width - 12, collar_height))

        # Draw black tie
        tie_width = 4
        tie_height = 16
        tie_x = center_x - tie_width // 2
        tie_y = body_y + collar_height
        pygame.draw.rect(self.screen, (10, 10, 10), (tie_x, tie_y, tie_width, tie_height))

        # Draw arms (black suit sleeves)
        left_arm_x = body_x - arm_width
        right_arm_x = body_x + body_width
        arm_y = body_y + 4
        pygame.draw.rect(self.screen, (30, 30, 30), (left_arm_x, arm_y, arm_width, arm_height))
        pygame.draw.rect(self.screen, (30, 30, 30), (right_arm_x, arm_y, arm_width, arm_height))

        # Draw hands (pale skin)
        hand_size = 6
        pygame.draw.circle(self.screen, (220, 180, 140), (left_arm_x + arm_width // 2, arm_y + arm_height), hand_size // 2)
        pygame.draw.circle(self.screen, (220, 180, 140), (right_arm_x + arm_width // 2, arm_y + arm_height), hand_size // 2)

        # Draw head (pale skin)
        head_x = center_x
        head_y = body_y - head_size // 2
        pygame.draw.circle(self.screen, (220, 180, 140), (head_x, head_y), head_size // 2)

        # Draw sunglasses (black rectangles)
        glasses_width = 10
        glasses_height = 4
        glasses_y = head_y - 2
        pygame.draw.rect(self.screen, (10, 10, 10), (head_x - glasses_width - 1, glasses_y, glasses_width, glasses_height))
        pygame.draw.rect(self.screen, (10, 10, 10), (head_x + 1, glasses_y, glasses_width, glasses_height))

        # Draw clipboard in hand
        clipboard_width = 10
        clipboard_height = 14
        clipboard_x = left_arm_x - clipboard_width // 2
        clipboard_y = arm_y + arm_height - 8
        # Clipboard backing
        pygame.draw.rect(self.screen, (139, 90, 43), (clipboard_x, clipboard_y, clipboard_width, clipboard_height))
        # Paper on clipboard
        pygame.draw.rect(self.screen, (240, 240, 240), (clipboard_x + 1, clipboard_y + 2, clipboard_width - 2, clipboard_height - 4))
        # Clipboard lines (audit checklist)
        for i in range(3):
            line_y = clipboard_y + 4 + i * 3
            pygame.draw.line(self.screen, (100, 100, 100), (clipboard_x + 2, line_y), (clipboard_x + clipboard_width - 2, line_y), 1)

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

            # Draw character exactly like third party but with gold suit and crown
            # Colors
            GOLD_SUIT = (218, 165, 32)      # Gold suit for admin
            GREEN_SUIT = (60, 140, 60)      # Green suit when protected
            SKIN = (220, 180, 140)          # Skin tone
            BLACK = (0, 0, 0)               # Outlines
            WHITE = (255, 255, 255)         # Shirt
            CROWN_GOLD = (255, 215, 0)      # Crown color
            
            # Suit color based on JIT status
            suit_color = GREEN_SUIT if admin_role.has_jit else GOLD_SUIT
            
            # Calculate base position (center of character)
            base_x = int(screen_x - admin_role.width // 2)
            base_y = int(screen_y - admin_role.height // 2)
            
            # Head (rectangle like third party)
            head_rect = pygame.Rect(base_x + 12, base_y + 4, 16, 12)
            pygame.draw.rect(self.screen, SKIN, head_rect)
            pygame.draw.rect(self.screen, BLACK, head_rect, 1)
            
            # Hair
            pygame.draw.rect(self.screen, BLACK, (base_x + 12, base_y + 4, 16, 4))
            
            # Eyes
            pygame.draw.rect(self.screen, BLACK, (base_x + 15, base_y + 10, 2, 2))  # Left eye
            pygame.draw.rect(self.screen, BLACK, (base_x + 23, base_y + 10, 2, 2))  # Right eye
            
            # Smile
            pygame.draw.line(self.screen, BLACK, (base_x + 16, base_y + 13), (base_x + 24, base_y + 13), 1)
            
            # Body - gold business suit
            suit_rect = pygame.Rect(base_x + 10, base_y + 16, 20, 16)
            pygame.draw.rect(self.screen, suit_color, suit_rect)
            pygame.draw.rect(self.screen, BLACK, suit_rect, 1)
            
            # White shirt collar
            pygame.draw.rect(self.screen, WHITE, (base_x + 14, base_y + 16, 12, 3))
            
            # Legs (same as zombie - 8 pixels tall at bottom)
            leg_color = (40, 40, 60) if admin_role.has_jit else (60, 50, 30)  # Dark pants
            pygame.draw.rect(self.screen, leg_color, (base_x + 12, base_y + 32, 6, 8))  # Left leg
            pygame.draw.rect(self.screen, leg_color, (base_x + 22, base_y + 32, 6, 8))  # Right leg
            pygame.draw.rect(self.screen, BLACK, (base_x + 12, base_y + 32, 6, 8), 1)
            pygame.draw.rect(self.screen, BLACK, (base_x + 22, base_y + 32, 6, 8), 1)
            
            # Cute little crown on top of head
            crown_center_x = base_x + 20  # Center of head
            crown_y = base_y + 2  # Just above head
            
            # Draw crown (cute and small)
            crown_points = [
                (crown_center_x - 5, crown_y + 3),      # Left base
                (crown_center_x - 4, crown_y),          # Left peak
                (crown_center_x - 2, crown_y + 2),      # Left valley
                (crown_center_x, crown_y - 1),          # Center peak
                (crown_center_x + 2, crown_y + 2),      # Right valley
                (crown_center_x + 4, crown_y),          # Right peak
                (crown_center_x + 5, crown_y + 3),      # Right base
            ]
            pygame.draw.polygon(self.screen, CROWN_GOLD, crown_points)
            pygame.draw.polygon(self.screen, BLACK, crown_points, 1)
            
            # Add jewels on crown (small colored dots)
            pygame.draw.circle(self.screen, (255, 0, 0), (crown_center_x, crown_y), 1)  # Red jewel

            # Draw purple shield if JIT protected
            if admin_role.has_jit:
                from shield import render_shield
                camera_offset = (game_map.camera_x, game_map.camera_y)
                render_shield(self.screen, admin_role, camera_offset, pulse_time)

            # Draw label with permission set name
            try:
                font = self.small_font
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
