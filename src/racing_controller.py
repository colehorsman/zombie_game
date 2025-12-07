"""Racing genre controller - Rad Racer / OutRun style pseudo-3D racing.

Implements classic NES-style behind-the-car racing with:
- Pseudo-3D road perspective (road coming toward you)
- Zombie cars to race against and zap
- AWS DeepRacer inspired track
- Road Rash style combat

**Feature: multi-genre-levels**
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import List

import pygame

from genre_controller import GenreController, GenreControllerFactory, InputState
from models import GenreType, Vector2

logger = logging.getLogger(__name__)


@dataclass
class RoadSegment:
    """A segment of the road for pseudo-3D rendering."""

    curve: float  # Curvature (-1 to 1)
    hill: float  # Hill slope
    sprite_x: float  # X position of any sprite on this segment


@dataclass
class EnemyRacer:
    """Enemy racer (zombie car) on the track."""

    zombie: object
    road_position: float  # Position along the road (0 = start)
    lane: float  # -1 = left, 0 = center, 1 = right
    speed: float
    color: tuple = (50, 180, 50)  # Random car color
    eliminated: bool = False
    spin_timer: float = 0.0


# Vibrant car colors for enemy racers
CAR_COLORS = [
    ((220, 50, 50), (180, 30, 30), (255, 80, 80)),  # Red
    ((50, 50, 220), (30, 30, 180), (80, 80, 255)),  # Blue
    ((220, 180, 50), (180, 140, 30), (255, 220, 80)),  # Yellow/Gold
    ((50, 220, 220), (30, 180, 180), (80, 255, 255)),  # Cyan
    ((220, 50, 180), (180, 30, 140), (255, 80, 220)),  # Magenta
    ((50, 220, 50), (30, 180, 30), (80, 255, 80)),  # Green
    ((220, 120, 50), (180, 90, 30), (255, 150, 80)),  # Orange
    ((180, 50, 220), (140, 30, 180), (220, 80, 255)),  # Purple
]


@dataclass
class Projectile:
    """Shell/zap projectile."""

    road_position: float
    lane: float
    active: bool = True


class RacingController(GenreController):
    """Rad Racer / OutRun style pseudo-3D racing.

    Features:
    - Behind-the-car camera perspective
    - Road curves and hills
    - Zombie cars to race/zap
    - AWS DeepRacer inspired visuals
    """

    # Road rendering constants
    ROAD_WIDTH = 2000
    SEGMENT_LENGTH = 100  # Smaller segments = smoother movement
    RUMBLE_LENGTH = 3
    DRAW_DISTANCE = 150  # See further ahead

    # Player constants - MUCH FASTER
    MAX_SPEED = 800  # Much faster top speed
    ACCELERATION = 500  # Faster acceleration
    BRAKE_POWER = 600
    CENTRIFUGAL = 0.25
    OFF_ROAD_DECEL = 0.94

    # Track
    TRACK_LENGTH = 5000  # Longer track
    TOTAL_LAPS = 3

    FIRE_COOLDOWN = 0.5

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        super().__init__(genre, screen_width, screen_height)

        # Player state
        self.player_x = 0.0  # -1 to 1 (left to right on road)
        self.position = 0.0  # Position along track
        self.speed = 0.0
        self.lap = 0

        # Road segments
        self.segments: List[RoadSegment] = []

        # Enemy racers
        self.racers: List[EnemyRacer] = []

        # Projectiles
        self.projectiles: List[Projectile] = []
        self.fire_cooldown = 0.0

        # Race state
        self.race_started = False
        self.race_countdown = 3.0
        self.race_time = 0.0
        self.race_complete = False

        # Build track
        self._build_track()

        # Colors (vibrant racing game palette)
        self.colors = {
            "sky_top": (100, 180, 255),
            "sky_bottom": (200, 230, 255),
            "grass_light": (16, 200, 16),
            "grass_dark": (0, 154, 0),
            "road_light": (107, 107, 107),
            "road_dark": (90, 90, 90),
            "rumble_light": (255, 255, 255),
            "rumble_dark": (255, 0, 0),
            "lane": (255, 255, 255),
            "mountain": (100, 120, 140),
            "mountain_snow": (240, 245, 255),
        }

        # Background elements
        self.clouds = [(random.randint(0, screen_width), random.randint(20, 100)) for _ in range(5)]
        self.mountains = self._generate_mountains()

        self.on_zombie_eliminated_callback = None
        logger.info("Racing controller initialized (Rad Racer style)")

    def _generate_mountains(self) -> List[tuple]:
        """Generate mountain silhouettes for background."""
        mountains = []
        x = 0
        while x < self.screen_width * 2:
            height = random.randint(60, 120)
            width = random.randint(100, 200)
            mountains.append((x, height, width))
            x += width - 30
        return mountains

    def _build_track(self) -> None:
        """Build the race track with lots of curves and hills like Rad Racer."""
        self.segments = []

        for i in range(self.TRACK_LENGTH):
            curve = 0
            hill = 0

            # Create a varied, interesting track with lots of turns
            section = i % 400

            # S-curves at start
            if 20 < section < 50:
                curve = 0.7
            elif 50 < section < 80:
                curve = -0.7
            # Long sweeping right
            elif 90 < section < 140:
                curve = 0.5
            # Sharp left hairpin
            elif 150 < section < 180:
                curve = -1.2
            # Gentle right
            elif 200 < section < 250:
                curve = 0.4
            # Sharp right
            elif 260 < section < 290:
                curve = 1.0
            # Long left curve
            elif 310 < section < 370:
                curve = -0.6

            # Hills throughout - more dramatic
            hill_section = i % 150
            if 10 < hill_section < 35:
                hill = 40  # Uphill
            elif 35 < hill_section < 50:
                hill = -30  # Crest and downhill
            elif 70 < hill_section < 90:
                hill = -40  # Downhill dip
            elif 90 < hill_section < 110:
                hill = 35  # Back up
            elif 120 < hill_section < 135:
                hill = 20  # Small bump

            self.segments.append(RoadSegment(curve=curve, hill=hill, sprite_x=0))

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up racing level with zombie racers."""
        self.zombies = zombies
        self.racers.clear()
        self.projectiles.clear()

        # Create enemy racers from zombies
        num_racers = min(len(zombies), 6)

        for i, zombie in enumerate(zombies[:num_racers]):
            racer = EnemyRacer(
                zombie=zombie,
                road_position=200 + i * 200,  # Spread them ahead
                lane=random.uniform(-0.6, 0.6),
                speed=random.uniform(450, 650),  # Much faster - challenging!
                color=random.choice(CAR_COLORS),  # Random car color
            )
            self.racers.append(racer)
            zombie.is_hidden = False
            zombie.health = 100

        # Hide remaining zombies
        for zombie in zombies[num_racers:]:
            zombie.is_hidden = True

        # Reset player
        self.player_x = 0
        self.position = 0
        self.speed = 0
        self.lap = 0

        self.is_initialized = True
        self.race_started = False
        self.race_countdown = 3.0

        logger.info(f"Racing level initialized with {len(self.racers)} zombie racers")

    def update(self, delta_time: float, player) -> None:
        """Update racing game logic."""
        if not self.is_initialized:
            return

        # Countdown
        if not self.race_started:
            self.race_countdown -= delta_time
            if self.race_countdown <= 0:
                self.race_started = True
            return

        self.race_time += delta_time

        if self.fire_cooldown > 0:
            self.fire_cooldown -= delta_time

        # Update player position
        self._update_player(delta_time)

        # Update enemy racers
        self._update_racers(delta_time)

        # Update projectiles
        self._update_projectiles(delta_time)

        # Check collisions
        self._check_collisions()

        # Check lap completion
        if self.position >= self.TRACK_LENGTH * self.SEGMENT_LENGTH:
            self.position -= self.TRACK_LENGTH * self.SEGMENT_LENGTH
            self.lap += 1
            logger.info(f"🏁 Lap {self.lap} complete!")

            if self.lap >= self.TOTAL_LAPS:
                self.race_complete = True
                self.is_complete = True
                logger.info("🏆 Race finished!")

    def _update_player(self, delta_time: float) -> None:
        """Update player car physics."""
        # Get current road segment
        segment_index = int(self.position / self.SEGMENT_LENGTH) % len(self.segments)
        segment = self.segments[segment_index]

        # Apply centrifugal force on curves
        self.player_x -= segment.curve * self.speed * self.CENTRIFUGAL * delta_time * 0.01

        # Check if off road
        if abs(self.player_x) > 1:
            self.speed *= self.OFF_ROAD_DECEL
            # Bump back onto road
            if self.player_x > 1:
                self.player_x = 1
            elif self.player_x < -1:
                self.player_x = -1

        # Move forward
        self.position += self.speed * delta_time

    def _update_racers(self, delta_time: float) -> None:
        """Update enemy racer positions."""
        for racer in self.racers:
            if racer.eliminated:
                continue

            if racer.spin_timer > 0:
                racer.spin_timer -= delta_time
                racer.speed *= 0.95
                continue

            # Move forward
            racer.road_position += racer.speed * delta_time

            # Wrap around track
            if racer.road_position >= self.TRACK_LENGTH * self.SEGMENT_LENGTH:
                racer.road_position -= self.TRACK_LENGTH * self.SEGMENT_LENGTH

            # Slight lane weaving
            racer.lane += random.uniform(-0.5, 0.5) * delta_time
            racer.lane = max(-0.8, min(0.8, racer.lane))

    def _update_projectiles(self, delta_time: float) -> None:
        """Update projectile positions."""
        for proj in self.projectiles:
            if not proj.active:
                continue
            # Much faster projectiles (1500 units/sec instead of 500)
            proj.road_position += 1500 * delta_time

            # Deactivate if too far
            if proj.road_position > self.position + 8000:
                proj.active = False

        self.projectiles = [p for p in self.projectiles if p.active]

    def _check_collisions(self) -> None:
        """Check projectile-racer collisions."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            for racer in self.racers:
                if racer.eliminated or racer.spin_timer > 0:
                    continue

                # Check if projectile hit racer
                dist = abs(proj.road_position - racer.road_position)
                lane_dist = abs(proj.lane - racer.lane)

                if dist < 200 and lane_dist < 0.4:
                    proj.active = False
                    racer.zombie.take_damage(50)
                    racer.spin_timer = 1.5
                    racer.speed = 0

                    logger.info(f"💥 Hit {racer.zombie.identity_name}!")

                    if racer.zombie.health <= 0:
                        racer.eliminated = True
                        racer.zombie.is_hidden = True
                        if self.on_zombie_eliminated_callback:
                            self.on_zombie_eliminated_callback(racer.zombie)
                    break

    def handle_input(self, input_state: InputState, player) -> None:
        """Handle player input."""
        if not self.race_started:
            return

        # Steering
        if input_state.left:
            self.player_x -= 2.5 * 0.016
        if input_state.right:
            self.player_x += 2.5 * 0.016

        # Acceleration
        if input_state.up:
            self.speed = min(self.speed + self.ACCELERATION * 0.016, self.MAX_SPEED)
        elif input_state.down:
            self.speed = max(0, self.speed - self.BRAKE_POWER * 0.016)
        else:
            # Natural deceleration
            self.speed *= 0.99

        # Fire
        if input_state.shoot and self.fire_cooldown <= 0:
            self._fire_projectile()
            self.fire_cooldown = self.FIRE_COOLDOWN

    def _fire_projectile(self) -> None:
        """Fire a projectile ahead from the front of the car."""
        proj = Projectile(
            road_position=self.position + 300,  # Start further ahead (front of car)
            lane=self.player_x,
        )
        self.projectiles.append(proj)

    def check_completion(self) -> bool:
        return self.race_complete

    def get_active_zombie_count(self) -> int:
        return sum(1 for r in self.racers if not r.eliminated)

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render the pseudo-3D racing view."""
        # Gradient sky
        self._render_sky(surface)

        # Background mountains
        self._render_mountains(surface)

        # Ground/horizon
        horizon_y = self.screen_height // 2
        pygame.draw.rect(
            surface,
            self.colors["grass_light"],
            (0, horizon_y, self.screen_width, self.screen_height - horizon_y),
        )

        # Render road segments from back to front
        self._render_road(surface)

        # Render enemy cars
        self._render_racers(surface)

        # Render projectiles
        self._render_projectiles(surface)

        # Render player car (at bottom center)
        self._render_player_car(surface)

        # HUD
        self._render_hud(surface)

        # Countdown
        if not self.race_started:
            self._render_countdown(surface)

    def _render_sky(self, surface) -> None:
        """Render gradient sky with clouds (optimized with bands)."""
        horizon_y = self.screen_height // 2

        # Draw gradient in bands (much faster than per-line)
        num_bands = 12
        band_height = horizon_y // num_bands

        for i in range(num_bands):
            ratio = i / num_bands
            r = int(
                self.colors["sky_top"][0]
                + (self.colors["sky_bottom"][0] - self.colors["sky_top"][0]) * ratio
            )
            g = int(
                self.colors["sky_top"][1]
                + (self.colors["sky_bottom"][1] - self.colors["sky_top"][1]) * ratio
            )
            b = int(
                self.colors["sky_top"][2]
                + (self.colors["sky_bottom"][2] - self.colors["sky_top"][2]) * ratio
            )
            pygame.draw.rect(
                surface,
                (r, g, b),
                (0, i * band_height, self.screen_width, band_height + 1),
            )

        # Clouds (move with player position for parallax)
        cloud_offset = (self.position * 0.01) % self.screen_width
        for cx, cy in self.clouds:
            cloud_x = int((cx - cloud_offset) % self.screen_width)
            # Draw fluffy cloud
            pygame.draw.ellipse(surface, (255, 255, 255), (cloud_x, cy, 80, 30))
            pygame.draw.ellipse(surface, (255, 255, 255), (cloud_x + 20, cy - 15, 60, 35))
            pygame.draw.ellipse(surface, (255, 255, 255), (cloud_x + 50, cy, 70, 25))

    def _render_mountains(self, surface) -> None:
        """Render mountain silhouettes."""
        horizon_y = self.screen_height // 2
        mountain_offset = (self.position * 0.02) % (self.screen_width * 2)

        for mx, height, width in self.mountains:
            x = int((mx - mountain_offset) % (self.screen_width * 2) - self.screen_width // 2)
            if -width < x < self.screen_width + width:
                # Mountain triangle
                points = [
                    (x, horizon_y),
                    (x + width // 2, horizon_y - height),
                    (x + width, horizon_y),
                ]
                pygame.draw.polygon(surface, self.colors["mountain"], points)
                # Snow cap
                snow_points = [
                    (x + width // 2 - 15, horizon_y - height + 20),
                    (x + width // 2, horizon_y - height),
                    (x + width // 2 + 15, horizon_y - height + 20),
                ]
                pygame.draw.polygon(surface, self.colors["mountain_snow"], snow_points)

    def _render_road(self, surface) -> None:
        """Render the pseudo-3D road."""
        base_segment = int(self.position / self.SEGMENT_LENGTH)

        # Camera height and depth
        camera_height = 1000
        camera_depth = 1 / math.tan(80 * math.pi / 360)  # FOV

        max_y = self.screen_height

        x = 0
        dx = 0

        for n in range(self.DRAW_DISTANCE):
            segment_index = (base_segment + n) % len(self.segments)
            segment = self.segments[segment_index]

            # Project to screen
            scale = camera_depth / (n + 1)

            # Road width at this distance
            road_width = self.ROAD_WIDTH * scale

            # Screen Y position
            y = int(self.screen_height / 2 + camera_height * scale)

            if y >= max_y:
                continue

            # Accumulate curve
            x += dx
            dx += segment.curve * scale * 2

            # Screen X position (centered + curve + player offset)
            screen_x = self.screen_width / 2 + x - self.player_x * road_width

            # Determine colors (alternating for rumble strips)
            rumble = (segment_index // self.RUMBLE_LENGTH) % 2 == 0

            grass_color = self.colors["grass_light"] if rumble else self.colors["grass_dark"]
            road_color = self.colors["road_light"] if rumble else self.colors["road_dark"]
            rumble_color = self.colors["rumble_light"] if rumble else self.colors["rumble_dark"]

            # Draw grass
            pygame.draw.rect(surface, grass_color, (0, y, self.screen_width, max_y - y))

            # Draw road
            road_left = int(screen_x - road_width / 2)
            road_right = int(screen_x + road_width / 2)
            pygame.draw.rect(surface, road_color, (road_left, y, road_right - road_left, max_y - y))

            # Draw rumble strips
            rumble_width = int(road_width * 0.1)
            pygame.draw.rect(
                surface,
                rumble_color,
                (road_left - rumble_width, y, rumble_width, max_y - y),
            )
            pygame.draw.rect(surface, rumble_color, (road_right, y, rumble_width, max_y - y))

            # Draw center line (dashed)
            if rumble:
                line_width = max(2, int(road_width * 0.02))
                pygame.draw.rect(
                    surface,
                    self.colors["lane"],
                    (int(screen_x - line_width / 2), y, line_width, max_y - y),
                )

            max_y = y

    def _render_racers(self, surface) -> None:
        """Render enemy racers as sporty cars matching player car style."""
        camera_depth = 1 / math.tan(80 * math.pi / 360)

        # Sort racers by distance (far to near)
        visible_racers = []
        for racer in self.racers:
            if racer.eliminated:
                continue

            dist = racer.road_position - self.position
            if dist < 0:
                dist += self.TRACK_LENGTH * self.SEGMENT_LENGTH

            if 0 < dist < self.DRAW_DISTANCE * self.SEGMENT_LENGTH:
                visible_racers.append((racer, dist))

        visible_racers.sort(key=lambda x: x[1], reverse=True)

        for racer, dist in visible_racers:
            # Calculate screen position
            n = dist / self.SEGMENT_LENGTH
            scale = camera_depth / (n + 1)

            # Scale factor to make cars MUCH bigger (similar to player car)
            size_mult = 4.0  # Make cars 4x bigger to match player car size

            y = int(self.screen_height / 2 + 1000 * scale)
            road_width = self.ROAD_WIDTH * scale

            # X position based on lane
            x = self.screen_width / 2 + (racer.lane - self.player_x) * road_width / 2

            # Use racer's random color or gray if spinning
            if racer.spin_timer <= 0:
                body_main, body_dark, body_light = racer.color
            else:
                body_main = (120, 120, 120)
                body_dark = (80, 80, 80)
                body_light = (160, 160, 160)

            cx = int(x)
            cy = int(y)

            # Scale all dimensions
            s = scale * size_mult

            # Only render if big enough to see
            if s < 0.05:
                continue

            # === SHADOW ===
            shadow_w = int(100 * s)
            shadow_h = int(20 * s)
            if shadow_w > 5:
                pygame.draw.ellipse(
                    surface,
                    (20, 20, 20),
                    (cx - shadow_w // 2, cy - int(3 * s), shadow_w, shadow_h),
                )

            # === REAR WHEELS ===
            wheel_w = int(18 * s)
            wheel_h = int(25 * s)
            if wheel_w > 3:
                pygame.draw.ellipse(
                    surface,
                    (40, 40, 40),
                    (cx - int(52 * s), cy - int(25 * s), wheel_w, wheel_h),
                )
                pygame.draw.ellipse(
                    surface,
                    (40, 40, 40),
                    (cx + int(34 * s), cy - int(25 * s), wheel_w, wheel_h),
                )

            # === MAIN BODY - Sports car silhouette ===
            body_points = [
                (cx - int(45 * s), cy),  # Bottom left
                (cx - int(48 * s), cy - int(20 * s)),  # Left side
                (cx - int(42 * s), cy - int(40 * s)),  # Left shoulder
                (cx - int(30 * s), cy - int(50 * s)),  # Left roof edge
                (cx + int(30 * s), cy - int(50 * s)),  # Right roof edge
                (cx + int(42 * s), cy - int(40 * s)),  # Right shoulder
                (cx + int(48 * s), cy - int(20 * s)),  # Right side
                (cx + int(45 * s), cy),  # Bottom right
            ]
            pygame.draw.polygon(surface, body_main, body_points)

            # === BODY HIGHLIGHTS ===
            highlight_left = [
                (cx - int(45 * s), cy - int(5 * s)),
                (cx - int(46 * s), cy - int(25 * s)),
                (cx - int(40 * s), cy - int(37 * s)),
                (cx - int(35 * s), cy - int(35 * s)),
                (cx - int(38 * s), cy - int(20 * s)),
                (cx - int(40 * s), cy - int(5 * s)),
            ]
            pygame.draw.polygon(surface, body_light, highlight_left)

            highlight_right = [
                (cx + int(45 * s), cy - int(5 * s)),
                (cx + int(46 * s), cy - int(25 * s)),
                (cx + int(40 * s), cy - int(37 * s)),
                (cx + int(35 * s), cy - int(35 * s)),
                (cx + int(38 * s), cy - int(20 * s)),
                (cx + int(40 * s), cy - int(5 * s)),
            ]
            pygame.draw.polygon(surface, body_light, highlight_right)

            # === REAR WINDOW ===
            window_points = [
                (cx - int(25 * s), cy - int(47 * s)),
                (cx - int(20 * s), cy - int(60 * s)),
                (cx + int(20 * s), cy - int(60 * s)),
                (cx + int(25 * s), cy - int(47 * s)),
            ]
            pygame.draw.polygon(surface, (80, 120, 160), window_points)

            # === SPOILER ===
            if s > 0.15:
                spoiler_y = cy - int(65 * s)
                pygame.draw.rect(
                    surface,
                    (60, 60, 60),
                    (cx - int(40 * s), spoiler_y, int(80 * s), int(5 * s)),
                )
                pygame.draw.rect(
                    surface,
                    (60, 60, 60),
                    (cx - int(25 * s), spoiler_y + int(3 * s), int(4 * s), int(12 * s)),
                )
                pygame.draw.rect(
                    surface,
                    (60, 60, 60),
                    (cx + int(21 * s), spoiler_y + int(3 * s), int(4 * s), int(12 * s)),
                )

            # === TAIL LIGHTS (LED strip style) ===
            light_w = int(12 * s)
            light_h = max(2, int(4 * s))
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (cx - int(42 * s), cy - int(15 * s), light_w, light_h),
            )
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (cx + int(30 * s), cy - int(15 * s), light_w, light_h),
            )

            # === EXHAUST PIPES ===
            if s > 0.12:
                exhaust_r = max(2, int(5 * s))
                pygame.draw.circle(
                    surface,
                    (80, 80, 80),
                    (cx - int(15 * s), cy - int(2 * s)),
                    exhaust_r,
                )
                pygame.draw.circle(
                    surface,
                    (80, 80, 80),
                    (cx + int(15 * s), cy - int(2 * s)),
                    exhaust_r,
                )

            # === NAME LABEL ===
            if s > 0.2:
                font = pygame.font.Font(None, max(16, int(24 * s)))
                name = racer.zombie.identity_name[:12]
                label = font.render(name, True, (255, 255, 255))
                label_bg = pygame.Surface((label.get_width() + 4, label.get_height() + 2))
                label_bg.fill((0, 0, 0))
                label_bg.set_alpha(150)
                surface.blit(label_bg, (cx - label.get_width() // 2 - 2, cy - int(75 * s)))
                surface.blit(label, (cx - label.get_width() // 2, cy - int(73 * s)))

    def _render_projectiles(self, surface) -> None:
        """Render projectiles as energy blasts."""
        camera_depth = 1 / math.tan(80 * math.pi / 360)

        for proj in self.projectiles:
            if not proj.active:
                continue

            dist = proj.road_position - self.position
            if dist <= 0 or dist > self.DRAW_DISTANCE * self.SEGMENT_LENGTH:
                continue

            n = dist / self.SEGMENT_LENGTH
            scale = camera_depth / (n + 1)

            y = int(self.screen_height / 2 + 1000 * scale)
            road_width = self.ROAD_WIDTH * scale
            x = self.screen_width / 2 + (proj.lane - self.player_x) * road_width / 2

            # Much larger projectile with glow effect
            size = max(8, int(35 * scale))

            # Outer glow (purple)
            pygame.draw.circle(surface, (180, 100, 255), (int(x), int(y - size)), size + 4)
            # Middle glow
            pygame.draw.circle(surface, (220, 150, 255), (int(x), int(y - size)), size + 2)
            # Core (bright)
            pygame.draw.circle(surface, (255, 200, 255), (int(x), int(y - size)), size)
            # Inner bright spot
            pygame.draw.circle(surface, (255, 255, 255), (int(x), int(y - size)), max(3, size // 2))

    def _render_player_car(self, surface) -> None:
        """Render a sleek sports car (Lamborghini/Ferrari style) from behind."""
        # Car position (bottom center, offset by steering)
        car_x = self.screen_width // 2 + int(self.player_x * 80)
        car_y = self.screen_height - 120

        # Sports car colors (Sonrai purple theme)
        body_main = (120, 50, 180)
        body_light = (160, 80, 220)
        body_dark = (80, 30, 120)
        body_accent = (200, 120, 255)
        glass = (80, 120, 160)
        glass_shine = (150, 180, 220)

        # Shadow under car
        pygame.draw.ellipse(surface, (20, 20, 20, 100), (car_x - 50, car_y + 55, 100, 20))

        # === REAR WHEELS (behind body) ===
        wheel_color = (25, 25, 25)
        tire_color = (40, 40, 40)
        # Left wheel
        pygame.draw.ellipse(surface, tire_color, (car_x - 52, car_y + 35, 18, 25))
        pygame.draw.ellipse(surface, wheel_color, (car_x - 50, car_y + 38, 14, 19))
        # Right wheel
        pygame.draw.ellipse(surface, tire_color, (car_x + 34, car_y + 35, 18, 25))
        pygame.draw.ellipse(surface, wheel_color, (car_x + 36, car_y + 38, 14, 19))

        # === MAIN BODY - Low, wide sports car silhouette ===
        # Lower body (wide rear)
        body_points = [
            (car_x - 45, car_y + 55),  # Bottom left
            (car_x - 48, car_y + 35),  # Left side
            (car_x - 42, car_y + 15),  # Left shoulder
            (car_x - 30, car_y + 5),  # Left roof edge
            (car_x + 30, car_y + 5),  # Right roof edge
            (car_x + 42, car_y + 15),  # Right shoulder
            (car_x + 48, car_y + 35),  # Right side
            (car_x + 45, car_y + 55),  # Bottom right
        ]
        pygame.draw.polygon(surface, body_main, body_points)

        # Body highlights (left side)
        highlight_left = [
            (car_x - 45, car_y + 50),
            (car_x - 46, car_y + 30),
            (car_x - 40, car_y + 18),
            (car_x - 35, car_y + 20),
            (car_x - 38, car_y + 35),
            (car_x - 40, car_y + 50),
        ]
        pygame.draw.polygon(surface, body_light, highlight_left)

        # Body highlights (right side)
        highlight_right = [
            (car_x + 45, car_y + 50),
            (car_x + 46, car_y + 30),
            (car_x + 40, car_y + 18),
            (car_x + 35, car_y + 20),
            (car_x + 38, car_y + 35),
            (car_x + 40, car_y + 50),
        ]
        pygame.draw.polygon(surface, body_light, highlight_right)

        # === REAR WINDOW / ENGINE COVER ===
        window_points = [
            (car_x - 25, car_y + 8),
            (car_x - 20, car_y - 5),
            (car_x + 20, car_y - 5),
            (car_x + 25, car_y + 8),
        ]
        pygame.draw.polygon(surface, glass, window_points)
        # Window shine
        shine_points = [
            (car_x - 15, car_y + 5),
            (car_x - 12, car_y - 2),
            (car_x + 5, car_y - 2),
            (car_x + 2, car_y + 5),
        ]
        pygame.draw.polygon(surface, glass_shine, shine_points)

        # === SPOILER (racing style) ===
        spoiler_color = (60, 60, 60)
        # Spoiler wing
        pygame.draw.rect(surface, spoiler_color, (car_x - 40, car_y - 12, 80, 5))
        # Spoiler supports
        pygame.draw.rect(surface, spoiler_color, (car_x - 25, car_y - 10, 4, 12))
        pygame.draw.rect(surface, spoiler_color, (car_x + 21, car_y - 10, 4, 12))

        # === REAR DIFFUSER ===
        diffuser_points = [
            (car_x - 35, car_y + 55),
            (car_x - 30, car_y + 48),
            (car_x + 30, car_y + 48),
            (car_x + 35, car_y + 55),
        ]
        pygame.draw.polygon(surface, body_dark, diffuser_points)

        # Diffuser vents
        for i in range(-2, 3):
            vent_x = car_x + i * 12
            pygame.draw.line(surface, (40, 40, 40), (vent_x, car_y + 50), (vent_x, car_y + 55), 2)

        # === TAIL LIGHTS (LED strip style) ===
        # Left tail light strip
        pygame.draw.rect(surface, (255, 0, 0), (car_x - 42, car_y + 40, 12, 4))
        pygame.draw.rect(surface, (255, 100, 100), (car_x - 40, car_y + 41, 8, 2))
        # Right tail light strip
        pygame.draw.rect(surface, (255, 0, 0), (car_x + 30, car_y + 40, 12, 4))
        pygame.draw.rect(surface, (255, 100, 100), (car_x + 32, car_y + 41, 8, 2))

        # Center brake light
        pygame.draw.rect(surface, (200, 0, 0), (car_x - 15, car_y + 6, 30, 3))

        # === EXHAUST PIPES ===
        exhaust_color = (80, 80, 80)
        # Quad exhaust
        pygame.draw.circle(surface, exhaust_color, (car_x - 20, car_y + 53), 5)
        pygame.draw.circle(surface, (50, 50, 50), (car_x - 20, car_y + 53), 3)
        pygame.draw.circle(surface, exhaust_color, (car_x - 10, car_y + 53), 5)
        pygame.draw.circle(surface, (50, 50, 50), (car_x - 10, car_y + 53), 3)
        pygame.draw.circle(surface, exhaust_color, (car_x + 10, car_y + 53), 5)
        pygame.draw.circle(surface, (50, 50, 50), (car_x + 10, car_y + 53), 3)
        pygame.draw.circle(surface, exhaust_color, (car_x + 20, car_y + 53), 5)
        pygame.draw.circle(surface, (50, 50, 50), (car_x + 20, car_y + 53), 3)

        # === RACING STRIPE ===
        pygame.draw.line(surface, body_accent, (car_x, car_y - 8), (car_x, car_y + 55), 4)

    def _render_hud(self, surface) -> None:
        """Render the HUD."""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        # Speed - display as reasonable MPH (internal speed / 4)
        display_speed = int(self.speed / 4)
        speed_text = f"SPEED: {display_speed} MPH"
        surface.blit(font.render(speed_text, True, (255, 255, 255)), (20, 20))

        # Lap
        lap_text = f"LAP: {min(self.lap + 1, self.TOTAL_LAPS)}/{self.TOTAL_LAPS}"
        surface.blit(font.render(lap_text, True, (255, 255, 255)), (20, 55))

        # Time
        mins = int(self.race_time // 60)
        secs = int(self.race_time % 60)
        time_text = f"TIME: {mins}:{secs:02d}"
        surface.blit(small_font.render(time_text, True, (255, 255, 255)), (20, 90))

        # Racers remaining
        remaining = self.get_active_zombie_count()
        racers_text = f"ZOMBIES: {remaining}"
        surface.blit(small_font.render(racers_text, True, (255, 255, 255)), (20, 115))

        # Controls
        hint = "←→: Steer | ↑: Gas | ↓: Brake | SPACE: Fire"
        hint_surface = small_font.render(hint, True, (200, 200, 200))
        surface.blit(
            hint_surface,
            (
                self.screen_width // 2 - hint_surface.get_width() // 2,
                self.screen_height - 25,
            ),
        )

    def _render_countdown(self, surface) -> None:
        """Render countdown."""
        font = pygame.font.Font(None, 120)

        count = max(1, int(self.race_countdown) + 1)
        if count > 3:
            count = 3

        text = str(count) if self.race_countdown > 0 else "GO!"
        color = (255, 255, 0) if self.race_countdown > 0 else (0, 255, 0)

        text_surface = font.render(text, True, color)
        x = self.screen_width // 2 - text_surface.get_width() // 2
        y = self.screen_height // 3

        # Shadow
        shadow = font.render(text, True, (0, 0, 0))
        surface.blit(shadow, (x + 3, y + 3))
        surface.blit(text_surface, (x, y))


# Register
GenreControllerFactory.register(GenreType.RACING, RacingController)
