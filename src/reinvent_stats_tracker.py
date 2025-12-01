"""
re:Invent 2025 Stats Tracker for Sonrai Zombie Blaster.

Tracks cumulative arcade mode statistics during AWS re:Invent (Dec 1-4, 2025).
Logs to a JSON file for easy aggregation and social media posts.

Stats tracked:
- Total zombies quarantined across all arcade sessions
- Highest single-session score
- Total arcade sessions played
- Session history with timestamps
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# re:Invent 2025 date range (Dec 1-4, ending at midnight Dec 5)
REINVENT_START = datetime(2025, 12, 1, 0, 0, 0)
REINVENT_END = datetime(2025, 12, 5, 0, 0, 0)

# Stats file location
STATS_FILE = Path("reinvent_2025_stats.json")


@dataclass
class ArcadeSession:
    """Record of a single arcade mode session."""

    timestamp: str
    zombies_eliminated: int
    highest_combo: int
    duration_seconds: float
    player_name: str = "Anonymous"


@dataclass
class ReinventStats:
    """Cumulative stats for re:Invent 2025."""

    total_zombies_quarantined: int = 0
    highest_single_session_score: int = 0
    highest_combo_ever: int = 0
    total_sessions: int = 0
    sessions: List[dict] = field(default_factory=list)

    # Metadata
    tracking_start: str = ""
    last_updated: str = ""


class ReinventStatsTracker:
    """
    Tracks and persists arcade mode statistics for re:Invent 2025.

    Only records stats during the re:Invent date range (Dec 1-4, 2025).
    Can be enabled/disabled via environment variable.
    """

    def __init__(self, stats_file: Path = STATS_FILE, force_enabled: bool = False):
        """
        Initialize the stats tracker.

        Args:
            stats_file: Path to the JSON stats file
            force_enabled: If True, track stats regardless of date (for testing)
        """
        self._stats_file = stats_file
        self._force_enabled = force_enabled
        self._stats: Optional[ReinventStats] = None

        # Check if tracking is enabled via env var
        self._env_enabled = os.getenv("REINVENT_STATS_ENABLED", "true").lower() == "true"

        # Load existing stats if available
        self._load_stats()

        logger.info(f"📊 re:Invent stats tracker initialized (enabled={self.is_enabled})")

    @property
    def is_enabled(self) -> bool:
        """Check if stats tracking is currently enabled."""
        if not self._env_enabled:
            return False
        if self._force_enabled:
            return True

        # Check if we're within re:Invent date range
        now = datetime.now()
        return REINVENT_START <= now < REINVENT_END

    @property
    def is_reinvent_period(self) -> bool:
        """Check if we're currently in the re:Invent period."""
        now = datetime.now()
        return REINVENT_START <= now < REINVENT_END

    def _load_stats(self) -> None:
        """Load stats from file if it exists."""
        if self._stats_file.exists():
            try:
                with open(self._stats_file, "r") as f:
                    data = json.load(f)
                    self._stats = ReinventStats(
                        total_zombies_quarantined=data.get("total_zombies_quarantined", 0),
                        highest_single_session_score=data.get("highest_single_session_score", 0),
                        highest_combo_ever=data.get("highest_combo_ever", 0),
                        total_sessions=data.get("total_sessions", 0),
                        sessions=data.get("sessions", []),
                        tracking_start=data.get("tracking_start", ""),
                        last_updated=data.get("last_updated", ""),
                    )
                    logger.info(
                        f"📊 Loaded existing stats: {self._stats.total_sessions} sessions, {self._stats.total_zombies_quarantined} total zombies"
                    )
            except Exception as e:
                logger.error(f"📊 Failed to load stats file: {e}")
                self._stats = ReinventStats()
        else:
            self._stats = ReinventStats()

    def _save_stats(self) -> None:
        """Save stats to file."""
        if self._stats is None:
            return

        try:
            self._stats.last_updated = datetime.now().isoformat()
            if not self._stats.tracking_start:
                self._stats.tracking_start = datetime.now().isoformat()

            with open(self._stats_file, "w") as f:
                json.dump(asdict(self._stats), f, indent=2)

            logger.info(f"📊 Stats saved to {self._stats_file}")
        except Exception as e:
            logger.error(f"📊 Failed to save stats: {e}")

    def record_arcade_session(
        self,
        zombies_eliminated: int,
        highest_combo: int,
        duration_seconds: float,
        player_name: str = "Anonymous",
    ) -> bool:
        """
        Record an arcade mode session.

        Args:
            zombies_eliminated: Number of zombies eliminated in this session
            highest_combo: Highest combo achieved in this session
            duration_seconds: Duration of the session in seconds
            player_name: Optional player name/identifier

        Returns:
            True if this session achieved a new high score, False otherwise
        """
        if not self.is_enabled:
            logger.debug("📊 Stats tracking disabled, skipping record")
            return False

        if self._stats is None:
            self._stats = ReinventStats()

        # Track if this is a new high score
        is_new_high_score = False

        # Create session record
        session = ArcadeSession(
            timestamp=datetime.now().isoformat(),
            zombies_eliminated=zombies_eliminated,
            highest_combo=highest_combo,
            duration_seconds=duration_seconds,
            player_name=player_name,
        )

        # Update cumulative stats
        self._stats.total_zombies_quarantined += zombies_eliminated
        self._stats.total_sessions += 1

        if zombies_eliminated > self._stats.highest_single_session_score:
            self._stats.highest_single_session_score = zombies_eliminated
            is_new_high_score = True
            logger.info(f"📊 🏆 NEW HIGH SCORE: {zombies_eliminated} zombies!")

        if highest_combo > self._stats.highest_combo_ever:
            self._stats.highest_combo_ever = highest_combo
            logger.info(f"📊 🔥 NEW COMBO RECORD: {highest_combo}x!")

        # Add session to history
        self._stats.sessions.append(asdict(session))

        # Save to file
        self._save_stats()

        logger.info(
            f"📊 Session recorded: {zombies_eliminated} zombies, {highest_combo}x combo | "
            f"Totals: {self._stats.total_zombies_quarantined} zombies, {self._stats.total_sessions} sessions"
        )

        return is_new_high_score

    def get_stats_summary(self) -> dict:
        """
        Get a summary of current stats for display.

        Returns:
            Dictionary with key stats
        """
        if self._stats is None:
            return {
                "total_zombies": 0,
                "high_score": 0,
                "highest_combo": 0,
                "total_sessions": 0,
            }

        return {
            "total_zombies": self._stats.total_zombies_quarantined,
            "high_score": self._stats.highest_single_session_score,
            "highest_combo": self._stats.highest_combo_ever,
            "total_sessions": self._stats.total_sessions,
        }

    def get_social_post(self) -> str:
        """
        Generate a social media post with the stats.

        Returns:
            Formatted string for LinkedIn/Twitter
        """
        stats = self.get_stats_summary()

        return (
            f"🎮🧟 At AWS re:Invent 2025, we quarantined {stats['total_zombies']:,} "
            f"unused cloud identities with Sonrai Zombie Blaster!\n\n"
            f"🏆 High Score: {stats['high_score']} zombies in 60 seconds\n"
            f"🔥 Best Combo: {stats['highest_combo']}x\n"
            f"👥 Total Sessions: {stats['total_sessions']}\n\n"
            f"Every zombie = a real unused IAM identity quarantined via "
            f"@SonraiSecurity Cloud Permissions Firewall! 🛡️\n\n"
            f"#AWSreInvent #CloudSecurity #Sonrai #ZombieBlaster"
        )

    def print_summary(self) -> None:
        """Print a formatted summary to console."""
        stats = self.get_stats_summary()

        print("\n" + "=" * 50)
        print("📊 SONRAI ZOMBIE BLASTER - re:Invent 2025 STATS")
        print("=" * 50)
        print(f"🧟 Total Zombies Quarantined: {stats['total_zombies']:,}")
        print(f"🏆 Highest Single Score:      {stats['high_score']}")
        print(f"🔥 Highest Combo Ever:        {stats['highest_combo']}x")
        print(f"👥 Total Arcade Sessions:     {stats['total_sessions']}")
        print("=" * 50)
        print("\n📱 SOCIAL POST:\n")
        print(self.get_social_post())
        print("\n")


# Global instance for easy access
_tracker: Optional[ReinventStatsTracker] = None


def get_tracker() -> ReinventStatsTracker:
    """Get the global stats tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ReinventStatsTracker()
    return _tracker


def record_arcade_session(
    zombies_eliminated: int,
    highest_combo: int,
    duration_seconds: float,
    player_name: str = "Anonymous",
) -> bool:
    """Convenience function to record an arcade session.

    Returns:
        True if this session achieved a new high score, False otherwise
    """
    return get_tracker().record_arcade_session(
        zombies_eliminated=zombies_eliminated,
        highest_combo=highest_combo,
        duration_seconds=duration_seconds,
        player_name=player_name,
    )


if __name__ == "__main__":
    # Test/demo the tracker
    tracker = ReinventStatsTracker(force_enabled=True)

    # Simulate some sessions
    tracker.record_arcade_session(45, 8, 60.0, "Player1")
    tracker.record_arcade_session(62, 12, 60.0, "Player2")
    tracker.record_arcade_session(38, 5, 60.0, "Player3")
    tracker.record_arcade_session(71, 15, 60.0, "Player4")  # New high score!

    # Print summary
    tracker.print_summary()
