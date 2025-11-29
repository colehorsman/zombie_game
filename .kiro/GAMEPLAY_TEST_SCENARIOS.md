# Gameplay Test Scenarios - Pre-re:Invent Testing

**Date:** November 28, 2024
**Tester:** Cole
**Duration:** 3 days (Nov 28-30)
**Goal:** Ensure flawless experience for re:Invent attendees
**Prepared by:** QA Agent, UX Agent, Product Manager, Sonrai Agent

---

## 🎯 Testing Objectives

1. **Validate all core gameplay mechanics**
2. **Verify controller support is flawless**
3. **Test all cheat codes work correctly**
4. **Ensure quests function properly**
5. **Validate Sonrai API integration**
6. **Check performance (60 FPS target)**
7. **Identify any UX issues**
8. **Find and document bugs**

---

## Test Scenario Format

Each scenario includes:
- **Scenario ID** - Unique identifier
- **Feature** - What you're testing
- **Steps** - Exact actions to perform
- **Success Criteria** - What should happen
- **Notes** - Space for your observations

---

## 🎮 Test Scenarios

### Category 1: Controller & Input (QA Agent)

#### TC-001: Controller Connection
**Feature:** Bluetooth controller pairing
**Priority:** Critical

**Steps:**
1. Turn on 8BitDo controller
2. Launch game
3. Press any button on controller
4. Navigate menus with D-pad

**Success Criteria:**
- ✅ Controller detected automatically
- ✅ D-pad navigation works in all menus
- ✅ Button mappings correct (A=shoot, B=jump, etc.)
- ✅ No input lag
- ✅ Vibration works (if supported)

**Notes:**
```
Controller Model: _______________
Connection Time: _______________
Issues Found: _______________
```

---

#### TC-002: Controller Gameplay
**Feature:** Controller during active gameplay
**Priority:** Critical

**Steps:**
1. Connect controller
2. Enter any level
3. Test all controls:
   - Left stick: Movement
   - A button: Shoot
   - B button: Jump
   - X button: Interact
   - Y button: Special
   - Start: Pause
   - Select: Menu

**Success Criteria:**
- ✅ All buttons respond instantly
- ✅ Movement feels smooth
- ✅ Shooting is responsive
- ✅ Jumping works consistently
- ✅ Pause menu accessible
- ✅ No dropped inputs

**Notes:**
```
Responsiveness (1-10): _______________
Issues Found: _______________
```

---

### Category 2: Cheat Codes (QA Agent + Product Manager)

#### TC-003: UNLOCK Cheat Code
**Feature:** Unlock all levels
**Priority:** High

**Steps:**
1. Start game in lobby
2. Type "UNLOCK" (keyboard)
3. Check all doors

**Success Criteria:**
- ✅ All account doors become accessible
- ✅ No error messages
- ✅ Can enter any level
- ✅ Cheat code message appears

**Notes:**
```
Doors unlocked: _______________
Issues: _______________
```

---

#### TC-004: GODMODE Cheat Code
**Feature:** Invincibility
**Priority:** High

**Steps:**
1. Enter any level
2. Type "GODMODE"
3. Walk into zombies
4. Let zombies attack you

**Success Criteria:**
- ✅ No damage taken
- ✅ Health stays at maximum
- ✅ Can walk through zombies
- ✅ Cheat code indicator visible

**Notes:**
```
Invincibility working: _______________
Issues: _______________
```

---

#### TC-005: AMMO Cheat Code
**Feature:** Unlimited ammo
**Priority:** Medium

**Steps:**
1. Enter any level
2. Type "AMMO"
3. Shoot continuously
4. Check ammo counter

**Success Criteria:**
- ✅ Ammo never depletes
- ✅ Can shoot indefinitely
- ✅ No reload needed
- ✅ Cheat code indicator visible

**Notes:**
```
Unlimited ammo working: _______________
Issues: _______________
```

---

#### TC-006: SPEED Cheat Code
**Feature:** Increased movement speed
**Priority:** Medium

**Steps:**
1. Enter any level
2. Note normal movement speed
3. Type "SPEED"
4. Move around

**Success Criteria:**
- ✅ Movement noticeably faster
- ✅ Still controllable
- ✅ No collision issues
- ✅ Can toggle off

**Notes:**
```
Speed increase noticeable: _______________
Issues: _______________
```

---

