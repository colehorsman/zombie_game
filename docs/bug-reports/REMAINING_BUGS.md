# Remaining Bugs - November 24, 2025

## Critical Issues Still Present

### Bug #6: Start Button (Pause) Not Working in Level
**Severity:** HIGH  
**Status:** 🔴 BROKEN  
**Description:** Controller Start button (button 7) does not pause the game when in a level  
**Expected:** Start button should show pause menu  
**Actual:** Nothing happens

**Investigation Needed:**
- Verify controller button number (may not be button 7)
- Add logging to see what button is actually pressed
- Test with keyboard ESC key to confirm pause menu works

---

### Bug #7: JIT Quest Not Appearing in Production Data
**Severity:** CRITICAL  
**Status:** 🔴 BROKEN  
**Description:** JIT Access Quest does not appear in Production Data account (160224865296)  
**Expected:** 
- Dialogue: "An auditor found elevated access in your production account - find the Administrator access and apply Just-In-Time protection to prevent a significant deficiency"
- Auditor character visible
- Admin roles with crowns visible

**Actual:** No quest, no auditor, no admin roles

**Investigation Needed:**
- Check if `_initialize_jit_quest()` is being called for Production Data
- Verify Production Data account ID is in `JIT_QUEST_ACCOUNTS`
- Check if API returns admin/privileged permission sets
- Add logging to JIT quest initialization

---

### Bug #8: Return to Lobby Closes Game
**Severity:** CRITICAL  
**Status:** 🔴 BROKEN (Regression - fix didn't work)  
**Description:** Selecting "Return to Lobby" from pause menu appears to close the game instead of returning to lobby  
**Expected:** Player returns to lobby, can enter other levels  
**Actual:** Game closes/crashes

**Investigation Needed:**
- Check if `_return_to_lobby()` is crashing
- Add error handling and logging
- Verify game state transitions correctly
- Check if there's an exception being thrown

---

## Fixed Bugs (Confirmed Working)

✅ **Bug #1** - Pause menu "Return to Lobby" code fixed (but still broken - see Bug #8)  
✅ **Bug #2** - Zombie quarantine in production - WORKING  
✅ **Bug #3** - Third party takes 10 hits - FIXED  
✅ **Bug #4** - Zombies invulnerable after quest - FIXED  
✅ **Controller hot-plug** - FIXED

---

## Priority Order

1. **Bug #8** - Return to Lobby (blocks testing workflow)
2. **Bug #7** - JIT Quest not appearing (blocks demo)
3. **Bug #6** - Start button pause (UX issue)
4. **Bug #5** - Third party "Noops" error (still investigating)

---

## Next Steps

1. Add comprehensive logging to:
   - `_return_to_lobby()` method
   - `_initialize_jit_quest()` method
   - Controller button press events
2. Restart game and test each bug systematically
3. Check logs for errors/exceptions
4. Fix issues one by one
