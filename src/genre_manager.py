"""Genre Manager for multi-genre level system.

Manages genre selection, unlocks, and preferences for AWS account levels.
"""

import logging
from typing import Dict, List, Optional, Set

from models import GENRE_UNLOCK_CONDITIONS, GenreType, UnlockCondition

logger = logging.getLogger(__name__)


class GenreManager:
    """Manages genre selection, unlocks, and preferences.

    Handles:
    - Tracking which genres are unlocked
    - Storing per-account genre preferences
    - Checking unlock conditions based on progress
    """

    def __init__(self, save_manager=None):
        """Initialize the genre manager.

        Args:
            save_manager: Optional SaveManager for persistence
        """
        self.save_manager = save_manager
        self.unlocked_genres: Set[GenreType] = {GenreType.PLATFORMER}
        self.account_preferences: Dict[str, GenreType] = {}

        # Load saved data if available
        if save_manager:
            self._load_from_save()

    def _load_from_save(self) -> None:
        """Load genre data from save file."""
        if not self.save_manager:
            return

        try:
            save_data = self.save_manager.load()
            if save_data and "genre_data" in save_data:
                genre_data = save_data["genre_data"]

                # Load unlocked genres
                unlocked = genre_data.get("unlocked_genres", ["platformer"])
                self.unlocked_genres = {
                    GenreType(g)
                    for g in unlocked
                    if g in [gt.value for gt in GenreType]
                }
                # Always ensure platformer is unlocked
                self.unlocked_genres.add(GenreType.PLATFORMER)

                # Load account preferences
                prefs = genre_data.get("account_preferences", {})
                self.account_preferences = {
                    acc: GenreType(g)
                    for acc, g in prefs.items()
                    if g in [gt.value for gt in GenreType]
                }

                logger.info(
                    f"Loaded genre data: {len(self.unlocked_genres)} unlocked, "
                    f"{len(self.account_preferences)} preferences"
                )
        except Exception as e:
            logger.error(f"Failed to load genre data: {e}")

    def save(self) -> None:
        """Save genre data to save file."""
        if not self.save_manager:
            return

        try:
            save_data = self.save_manager.load() or {}
            save_data["genre_data"] = {
                "unlocked_genres": [g.value for g in self.unlocked_genres],
                "account_preferences": {
                    acc: g.value for acc, g in self.account_preferences.items()
                },
            }
            self.save_manager.save(save_data)
            logger.info("Saved genre data")
        except Exception as e:
            logger.error(f"Failed to save genre data: {e}")

    def get_available_genres(self) -> List[GenreType]:
        """Return list of unlocked genres.

        Returns:
            List of GenreType values that are unlocked
        """
        return list(self.unlocked_genres)

    def is_genre_unlocked(self, genre: GenreType) -> bool:
        """Check if a genre is unlocked.

        Args:
            genre: The genre to check

        Returns:
            True if unlocked, False otherwise
        """
        return genre in self.unlocked_genres

    def select_genre(self, account_id: str, genre: GenreType) -> bool:
        """Set genre preference for an account.

        Args:
            account_id: AWS account ID
            genre: Genre to use for this account

        Returns:
            True if selection was successful, False if genre is locked
        """
        if genre not in self.unlocked_genres:
            logger.warning(
                f"Cannot select locked genre {genre.value} for account {account_id}"
            )
            return False

        self.account_preferences[account_id] = genre
        logger.info(f"Selected genre {genre.value} for account {account_id}")
        self.save()
        return True

    def get_genre_for_account(self, account_id: str) -> GenreType:
        """Get saved genre preference or default.

        Args:
            account_id: AWS account ID

        Returns:
            The preferred genre for this account, or PLATFORMER as default
        """
        return self.account_preferences.get(account_id, GenreType.PLATFORMER)

    def check_unlock_conditions(
        self, levels_completed: int, zombies_eliminated: int
    ) -> List[GenreType]:
        """Check if any new genres should be unlocked.

        Args:
            levels_completed: Total levels completed
            zombies_eliminated: Total zombies eliminated

        Returns:
            List of newly unlocked genres (empty if none)
        """
        newly_unlocked = []

        for genre, condition in GENRE_UNLOCK_CONDITIONS.items():
            if genre in self.unlocked_genres:
                continue  # Already unlocked

            should_unlock = False
            if condition.type == "default":
                should_unlock = True
            elif condition.type == "levels_completed":
                should_unlock = levels_completed >= condition.value
            elif condition.type == "zombies_eliminated":
                should_unlock = zombies_eliminated >= condition.value

            if should_unlock:
                newly_unlocked.append(genre)

        return newly_unlocked

    def unlock_genre(self, genre: GenreType) -> None:
        """Unlock a genre.

        Args:
            genre: The genre to unlock
        """
        if genre not in self.unlocked_genres:
            self.unlocked_genres.add(genre)
            logger.info(f"🎮 Unlocked genre: {genre.value}")
            self.save()

    def unlock_all(self) -> None:
        """Unlock all genres (cheat/debug)."""
        for genre in GenreType:
            self.unlocked_genres.add(genre)
        logger.info("🎮 Unlocked all genres!")
        self.save()

    def to_dict(self) -> dict:
        """Serialize for save file.

        Returns:
            Dictionary representation of genre data
        """
        return {
            "unlocked_genres": [g.value for g in self.unlocked_genres],
            "account_preferences": {
                acc: g.value for acc, g in self.account_preferences.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict, save_manager=None) -> "GenreManager":
        """Deserialize from save file.

        Args:
            data: Dictionary with genre data
            save_manager: Optional SaveManager for persistence

        Returns:
            GenreManager instance
        """
        manager = cls(save_manager=None)  # Don't load from save again

        if data:
            unlocked = data.get("unlocked_genres", ["platformer"])
            manager.unlocked_genres = {
                GenreType(g) for g in unlocked if g in [gt.value for gt in GenreType]
            }
            manager.unlocked_genres.add(GenreType.PLATFORMER)

            prefs = data.get("account_preferences", {})
            manager.account_preferences = {
                acc: GenreType(g)
                for acc, g in prefs.items()
                if g in [gt.value for gt in GenreType]
            }

        manager.save_manager = save_manager
        return manager
