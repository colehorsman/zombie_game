"""Racing genre controller for Mario Kart style gameplay.

Implements 8-bit style top-down racing with the player racing against
zombie karts on a track. Zap opponents or beat them to the finish!

**Feature: multi-genre-levels**
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.6**
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import List, Optional

import pygame

from genre_controller import GenreController, GenreControllerFactory, InputState
from models import GenreType, Vector2

logger = logging.getLogger(__name__)


@dataclass
class RacingProjectile:
    """Projectile fired by the player kart (shell/zap)."""

    position: Vector2
    velocity: Vector2
    damage: int = 50  # 2 hits to eliminate
    radius: int = 10
    active: bool = True


@dataclass
class RacerKart:
    """AI racer kart (zombie)."""

    zombie: object  # Reference to zombie entity
    position: Vector2
    velocity: float = 0
    angle: float = 0  # Direction in radians
    lap: int = 0
    checkpoint: int = 0
    speed: float = 100
    max_speed: float = 150
    is_eliminated: bool = False
    stun_timer: float = 0


class RacingController(GenreController):
    """Controller for Mario Kart style 8-bit racing gameplay.

    Features:
    - Top-down oval race track
    - Player kart at bottom
    - AI zombie karts racing
    - Shoot shells to stun/eliminate opponents
    - Complete laps to win

    **Property 6: Racing Player Controls**
    Player controls kart with steering and acceleration.
    **Validates: Requirements 3.2, 3.4**

    **Property 7: Racing Zombie Behavior**
    Zombies race as AI karts, can be zapped.
    **Validates: Requirements 3.3, 3.6**
    """

    # Game constants
    PLAYER_ACCELERATION = 200
    PLAYER_MAX_SPEED = 250
    PLAYER_TURN_SPEED = 3.5
    PLAYER_FRICTION = 0.98
    FIRE_COOLDOWN = 0.5
    PROJECTILE_SPEED = 400
    TOTAL_LAPS = 3

    # Track constants (oval track)
    TRACK_CENTER_X = 640
    TRACK_CENTER_Y = 360
    TRACK_RADIUS_X = 500  # Horizontal radius
    TRACK_RADIUS_Y = 280  # Vertical radius
    TRACK_WIDTH = 100  # Width of the road

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the racing controller."""
        super().__init__(genre, screen_width, screen_height)

        # Player state
        self.player_x = self.TRACK_CENTER_X
        self.player_y = self.TRACK_CENTER_Y + self.TRACK_RADIUS_Y - 30
        self.player_angle = -math.pi / 2  # Facing up
        self.player_speed = 0
        self.player_lap = 0
        self.player_checkpoint = 0

        # Projectiles
        self.projectiles: List[RacingProjectile] = []
        self.fire_cooldown = 0

        # AI racers
        self.racers: List[RacerKart] = []

        # Race state
        self.race_started = False
        self.race_countdown = 3.0
        self.race_time = 0
        self.race_complete = False
        self.player_position = 1  # Current race position

        # Callback for zombie elimination
        self.on_zombie_eliminated_callback = None

        logger.info("RacingController initialized")

    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up racing level with zombie karts."""
        self.zombies = zombies
        self.racers.clear()
        self.projectiles.clear()

        # Create AI racers from zombies
        num_racers = min(len(zombies), 7)  # Max 7 AI racers + player = 8
        for i, zombie in enumerate(zombies[:num_racers]):
            # Position racers around the starting line
            angle_offset = (i + 1) * 0.15  # Spread them out
            start_angle = -math.pi / 2 + angle_offset

            # Calculate position on track
            x = self.TRACK_CENTER_X + math.cos(start_angle) * self.TRACK_RADIUS_X
            y = self.TRACK_CENTER_Y + math.sin(start_angle) * self.TRACK_RADIUS_Y

            racer = RacerKart(
                zombie=zombie,
                position=Vector2(x, y),
                angle=start_angle + math.pi / 2,  # Face along track
                speed=random.uniform(80, 120),
                max_speed=random.uniform(130, 180),
            )
            self.racers.append(racer)

            # Update zombie position
            zombie.position = Vector2(x, y)
            zombie.is_hidden = False

        # Hide remaining zombies
        for zombie in zombies[num_racers:]:
            zombie.is_hidden = True

        self.is_initialized = True
        self.race_started = False
        self.race_countdown = 3.0
        logger.info(f"Racing level initialized with {len(self.racers)} AI racers")

    def update(self, delta_time: float, player) -> None:
        """Update racing game logic."""
        if not self.is_initialized:
            return

        # Handle countdown
        if not self.race_started:
            self.race_countdown -= delta_time
            if self.race_countdown <= 0:
                self.race_started = True
            return

        # Update race time
        self.race_time += delta_time

        # Update fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= delta_time

        # Update player physics
        self._update_player_physics(delta_time)

        # Update AI racers
        self._update_ai_racers(delta_time)

        # Update projectiles
        self._update_projectiles(delta_time)

        # Check projectile collisions
        self._check_projectile_collisions()

        # Update race positions
        self._update_race_positions()

        # Check lap completion
        self._check_lap_completion()

        # Sync player position
        player.position.x = self.player_x
        player.position.y = self.player_y

        # Check completion
        if self.player_lap >= self.TOTAL_LAPS:
            self.race_complete = True
            self.is_complete = True

    def _update_player_physics(self, delta_time: float) -> None:
        """Update player kart physics."""
        # Apply friction
        self.player_speed *= self.PLAYER_FRICTION

        # Move player
        self.player_x += math.cos(self.player_angle) * self.player_speed * delta_time
        self.player_y += math.sin(self.player_angle) * self.player_speed * delta_time

        # Keep on track (simple boundary)
        self._keep_on_track()

    def _keep_on_track(self) -> None:
        """Keep player on the oval track."""
        # Calculate normalized position relative to track center
        dx = (self.player_x - self.TRACK_CENTER_X) / self.TRACK_RADIUS_X
        dy = (self.player_y - self.TRACK_CENTER_Y) / self.TRACK_RADIUS_Y
        dist = math.sqrt(dx * dx + dy * dy)

        # Inner and outer boundaries
        inner_bound = 0.6
        outer_bound = 1.3

        if dist < inner_bound or dist > outer_bound:
            # Push back onto track
            target_dist = 1.0 if dist > outer_bound else 0.8
            angle = math.atan2(dy, dx)
            self.player_x = (
                self.TRACK_CENTER_X + math.cos(angle) * self.TRACK_RADIUS_X * target_dist
            )
            self.player_y = (
                self.TRACK_CENTER_Y + math.sin(angle) * self.TRACK_RADIUS_Y * target_dist
            )
            self.player_speed *= 0.5  # Slow down on collision

    def _update_ai_racers(self, delta_time: float) -> None:
        """Update AI racer movement."""
        for racer in self.racers:
            if racer.is_eliminated:
                continue

            # Update stun timer
            if racer.stun_timer > 0:
                racer.stun_timer -= delta_time
                continue

            # Calculate target angle (follow track)
            dx = (racer.position.x - self.TRACK_CENTER_X) / self.TRACK_RADIUS_X
            dy = (racer.position.y - self.TRACK_CENTER_Y) / self.TRACK_RADIUS_Y
            current_angle = math.atan2(dy, dx)

            # Target is 90 degrees ahead on the track (counter-clockwise)
            target_angle = current_angle - math.pi / 2

            # Smoothly turn toward target
            angle_diff = target_angle - racer.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            racer.angle += angle_diff * 2 * delta_time

            # Accelerate
            racer.velocity = min(racer.velocity + 50 * delta_time, racer.max_speed)

            # Move
            racer.position.x += math.cos(racer.angle) * racer.velocity * delta_time
            racer.position.y += math.sin(racer.angle) * racer.velocity * delta_time

            # Update zombie position
            racer.zombie.position = racer.position

    def _update_projectiles(self, delta_time: float) -> None:
        """Update projectile positions."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            proj.position.x += proj.velocity.x * delta_time
            proj.position.y += proj.velocity.y * delta_time

            # Remove if off screen
            if (
                proj.position.x < 0
                or proj.position.x > self.screen_width
                or proj.position.y < 0
                or proj.position.y > self.screen_height
            ):
                proj.active = False

        # Clean up inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def _check_projectile_collisions(self) -> None:
        """Check for projectile-racer collisions."""
        for proj in self.projectiles:
            if not proj.active:
                continue

            for racer in self.racers:
                if racer.is_eliminated:
                    continue

                # Simple distance check
                dx = proj.position.x - racer.position.x
                dy = proj.position.y - racer.position.y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < 30:  # Hit radius
                    proj.active = False
                    racer.zombie.take_damage(proj.damage)

                    if racer.zombie.health <= 0:
                        racer.is_eliminated = True
                        racer.zombie.is_hidden = True
                        if self.on_zombie_eliminated_callback:
                            self.on_zombie_eliminated_callback(racer.zombie)
                        logger.info(f"Racer eliminated! {racer.zombie.identity_name}")
                    else:
                        racer.stun_timer = 1.5  # Stun for 1.5 seconds
                        racer.velocity = 0
                        logger.debug(f"Racer stunned! {racer.zombie.identity_name}")
                    break

    def _update_race_positions(self) -> None:
        """Calculate current race positions."""
        # Simple position based on progress around track
        positions = []

        # Player progress
        player_dx = (self.player_x - self.TRACK_CENTER_X) / self.TRACK_RADIUS_X
        player_dy = (self.player_y - self.TRACK_CENTER_Y) / self.TRACK_RADIUS_Y
        player_angle = math.atan2(player_dy, player_dx)
        player_progress = self.player_lap * 2 * math.pi - player_angle
        positions.append(("player", player_progress))

        # Racer progress
        for racer in self.racers:
            if racer.is_eliminated:
                continue
            dx = (racer.position.x - self.TRACK_CENTER_X) / self.TRACK_RADIUS_X
            dy = (racer.position.y - self.TRACK_CENTER_Y) / self.TRACK_RADIUS_Y
            angle = math.atan2(dy, dx)
            progress = racer.lap * 2 * math.pi - angle
            positions.append((racer, progress))

        # Sort by progress (higher is better)
        positions.sort(key=lambda x: x[1], reverse=True)

        # Find player position
        for i, (entity, _) in enumerate(positions):
            if entity == "player":
                self.player_position = i + 1
                break

    def _check_lap_completion(self) -> None:
        """Check if player completed a lap."""
        # Simple checkpoint system based on angle
        player_dx = (self.player_x - self.TRACK_CENTER_X) / self.TRACK_RADIUS_X
        player_dy = (self.player_y - self.TRACK_CENTER_Y) / self.TRACK_RADIUS_Y
        player_angle = math.atan2(player_dy, player_dx)

        # Checkpoint at top of track (angle near -pi/2)
        if abs(player_angle + math.pi / 2) < 0.3:
            if self.player_checkpoint == 1:
                self.player_lap += 1
                self.player_checkpoint = 0
                logger.info(f"Lap {self.player_lap} complete!")
        # Checkpoint at bottom of track (angle near pi/2)
        elif abs(player_angle - math.pi / 2) < 0.3:
            self.player_checkpoint = 1

    def handle_input(self, input_state: InputState, player) -> None:
        """Process racing input."""
        if not self.race_started:
            return

        # Steering
        if input_state.left:
            self.player_angle -= self.PLAYER_TURN_SPEED * 0.016
        if input_state.right:
            self.player_angle += self.PLAYER_TURN_SPEED * 0.016

        # Acceleration
        if input_state.up:
            self.player_speed = min(
                self.player_speed + self.PLAYER_ACCELERATION * 0.016,
                self.PLAYER_MAX_SPEED,
            )
        elif input_state.down:
            self.player_speed = max(
                self.player_speed - self.PLAYER_ACCELERATION * 0.016,
                -self.PLAYER_MAX_SPEED / 2,
            )

        # Shooting
        if input_state.shoot and self.fire_cooldown <= 0:
            self._fire_projectile()
            self.fire_cooldown = self.FIRE_COOLDOWN

    def _fire_projectile(self) -> None:
        """Fire a shell projectile."""
        proj = RacingProjectile(
            position=Vector2(self.player_x, self.player_y),
            velocity=Vector2(
                math.cos(self.player_angle) * self.PROJECTILE_SPEED,
                math.sin(self.player_angle) * self.PROJECTILE_SPEED,
            ),
        )
        self.projectiles.append(proj)

    def check_completion(self) -> bool:
        """Check if race is complete."""
        return self.race_complete or self.is_complete

    def get_active_zombie_count(self) -> int:
        """Get count of active racers."""
        return sum(1 for r in self.racers if not r.is_eliminated)

    def render(self, surface, camera_offset: Vector2) -> None:
        """Render racing elements."""
        # Render track
        self._render_track(surface)

        # Render AI racers with labels
        self._render_racers(surface)

        # Render projectiles
        self._render_projectiles(surface)

        # Render player kart
        self._render_player_kart(surface)

        # Render HUD
        self._render_hud(surface)

        # Render countdown
        if not self.race_started:
            self._render_countdown(surface)

    def _render_track(self, surface) -> None:
        """Render the oval race track."""
        # Track colors
        GRASS = (34, 139, 34)
        TRACK = (80, 80, 80)
        TRACK_EDGE = (255, 255, 255)
        TRACK_LINE = (255, 255, 0)

        # Fill with grass
        surface.fill(GRASS)

        # Draw outer track edge
        pygame.draw.ellipse(
            surface,
            TRACK_EDGE,
            (
                self.TRACK_CENTER_X - self.TRACK_RADIUS_X - self.TRACK_WIDTH // 2,
                self.TRACK_CENTER_Y - self.TRACK_RADIUS_Y - self.TRACK_WIDTH // 2,
                (self.TRACK_RADIUS_X + self.TRACK_WIDTH // 2) * 2,
                (self.TRACK_RADIUS_Y + self.TRACK_WIDTH // 2) * 2,
            ),
            3,
        )

        # Draw track surface
        pygame.draw.ellipse(
            surface,
            TRACK,
            (
                self.TRACK_CENTER_X - self.TRACK_RADIUS_X - self.TRACK_WIDTH // 2 + 3,
                self.TRACK_CENTER_Y - self.TRACK_RADIUS_Y - self.TRACK_WIDTH // 2 + 3,
                (self.TRACK_RADIUS_X + self.TRACK_WIDTH // 2) * 2 - 6,
                (self.TRACK_RADIUS_Y + self.TRACK_WIDTH // 2) * 2 - 6,
            ),
        )

        # Draw inner grass (center of track)
        pygame.draw.ellipse(
            surface,
            GRASS,
            (
                self.TRACK_CENTER_X - self.TRACK_RADIUS_X + self.TRACK_WIDTH // 2,
                self.TRACK_CENTER_Y - self.TRACK_RADIUS_Y + self.TRACK_WIDTH // 2,
                (self.TRACK_RADIUS_X - self.TRACK_WIDTH // 2) * 2,
                (self.TRACK_RADIUS_Y - self.TRACK_WIDTH // 2) * 2,
            ),
        )

        # Draw inner track edge
        pygame.draw.ellipse(
            surface,
            TRACK_EDGE,
            (
                self.TRACK_CENTER_X - self.TRACK_RADIUS_X + self.TRACK_WIDTH // 2,
                self.TRACK_CENTER_Y - self.TRACK_RADIUS_Y + self.TRACK_WIDTH // 2,
                (self.TRACK_RADIUS_X - self.TRACK_WIDTH // 2) * 2,
                (self.TRACK_RADIUS_Y - self.TRACK_WIDTH // 2) * 2,
            ),
            3,
        )

        # Draw start/finish line
        pygame.draw.rect(
            surface,
            TRACK_LINE,
            (
                self.TRACK_CENTER_X - 5,
                self.TRACK_CENTER_Y + self.TRACK_RADIUS_Y - self.TRACK_WIDTH // 2,
                10,
                self.TRACK_WIDTH,
            ),
        )

    def _render_racers(self, surface) -> None:
        """Render AI racer karts with labels."""
        font = pygame.font.Font(None, 16)

        for racer in self.racers:
            if racer.is_eliminated:
                continue

            x, y = int(racer.position.x), int(racer.position.y)

            # Kart color (green for zombies)
            if racer.stun_timer > 0:
                color = (150, 150, 150)  # Gray when stunned
            else:
                color = (0, 200, 0)  # Green

            # Draw kart body (rotated rectangle approximation)
            angle = racer.angle
            cos_a, sin_a = math.cos(angle), math.sin(angle)

            # Kart points
            points = [
                (x + cos_a * 15 - sin_a * 8, y + sin_a * 15 + cos_a * 8),
                (x + cos_a * 15 + sin_a * 8, y + sin_a * 15 - cos_a * 8),
                (x - cos_a * 10 + sin_a * 8, y - sin_a * 10 - cos_a * 8),
                (x - cos_a * 10 - sin_a * 8, y - sin_a * 10 + cos_a * 8),
            ]
            pygame.draw.polygon(surface, color, points)

            # Draw wheels
            wheel_color = (50, 50, 50)
            for wx, wy in [(10, 6), (10, -6), (-8, 6), (-8, -6)]:
                wheel_x = x + cos_a * wx - sin_a * wy
                wheel_y = y + sin_a * wx + cos_a * wy
                pygame.draw.circle(surface, wheel_color, (int(wheel_x), int(wheel_y)), 4)

            # Render name label
            label_text = racer.zombie.identity_name
            if len(label_text) > 12:
                label_text = label_text[:9] + "..."
            label_surface = font.render(label_text, True, (255, 255, 255))
            label_x = x - label_surface.get_width() // 2
            label_y = y - 25
            surface.blit(label_surface, (label_x, label_y))

    def _render_projectiles(self, surface) -> None:
        """Render shell projectiles."""
        for proj in self.projectiles:
            if proj.active:
                # Draw as red shell
                pygame.draw.circle(
                    surface,
                    (255, 0, 0),
                    (int(proj.position.x), int(proj.position.y)),
                    8,
                )
                pygame.draw.circle(
                    surface,
                    (255, 100, 100),
                    (int(proj.position.x) - 2, int(proj.position.y) - 2),
                    3,
                )

    def _render_player_kart(self, surface) -> None:
        """Render the player's kart."""
        x, y = int(self.player_x), int(self.player_y)
        angle = self.player_angle
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Purple kart for player
        PURPLE = (150, 50, 200)
        PURPLE_LIGHT = (200, 100, 255)

        # Kart body
        points = [
            (x + cos_a * 18 - sin_a * 10, y + sin_a * 18 + cos_a * 10),
            (x + cos_a * 18 + sin_a * 10, y + sin_a * 18 - cos_a * 10),
            (x - cos_a * 12 + sin_a * 10, y - sin_a * 12 - cos_a * 10),
            (x - cos_a * 12 - sin_a * 10, y - sin_a * 12 + cos_a * 10),
        ]
        pygame.draw.polygon(surface, PURPLE, points)

        # Cockpit
        pygame.draw.circle(surface, PURPLE_LIGHT, (x, y), 6)

        # Wheels
        wheel_color = (30, 30, 30)
        for wx, wy in [(12, 8), (12, -8), (-10, 8), (-10, -8)]:
            wheel_x = x + cos_a * wx - sin_a * wy
            wheel_y = y + sin_a * wx + cos_a * wy
            pygame.draw.circle(surface, wheel_color, (int(wheel_x), int(wheel_y)), 5)

    def _render_hud(self, surface) -> None:
        """Render race HUD."""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        # Position
        pos_text = f"Position: {self.player_position}/{len(self.racers) + 1}"
        pos_surface = font.render(pos_text, True, (255, 255, 255))
        surface.blit(pos_surface, (20, 20))

        # Lap
        lap_text = f"Lap: {self.player_lap + 1}/{self.TOTAL_LAPS}"
        lap_surface = font.render(lap_text, True, (255, 255, 255))
        surface.blit(lap_surface, (20, 55))

        # Time
        minutes = int(self.race_time // 60)
        seconds = int(self.race_time % 60)
        time_text = f"Time: {minutes}:{seconds:02d}"
        time_surface = small_font.render(time_text, True, (255, 255, 255))
        surface.blit(time_surface, (20, 90))

        # Instructions
        if self.race_started:
            inst_text = "Arrow Keys: Steer/Accelerate | SPACE: Fire Shell"
            inst_surface = small_font.render(inst_text, True, (200, 200, 200))
            surface.blit(
                inst_surface,
                (
                    self.screen_width // 2 - inst_surface.get_width() // 2,
                    self.screen_height - 30,
                ),
            )

    def _render_countdown(self, surface) -> None:
        """Render race countdown."""
        font = pygame.font.Font(None, 120)

        if self.race_countdown > 0:
            count = int(self.race_countdown) + 1
            if count > 3:
                count = 3
            text = str(count)
            color = (255, 255, 0)
        else:
            text = "GO!"
            color = (0, 255, 0)

        text_surface = font.render(text, True, color)
        x = self.screen_width // 2 - text_surface.get_width() // 2
        y = self.screen_height // 2 - text_surface.get_height() // 2
        surface.blit(text_surface, (x, y))


# Register the racing controller with the factory
GenreControllerFactory.register(GenreType.RACING, RacingController)
