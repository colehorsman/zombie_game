# Design Document: Game Enhancements

## Overview

This design document outlines the architecture and implementation approach for enhancing the Sonrai Zombie Blaster game with multi-level progression, boss battles, a damage/health system, protected identities, and improved documentation. These enhancements build upon the existing game architecture while maintaining backward compatibility and code quality.

## Architecture

The enhancements integrate into the existing architecture with new components:

```
┌─────────────────────────────────────────┐
│         Game Loop & Main Entry          │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼─────────┐
│  Game Engine   │    │   API Client     │
│  - Level Mgmt  │    │   - Exemptions   │
│  - Boss System │    │   - High-Risk    │
│  - Damage Sys  │    │   - Quarantine   │
└───────┬────────┘    └────────┬─────────┘
        │                      │
┌───────▼────────┐    ┌────────▼─────────┐
│   Renderer     │    │   Data Models    │
│  - Health Bars │    │   - Boss         │
│  - Shields     │    │   - Level        │
│  - Damage #s   │    │   - Protected    │
└────────────────┘    └──────────────────┘
```

## Components and Interfaces

### 1. Level Manager (`level_manager.py`)

New component for managing level progression.

```python
class LevelManager:
    def __init__(self, csv_path: str)
    def load_accounts() -> List[AccountLevel]
    def get_current_level() -> AccountLevel
    def advance_level() -> bool
    def is_final_level() -> bool
    def get_level_stats() -> LevelStats
```

**Responsibilities:**
- Load and parse AWS account data from CSV
- Sort accounts by environment type
- Track current level progress
- Provide level transition logic

### 2. Boss Entity (`boss.py`)

New entity class for boss enemies.

```python
class Boss:
    identity_id: str
    name: str
    position: Vector2
    health: int
    max_health: int
    sprite: pygame.Surface
    attack_pattern: AttackPattern
    
    def __init__(self, identity_data: dict, position: Vector2)
    def update(delta_time: float, player_pos: Vector2) -> None
    def take_damage(damage: int) -> bool
    def spawn_minions() -> List[Zombie]
    def get_bounds() -> Rect
```

**Responsibilities:**
- Boss entity state and behavior
- Health management
- AI movement toward player
- Mini-zombie spawning at health thresholds
- Attack pattern execution

### 3. Protected Entity (`protected_entity.py`)

New entity class for exempted/protected identities.

```python
class ProtectedEntity:
    identity_id: str
    name: str
    position: Vector2
    protection_reason: str
    sprite: pygame.Surface
    shield_sprite: pygame.Surface
    
    def __init__(self, exemption_data: dict, position: Vector2)
    def update(delta_time: float) -> None
    def render_shield(surface: pygame.Surface, camera_offset: Vector2) -> None
    def get_bounds() -> Rect
```

**Responsibilities:**
- Protected entity representation
- Purple shield rendering
- Tooltip information
- Collision detection (for ignoring)

### 4. Damage System (`damage_system.py`)

New component for managing health and damage.

```python
class DamageSystem:
    def apply_damage(entity: Entity, damage: int) -> DamageResult
    def create_damage_number(position: Vector2, damage: int) -> DamageNumber
    def update_damage_numbers(delta_time: float) -> None
    def render_damage_numbers(surface: pygame.Surface) -> None
```

**Responsibilities:**
- Apply damage to entities
- Create floating damage number animations
- Track and update active damage numbers
- Render damage numbers

### 5. Enhanced Sonrai API Client

Extended methods for new API calls.

```python
class SonraiAPIClient:
    # Existing methods...
    
    def fetch_exemptions(account: str) -> List[Exemption]
    def fetch_high_risk_entities(account: str) -> List[HighRiskEntity]
```

**New Responsibilities:**
- Fetch exempted identities per account
- Fetch high-risk entities for boss data

## Data Models

### AccountLevel

```python
@dataclass
class AccountLevel:
    account_number: str
    environment_type: str  # sandbox, dev, staging, prod
    level_number: int
    zombie_count: int
```

### Boss

```python
@dataclass
class Boss:
    identity_id: str
    name: str
    position: Vector2
    health: int
    max_health: int
    risk_score: float
    risk_factors: List[str]
    minion_spawn_thresholds: List[float]  # [0.75, 0.50, 0.25]
    is_defeated: bool
```

### Exemption

```python
@dataclass
class Exemption:
    resource_id: str
    resource_name: str
    exemption_reason: str
    expiration_date: Optional[datetime]
```

### HighRiskEntity

```python
@dataclass
class HighRiskEntity:
    resource_id: str
    resource_name: str
    risk_score: float
    risk_factors: List[str]
```

### DamageResult

```python
@dataclass
class DamageResult:
    damage_dealt: int
    remaining_health: int
    is_eliminated: bool
    is_critical: bool
```

### Enhanced GameState

