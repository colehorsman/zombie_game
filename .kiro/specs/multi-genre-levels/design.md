# Design Document: Multi-Genre Level System

## Overview

This feature transforms the level system into a "Choose Your Own Adventure" experience where players select different classic arcade game genres for each AWS account. Four genres are supported: Platformer (Mario), Space Shooter (Asteroids/Galaga), Maze Chase (Pac-Man with Wally), and Fighting (Mortal Kombat). Each genre provides unique gameplay while maintaining the core zombie elimination and educational mission.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Game Engine                                    │
│  ┌─────────────────┐                                                    │
│  │  Genre Manager  │◄─── Manages genre selection, unlocks, preferences  │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Genre Controllers (Strategy Pattern)          │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │   │
│  │  │ Platformer   │ │ SpaceShooter │ │  MazeChase   │ │Fighting │ │   │
│  │  │ Controller   │ │ Controller   │ │  Controller  │ │Controller│ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └─────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Zombie Behavior Adapters                      │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ │   │
│  │  │ Patrol AI    │ │ Formation AI │ │  Ghost AI    │ │Fighter  │ │   │
│  │  │ (Platformer) │ │ (Shooter)    │ │  (Maze)      │ │AI       │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └─────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           ▼                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Progress        │  │ Save Manager    │  │ Sonrai Client   │         │
│  │ Tracker         │  │ (Persistence)   │  │ (Quarantine)    │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. GenreManager

Central manager for genre selection, unlocks, and preferences.

```python
class GenreManager:
    def __init__(self, save_manager: SaveManager):
        self.save_manager = save_manager
        self.unlocked_genres: Set[Genre] = {Genre.PLATFORMER}
        self.account_preferences: Dict[str, Genre] = {}

    def get_available_genres(self) -> List[Genre]:
        """Return list of unlocked genres."""

    def select_genre(self, account_id: str, genre: Genre) -> None:
        """Set genre preference for an account."""

    def get_genre_for_account(self, account_id: str) -> Genre:
        """Get saved genre preference or default."""

    def check_unlock_conditions(self, progress: ProgressTracker) -> List[Genre]:
        """Check if any new genres should be unlocked."""

    def unlock_genre(self, genre: Genre) -> None:
        """Unlock a genre and trigger notification."""
```

### 2. GenreController (Abstract Base)

Base class for genre-specific game logic using Strategy Pattern.

```python
class GenreController(ABC):
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.zombies: List[Zombie] = []

    @abstractmethod
    def initialize_level(self, account: AWSAccount, zombies: List[UnusedIdentity]) -> None:
        """Set up level layout and spawn zombies."""

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update game logic for this genre."""

    @abstractmethod
    def handle_input(self, input_state: InputState) -> None:
        """Process player input for this genre."""

    @abstractmethod
    def check_completion(self) -> bool:
        """Check if level completion conditions are met."""

    @abstractmethod
    def get_player_controls(self) -> ControlScheme:
        """Return the control scheme for this genre."""
```

### 3. PlatformerController

Side-scrolling platformer implementation (existing behavior, refactored).

```python
class PlatformerController(GenreController):
    def initialize_level(self, account: AWSAccount, zombies: List[UnusedIdentity]) -> None:
        """Load side-scrolling layout, place zombies on platforms."""

    def update(self, delta_time: float) -> None:
        """Update platformer physics, zombie patrol AI."""

    def handle_input(self, input_state: InputState) -> None:
        """Handle jump, run, shoot controls."""

    def check_completion(self) -> bool:
        """Check if player reached level end."""
```

### 4. SpaceShooterController

Asteroids/Galaga-style vertical shooter.

```python
class SpaceShooterController(GenreController):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.formation_patterns = FormationPatterns()
        self.player_ship_y = SCREEN_HEIGHT - 100  # Fixed at bottom

    def initialize_level(self, account: AWSAccount, zombies: List[UnusedIdentity]) -> None:
        """Load space environment, spawn zombies in formations at top."""

    def update(self, delta_time: float) -> None:
        """Move zombies downward, check for bottom collision."""

    def handle_input(self, input_state: InputState) -> None:
        """Handle horizontal movement, upward shooting."""

    def check_completion(self) -> bool:
        """Check if all zombies eliminated."""
```

### 5. MazeChaseController

Pac-Man style maze gameplay with Wally.

