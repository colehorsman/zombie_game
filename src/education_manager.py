"""Education Manager for Story Mode educational content.

Manages educational triggers, progress tracking, and dialogue content delivery
for the Story Mode educational experience.
"""

import logging
from typing import Optional

from models import DialogueMessage, DialogueSequence, EducationalProgress, TriggerType
from save_manager import SaveManager

logger = logging.getLogger(__name__)


# Educational content templates with placeholders for dynamic data
EDUCATION_CONTENT = {
    TriggerType.STORY_MODE_WELCOME: [
        DialogueMessage(
            text="Welcome to Story Mode, Security Agent!",
            speaker="SONRAI",
            highlight_words=["Story Mode", "Security Agent"],
        ),
        DialogueMessage(
            text="Your mission: Eliminate zombie identities lurking in your AWS accounts.",
            speaker="SONRAI",
            highlight_words=["zombie identities", "AWS accounts"],
        ),
        DialogueMessage(
            text="Zombies are unused IAM identities - accounts that haven't been used in a long time.",
            speaker="SONRAI",
            highlight_words=["unused IAM identities"],
        ),
        DialogueMessage(
            text="They're security risks because attackers can compromise dormant accounts!",
            speaker="SONRAI",
            highlight_words=["security risks", "compromise"],
        ),
    ],
    TriggerType.FIRST_ZOMBIE_KILL: [
        DialogueMessage(
            text="You just quarantined {zombie_name}!",
            speaker="SONRAI",
            highlight_words=["quarantined"],
        ),
        DialogueMessage(
            text="This {zombie_type} hasn't been used in {days_since_login} days.",
            speaker="SONRAI",
            highlight_words=["{zombie_type}"],
        ),
        DialogueMessage(
            text="Sonrai's Cloud Permissions Firewall has disabled this identity.",
            speaker="SONRAI",
            highlight_words=["Cloud Permissions Firewall"],
        ),
        DialogueMessage(
            text="The identity can no longer access AWS resources - threat neutralized!",
            speaker="SONRAI",
            highlight_words=["threat neutralized"],
        ),
    ],
    TriggerType.FIRST_ROLE_ENCOUNTER: [
        DialogueMessage(
            text="You encountered a Role-type zombie!",
            speaker="SONRAI",
            highlight_words=["Role-type"],
        ),
        DialogueMessage(
            text="IAM Roles are used by services, applications, and cross-account access.",
            speaker="SONRAI",
            highlight_words=["services", "applications", "cross-account"],
        ),
        DialogueMessage(
            text="Unused roles are especially dangerous - they often have broad permissions!",
            speaker="SONRAI",
            highlight_words=["dangerous", "broad permissions"],
        ),
    ],
    TriggerType.FIRST_USER_ENCOUNTER: [
        DialogueMessage(
            text="You encountered a User-type zombie!",
            speaker="SONRAI",
            highlight_words=["User-type"],
        ),
        DialogueMessage(
            text="IAM Users are human accounts - employees, contractors, or service accounts.",
            speaker="SONRAI",
            highlight_words=["human accounts"],
        ),
        DialogueMessage(
            text="When people leave or change roles, their accounts often become zombies.",
            speaker="SONRAI",
            highlight_words=["zombies"],
        ),
    ],
    TriggerType.MILESTONE_5_KILLS: [
        DialogueMessage(
            text="5 zombies quarantined! You're making progress!",
            speaker="SONRAI",
            highlight_words=["5 zombies"],
        ),
        DialogueMessage(
            text="Regular identity audits are crucial for cloud security.",
            speaker="SONRAI",
            highlight_words=["identity audits", "cloud security"],
        ),
        DialogueMessage(
            text="Sonrai continuously monitors for unused identities so you don't have to!",
            speaker="SONRAI",
            highlight_words=["continuously monitors"],
        ),
    ],
    TriggerType.MILESTONE_10_KILLS: [
        DialogueMessage(
            text="10 zombies eliminated! You're a security champion!",
            speaker="SONRAI",
            highlight_words=["10 zombies", "security champion"],
        ),
        DialogueMessage(
            text="Each quarantined identity reduces your attack surface.",
            speaker="SONRAI",
            highlight_words=["attack surface"],
        ),
    ],
    TriggerType.LEVEL_COMPLETE: [
        DialogueMessage(
            text="Level Complete! All zombies in this account have been quarantined.",
            speaker="SONRAI",
            highlight_words=["Level Complete"],
        ),
        DialogueMessage(
            text="Security concepts learned: Identity lifecycle, least privilege, continuous monitoring.",
            speaker="SONRAI",
            highlight_words=[
                "Identity lifecycle",
                "least privilege",
                "continuous monitoring",
            ],
        ),
    ],
}