```python
@dataclass
class GameState:
    # Existing fields...
    current_level: int
    total_levels: int
    score: int
    damage_multiplier: int
    boss_active: bool
    boss_health: int
    boss_max_health: int
    protected_entities_count: int
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Level progression order

*For any* sequence of level completions, levels should be completed in order from lowest level number to highest, with no skipped levels
**Validates: Requirements 1.2, 1.6**

### Property 2: Boss spawn after level clear

*For any* level where all zombies are eliminated, a boss should spawn before level completion
**Validates: Requirements 2.1**

### Property 3: Health depletion accuracy

*For any* entity with health H and damage D applied, the remaining health should equal max(0, H - D)
**Validates: Requirements 3.3**

### Property 4: Damage multiplier progression

*For any* score S, the damage multiplier should equal 1 + floor(S / 10)
**Validates: Requirements 4.3**

### Property 5: Protected entity invulnerability

*For any* projectile collision with a protected entity, the entity's health should remain unchanged
**Validates: Requirements 5.6**

### Property 6: Purple shield visibility

*For any* protected entity that is rendered, a purple shield visual indicator should be displayed
**Validates: Requirements 5.5**

### Property 7: Exemption data completeness

*For any* exemption fetched from the API, it should contain a resource_id, resource_name, and exemption_reason
**Validates: Requirements 6.2**

### Property 8: Boss health bar accuracy

*For any* boss with health H and max_health M, the health bar should display a fill percentage of H/M
**Validates: Requirements 2.3, 2.4**

### Property 9: Mini-zombie spawn thresholds

*For any* boss with spawn thresholds at [75%, 50%, 25%] health, mini-zombies should spawn exactly when health crosses each threshold
**Validates: Requirements 12.2**

### Property 10: Damage number animation lifecycle

*For any* damage number created, it should be visible for exactly 1.0 seconds before being removed
**Validates: Requirements 8.1**

### Property 11: Level completion statistics accuracy

*For any* completed level, the displayed statistics should match the actual zombies eliminated, time taken, and score earned during that level
**Validates: Requirements 9.2**

### Property 12: CSV account loading completeness

*For any* valid CSV file with N rows, the system should load exactly N account levels (excluding header and invalid rows)
**Validates: Requirements 11.2**

### Property 13: Entity health initialization

*For any* regular zombie created, it should have health = 3; for any 3rd party created, it should have health = 10
**Validates: Requirements 3.1, 3.2**

### Property 14: Elimination only at zero health

*For any* entity, it should only be eliminated when health reaches exactly 0, not before
**Validates: Requirements 3.4**

### Property 15: Score increment on quarantine

*For any* successful zombie quarantine, the score should increase by exactly 1
**Validates: Requirements 4.2**

## Implementation Strategy

### Phase 1: Damage and Health System (Foundation)

1. Add `health` and `max_health` to `Zombie` and `ThirdParty` classes
2. Add `damage` to `Projectile` class
3. Modify collision detection to apply damage instead of instant elimination
4. Create `DamageSystem` class for damage numbers
5. Update `Renderer` to display health bars
6. Add visual feedback (flash, damage numbers)

**Why First**: This is foundational for all other features. Bosses and protected entities both rely on the health system.

### Phase 2: Protected Identities

1. Add `fetch_exemptions()` to `SonraiAPIClient`
2. Create `ProtectedEntity` class
3. Add purple shield sprite rendering
4. Modify collision detection to skip protected entities
5. Add tooltip rendering for protected entities
6. Identify and mark Sonrai 3rd party as protected

**Why Second**: Independent of level system, can be tested with existing single-level game.

### Phase 3: Multi-Level System

1. Create `LevelManager` class
2. Add CSV parsing for account data
3. Modify `GameEngine` to support level-based loading
4. Add level transition screens
5. Update UI to show level information
6. Add level completion logic

**Why Third**: Builds on damage system, provides structure for boss battles.

### Phase 4: Boss Battles

1. Create `Boss` class with health system
2. Add boss sprite rendering (larger size)
3. Implement boss AI (movement toward player)
4. Add mini-zombie spawning at health thresholds
5. Add boss health bar rendering
6. Integrate boss spawn after level clear
7. Add `fetch_high_risk_entities()` to API client

**Why Fourth**: Requires level system to be in place, uses damage system.

### Phase 5: Scoring and Multipliers

1. Add `score` and `damage_multiplier` to `GameState`
2. Implement score increment on quarantine
3. Add damage multiplier calculation
4. Update projectile damage based on multiplier
5. Add UI display for score and multiplier
6. Add notification for multiplier increases

**Why Fifth**: Enhances existing systems, relatively simple addition.

### Phase 6: Documentation

1. Capture gameplay screenshots
2. Update README with new features
3. Add gameplay guide
4. Document new controls
5. Add screenshots section

**Why Last**: Requires all features to be implemented for accurate screenshots.

## API Queries

### Exemptions Query

```graphql
query getExemptions($account: String!) {
  Exemptions(where: { account: { value: $account, op: EQ } }) {
    items {
      resourceId
      resourceName
      exemptionReason
      expirationDate
    }
  }
}
```

### High-Risk Entities Query

```graphql
query getHighRiskEntities($account: String!) {
  HighRiskIdentities(where: { 
    account: { value: $account, op: EQ }
    riskScore: { value: "7.0", op: GTE }
  }) {
    items {
      resourceId
      resourceName
      riskScore
      riskFactors
    }
  }
}
```

## Visual Design Specifications

### Health Bars

- **Size**: 30px wide x 4px tall
- **Position**: Centered above entity, 5px gap
- **Colors**: 
  - Background: Gray (128, 128, 128)
  - Health: Red (220, 20, 20)
  - Border: Black (0, 0, 0)
- **Animation**: Smooth depletion over 0.2 seconds

### Purple Shield

- **Shape**: Hexagon or circle overlay
- **Color**: Purple (160, 32, 240) with 50% opacity
- **Size**: 1.2x entity size
- **Effect**: Pulsing scale between 1.0x and 1.1x over 1.0 second
- **Glow**: Outer glow effect, 2px radius

### Damage Numbers

- **Font**: Retro pixel font, 16px
- **Color**: White (255, 255, 255) fading to transparent
- **Animation**: Rise 30px over 1.0 second
- **Position**: Start at hit location, float upward

### Boss Sprite

- **Size**: 120px x 120px (3x zombie size)
- **Style**: More detailed, menacing appearance
- **Colors**: Darker, more saturated than regular zombies
- **Features**: Crown or special marker to indicate boss status

### Boss Health Bar

- **Size**: 400px wide x 20px tall
- **Position**: Top center of screen, 20px from top
- **Colors**:
  - Background: Dark gray (64, 64, 64)
  - Health: Red gradient (255, 0, 0) to (180, 0, 0)
  - Border: Gold (255, 215, 0)
- **Label**: Boss name displayed above bar

## Testing Strategy

### Unit Testing

- CSV parsing with valid and invalid data
- Damage calculation with various values
- Health depletion and elimination logic
- Score and multiplier calculations
- Protected entity collision detection
- Boss spawn threshold detection

### Property-Based Testing

- Health system with random damage values
- Level progression with random completion orders
- Damage multiplier with random scores
- Boss minion spawning with random health values

### Integration Testing

- Full level progression from start to finish
- Boss battle with minion spawning
- Protected entity interaction
- API calls for exemptions and high-risk entities

### Manual Testing

- Visual verification of health bars, shields, damage numbers
- Boss AI behavior and attack patterns
- Level transition screens
- Gameplay feel and balance

## Performance Considerations

- **Health Bar Rendering**: Batch render all health bars in single pass
- **Damage Numbers**: Limit to 20 active damage numbers, remove oldest if exceeded
- **Boss AI**: Update boss position every 3 frames instead of every frame
- **Shield Effect**: Use cached sprite with pre-rendered glow
- **CSV Loading**: Cache parsed account data, don't reload each level

## Configuration

New environment variables:

```
# Boss Configuration
BOSS_HEALTH_MULTIPLIER=50  # Boss health = this * regular zombie health
BOSS_SPEED=0.5  # Boss movement speed relative to zombies

