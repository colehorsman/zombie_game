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

### 6. BossBattleController

Mortal Kombat-style 1v1 boss combat in a dedicated arena.

```python
class BossBattleController:
    """Controls Mortal Kombat-style boss battles in a separate arena."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.boss: Optional[CyberBoss] = None
        self.player_fighter: Optional[PlayerFighter] = None
        self.arena: Optional[FightingArena] = None
        self.round_number: int = 1
        self.max_rounds: int = 3
        self.round_timer: float = 99.0
        self.combat_state: CombatState = CombatState.VS_SCREEN
        self.return_level: Optional[Level] = None  # Level to return to after battle

    def start_boss_battle(self, boss_type: BossType, return_level: Level) -> None:
        """Transition to boss arena and start the fight."""
        self.return_level = return_level
        self.boss = create_boss_fighter(boss_type)
        self.player_fighter = PlayerFighter()
        self.arena = FightingArena(boss_type)
        self.combat_state = CombatState.VS_SCREEN
        self.round_number = 1

    def update(self, delta_time: float) -> None:
        """Update combat state machine."""
        if self.combat_state == CombatState.VS_SCREEN:
            self._update_vs_screen(delta_time)
        elif self.combat_state == CombatState.FIGHTING:
            self._update_fighting(delta_time)
        elif self.combat_state == CombatState.ROUND_END:
            self._update_round_end(delta_time)
        elif self.combat_state == CombatState.VICTORY:
            self._update_victory(delta_time)
        elif self.combat_state == CombatState.DEFEAT:
            self._update_defeat(delta_time)

    def handle_input(self, input_state: InputState) -> None:
        """Handle fighting game controls."""
        if self.combat_state != CombatState.FIGHTING:
            return
        
        # Movement
        if input_state.left:
            self.player_fighter.move_left()
        elif input_state.right:
            self.player_fighter.move_right()
        
        # Attacks
        if input_state.punch:
            self.player_fighter.punch()
        elif input_state.kick:
            self.player_fighter.kick()
        elif input_state.special:
            self.player_fighter.special_move()
        
        # Defense
        if input_state.block:
            self.player_fighter.block()

    def end_battle(self, player_won: bool) -> None:
        """End battle and return to level."""
        if player_won:
            self.combat_state = CombatState.VICTORY
        else:
            self.combat_state = CombatState.DEFEAT
```

### 7. PlayerFighter

Player character for fighting mode with attack moves.

```python
class PlayerFighter:
    """Player character in Mortal Kombat-style combat."""
    
    def __init__(self):
        self.position: Vector2 = Vector2(200, ARENA_GROUND_Y)
        self.health: int = 100
        self.max_health: int = 100
        self.state: FighterState = FighterState.IDLE
        self.facing: int = 1  # 1 = right, -1 = left
        self.is_blocking: bool = False
        self.attack_cooldown: float = 0.0
        self.combo_count: int = 0
        
        # Attack properties
        self.punch_damage: int = 5
        self.kick_damage: int = 8
        self.special_damage: int = 15
        
    def punch(self) -> Optional[Attack]:
        """Execute quick punch attack."""
        if self.attack_cooldown > 0 or self.is_blocking:
            return None
        self.state = FighterState.PUNCHING
        self.attack_cooldown = 0.3
        return Attack(damage=self.punch_damage, range=50, type="punch")
    
    def kick(self) -> Optional[Attack]:
        """Execute kick attack with longer range."""
        if self.attack_cooldown > 0 or self.is_blocking:
            return None
        self.state = FighterState.KICKING
        self.attack_cooldown = 0.5
        return Attack(damage=self.kick_damage, range=70, type="kick")
    
    def special_move(self) -> Optional[Attack]:
        """Execute powerful special attack (Quarantine Blast)."""
        if self.attack_cooldown > 0 or self.is_blocking:
            return None
        self.state = FighterState.SPECIAL
        self.attack_cooldown = 1.0
        return Attack(damage=self.special_damage, range=100, type="special")
    
    def block(self) -> None:
        """Enter blocking stance."""
        self.is_blocking = True
        self.state = FighterState.BLOCKING
    
    def take_damage(self, damage: int) -> None:
        """Take damage, reduced if blocking."""
        if self.is_blocking:
            damage = damage // 3  # Block reduces damage by 2/3
        self.health = max(0, self.health - damage)
        if not self.is_blocking:
            self.state = FighterState.HIT
```

### 8. BossFighter

Boss character with unique attack patterns per boss type.