class EducationManager:
    """Manages educational triggers, progress, and content delivery for Story Mode."""

    def __init__(self, save_manager: Optional[SaveManager] = None):
        """
        Initialize the Education Manager.

        Args:
            save_manager: SaveManager for persisting progress (optional)
        """
        self.save_manager = save_manager
        self.progress = EducationalProgress()
        self.active_dialogue: Optional[DialogueSequence] = None
        self._pending_format_kwargs: dict = {}

        # Load progress from save if available
        if save_manager:
            self.progress = save_manager.load_educational_progress()
            logger.info(
                f"Loaded educational progress: {len(self.progress.completed_triggers)} triggers seen"
            )

    def check_trigger(
        self, trigger_type: TriggerType, context: Optional[dict] = None
    ) -> Optional[DialogueSequence]:
        """
        Check if an educational trigger should fire.

        Args:
            trigger_type: The type of trigger to check
            context: Optional context data (zombie_name, zombie_type, etc.)

        Returns:
            DialogueSequence if trigger should fire, None otherwise
        """
        # Don't trigger if already seen
        if self.progress.has_seen(trigger_type):
            logger.debug(f"Skipping trigger {trigger_type.value} - already seen")
            return None

        # Don't trigger if another dialogue is active
        if self.active_dialogue is not None:
            logger.debug(
                f"Skipping trigger {trigger_type.value} - dialogue already active"
            )
            return None

        # Get content for this trigger
        messages = EDUCATION_CONTENT.get(trigger_type)
        if not messages:
            logger.warning(f"No content defined for trigger {trigger_type.value}")
            return None

        # Create dialogue sequence
        dialogue = DialogueSequence(
            trigger_type=trigger_type,
            messages=list(messages),  # Copy to avoid modifying template
        )

        self.active_dialogue = dialogue
        self._pending_format_kwargs = context or {}

        logger.info(f"Triggered educational dialogue: {trigger_type.value}")
        return dialogue

    def get_format_kwargs(self) -> dict:
        """Get the format kwargs for the current dialogue."""
        return self._pending_format_kwargs

    def advance_dialogue(self) -> bool:
        """
        Advance to the next page of the active dialogue.

        Returns:
            True if advanced, False if dialogue is complete
        """
        if not self.active_dialogue:
            return False

        if self.active_dialogue.next_page():
            return True

        # Dialogue complete - mark as seen
        self.mark_completed(self.active_dialogue.trigger_type)
        return False

    def dismiss_dialogue(self) -> None:
        """Dismiss the active dialogue and mark it as completed."""
        if self.active_dialogue:
            self.mark_completed(self.active_dialogue.trigger_type)
            self.active_dialogue = None
            self._pending_format_kwargs = {}

    def mark_completed(self, trigger_type: TriggerType) -> None:
        """
        Mark an educational sequence as completed.

        Args:
            trigger_type: The trigger type to mark as seen
        """
        self.progress.mark_seen(trigger_type)
        logger.info(f"Marked educational trigger as seen: {trigger_type.value}")

    def reset_progress(self) -> None:
        """Reset all educational progress for tutorial replay."""
        self.progress.reset()
        self.active_dialogue = None
        self._pending_format_kwargs = {}
        logger.info("Reset all educational progress")

    def increment_eliminations(self) -> Optional[DialogueSequence]:
        """
        Increment zombie elimination count and check for milestone triggers.

        Returns:
            DialogueSequence if a milestone was reached, None otherwise
        """
        self.progress.zombies_eliminated += 1
        count = self.progress.zombies_eliminated

        # Check milestones
        if count == 5:
            return self.check_trigger(TriggerType.MILESTONE_5_KILLS)
        elif count == 10:
            return self.check_trigger(TriggerType.MILESTONE_10_KILLS)

        return None

    def check_zombie_type_education(
        self, zombie_type: str, context: Optional[dict] = None
    ) -> Optional[DialogueSequence]:
        """
        Check if we should show education for this zombie type.

        Args:
            zombie_type: The type of zombie (User, Role, etc.)
            context: Optional context data

        Returns:
            DialogueSequence if first encounter with this type, None otherwise
        """
        zombie_type_lower = zombie_type.lower()

        if "role" in zombie_type_lower and not self.progress.first_role_seen:
            self.progress.first_role_seen = True
            return self.check_trigger(TriggerType.FIRST_ROLE_ENCOUNTER, context)

        if "user" in zombie_type_lower and not self.progress.first_user_seen:
            self.progress.first_user_seen = True
            return self.check_trigger(TriggerType.FIRST_USER_ENCOUNTER, context)

        return None

    def is_dialogue_active(self) -> bool:
        """Check if a dialogue is currently active."""
        return self.active_dialogue is not None

    def get_active_dialogue(self) -> Optional[DialogueSequence]:
        """Get the currently active dialogue sequence."""
        return self.active_dialogue

    def save_progress(self) -> None:
        """Save educational progress to disk (requires save_manager)."""
        if self.save_manager:
            # Note: This would need to be called as part of the game's save routine
            # The SaveManager.save_game method now accepts educational_progress
            logger.info("Educational progress ready for save")
        else:
            logger.warning("No save manager - progress not persisted")

    def get_progress(self) -> EducationalProgress:
        """Get the current educational progress."""
        return self.progress
