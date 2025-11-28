# Product Backlog - Sonrai Zombie Blaster

**Last Updated**: 2025-11-24
**Product Owner**: Cole Horsman
**Status**: Active Development

---

## Legend

| Priority | Label | Description |
|----------|-------|-------------|
| 🔴 P0 | Critical | Blocking issues, must fix immediately |
| 🟠 P1 | High | Important for next release |
| 🟡 P2 | Medium | Should have, schedule when possible |
| 🟢 P3 | Low | Nice to have, future consideration |

| Status | Label |
|--------|-------|
| ✅ | Done |
| 🚧 | In Progress |
| 📋 | Ready for Dev |
| 🔍 | Needs Investigation |
| ⏸️ | On Hold |

---

## ✅ Recently Completed

| ID | Item | Status |
|----|------|--------|
| BUG-001 | Projectiles passing through zombies after quest completion | ✅ Fixed (spatial grid recreation) |
| BUG-002 | Door interaction cooldown causing re-entry | ✅ Fixed |
| BUG-003 | Lobby spawn position incorrect | ✅ Fixed |
| BUG-004 | Controller A/B buttons not dismissing messages | ✅ Fixed |
| FEAT-001 | JIT Access Quest (Production accounts) | ✅ Implemented |
| FEAT-002 | Service Protection Quest (Hacker challenge) | ✅ Implemented |
| FEAT-003 | Health/Damage system (3 HP zombies, 10 HP 3rd parties) | ✅ Implemented |
| FEAT-004 | Spatial grid collision optimization | ✅ Implemented |

---

## 🐛 Bugs

| ID | Priority | Description | Status | Notes |
|----|----------|-------------|--------|-------|
| BUG-005 | 🟠 P1 | Save/Load error: 'Level' object has no attribute 'is_completed' | 📋 Ready | Add attribute to Level class |
| BUG-006 | 🟡 P2 | Third party "Noops" error on block | 🔍 Investigate | Error handling needed |

---

## 🚀 Features - Current Sprint

### Epic: Visual Polish & UX

| ID | Priority | User Story | Status | Acceptance Criteria |
|----|----------|------------|--------|---------------------|
| FEAT-005 | 🟠 P1 | As a player, I want the raygun to look like a real weapon | 📋 Ready | Retro sci-fi style, visible in all states, 8-bit aesthetic |
| FEAT-006 | 🟡 P2 | As a player, I want a clean Zelda-style pause menu | 📋 Ready | Bulleted format, keyboard navigation, semi-transparent overlay |
| FEAT-007 | 🟡 P2 | As a player, I want the hacker to look more threatening | 📋 Ready | Laptop accessory, typing animation, matrix-style effects |

### Epic: Gameplay Enhancements

| ID | Priority | User Story | Status | Acceptance Criteria |
|----|----------|------------|--------|---------------------|
| FEAT-008 | 🟡 P2 | As a player, I want a lasso tool to capture admin roles (JIT quest) | 📋 Ready | Ranged interaction, visual animation, replaces walk-into mechanic |
| FEAT-009 | 🟢 P3 | As a player, I want damage numbers to appear when hitting enemies | 📋 Ready | Rise 30px, fade over 1s, max 20 active |
| FEAT-010 | 🟢 P3 | As a player, I want protected entities to show purple shields | 📋 Ready | Pulsing animation, 50% opacity, tooltip on proximity |

### Epic: Player Damage & Consequences System

| ID | Priority | User Story | Status | Notes |
|----|----------|------------|--------|-------|
| FEAT-027 | 🟠 P1 | As a player, I want to take damage when zombies touch me | 📋 Ready | Adds risk/reward, teaches defensive positioning |
| FEAT-028 | 🟠 P1 | Player health system (10 HP, visual health bar) | 📋 Ready | Hearts display, damage feedback, invincibility frames |
| FEAT-029 | 🟠 P1 | Damage consequences: 1 hit = 1 zombie unquarantined | 📋 Ready | Teaches cost of mistakes, mirrors real security incidents |
| FEAT-030 | 🟡 P2 | Death/respawn: All zombies unquarantined, level restarts | 📋 Ready | Except during boss battles (game over instead) |
| FEAT-031 | 🟡 P2 | Arcade mode damage: 1 hit = -1 from elimination count | 📋 Ready | Different consequence for timed mode |
| FEAT-032 | 🟢 P3 | Health power-ups and recovery items | 📋 Ready | Healing items, shield power-ups, temporary invincibility |

