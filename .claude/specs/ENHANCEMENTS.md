# Planned Game Enhancements

This document outlines planned enhancements to transform Sonrai Zombie Blaster from a single-level experience into a full-featured multi-level progression game with boss battles and enhanced gameplay.

## Status: PLANNED (Not Yet Implemented)

Most of these features are designed but not yet implemented. This serves as the roadmap for future development.

## Enhancement Overview

Transform the game with:
- **Multi-level progression** through AWS accounts (sandbox → production)
- **Boss battles** with high-risk entities from Sonrai
- **Enhanced visual feedback** (damage numbers, animations, effects)
- **Boss AI** with attack patterns and minion spawning
- **Level transition screens** with statistics
- **Comprehensive documentation** with gameplay screenshots

## E1: Multi-Level Progression System

**Goal**: Progress through multiple AWS accounts, cleaning up each environment systematically.

### Requirements

1. Load AWS account data from `assets/aws_accounts.csv`
2. Sort accounts by environment: sandbox → dev → staging → production
3. Load zombies only from current level's AWS account
4. Display level number, account number, and environment type in UI
5. Show level completion screen after clearing all zombies
6. Progress to next level on dismissal
7. Display special victory screen on final production level

### Implementation Components

**LevelManager** (`level_manager.py`):
```python
class LevelManager:
    def __init__(self, csv_path: str)
    def load_accounts() -> List[AccountLevel]
    def get_current_level() -> AccountLevel
    def advance_level() -> bool
    def is_final_level() -> bool
    def get_level_stats() -> LevelStats
```

**AccountLevel** data model:
```python
@dataclass
class AccountLevel:
    account_number: str
    environment_type: str  # sandbox, dev, staging, prod
    level_number: int
    zombie_count: int
```

### CSV Format

```csv
account_number,environment_type
577945324761,sandbox
514455208804,dev
240768036625,staging
613056517323,production
```

## E2: Boss Battle System

**Goal**: Challenging boss fights after each level representing high-risk security threats.

### Requirements

1. Spawn boss after all zombies eliminated in a level
2. Render boss 3-4x larger than regular zombies
3. Display boss health bar at top of screen
4. Update health bar as boss takes damage
5. Show special congratulations on boss defeat
6. Execute boss AI (movement, attacks, minion spawning)
7. Create mini-zombies at health thresholds

### Implementation Components

**Boss** (`boss.py`):
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

### Boss Data from API

**High-Risk Entities Query**:
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

### Boss Specifications

**Health**: 150 HP (50x regular zombie)
**Size**: 120x120px (3x zombie size)
**Speed**: 0.5x zombie speed (slower, more menacing)
**Minion Spawning**: At 75%, 50%, 25% health (3 mini-zombies each)
**Visual**: Darker colors, crown marker, detailed appearance

**Boss Health Bar**:
- Position: Top center, 20px from top
- Size: 400px × 20px
- Colors: Red gradient with gold border
- Label: Boss name above bar

## E3: Enhanced Visual Feedback

**Goal**: Clear visual communication of damage, health, and game events.

### Requirements

1. Floating damage numbers that rise and fade
2. Entity flash on damage (0.1s)
3. Health bars with red/gray coloring
4. Smooth health bar animations (0.2s)
5. Damage multiplier increase notifications (2s display)

### Visual Specifications

**Damage Numbers**:
- Font: Retro pixel, 16px
- Color: White fading to transparent
- Animation: Rise 30px over 1.0s
- Position: Start at hit location, float upward
- Limit: Max 20 active damage numbers

**Flash Effect**:
- Duration: 0.1 seconds
- Method: Lighten sprite by 50%
- Trigger: On any damage taken

## E4: Level Transition Screens

**Goal**: Clear communication of progress and statistics between levels.

### Requirements

1. Display level completion screen with statistics
2. Show zombies eliminated, time taken, score earned
3. Dismiss screen on key press
4. Display "Loading Level X" message during transition
5. Show victory screen with total game statistics on final level

### Screen Layout

**Level Completion**:
```
╔════════════════════════════════════╗
║      LEVEL 1 COMPLETE!             ║
║                                    ║
║  Zombies Eliminated: 47            ║
║  Time Taken: 3:42                  ║
║  Score Earned: 470                 ║
║  Damage Multiplier: 5x             ║
║                                    ║
║  Press ENTER to continue...        ║
╚════════════════════════════════════╝
```

**Final Victory**:
```
╔════════════════════════════════════╗
║    🎉 VICTORY! 🎉                  ║
║                                    ║
║  All AWS Accounts Secured!         ║
║                                    ║
║  Total Zombies Eliminated: 347     ║
║  Total Time: 18:23                 ║
║  Final Score: 3,470                ║
║  Final Damage Multiplier: 35x      ║
║  Levels Completed: 7               ║
║  Bosses Defeated: 7                ║
║                                    ║
║  Cloud Security: OPTIMIZED ✓       ║
╚════════════════════════════════════╝
```

## E5: Boss AI and Attack Patterns

**Goal**: Engaging, challenging boss battles with interesting behaviors.

### Requirements

1. Move boss toward player at slower speed
2. Spawn 3 mini-zombies at 75%, 50%, 25% health thresholds
3. Position mini-zombies near boss
4. Remove all mini-zombies on boss defeat
5. Respect map boundaries and collision detection