```python
class MazeChaseController(GenreController):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.maze = MazeLayout()
        self.ghost_ai = GhostAI()

    def initialize_level(self, account: AWSAccount, zombies: List[UnusedIdentity]) -> None:
        """Generate maze, place Wally and zombie ghosts."""

    def update(self, delta_time: float) -> None:
        """Update Wally movement, ghost pathfinding."""

    def handle_input(self, input_state: InputState) -> None:
        """Handle 4-directional movement (no shooting - chomp on contact)."""

    def check_completion(self) -> bool:
        """Check if all zombies chomped."""

    def handle_collision(self, wally: Player, zombie: Zombie) -> None:
        """Determine if chomp (front) or damage (rear)."""
```

### 6. FightingController

Mortal Kombat-style 1v1 combat.

```python
class FightingController(GenreController):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.current_opponent_index = 0
        self.combat_state = CombatState()

    def initialize_level(self, account: AWSAccount, zombies: List[UnusedIdentity]) -> None:
        """Set up arena, queue zombies as opponents."""

    def update(self, delta_time: float) -> None:
        """Update combat, opponent AI, health bars."""

    def handle_input(self, input_state: InputState) -> None:
        """Handle punch, kick, special move, block controls."""

    def check_completion(self) -> bool:
        """Check if all opponents defeated."""

    def next_opponent(self) -> Optional[Zombie]:
        """Load next zombie opponent after defeat."""
```

### 7. ZombieBehaviorAdapter

Adapts zombie behavior for each genre.

```python
class ZombieBehaviorAdapter:
    @staticmethod
    def create_for_genre(genre: Genre, identity: UnusedIdentity) -> Zombie:
        """Create zombie with genre-appropriate behavior."""

    @staticmethod
    def get_patrol_behavior() -> ZombieBehavior:
        """Platformer: patrol platforms, chase horizontally."""

    @staticmethod
    def get_formation_behavior(pattern: FormationPattern) -> ZombieBehavior:
        """Space Shooter: descend in formation."""

    @staticmethod
    def get_ghost_behavior(maze: MazeLayout) -> ZombieBehavior:
        """Maze Chase: pathfind through maze."""

    @staticmethod
    def get_fighter_behavior(difficulty: int) -> ZombieBehavior:
        """Fighting: combat AI with combos."""
```

### 8. ProgressTracker

Unified progress tracking across all genres.

```python
class ProgressTracker:
    def __init__(self):
        self.total_zombies_eliminated: int = 0
        self.levels_completed: int = 0
        self.account_completion: Dict[str, bool] = {}
        self.genre_stats: Dict[Genre, GenreStats] = {}

    def record_elimination(self, zombie: Zombie, genre: Genre) -> None:
        """Record zombie elimination, check unlock conditions."""

    def record_level_complete(self, account_id: str, genre: Genre) -> None:
        """Record level completion."""

    def get_account_status(self, account_id: str) -> AccountStatus:
        """Get completion status for an account."""

    def to_dict(self) -> dict:
        """Serialize for save file."""
```

## Data Models

### Genre Enum

```python
class Genre(Enum):
    PLATFORMER = "platformer"
    SPACE_SHOOTER = "space_shooter"
    MAZE_CHASE = "maze_chase"
    FIGHTING = "fighting"
```

### Genre Unlock Conditions

```python
GENRE_UNLOCK_CONDITIONS = {
    Genre.PLATFORMER: UnlockCondition(type="default", value=0),
    Genre.SPACE_SHOOTER: UnlockCondition(type="levels_completed", value=1),
    Genre.MAZE_CHASE: UnlockCondition(type="zombies_eliminated", value=50),
    Genre.FIGHTING: UnlockCondition(type="levels_completed", value=3),
}
```

### Control Schemes

```python
CONTROL_SCHEMES = {
    Genre.PLATFORMER: ControlScheme(
        movement=["left", "right"],
        actions=["jump", "shoot"],
        description="Move, Jump, Shoot"
    ),
    Genre.SPACE_SHOOTER: ControlScheme(
        movement=["left", "right"],
        actions=["shoot"],
        description="Move, Shoot Up"
    ),
    Genre.MAZE_CHASE: ControlScheme(
        movement=["up", "down", "left", "right"],
        actions=[],
        description="Move to Chomp"
    ),
    Genre.FIGHTING: ControlScheme(
        movement=["left", "right"],
        actions=["punch", "kick", "special", "block"],
        description="Move, Punch, Kick, Special, Block"
    ),
}
```