---

## 📋 Features - Backlog

### Epic: Multi-Level System Enhancements

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-011 | 🟢 P3 | Level completion screen with stats | 📋 Ready |
| FEAT-012 | 🟢 P3 | Final victory screen after all levels | 📋 Ready |
| FEAT-013 | 🟢 P3 | Cross-level scoring persistence | 📋 Ready |

### Epic: Boss Battles

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-014 | 🟢 P3 | Boss entity (3x size, 150 HP) from high-risk identities | 📋 Ready |
| FEAT-015 | 🟢 P3 | Boss health bar (top of screen) | 📋 Ready |
| FEAT-016 | 🟢 P3 | Mini-zombie spawning at 75%, 50%, 25% boss health | 📋 Ready |

### Epic: Audio & Music

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-017 | 🟢 P3 | 8-bit background music | ⏸️ On Hold |
| FEAT-018 | 🟢 P3 | Sound effects (laser, hit, victory) | ⏸️ On Hold |

### Epic: Production Outage Simulation

| ID | Priority | User Story | Status | Notes |
|----|----------|------------|--------|-------|
| FEAT-019 | 🟠 P1 | As a practitioner, I want to experience production outage scenarios | 📋 Ready | Teaches incident response, change freezes, war room dynamics |
| FEAT-020 | 🟡 P2 | Production outage: API rate limiting (throttled remediation) | 📋 Ready | Simulates AWS API throttling during incidents |
| FEAT-021 | 🟡 P2 | Production outage: Change freeze (no quarantine allowed) | 📋 Ready | Teaches change management policies |
| FEAT-022 | 🟡 P2 | Production outage: War room mode (team coordination required) | 📋 Ready | Multi-step approval process simulation |
| FEAT-023 | 🟡 P2 | Production outage: Rollback scenario (undo recent changes) | 📋 Ready | Teaches rollback procedures |

### Epic: Future Quests

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-024 | 🟢 P3 | S3 protection quest (Dev level) | ⏸️ Future |
| FEAT-025 | 🟢 P3 | RDS protection quest (Staging level) | ⏸️ Future |
| FEAT-026 | 🟢 P3 | Quest difficulty scaling by level | ⏸️ Future |

---

## 🧪 QA & Testing

| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| QA-001 | 🟠 P1 | Verify all bug fixes from Nov 24 session | 📋 Ready |
| QA-002 | 🟡 P2 | Property tests for damage/health system | 📋 Ready |
| QA-003 | 🟡 P2 | Cross-level functionality verification | 📋 Ready |
| QA-004 | 🟡 P2 | Integration test suite (test_integration.py) | 📋 Ready |

---

## 🔧 Technical Debt

| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| TECH-001 | 🟡 P2 | Standardize API error handling patterns | 📋 Ready |
| TECH-002 | 🟢 P3 | Update failing unit tests (outdated API signatures) | 📋 Ready |
| TECH-003 | 🟢 P3 | Documentation agent for auto-generating docs | ⏸️ Future |

---

## 📊 Sprint Planning

### Current Sprint Focus
1. **Bug fixes verified** - QA-001
2. **Visual polish** - FEAT-005 (raygun), FEAT-006 (pause menu)
3. **Save/load fix** - BUG-005

### Definition of Done
- [ ] Feature implemented and working
- [ ] No regressions in existing functionality
- [ ] 60 FPS maintained
- [ ] Manual testing passed

---

## 📈 Velocity & Progress

| Metric | Value |
|--------|-------|
| Core Game | ✅ 100% Complete |
| Quests | ✅ 2/2 Implemented |
| Visual Polish | 🟡 60% |
| QA Coverage | 🟡 70% |
| Documentation | 🟡 80% |

---

## 🗺️ Roadmap

