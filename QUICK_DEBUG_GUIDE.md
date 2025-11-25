# Quick Debug Guide: Projectile Collision Bug

## Run Game with Logging
```bash
python3 src/main.py
```

## Test Steps
1. Enter Sandbox level (first door)
2. Shoot at zombies (SPACE or A button)
3. Watch console for logs

## What to Look For

### Scenario 1: No Zombies Visible
```
🔍 COLLISION CHECK: 1 projectiles vs 0 visible zombies (total: 5)
```
**Problem:** Zombies are being filtered out  
**Check:** `is_hidden` flags or `is_on_screen()` logic

### Scenario 2: Zombies Quarantining
```
Zombie[0]: ... is_quarantining=True
🎯 COLLISION RESULT: 0 collisions detected
```
**Problem:** Zombies stuck with quarantine flag  
**Check:** Where `is_quarantining` is set to True

### Scenario 3: No Collisions Despite Zombies Present
```
🔍 COLLISION CHECK: 1 projectiles vs 5 visible zombies
🎯 COLLISION RESULT: 0 collisions detected
```
**Problem:** Spatial grid or collision detection broken  
**Check:** `SpatialGrid.add_zombie()` and `get_nearby_zombies()`

### Scenario 4: No Logs at All
**Problem:** Collision check not running  
**Check:** Game state, projectile creation

## Files to Check
- `src/game_engine.py:1318-1345` - Collision detection with logging
- `src/collision.py:137-195` - Spatial grid collision logic
- `src/zombie.py:401-415` - Zombie bounds calculation

## Quick Fixes to Try

### Fix 1: Reset All Zombie Flags
Add to `_enter_level()` after loading zombies:
```python
for zombie in level_zombies:
    zombie.is_quarantining = False
    zombie.is_hidden = False
```

### Fix 2: Increase Projectile Size
In `src/projectile.py:26`:
```python
self.radius = 8  # Was 4, try 8
```

### Fix 3: Remove Zombie Collision Offset
In `src/zombie.py:49-50`:
```python
self.collision_offset_x = 0  # Was 6
self.collision_offset_y = 0  # Was 4
```

## Success Looks Like
```
🔍 COLLISION CHECK: 1 projectiles vs 5 visible zombies (total: 5)
  Projectile[0]: pos=(120.0, 400.0), bounds=<rect(116, 396, 8, 8)>
  Zombie[0]: pos=(150.0, 400.0), bounds=<rect(156, 404, 28, 32)>, is_quarantining=False
🎯 COLLISION RESULT: 1 collisions detected
Successfully quarantined TestZombie
```
