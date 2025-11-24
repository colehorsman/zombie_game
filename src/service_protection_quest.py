"""Service protection quest system."""

from dataclasses import dataclass
from typing import List, Optional
import pygame

from models import Vector2, ServiceProtectionQuest, QuestStatus


@dataclass
class ServiceNode:
    """Represents a protectable AWS service."""
    service_type: str  # "bedrock", "s3", "rds", etc.
    position: Vector2  # Icon location (x, y)
    protected: bool  # Protection status
    sprite_base: pygame.Surface  # Normal sprite (48x48)
    sprite_protected: pygame.Surface  # With green shield
    sprite_unprotected: pygame.Surface  # With red warning

    def get_current_sprite(self) -> pygame.Surface:
        """Returns appropriate sprite based on state."""
        if self.protected:
            return self.sprite_protected
        return self.sprite_base


class ServiceProtectionQuestManager:
    """Manages all service protection quests."""

    def __init__(self):
        """Initialize the quest manager."""
        self.quests: List[ServiceProtectionQuest] = []
        self.active_quest: Optional[ServiceProtectionQuest] = None

    def add_quest(self, quest: ServiceProtectionQuest) -> None:
        """Add a quest to the manager."""
        self.quests.append(quest)

    def get_quest_for_level(self, level: int) -> Optional[ServiceProtectionQuest]:
        """Get the quest for a specific level."""
        for quest in self.quests:
            if quest.level == level:
                return quest
        return None

    def get_active_quest(self) -> Optional[ServiceProtectionQuest]:
        """Get the currently active quest."""
        for quest in self.quests:
            if quest.status in (QuestStatus.TRIGGERED, QuestStatus.ACTIVE):
                return quest
        return None


def create_bedrock_protection_quest(
    quest_id: str,
    level: int,
    trigger_pos: Vector2,
    service_pos: Vector2
) -> ServiceProtectionQuest:
    """
    Factory function to create a Bedrock protection quest.

    Args:
        quest_id: Unique identifier for the quest
        level: Level number (1 for Sandbox, 6 for Production)
        trigger_pos: Position where quest triggers
        service_pos: Position of service icon

    Returns:
        ServiceProtectionQuest instance configured for Bedrock
    """
    return ServiceProtectionQuest(
        quest_id=quest_id,
        level=level,
        service_type="bedrock",
        trigger_position=trigger_pos,
        service_position=service_pos,
        time_limit=60.0,  # 60 seconds
        time_remaining=60.0,
        status=QuestStatus.NOT_STARTED,
        hacker_spawned=False,
        player_won=False
    )