```
Current     → Visual Polish, Bug Fixes
Next Sprint → Damage Numbers, Purple Shields, Pause Menu
Future      → Boss Battles, Audio, Additional Quests
```

---

## 🚨 Production Outage Feature - Detailed Design

### Overview
**Goal**: Simulate real-world production incidents that security teams face, teaching incident response, change management, and crisis decision-making through gameplay.

### Core Concept
During production account gameplay, random "outage events" occur that temporarily restrict or modify remediation capabilities, forcing players to adapt their strategy just like real security teams during incidents.

---

### Outage Type 1: Change Freeze 🧊
**Real-World Scenario**: Major incident declared, all non-emergency changes frozen

**Gameplay Mechanics**:
- **Duration**: 10-15 seconds
- **Effect**: Cannot quarantine identities or apply JIT protection
- **Visual**: Red "CHANGE FREEZE" banner across top, flashing border
- **Audio**: Alert siren (optional)
- **Player Actions**: Can still move, shoot (damage zombies), collect power-ups
- **Strategy**: Focus on positioning, combo building, power-up collection
- **Message**: "⚠️ PRODUCTION INCIDENT - Change freeze in effect. War room convened. ETA: 12s"

**Educational Value**:
- Teaches that security work doesn't stop during incidents
- Shows importance of preparation (power-ups = tools ready)
- Demonstrates change management discipline
- Mirrors real CAB (Change Advisory Board) freezes

**Trigger Conditions**:
- Production accounts only
- Random 5-10% chance every 30 seconds
- Never during first 30 seconds of level
- Never during active quests

---

### Outage Type 2: API Rate Limiting ⏱️
**Real-World Scenario**: AWS API throttling during high-volume operations

**Gameplay Mechanics**:
- **Duration**: 15-20 seconds
- **Effect**: Quarantine actions delayed by 2-3 seconds (queued)
- **Visual**: Yellow "RATE LIMITED" indicator, progress bar showing queue
- **Zombie Behavior**: Eliminated zombies stay visible (ghosted) until API processes
- **Queue Display**: "API Queue: 7 pending operations"
- **Strategy**: Prioritize high-value targets, manage queue carefully

**Educational Value**:
- Teaches AWS API rate limits are real constraints
- Shows importance of batch operations
- Demonstrates need for retry logic
- Mirrors real CloudTrail/IAM API throttling

**Trigger Conditions**:
- Production accounts only
- Triggered after 10+ rapid eliminations
- Cooldown: 60 seconds between occurrences

---

### Outage Type 3: War Room Mode 🎯
**Real-World Scenario**: Critical incident requires approval for all changes

**Gameplay Mechanics**:
- **Duration**: 20 seconds
- **Effect**: Each quarantine requires "approval" (press A/Space to confirm)
- **Visual**: Popup dialog: "Approve quarantine of [identity]? (A) Yes (B) No"
- **Time Cost**: 1-2 seconds per approval
- **Risk**: Wrong approvals spawn "audit zombie" (penalty)
- **Strategy**: Quick decision-making under pressure

**Educational Value**:
- Teaches incident command structure
- Shows approval overhead during crises
- Demonstrates risk of hasty decisions
- Mirrors real war room dynamics

**Trigger Conditions**:
- Production accounts only
- Triggered by eliminating 20+ zombies quickly
- Once per level maximum

---

### Outage Type 4: Rollback Required 🔄
**Real-World Scenario**: Recent change caused issues, must rollback

**Gameplay Mechanics**:
- **Duration**: 10 seconds
- **Effect**: Last 5 quarantined identities "un-quarantine" (zombies respawn)
- **Visual**: Purple "ROLLBACK IN PROGRESS" banner
- **Zombie Respawn**: Previously eliminated zombies return at spawn points
- **Message**: "⚠️ Rollback initiated - Recent changes reverted due to service impact"
- **Strategy**: Re-eliminate zombies quickly, learn from mistake

**Educational Value**:
- Teaches that changes can be reverted
- Shows impact of rollback decisions
- Demonstrates importance of testing
- Mirrors real incident rollback procedures

