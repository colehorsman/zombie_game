"""Service protection quest system."""

from dataclasses import dataclass
from typing import List, Optional
import pygame

from models import Vector2, ServiceProtectionQuest, QuestStatus
from bedrock_sprite import (
    generate_bedrock_sprite,
    generate_bedrock_protected,
    generate_bedrock_unprotected
)


# Position constants for platformer levels
# Ground level: (60 tiles × 16) - (8 ground tiles × 16) = 832
PLATFORMER_GROUND_Y = 832

# Service icon dimensions
SERVICE_ICON_HEIGHT = 48

# Service icon Y position (sits ON ground, not below)
SERVICE_ICON_Y = PLATFORMER_GROUND_Y - SERVICE_ICON_HEIGHT  # 784


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


def create_service_node(service_type: str, position: Vector2) -> ServiceNode:
    """
    Create a ServiceNode with generated sprites.

    Args:
        service_type: Type of service ("bedrock", "s3", etc.)
        position: Position of the service icon

    Returns:
        ServiceNode instance with all sprite variants
    """
    # Generate sprites based on service type
    if service_type in ("bedrock", "bedrock-agentcore"):
        sprite_base = generate_bedrock_sprite()
        sprite_protected = generate_bedrock_protected()
        sprite_unprotected = generate_bedrock_unprotected()
    else:
        # For future service types, use bedrock as fallback
        sprite_base = generate_bedrock_sprite()
        sprite_protected = generate_bedrock_protected()
        sprite_unprotected = generate_bedrock_unprotected()

    return ServiceNode(
        service_type=service_type,
        position=position,
        protected=False,  # Start unprotected
        sprite_base=sprite_base,
        sprite_protected=sprite_protected,
        sprite_unprotected=sprite_unprotected
    )


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
        service_type="bedrock-agentcore",
        trigger_position=trigger_pos,
        service_position=service_pos,
        time_limit=60.0,  # 60 seconds
        time_remaining=60.0,
        status=QuestStatus.NOT_STARTED,
        hacker_spawned=False,
        player_won=False
    )
