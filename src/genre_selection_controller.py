"""Genre Selection Menu Controller for multi-genre level system.

Allows players to choose which genre/gameplay style to use for a level.
"""

import logging
from enum import Enum, auto
from typing import List, Optional

from models import CONTROL_SCHEMES, GenreType

logger = logging.getLogger(__name__)


class GenreSelectionAction(Enum):
    """Actions from genre selection menu."""

    NONE = auto()
    SELECT = auto()
    CANCEL = auto()


class GenreSelectionController:
    """Manages genre selection menu for level entry.

    Shows available genres with descriptions and control schemes.
    """

    # Genre display info
    GENRE_INFO = {
        GenreType.PLATFORMER: {
            "name": "🎮 PLATFORMER",
            "desc": "Classic side-scrolling action!\nJump between platforms, shoot zombies.",
            "unlock": "Default",
        },
        GenreType.SPACE_SHOOTER: {
            "name": "🚀 SPACE SHOOTER",
            "desc": "Galaga-style shooting!\nZombies descend from above.",
            "unlock": "Complete 1 level",
        },
        GenreType.MAZE_CHASE: {
            "name": "👻 MAZE CHASE",
            "desc": "Pac-Man style chomping!\nNavigate maze, eat zombies.",
            "unlock": "Eliminate 50 zombies",
        },
        GenreType.FIGHTING: {
            "name": "🥊 BOSS BATTLE",
            "desc": "Mortal Kombat style!\nFight the level boss 1v1.",
            "unlock": "Complete 3 levels",
        },
    }

    def __init__(self, unlocked_genres: Optional[List[GenreType]] = None):
        """Initialize genre selection controller.

        Args:
            unlocked_genres: List of unlocked genres (default: just platformer)
        """
        self._active = False
        self._selected_index = 0
        self._level_name: Optional[str] = None
        self._is_story_mode = False

        # Default to platformer only if not specified
        self._unlocked_genres = unlocked_genres or [GenreType.PLATFORMER]
        self._all_genres = list(GenreType)

        logger.info(
            f"GenreSelectionController initialized with {len(self._unlocked_genres)} unlocked genres"
        )

    @property
    def active(self) -> bool:
        return self._active

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @property
    def selected_genre(self) -> GenreType:
        """Get currently selected genre."""
        if self._selected_index < len(self._all_genres):
            return self._all_genres[self._selected_index]
        return GenreType.PLATFORMER

    def set_unlocked_genres(self, genres: List[GenreType]) -> None:
        """Update list of unlocked genres."""
        self._unlocked_genres = genres
        logger.info(f"Updated unlocked genres: {[g.value for g in genres]}")

    def show(self, level_name: str, is_story_mode: bool = False) -> str:
        """Show genre selection menu.

        Args:
            level_name: Name of level being entered
            is_story_mode: Whether story mode was selected

        Returns:
            Menu message string
        """
        self._active = True
        self._selected_index = 0
        self._level_name = level_name
        self._is_story_mode = is_story_mode
        logger.info(f"🎮 Genre selection menu shown for: {level_name}")
        return self.build_message()

    def hide(self) -> None:
        """Hide genre selection menu."""
        self._active = False
        self._level_name = None
        logger.debug("Genre selection menu hidden")

    def navigate(self, direction: int) -> str:
        """Navigate menu selection.

        Args:
            direction: -1 for up, 1 for down

        Returns:
            Updated menu message
        """
        if not self._active:
            return ""

        self._selected_index = (self._selected_index + direction) % len(
            self._all_genres
        )
        return self.build_message()

    def select(self) -> GenreSelectionAction:
        """Select current genre.

        Returns:
            SELECT if genre is unlocked, NONE if locked
        """
        if not self._active:
            return GenreSelectionAction.NONE

        genre = self.selected_genre
        if genre in self._unlocked_genres:
            logger.info(f"🎮 Genre selected: {genre.value}")
            return GenreSelectionAction.SELECT
        else:
            logger.info(f"🔒 Genre locked: {genre.value}")
            return GenreSelectionAction.NONE

    def cancel(self) -> GenreSelectionAction:
        """Cancel genre selection."""
        logger.info("❌ Genre selection cancelled")
        self.hide()
        return GenreSelectionAction.CANCEL

    def build_message(self) -> str:
        """Build genre selection menu message."""
        mode_str = "STORY MODE" if self._is_story_mode else "ARCADE MODE"
        header = f"🎮 SELECT GENRE - {mode_str}\n"
        header += f"Level: {self._level_name}\n\n"

        lines = []
        for i, genre in enumerate(self._all_genres):
            info = self.GENRE_INFO.get(
                genre, {"name": genre.value, "desc": "", "unlock": ""}
            )
            is_unlocked = genre in self._unlocked_genres
            is_selected = i == self._selected_index

            # Selection indicator
            prefix = "▶ " if is_selected else "  "

            # Lock indicator
            lock = "" if is_unlocked else " 🔒"

            lines.append(f"{prefix}{info['name']}{lock}")

        # Show description for selected genre
        selected_info = self.GENRE_INFO.get(self.selected_genre, {})
        desc = selected_info.get("desc", "")

        # Show unlock requirement if locked
        is_locked = self.selected_genre not in self._unlocked_genres
        unlock_text = ""
        if is_locked:
            unlock_text = f"\n\n🔒 Unlock: {selected_info.get('unlock', 'Unknown')}"

        # Control scheme
        scheme = CONTROL_SCHEMES.get(self.selected_genre)
        controls = f"\nControls: {scheme.description}" if scheme else ""

        footer = "\n\n─────────────────────────────\n"
        footer += "A/ENTER: Select | B/ESC: Back"

        return (
            f"{header}"
            + "\n".join(lines)
            + f"\n\n{desc}{unlock_text}{controls}{footer}"
        )