**Trigger Conditions**:
- Production accounts only
- 10% chance after eliminating 15+ zombies
- Only if player has eliminated 5+ in last 10 seconds

---

### Outage Type 5: Degraded Performance 🐌
**Real-World Scenario**: System slowdown during high load

**Gameplay Mechanics**:
- **Duration**: 15 seconds
- **Effect**: Player movement speed reduced by 30%, projectile speed reduced by 20%
- **Visual**: Orange "DEGRADED PERFORMANCE" indicator, screen slight desaturation
- **Zombie Behavior**: Normal speed (they have advantage)
- **Message**: "⚠️ System degradation detected - API latency elevated"
- **Strategy**: Defensive play, use terrain, conserve ammo

**Educational Value**:
- Teaches that systems slow down under load
- Shows importance of performance monitoring
- Demonstrates graceful degradation
- Mirrors real API latency spikes

**Trigger Conditions**:
- Production accounts only
- Random 8% chance every 45 seconds
- More likely with 30+ active zombies

---

### Outage Type 6: Compliance Audit 📋
**Real-World Scenario**: Auditor reviewing changes in real-time

**Gameplay Mechanics**:
- **Duration**: 20 seconds
- **Effect**: Must document each quarantine (type reason: 1=unused, 2=risky, 3=expired)
- **Visual**: Blue "AUDIT IN PROGRESS" banner, number selection overlay
- **Time Cost**: 0.5 seconds per documentation
- **Reward**: Bonus points for correct categorization
- **Penalty**: Audit zombie spawns for wrong category
- **Strategy**: Accurate categorization under time pressure

**Educational Value**:
- Teaches compliance documentation requirements
- Shows audit overhead on operations
- Demonstrates importance of accurate records
- Mirrors real SOC2/ISO27001 audits

**Trigger Conditions**:
- Production accounts only
- Triggered when entering level with 50+ zombies
- Once per level maximum

---

### Implementation Details

#### Data Model
```python
@dataclass
class ProductionOutage:
    type: OutageType  # CHANGE_FREEZE, RATE_LIMITED, WAR_ROOM, etc.
    duration: float  # seconds remaining
    start_time: float
    severity: str  # "warning", "critical", "emergency"
    message: str
    restrictions: List[str]  # ["no_quarantine", "approval_required", etc.]
    active: bool
```

#### Outage Manager
```python
class OutageManager:
    def __init__(self):
        self.active_outage = None
        self.cooldown_timer = 0
        self.outage_history = []
    
    def trigger_random_outage(self, game_state):
        """Randomly trigger outage based on conditions"""
        
    def update(self, delta_time, game_state):
        """Update active outage, check for expiration"""
        
    def can_quarantine(self) -> bool:
        """Check if quarantine allowed during outage"""
        
    def get_quarantine_delay(self) -> float:
        """Get delay for rate-limited scenarios"""
```

#### Visual Indicators
- **Top Banner**: Outage type and countdown
- **Screen Effects**: Border flash, color tint, shake
- **HUD Elements**: Queue display, approval prompts
- **Zombie Effects**: Ghosted appearance during delays

#### Audio Cues (Optional)
- Alert siren for change freeze
- Beep for rate limit warnings
- Urgent tone for war room
- Whoosh for rollback

---

### Educational Impact

**Learning Objectives**:
1. **Incident Response**: How teams handle production crises
2. **Change Management**: Why change freezes exist
3. **API Constraints**: Real-world rate limiting
4. **Approval Processes**: War room decision-making
5. **Rollback Procedures**: When and how to revert
6. **Performance Degradation**: System behavior under load
7. **Compliance**: Audit requirements and documentation

**Target Audiences**:
- **Junior Engineers**: Learn incident response basics
- **Security Teams**: Practice crisis decision-making
- **Managers**: Understand operational constraints
- **Executives**: See real-world incident dynamics

**Real-World Parallels**:
- AWS API throttling during mass remediation
- Change freezes during Black Friday/Cyber Monday
- War rooms during security incidents
- Rollbacks after failed deployments
- Performance issues during DDoS attacks
- Compliance audits during SOC2 reviews