### Category 3: Arcade Mode (Product Manager + UX Agent)

#### TC-007: Arcade Mode Start
**Feature:** Arcade mode initialization
**Priority:** Critical

**Steps:**
1. From lobby, type "ARCADE"
2. Observe transition
3. Check HUD elements

**Success Criteria:**
- ✅ Smooth transition to arcade mode
- ✅ Score counter visible
- ✅ Wave counter visible
- ✅ Combo multiplier visible
- ✅ Timer visible
- ✅ Background music changes

**Notes:**
```
Transition smooth: _______________
HUD complete: _______________
Issues: _______________
```

---

#### TC-008: Arcade Mode Progression
**Feature:** Wave system and difficulty scaling
**Priority:** Critical

**Steps:**
1. Start arcade mode
2. Complete Wave 1
3. Complete Wave 2
4. Complete Wave 3
5. Observe difficulty increase

**Success Criteria:**
- ✅ Waves progress automatically
- ✅ Zombie count increases each wave
- ✅ Spawn rate increases
- ✅ Difficulty feels balanced
- ✅ No performance issues
- ✅ Wave transition clear

**Notes:**
```
Wave 1 zombies: _______________
Wave 2 zombies: _______________
Wave 3 zombies: _______________
Difficulty curve: _______________
FPS maintained: _______________
Issues: _______________
```

---

#### TC-009: Arcade Mode Combo System
**Feature:** Combo multiplier mechanics
**Priority:** High

**Steps:**
1. Start arcade mode
2. Eliminate zombies rapidly
3. Watch combo counter
4. Let combo expire
5. Build combo again

**Success Criteria:**
- ✅ Combo counter increases with rapid kills
- ✅ Multiplier applies to score
- ✅ Visual feedback on combo
- ✅ Combo expires after delay
- ✅ Audio feedback (if implemented)

**Notes:**
```
Max combo reached: _______________
Multiplier working: _______________
Visual feedback clear: _______________
Issues: _______________
```

---

#### TC-010: Arcade Mode Results Screen
**Feature:** End-of-game statistics
**Priority:** High

**Steps:**
1. Play arcade mode until game over
2. View results screen
3. Check all stats displayed

**Success Criteria:**
- ✅ Final score displayed
- ✅ Zombies eliminated count
- ✅ Highest wave reached
- ✅ Max combo displayed
- ✅ Time survived shown
- ✅ Can return to lobby
- ✅ Can restart arcade mode

**Notes:**
```
All stats visible: _______________
Navigation working: _______________
Issues: _______________
```

---

### Category 4: Boss Battles (Product Vision + UX Agent)

#### TC-011: Boss Spawn
**Feature:** Boss battle initialization
**Priority:** High

**Steps:**
1. Enter production account
2. Eliminate all zombies
3. Wait for boss spawn
4. Observe boss entrance

**Success Criteria:**- ✅ Boss sp
awns after clearing level
- ✅ Boss entrance animation plays
- ✅ Boss health bar appears
- ✅ Boss music starts (if implemented)
- ✅ Boss has distinct appearance
- ✅ Warning message appears

**Notes:**
```
Boss spawn timing: _______________
Visual impact: _______________
Issues: _______________
```

---

#### TC-012: Boss Combat
**Feature:** Boss battle mechanics
**Priority:** High

**Steps:**
1. Engage boss in combat
2. Shoot boss multiple times
3. Observe boss attacks
4. Dodge boss attacks
5. Defeat boss

**Success Criteria:**
- ✅ Boss takes damage from projectiles
- ✅ Boss health bar decreases
- ✅ Boss attacks player
- ✅ Boss attacks are telegraphed
- ✅ Boss defeat triggers victory
- ✅ Rewards granted on victory

**Notes:**
```
Boss difficulty: _______________
Attack patterns clear: _______________
Victory satisfying: _______________
Issues: _______________
```

---

### Category 5: Quest Systems (Sonrai Agent + Product Manager)

#### TC-013: Service Protection Quest
**Feature:** Third-party protection race
**Priority:** Critical

**Steps:**
1. Enter production account
2. Locate Service Protection Quest
3. Find hacker entity (red)
4. Race to eliminate third parties
5. Complete quest

**Success Criteria:**
- ✅ Quest appears in correct accounts
- ✅ Hacker spawns and moves
- ✅ Third parties visible
- ✅ Can eliminate third parties
- ✅ Hacker eliminates if reached first
- ✅ Quest success/failure clear
- ✅ API calls succeed (check logs)

