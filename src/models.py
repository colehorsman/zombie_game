"""Data models for Sonrai Zombie Blaster."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class GameStatus(Enum):
    """Game state enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    VICTORY = "victory"
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


@dataclass
class GameState:
    """Tracks the current state of the game."""
    status: GameStatus
    zombies_remaining: int
    zombies_quarantined: int
    total_zombies: int
    error_message: Optional[str] = None
    congratulations_message: Optional[str] = None
    play_time: float = 0.0


@dataclass
class QuarantineResult:
    """Response from API quarantine operation."""
    success: bool
    identity_id: str
    error_message: Optional[str] = None