---

### Difficulty Scaling

**Sandbox Account**: No outages (learning environment)
**Dev Account**: 5% outage chance, shorter durations
**Staging Account**: 10% outage chance, medium durations
**Production Account**: 15% outage chance, full durations

**Arcade Mode**: 20% outage chance, rapid succession (hardcore mode)

---

### Success Metrics

**Player Engagement**:
- Do players understand outage mechanics?
- Do they adapt strategy during outages?
- Do they learn from repeated outages?

**Educational Value**:
- Can players explain why change freezes happen?
- Do they understand API rate limiting?
- Can they describe war room procedures?

**Gameplay Balance**:
- Are outages frustrating or challenging?
- Do they add strategic depth?
- Do they feel realistic?

---

### Future Enhancements

**Phase 2**:
- **Multi-Outage Scenarios**: Multiple simultaneous outages
- **Outage Prediction**: Visual warnings 5 seconds before
- **Mitigation Tools**: Power-ups that reduce outage impact
- **Outage Logs**: Post-level review of incidents handled

**Phase 3**:
- **Custom Outages**: Players create scenarios
- **Team Mode**: Multiplayer war room coordination
- **Incident Playbooks**: Follow real runbooks during outages
- **Metrics Dashboard**: Track MTTR, MTTD, incident count

---

### Implementation Priority

**Phase 1 (MVP)**: 
- Change Freeze (simplest, highest educational value)
- API Rate Limiting (teaches real constraints)

**Phase 2**:
- War Room Mode (adds decision-making)
- Rollback Required (teaches reversibility)

**Phase 3**:
- Degraded Performance (adds difficulty)
- Compliance Audit (teaches documentation)

**Estimated Effort**: 3-4 days for Phase 1, 2-3 days per additional phase

---

## ❤️ Player Damage & Consequences System - Detailed Design

### Overview
**Goal**: Add meaningful consequences to player mistakes, teaching that security incidents have real costs and that defensive positioning matters as much as offensive action.

### Core Concept
Players start with 10 HP. When zombies touch the player, they take damage. Each hit has consequences that mirror real-world security incidents—undoing previous remediation work and forcing players to re-secure compromised identities.

---

## Health System Mechanics

### Base Health System
**Starting Health**: 10 HP (displayed as 5 hearts, 2 HP per heart)

**Visual Display**:
- **Top-left HUD**: Row of hearts (♥♥♥♥♥)
- **Full Heart**: ♥ (red, 2 HP)
- **Half Heart**: ♡ (pink outline, 1 HP)
- **Empty Heart**: ♡ (gray outline, 0 HP)

**Damage Values**:
- **Zombie Touch**: 1 HP damage
- **Third-Party Touch**: 2 HP damage
- **Boss Touch**: 3 HP damage
- **Hacker Touch**: 2 HP damage
- **Environmental Hazards**: 1 HP damage (future: spikes, fire)

**Invincibility Frames**:
- **Duration**: 1.5 seconds after taking damage
- **Visual**: Player sprite flashes (alternating visible/invisible every 0.1s)
- **Purpose**: Prevents instant death from multiple zombies
- **Gameplay**: Teaches spacing and escape tactics

---

## Damage Consequences by Game Mode

### Normal Level Mode: Zombie Unquarantine

**Mechanic**: Each hit unquarantines 1 previously eliminated zombie

**Implementation**:
```python
def on_player_damage(damage_amount):
    player.health -= damage_amount
    
    # For each HP lost, unquarantine 1 zombie
    for i in range(damage_amount):
        if quarantined_zombies:
            zombie = quarantined_zombies.pop()
            zombie.respawn_at_spawn_point()
            zombie.status = "active"
            active_zombies.append(zombie)
            
    show_message(f"⚠️ Security breach! {damage_amount} identities reactivated!")
```

**Visual Feedback**:
- **Screen Flash**: Red tint for 0.3 seconds
- **Damage Number**: "-1 HP" floats up from player
- **Zombie Respawn**: Purple portal effect at spawn point
- **Message**: "⚠️ Security breach! 1 identity reactivated!"
- **Sound**: Damage sound + zombie groan (optional)

