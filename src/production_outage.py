"""Production Outage system - random events that freeze the player while they "fix prod"."""

import logging
import random
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# Fun error messages to display during outages
ERROR_MESSAGES = [
    "ERROR: NullPointerException at line 42069",
    "CRITICAL: Database connection timeout",
    "ALERT: Memory usage at 99.7%",
    "WARNING: Certificate expires in -3 days",
    "ERROR: Cannot read property 'undefined' of undefined",
    "FATAL: Segmentation fault (core dumped)",
    "PANIC: Kernel panic - not syncing",
    "ERROR: It works on my machine",
    "CRITICAL: Have you tried turning it off and on again?",
    "ALERT: The cloud is on fire",
    "ERROR: 404 - Production not found",
    "WARNING: This is fine. Everything is fine.",
    "CRITICAL: Someone pushed to main without testing",
    "ERROR: AWS us-east-1 is having issues (again)",
    "ALERT: PagerDuty escalation in progress",
    "FATAL: rm -rf / was a bad idea",
    "ERROR: JSON parsing failed at position NaN",
    "CRITICAL: Kubernetes pod in CrashLoopBackOff",
    "WARNING: SSL handshake failed (expired cert)",
    "ALERT: DynamoDB throttling detected",
]


@dataclass
class OutageState:
    """State for a production outage event."""

    active: bool = False
    time_remaining: float = 0.0
    total_duration: float = 5.0
    error_message: str = ""
    flash_timer: float = 0.0  # For flashing red border effect


class ProductionOutageManager:
    """Manages random production outage events during gameplay."""

    def __init__(
        self,
        trigger_chance_per_second: float = 0.005,  # 0.5% chance per second
        cooldown_seconds: float = 30.0,  # Minimum time between outages
        outage_duration: float = 5.0,  # How long outage lasts
    ):
        """
        Initialize the outage manager.

        Args:
            trigger_chance_per_second: Probability per second of outage (default 0.5%)
            cooldown_seconds: Minimum time between outages
            outage_duration: How long each outage lasts
        """
        self.trigger_chance_per_second = trigger_chance_per_second
        self.cooldown_seconds = cooldown_seconds
        self.outage_duration = outage_duration

        # State tracking
        self._active = False
        self._time_remaining = 0.0
        self._error_message = ""
        self._cooldown_remaining = 0.0
        self._flash_timer = 0.0
        self._enabled = True  # Can be disabled during boss battles, etc.

    def enable(self) -> None:
        """Enable outage triggers."""
        self._enabled = True
        logger.info("🚨 Production outage system enabled")

    def disable(self) -> None:
        """Disable outage triggers (but don't cancel active outage)."""
        self._enabled = False
        logger.info("🚨 Production outage system disabled")

    def is_active(self) -> bool:
        """Check if an outage is currently active."""
        return self._active

    def get_state(self) -> OutageState:
        """Get current outage state for rendering."""
        return OutageState(
            active=self._active,
            time_remaining=self._time_remaining,
            total_duration=self.outage_duration,
            error_message=self._error_message,
            flash_timer=self._flash_timer,
        )

    def get_progress(self) -> float:
        """Get progress of fixing the outage (0.0 to 1.0)."""
        if not self._active:
            return 0.0
        return 1.0 - (self._time_remaining / self.outage_duration)

    def should_trigger(self, delta_time: float) -> bool:
        """
        Check if an outage should trigger this frame.

        Args:
            delta_time: Time elapsed since last frame

        Returns:
            True if outage should trigger
        """
        # Don't trigger if disabled, already active, or in cooldown
        if not self._enabled or self._active or self._cooldown_remaining > 0:
            return False

        # Random chance based on time elapsed
        # Convert per-second chance to per-frame chance
        chance = self.trigger_chance_per_second * delta_time
        return random.random() < chance

    def trigger(self) -> None:
        """Manually trigger an outage (for testing or scripted events)."""
        if self._active:
            return  # Already in outage

        self._active = True
        self._time_remaining = self.outage_duration
        self._error_message = random.choice(ERROR_MESSAGES)
        self._flash_timer = 0.0

        logger.info(f"🚨 PRODUCTION OUTAGE! {self._error_message}")

    def update(self, delta_time: float) -> bool:
        """
        Update outage state.

        Args:
            delta_time: Time elapsed since last frame

        Returns:
            True if outage just ended this frame
        """
        # Update cooldown
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= delta_time

        # Check for random trigger
        if self.should_trigger(delta_time):
            self.trigger()

        # Update active outage
        if self._active:
            self._time_remaining -= delta_time
            self._flash_timer += delta_time

            # Check if outage ended
            if self._time_remaining <= 0:
                self._active = False
                self._time_remaining = 0.0
                self._cooldown_remaining = self.cooldown_seconds
                logger.info("✅ Production outage resolved! Back to work...")
                return True  # Outage just ended

        return False

    def reset(self) -> None:
        """Reset all outage state (for new game/level)."""
        self._active = False
        self._time_remaining = 0.0
        self._error_message = ""
        self._cooldown_remaining = 0.0
        self._flash_timer = 0.0
