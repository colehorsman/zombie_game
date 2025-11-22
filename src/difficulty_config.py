"""Difficulty configuration for environment-based gameplay mechanics."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class EnvironmentDifficulty:
    """Difficulty settings for a specific environment type."""

    environment: str          # "sandbox", "staging", etc.
    zombie_hp: int           # Base zombie health points
    reveal_radius: int       # How close player must be to see zombies (pixels)
    approvals_needed: int    # Approval collectibles needed to quarantine
    change_delay: float      # Delay in seconds after hit before quarantine
    boss_hp_multiplier: int  # Boss health = zombie_hp * multiplier

    # Visual indicators
    uses_approval_system: bool = False
    uses_change_delay: bool = False
    uses_reduced_visibility: bool = False


# Environment difficulty configurations
# Scales from easy (Sandbox) to extreme (Org) with production red tape
ENVIRONMENT_DIFFICULTY: Dict[str, EnvironmentDifficulty] = {
    "sandbox": EnvironmentDifficulty(
        environment="sandbox",
        zombie_hp=3,
        reveal_radius=60,  # Normal visibility
        approvals_needed=0,
        change_delay=0.0,  # Instant quarantine
        boss_hp_multiplier=50,
        uses_approval_system=False,
        uses_change_delay=False,
        uses_reduced_visibility=False,
    ),

    "staging": EnvironmentDifficulty(
        environment="staging",
        zombie_hp=3,
        reveal_radius=60,
        approvals_needed=0,
        change_delay=0.0,
        boss_hp_multiplier=50,
        uses_approval_system=False,
        uses_change_delay=False,
        uses_reduced_visibility=False,
    ),

    "automation": EnvironmentDifficulty(
        environment="automation",
        zombie_hp=4,
        reveal_radius=60,
        approvals_needed=0,
        change_delay=0.0,
        boss_hp_multiplier=50,
        uses_approval_system=False,
        uses_change_delay=False,
        uses_reduced_visibility=False,
    ),

    "webapp": EnvironmentDifficulty(
        environment="webapp",
        zombie_hp=4,
        reveal_radius=50,  # Harder to find
        approvals_needed=0,
        change_delay=0.0,
        boss_hp_multiplier=60,
        uses_approval_system=False,
        uses_change_delay=False,
        uses_reduced_visibility=True,
    ),

    "production-data": EnvironmentDifficulty(
        environment="production-data",
        zombie_hp=5,
        reveal_radius=30,  # Much harder to find
        approvals_needed=1,  # Need 1 approval
        change_delay=15.0,  # 15 second change window
        boss_hp_multiplier=70,
        uses_approval_system=True,
        uses_change_delay=True,
        uses_reduced_visibility=True,
    ),

    "production": EnvironmentDifficulty(
        environment="production",
        zombie_hp=6,
        reveal_radius=20,  # Very hard to find
        approvals_needed=3,  # Need 3 approvals (CAB process)
        change_delay=30.0,  # 30 second change window
        boss_hp_multiplier=80,
        uses_approval_system=True,
        uses_change_delay=True,
        uses_reduced_visibility=True,
    ),

    "org": EnvironmentDifficulty(
        environment="org",
        zombie_hp=7,
        reveal_radius=15,  # Extremely hard to find
        approvals_needed=5,  # Need 5 approvals (ultimate red tape)
        change_delay=30.0,  # 30 second change window
        boss_hp_multiplier=100,
        uses_approval_system=True,
        uses_change_delay=True,
        uses_reduced_visibility=True,
    ),
}


def get_difficulty_for_environment(environment_type: str) -> EnvironmentDifficulty:
    """
    Get difficulty configuration for an environment.

    Args:
        environment_type: Environment type (e.g., "sandbox", "production")

    Returns:
        EnvironmentDifficulty configuration

    Raises:
        KeyError: If environment type not found
    """
    if environment_type not in ENVIRONMENT_DIFFICULTY:
        raise KeyError(f"Unknown environment type: {environment_type}")

    return ENVIRONMENT_DIFFICULTY[environment_type]


def get_zombie_hp_for_environment(environment_type: str) -> int:
    """Get zombie HP for an environment."""
    return get_difficulty_for_environment(environment_type).zombie_hp


def get_reveal_radius_for_environment(environment_type: str) -> int:
    """Get reveal radius for an environment."""
    return get_difficulty_for_environment(environment_type).reveal_radius


def requires_approvals(environment_type: str) -> bool:
    """Check if environment requires approval collectibles."""
    return get_difficulty_for_environment(environment_type).uses_approval_system


def get_approvals_needed(environment_type: str) -> int:
    """Get number of approvals needed for an environment."""
    return get_difficulty_for_environment(environment_type).approvals_needed


def get_change_delay(environment_type: str) -> float:
    """Get change window delay for an environment."""
    return get_difficulty_for_environment(environment_type).change_delay


def has_change_delay(environment_type: str) -> bool:
    """Check if environment has change window delay."""
    return get_difficulty_for_environment(environment_type).uses_change_delay


def get_boss_hp(environment_type: str, base_zombie_hp: int = None) -> int:
    """
    Calculate boss HP for an environment.

    Args:
        environment_type: Environment type
        base_zombie_hp: Base zombie HP (if None, uses environment default)

    Returns:
        Boss health points
    """
    config = get_difficulty_for_environment(environment_type)
    if base_zombie_hp is None:
        base_zombie_hp = config.zombie_hp
    return base_zombie_hp * config.boss_hp_multiplier


# Visual feedback colors for different states
APPROVAL_COLORS = {
    "locked": (220, 20, 20),      # Red - needs approvals
    "approved": (20, 220, 20),    # Green - approved, can quarantine
    "pending": (220, 220, 20),    # Yellow - change window pending
}

# Status text templates
STATUS_TEXT = {
    "locked": "🔒 APPROVAL NEEDED",
    "approved": "✓ APPROVED",
    "pending": "⏳ CHANGE PENDING ({:.0f}s)",
    "request_submitted": "REQUEST SUBMITTED",
    "under_review": "UNDER REVIEW",
}