**Educational Value**:
- **Teaches**: Security incidents can undo previous work
- **Mirrors**: Real breaches that reactivate dormant accounts
- **Shows**: Importance of maintaining security posture
- **Demonstrates**: Cost of mistakes in production

**Strategic Impact**:
- **Risk/Reward**: Aggressive play vs. defensive positioning
- **Resource Management**: Health is a resource like ammo
- **Difficulty Scaling**: More zombies = harder to avoid damage
- **Comeback Mechanic**: Can re-eliminate respawned zombies

---

### Death & Level Restart

**Trigger**: Player health reaches 0 HP

**Consequence**: All zombies unquarantined, level restarts from beginning

**Implementation**:
```python
def on_player_death():
    # Unquarantine ALL zombies
    for zombie in quarantined_zombies:
        zombie.respawn_at_spawn_point()
        zombie.status = "active"
        active_zombies.extend(quarantined_zombies)
        quarantined_zombies.clear()
    
    # Reset player state
    player.health = 10
    player.position = level_start_position
    player.power_ups.clear()
    
    # Reset quest progress (if any)
    active_quest.reset()
    
    show_message("💀 SECURITY FAILURE - All identities reactivated. Level restarting...")
    play_death_animation()
```

**Death Animation**:
1. **Player Collapse**: Sprite falls down (0.5s)
2. **Screen Fade**: Fade to black (1s)
3. **Message Display**: "SECURITY FAILURE" (2s)
4. **Statistics**: Show zombies eliminated before death
5. **Restart Prompt**: "Press SPACE to restart level"

**Educational Value**:
- **Teaches**: Complete security failures require full remediation
- **Mirrors**: Major breaches that compromise entire environments
- **Shows**: Importance of not letting threats accumulate
- **Demonstrates**: Cost of losing control

**Exception - Boss Battles**:
- **Different Behavior**: Death during boss = Game Over (not restart)
- **Reason**: Boss battles are climactic, should have higher stakes
- **Message**: "💀 GAME OVER - Boss defeated you. Return to lobby?"

---

### Arcade Mode: Elimination Count Penalty

**Mechanic**: Each hit subtracts 1 from elimination count (not score)

**Implementation**:
```python
def on_player_damage_arcade(damage_amount):
    player.health -= damage_amount
    
    # Subtract from elimination count
    arcade_stats.eliminations = max(0, arcade_stats.eliminations - damage_amount)
    
    # Visual feedback
    show_floating_text(f"-{damage_amount} eliminations!", color=RED)
    
    # No zombie respawn in arcade mode (would be chaotic)
```

**Why Different?**:
- **Arcade Mode**: Timed challenge, respawning zombies would be too punishing
- **Score Preservation**: Combo multipliers and power-ups still count
- **Elimination Count**: Only the "zombies eliminated" stat is reduced
- **Balance**: Keeps arcade mode fast-paced and fun

**Visual Feedback**:
- **Screen Flash**: Red tint
- **Stat Update**: Elimination counter decreases visibly
- **Message**: "⚠️ Hit! -1 elimination"
- **No Respawn**: Zombies stay eliminated

**Educational Value**:
- **Teaches**: Mistakes have measurable costs
- **Shows**: Performance metrics can be negatively impacted
- **Demonstrates**: Importance of avoiding incidents even under time pressure

**Death in Arcade Mode**:
- **Consequence**: Session ends immediately
- **Results Screen**: Shows stats at time of death
- **No Restart**: Must start new arcade session
- **Message**: "💀 Arcade session failed! Final score: [score]"

---

## Health Recovery System

### Health Power-Ups

**Heart Power-Up** ❤️
- **Spawn Rate**: 5% chance when eliminating zombie
- **Effect**: Restore 2 HP (1 full heart)
- **Max Health**: Cannot exceed 10 HP
- **Visual**: Red heart icon, pulsing animation
- **Duration**: 10 seconds before despawning
- **Sound**: Healing chime (optional)