### AI Behavior

**Movement Pattern**:
- Target: Player position
- Speed: 0.5x regular zombie speed
- Update: Every 3 frames (performance optimization)

**Minion Spawning**:
- Threshold: Every 25% health lost
- Count: 3 mini-zombies per spawn
- Position: Random positions within 100px of boss
- Type: Regular zombies (3 HP each)

**Attack Pattern** (future):
- Projectile attacks
- Area-of-effect abilities
- Special moves at low health

## E6: Scoring and Damage Multiplier

**Status**: ✅ IMPLEMENTED

**Current System**:
- Base damage: 1 per projectile
- Score: +1 per successful quarantine
- Multiplier: +1 every 10 quarantines
- Projectile damage: Base × multiplier
- UI displays: Score and current multiplier

## E7: Documentation and Screenshots

**Goal**: Comprehensive documentation with visual examples.

### Requirements

1. Include Screenshots section with 4+ gameplay images
2. Document multi-level progression system
3. Explain damage and health system
4. Describe protected identities and purple shields
5. Add Gameplay section explaining scoring/multipliers
6. Save screenshots to `assets/screenshots/`
7. Use relative paths for screenshot display

### Screenshot Needs

1. **Main gameplay** - Player shooting zombies with UI visible
2. **Congratulations message** - Retro Game Boy-style message bubble
3. **Protected entities** - Purple shields on Sonrai/exempted entities
4. **Health system** - Damage numbers and health bars visible
5. **Boss battle** (when implemented) - Boss with health bar and minions
6. **Level completion** (when implemented) - Transition screen
7. **Victory screen** (when implemented) - Final statistics

## Implementation Phases

### Phase 1: Visual Enhancements ✅ DONE
- ✅ Health bars
- ✅ Protected entity purple shields
- ✅ Damage system (HP-based elimination)
- 🚧 Floating damage numbers (partially done)
- 🚧 Enhanced animations

### Phase 2: Documentation (IN PROGRESS)
- 🚧 Screenshot capture
- 🚧 README updates
- 🚧 Gameplay guide
- ✅ API documentation (comprehensive)

### Phase 3: Multi-Level System (PLANNED)
- ⏳ CSV account loading
- ⏳ Level manager
- ⏳ Level-based zombie loading
- ⏳ Level transition screens
- ⏳ Level progression logic

### Phase 4: Boss Battles (PLANNED)
- ⏳ Boss entity class
- ⏳ Boss sprite rendering
- ⏳ Boss AI implementation
- ⏳ Mini-zombie spawning
- ⏳ Boss health bar
- ⏳ High-risk entities API integration

### Phase 5: Polish (PLANNED)
- ⏳ Enhanced sound effects
- ⏳ Particle effects
- ⏳ Improved animations
- ⏳ Balance tuning
- ⏳ Performance optimization

## Design Properties for Enhancements

When implementing enhancements, verify these properties:

1. **Level progression order**: Levels completed in order, no skipping
2. **Boss spawn after level clear**: Boss spawns when all zombies eliminated
3. **Health depletion accuracy**: Remaining health = max(0, H - D)
4. **Damage multiplier progression**: Multiplier = 1 + floor(Score / 10)
5. **Protected entity invulnerability**: Protected entities never take damage
6. **Purple shield visibility**: All protected entities show purple shield
7. **Exemption data completeness**: All exemptions have ID, name, reason
8. **Boss health bar accuracy**: Health bar fill = current HP / max HP
9. **Mini-zombie spawn thresholds**: Spawn exactly at 75%, 50%, 25%
10. **Damage number lifecycle**: Visible for exactly 1.0 seconds
11. **Level stats accuracy**: Displayed stats match actual game data
12. **CSV loading completeness**: Load exactly N valid account rows
13. **Entity health initialization**: Zombies=3HP, ThirdParties=10HP
14. **Elimination at zero health**: Eliminate only when HP = 0
15. **Score increment on quarantine**: Score +1 per successful quarantine

## Configuration for Enhancements

New `.env` variables:

```bash
# Boss Configuration
BOSS_HEALTH_MULTIPLIER=50  # Boss health = 50x zombie health
BOSS_SPEED=0.5  # Boss speed relative to zombies
BOSS_MINION_COUNT=3  # Minions spawned per threshold

# Damage Configuration
DAMAGE_MULTIPLIER_THRESHOLD=10  # Zombies per damage increase

# Visual Configuration
SHOW_HEALTH_BARS=true
SHOW_DAMAGE_NUMBERS=true
SHOW_BOSS_HEALTH_BAR=true

# Level Configuration
ACCOUNTS_CSV_PATH=assets/aws_accounts.csv
```

## Migration and Compatibility

To maintain backward compatibility:
- Add feature flags to enable/disable enhancements
- Keep single-level mode as fallback
- Gracefully handle missing CSV (use default account)
- Allow disabling boss battles via config
- Support both instant-kill and HP-based modes (config toggle)

## Success Metrics

When implementing enhancements:
- ✅ All existing tests continue to pass
- ✅ New features have >80% test coverage
- ✅ Game maintains 60 FPS with all enhancements
- ✅ Level transitions complete in <1 second
- ✅ Boss battles challenging but fair (70-80% player win rate)
- ✅ Clear documentation with visual examples
- ✅ No regression in existing functionality
