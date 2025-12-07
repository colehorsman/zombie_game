"""Data models for Sonrai Zombie Blaster."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


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


class TriggerType(Enum):
    """Educational dialogue trigger types for Story Mode."""

    # Core triggers
    STORY_MODE_WELCOME = "story_mode_welcome"
    FIRST_ZOMBIE_KILL = "first_zombie_kill"
    FIRST_ROLE_ENCOUNTER = "first_role_encounter"
    FIRST_USER_ENCOUNTER = "first_user_encounter"
    MILESTONE_5_KILLS = "milestone_5_kills"
    MILESTONE_10_KILLS = "milestone_10_kills"
    LEVEL_COMPLETE = "level_complete"

    # Advanced security triggers
    FIRST_HIGH_RISK_POLICY = "first_high_risk_policy"
    FIRST_THREAT_VECTOR = "first_threat_vector"
    FIRST_THIRD_PARTY_BLOCK = "first_third_party_block"
    SERVICE_PROTECTION_COMPLETE = "service_protection_complete"
    JIT_PROTECTION_APPLIED = "jit_protection_applied"


class GenreType(Enum):
    """Game genre types for multi-genre levels.

    Each AWS account level can be played in different game genres
    while maintaining the core identity management theme.

    **Feature: multi-genre-levels**
    """

    PLATFORMER = "platformer"  # Mario-style side-scrolling (default)
    SPACE_SHOOTER = "space_shooter"  # Asteroids/Galaga vertical shooter
    MAZE_CHASE = "maze_chase"  # Pac-Man style with Wally
    FIGHTING = "fighting"  # Mortal Kombat style boss battles


class CombatState(Enum):
    """States for Mortal Kombat-style boss battle flow."""

    VS_SCREEN = "vs_screen"  # "VS" screen with portraits
    ROUND_START = "round_start"  # "ROUND 1" announcement
    FIGHTING = "fighting"  # Active combat
    ROUND_END = "round_end"  # Round result display
    VICTORY = "victory"  # Player won
    DEFEAT = "defeat"  # Player lost
    RETURNING = "returning"  # Transitioning back to level


class FighterState(Enum):
    """States for fighter characters in boss battles."""

    IDLE = "idle"
    WALKING = "walking"
    PUNCHING = "punching"
    KICKING = "kicking"
    SPECIAL = "special"
    BLOCKING = "blocking"
    HIT = "hit"
    KO = "ko"


class BossAIState(Enum):
    """AI states for boss fighters."""

    APPROACH = "approach"  # Moving toward player
    ATTACK = "attack"  # Executing attack
    RETREAT = "retreat"  # Backing away
    BLOCK = "block"  # Blocking player attacks
    TAUNT = "taunt"  # Idle taunt animation


@dataclass
class UnlockCondition:
    """Condition for unlocking a genre."""

    type: str  # "default", "levels_completed", "zombies_eliminated"
    value: int  # Threshold value (0 for default)


@dataclass
class ControlScheme:
    """Control scheme for a genre."""

    movement: List[str]  # Movement directions available
    actions: List[str]  # Action buttons available
    description: str  # Human-readable description


@dataclass
class Attack:
    """An attack in fighting mode."""

    damage: int
    range: int
    type: str  # "punch", "kick", "special"
    cooldown: float = 0.3


@dataclass
class BossAttack:
    """A boss-specific attack."""

    name: str
    damage: int
    range: int
    cooldown: float


# Genre unlock conditions
GENRE_UNLOCK_CONDITIONS: Dict[GenreType, UnlockCondition] = {
    GenreType.PLATFORMER: UnlockCondition(type="default", value=0),
    GenreType.SPACE_SHOOTER: UnlockCondition(type="levels_completed", value=1),
    GenreType.MAZE_CHASE: UnlockCondition(type="zombies_eliminated", value=50),
    GenreType.FIGHTING: UnlockCondition(type="levels_completed", value=3),
}

# Control schemes per genre
CONTROL_SCHEMES: Dict[GenreType, ControlScheme] = {
    GenreType.PLATFORMER: ControlScheme(
        movement=["left", "right"],
        actions=["jump", "shoot"],
        description="Move, Jump, Shoot",
    ),
    GenreType.SPACE_SHOOTER: ControlScheme(
        movement=["left", "right"],
        actions=["shoot"],
        description="Move, Shoot Up",
    ),
    GenreType.MAZE_CHASE: ControlScheme(
        movement=["up", "down", "left", "right"],
        actions=[],
        description="Move to Chomp",
    ),
    GenreType.FIGHTING: ControlScheme(
        movement=["left", "right"],
        actions=["punch", "kick", "special", "block"],
        description="Move, Punch, Kick, Special, Block",
    ),
}


@dataclass
class DialogueMessage:
    """A single message in an educational dialogue sequence."""

    text: str
    speaker: str = "SONRAI"  # Who is "speaking" (SONRAI, SYSTEM, etc.)
    highlight_words: list = field(default_factory=list)  # Words to emphasize in display

    def format_text(self, **kwargs) -> str:
        """Format text with placeholder values (e.g., zombie name, type)."""
        try:
            return self.text.format(**kwargs)
        except (KeyError, ValueError):
            # KeyError: missing placeholder key
            # ValueError: malformed format string (e.g., single '{')
            return self.text


@dataclass
class DialogueSequence:
    """A multi-page educational dialogue triggered by gameplay events."""

    trigger_type: TriggerType
    messages: list  # List of DialogueMessage
    current_page: int = 0

    def next_page(self) -> bool:
        """
        Advance to next page.

        Returns:
            True if advanced to next page, False if already at end.
        """
        if self.current_page < len(self.messages) - 1:
            self.current_page += 1
            return True
        return False

    def is_complete(self) -> bool:
        """Check if all pages have been viewed (on last page)."""
        return self.current_page >= len(self.messages) - 1

    def get_current_message(self) -> Optional["DialogueMessage"]:
        """Get the current message to display."""
        if 0 <= self.current_page < len(self.messages):
            return self.messages[self.current_page]
        return None

    def reset(self) -> None:
        """Reset to first page."""
        self.current_page = 0


@dataclass
class Vector2:
    """2D vector for position and velocity."""

    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
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
    pending_elimination: Optional["Zombie"] = None  # Zombie waiting for elimination message
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
    jit_quest: Optional["JitQuestState"] = None  # JIT quest state (only in production accounts)

    # Arcade Mode fields
    arcade_mode: Optional["ArcadeModeState"] = None  # Arcade mode state (60-second challenge)

    # Photo Booth fields
    photo_booth_consent_active: bool = False  # True when showing consent prompt
    photo_booth_path: Optional[str] = None  # Path to generated photo booth image
    photo_booth_summary_active: bool = False  # True when showing photo booth summary screen

    # Educational Dialogue fields (Story Mode)
    active_dialogue: Optional["DialogueSequence"] = None  # Current educational dialogue
    dialogue_format_kwargs: dict = field(default_factory=dict)  # Format args for dialogue text
    is_story_mode: bool = False  # Whether playing in Story Mode (educational) vs Arcade

    # Multi-genre system
    current_genre: GenreType = GenreType.PLATFORMER  # Default to platformer

    # Player stats (for save/load)
    score: int = 0  # Player's current score
    eliminations: int = 0  # Total zombies eliminated
    damage_multiplier: float = 1.0  # Current damage multiplier
    genre_preferences: Dict[str, GenreType] = field(default_factory=dict)  # Per-level genre choices

    @property
    def is_dialogue_active(self) -> bool:
        """Check if an educational dialogue is currently active."""
        return self.active_dialogue is not None


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
    auditor_position: Vector2 = field(
        default_factory=lambda: Vector2(0, 0)
    )  # Auditor patrol position
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


@dataclass
class EducationalProgress:
    """Tracks which educational content the player has seen in Story Mode."""

    completed_triggers: set = field(default_factory=set)  # Set of TriggerType values seen
    zombies_eliminated: int = 0  # Total zombies eliminated in Story Mode
    first_role_seen: bool = False  # Has player encountered a Role-type zombie
    first_user_seen: bool = False  # Has player encountered a User-type zombie

    def has_seen(self, trigger_type: TriggerType) -> bool:
        """Check if player has seen this educational trigger."""
        return trigger_type.value in self.completed_triggers

    def mark_seen(self, trigger_type: TriggerType) -> None:
        """Mark an educational trigger as seen."""
        self.completed_triggers.add(trigger_type.value)

    def to_dict(self) -> dict:
        """Serialize for save file."""
        return {
            "completed_triggers": list(self.completed_triggers),
            "zombies_eliminated": self.zombies_eliminated,
            "first_role_seen": self.first_role_seen,
            "first_user_seen": self.first_user_seen,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EducationalProgress":
        """Deserialize from save file."""
        if not data:
            return cls()
        return cls(
            completed_triggers=set(data.get("completed_triggers", [])),
            zombies_eliminated=data.get("zombies_eliminated", 0),
            first_role_seen=data.get("first_role_seen", False),
            first_user_seen=data.get("first_user_seen", False),
        )

    def reset(self) -> None:
        """Reset all educational progress for tutorial replay."""
        self.completed_triggers.clear()
        self.zombies_eliminated = 0
        self.first_role_seen = False
        self.first_user_seen = False
