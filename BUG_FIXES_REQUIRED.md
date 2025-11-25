# Critical Bug Fixes Required

**Priority:** 🔴 HIGHEST - Block all other work  
**Date:** November 24, 2025

## Bug #1: Pause Menu "Return to Lobby" Not Working ✅ ROOT CAUSE FOUND

**File:** `src/game_engine.py`  
**Line:** 1392-1393  
**Method:** `_execute_pause_menu_option()`

### Root Cause
```python
elif selected_option == "Return to Lobby":
    # Return to lobby (only if in a level)
    if self.game_state.previous_status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
        self.game_state.congratulations_message = None
        self.game_state.status = self.game_state.previous_status  # ❌ BUG: Sets status BACK to PLAYING
        self._return_to_lobby()  # Then tries to return to lobby
```

The code sets `status` back to `previous_status` (PLAYING) BEFORE calling `_return_to_lobby()`, which then tries to transition from PLAYING to LOBBY. This causes a conflict.

### Fix
```python
elif selected_option == "Return to Lobby":
    # Return to lobby (only if in a level)
    if self.game_state.previous_status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
        self.game_state.congratulations_message = None
        # Don't restore status here - let _return_to_lobby() handle it
        self._return_to_lobby()
    else:
        # Already in lobby, just resume
        self.dismiss_message()
```

---

## Bug #2: Zombie Quarantine Not Working in Production ⚠️ NEEDS INVESTIGATION

**File:** `src/game_engine.py`  
**Method:** `_quarantine_zombie()`

### Hypothesis
Zombies in production account may not have correct scope set when loaded from API.

### Investigation Needed
1. Check if zombies in production have `zombie.scope` populated
2. Verify scope format matches expected pattern
3. Add logging to see what scope is being sent to API
4. Test with production account: 613056517323

### Debug Code to Add
```python
logger.info(f"Quarantining zombie: {zombie.identity_name}")
logger.info(f"  Account: {zombie.account}")
logger.info(f"  Scope: {zombie.scope}")
logger.info(f"  Root scope: {root_scope}")
```

---

## Bug #3: Third Party Protection Takes 1 Hit Instead of 10 ✅ ROOT CAUSE FOUND

**File:** `src/game_engine.py`  
**Line:** 760  
**Method:** `_update_lobby()`

### Root Cause
In lobby mode, the code calls `_block_third_party()` immediately on collision without checking health:

```python
# LOBBY collision code (WRONG)
if projectile.get_bounds().colliderect(third_party.get_bounds()):
    self._block_third_party(third_party)  # ❌ Immediate blocking, no health check
    if projectile in self.projectiles:
        self.projectiles.remove(projectile)
    break
```

Compare to LEVEL mode collision code (CORRECT):
```python
# LEVEL collision code (CORRECT)
for projectile, third_party in third_party_collisions:
    if projectile in self.projectiles:
        self.projectiles.remove(projectile)
    
    # Apply damage to third party
    eliminated = third_party.take_damage(projectile.damage)  # ✅ Uses health system
    
    # Only handle blocking if third party health reached 0
    if eliminated:
        self._handle_third_party_blocking(third_party)
```

### Fix
Replace lobby collision code (lines 755-764) with proper health-based system:

```python
# Check projectile collisions with third parties
if self.game_map and hasattr(self.game_map, 'third_parties'):
    for projectile in self.projectiles[:]:
        for third_party in self.game_map.third_parties[:]:
            if not third_party.is_blocking and not third_party.is_protected:
                if projectile.get_bounds().colliderect(third_party.get_bounds()):
                    # Remove projectile
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    
                    # Apply damage (third parties have 10 health)
                    eliminated = third_party.take_damage(projectile.damage)
                    
                    # Only block if health reaches 0
                    if eliminated:
                        self._block_third_party(third_party)
                    
                    break
```

---

## Bug #4: Zombies Invulnerable After Hacker Challenge ✅ ROOT CAUSE FOUND

**File:** `src/game_engine.py`  
**Line:** 502  
**Method:** `_try_protect_service()`

### Root Cause
When quest succeeds, the code sets status to PAUSED but doesn't save `previous_status`:

```python
# Stop hacker
self.hacker = None

# Pause game to show success message
self.game_state.status = GameStatus.PAUSED  # ❌ Doesn't save previous_status

# Show success message
self.game_state.congratulations_message = (...)
```

When player presses ENTER to dismiss, `dismiss_message()` tries to restore from `previous_status` which is None, causing issues with game state.

### Fix
Save `previous_status` before pausing:

```python
# Stop hacker
self.hacker = None

# Pause game to show success message
self.game_state.previous_status = self.game_state.status  # ✅ Save current status
self.game_state.status = GameStatus.PAUSED

# Show success message
self.game_state.congratulations_message = (...)
```

### Additional Investigation
The collision detection code at line 1233 checks:
```python
if self.game_state.status != GameStatus.BOSS_BATTLE:
```

This should allow collisions during PLAYING status. Need to verify that status is actually PLAYING after dismissing the quest success message.

---

## Fix Priority Order

1. **Bug #4** - Most critical (blocks demo completely)
2. **Bug #1** - Critical (blocks workflow)
3. **Bug #3** - High (gameplay balance, easy fix)
4. **Bug #2** - Critical (needs investigation first)

## Testing Plan

After fixes:
1. Test pause menu "Return to Lobby" from both Sandbox and Production
2. Test hacker challenge → dismiss message → shoot zombies
3. Test third party in lobby takes 10 hits
4. Test zombie quarantine in production account with logging

## QA Tester Action Items

1. Create regression tests for each bug
2. Test fixes don't break existing functionality
3. Verify with REAL gameplay, not just mocks
4. Add logging to catch similar issues in future
