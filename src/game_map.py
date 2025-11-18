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

        # Load the actual floorplan image
        print(f"Loading floorplan from {map_image_path}...")
        if os.path.exists("assets/floorplan_updated.png"):
            self._load_actual_floorplan("assets/floorplan_updated.png")
        else:
            # Fallback to custom floorplan if file doesn't exist
            print("Using custom AWS re:invent themed floorplan...")
            self._create_placeholder_map()
        print(f"Loaded floorplan: {self.map_width}x{self.map_height}")

        # Camera position (top-left corner of viewport)
        self.camera_x = 0
        self.camera_y = 0

        # Zombie reveal radius (pixels) - smaller radius means you have to get closer
        self.reveal_radius = 60  # Reduced from 80 to make hunting more challenging

    def _load_actual_floorplan(self, image_path: str) -> None:
        """
        Load the actual AWS re:Invent floorplan image and add zombie theme overlays.

        Args:
            image_path: Path to the floorplan PNG image
        """
        try:
            # Load the base floorplan image
            base_image = pygame.image.load(image_path)

            # Scale the image to a bigger size for better visibility and more gameplay space
            target_width = 4800  # Increased from 3600 for better quality
            aspect_ratio = base_image.get_height() / base_image.get_width()
            target_height = int(target_width * aspect_ratio)

            self.map_width = target_width
            self.map_height = target_height

            # Use smoothscale for better quality
            scaled_image = pygame.transform.smoothscale(base_image, (self.map_width, self.map_height))
            self.map_surface = scaled_image.copy()

            # Brighten the image for better visibility
            self._brighten_image()

            # Add zombie-themed overlays (but NO blood splatters/red circles)
            self._add_zombie_theme_overlays()

        except Exception as e:
            print(f"Error loading floorplan: {e}")
            # Fallback to custom map
            self._create_placeholder_map()

    def _brighten_image(self) -> None:
        """Brighten the floorplan image for better visibility."""
        # Create a semi-transparent white overlay to brighten the image
        overlay = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60))  # White with 60 alpha for subtle brightening
        self.map_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _add_zombie_theme_overlays(self) -> None:
        """Add zombie-themed visual overlays to the floorplan (no blood splatters)."""
        # Color palette
        BLOOD_RED = (139, 0, 0)
        WARNING_YELLOW = (255, 215, 0)
        HAZARD_ORANGE = (255, 69, 0)
        BLACK = (0, 0, 0)
        SONRAI_BLUE = (70, 90, 180)  # Sonrai brand blue

        # Add Sonrai logo at the top (simplified version)
        self._draw_sonrai_logo(self.map_width // 2, 80)

        # Add "WALKER OUTBREAK" warning at top
        try:
            title_font = pygame.font.Font(None, 48)
            title_text = "⚠ WALKER OUTBREAK - SECURE & QUARANTINE ⚠"
            title_surface = title_font.render(title_text, True, BLOOD_RED)
            title_rect = title_surface.get_rect(center=(self.map_width // 2, 140))
            self.map_surface.blit(title_surface, title_rect)
        except:
            pass

        # Add warning signs scattered around (no blood circles)
        warning_positions = [
            (300, 400, "⚠ WALKER\nZONE"),
            (self.map_width - 400, 400, "⚠ INFECTED\nAREA"),
            (300, self.map_height - 400, "⚠ STAY\nALERT"),
            (self.map_width - 400, self.map_height - 400, "⚠ QUARANTINE\nZONE"),
        ]

        for wx, wy, wtext in warning_positions:
            # Warning sign background
            sign_width, sign_height = 140, 90
            pygame.draw.rect(self.map_surface, WARNING_YELLOW,
                           (wx - sign_width//2, wy - sign_height//2, sign_width, sign_height))
            pygame.draw.rect(self.map_surface, BLACK,
                           (wx - sign_width//2, wy - sign_height//2, sign_width, sign_height), 3)
            # Warning text
            try:
                font = pygame.font.Font(None, 20)
                for i, line in enumerate(wtext.split('\n')):
                    text_surface = font.render(line, True, BLACK)
                    text_rect = text_surface.get_rect(center=(wx, wy - 18 + i * 24))
                    self.map_surface.blit(text_surface, text_rect)
            except:
                pass

    def _draw_sonrai_logo(self, x: int, y: int) -> None:
        """
        Draw the Sonrai Security logo (simplified 8-bit version).

        Args:
            x: Center X position
            y: Center Y position
        """
        SONRAI_BLUE = (70, 90, 180)
        DARK_BLUE = (35, 47, 62)
        WHITE = (255, 255, 255)

        # Simplified infinity-like symbol (8-bit style)
        logo_size = 40

        # Left loop of infinity
        pygame.draw.circle(self.map_surface, SONRAI_BLUE, (x - logo_size//2, y), logo_size//3, 4)
        # Right loop of infinity
        pygame.draw.circle(self.map_surface, SONRAI_BLUE, (x + logo_size//2, y), logo_size//3, 4)
        # Center connection
        pygame.draw.line(self.map_surface, SONRAI_BLUE,
                        (x - logo_size//4, y), (x + logo_size//4, y), 6)

        # "sonrai security" text
        try:
            logo_font = pygame.font.Font(None, 32)
            text = "sonrai security"
            text_surface = logo_font.render(text, True, DARK_BLUE)
            text_rect = text_surface.get_rect(center=(x, y + logo_size))
            # White background for readability
            bg_rect = text_rect.inflate(10, 4)
            pygame.draw.rect(self.map_surface, WHITE, bg_rect)
            self.map_surface.blit(text_surface, text_rect)
        except:
            pass

    def _create_placeholder_map(self) -> None:
        """Create an AWS re:invent themed floorplan."""
        self.map_width = 3600  # Increased from 2400 for more zombie space
        self.map_height = 2700  # Increased from 1800 for more zombie space
        self.map_surface = pygame.Surface((self.map_width, self.map_height))

        # AWS + Zombie Color palette (retro 8-bit style)
        AWS_ORANGE = (255, 153, 0)
        DARK_BLUE = (35, 47, 62)
        LIGHT_BLUE = (146, 186, 211)
        AISLE_COLOR = (180, 200, 210)  # Slightly darker/grittier aisles
        BOOTH_COLOR = (70, 90, 110)     # Dark blue-grey for booths
        TEXT_COLOR = (255, 255, 255)    # White text
        ACCENT_COLOR = (255, 200, 100)  # Warm accent
        BLOOD_RED = (139, 0, 0)         # Dark red for blood/danger
        QUARANTINE_YELLOW = (255, 215, 0)  # Warning yellow
        HAZARD_ORANGE = (255, 69, 0)    # Biohazard orange
        SAFE_ZONE_GREEN = (34, 139, 34)  # Safe zone green

        # Background - main floor with gritty texture
        self.map_surface.fill(AISLE_COLOR)
        # Add subtle grid pattern for concrete floor feel
        for x in range(0, self.map_width, 50):
            pygame.draw.line(self.map_surface, (170, 190, 200), (x, 0), (x, self.map_height), 1)
        for y in range(0, self.map_height, 50):
            pygame.draw.line(self.map_surface, (170, 190, 200), (0, y), (self.map_width, y), 1)

        # Define exhibit areas with realistic re:invent + zombie theme
        areas = [
            # (x, y, width, height, "Label", color, is_safe_zone)
            # Row 1: AWS Services - OVERRUN
            (150, 150, 750, 600, "EC2 & Compute\n⚠ WALKERS DETECTED", BOOTH_COLOR, False),
            (1050, 150, 750, 600, "Lambda & Serverless\n⚠ CONTAMINATED", BOOTH_COLOR, False),
            (1950, 150, 750, 600, "SageMaker & AI/ML\n⚠ BREACH", BOOTH_COLOR, False),

            # Row 2: Partner & Builder zones
            (150, 900, 600, 750, "AWS Partners\n⚠ OVERRUN", (90, 110, 140), False),
            (900, 900, 900, 450, "Builders Fair\nQUARANTINE ZONE", HAZARD_ORANGE, True),
            (1950, 900, 750, 450, "Container Services\n⚠ INFECTED", BOOTH_COLOR, False),

            # Row 3: Data & Main areas
            (150, 1800, 750, 600, "S3 & Storage\n⚠ HOSTILE", BOOTH_COLOR, False),
            (1050, 1500, 750, 900, "THE SANCTUARY\n(Main Stage)", SAFE_ZONE_GREEN, True),
            (1950, 1500, 750, 900, "Expo Hall\n⚠ WALKER HORDE", BOOTH_COLOR, False),

            # Side areas
            (2850, 150, 600, 1050, "Networking Zone\n⚠ COMPROMISED", BOOTH_COLOR, False),
            (2850, 1350, 600, 1050, "Gaming Lounge\n⚠ INFESTED", BOOTH_COLOR, False),
        ]

        # Draw areas with enhanced details
        for x, y, w, h, label, color, is_safe in areas:
            # Draw booth rectangle
            pygame.draw.rect(self.map_surface, color, (x, y, w, h))

            # Draw border (thicker for safe zones)
            border_width = 5 if is_safe else 3
            border_color = SAFE_ZONE_GREEN if is_safe else DARK_BLUE
            pygame.draw.rect(self.map_surface, border_color, (x, y, w, h), border_width)

            # Add danger stripes for non-safe zones
            if not is_safe:
                stripe_spacing = 40
                for i in range(0, w + h, stripe_spacing):
                    stripe_start = (x + i, y)
                    stripe_end = (x, y + i)
                    if stripe_start[0] <= x + w and stripe_end[1] <= y + h:
                        pygame.draw.line(self.map_surface, BLOOD_RED, stripe_start, stripe_end, 2)

            # Add label with appropriate color
            label_color = TEXT_COLOR if is_safe else (255, 200, 200)  # Slight red tint for danger zones
            self._draw_text_centered(label, x + w//2, y + h//2, label_color, size=28)

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
        """Draw AWS + zombie-themed branding elements on the map."""
        AWS_ORANGE = (255, 153, 0)
        DARK_BLUE = (35, 47, 62)
        BLOOD_RED = (139, 0, 0)
        WARNING_YELLOW = (255, 215, 0)

        # Draw "AWS re:Invent 2024 - OUTBREAK" title at top
        try:
            title_font = pygame.font.Font(None, 56)
            title_text = "AWS re:Invent 2024"
            title_surface = title_font.render(title_text, True, AWS_ORANGE)
            title_rect = title_surface.get_rect(center=(self.map_width // 2, 35))

            # Draw shadow
            shadow_surface = title_font.render(title_text, True, DARK_BLUE)
            self.map_surface.blit(shadow_surface, (title_rect.x + 3, title_rect.y + 3))
            # Draw text
            self.map_surface.blit(title_surface, title_rect)

            # Add "WALKER OUTBREAK" subtitle
            subtitle_font = pygame.font.Font(None, 36)
            subtitle_text = "⚠ WALKER OUTBREAK - SECURE & QUARANTINE ⚠"
            subtitle_surface = subtitle_font.render(subtitle_text, True, BLOOD_RED)
            subtitle_rect = subtitle_surface.get_rect(center=(self.map_width // 2, 80))
            self.map_surface.blit(subtitle_surface, subtitle_rect)
        except:
            pass

        # Draw biohazard symbols in corners (no blood splatters)
        self._draw_biohazard(150, 50, 40, WARNING_YELLOW)
        self._draw_biohazard(self.map_width - 150, 50, 40, WARNING_YELLOW)
        self._draw_biohazard(150, self.map_height - 50, 40, WARNING_YELLOW)
        self._draw_biohazard(self.map_width - 150, self.map_height - 50, 40, WARNING_YELLOW)

    def _draw_biohazard(self, x: int, y: int, size: int, color: tuple) -> None:
        """Draw a biohazard symbol (8-bit style)."""
        # Draw central circle
        pygame.draw.circle(self.map_surface, color, (x, y), size // 4, 3)

        # Draw three triangular sections (simplified biohazard)
        for angle in [0, 120, 240]:
            import math
            rad = math.radians(angle)
            outer_x = x + int(size * 0.7 * math.cos(rad))
            outer_y = y + int(size * 0.7 * math.sin(rad))
            pygame.draw.circle(self.map_surface, color, (outer_x, outer_y), size // 3, 2)

    def _draw_blood_splatter(self, x: int, y: int, size: int) -> None:
        """Draw a blood splatter (8-bit style)."""
        BLOOD_RED = (139, 0, 0)
        DARK_BLOOD = (100, 0, 0)

        # Main splatter
        pygame.draw.circle(self.map_surface, BLOOD_RED, (x, y), size)

        # Add smaller splatters around
        import random
        for _ in range(random.randint(3, 6)):
            offset_x = random.randint(-size * 2, size * 2)
            offset_y = random.randint(-size * 2, size * 2)
            splatter_size = random.randint(size // 3, size // 2)
            pygame.draw.circle(self.map_surface, DARK_BLOOD, (x + offset_x, y + offset_y), splatter_size)

    def _draw_directional_markers(self) -> None:
        """Draw entrance and directional markers with zombie theme."""
        DARK_BLUE = (35, 47, 62)
        AWS_ORANGE = (255, 153, 0)
        BLOOD_RED = (139, 0, 0)
        WARNING_YELLOW = (255, 215, 0)

        # Draw warning signs scattered around the map
        warning_positions = [
            (300, 700, "⚠ WALKER\nZONE"),
            (1800, 700, "⚠ DO NOT\nENTER"),
            (3200, 1200, "⚠ INFECTED\nAREA"),
            (500, 2300, "⚠ STAY\nALERT"),
            (2200, 2400, "⚠ SECURE\nPERIMETER"),
        ]

        for wx, wy, wtext in warning_positions:
            # Warning sign background
            sign_width, sign_height = 120, 80
            pygame.draw.rect(self.map_surface, WARNING_YELLOW,
                           (wx - sign_width//2, wy - sign_height//2, sign_width, sign_height))
            pygame.draw.rect(self.map_surface, (0, 0, 0),
                           (wx - sign_width//2, wy - sign_height//2, sign_width, sign_height), 3)
            # Warning text
            try:
                font = pygame.font.Font(None, 18)
                for i, line in enumerate(wtext.split('\n')):
                    text_surface = font.render(line, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(wx, wy - 15 + i * 20))
                    self.map_surface.blit(text_surface, text_rect)
            except:
                pass

        # Draw "EVACUATION ROUTE" marker at bottom center
        entrance_x = self.map_width // 2
        entrance_y = self.map_height - 100

        try:
            font = pygame.font.Font(None, 40)
            entrance_text = font.render("⬇ EVACUATION ROUTE ⬇", True, BLOOD_RED)
            entrance_rect = entrance_text.get_rect(center=(entrance_x, entrance_y))
            # Black outline
            outline_text = font.render("⬇ EVACUATION ROUTE ⬇", True, (0, 0, 0))
            self.map_surface.blit(outline_text, (entrance_rect.x - 2, entrance_rect.y - 2))
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

        # Much more lenient threshold for the actual floorplan - most areas should be walkable
        # Only block very dark areas (likely booth interiors or solid objects)
        # Threshold: if brightness > 40, it's walkable (was 100, now much more lenient)
        return brightness > 40

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
