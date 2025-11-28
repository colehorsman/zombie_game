# Gameplay Testing Guide - Sprint 1 Features

**Date**: 2025-11-28
**Focus**: Player Damage System & Health Mechanics
**Duration**: Morning session before Sprint 2 kickoff

---

## 🎯 Testing Objectives

1. **Validate Sprint 1 Features** - Ensure all damage mechanics work as designed
2. **Educational Impact** - Verify features teach security concepts effectively
3. **Balance & Feel** - Assess if gameplay is fun and fair
4. **Bug Discovery** - Find any issues before Sprint 2
5. **Performance** - Confirm 60 FPS maintained

---

## 🧪 Test Scenarios

### Scenario 1: Basic Damage System

**Test**: Player takes damage from zombies

**Steps**:
1. Launch game: `python3 src/main.py`
2. Use UNLOCK cheat code to access levels
3. Enter any level with zombies
4. Allow zombie to touch player

**Expected Results**:
- ✅ Player takes 1 HP damage
- ✅ Hearts UI updates (full → half or half → empty)
- ✅ Player sprite flashes (invincibility frames)
- ✅ 1.5s invincibility after hit
- ✅ Cannot take damage during invincibility

**Educational Check**:
- Does damage feel meaningful?
- Is visual feedback clear?
- Does invincibility prevent frustration?

---

### Scenario 2: Zombie Respawn on Damage

**Test**: Damage causes zombies to respawn (normal mode)

**Steps**:
1. Enter level and eliminate 5 zombies
2. Note zombie count
3. Take damage from remaining zombie
4. Observe zombie count

**Expected Results**:
- ✅ 1 previously eliminated zombie respawns
- ✅ Respawned zombie appears in level
- ✅ Teaches "security incidents undo work"

**Educational Check**:
- Is the consequence clear?
- Does it feel fair?
- Does it teach the intended lesson?

---

### Scenario 3: Death and Level Restart

**Test**: 0 HP triggers level restart

**Steps**:
1. Enter level
2. Eliminate several zombies
3. Take damage until health reaches 0
4. Observe what happens

**Expected Results**:
- ✅ All zombies respawn
- ✅ Player returns to start position
- ✅ Level resets completely
- ✅ Hearts UI shows full health (10 HP)

**Educational Check**:
- Does death feel like a significant failure?
- Is the reset fair?
- Does it motivate better play?

---

### Scenario 4: Arcade Mode Damage

**Test**: Damage in arcade mode (if implemented)

**Steps**:
1. Use Konami code to trigger arcade mode
2. Start arcade challenge
3. Take damage from zombie

**Expected Results**:
- ✅ Player takes damage
- ✅ Elimination count decreases by 1
- ✅ Zombies do NOT respawn
- ✅ Arcade timer continues

**Educational Check**:
- Does arcade damage feel different?
- Is the penalty appropriate?
- Does it add challenge without frustration?

---

### Scenario 5: Multiple Damage Sources

**Test**: Different entities deal appropriate damage

**Steps**:
1. Test zombie damage (1 HP)
2. Test third-party damage (if different)
3. Test boss damage (if different)

**Expected Results**:
- ✅ Each entity type deals correct damage
- ✅ Invincibility frames work for all sources
- ✅ Visual feedback consistent

---

### Scenario 6: Edge Cases

**Test**: Unusual situations

**Steps**:
1. Take damage at exactly 1 HP (should die)
2. Take damage with half heart (1 HP → 0 HP)
3. Take damage while already invincible
4. Pause during invincibility frames
5. Save/load with partial health

**Expected Results**:
- ✅ All edge cases handled gracefully
- ✅ No crashes or unexpected behavior
- ✅ Save/load preserves health state

---

### Scenario 7: Performance Testing

**Test**: Damage system doesn't impact performance

**Steps**:
1. Enter level with many zombies (50+)
2. Take damage repeatedly
3. Monitor FPS (should stay 60)
4. Check for lag or stuttering

**Expected Results**:
- ✅ 60 FPS maintained
- ✅ No lag during damage
- ✅ Smooth invincibility animation
- ✅ Hearts UI renders efficiently

---

## 📊 Testing Checklist

### Functional Testing
- [ ] Player takes 1 HP damage from zombies
- [ ] Hearts UI updates correctly
- [ ] Invincibility frames work (1.5s)
- [ ] Sprite flashing during invincibility
- [ ] Zombie respawns on damage (normal mode)
- [ ] Death triggers level restart
- [ ] All zombies respawn on death
- [ ] Player returns to start on death
- [ ] Health resets to 10 HP on death
- [ ] Save/load preserves health state

