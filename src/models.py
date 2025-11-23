"""Data models for Sonrai Zombie Blaster."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class GameStatus(Enum):
    """Game state enumeration."""
    MENU = "menu"
    LOBBY = "lobby"  # Top-down lobby mode (main branch style)
    PLAYING = "playing"  # Platformer level mode (feature branch style)
    PAUSED = "paused"
    VICTORY = "victory"
    BOSS_BATTLE = "boss_battle"
    ERROR = "error"


@dataclass
class Vector2:
    """2D vector for position and velocity."""
    x: float
    y: float

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)


@dataclass
class UnusedIdentity:
    """Represents an unused AWS identity from Sonrai API."""
    identity_id: str
    identity_name: str
    identity_type: str  # IAM user, role, service account
    last_used: Optional[datetime]
    risk_score: float
    scope: str = None  # Full scope path (e.g., "aws/r-ui1v/ou-ui1v-abc123/577945324761")
    account: str = None  # AWS account number


@dataclass
class GameState:
    """Tracks the current state of the game."""
    status: GameStatus
    zombies_remaining: int
    zombies_quarantined: int
    total_zombies: int
    previous_status: Optional[GameStatus] = None  # Status before pausing
    third_parties_blocked: int = 0
    total_third_parties: int = 0
    error_message: Optional[str] = None
    congratulations_message: Optional[str] = None
    powerup_message: Optional[str] = None  # Power-up collection message
    powerup_message_timer: float = 0.0  # Time remaining to show power-up message
    resource_message: Optional[str] = None  # Resource interaction message (S3, RDS, etc.)
    resource_message_timer: float = 0.0  # Time remaining to show resource message
    play_time: float = 0.0
    pending_elimination: Optional['Zombie'] = None  # Zombie waiting for elimination message
    elimination_delay: float = 0.0  # Countdown timer before showing message
    current_level: int = 1  # Current level number (1-7)
    environment_type: str = "sandbox"  # Environment type (sandbox, production, etc)
    completed_levels: set = field(default_factory=set)  # Set of completed level account IDs
    current_level_account_id: Optional[str] = None  # Account ID of current level being played


@dataclass
class QuarantineResult:
    """Response from API quarantine operation."""
    success: bool
    identity_id: str
    error_message: Optional[str] = None