**Shield Power-Up** 🛡️
- **Spawn Rate**: 3% chance when eliminating third-party
- **Effect**: Temporary invincibility (5 seconds)
- **Visual**: Blue shield bubble around player
- **Behavior**: Zombies bounce off shield
- **Strategic Use**: Push through zombie crowds safely

**Mega Health** 💊
- **Spawn Rate**: 1% chance (rare)
- **Effect**: Full health restore (10 HP)
- **Visual**: Green cross icon, glowing
- **Message**: "✨ Full health restored!"

### Quest Rewards
- **Quest Completion**: Restore 3 HP
- **Boss Defeat**: Full health restore
- **Level Completion**: Full health for next level

---

## Collision Detection & Damage

### Zombie Collision
```python
def check_zombie_collision(player, zombies):
    if player.invincible:
        return  # No damage during invincibility frames
    
    for zombie in zombies:
        if player.bounds.colliderect(zombie.bounds):
            apply_damage(player, 1)
            knockback_player(player, zombie.position)
            start_invincibility_frames(player, 1.5)
            break  # Only one hit per frame
```

### Knockback System
- **Direction**: Away from damage source
- **Distance**: 30 pixels
- **Duration**: 0.2 seconds
- **Purpose**: Creates space, prevents stunlock
- **Visual**: Player sprite pushed back

### Damage Feedback
1. **Visual**: Screen flash, player flash, damage number
2. **Audio**: Damage sound, player grunt (optional)
3. **Haptic**: Controller rumble (if supported)
4. **UI**: Health bar update, heart animation

---

## Difficulty Scaling

### By Account Type

**Sandbox Account**:
- **Starting Health**: 10 HP (normal)
- **Damage**: Standard (1 HP per zombie)
- **Respawn Penalty**: 1 zombie per hit
- **Health Drops**: 5% chance

**Dev Account**:
- **Starting Health**: 10 HP
- **Damage**: Standard
- **Respawn Penalty**: 1 zombie per hit
- **Health Drops**: 4% chance

**Staging Account**:
- **Starting Health**: 8 HP (harder)
- **Damage**: Standard
- **Respawn Penalty**: 2 zombies per hit (more punishing)
- **Health Drops**: 3% chance

**Production Account**:
- **Starting Health**: 6 HP (hardest)
- **Damage**: Standard
- **Respawn Penalty**: 2 zombies per hit
- **Health Drops**: 2% chance
- **Additional**: Production outages can cause damage

---

## Educational Messaging

### Damage Messages (Contextual)

**First Hit**:
```
⚠️ SECURITY BREACH DETECTED!
A zombie touched you - 1 identity reactivated.
Maintain safe distance from threats!
```

**Multiple Hits**:
```
⚠️ MULTIPLE BREACHES!
{count} identities reactivated.
Defensive positioning is critical!
```

**Low Health (3 HP or less)**:
```
🚨 CRITICAL: Health low!
One more breach could trigger full remediation.
Seek health power-ups or complete quest for healing.
```

**Death**:
```
💀 TOTAL SECURITY FAILURE
All remediation work lost. Environment compromised.

In production, this would mean:
- All quarantined accounts reactivated
- Full incident response required
- Potential data breach
- Compliance violations

Learn from this. Restart and secure the environment.
```

---

## Real-World Parallels

### What This Teaches

**Taking Damage = Security Incident**
- **Real World**: Malware infection, unauthorized access, data leak
- **Game**: Zombie touches player
- **Consequence**: Previous security work is undone

**Zombie Respawn = Account Reactivation**
- **Real World**: Compromised account reactivates after incomplete remediation
- **Game**: Previously eliminated zombie returns
- **Lesson**: Incidents can undo security improvements

**Death = Major Breach**
- **Real World**: Complete environment compromise requiring full remediation
- **Game**: All zombies unquarantined, level restart
- **Lesson**: Losing control has catastrophic consequences

**Health Management = Risk Management**
- **Real World**: Maintaining security posture, monitoring threats
- **Game**: Avoiding damage, collecting health power-ups
- **Lesson**: Proactive defense is cheaper than reactive remediation

**Invincibility Frames = Incident Response Window**
- **Real World**: Brief window to contain breach before it spreads
- **Game**: 1.5 seconds to escape after taking damage
- **Lesson**: Quick response can prevent cascading failures

