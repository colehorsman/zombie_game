# CRITICAL BUGS - Live Testing Results

**Date:** November 24, 2025  
**Priority:** 🔴 HIGHEST - Block all other work  
**Status:** 3/4 FIXED ✅ | 1/4 INVESTIGATING 🔍

## Bug Report from Live Testing

### Bug #1: Pause Menu "Return to Lobby" Not Working
**Severity:** CRITICAL  
**Status:** ✅ FIXED  
**Description:** When pressing ESC and selecting "Return to Lobby" from pause menu, nothing happens  
**Tested In:**
- Sandbox level
- Production level

**Expected:** Should return player to lobby  
**Actual:** Menu selection does nothing

**Fix Applied:** Removed line that was restoring status to PLAYING before calling `_return_to_lobby()`

---

### Bug #2: Zombie Quarantine Not Working in Production
**Severity:** CRITICAL  
**Status:** 🔍 INVESTIGATING (Debug logging added)  
**Description:** Shooting zombies in production account does not quarantine them  
**Hypothesis:** Wrong scope being used for API call  
**Impact:** Core gameplay mechanic broken in production levels

**Expected:** Zombie eliminated → API quarantine call → zombie removed  
**Actual:** Zombies take damage but don't get quarantined

**Investigation Added:** Debug logging now shows identity ID, account, full scope, and root scope when quarantining

---

### Bug #3: Third Party Protection Takes 1 Hit Instead of 10
**Severity:** HIGH  
**Status:** ✅ FIXED  
**Description:** Third parties in lobby are immediately protected on first raygun hit  
**Location:** Lobby mode

**Expected:** Should take 10 hits to protect a third party  
**Actual:** Takes 1 hit - instant protection

**Fix Applied:** Updated lobby collision code to use health system with `take_damage()` and check `eliminated` flag

---

### Bug #4: Zombies Invulnerable After Hacker Challenge
**Severity:** CRITICAL  
**Status:** ✅ FIXED  
**Description:** After completing hacker challenge (Service Protection Quest), zombies become invulnerable - projectiles pass through them  
**Impact:** Cannot demonstrate zombie quarantine after quest completion

**Expected:** Zombies should remain vulnerable to raygun after quest  
**Actual:** Projectiles pass through zombies without collision

**Note:** Hacker challenge itself worked correctly!

**Fix Applied:** Added `previous_status` save before pausing for quest success messages (both hacker challenge and JIT quest)

---

---

### Bug #5: Third Party Blocking Shows "Failed to block" Error
**Severity:** HIGH  
**Status:** 🔍 INVESTIGATING  
**Description:** When shooting third party "Noops" 10 times, it appears to work but shows error message "Failed to block Noops"  
**Location:** Lobby mode

**Expected:** Third party blocked successfully with success message  
**Actual:** Third party blocked but error message displayed, glitchy behavior

**Investigation Needed:**
1. Check if API call actually succeeded despite error message
2. Verify error handling in `_block_third_party()` method
3. Check if third party name "Noops" causes issues
4. Review success/failure message logic

---

## QA Tester Responsibility

The automated tests passed but did NOT catch these critical runtime bugs. The QA Tester needs to:

1. ✅ Acknowledge these bugs exist in real gameplay
2. 🔴 Create regression tests for each bug
3. 🔴 Verify fixes don't break other functionality
4. 🔴 Test with REAL API calls, not just mocks

## Investigation Priority

1. **Bug #4** - Most critical (blocks demo)
2. **Bug #1** - Critical (blocks workflow)
3. **Bug #2** - Critical (core mechanic)
4. **Bug #3** - High (gameplay balance)

## Next Steps

1. Investigate pause menu execution logic
2. Check zombie collision detection after quest completion
3. Verify API scope usage in production accounts
4. Review third party health/hit counter logic
