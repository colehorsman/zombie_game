# CRITICAL BUG: Projectiles Not Hitting Zombies

## User Report
**Date:** 2024-11-24  
**Severity:** CRITICAL - Game Breaking  
**Status:** UNRESOLVED

### Symptoms
1. ✅ Player collision with zombies WORKS (player gets stopped by zombies)
2. ❌ Projectile collision with zombies FAILS (bullets pass through without damage)
3. User got stuck between zombies and bricks with no way to shoot them
4. Issue persists across game sessions

### What We've Tried

#### Investigation 1: Zombie State Flags
**Hypothesis:** Zombies have `is_quarantining=True` flag set incorrectly  
**Finding:** Collision detection correctly skips zombies with this flag  
**Status:** ✅ Bug fixes already in place for quest completion/failure  
**Conclusion:** Not the root cause (player collision would also fail)

#### Investigation 2: Collision Detection Logic
**Location:** `src/collision.py` - `check_collisions_with_spatial_grid()`  
**Finding:** Logic is correct - skips zombies with `is_quarantining=True` or `is_blocking=True`  
**Status:** ✅ Working as designed  
**Conclusion:** Logic is sound

#### Investigation 3: Collision Bounds
**Location:** `src/zombie.py` - `get_bounds()`  
**Finding:** 
- Zombie visual sprite: 40x40 pixels
- Zombie collision box: 28x32 pixels (smaller, with +6x, +4y offset)
- This is INTENTIONAL for easier player navigation
**Status:** ✅ Working as designed  
**Conclusion:** Bounds are correct

#### Investigation 4: Test Collision Positions
**Finding:** Test positions were too far apart (10 pixels between centers)  
**Status:** ⚠️ Tests need better positions  
**Conclusion:** Tests were wrong, not the code

### Key Diagnostic Results

```python
# Zombie at (100, 100)
Zombie bounds: <rect(106, 104, 28, 32)>  # Offset by +6, +4

# Projectile at (90, 100)  
Projectile bounds: <rect(86, 96, 8, 8)>

# Result: NO OVERLAP (10 pixels apart)
```

### Critical Clue
**Player collision works, projectile collision doesn't!**

This means:
1. ✅ Zombie bounds are correct (player can collide)
2. ✅ Collision detection runs (player stops at zombies)
3. ❌ Something specific to PROJECTILE collision is broken

### Code Locations

#### Projectile Collision Check (Line 1325-1345)
```python
# src/game_engine.py:1325
collisions = check_collisions_with_spatial_grid(
    self.projectiles,
    visible_zombies,
    self.spatial_grid
)

# Handle zombie collisions
for projectile, zombie in collisions:
    if projectile in self.projectiles:
        self.projectiles.remove(projectile)
    
    eliminated = zombie.take_damage(projectile.damage)
    
    if eliminated:
        self._handle_zombie_elimination(zombie)
```

#### Player Collision Check (Line 1150-1175)
```python
# src/game_engine.py:1150
for zombie in self.zombies:
    if not zombie.is_hidden:
        zombie_bounds = zombie.get_bounds()
        if player_bounds.colliderect(zombie_bounds):
            # Push player back (THIS WORKS!)
            if self.player.velocity.x > 0:
                self.player.position.x = zombie_bounds.left - self.player.width
```

### Possible Root Causes

#### Theory 1: Spatial Grid Issue
The spatial grid might not be properly tracking zombies for projectile collision but works for direct rect collision.

**Check:**
- `SpatialGrid.add_zombie()` - is it adding zombies correctly?
- `SpatialGrid.get_nearby_zombies()` - is it returning zombies near projectiles?

#### Theory 2: Visible Zombies Filter
```python
visible_zombies = [
    z for z in self.zombies
    if not z.is_hidden and self.game_map.is_on_screen(...)
]
```
Maybe zombies are being filtered out incorrectly?

#### Theory 3: Projectile Bounds Issue
Projectile radius is only 4 pixels. Maybe projectiles are too small to hit the offset collision boxes?

#### Theory 4: Timing Issue
Projectiles might be removed before collision check runs, or collision check might not run every frame.

### What Needs Investigation

1. **Add debug logging to collision detection:**
   ```python
   logger.info(f"Checking {len(self.projectiles)} projectiles vs {len(visible_zombies)} zombies")
   logger.info(f"Spatial grid returned {len(nearby)} nearby zombies")
   ```

2. **Check if `visible_zombies` list is empty:**
   - Are zombies being filtered out by `is_hidden` check?
   - Are zombies off-screen when they shouldn't be?

3. **Verify spatial grid is working:**
   - Add logging to `SpatialGrid.add_zombie()`
   - Add logging to `SpatialGrid.get_nearby_zombies()`

4. **Check projectile lifecycle:**
   - Are projectiles being removed before collision check?
   - Are projectiles hitting walls first?

### Test Results
- ✅ 164/174 tests passing (94.3%)
- ✅ 13/13 new quest trigger tests passing
- ❌ 10 pre-existing test failures (unrelated)

### Files Modified Today
- `src/game_engine.py` - Added ENTER/SPACE key quest triggering (lines 1722-1750)
- Created `tests/test_quest_trigger_keyboard.py` - All tests pass
- Created `tests/test_zombie_stuck_collision_bug.py` - Documents the bug
- Created `diagnose_collision_bug.py` - Diagnostic script
- Created `diagnose_collision_bounds.py` - Bounds diagnostic

### Next Steps for Claude

1. **Add comprehensive logging** to collision detection in `_update_playing()`
2. **Test in actual game** with logging enabled
3. **Check spatial grid** - verify zombies are being added and retrieved
4. **Verify visible_zombies filter** - ensure zombies aren't being excluded
5. **Check projectile-zombie distance** - maybe projectiles need to be closer?

### How to Reproduce
1. Launch game: `python3 src/main.py`
2. Enter any level (Sandbox recommended)
3. Shoot at zombies
4. Observe: Player collides with zombies, but projectiles pass through

### Expected Behavior
Projectiles should hit zombies and deal damage, just like player collision works.

### Actual Behavior
Projectiles pass through zombies without any collision detection.

---

**Note:** This is a CRITICAL bug that makes the game unplayable. Player cannot eliminate zombies, which is the core gameplay mechanic.
