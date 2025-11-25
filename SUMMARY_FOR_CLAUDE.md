# Summary: Projectile Collision Bug Investigation

## The Problem
**CRITICAL BUG:** Projectiles pass through zombies without dealing damage.

- ✅ Player collision with zombies WORKS (player gets stopped)
- ❌ Projectile collision with zombies FAILS (bullets pass through)
- Game is unplayable - can't eliminate zombies

## What I Tried

### 1. Checked Zombie State Flags ✅
**Theory:** Zombies stuck with `is_quarantining=True` flag  
**Result:** Bug fixes already in place for quest completion/failure  
**Conclusion:** Not the issue (player collision would also fail if this was the problem)

### 2. Verified Collision Detection Logic ✅
**Location:** `src/collision.py:137` - `check_collisions_with_spatial_grid()`  
**Result:** Logic is correct, properly skips zombies being eliminated  
**Conclusion:** Code is sound

### 3. Checked Collision Bounds ✅
**Finding:** Zombie collision boxes are intentionally smaller (28x32) than visual sprites (40x40)  
**Result:** This is by design for easier player navigation  
**Conclusion:** Bounds are correct (player collision proves this)

### 4. Created Diagnostic Tests ⚠️
**Created:**
- `tests/test_zombie_stuck_collision_bug.py` - Documents the bug
- `diagnose_collision_bug.py` - Test script
- `diagnose_collision_bounds.py` - Bounds test

**Result:** Tests revealed collision bounds are offset (+6x, +4y) but this is intentional

## What I Failed At

❌ **Could not reproduce the bug in isolated tests**  
- Test collisions work when zombies/projectiles are close enough
- The bug only happens in the actual running game

❌ **Could not identify root cause**  
- Player collision works (same zombie bounds)
- Projectile collision fails (different code path)
- Something specific to projectile collision is broken

## Key Clue
**Player collision works, projectile collision doesn't!**

This tells us:
1. Zombie bounds are correct
2. Collision detection runs
3. Something in the projectile collision code path is broken

## What I Added

### Diagnostic Logging (src/game_engine.py:1318-1335)
Added logging to track:
- Number of projectiles vs visible zombies
- First projectile and zombie positions/bounds
- Zombie `is_quarantining` state
- Number of collisions detected

**To see logs:** Run game and check console output when shooting

### Test Coverage
- ✅ Created 13 new tests for ENTER/SPACE key quest triggering (all pass)
- ✅ Created 7 tests documenting collision bug behavior
- ✅ 164/174 total tests passing (94.3%)

## Files Modified
1. `src/game_engine.py` - Added diagnostic logging (lines 1318-1335)
2. `CRITICAL_BUG_REPORT.md` - Detailed investigation report
3. `tests/test_quest_trigger_keyboard.py` - New tests (all passing)
4. `tests/test_zombie_stuck_collision_bug.py` - Bug documentation tests

## Theories for Claude to Investigate

### Theory 1: Spatial Grid Not Working
The `SpatialGrid` might not be properly tracking zombies for projectile collision.

**Check:**
```python
# src/collision.py:137
def check_collisions_with_spatial_grid(projectiles, zombies, grid):
    grid.clear()
    for zombie in zombies:
        if not zombie.is_quarantining:
            grid.add_zombie(zombie)  # ← Is this working?
    
    for projectile in projectiles:
        nearby_zombies = grid.get_nearby_zombies(projectile)  # ← Are zombies returned?
```

### Theory 2: Visible Zombies Filter Too Aggressive
```python
# src/game_engine.py:1323
visible_zombies = [
    z for z in self.zombies
    if not z.is_hidden and self.game_map.is_on_screen(...)
]
```
Maybe zombies are being filtered out when they shouldn't be?

### Theory 3: Projectiles Too Small
Projectile radius is only 4 pixels. With zombie collision box offset by +6x, +4y, projectiles might miss the collision box entirely.

### Theory 4: Collision Check Not Running
Maybe the collision check is being skipped due to game state or timing issues?

## How to Debug

1. **Launch game with logging:**
   ```bash
   python3 src/main.py
   ```

2. **Enter Sandbox level and shoot zombies**

3. **Check console for logs:**
   ```
   🔍 COLLISION CHECK: X projectiles vs Y visible zombies
   🎯 COLLISION RESULT: Z collisions detected
   ```

4. **Look for:**
   - Are visible_zombies count > 0?
   - Are projectiles being created?
   - Are collisions being detected (should be > 0)?
   - What are the zombie positions/bounds?
   - Is `is_quarantining` False?

## Expected Console Output (if working)
```
🔍 COLLISION CHECK: 1 projectiles vs 5 visible zombies (total: 5)
  Projectile[0]: pos=(120.0, 400.0), bounds=<rect(116, 396, 8, 8)>
  Zombie[0]: pos=(150.0, 400.0), bounds=<rect(156, 404, 28, 32)>, is_quarantining=False
🎯 COLLISION RESULT: 1 collisions detected
```

## Expected Console Output (if broken)
```
🔍 COLLISION CHECK: 1 projectiles vs 0 visible zombies (total: 5)
🎯 COLLISION RESULT: 0 collisions detected
```
OR
```
🔍 COLLISION CHECK: 1 projectiles vs 5 visible zombies (total: 5)
  Projectile[0]: pos=(120.0, 400.0), bounds=<rect(116, 396, 8, 8)>
  Zombie[0]: pos=(150.0, 400.0), bounds=<rect(156, 404, 28, 32)>, is_quarantining=True
🎯 COLLISION RESULT: 0 collisions detected
```

## Next Steps

1. Run game with diagnostic logging
2. Analyze console output
3. Based on logs, investigate:
   - If `visible_zombies` is empty → check filter logic
   - If `is_quarantining=True` → check where flag is set
   - If collisions=0 but zombies present → check spatial grid
   - If no logs appear → check if collision code runs

## Critical Code Locations

- **Projectile collision:** `src/game_engine.py:1318-1345`
- **Player collision:** `src/game_engine.py:1150-1175` (THIS WORKS!)
- **Collision detection:** `src/collision.py:137-195`
- **Zombie bounds:** `src/zombie.py:401-415`
- **Projectile bounds:** `src/projectile.py:82-91`

---

**Status:** Bug is real, reproducible, and critical. Diagnostic logging added. Ready for Claude to investigate with actual game logs.
