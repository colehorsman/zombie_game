"""Level progression manager for multi-level gameplay."""

import csv
import logging
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Level:
    """Represents a single level (AWS account) in the game."""

    level_number: int  # 1-7
    account_id: str  # AWS account number
    account_name: str  # "MyHealth - Sandbox"
    environment_type: str  # "sandbox", "staging", "production", etc
    order: int  # Sort order (same as level_number for now)

    # Stats (populated during gameplay)
    zombies_eliminated: int = 0
    time_taken: float = 0.0
    score_earned: int = 0
    boss_defeated: bool = False
    is_completed: bool = False  # True when level has been beaten
    is_unlocked: bool = False  # True when level is available to play


class LevelManager:
    """
    Manages level progression through AWS accounts in SDLC order.

    Levels progress from Sandbox (most zombies, hardest) through to Org (final).
    Each level represents one AWS account that must be cleared before advancing.
    """

    def __init__(self, csv_path: str = "assets/aws_accounts.csv"):
        """
        Initialize the level manager.

        Args:
            csv_path: Path to CSV file with account data
        """
        self.csv_path = csv_path
        self.levels: List[Level] = []
        self.current_level_index = 0

        # Load levels from CSV
        self._load_levels_from_csv()

        logger.info(f"LevelManager initialized with {len(self.levels)} levels")
        logger.info(
            f"Level progression: {' → '.join([l.environment_type for l in self.levels])}"
        )

    def _load_levels_from_csv(self) -> None:
        """
        Load level data from CSV file.

        Expected CSV format:
            Account ID,Name,Environment Type,Order
            577945324761,MyHealth - Sandbox,sandbox,1
            ...
        """
        csv_file = Path(self.csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            levels_data = []

            for row in reader:
                try:
                    level = Level(
                        level_number=int(row["Order"]),
                        account_id=row["Account ID"].strip(),
                        account_name=row["Name"].strip(),
                        environment_type=row["Environment Type"].strip(),
                        order=int(row["Order"]),
                    )
                    levels_data.append(level)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid CSV row: {row}. Error: {e}")
                    continue

            # Sort by order to ensure correct progression
            self.levels = sorted(levels_data, key=lambda x: x.order)

            if not self.levels:
                raise ValueError("No valid levels loaded from CSV")

            # First level is always unlocked
            if self.levels:
                self.levels[0].is_unlocked = True

            logger.info(f"Loaded {len(self.levels)} levels from {self.csv_path}")

    def get_current_level(self) -> Level:
        """
        Get the current level.

        Returns:
            Current Level object
        """
        return self.levels[self.current_level_index]

    def get_level_by_number(self, level_number: int) -> Optional[Level]:
        """
        Get a level by its number.

        Args:
            level_number: Level number (1-7)

        Returns:
            Level object or None if not found
        """
        for level in self.levels:
            if level.level_number == level_number:
                return level
        return None

    def advance_to_next_level(self) -> bool:
        """
        Advance to the next level.

        Returns:
            True if advanced to next level, False if already at final level
        """
        if self.current_level_index < len(self.levels) - 1:
            # Mark current level as completed
            self.levels[self.current_level_index].is_completed = True

            # Advance to next level
            self.current_level_index += 1
            logger.info(
                f"Advanced to level {self.current_level_index + 1}: {self.get_current_level().environment_type}"
            )
            return True
        else:
            logger.info("Already at final level")
            return False

    def is_final_level(self) -> bool:
        """
        Check if currently on the final level.

        Returns:
            True if on final level (Org)
        """
        return self.current_level_index == len(self.levels) - 1

    def get_progress(self) -> tuple[int, int]:
        """
        Get current progress.

        Returns:
            Tuple of (current_level, total_levels)
        """
        return (self.current_level_index + 1, len(self.levels))

    def get_total_stats(self) -> dict:
        """
        Get cumulative stats across all completed levels.

        Returns:
            Dictionary with total stats
        """
        total_zombies = sum(level.zombies_eliminated for level in self.levels)
        total_time = sum(level.time_taken for level in self.levels)
        total_score = sum(level.score_earned for level in self.levels)
        bosses_defeated = sum(1 for level in self.levels if level.boss_defeated)
        levels_completed = sum(1 for level in self.levels if level.is_completed)

        return {
            "total_zombies_eliminated": total_zombies,
            "total_time": total_time,
            "total_score": total_score,
            "bosses_defeated": bosses_defeated,
            "levels_completed": levels_completed,
        }

    def complete_current_level(
        self, zombies: int, time: float, score: int, boss_defeated: bool = False
    ) -> None:
        """
        Mark current level as complete and record stats.

        Args:
            zombies: Number of zombies eliminated
            time: Time taken in seconds
            score: Score earned
            boss_defeated: Whether boss was defeated
        """
        current = self.get_current_level()
        current.zombies_eliminated = zombies
        current.time_taken = time
        current.score_earned = score
        current.boss_defeated = boss_defeated
        current.is_completed = True

        logger.info(
            f"Level {current.level_number} ({current.environment_type}) completed!"
        )
        logger.info(
            f"  Zombies: {zombies}, Time: {time:.1f}s, Score: {score}, Boss: {boss_defeated}"
        )

    def reset_progress(self) -> None:
        """Reset all progress back to level 1."""
        self.current_level_index = 0
        for level in self.levels:
            level.zombies_eliminated = 0
            level.time_taken = 0.0
            level.score_earned = 0
            level.boss_defeated = False
            level.is_completed = False
        logger.info("Progress reset to level 1")

    def get_level_description(self, level: Optional[Level] = None) -> str:
        """
        Get a formatted description of a level.

        Args:
            level: Level to describe (uses current level if None)

        Returns:
            Formatted string describing the level
        """
        if level is None:
            level = self.get_current_level()

        return (
            f"Level {level.level_number}: {level.environment_type.upper()}\n"
            f"Account: {level.account_name} ({level.account_id})"
        )