---

## Implementation Details

### Data Model
```python
@dataclass
class PlayerHealth:
    current_hp: int = 10
    max_hp: int = 10
    invincible: bool = False
    invincibility_timer: float = 0.0
    last_damage_time: float = 0.0
    damage_history: List[DamageEvent] = field(default_factory=list)

@dataclass
class DamageEvent:
    timestamp: float
    damage_amount: int
    source: str  # "zombie", "third_party", "boss", etc.
    zombies_respawned: int
```

### Health Manager
```python
class HealthManager:
    def apply_damage(self, player, amount, source):
        """Apply damage and trigger consequences"""
        
    def start_invincibility(self, player, duration):
        """Start invincibility frames"""
        
    def update_invincibility(self, player, delta_time):
        """Update invincibility timer"""
        
    def respawn_zombies(self, count):
        """Respawn zombies as damage consequence"""
        
    def restore_health(self, player, amount):
        """Restore health from power-ups"""
```

### Visual Components
- **Health Bar**: Top-left corner, heart icons
- **Damage Flash**: Red screen overlay (0.3s)
- **Player Flash**: Sprite flashing during invincibility
- **Damage Numbers**: Float up from player position
- **Respawn Effects**: Purple portal at zombie spawn points

---

## Testing Strategy

### Unit Tests
- Health reduction on damage
- Invincibility frame timing
- Zombie respawn count calculation
- Health power-up restoration
- Max health clamping

### Integration Tests
- Damage → zombie respawn workflow
- Death → level restart workflow
- Arcade mode damage → elimination penalty
- Boss battle death → game over

### Property Tests
- Health never exceeds max
- Health never goes below 0
- Invincibility prevents damage
- Respawn count matches damage taken

### Manual Testing
- Take damage from each enemy type
- Verify visual feedback (flash, hearts, numbers)
- Test invincibility frames (no double-hit)
- Verify zombie respawn locations
- Test death and restart flow
- Test arcade mode damage penalty

---

## Balancing Considerations

### Too Punishing?
- **Concern**: Players frustrated by losing progress
- **Mitigation**: Invincibility frames, health power-ups, quest healing
- **Tuning**: Adjust respawn count per difficulty level

### Too Easy?
- **Concern**: Players ignore damage, no consequences
- **Mitigation**: Increase respawn count in higher difficulties
- **Tuning**: Reduce health power-up spawn rate

### Arcade Mode Balance
- **Concern**: Damage too punishing in timed mode
- **Solution**: Elimination penalty instead of respawn
- **Tuning**: Consider reducing damage in arcade mode

---

## Implementation Priority

**Phase 1 (Core System)**:
1. Health system (10 HP, visual display)
2. Damage detection (zombie collision)
3. Invincibility frames (1.5s)
4. Damage consequences (zombie respawn)

**Phase 2 (Feedback)**:
5. Visual feedback (flash, hearts, numbers)
6. Death and restart flow
7. Educational messages

**Phase 3 (Recovery)**:
8. Health power-ups (heart drops)
9. Quest healing rewards
10. Shield power-up

**Phase 4 (Polish)**:
11. Arcade mode damage penalty
12. Boss battle death = game over
13. Difficulty scaling by account

**Estimated Effort**: 4-5 days total (1-2 days per phase)

---

## Success Metrics

**Gameplay Balance**:
- Average deaths per level: 1-2 (challenging but fair)
- Health power-up usage: 60%+ (players seek healing)
- Damage avoidance: Players learn to maintain distance

**Educational Impact**:
- Players understand damage = undone work
- Players learn defensive positioning
- Players appreciate cost of mistakes

**Player Feedback**:
- "Damage feels fair, not cheap"
- "I learned to be more careful"
- "Health management adds strategy"

---

## 📝 Notes

- All Sonrai API integrations require `.env` configuration
- Game targets 60 FPS across all features
- Maintain retro 8-bit aesthetic in all visual updates
- Test with real Sonrai API data before release
- Production outage feature should feel challenging but fair, not punishing
