# Arcade Mode Test Scenarios

## Overview
Comprehensive testing scenarios for Arcade Mode gameplay, mechanics, and progression.

**Test Date:** November 28, 2024
**Tester:** [Your Name]
**Build:** v2.0 (Hybrid Mode)

---

## Pre-Test Setup

### Environment Check
- [ ] Game launches without errors
- [ ] 60 FPS in lobby
- [ ] Controller connected (if testing controller)
- [ ] Audio working (if implemented)

### Cheat Codes Available
- `UNLOCK` - Unlock all levels
- `GOD` - God mode (invincibility)
- `SPEED` - Increase player speed
- `AMMO` - Unlimited ammo
- `ARCADE` - Toggle arcade mode

---

## Test Scenario 1: Arcade Mode Entry

### Objective
Verify arcade mode can be entered and initialized correctly

### Steps
1. Launch game
2. Enter lobby
3. Type `ARCADE` cheat code
4. Observe transition

### Expected Results
- [ ] Arcade mode activates immediately
- [ ] Screen transitions to arcade gameplay
- [ ] HUD shows arcade-specific elements (score, combo, wave)
- [ ] Zombies begin spawning
- [ ] Player can move and shoot

### Pass/Fail Criteria
**PASS:** All expected results met
**FAIL:** Any crash, freeze, or missing element

### Notes
```
[Record observations here]
```

---

## Test Scenario 2: Basic Gameplay Loop

### Objective
Verify core arcade mechanics work correctly

### Steps
1. Enter arcade mode
2. Eliminate 10 zombies
3. Observe score increases
4. Check combo system
5. Survive 1 minute

### Expected Results
- [ ] Zombies spawn continuously
- [ ] Score increases per elimination (+100 base)
- [ ] Combo counter increments
- [ ] Combo multiplier applies (1.5x at 5+ combo)
- [ ] Wave counter increments
- [ ] Difficulty increases over time

### Metrics to Record
- Score after 1 minute: _______
- Highest combo achieved: _______
- Wave reached: _______
- Zombies eliminated: _______
- FPS average: _______

### Pass/Fail Criteria
**PASS:** All mechanics functional, 60 FPS maintained
**FAIL:** Crashes, freezes, or FPS < 30

### Notes
```
[Record observations here]
```

---

## Test Scenario 3: Combo System

### Objective
Verify combo mechanics and multipliers work correctly

### Steps
1. Enter arcade mode
2. Eliminate zombies rapidly (< 3 seconds between kills)
3. Build combo to 5+
4. Observe multiplier activation
5. Let combo expire (no kills for 3+ seconds)
6. Rebuild combo

### Expected Results
- [ ] Combo increments on each elimination
- [ ] 1.5x multiplier activates at 5+ combo
- [ ] Visual feedback shows multiplier (color change, text)
- [ ] Combo resets after 3 seconds of no eliminations
- [ ] Score reflects multiplier correctly

### Test Cases

**Case 1: Build Combo**
- Eliminate 5 zombies rapidly
- Expected: Combo = 5, Multiplier = 1.5x
- Score per kill: 150 (100 × 1.5)

**Case 2: Maintain Combo**
- Keep eliminating within 3 seconds
- Expected: Combo continues incrementing
- Multiplier stays active

**Case 3: Combo Expiration**
- Stop eliminating for 3+ seconds
- Expected: Combo resets to 0
- Multiplier deactivates

### Pass/Fail Criteria
**PASS:** All combo mechanics work as expected
**FAIL:** Combo doesn't increment, multiplier doesn't apply, or timing incorrect

### Notes
```
[Record observations here]
```

---

## Test Scenario 4: Difficulty Scaling

### Objective
Verify difficulty increases appropriately over time

### Steps
1. Enter arcade mode
2. Survive for 5 minutes
3. Observe spawn rate changes
4. Note zombie speed changes
5. Track wave progression

### Expected Results
- [ ] Spawn rate increases every 30 seconds
- [ ] Zombie speed increases gradually
- [ ] Wave number increments
- [ ] Game becomes progressively harder
- [ ] Performance remains stable (60 FPS)

### Metrics to Record

**Minute 1:**
- Zombies on screen: _______
- Spawn rate (zombies/sec): _______
- Zombie speed: _______

**Minute 3:**
- Zombies on screen: _______
- Spawn rate (zombies/sec): _______
- Zombie speed: _______

**Minute 5:**
- Zombies on screen: _______
- Spawn rate (zombies/sec): _______
- Zombie speed: _______

### Pass/Fail Criteria
**PASS:** Noticeable difficulty increase, stable performance
**FAIL:** No difficulty change, or performance degrades

### Notes
```
[Record observations here]
```

---

## Test Scenario 5: Death and Game Over

### Objective
Verify death mechanics and game over screen

### Steps
1. Enter arcade mode
2. Allow zombies to touch player
3. Observe health decrease
4. Die (health reaches 0)
5. View results screen

### Expected Results
- [ ] Player takes damage on zombie contact
- [ ] Health bar decreases visually
- [ ] Player dies at 0 health
- [ ] Game over screen appears
- [ ] Results show: score, zombies eliminated, time survived, highest combo
- [ ] Option to return to lobby or retry

