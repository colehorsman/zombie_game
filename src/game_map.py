"""Map system for navigating the AWS re:invent floorplan."""

import logging
import os
import pygame
import random
from typing import List, Tuple, Optional
from models import Vector2
from zombie import Zombie
from door import Door
from collectible import Collectible
from third_party import ThirdParty


logger = logging.getLogger(__name__)


class GameMap:
    """Handles the floorplan map, camera, and zombie placement."""

    def __init__(self, map_image_path: str, screen_width: int, screen_height: int, account_data: dict = None, third_party_data: dict = None):
        """
        Initialize the game map.

        Args:
            map_image_path: Path to the floorplan image
            screen_width: Width of the game viewport
            screen_height: Height of the game viewport
            account_data: Dictionary mapping account names to zombie counts (e.g., {"MyHealth Sandbox": 534, "MyHealth Stage": 34})
            third_party_data: Dictionary mapping account numbers to 3rd party info (e.g., {"577945324761": [{"name": "nOps", "status": "Granted"}]})
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Tile size for Mario-style grid
        self.tile_size = 16

        # AWS Account number to friendly name mapping (from assets/aws_accounts.csv)
        self.account_names = {
            "577945324761": "MyHealth - Sandbox",
            "613056517323": "MyHealth - Production",
            "514455208804": "MyHealth - Stage",
            "393582650665": "MyHealth - Automation",
            "160224865296": "MyHealth - Production Data",
            "240768036625": "MyHealth-WebApp",
            "437154727976": "Sonrai MyHealth - Org",
            # Accounts not in CSV will display their account numbers
        }

        # Store account data and 3rd party data for room/entity creation
        self.account_data = account_data or {"Default Account": 100}
        self.third_party_data = third_party_data or {}

        # Create Mario-style tile-based map
        print("Creating Mario-style tile-based map...")
        self._create_mario_style_map()
        print(f"Created map: {self.map_width}x{self.map_height}")

        # Camera position (top-left corner of viewport)
        self.camera_x = 0
        self.camera_y = 0

        # Zombie reveal radius (pixels) - smaller radius means you have to get closer
        self.reveal_radius = 60  # Reduced from 80 to make hunting more challenging

    def _generate_rooms_from_accounts(self, tiles_wide: int, tiles_high: int) -> List[Tuple[int, int, int, int]]:
        """
        Generate rooms dynamically based on AWS account zombie counts.

        Args:
            tiles_wide: Map width in tiles
            tiles_high: Map height in tiles

        Returns:
            List of room tuples (x, y, width, height) in tiles
        """
        rooms = []
        total_zombies = sum(self.account_data.values())

        # Sort accounts by zombie count (largest first)
        sorted_accounts = sorted(self.account_data.items(), key=lambda x: x[1], reverse=True)

        # Calculate room sizes proportionally
        # Leave space for hallways (20% of map)
        usable_width = int(tiles_wide * 0.9)
        usable_height = int(tiles_high * 0.9)

        # Starting position (with margin)
        current_x = 10
        current_y = 10
        row_height = 0

        for i, (account_name, zombie_count) in enumerate(sorted_accounts):
            # Calculate room size proportional to zombie count
            # Minimum room size: 20x20 tiles
            # Maximum room size: 60x50 tiles
            proportion = zombie_count / total_zombies
            room_width = max(20, min(60, int(40 + proportion * 40)))
            room_height = max(20, min(50, int(30 + proportion * 30)))

            # Check if we need to start a new row
            if current_x + room_width > usable_width:
                current_x = 10
                current_y += row_height + 5  # Move down with spacing
                row_height = 0

            # Ensure room fits within map bounds
            if current_y + room_height > usable_height:
                print(f"Warning: Room {i} ({account_name}) would exceed map bounds, skipping")
                continue

            # Add room (ensuring it's within bounds)
            room_index = len(rooms)  # Get the actual index for this room
            rooms.append((current_x, current_y, room_width, room_height))

            # Store room info for labeling (use actual room index, not iteration index)
            if not hasattr(self, 'room_accounts'):
                self.room_accounts = {}
            self.room_accounts[room_index] = {
                'name': account_name,
                'zombie_count': zombie_count
            }

            # Update position for next room
            current_x += room_width + 5  # Add spacing between rooms
            row_height = max(row_height, room_height)

        return rooms

    def _create_mario_style_map(self) -> None:
        """Create a Mario Bros-style tile-based map with AWS office theme."""
        # Calculate total zombies and determine map size
        total_zombies = sum(self.account_data.values())
        num_accounts = len(self.account_data)

        print(f"Creating map for {num_accounts} AWS accounts with {total_zombies} total zombies")

        # Base map dimensions - scale based on zombie count
        # Minimum size for small accounts, scale up for larger
        base_tiles_wide = max(150, int(150 * (total_zombies / 500)))
        base_tiles_high = max(112, int(112 * (total_zombies / 500)))

        tiles_wide = base_tiles_wide
        tiles_high = base_tiles_high

        self.map_width = tiles_wide * self.tile_size
        self.map_height = tiles_high * self.tile_size

        # Create map surface
        self.map_surface = pygame.Surface((self.map_width, self.map_height))

        # Mario-style color palette (with purple corporate theme)
        FLOOR_PURPLE = (80, 60, 100)      # Dark purple floor
        FLOOR_LIGHT = (100, 80, 120)      # Light purple floor (checkered)
        WALL_PURPLE = (60, 40, 90)        # Dark purple walls
        WALL_HIGHLIGHT = (100, 70, 140)   # Purple wall highlights
        WALL_SHADOW = (40, 25, 60)        # Purple wall shadows
        BLACK = (0, 0, 0)                 # Outlines

        # Create tile map (0 = floor, 1 = wall)
        tile_map = [[0 for _ in range(tiles_wide)] for _ in range(tiles_high)]

        # Add outer border walls
        for x in range(tiles_wide):
            tile_map[0][x] = 1
            tile_map[tiles_high - 1][x] = 1
        for y in range(tiles_high):
            tile_map[y][0] = 1
            tile_map[y][tiles_wide - 1] = 1

        # Create AWS account rooms dynamically based on zombie counts
        rooms = self._generate_rooms_from_accounts(tiles_wide, tiles_high)

        print(f"Generated {len(rooms)} rooms for AWS accounts")

        # Draw room walls
        for rx, ry, rw, rh in rooms:
            # Top and bottom walls
            for x in range(rx, rx + rw):
                tile_map[ry][x] = 1
                tile_map[ry + rh - 1][x] = 1
            # Left and right walls
            for y in range(ry, ry + rh):
                tile_map[y][rx] = 1
                tile_map[y][rx + rw - 1] = 1

        # Store room data for later use (AWS account integration)
        self.rooms = rooms

        # Render tiles to surface
        for y in range(tiles_high):
            for x in range(tiles_wide):
                tile_x = x * self.tile_size
                tile_y = y * self.tile_size

                if tile_map[y][x] == 1:
                    # Wall tile (Mario-style block)
                    self._draw_wall_tile(tile_x, tile_y)
                else:
                    # Floor tile (checkered pattern)
                    if (x + y) % 2 == 0:
                        self._draw_floor_tile(tile_x, tile_y, FLOOR_PURPLE)
                    else:
                        self._draw_floor_tile(tile_x, tile_y, FLOOR_LIGHT)

        # Store tile map for collision detection (needed by doors/collectibles)
        self.tile_map = tile_map
        self.tiles_wide = tiles_wide
        self.tiles_high = tiles_high

        # Add room labels
        self._add_room_labels()

        # Create doors for rooms
        self.doors = self._create_room_doors()

        # Create collectibles (question blocks)
        self.collectibles = self._create_collectibles()

        # Create 3rd party entities in hallways
        self.third_parties = self._create_third_party_entities()

    def _draw_floor_tile(self, x: int, y: int, base_color: tuple) -> None:
        """Draw a simple Mario-style floor tile."""
        # Fill with base color
        pygame.draw.rect(self.map_surface, base_color, (x, y, self.tile_size, self.tile_size))

        # Add subtle border for tile definition
        border_color = tuple(max(0, c - 20) for c in base_color)
        pygame.draw.rect(self.map_surface, border_color, (x, y, self.tile_size, self.tile_size), 1)

    def _draw_wall_tile(self, x: int, y: int) -> None:
        """Draw a Mario-style wall block with purple theme."""
        WALL_PURPLE = (60, 40, 90)
        WALL_HIGHLIGHT = (100, 70, 140)
        WALL_SHADOW = (40, 25, 60)
        BLACK = (0, 0, 0)

        # Main block
        pygame.draw.rect(self.map_surface, WALL_PURPLE, (x, y, self.tile_size, self.tile_size))

        # Top and left highlights (3 pixels thick like Mario)
        pygame.draw.line(self.map_surface, WALL_HIGHLIGHT, (x, y), (x + self.tile_size - 1, y), 3)
        pygame.draw.line(self.map_surface, WALL_HIGHLIGHT, (x, y), (x, y + self.tile_size - 1), 3)

        # Bottom and right shadows
        pygame.draw.line(self.map_surface, WALL_SHADOW, (x, y + self.tile_size - 1), (x + self.tile_size - 1, y + self.tile_size - 1), 2)
        pygame.draw.line(self.map_surface, WALL_SHADOW, (x + self.tile_size - 1, y), (x + self.tile_size - 1, y + self.tile_size - 1), 2)

        # Black outline
        pygame.draw.rect(self.map_surface, BLACK, (x, y, self.tile_size, self.tile_size), 1)

    def _add_room_labels(self) -> None:
        """Add AWS account labels to rooms."""
        AWS_ORANGE = (255, 153, 0)
        WHITE = (255, 255, 255)

        try:
            font = pygame.font.Font(None, 18)
            small_font = pygame.font.Font(None, 14)

            for i, (rx, ry, rw, rh) in enumerate(self.rooms):
                if i in self.room_accounts:
                    account_info = self.room_accounts[i]
                    account_num = account_info['name']  # AWS account number
                    zombie_count = account_info['zombie_count']

                    # Get friendly name from mapping, fallback to account number
                    friendly_name = self.account_names.get(account_num, account_num)

                    # Calculate center of room
                    center_x = (rx + rw // 2) * self.tile_size
                    center_y = (ry + rh // 2) * self.tile_size

                    # Render account name (friendly name)
                    name_surface = font.render(friendly_name, True, AWS_ORANGE)
                    name_rect = name_surface.get_rect(center=(center_x, center_y - 10))

                    # Render zombie count
                    count_text = f"{zombie_count} zombies"
                    count_surface = small_font.render(count_text, True, WHITE)
                    count_rect = count_surface.get_rect(center=(center_x, center_y + 10))

                    # Draw shadows
                    name_shadow = font.render(friendly_name, True, (0, 0, 0))
                    count_shadow = small_font.render(count_text, True, (0, 0, 0))
                    self.map_surface.blit(name_shadow, (name_rect.x + 2, name_rect.y + 2))
                    self.map_surface.blit(count_shadow, (count_rect.x + 2, count_rect.y + 2))

                    # Draw text
                    self.map_surface.blit(name_surface, name_rect)
                    self.map_surface.blit(count_surface, count_rect)
        except Exception as e:
            print(f"Error rendering room labels: {e}")
            pass

    def _create_room_doors(self) -> List[Door]:
        """Create pipe-style doors for each room."""
        doors = []

        # Add one door to each room (placed at bottom center of room)
        for i, (rx, ry, rw, rh) in enumerate(self.rooms):
            # Calculate door position (bottom center of room)
            door_tile_x = rx + rw // 2 - 1  # Center horizontally (door is 2 tiles wide)
            door_tile_y = ry + rh - 2       # Near bottom of room

            # Convert to pixel coordinates
            door_x = door_tile_x * self.tile_size
            door_y = door_tile_y * self.tile_size

            # Get friendly room name if available
            room_name = None
            if i in self.room_accounts:
                account_num = self.room_accounts[i]['name']
                room_name = self.account_names.get(account_num, account_num)

            # Create door leading to this room
            door = Door(Vector2(door_x, door_y), direction="vertical", destination_room=i, destination_room_name=room_name)
            doors.append(door)

            # Clear the BOTTOM WALL tiles where the door is (make it walkable)
            # Door is 32 pixels (2 tiles) wide, and we need to punch through the bottom wall
            FLOOR_PURPLE = (80, 60, 100)      # Dark purple floor
            FLOOR_LIGHT = (100, 80, 120)      # Light purple floor

            for dx in range(2):
                tile_x = door_tile_x + dx
                # Clear both the door position AND the bottom wall
                for dy in range(2):  # Clear door position and wall below it
                    tile_y = door_tile_y + dy
                    if 0 <= tile_x < self.tiles_wide and 0 <= tile_y < self.tiles_high:
                        self.tile_map[tile_y][tile_x] = 0  # Make walkable

                        # Re-render this tile as floor on map_surface
                        pixel_x = tile_x * self.tile_size
                        pixel_y = tile_y * self.tile_size
                        if (tile_x + tile_y) % 2 == 0:
                            self._draw_floor_tile(pixel_x, pixel_y, FLOOR_PURPLE)
                        else:
                            self._draw_floor_tile(pixel_x, pixel_y, FLOOR_LIGHT)

        print(f"Created {len(doors)} doors for AWS account rooms")
        return doors

    def _create_collectibles(self) -> List[Collectible]:
        """Create question block collectibles scattered throughout the map."""
        collectibles = []

        # Place collectibles in each room (3-5 per room)
        for i, (rx, ry, rw, rh) in enumerate(self.rooms):
            num_collectibles = random.randint(3, 5)

            for _ in range(num_collectibles):
                # Random position within the room (away from walls)
                coll_tile_x = rx + random.randint(3, rw - 4)
                coll_tile_y = ry + random.randint(3, rh - 4)

                # Convert to pixel coordinates
                coll_x = coll_tile_x * self.tile_size
                coll_y = coll_tile_y * self.tile_size

                # Create collectible with random data value
                data_value = random.randint(5, 20)
                collectible = Collectible(Vector2(coll_x, coll_y), data_value)
                collectibles.append(collectible)

        print(f"Created {len(collectibles)} collectible question blocks")
        return collectibles

    def _create_third_party_entities(self) -> List[ThirdParty]:
        """
        Create 3rd party entities in hallways near their associated AWS account rooms.

        Returns:
            List of ThirdParty entities
        """
        third_parties = []

        if not self.third_party_data:
            logger.info("No 3rd party data provided, skipping 3rd party entity creation")
            return third_parties

        # Check if we have org-level 3rd parties (under "all" key)
        org_third_parties = self.third_party_data.get("all", [])

        # If we have org-level 3rd parties, place them ALL around MyHealth Production room
        if org_third_parties and self.room_accounts:
            import math

            # Find the MyHealth Production room (account 613056517323)
            production_room_index = None
            production_account = "613056517323"

            for room_index, room_info in self.room_accounts.items():
                if room_info['name'] == production_account:
                    production_room_index = room_index
                    break

            if production_room_index is not None:
                # Get room bounds (in tiles)
                rx, ry, rw, rh = self.rooms[production_room_index]

                logger.info(f"Placing ALL {len(org_third_parties)} 3rd parties around MyHealth Production (room {production_room_index})")

                # Distribute 3rd parties along all 4 walls (outside the room)
                num_parties = len(org_third_parties)
                parties_per_wall = num_parties // 4
                extra_parties = num_parties % 4

                # Define walls: top, right, bottom, left
                walls = ['top', 'right', 'bottom', 'left']
                party_index = 0

                for wall_idx, wall in enumerate(walls):
                    # Distribute extra parties among first walls
                    num_on_this_wall = parties_per_wall + (1 if wall_idx < extra_parties else 0)

                    for wall_position in range(num_on_this_wall):
                        if party_index >= num_parties:
                            break

                        third_party_info = org_third_parties[party_index]
                        third_party_name = third_party_info.get('name', 'Unknown')

                        # Calculate position based on wall
                        hallway_distance = 4  # tiles away from room wall

                        if wall == 'top':
                            # Top wall - pace horizontally
                            hallway_tile_y = ry - hallway_distance
                            # Space evenly along top wall
                            spacing = rw / (num_on_this_wall + 1)
                            hallway_tile_x = rx + int((wall_position + 1) * spacing)
                            patrol_axis = 'horizontal'
                            patrol_min = rx * self.tile_size
                            patrol_max = (rx + rw) * self.tile_size

                        elif wall == 'bottom':
                            # Bottom wall - pace horizontally
                            hallway_tile_y = ry + rh + hallway_distance
                            spacing = rw / (num_on_this_wall + 1)
                            hallway_tile_x = rx + int((wall_position + 1) * spacing)
                            patrol_axis = 'horizontal'
                            patrol_min = rx * self.tile_size
                            patrol_max = (rx + rw) * self.tile_size

                        elif wall == 'left':
                            # Left wall - pace vertically
                            hallway_tile_x = rx - hallway_distance
                            spacing = rh / (num_on_this_wall + 1)
                            hallway_tile_y = ry + int((wall_position + 1) * spacing)
                            patrol_axis = 'vertical'
                            patrol_min = ry * self.tile_size
                            patrol_max = (ry + rh) * self.tile_size

                        else:  # right
                            # Right wall - pace vertically
                            hallway_tile_x = rx + rw + hallway_distance
                            spacing = rh / (num_on_this_wall + 1)
                            hallway_tile_y = ry + int((wall_position + 1) * spacing)
                            patrol_axis = 'vertical'
                            patrol_min = ry * self.tile_size
                            patrol_max = (ry + rh) * self.tile_size

                        # Ensure position is within map bounds
                        hallway_tile_x = max(2, min(hallway_tile_x, self.tiles_wide - 3))
                        hallway_tile_y = max(2, min(hallway_tile_y, self.tiles_high - 3))

                        # Check if this is a walkable position
                        max_attempts = 20
                        position_found = False
                        for attempt in range(max_attempts):
                            test_x = (hallway_tile_x + (attempt % 3) - 1) * self.tile_size
                            test_y = (hallway_tile_y + (attempt // 3) - 1) * self.tile_size

                            if self.is_walkable(int(test_x), int(test_y)):
                                third_party_x = test_x
                                third_party_y = test_y
                                position_found = True
                                break

                        if not position_found:
                            third_party_x = hallway_tile_x * self.tile_size
                            third_party_y = hallway_tile_y * self.tile_size

                        # Create 3rd party entity
                        third_party = ThirdParty(
                            name=third_party_name,
                            account=production_account,
                            position=Vector2(third_party_x, third_party_y),
                            third_party_id=third_party_info.get('thirdPartyId', None)
                        )

                        # Store patrol information for pacing along wall
                        third_party.patrol_axis = patrol_axis  # 'horizontal' or 'vertical'
                        third_party.patrol_min = patrol_min
                        third_party.patrol_max = patrol_max

                        third_parties.append(third_party)
                        party_index += 1

                logger.info(f"Created {len(third_parties)} 3rd party entities surrounding MyHealth Production")
            else:
                logger.warning("MyHealth Production room not found, 3rd parties not created")

            return third_parties

        # For per-account 3rd parties (if provided)
        for room_index, room_info in self.room_accounts.items():
            account_num = room_info['name']  # AWS account number
            account_third_parties = self.third_party_data.get(account_num, [])

            if not account_third_parties:
                continue

            # Get room bounds (in tiles)
            rx, ry, rw, rh = self.rooms[room_index]

            logger.info(f"Creating {len(account_third_parties)} 3rd parties for account {account_num} (room {room_index})")

            # Place 3rd parties in the hallway outside the room door
            # The door is at the bottom center of the room, so place them in the hallway below
            for i, third_party_info in enumerate(account_third_parties):
                third_party_name = third_party_info.get('name', 'Unknown')

                # Calculate position in hallway outside the door
                # Door is at (rx + rw // 2, ry + rh - 2), so place 3rd parties nearby
                door_tile_x = rx + rw // 2 - 1
                door_tile_y = ry + rh - 2

                # Place 3rd parties in a line in the hallway below the door
                # Offset horizontally based on index
                hallway_tile_x = door_tile_x + (i - len(account_third_parties) // 2) * 3
                hallway_tile_y = door_tile_y + 4  # 4 tiles below the door

                # Ensure position is within map bounds
                hallway_tile_x = max(2, min(hallway_tile_x, self.tiles_wide - 3))
                hallway_tile_y = max(2, min(hallway_tile_y, self.tiles_high - 3))

                # Check if this is a walkable position, if not, try nearby
                max_attempts = 10
                position_found = False
                for attempt in range(max_attempts):
                    test_x = (hallway_tile_x + attempt) * self.tile_size
                    test_y = hallway_tile_y * self.tile_size

                    if self.is_walkable(int(test_x), int(test_y)):
                        # Convert to pixel coordinates
                        third_party_x = test_x
                        third_party_y = test_y
                        position_found = True
                        break

                if not position_found:
                    # Fallback: place anywhere in the hallway
                    third_party_x = hallway_tile_x * self.tile_size
                    third_party_y = hallway_tile_y * self.tile_size

                # Create 3rd party entity
                third_party = ThirdParty(
                    name=third_party_name,
                    account=account_num,
                    position=Vector2(third_party_x, third_party_y),
                    third_party_id=third_party_info.get('thirdPartyId', None)
                )
                third_parties.append(third_party)

        logger.info(f"Created {len(third_parties)} 3rd party entities across all accounts")
        return third_parties

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
        Check if a position is in a walkable area using tile map.

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels

        Returns:
            True if the position is walkable (floor), False if blocked (wall)
        """
        # Clamp to map bounds
        x = max(0, min(int(x), self.map_width - 1))
        y = max(0, min(int(y), self.map_height - 1))

        # Convert pixel coordinates to tile coordinates
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size

        # Check bounds
        if tile_x < 0 or tile_x >= self.tiles_wide or tile_y < 0 or tile_y >= self.tiles_high:
            return False

        # Check tile map (0 = walkable floor, 1 = wall)
        return self.tile_map[tile_y][tile_x] == 0

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

    def scatter_zombies(self, zombies: List[Zombie], min_distance: int = 50) -> None:
        """
        Scatter zombies by AWS account - each account's zombies go in their room.

        Args:
            zombies: List of zombie entities to place (each has an account field)
            min_distance: Minimum distance in pixels between zombies (default: 50)
        """
        import random as rand
        from collections import defaultdict

        # Group zombies by account
        zombies_by_account = defaultdict(list)
        for zombie in zombies:
            if hasattr(zombie, 'account') and zombie.account:
                zombies_by_account[zombie.account].append(zombie)
            else:
                # Fallback for zombies without account info
                zombies_by_account["Unknown"].append(zombie)

        logger.info(f"Grouped zombies into {len(zombies_by_account)} accounts")

        # Place each account's zombies in their respective room
        for room_index, room_info in self.room_accounts.items():
            account_num = room_info['name']  # AWS account number
            account_zombies = zombies_by_account.get(account_num, [])

            if not account_zombies:
                logger.warning(f"No zombies found for account {account_num} (room {room_index})")
                continue

            # Get room bounds (in tiles)
            rx, ry, rw, rh = self.rooms[room_index]

            # Convert to pixel coordinates (with margins from walls)
            room_x_min = (rx + 3) * self.tile_size  # 3 tiles from left wall
            room_x_max = (rx + rw - 3) * self.tile_size  # 3 tiles from right wall
            room_y_min = (ry + 3) * self.tile_size  # 3 tiles from top wall
            room_y_max = (ry + rh - 3) * self.tile_size  # 3 tiles from bottom wall

            logger.info(f"Placing {len(account_zombies)} zombies in room {room_index} (account {account_num})")

            # Place each zombie in this room
            placed_positions = []
            for i, zombie in enumerate(account_zombies):
                max_attempts = 100
                position_found = False

                for attempt in range(max_attempts):
                    # Generate random position within room bounds
                    x = rand.uniform(room_x_min, room_x_max)
                    y = rand.uniform(room_y_min, room_y_max)

                    # Check if walkable
                    if not self.is_walkable(int(x), int(y)):
                        continue

                    candidate_pos = Vector2(x, y)

                    # Check minimum distance from other zombies in this room
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
                        break

                if not position_found:
                    # Fallback: place anywhere in room (ignore distance)
                    x = rand.uniform(room_x_min, room_x_max)
                    y = rand.uniform(room_y_min, room_y_max)
                    zombie.position = Vector2(x, y)
                    placed_positions.append(zombie.position)

                zombie.is_hidden = True  # Start hidden

        logger.info(f"Successfully scattered {len(zombies)} zombies across {len(self.room_accounts)} rooms")

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
