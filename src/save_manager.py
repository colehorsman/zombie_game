"""Save game state management for Sonrai Zombie Blaster."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Set

from models import Vector2, GameStatus

logger = logging.getLogger(__name__)


class SaveManager:
    """Manages game state persistence to disk."""

    def __init__(self, save_file_path: str = ".zombie_save.json"):
        """
        Initialize the save manager.

        Args:
            save_file_path: Path to save file (relative to project root)
        """
        self.save_file = Path(save_file_path)
        self.version = "2.0"

    def save_game(
        self,
        player_score: int,
        player_eliminations: int,
        damage_multiplier: float,
        player_position: Vector2,
        game_status: GameStatus,
        current_level: Optional[str],
        play_time: float,
        completed_levels: List[str],
        unlocked_levels: List[str],
        quarantined_identities: Set[str],
        blocked_third_parties: Set[str],
    ) -> bool:
        """
        Save current game state to disk.

        Args:
            player_score: Player's current score
            player_eliminations: Number of zombies eliminated
            damage_multiplier: Current damage multiplier
            player_position: Player's position (Vector2)
            game_status: Current game status (LOBBY, PLAYING, etc.)
            current_level: Current level account number (None if in lobby)
            play_time: Total play time in seconds
            completed_levels: List of completed level account numbers
            unlocked_levels: List of unlocked level account numbers
            quarantined_identities: Set of quarantined identity IDs
            blocked_third_parties: Set of blocked third-party names

        Returns:
            True if save successful, False otherwise
        """
        try:
            save_data = {
                "version": self.version,
                "last_saved": datetime.now().isoformat(),
                "player": {
                    "score": player_score,
                    "eliminations": player_eliminations,
                    "damage_multiplier": damage_multiplier,
                    "position": {"x": player_position.x, "y": player_position.y},
                },
                "game_state": {
                    "status": game_status.name,
                    "current_level": current_level,
                    "play_time": play_time,
                },
                "progress": {
                    "completed_levels": completed_levels,
                    "unlocked_levels": unlocked_levels,
                },
                "quarantined_identities": list(quarantined_identities),
                "blocked_third_parties": list(blocked_third_parties),
            }

            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.save_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(save_data, f, indent=2)

            # Atomic rename
            temp_file.replace(self.save_file)

            logger.info(f"Game saved successfully to {self.save_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False

    def load_game(self) -> Optional[Dict]:
        """
        Load game state from disk.

        Returns:
            Dictionary of saved game state, or None if no save exists or error
        """
        try:
            if not self.save_file.exists():
                logger.info("No save file found, starting new game")
                return None

            with open(self.save_file, "r") as f:
                save_data = json.load(f)

            # Version check
            if save_data.get("version") != self.version:
                logger.warning(
                    f"Save file version mismatch (expected {self.version}, got {save_data.get('version')})"
                )
                # Could implement migration logic here if needed

            logger.info(f"Game loaded successfully from {self.save_file}")
            logger.info(f"Last saved: {save_data.get('last_saved')}")
            logger.info(
                f"Quarantined identities: {len(save_data.get('quarantined_identities', []))}"
            )
            logger.info(
                f"Completed levels: {len(save_data.get('progress', {}).get('completed_levels', []))}"
            )

            return save_data

        except json.JSONDecodeError as e:
            logger.error(f"Save file corrupted (invalid JSON): {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return None

    def delete_save(self) -> bool:
        """
        Delete the save file (for new game).

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if self.save_file.exists():
                self.save_file.unlink()
                logger.info("Save file deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete save file: {e}")
            return False

    def has_save(self) -> bool:
        """
        Check if a save file exists.

        Returns:
            True if save file exists, False otherwise
        """
        return self.save_file.exists()

    def get_save_info(self) -> Optional[Dict[str, any]]:
        """
        Get basic information about the save file without fully loading it.

        Returns:
            Dictionary with save info (last_saved, version, etc.) or None
        """
        try:
            if not self.save_file.exists():
                return None

            with open(self.save_file, "r") as f:
                save_data = json.load(f)

            return {
                "last_saved": save_data.get("last_saved"),
                "version": save_data.get("version"),
                "score": save_data.get("player", {}).get("score", 0),
                "eliminations": save_data.get("player", {}).get("eliminations", 0),
                "completed_levels": len(
                    save_data.get("progress", {}).get("completed_levels", [])
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get save info: {e}")
            return None
