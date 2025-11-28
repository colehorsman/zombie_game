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


class QuestStatus(Enum):
    """Service protection quest state enumeration."""
    NOT_STARTED = "not_started"  # Quest exists but not triggered
    TRIGGERED = "triggered"  # Dialog shown, waiting for ENTER
    ACTIVE = "active"  # Hacker spawned, race in progress
    COMPLETED = "completed"  # Service protected successfully


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

    # Service Protection Quest fields
    quest_message: Optional[str] = None  # Current quest message
    quest_message_timer: float = 0.0  # Time to display quest message
    service_hint_message: Optional[str] = None  # Hint at bottom of screen
    service_hint_timer: float = 0.0  # Time to display hint
    services_protected: int = 0  # Count of protected services

    # JIT Access Quest fields
    jit_quest: Optional['JitQuestState'] = None  # JIT quest state (only in production accounts)
    
    # Arcade Mode fields
    arcade_mode: Optional['ArcadeModeState'] = None  # Arcade mode state (60-second challenge)


@dataclass
class QuarantineResult:
    """Response from API quarantine operation."""
    success: bool
    identity_id: str
    error_message: Optional[str] = None


@dataclass
class ServiceProtectionQuest:
    """Represents a service protection race quest."""
    quest_id: str  # Unique identifier
    level: int  # Level number (1 for Sandbox, 6 for Production)
    service_type: str  # "bedrock", "s3", etc.
    trigger_position: Vector2  # Where quest triggers (x=300)
    service_position: Vector2  # Where service icon is located
    time_limit: float  # Race time limit (60.0 seconds)
    time_remaining: float  # Current countdown
    status: QuestStatus  # NOT_STARTED, TRIGGERED, ACTIVE, COMPLETED
    hacker_spawned: bool = False  # Whether hacker has been spawned
    player_won: bool = False  # Race outcome


@dataclass
class PermissionSet:
    """Represents an AWS permission set (admin/privileged role)."""
    id: str  # Permission set ID
    name: str  # Permission set name
    identity_labels: list  # Labels like ["ADMIN"] or ["PRIVILEGED"]
    user_count: int  # Number of users with this permission set
    has_jit: bool = False  # Whether JIT protection is enabled
    position: Optional[Vector2] = None  # Position in game world


@dataclass
class JitQuestState:
    """State for the JIT Access Quest."""
    active: bool = False  # Whether quest is active
    auditor_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))  # Auditor patrol position
    admin_roles: list = field(default_factory=list)  # List of PermissionSet objects
    protected_count: int = 0  # Number of roles with JIT protection
    total_count: int = 0  # Total number of admin/privileged roles
    quest_completed: bool = False  # Whether all roles are protected
    quest_failed: bool = False  # Whether player left without completing
    quest_message: Optional[str] = None  # Current quest message
    quest_message_timer: float = 0.0  # Time to display message


@dataclass
class ArcadeModeState:
    """State for Arcade Mode session."""
    active: bool = False  # Whether arcade mode is active
    in_countdown: bool = False  # Whether in 3-second countdown
    countdown_time: float = 3.0  # Countdown timer (3 seconds)
    time_remaining: float = 60.0  # Main timer (60 seconds)
    session_duration: float = 0.0  # Total time elapsed in session
    eliminations_count: int = 0  # Total zombies eliminated
    combo_count: int = 0  # Current combo count
    combo_multiplier: float = 1.0  # Current combo multiplier
    highest_combo: int = 0  # Highest combo achieved
    powerups_collected: int = 0  # Total power-ups collected


@dataclass
class ArcadeStats:
    """Statistics for arcade mode session."""
    total_eliminations: int = 0
    eliminations_per_second: float = 0.0
    highest_combo: int = 0
    powerups_collected: int = 0


@dataclass
class QuarantineReport:
    """Report from batch quarantine operation."""
    total_queued: int = 0  # Total zombies in queue
    successful: int = 0  # Successfully quarantined
    failed: int = 0  # Failed to quarantine
    error_messages: list = field(default_factory=list)  # List of error messages
