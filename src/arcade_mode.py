"""Arcade Mode Manager - 60-second elimination challenge."""

import logging
from typing import List, Optional

from models import ArcadeModeState, ArcadeStats, Vector2
from combo_tracker import ComboTracker
from zombie import Zombie
from powerup import PowerUp, PowerUpType, spawn_random_powerups


logger = logging.getLogger(__name__)


class ArcadeModeManager:
    """Manages arcade mode sessions with 60-second timer and elimination queue."""

    def __init__(self):
        """Initialize the arcade mode manager."""
        self.active = False
        self.time_remaining = 60.0
        self.countdown_time = 3.0  # 3-second countdown before timer starts
        self.in_countdown = False
        
        # Elimination queue (no API calls during arcade mode)
        self.elimination_queue: List[Zombie] = []
        
        # Combo tracking
        self.combo_tracker = ComboTracker()
        
        # Statistics
        self.eliminations_count = 0
        self.powerups_collected = 0
        self.highest_combo = 0
        
        # Session start time (for calculating eliminations per second)
        self.session_duration = 0.0
        
        # Dynamic spawning
        self.respawn_queue: List[Zombie] = []  # Zombies waiting to respawn
        self.respawn_timers: dict = {}  # {zombie_id: time_remaining}
        self.respawn_delay = 2.0  # 2 seconds
        self.spawn_distance = 500  # Spawn 500 pixels from player
        self.min_zombie_count = 20  # Minimum zombies on screen

    def start_session(self) -> None:
        """Start a new arcade mode session with 3-second countdown."""
        logger.info("🎮 Starting arcade mode session")
        
        self.active = True
        self.in_countdown = True
        self.countdown_time = 3.0
        self.time_remaining = 60.0
        self.session_duration = 0.0
        
        # Reset statistics
        self.elimination_queue.clear()
        self.eliminations_count = 0
        self.powerups_collected = 0
        self.highest_combo = 0
        
        # Reset combo tracker
        self.combo_tracker.reset()
        
        # Reset spawning
        self.respawn_queue.clear()
        self.respawn_timers.clear()

    def update(self, delta_time: float) -> None:
        """
        Update arcade mode timers and state.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.active:
            return
        
        # Handle countdown phase
        if self.in_countdown:
            self.countdown_time -= delta_time
            if self.countdown_time <= 0:
                self.in_countdown = False
                self.countdown_time = 0.0
                logger.info("⏱️  Countdown complete - arcade mode timer started")
            return
        
        # Update main timer
        self.time_remaining -= delta_time
        self.session_duration += delta_time
        
        # Update combo tracker
        self.combo_tracker.update(delta_time)
        
        # Update respawn timers
        self._update_respawn_timers(delta_time)
        
        # Clamp timer to 0
        if self.time_remaining < 0:
            self.time_remaining = 0.0
        
        # Check for session end
        if self.time_remaining <= 0:
            self._end_session()

    def _update_respawn_timers(self, delta_time: float) -> None:
        """
        Update respawn timers for dynamic spawning.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        # TODO: Implement dynamic spawning logic
        # This is a placeholder to prevent AttributeError
        pass

    def _end_session(self) -> None:
        """End the arcade mode session."""
        if not self.active:
            return
        
        logger.info(f"🏁 Arcade mode session ended - {self.eliminations_count} eliminations")
        self.active = False
        self.in_countdown = False

    def queue_elimination(self, zombie: Zombie) -> None:
        """
        Queue a zombie elimination (no API call during arcade mode).
        
        Args:
            zombie: Zombie to queue for elimination
        """
        if not self.active:
            return
        
        # Prevent duplicates
        if zombie in self.elimination_queue:
            return
        
        self.elimination_queue.append(zombie)
        self.eliminations_count += 1
        
        # Update combo
        self.combo_tracker.add_elimination()
        
        # Track highest combo
        if self.combo_tracker.get_combo_count() > self.highest_combo:
            self.highest_combo = self.combo_tracker.get_combo_count()
        
        logger.debug(f"⚡ Queued elimination: {zombie.identity_name} (Total: {self.eliminations_count}, Combo: {self.combo_tracker.get_combo_count()}x)")

    def record_powerup_collection(self, powerup_type: PowerUpType) -> None:
        """
        Record a power-up collection.
        
        Args:
            powerup_type: Type of power-up collected
        """
        self.powerups_collected += 1
        logger.debug(f"💎 Power-up collected: {powerup_type.value} (Total: {self.powerups_collected})")

    def clear_elimination_queue(self) -> None:
        """Clear the elimination queue (when player opts out of quarantine)."""
        logger.info(f"🗑️  Clearing elimination queue ({len(self.elimination_queue)} zombies)")
        self.elimination_queue.clear()

    def get_elimination_queue(self) -> List[Zombie]:
        """Get a copy of the elimination queue."""
        return self.elimination_queue.copy()

    def get_stats(self) -> ArcadeStats:
        """
        Get arcade mode statistics.
        
        Returns:
            ArcadeStats object with session statistics
        """
        eliminations_per_second = 0.0
        if self.session_duration > 0:
            eliminations_per_second = self.eliminations_count / self.session_duration
        
        return ArcadeStats(
            total_eliminations=self.eliminations_count,
            eliminations_per_second=eliminations_per_second,
            highest_combo=self.highest_combo,
            powerups_collected=self.powerups_collected
        )

    def get_state(self) -> ArcadeModeState:
        """
        Get current arcade mode state.
        
        Returns:
            ArcadeModeState object with current state
        """
        return ArcadeModeState(
            active=self.active,
            in_countdown=self.in_countdown,
            countdown_time=self.countdown_time,
            time_remaining=self.time_remaining,
            session_duration=self.session_duration,
            eliminations_count=self.eliminations_count,
            combo_count=self.combo_tracker.get_combo_count(),
            combo_multiplier=self.combo_tracker.get_combo_multiplier(),
            highest_combo=self.highest_combo,
            powerups_collected=self.powerups_collected
        )

    def is_active(self) -> bool:
        """Check if arcade mode is active."""
        return self.active

    def is_in_countdown(self) -> bool:
        """Check if in countdown phase."""
        return self.in_countdown

    def get_time_remaining(self) -> float:
        """Get time remaining in seconds."""
        return self.time_remaining

    def get_countdown_time(self) -> float:
        """Get countdown time remaining."""
        return self.countdown_time

    def get_elimination_count(self) -> int:
        """Get total eliminations."""
        return self.eliminations_count

    def get_combo_count(self) -> int:
        """Get current combo count."""
        return self.combo_tracker.get_combo_count()

    def get_combo_multiplier(self) -> float:
        """Get current combo multiplier."""
        return self.combo_tracker.get_combo_multiplier()

    def cancel_session(self) -> None:
        """Cancel the current arcade mode session."""
        logger.info("❌ Arcade mode session cancelled")
        self.active = False
        self.in_countdown = False
        self.elimination_queue.clear()

    def spawn_arcade_powerups(self, level_width: int, ground_y: int, count: int = 5) -> List[PowerUp]:
        """
        Spawn arcade-specific power-ups at higher density.
        
        Args:
            level_width: Width of the level
            ground_y: Y position of the ground
            count: Number of power-ups to spawn
            
        Returns:
            List of spawned power-ups
        """
        powerups = spawn_random_powerups(
            level_width=level_width,
            ground_y=ground_y,
            count=count,
            arcade_mode=True  # Higher chance of arcade power-ups
        )
        logger.info(f"🎁 Spawned {len(powerups)} arcade power-ups")
        return powerups

    def calculate_initial_zombie_count(self, level_width: int) -> int:
        """
        Calculate initial zombie count based on level width.
        
        Density: 1 zombie per 100 pixels
        Minimum: 20 zombies
        
        Args:
            level_width: Width of the level in pixels
            
        Returns:
            Number of zombies to spawn
        """
        density_count = level_width // 100
        return max(self.min_zombie_count, density_count)

    def queue_zombie_for_respawn(self, zombie: Zombie) -> None:
        """
        Queue a zombie for respawn after 2-second delay.
        
        Args:
            zombie: Zombie to respawn
        """
        if not self.active or self.in_countdown:
            return
        
        # Add to respawn queue if not already there
        if zombie.identity_id not in self.respawn_timers:
            self.respawn_queue.append(zombie)
            self.respawn_timers[zombie.identity_id] = self.respawn_delay
            logger.debug(f"🔄 Queued zombie for respawn: {zombie.identity_name} (2s delay)")

    def _update_respawn_timers(self, delta_time: float) -> None:
        """
        Update respawn timers and trigger respawns.
        
        Args:
            delta_time: Time elapsed since last frame
        """
        # Update all timers
        expired_ids = []
        for zombie_id, time_remaining in self.respawn_timers.items():
            self.respawn_timers[zombie_id] = time_remaining - delta_time
            if self.respawn_timers[zombie_id] <= 0:
                expired_ids.append(zombie_id)
        
        # Remove expired timers
        for zombie_id in expired_ids:
            del self.respawn_timers[zombie_id]

    def get_zombies_ready_to_respawn(self) -> List[Zombie]:
        """
        Get zombies that are ready to respawn (timer expired).
        
        Returns:
            List of zombies ready to respawn
        """
        ready = []
        for zombie in self.respawn_queue[:]:  # Copy to avoid modification during iteration
            if zombie.identity_id not in self.respawn_timers:
                ready.append(zombie)
                self.respawn_queue.remove(zombie)
        
        return ready

    def respawn_zombie(self, zombie: Zombie, player_pos: Vector2, level_width: int, ground_y: int) -> None:
        """
        Respawn a zombie at a safe distance from the player.
        
        Spawns 500 pixels away from player (left or right).
        
        Args:
            zombie: Zombie to respawn
            player_pos: Player's current position
            level_width: Width of the level
            ground_y: Y position of the ground
        """
        import random
        
        # Choose spawn side (left or right of player)
        spawn_left = random.choice([True, False])
        
        if spawn_left:
            # Spawn to the left
            spawn_x = player_pos.x - self.spawn_distance
            # Clamp to level bounds
            spawn_x = max(50, spawn_x)
        else:
            # Spawn to the right
            spawn_x = player_pos.x + self.spawn_distance
            # Clamp to level bounds
            spawn_x = min(level_width - 50, spawn_x)
        
        # Reset zombie state
        zombie.position = Vector2(spawn_x, ground_y - zombie.height)
        zombie.health = zombie.max_health
        zombie.is_flashing = False
        zombie.flash_timer = 0.0
        zombie.velocity = Vector2(0, 0)
        zombie.on_ground = True
        zombie.is_hidden = False
        
        logger.debug(f"♻️  Respawned zombie: {zombie.identity_name} at ({spawn_x}, {ground_y})")

    def should_respawn_zombies(self, current_zombie_count: int) -> bool:
        """
        Check if zombies should be respawned to maintain minimum count.
        
        Args:
            current_zombie_count: Current number of active zombies
            
        Returns:
            True if zombies should be respawned
        """
        return current_zombie_count < self.min_zombie_count