### Results Screen Should Show
- Final Score: _______
- Zombies Eliminated: _______
- Time Survived: _______
- Highest Combo: _______
- Waves Completed: _______

### Pass/Fail Criteria
**PASS:** Death mechanics work, results screen displays correctly
**FAIL:** Crash on death, missing results, or can't exit

### Notes
```
[Record observations here]
```

---

## Test Scenario 6: Performance Under Load

### Objective
Verify game maintains 60 FPS with many entities

### Steps
1. Enter arcade mode
2. Use `GOD` cheat for invincibility
3. Survive 10+ minutes
4. Allow zombie count to build up
5. Monitor FPS

### Expected Results
- [ ] FPS stays at 60 with 100+ zombies
- [ ] FPS stays above 30 with 200+ zombies
- [ ] No crashes or freezes
- [ ] Collision detection still works
- [ ] Input remains responsive

### Metrics to Record
- Max zombies on screen: _______
- FPS at max zombies: _______
- Memory usage: _______
- Any lag or stuttering: _______

### Pass/Fail Criteria
**PASS:** 60 FPS with 100+ zombies, > 30 FPS with 200+
**FAIL:** FPS < 30 with < 100 zombies, or crashes

### Notes
```
[Record observations here]
```

---

## Test Scenario 7: Controller Support

### Objective
Verify controller works in arcade mode

### Steps
1. Connect controller
2. Enter arcade mode
3. Test all controls:
   - Movement (left stick)
   - Shooting (A button)
   - Pause (Start button)
   - Exit (B button)

### Expected Results
- [ ] Left stick moves player smoothly
- [ ] A button shoots projectiles
- [ ] Start button pauses game
- [ ] B button exits to lobby
- [ ] No input lag
- [ ] Dead zones work correctly

### Pass/Fail Criteria
**PASS:** All controls responsive and accurate
**FAIL:** Any control doesn't work or has significant lag

### Notes
```
[Record observations here]
```

---

## Test Scenario 8: Pause and Resume

### Objective
Verify pause functionality works correctly

### Steps
1. Enter arcade mode
2. Play for 30 seconds
3. Pause game (ESC or Start button)
4. Wait 10 seconds
5. Resume game
6. Continue playing

### Expected Results
- [ ] Game pauses immediately
- [ ] All entities freeze
- [ ] Timer stops
- [ ] Pause menu appears
- [ ] Can resume without issues
- [ ] Score/combo preserved
- [ ] No entities moved during pause

### Pass/Fail Criteria
**PASS:** Pause/resume works flawlessly
**FAIL:** Game doesn't pause, or state corrupted on resume

### Notes
```
[Record observations here]
```

---

## Test Scenario 9: Exit to Lobby

### Objective
Verify can exit arcade mode cleanly

### Steps
1. Enter arcade mode
2. Play for 1 minute
3. Exit to lobby (ESC → Exit, or B button)
4. Observe transition
5. Re-enter arcade mode

### Expected Results
- [ ] Clean exit to lobby
- [ ] No crashes or errors
- [ ] Lobby state preserved
- [ ] Can re-enter arcade mode
- [ ] New arcade session starts fresh

### Pass/Fail Criteria
**PASS:** Clean exit and re-entry
**FAIL:** Crash, freeze, or corrupted state

### Notes
```
[Record observations here]
```

---

## Test Scenario 10: Edge Cases

### Objective
Test unusual scenarios and edge cases

### Test Cases

**Case 1: Rapid Mode Switching**
1. Enter arcade mode
2. Immediately exit
3. Re-enter
4. Repeat 5 times
- Expected: No crashes, clean transitions

**Case 2: Zero Zombies**
1. Enter arcade mode
2. Eliminate all zombies before new spawn
3. Observe behavior
- Expected: New zombies spawn, no crash

**Case 3: Maximum Score**
1. Use cheats to survive long time
2. Build very high score (1,000,000+)
3. Check score display
- Expected: Score displays correctly, no overflow

**Case 4: Combo Overflow**
1. Build combo to 100+
2. Check multiplier
3. Check score calculation
- Expected: Multiplier caps or continues correctly

### Pass/Fail Criteria
**PASS:** All edge cases handled gracefully
**FAIL:** Any crash or undefined behavior

### Notes
```
[Record observations here]
```

---

## Test Summary

### Overall Results

**Total Scenarios:** 10
**Passed:** _______
**Failed:** _______
**Blocked:** _______

### Critical Issues Found
```
[List any critical bugs or issues]
```

### Minor Issues Found
```
[List any minor bugs or polish items]
```

### Performance Summary
- Average FPS: _______
- Lowest FPS: _______
- Max zombies handled: _______
- Memory usage: _______

### Recommendations
```
[Suggestions for improvements]
```

---

## Sign-Off

**Tester:** _______________________
**Date:** _______________________
**Build Tested:** _______________________
**Status:** ☐ Ready for Demo  ☐ Needs Work  ☐ Blocked

---

*Use this document to systematically test arcade mode and ensure it's demo-ready for re:Invent and Kiroween submission.*
