"""Progress tracking across all genres.

Tracks zombies eliminated, levels completed, and per-genre statistics.

**Feature: multi-genre-levels**
**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

from models import GenreType

logger = logging.getLogger(__name__)


@dataclass
class GenreStats:
    """Statistics for a specific genre."""

    zombies_eliminated: int = 0
    levels_completed: int = 0
    time_played: float = 0.0
    boss_battles_won: int = 0


@dataclass
class ProgressTracker:
    """Tracks player progress across all genres.

    **Property 10: Cross-Genre Progress Aggregation**
    Elimination in any genre increases total count.
    Account completion is genre-independent.
    **Validates: Requirements 9.1, 9.2, 9.3**
    """

    # Global stats
    total_zombies_eliminated: int = 0
    total_levels_completed: int = 0
    total_boss_battles_won: int = 0

    # Per-genre stats
    genre_stats: Dict[GenreType, GenreStats] = field(default_factory=dict)

    # Account completion tracking
    completed_accounts: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize genre stats for all genres."""
        for genre in GenreType:
            if genre not in self.genre_stats:
                self.genre_stats[genre] = GenreStats()

    def record_elimination(self, genre: GenreType, count: int = 1) -> None:
        """Record zombie elimination.

        Args:
            genre: Genre where elimination occurred
            count: Number of zombies eliminated
        """
        self.total_zombies_eliminated += count
        self.genre_stats[genre].zombies_eliminated += count
        logger.debug(f"Recorded {count} elimination(s) in {genre.value}")

    def record_level_completion(self, genre: GenreType, account_id: str) -> None:
        """Record level completion.

        Args:
            genre: Genre where level was completed
            account_id: Account ID of completed level
        """
        self.total_levels_completed += 1
        self.genre_stats[genre].levels_completed += 1
        self.completed_accounts[account_id] = True
        logger.info(f"Level {account_id} completed in {genre.value}")

    def record_boss_victory(self, genre: GenreType) -> None:
        """Record boss battle victory.

        Args:
            genre: Genre where boss was defeated
        """
        self.total_boss_battles_won += 1
        self.genre_stats[genre].boss_battles_won += 1
        logger.info(f"Boss defeated in {genre.value}")

    def record_time_played(self, genre: GenreType, seconds: float) -> None:
        """Record time played in a genre.

        Args:
            genre: Genre played
            seconds: Time played in seconds
        """
        self.genre_stats[genre].time_played += seconds

    def is_account_completed(self, account_id: str) -> bool:
        """Check if an account has been completed.

        Args:
            account_id: Account ID to check

        Returns:
            True if account is completed in any genre
        """
        return self.completed_accounts.get(account_id, False)

    def get_genre_stats(self, genre: GenreType) -> GenreStats:
        """Get statistics for a specific genre.

        Args:
            genre: Genre to get stats for

        Returns:
            GenreStats for the genre
        """
        return self.genre_stats.get(genre, GenreStats())

    def to_dict(self) -> dict:
        """Serialize progress to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "total_zombies_eliminated": self.total_zombies_eliminated,
            "total_levels_completed": self.total_levels_completed,
            "total_boss_battles_won": self.total_boss_battles_won,
            "genre_stats": {
                genre.value: {
                    "zombies_eliminated": stats.zombies_eliminated,
                    "levels_completed": stats.levels_completed,
                    "time_played": stats.time_played,
                    "boss_battles_won": stats.boss_battles_won,
                }
                for genre, stats in self.genre_stats.items()
            },
            "completed_accounts": self.completed_accounts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgressTracker":
        """Deserialize progress from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ProgressTracker instance
        """
        tracker = cls(
            total_zombies_eliminated=data.get("total_zombies_eliminated", 0),
            total_levels_completed=data.get("total_levels_completed", 0),
            total_boss_battles_won=data.get("total_boss_battles_won", 0),
        )

        # Restore genre stats
        genre_stats_data = data.get("genre_stats", {})
        for genre_value, stats_data in genre_stats_data.items():
            try:
                genre = GenreType(genre_value)
                tracker.genre_stats[genre] = GenreStats(
                    zombies_eliminated=stats_data.get("zombies_eliminated", 0),
                    levels_completed=stats_data.get("levels_completed", 0),
                    time_played=stats_data.get("time_played", 0.0),
                    boss_battles_won=stats_data.get("boss_battles_won", 0),
                )
            except ValueError:
                pass  # Unknown genre, skip

        # Restore completed accounts
        tracker.completed_accounts = data.get("completed_accounts", {})

        return tracker
