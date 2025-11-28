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
        
        # Clamp timer to 0
        if self.time_remaining < 0:
            self.time_remaining = 0.0
        
        # Check for session end
        if self.time_remaining <= 0:
            self._end_session()

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