```python
class BossFighter:
    """Boss character in Mortal Kombat-style combat."""
    
    def __init__(self, boss_type: BossType):
        self.boss_type = boss_type
        self.position: Vector2 = Vector2(600, ARENA_GROUND_Y)
        self.health: int = 150
        self.max_health: int = 150
        self.state: FighterState = FighterState.IDLE
        self.facing: int = -1  # Facing left toward player
        self.ai_state: BossAIState = BossAIState.APPROACH
        self.attack_cooldown: float = 0.0
        self.aggression: float = 0.5  # Increases as health decreases
        
        # Boss-specific attacks
        self.attacks = self._get_boss_attacks(boss_type)
    
    def _get_boss_attacks(self, boss_type: BossType) -> List[BossAttack]:
        """Get unique attacks for this boss type."""
        if boss_type == BossType.SCATTERED_SPIDER:
            return [
                BossAttack("Web Strike", damage=10, range=80, cooldown=0.8),
                BossAttack("Credential Theft", damage=15, range=60, cooldown=1.5),
                BossAttack("Social Engineering", damage=20, range=100, cooldown=2.0),
            ]
        elif boss_type == BossType.HEARTBLEED:
            return [
                BossAttack("Memory Leak", damage=8, range=70, cooldown=0.6),
                BossAttack("Data Bleed", damage=12, range=90, cooldown=1.2),
                BossAttack("Buffer Overflow", damage=25, range=50, cooldown=2.5),
            ]
        elif boss_type == BossType.WANNACRY:
            return [
                BossAttack("Encrypt Strike", damage=10, range=60, cooldown=0.7),
                BossAttack("Ransom Demand", damage=15, range=80, cooldown=1.3),
                BossAttack("Worm Spread", damage=30, range=120, cooldown=3.0),
            ]
        # ... more boss types
    
    def update_ai(self, player_position: Vector2, delta_time: float) -> Optional[BossAttack]:
        """Update boss AI and potentially execute attack."""
        distance = abs(self.position.x - player_position.x)
        
        # Increase aggression as health decreases
        self.aggression = 0.5 + (1 - self.health / self.max_health) * 0.5
        
        if self.ai_state == BossAIState.APPROACH:
            if distance > 100:
                self._move_toward_player(player_position)
            else:
                self.ai_state = BossAIState.ATTACK
        
        elif self.ai_state == BossAIState.ATTACK:
            if self.attack_cooldown <= 0:
                attack = self._choose_attack(distance)
                if attack:
                    self.attack_cooldown = attack.cooldown
                    return attack
            self.ai_state = BossAIState.RETREAT if random.random() < 0.3 else BossAIState.APPROACH
        
        return None
```

### 9. FightingArena

The arena environment for boss battles.

```python
class FightingArena:
    """Mortal Kombat-style fighting arena."""
    
    def __init__(self, boss_type: BossType):
        self.boss_type = boss_type
        self.width: int = 800
        self.height: int = 600
        self.ground_y: int = 450
        self.background = self._load_arena_background(boss_type)
        self.effects: List[VisualEffect] = []
    
    def _load_arena_background(self, boss_type: BossType) -> ArenaBackground:
        """Load boss-specific arena background."""
        # Each boss has a themed arena
        arena_themes = {
            BossType.SCATTERED_SPIDER: "cyber_web_arena",
            BossType.HEARTBLEED: "bleeding_server_arena",
            BossType.WANNACRY: "ransomware_arena",
        }
        return ArenaBackground(arena_themes.get(boss_type, "default_arena"))
    
    def render(self, surface: pygame.Surface) -> None:
        """Render arena background and effects."""
        self.background.render(surface)
        for effect in self.effects:
            effect.render(surface)
    
    def render_health_bars(self, surface: pygame.Surface, 
                           player_health: int, player_max: int,
                           boss_health: int, boss_max: int) -> None:
        """Render health bars at top of screen."""
        # Player health bar (left side)
        player_pct = player_health / player_max
        pygame.draw.rect(surface, (100, 100, 100), (50, 30, 300, 25))
        pygame.draw.rect(surface, (0, 255, 0), (50, 30, 300 * player_pct, 25))
        
        # Boss health bar (right side)
        boss_pct = boss_health / boss_max
        pygame.draw.rect(surface, (100, 100, 100), (450, 30, 300, 25))
        pygame.draw.rect(surface, (255, 0, 0), (450, 30, 300 * boss_pct, 25))
    
    def render_timer(self, surface: pygame.Surface, time_remaining: float) -> None:
        """Render round timer in center."""
        # Display seconds remaining
        seconds = int(time_remaining)
        # Render centered at top
```

### 10. CombatState Enum

```python
class CombatState(Enum):
    """States for boss battle flow."""
    VS_SCREEN = "vs_screen"      # "VS" screen with portraits
    ROUND_START = "round_start"  # "ROUND 1" announcement
    FIGHTING = "fighting"        # Active combat
    ROUND_END = "round_end"      # Round result display
    VICTORY = "victory"          # Player won
    DEFEAT = "defeat"            # Player lost
    RETURNING = "returning"      # Transitioning back to level
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

### Property 13: Boss Arena Transition
*For any* boss battle trigger, the system SHALL transition to a dedicated arena room and return to the original level after the battle ends.
**Validates: Requirements 5.1, 5.8, 11.1**

### Property 14: Boss Health Bar Display
*For any* boss battle, health bars for both player and boss SHALL be displayed at the top of the screen and accurately reflect current health.
**Validates: Requirements 11.2**

### Property 15: Boss Timer Behavior
*For any* boss battle round, the timer SHALL count down from 99 seconds, and reaching zero SHALL determine winner by remaining health percentage.
**Validates: Requirements 11.3, 11.4**

### Property 16: Attack Damage Application
*For any* successful attack (not blocked), the target's health SHALL decrease by the attack's damage value.
**Validates: Requirements 5.4, 5.5**

### Property 17: Block Damage Reduction
*For any* attack received while blocking, the damage SHALL be reduced (by at least 50%).
**Validates: Requirements 13.3**

### Property 18: Boss AI Aggression Scaling
*For any* boss, aggression level SHALL increase as boss health decreases (low health = more aggressive).
**Validates: Requirements 14.4**

### Property 19: Victory Quarantine Trigger
*For any* boss defeat, the system SHALL trigger the quarantine animation and API call for that boss's identity.
**Validates: Requirements 5.6**

### Property 20: Defeat Retry Option
*For any* player defeat in boss battle, the system SHALL display a retry option allowing the player to attempt the fight again.
**Validates: Requirements 5.7**

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