**Notes:**
```
Quest triggered: _______________
Hacker behavior: _______________
API integration: _______________
Issues: _______________
```

---

#### TC-014: JIT Access Quest
**Feature:** Just-in-time access protection
**Priority:** Critical

**Steps:**
1. Enter production account
2. Locate JIT Access Quest
3. Find auditor entity (blue)
4. Find admin roles (crowns)
5. Touch roles to protect them
6. Complete before auditor finds unprotected role

**Success Criteria:**
- ✅ Quest appears in correct accounts
- ✅ Auditor spawns and patrols
- ✅ Admin roles visible with crowns
- ✅ Touching role applies protection
- ✅ Shield appears on protected roles
- ✅ Quest success/failure clear
- ✅ API calls succeed (check logs)

**Notes:**
```
Quest triggered: _______________
Auditor behavior: _______________
Visual feedback: _______________
API integration: _______________
Issues: _______________
```

---

### Category 6: Sonrai API Integration (Sonrai Agent)

#### TC-015: Zombie Elimination API Call
**Feature:** Quarantine identity on elimination
**Priority:** Critical

**Steps:**
1. Enter any level with zombies
2. Eliminate a zombie
3. Check console logs for API call
4. Verify quarantine succeeded

**Success Criteria:**
- ✅ API call triggered on elimination
- ✅ Correct SRN sent to API
- ✅ Quarantine succeeds (200 response)
- ✅ No errors in logs
- ✅ Game continues smoothly

**Notes:**
```
API response time: _______________
Success rate: _______________
Issues: _______________
```

---

#### TC-016: API Error Handling
**Feature:** Graceful degradation on API failure
**Priority:** High

**Steps:**
1. Temporarily break API credentials
2. Launch game
3. Try to enter level
4. Eliminate zombie
5. Observe behavior

**Success Criteria:**
- ✅ Game doesn't crash
- ✅ Error logged to console
- ✅ User-friendly message (if implemented)
- ✅ Can still play game
- ✅ Can retry after fixing

**Notes:**
```
Error handling: _______________
User experience: _______________
Issues: _______________
```

---

### Category 7: Performance (Architecture Agent + Operations Agent)

#### TC-017: FPS Stability
**Feature:** 60 FPS target maintenance
**Priority:** Critical

**Steps:**
1. Enter level with many zombies
2. Play for 5 minutes
3. Monitor FPS counter
4. Note any drops

**Success Criteria:**
- ✅ Maintains 60 FPS with 100+ zombies
- ✅ Stays above 30 FPS with 200+ zombies
- ✅ No stuttering or freezing
- ✅ Smooth gameplay throughout

**Notes:**
```
Average FPS: _______________
Lowest FPS: _______________
Max zombies on screen: _______________
Issues: _______________
```

---

#### TC-018: Memory Usage
**Feature:** Memory leak prevention
**Priority:** High

**Steps:**
1. Play game for 30 minutes
2. Enter/exit multiple levels
3. Use various features
4. Monitor memory usage

**Success Criteria:**
- ✅ Memory usage stable
- ✅ No continuous growth
- ✅ Proper cleanup on level exit
- ✅ No crashes from memory issues

**Notes:**
```
Starting memory: _______________
After 30 min: _______________
Memory leaks detected: _______________
Issues: _______________
```

---

### Category 8: User Experience (UX Agent)

#### TC-019: First-Time User Experience
**Feature:** New player onboarding
**Priority:** Critical

**Steps:**
1. Launch game fresh (no save data)
2. Navigate lobby
3. Enter first level
4. Play for 5 minutes
5. Note any confusion

**Success Criteria:**
- ✅ Controls are intuitive
- ✅ Objectives are clear
- ✅ Visual feedback is obvious
- ✅ No confusion about what to do
- ✅ Tutorial helpful (if implemented)

**Notes:**
```
Clarity (1-10): _______________
Confusion points: _______________
Suggestions: _______________
```

---

#### TC-020: Visual Clarity
**Feature:** UI/UX readability
**Priority:** High

**Steps:**
1. Play game in various lighting conditions
2. Check all UI elements
3. Verify text readability
4. Check color contrast

