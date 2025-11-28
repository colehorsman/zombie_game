"""Boss dialogue controller - manages boss introduction dialogue display."""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BossDialogueContent:
    """Content for a boss dialogue screen."""

    title: str
    description: str
    how_attacked: list
    victims: str
    prevention: list
    mechanic: str

    @classmethod
    def from_dict(cls, data: dict) -> "BossDialogueContent":
        """Create from dictionary (as returned by get_boss_dialogue)."""
        return cls(
            title=data.get("title", "BOSS APPEARS!"),
            description=data.get("description", ""),
            how_attacked=data.get("how_attacked", []),
            victims=data.get("victims", ""),
            prevention=data.get("prevention", []),
            mechanic=data.get("mechanic", ""),
        )


class BossDialogueController:
    """
    Manages boss introduction dialogue display.

    Extracted from GameEngine to reduce complexity and improve testability.
    Shows educational content about cyber attacks before boss battles.
    """

    def __init__(self):
        """Initialize the boss dialogue controller."""
        self.is_showing: bool = False
        self.content: Optional[BossDialogueContent] = None
        self.has_been_shown: bool = False  # Track if dialogue was shown this session

    def show(self, dialogue_data: dict) -> None:
        """
        Show boss dialogue with the given content.

        Args:
            dialogue_data: Dictionary with dialogue content (from get_boss_dialogue)
        """
        self.content = BossDialogueContent.from_dict(dialogue_data)
        self.is_showing = True
        self.has_been_shown = True
        logger.info(f"📖 Showing boss dialogue: {self.content.title}")

    def dismiss(self) -> bool:
        """
        Dismiss the dialogue.

        Returns:
            True if dialogue was dismissed, False if no dialogue was showing
        """
        if not self.is_showing:
            return False

        self.is_showing = False
        logger.info("📖 Boss dialogue dismissed")
        return True

    def reset(self) -> None:
        """Reset dialogue state for a new level/session."""
        self.is_showing = False
        self.content = None
        self.has_been_shown = False

    def build_message(self) -> str:
        """
        Build the dialogue message for display.

        Returns:
            Formatted dialogue message string
        """
        if not self.content:
            return "BOSS BATTLE!"

        lines = []

        # Title
        lines.append(self.content.title)
        lines.append("")

        # Description
        lines.append(self.content.description)
        lines.append("")

        # How they attacked
        lines.append("HOW THEY ATTACKED:")
        for attack in self.content.how_attacked:
            lines.append(f"  • {attack}")
        lines.append("")

        # Victims
        lines.append(f"NOTABLE VICTIMS: {self.content.victims}")
        lines.append("")

        # Prevention
        lines.append("PREVENTION:")
        for prevention in self.content.prevention:
            lines.append(f"  ✓ {prevention}")
        lines.append("")

        # Game mechanic
        lines.append("═" * 40)
        lines.append(self.content.mechanic)
        lines.append("")
        lines.append("Press ENTER to begin the battle!")

        return "\n".join(lines)

    def get_title(self) -> str:
        """Get the boss title for UI display."""
        if self.content:
            return self.content.title
        return "BOSS BATTLE"