# Damage Configuration
BASE_DAMAGE=1  # Starting damage per projectile
DAMAGE_MULTIPLIER_THRESHOLD=10  # Zombies per damage increase

# Visual Configuration
SHOW_HEALTH_BARS=true  # Display health bars above entities
SHOW_DAMAGE_NUMBERS=true  # Display floating damage numbers
```

## Error Handling

### CSV Loading Errors

- **Missing File**: Display error message, exit gracefully
- **Invalid Format**: Log warning, skip invalid rows, continue with valid data
- **Empty File**: Display error message, exit gracefully

### API Errors

- **Exemptions Fetch Failure**: Log error, continue without exemptions
- **High-Risk Fetch Failure**: Log error, create generic boss
- **Network Timeout**: Retry with exponential backoff

### Boss Spawn Errors

- **No High-Risk Data**: Create generic boss with placeholder name
- **Boss Spawn Position Invalid**: Find nearest valid position
- **Minion Spawn Failure**: Log error, continue without minions

## Migration Path

To maintain backward compatibility:

1. Add feature flags to enable/disable enhancements
2. Keep original single-level mode as fallback
3. Gracefully handle missing CSV file (use default account)
4. Allow disabling boss battles via config
5. Support both instant-kill and health-based modes

## Success Metrics

- All existing tests continue to pass
- New features have >80% test coverage
- Game maintains 60 FPS with all enhancements
- Level transitions complete in <1 second
- Boss battles are challenging but fair (player win rate 70-80%)