**Success Criteria:**
- ✅ All text readable
- ✅ Icons clear and distinct
- ✅ Health bar visible
- ✅ Score/stats easy to read
- ✅ Quest objectives clear
- ✅ Color-blind friendly (if implemented)

**Notes:**
```
Readability (1-10): _______________
Problem areas: _______________
Suggestions: _______________
```

---

### Category 9: Edge Cases (QA Agent)

#### TC-021: Rapid Level Switching
**Feature:** State management on quick transitions
**Priority:** Medium

**Steps:**
1. Enter level
2. Immediately exit
3. Re-enter same level
4. Repeat 5 times

**Success Criteria:**
- ✅ No crashes
- ✅ Clean transitions
- ✅ State resets properly
- ✅ No memory leaks
- ✅ Performance stable

**Notes:**
```
Crashes: _______________
State issues: _______________
Performance: _______________
```

---

#### TC-022: Maximum Entity Stress Test
**Feature:** Entity limit handling
**Priority:** Medium

**Steps:**
1. Use GOD mode
2. Let zombies accumulate
3. Reach 500+ entities
4. Continue playing

**Success Criteria:**
- ✅ Game handles 500+ entities
- ✅ FPS stays above 30
- ✅ Collision detection works
- ✅ No crashes
- ✅ Entity cap enforced (if implemented)

**Notes:**
```
Max entities reached: _______________
FPS at max: _______________
Issues: _______________
```

---

## 📊 Test Summary Template

### Session Information
**Date:** _______________
**Duration:** _______________
**Build Version:** _______________
**Platform:** _______________
**Controller:** _______________

### Results Overview
**Total Tests:** 22
**Passed:** _______
**Failed:** _______
**Blocked:** _______
**Pass Rate:** _______%

### Critical Issues (P0)
```
[List any game-breaking bugs]
```

### High Priority Issues (P1)
```
[List important bugs that should be fixed]
```

### Medium Priority Issues (P2)
```
[List nice-to-have fixes]
```

### Performance Metrics
- **Average FPS:** _______
- **Lowest FPS:** _______
- **Max Entities:** _______
- **Memory Usage:** _______
- **API Success Rate:** _______

### UX Feedback
**What worked well:**
```
[Positive observations]
```

**What needs improvement:**
```
[Areas for enhancement]
```

**Suggestions:**
```
[Ideas for improvements]
```

---

## 🎯 Demo Readiness Checklist

### Core Gameplay
- [ ] Controller support flawless
- [ ] Movement smooth and responsive
- [ ] Combat feels good
- [ ] 60 FPS maintained
- [ ] No critical bugs

### Quest Systems
- [ ] Service Protection Quest works
- [ ] JIT Access Quest works
- [ ] Visual feedback clear
- [ ] API integration solid
- [ ] Success/failure obvious

### Polish
- [ ] Visual effects polished
- [ ] Audio working (if implemented)
- [ ] UI clean and readable
- [ ] Transitions smooth
- [ ] No placeholder art

### Sonrai Integration
- [ ] API calls succeed
- [ ] Error handling graceful
- [ ] Real data displays correctly
- [ ] Quarantine actions work
- [ ] Third-party blocking works

### Overall Assessment
**Ready for re:Invent:** ☐ Yes  ☐ No  ☐ With Fixes

**Confidence Level (1-10):** _______

**Blocker Issues:** _______

---

## 📝 Daily Testing Log

### Day 1 (Nov 28)
**Focus:** Controller + Core Gameplay
**Tests Completed:** _______
**Issues Found:** _______
**Notes:**
```
[Daily observations]
```

### Day 2 (Nov 29)
**Focus:** Quests + API Integration
**Tests Completed:** _______
**Issues Found:** _______
**Notes:**
```
[Daily observations]
```

### Day 3 (Nov 30)
**Focus:** Performance + Polish
**Tests Completed:** _______
**Issues Found:** _______
**Notes:**
```
[Daily observations]
```

---

## 🚀 Final Sign-Off

**Tester:** _______________________
**Date:** _______________________
**Status:** ☐ Ready for Demo  ☐ Needs Work  ☐ Blocked

**Recommendation:**
```
[Final assessment and recommendation]
```

---

*This comprehensive test plan ensures Sonrai Zombie Blaster is demo-ready for re:Invent and submission-ready for Kiroween. Test systematically, document thoroughly, and have fun!* 🎮👾