### Save File Schema Extension

```python
{
    "genre_data": {
        "unlocked_genres": ["platformer", "space_shooter"],
        "account_preferences": {
            "577945324761": "space_shooter",
            "613056517323": "platformer"
        },
        "genre_stats": {
            "platformer": {"zombies": 25, "time_played": 3600},
            "space_shooter": {"zombies": 15, "time_played": 1800}
        }
    },
    "progress": {
        "total_zombies_eliminated": 40,
        "levels_completed": 2,
        "account_completion": {
            "577945324761": true
        }
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Genre Selection Triggers Correct Template
*For any* genre selection, the system SHALL load the corresponding level template with the correct layout type (side-scrolling, vertical, maze, or arena).
**Validates: Requirements 1.3, 2.1, 3.1, 4.1, 5.1**

### Property 2: Genre Preference Persistence
*For any* genre selection for an account, saving and loading SHALL restore the same genre preference for that account.
**Validates: Requirements 1.4, 9.5**

### Property 3: Level Completion Condition
*For any* genre, eliminating all zombies (or reaching the end in Platformer) SHALL trigger level completion.
**Validates: Requirements 2.4, 3.5, 4.5, 5.5**

### Property 4: Space Shooter Player Position
*For any* Space Shooter level, the player ship SHALL be positioned at the bottom of the screen, and projectiles SHALL travel upward.
**Validates: Requirements 3.2, 3.4**

### Property 5: Space Shooter Zombie Behavior
*For any* zombie in Space Shooter mode, it SHALL spawn at the top and move downward, and reaching the bottom SHALL damage the player.
**Validates: Requirements 3.3, 3.6**

### Property 6: Maze Chase Movement Validity
*For any* zombie movement in Maze Chase mode, the zombie SHALL only move along valid maze paths (no wall clipping).
**Validates: Requirements 4.4**

### Property 7: Maze Chase Collision Direction
*For any* collision between Wally and a zombie in Maze Chase, front collision SHALL eliminate the zombie, and rear collision SHALL damage the player.
**Validates: Requirements 4.3, 4.6**

### Property 8: Fighting Sequential Opponents
*For any* Fighting mode level, zombies SHALL appear as sequential 1v1 opponents, not simultaneously.
**Validates: Requirements 5.2**

### Property 9: Identity Metadata Preservation
*For any* zombie across all genres, the original identity metadata (name, type, account, days since login) SHALL be preserved for educational display and quarantine.
**Validates: Requirements 7.5**

### Property 10: Cross-Genre Progress Aggregation
*For any* zombie elimination in any genre, the total elimination count SHALL increase, and account completion SHALL be tracked independently of genre used.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 11: Genre Unlock Conditions
*For any* new player, only Platformer SHALL be unlocked; completing 1 level SHALL unlock Space Shooter; eliminating 50 zombies SHALL unlock Maze Chase; completing 3 levels SHALL unlock Fighting.
**Validates: Requirements 10.1, 10.2, 10.3, 10.4**

### Property 12: Difficulty Scaling
*For any* account, the level difficulty SHALL scale with the account's zombie count (more zombies = harder).
**Validates: Requirements 8.4**

## Error Handling

### Genre Loading Failures
- If genre assets fail to load, fall back to Platformer (always available)
- Log error and show notification to player
- Don't corrupt save file on genre load failure

### Maze Generation
- If maze generation fails, use pre-built fallback maze
- Ensure maze always has valid path from start to all zombies

### Fighting AI
- If opponent AI fails, use simple attack pattern
- Prevent infinite loops in AI decision making

### Progress Tracking
- If progress update fails, retry on next frame
- Never lose elimination credit due to tracking error

## Testing Strategy

### Unit Tests
- Genre controller initialization
- Zombie behavior adapter for each genre
- Progress tracker aggregation
- Genre unlock condition evaluation
- Control scheme mapping

### Property-Based Tests (Hypothesis)
- Genre preference round-trip (save/load)
- Progress aggregation across genres
- Unlock conditions fire at exact thresholds
- Maze pathfinding produces valid paths
- Formation patterns produce valid positions

### Integration Tests
- Full genre selection flow from lobby
- Level completion triggers quarantine API
- Genre switching preserves progress
- Save/load with multiple genre preferences

### Manual Testing
- Visual verification of each genre's aesthetic
- Control feel and responsiveness per genre
- Difficulty balance across genres
- Genre unlock notifications
