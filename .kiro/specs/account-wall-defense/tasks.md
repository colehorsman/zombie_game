# Account Wall Defense System - Tasks

## Phase 1: Core Data Model (1-2 hours)

### Task 1.1: Create AccountWall Class
**File:** `src/models.py`
**Effort:** 30 min

- [ ] Add `AccountWall` dataclass with health, damage_level, thresholds
- [ ] Implement `take_damage()` method
- [ ] Implement `_update_damage_level()` method
- [ ] Add `health_percentage` and `is_breached` properties
- [ ] Add constants for WARNING_THRESHOLD (50) and CRITICAL_THRESHOLD (25)

### Task 1.2: Update ThirdParty Class
**File:** `src/third_party.py`
**Effort:** 20 min

- [ ] Add `wall_damage_rate` field (default 2.0)
- [ ] Add `is_attacking_wall` property
- [ ] Implement `get_wall_damage(delta_time)` method
- [ ] Ensure blocked/protected third parties return 0 damage

### Task 1.3: Update GameState
**File:** `src/models.py`
**Effort:** 10 min

- [ ] Add `account_wall: Optional[AccountWall]` field to GameState
- [ ] Initialize to None (set when entering level)

---

## Phase 2: Game Loop Integration (1-2 hours)

### Task 2.1: Initialize Wall on Level Entry
**File:** `src/game_engine.py`
**Effort:** 20 min

- [ ] In `_enter_level()`, create AccountWall instance
- [ ] Set initial health to 100
- [ ] Store in `self.game_state.account_wall`

### Task 2.2: Implement Wall Damage Update
**File:** `src/game_engine.py`
**Effort:** 30 min

- [ ] Create `_update_wall_damage(delta_time)` method
- [ ] Loop through third parties, sum damage from active ones
- [ ] Apply total damage to account wall
- [ ] Check for breach condition
- [ ] Call from `_update_playing()` each frame

### Task 2.3: Implement Wall Breach Game Over
**File:** `src/game_engine.py`
**Effort:** 30 min

- [ ] Create `_trigger_wall_breach_game_over(attacking_parties)` method
- [ ] Build breach message with attacker names
- [ ] Show game over screen with purple theme
- [ ] Reuse existing game over menu (Retry/Lobby)

### Task 2.4: Clean Up Wall on Level Exit
**File:** `src/game_engine.py`
**Effort:** 10 min

- [ ] In `_return_to_lobby()`, set `account_wall = None`
- [ ] In retry level logic, reset wall to full health

---

## Phase 3: Visual Rendering (1-2 hours)

### Task 3.1: Render Wall Health HUD
**File:** `src/renderer.py`
**Effort:** 30 min

- [ ] Create `_render_wall_health_hud()` method
- [ ] Draw health bar (green/yellow/red based on health)
- [ ] Show percentage text
- [ ] Position in HUD area (top of screen, below player health?)
- [ ] Call from main render loop when in level

### Task 3.2: Render Wall Damage Effects
**File:** `src/renderer.py`
**Effort:** 30 min

- [ ] Create `_render_wall_damage_effects()` method
- [ ] Draw cracks on level border based on damage_level
- [ ] Add warning pulse effect when critical (< 25%)
- [ ] Use existing color scheme (purple/red for danger)

### Task 3.3: Render Third Party Attack Indicator
**File:** `src/renderer.py`
**Effort:** 30 min

- [ ] Create `_render_third_party_attack_indicator()` method
- [ ] Draw pulsing line/beam from attacking third party toward wall
- [ ] Only show for active (non-blocked, non-protected) third parties
- [ ] Use red color for attack indicator

---

## Phase 4: Third Party Updates (30 min)

### Task 4.1: Stop Damage When Blocked
**File:** `src/game_engine.py`
**Effort:** 15 min

- [ ] In `_block_third_party()`, set `is_attacking_wall = False`
- [ ] Verify blocked third parties don't contribute to wall damage

### Task 4.2: Protected Third Parties Don't Attack
**File:** `src/game_engine.py` or `src/third_party.py`
**Effort:** 15 min

- [ ] Ensure Sonrai third parties have `is_protected = True`
- [ ] Ensure exempted third parties have `is_protected = True`
- [ ] Protected third parties return 0 from `get_wall_damage()`

---

## Phase 5: Testing & Polish (1 hour)

### Task 5.1: Unit Tests
**File:** `tests/test_account_wall.py`
**Effort:** 30 min

- [ ] Test AccountWall damage calculation
- [ ] Test damage level transitions (healthy → damaged → critical → breached)
- [ ] Test protected third party filtering
- [ ] Test breach detection

### Task 5.2: Integration Testing
**Effort:** 20 min

- [ ] Test wall damage accumulation in actual gameplay
- [ ] Test game over triggers correctly on breach
- [ ] Test blocking third party stops damage
- [ ] Test retry level resets wall health

### Task 5.3: Balance Tuning
**Effort:** 10 min

- [ ] Adjust damage rate for good gameplay feel
- [ ] Ensure player has time to react (not instant death)
- [ ] Test with multiple third parties active

---

## Implementation Order

**Recommended sequence:**
1. Phase 1 (Data Model) - Foundation
2. Phase 2 (Game Loop) - Core functionality
3. Phase 3 (Visuals) - Player feedback
4. Phase 4 (Third Party) - Complete integration
5. Phase 5 (Testing) - Validation

**Total Estimated Effort:** 4-6 hours

---

## Quick Start (MVP)

For a minimal viable implementation tonight:

1. **Task 1.1** - AccountWall class (30 min)
2. **Task 2.1** - Initialize on level entry (20 min)
3. **Task 2.2** - Wall damage update (30 min)
4. **Task 2.3** - Breach game over (30 min)
5. **Task 3.1** - Wall health HUD (30 min)

**MVP Total:** ~2.5 hours

This gives you:
- ✅ Wall health tracking
- ✅ Third parties damage walls
- ✅ Game over on breach
- ✅ Visual health bar

Visual polish (cracks, attack beams) can be added later.

---

## Dependencies

- Existing ThirdParty class
- Existing game over system (FEATURE-001)
- Existing purple theme rendering
- Existing HUD rendering system

## Files to Modify

| File | Changes |
|------|---------|
| `src/models.py` | Add AccountWall class, update GameState |
| `src/third_party.py` | Add wall damage methods |
| `src/game_engine.py` | Wall damage loop, breach handling |
| `src/renderer.py` | Wall health HUD, damage effects |
| `tests/test_account_wall.py` | New test file |
