# Bug Fix: Projectiles Not Hitting Zombies After Quest Completion

## Problem

**Critical Bug:** After completing the hacker challenge (Service Protection Quest) in Sandbox level, projectiles go right through all zombies. Players cannot eliminate any zombies after the quest completes.

## Root Cause (Updated)

**Primary Issue: Spatial Grid Dimensions Mismatch**

The spatial grid (used for efficient O(n) collision detection) was created once during `GameEngine.__init__` with **lobby map dimensions** (e.g., 3600x2700 pixels). When entering a platformer level, the map dimensions change significantly (can be up to 27,200px wide for 512 zombies), but the spatial grid was **never recreated**.

This caused collision detection to fail for zombies positioned beyond the original grid boundaries:
- Grid cell calculation: `zombie_x / cell_size` = `5000 / 50` = `100`
- But grid only has `72` columns (for 3600px width)
- The `range(min_col, max_col + 1)` loop becomes `range(100, 72)` which is **empty**
- Zombie is never added to any collision cell → projectile passes through

**Secondary Issue: Flag Reset Inconsistency**

The original partial fix reset `is_quarantining` but the `_handle_quest_failure` path didn't reset `is_hidden`, causing inconsistent state.

## Solution

### Fix 1: Recreate Spatial Grid on Level Transitions (Primary Fix)

Added spatial grid recreation in both `_enter_level` and `_return_to_lobby`:

```python
# In _enter_level (around line 903)
self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
logger.info(f"✅ Spatial grid recreated for level: {self.game_map.map_width}x{self.game_map.map_height}")

# In _return_to_lobby (around line 1062)
self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
logger.info(f"✅ Spatial grid recreated for lobby: {self.game_map.map_width}x{self.game_map.map_height}")
```

### Fix 2: Quest Completion Flag Reset (Original Partial Fix)

Reset `is_quarantining` and `is_hidden` flags on quest completion.

### Files Modified

**`src/game_engine.py`:**

1. **`_enter_level()` method (around line 903):**
   - **NEW:** Recreate spatial grid with platformer level dimensions

2. **`_return_to_lobby()` method (around line 1062):**
   - **NEW:** Recreate spatial grid with lobby dimensions

3. **`_try_protect_service()` method (line 520-540):**
   - Reset `is_quarantining` AND `is_hidden` flags before pausing game
   - Added debug logging to track zombie states

4. **`_handle_quest_failure()` method (line 475-495):**
   - Reset `is_quarantining` flags before pausing game
   - Added `previous_status` save (was missing, causing restore issues)
   - Added debug logging to track zombie states

## Testing

Comprehensive test suite in `tests/test_quest_collision_bug_fix.py`:

### Test Coverage

**Quest Flag Reset Tests:**
1. ✅ **test_zombies_not_quarantining_before_quest** - Verifies initial state
2. ✅ **test_zombies_visible_before_quest** - Verifies zombies are visible
3. ✅ **test_quest_completion_resets_quarantine_flags** - Verifies flag reset works
4. ✅ **test_collision_detection_works_after_quest_success** - End-to-end success scenario
5. ✅ **test_collision_detection_works_after_quest_failure** - End-to-end failure scenario

**Spatial Grid Recreation Tests:**
6. ✅ **test_spatial_grid_covers_level_width** - Verifies grid exists with valid dimensions
7. ✅ **test_collision_detection_for_distant_zombies** - Collision works at large X coordinates
8. ✅ **test_undersized_grid_misses_distant_zombies** - Documents edge case behavior

### Test Results

```
tests/test_quest_collision_bug_fix.py - 8 passed in 0.59s
```

## Verification

The fix ensures that:

1. Spatial grid is properly sized for the current map (lobby or level)
2. Zombies at any X coordinate can be hit by projectiles
3. When quest completes (success or failure), zombie flags are reset
4. Collision detection works normally after dismissing messages
5. Players can continue eliminating zombies after the quest
6. Debug logging helps identify if the issue occurs again

## Impact

- **Severity:** Critical (game-breaking)
- **Affected:** All platformer levels, especially Sandbox and Production with quests
- **Status:** ✅ **FIXED**
- **Tests:** ✅ **8 tests (5 original + 3 new)**
- **Regression:** ✅ **No existing tests broken**

## Deployment

Ready for immediate deployment. The fix addresses:
1. Root cause: Spatial grid dimensions mismatch
2. Secondary cause: Inconsistent flag reset on quest completion
