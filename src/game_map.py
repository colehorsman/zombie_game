"""Map system for navigating the AWS re:invent floorplan."""

import os
import pygame
import random
from typing import List, Tuple, Optional
from models import Vector2
from zombie import Zombie


class GameMap:
    """Handles the floorplan map, camera, and zombie placement."""

    def __init__(self, map_image_path: str, screen_width: int, screen_height: int):
        """
        Initialize the game map.

        Args:
            map_image_path: Path to the floorplan image
            screen_width: Width of the game viewport
            screen_height: Height of the game viewport
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Create custom AWS re:invent themed floorplan
        print("Creating AWS re:invent themed floorplan...")
        self._create_placeholder_map()
        print(f"Created custom floorplan: {self.map_width}x{self.map_height}")

        # Camera position (top-left corner of viewport)
        self.camera_x = 0
        self.camera_y = 0

        # Zombie reveal radius (pixels) - smaller radius means you have to get closer
        self.reveal_radius = 60  # Reduced from 80 to make hunting more challenging

    def _create_placeholder_map(self) -> None:
        """Create an AWS re:invent themed floorplan."""
        self.map_width = 3600  # Increased from 2400 for more zombie space
        self.map_height = 2700  # Increased from 1800 for more zombie space
        self.map_surface = pygame.Surface((self.map_width, self.map_height))

        # AWS Color palette (retro 8-bit style)
        AWS_ORANGE = (255, 153, 0)
        DARK_BLUE = (35, 47, 62)
        LIGHT_BLUE = (146, 186, 211)
        AISLE_COLOR = (200, 220, 230)  # Light blue for walkable aisles
        BOOTH_COLOR = (70, 90, 110)     # Dark blue-grey for booths
        TEXT_COLOR = (255, 255, 255)    # White text
        ACCENT_COLOR = (255, 200, 100)  # Warm accent

        # Background - main floor
        self.map_surface.fill(AISLE_COLOR)

        # Define exhibit areas with labels - scaled 1.5x for bigger map
        areas = [
            # (x, y, width, height, "Label", color)
            (150, 150, 750, 600, "Security\nNeighborhood", BOOTH_COLOR),
            (1050, 150, 750, 600, "Serverless\nZone", BOOTH_COLOR),
            (1950, 150, 750, 600, "AI/ML\nPavilion", BOOTH_COLOR),

            (150, 900, 600, 750, "Developer\nLounge", (90, 110, 140)),
            (900, 900, 900, 450, "Builders Fair", AWS_ORANGE),
            (1950, 900, 750, 450, "Container\nVillage", BOOTH_COLOR),

            (150, 1800, 750, 600, "Data &\nAnalytics", BOOTH_COLOR),
            (1050, 1500, 750, 900, "AWS Village\n(Main Stage)", (50, 70, 100)),
            (1950, 1500, 750, 900, "Expo\nShowfloor", BOOTH_COLOR),

            (2850, 150, 600, 1050, "Networking\nHub", BOOTH_COLOR),
            (2850, 1350, 600, 1050, "Gaming &\nMedia", BOOTH_COLOR),
        ]

        # Draw areas
        for x, y, w, h, label, color in areas:
            # Draw booth rectangle
            pygame.draw.rect(self.map_surface, color, (x, y, w, h))
            # Draw border
            pygame.draw.rect(self.map_surface, DARK_BLUE, (x, y, w, h), 3)

            # Add label
            self._draw_text_centered(label, x + w//2, y + h//2, TEXT_COLOR, size=32)

        # Draw AWS logo/branding areas
        self._draw_aws_branding()

        # Add directional markers
        self._draw_directional_markers()

    def _draw_text_centered(self, text: str, x: int, y: int, color: tuple, size: int = 24) -> None:
        """Draw centered text with optional multi-line support."""
        try:
            font = pygame.font.Font(None, size)
            lines = text.split('\n')
            total_height = len(lines) * size
            start_y = y - total_height // 2

            for i, line in enumerate(lines):
                text_surface = font.render(line, True, color)
                text_rect = text_surface.get_rect(center=(x, start_y + i * size + size // 2))
                self.map_surface.blit(text_surface, text_rect)
        except:
            pass  # Fallback if font rendering fails

    def _draw_aws_branding(self) -> None:
        """Draw AWS branding elements on the map."""
        AWS_ORANGE = (255, 153, 0)
        DARK_BLUE = (35, 47, 62)

        # Draw "AWS re:Invent 2024" title at top
        try:
            title_font = pygame.font.Font(None, 64)
            title_text = "AWS re:Invent 2024"
            title_surface = title_font.render(title_text, True, AWS_ORANGE)
            title_rect = title_surface.get_rect(center=(self.map_width // 2, 40))

            # Draw shadow
            shadow_surface = title_font.render(title_text, True, DARK_BLUE)
            self.map_surface.blit(shadow_surface, (title_rect.x + 3, title_rect.y + 3))
            # Draw text
            self.map_surface.blit(title_surface, title_rect)
        except:
            pass

        # Draw cloud decorations in corners
        self._draw_cloud(120, 50, 60, (255, 255, 255))
        self._draw_cloud(self.map_width - 120, 50, 60, (255, 255, 255))
        self._draw_cloud(120, self.map_height - 50, 60, (255, 255, 255))
        self._draw_cloud(self.map_width - 120, self.map_height - 50, 60, (255, 255, 255))

    def _draw_cloud(self, x: int, y: int, size: int, color: tuple) -> None:
        """Draw a simple pixelated cloud shape."""
        # Simple cloud using circles
        radius = size // 3
        pygame.draw.circle(self.map_surface, color, (x - radius, y), radius)
        pygame.draw.circle(self.map_surface, color, (x + radius, y), radius)
        pygame.draw.circle(self.map_surface, color, (x, y - radius//2), int(radius * 1.2))
        pygame.draw.rect(self.map_surface, color, (x - radius, y, radius * 2, radius))

    def _draw_directional_markers(self) -> None:
        """Draw entrance and directional markers."""
        DARK_BLUE = (35, 47, 62)
        AWS_ORANGE = (255, 153, 0)

        # Draw "ENTRANCE" marker at bottom center
        entrance_x = self.map_width // 2
        entrance_y = self.map_height - 80

        # Entrance arrow pointing down
        pygame.draw.polygon(self.map_surface, AWS_ORANGE, [
            (entrance_x, entrance_y + 30),
            (entrance_x - 20, entrance_y),
            (entrance_x + 20, entrance_y)
        ])

        try:
            font = pygame.font.Font(None, 36)
            entrance_text = font.render("ENTRANCE", True, DARK_BLUE)
            entrance_rect = entrance_text.get_rect(center=(entrance_x, entrance_y - 20))
            self.map_surface.blit(entrance_text, entrance_rect)
        except:
            pass

    def _apply_8bit_style(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Apply 8-bit retro style effects to the map image.

        Args:
            surface: Original pygame surface

        Returns:
            Processed surface with 8-bit style
        """
        width = surface.get_width()
        height = surface.get_height()

        # Step 1: Pixelate by scaling down
        pixelate_factor = 4  # How much to pixelate (higher = more pixelated)
        small_width = width // pixelate_factor
        small_height = height // pixelate_factor

        # Scale down (this creates the pixelation effect)
        small_surface = pygame.transform.scale(surface, (small_width, small_height))

        # Step 2: Reduce color palette on the SMALL surface (much faster!)
        retro_small = self._reduce_color_palette(small_surface)

        # Step 3: Scale back up to original size (keeps the pixelated, retro look)
        retro_surface = pygame.transform.scale(retro_small, (width, height))

        return retro_surface

    def _reduce_color_palette(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Reduce the color palette to create a retro 8-bit look.

        Args:
            surface: Input pygame surface

        Returns:
            Surface with reduced color palette
        """
        width = surface.get_width()
        height = surface.get_height()

        # Create a new surface
        new_surface = surface.copy()

        # Define 8-bit color palette (Game Boy style with some variation)
        palette = [
            (15, 56, 15),      # Dark green (walls/dark areas)
            (48, 98, 48),      # Medium green
            (139, 172, 15),    # Light green (floors)
            (155, 188, 15),    # Lightest green (highlights)
            (200, 200, 200),   # Light gray (text/details)
            (100, 100, 100),   # Dark gray (shadows)
        ]

        # Process each pixel and map to nearest palette color
        # Note: This is slow for large images, but works without numpy
        for x in range(width):
            for y in range(height):
                # Get the current pixel color
                color = surface.get_at((x, y))
                r, g, b = color[:3]

                # Find nearest color in palette
                min_distance = float('inf')
                closest_color = palette[0]

                for palette_color in palette:
                    # Calculate color distance
                    distance = ((r - palette_color[0]) ** 2 +
                               (g - palette_color[1]) ** 2 +
                               (b - palette_color[2]) ** 2)

                    if distance < min_distance:
                        min_distance = distance
                        closest_color = palette_color

                # Set the new pixel color
                new_surface.set_at((x, y), closest_color)

        return new_surface

    def get_random_position(self) -> Vector2:
        """
        Get a random position on the map.

        Returns:
            Random Vector2 position on the map
        """
        # Add some margin from edges
        margin = 100
        x = random.uniform(margin, self.map_width - margin)
        y = random.uniform(margin, self.map_height - margin)
        return Vector2(x, y)

    def is_walkable(self, x: int, y: int) -> bool:
        """
        Check if a position is in a walkable area (aisle) vs a blocked area (booth).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the position is walkable (light colors), False if blocked (dark colors)
        """
        # Clamp to map bounds
        x = max(0, min(int(x), self.map_width - 1))
        y = max(0, min(int(y), self.map_height - 1))

        # Get the pixel color at this position
        color = self.map_surface.get_at((x, y))
        r, g, b = color[:3]

        # Calculate brightness (average of RGB)
        brightness = (r + g + b) / 3

        # Walkable areas are lighter (aisles), blocked areas are darker (booths)
        # Threshold: if brightness > 100, it's walkable
        return brightness > 100

    def get_random_walkable_position(self) -> Vector2:
        """
        Get a random position in a walkable area (aisle).

        Returns:
            Random Vector2 position in a walkable area
        """
        margin = 100
        max_attempts = 100

        for _ in range(max_attempts):
            x = random.uniform(margin, self.map_width - margin)
            y = random.uniform(margin, self.map_height - margin)

            if self.is_walkable(int(x), int(y)):
                return Vector2(x, y)

        # Fallback: return any position if we can't find a walkable one
        return Vector2(
            random.uniform(margin, self.map_width - margin),
            random.uniform(margin, self.map_height - margin)
        )

    def scatter_zombies(self, zombies: List[Zombie], min_distance: int = 400) -> None:
        """
        Scatter zombies randomly across the floorplan in walkable areas (aisles).
        Ensures zombies are spread out with minimum distance between them.

        Args:
            zombies: List of zombie entities to place
            min_distance: Minimum distance in pixels between zombies (default: 1000)
        """
        import random as rand

        placed_positions = []
        fallback_count = 0

        # Player starts at center of map - keep zombies away from this area
        player_start_x = self.map_width / 2
        player_start_y = self.map_height / 2
        min_distance_from_start = 400  # Keep zombies at least this far from starting position

        # Divide map into grid sectors to help with initial distribution
        num_sectors_x = 8
        num_sectors_y = 6
        sector_width = self.map_width / num_sectors_x
        sector_height = self.map_height / num_sectors_y

        # Track which sectors have been used
        sector_usage = {}

        for i, zombie in enumerate(zombies):
            max_attempts = 500  # Increased attempts
            position_found = False

            for attempt in range(max_attempts):
                # For first zombies, try to use different sectors to spread them out
                if len(placed_positions) < num_sectors_x * num_sectors_y and attempt < 100:
                    # Pick a random unused or less-used sector
                    sector_x = rand.randint(0, num_sectors_x - 1)
                    sector_y = rand.randint(0, num_sectors_y - 1)
                    sector_key = (sector_x, sector_y)

                    # Generate position within this sector
                    x = sector_x * sector_width + rand.uniform(100, sector_width - 100)
                    y = sector_y * sector_height + rand.uniform(100, sector_height - 100)

                    # Clamp to map bounds
                    x = max(100, min(x, self.map_width - 100))
                    y = max(100, min(y, self.map_height - 100))

                    if not self.is_walkable(int(x), int(y)):
                        continue

                    candidate_pos = Vector2(x, y)
                else:
                    # Use random position
                    candidate_pos = self.get_random_walkable_position()

                # Check distance from player starting position
                dx_start = candidate_pos.x - player_start_x
                dy_start = candidate_pos.y - player_start_y
                dist_from_start = (dx_start * dx_start + dy_start * dy_start) ** 0.5

                if dist_from_start < min_distance_from_start:
                    continue  # Too close to starting position

                # Check if this position is far enough from all other zombies
                too_close = False
                for placed_pos in placed_positions:
                    dx = candidate_pos.x - placed_pos.x
                    dy = candidate_pos.y - placed_pos.y
                    distance = (dx * dx + dy * dy) ** 0.5

                    if distance < min_distance:
                        too_close = True
                        break

                if not too_close:
                    # Good position found!
                    zombie.position = candidate_pos
                    placed_positions.append(candidate_pos)
                    position_found = True

                    # Mark sector as used
                    if len(placed_positions) <= num_sectors_x * num_sectors_y:
                        sector_x = int(candidate_pos.x / sector_width)
                        sector_y = int(candidate_pos.y / sector_height)
                        sector_usage[(sector_x, sector_y)] = sector_usage.get((sector_x, sector_y), 0) + 1

                    break

            if not position_found:
                # Fallback: place with reduced distance requirement
                fallback_count += 1
                reduced_distance = max(200, min_distance - 200)

                for attempt in range(100):
                    candidate_pos = self.get_random_walkable_position()

                    # Check distance from player starting position
                    dx_start = candidate_pos.x - player_start_x
                    dy_start = candidate_pos.y - player_start_y
                    dist_from_start = (dx_start * dx_start + dy_start * dy_start) ** 0.5

                    if dist_from_start < min_distance_from_start:
                        continue  # Too close to starting position

                    too_close = False

                    for placed_pos in placed_positions:
                        dx = candidate_pos.x - placed_pos.x
                        dy = candidate_pos.y - placed_pos.y
                        distance = (dx * dx + dy * dy) ** 0.5

                        if distance < reduced_distance:
                            too_close = True
                            break

                    if not too_close:
                        zombie.position = candidate_pos
                        placed_positions.append(candidate_pos)
                        position_found = True
                        break

                if not position_found:
                    # Last resort
                    zombie.position = self.get_random_walkable_position()
                    placed_positions.append(zombie.position)

            zombie.is_hidden = True  # Start hidden

        if fallback_count > 0:
            print(f"Warning: {fallback_count} zombies placed with reduced spacing due to map constraints")

    def update_camera(self, player_x: float, player_y: float) -> None:
        """
        Update camera position to follow the player.

        Args:
            player_x: Player's x position on the map
            player_y: Player's y position on the map
        """
        # Center camera on player
        self.camera_x = player_x - self.screen_width // 2
        self.camera_y = player_y - self.screen_height // 2

        # Clamp camera to map bounds
        self.camera_x = max(0, min(self.camera_x, self.map_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, self.map_height - self.screen_height))

    def reveal_nearby_zombies(self, player_pos: Vector2, zombies: List[Zombie]) -> None:
        """
        Reveal zombies that are within the reveal radius of the player.

        Args:
            player_pos: Player's position
            zombies: List of zombie entities
        """
        for zombie in zombies:
            if zombie.is_hidden:
                # Calculate distance from player to zombie
                dx = zombie.position.x - player_pos.x
                dy = zombie.position.y - player_pos.y
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < self.reveal_radius:
                    zombie.is_hidden = False

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x: X position in world space
            world_y: Y position in world space

        Returns:
            Tuple of (screen_x, screen_y)
        """
        screen_x = int(world_x - self.camera_x)
        screen_y = int(world_y - self.camera_y)
        return (screen_x, screen_y)

    def is_on_screen(self, world_x: float, world_y: float, width: int, height: int) -> bool:
        """
        Check if an object is visible on screen.

        Args:
            world_x: X position in world space
            world_y: Y position in world space
            width: Object width
            height: Object height

        Returns:
            True if object is visible on screen
        """
        screen_x, screen_y = self.world_to_screen(world_x, world_y)

        return (screen_x + width > 0 and screen_x < self.screen_width and
                screen_y + height > 0 and screen_y < self.screen_height)

    def render(self, screen: pygame.Surface) -> None:
        """
        Render the visible portion of the map.

        Args:
            screen: Pygame surface to render to
        """
        # Create a subsurface of the map (the camera view)
        camera_rect = pygame.Rect(
            int(self.camera_x),
            int(self.camera_y),
            min(self.screen_width, self.map_width - int(self.camera_x)),
            min(self.screen_height, self.map_height - int(self.camera_y))
        )

        try:
            map_view = self.map_surface.subsurface(camera_rect)
            screen.blit(map_view, (0, 0))
        except ValueError:
            # Handle edge cases where subsurface is invalid
            screen.fill((240, 240, 240))