### Visual Testing
- [ ] Hearts render in top-left corner
- [ ] Full hearts are red
- [ ] Half hearts are pink
- [ ] Empty hearts are gray outline
- [ ] Sprite flashing is visible but not annoying
- [ ] UI doesn't overlap other elements
- [ ] Hearts scale properly at different resolutions

### Educational Testing
- [ ] Damage teaches "security incidents have costs"
- [ ] Respawn teaches "incidents undo work"
- [ ] Death teaches "catastrophic failure consequences"
- [ ] Invincibility teaches "recovery time needed"
- [ ] Overall system reinforces security concepts

### Performance Testing
- [ ] 60 FPS maintained with damage system
- [ ] No lag during invincibility
- [ ] Hearts UI renders efficiently
- [ ] No memory leaks over extended play

### Balance Testing
- [ ] 10 HP feels like right amount
- [ ] 1 HP per zombie hit feels fair
- [ ] 1.5s invincibility feels right
- [ ] Zombie respawn penalty feels meaningful
- [ ] Death penalty feels appropriate

---

## 🐛 Bug Reporting Template

If you find issues, document them:

```markdown
**Bug ID**: BUG-XXX
**Severity**: P0/P1/P2/P3
**Title**: Brief description

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Screenshots/Video**:
If applicable

**Environment**:
- OS: macOS
- Python: 3.11
- Commit: [SHA]

**Impact**:
How does this affect gameplay/education?
```

---

## 📝 Feedback Collection

### Gameplay Feel
- **Damage Feedback**: Is it clear when you take damage?
- **Invincibility**: Does 1.5s feel right?
- **Hearts UI**: Is health status always clear?
- **Death Penalty**: Is level restart fair?

### Educational Impact
- **Security Concepts**: Do mechanics teach intended lessons?
- **Motivation**: Does system motivate better play?
- **Understanding**: Are consequences clear?

### Balance
- **Difficulty**: Is it too easy/hard?
- **Health Amount**: Is 10 HP right?
- **Damage Amount**: Is 1 HP per hit fair?
- **Respawn Penalty**: Is it meaningful?

---

## 🎮 Recommended Testing Flow

### Quick Test (15 minutes)
1. Launch game
2. Test basic damage (Scenario 1)
3. Test death (Scenario 3)
4. Check performance

### Thorough Test (1 hour)
1. All 7 scenarios
2. Multiple levels
3. Different zombie counts
4. Edge cases
5. Performance monitoring

### Extended Test (2+ hours)
1. Full playthrough of multiple levels
2. Arcade mode testing
3. Save/load testing
4. Balance assessment
5. Educational impact evaluation

---

## 📊 Test Results Template

```markdown
## Sprint 1 Gameplay Test Results

**Date**: 2025-11-28
**Tester**: [Name]
**Duration**: [Time]
**Build**: [Commit SHA]

### Summary
- Scenarios Tested: X/7
- Bugs Found: X
- Performance: ✅/❌
- Educational Impact: ✅/❌
- Overall Assessment: [Rating 1-5]

### Detailed Results
[Scenario-by-scenario results]

### Bugs Found
[List of bugs with IDs]

### Recommendations
[Suggestions for improvements]

### Ready for Sprint 2?
✅ Yes / ❌ No (explain why)
```

---

## 🚀 Next Steps After Testing

### If All Tests Pass
1. Document test results
2. Commit any minor fixes
3. Update Sprint 1 status to "TESTED ✅"
4. Prepare for Sprint 2 kickoff @ 10 AM

### If Issues Found
1. Prioritize bugs (P0/P1 must fix before Sprint 2)
2. Create GitHub issues for bugs
3. Fix critical issues
4. Re-test
5. Update Sprint 2 plan if needed

---

## 🎯 Success Criteria

Sprint 1 features are ready for production when:
- ✅ All functional tests pass
- ✅ No P0/P1 bugs found
- ✅ Performance maintained (60 FPS)
- ✅ Educational impact validated
- ✅ Balance feels fair
- ✅ Visual feedback is clear
- ✅ Edge cases handled

---

**Happy Testing! 🎮**

**Remember**: The goal is to validate that Sprint 1 delivers on its promise to teach security fundamentals through meaningful player consequences.
