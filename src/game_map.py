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

        # Load the floorplan image
        if os.path.exists(map_image_path):
            try:
                original_surface = pygame.image.load(map_image_path)
                print(f"Loaded floorplan map: {original_surface.get_width()}x{original_surface.get_height()}")

                # Apply 8-bit retro style effects
                self.map_surface = self._apply_8bit_style(original_surface)
                self.map_width = self.map_surface.get_width()
                self.map_height = self.map_surface.get_height()
                print(f"Applied 8-bit style to map")
            except pygame.error as e:
                # If image load fails, create a placeholder
                print(f"Warning: Could not load map image: {e}")
                print("Creating placeholder map...")
                self._create_placeholder_map()
        else:
            # If image doesn't exist, create a placeholder
            print(f"Warning: Map image not found at {map_image_path}")
            print("Creating placeholder map...")
            self._create_placeholder_map()

        # Camera position (top-left corner of viewport)
        self.camera_x = 0
        self.camera_y = 0

        # Zombie reveal radius (pixels) - smaller radius means you have to get closer
        self.reveal_radius = 60  # Reduced from 80 to make hunting more challenging

    def _create_placeholder_map(self) -> None:
        """Create a placeholder map when the floorplan image is not available."""
        self.map_width = 2000
        self.map_height = 1500
        self.map_surface = pygame.Surface((self.map_width, self.map_height))
        self.map_surface.fill((240, 240, 240))  # Light gray background

        # Draw grid to simulate floorplan
        for x in range(0, self.map_width, 100):
            pygame.draw.line(self.map_surface, (200, 200, 200), (x, 0), (x, self.map_height))
        for y in range(0, self.map_height, 100):
            pygame.draw.line(self.map_surface, (200, 200, 200), (0, y), (self.map_width, y))

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

    def scatter_zombies(self, zombies: List[Zombie], min_distance: int = 1000) -> None:
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
