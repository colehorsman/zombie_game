# Sprint 2 Plan - Visual Polish & Arcade Enhancements

**Sprint Goal**: "Visual Polish & Arcade Enhancements"

**Start Date**: 2025-11-28 @ 10:00 AM CST
**End Date**: 2025-12-11
**Duration**: 2 weeks (10 working days)

---

## 🎯 Sprint Goal

Enhance visual feedback and arcade mode gameplay to improve player experience and educational impact.

---

## 📋 Sprint Backlog

### Selected Stories (P1/P2)

| ID | Story | Priority | Estimate | Owner |
|----|-------|----------|----------|-------|
| FEAT-005 | Retro raygun weapon visual | P2 | M (3-6h) | - |
| FEAT-031 | Arcade damage: elimination penalty | P2 | S (1-2h) | - |
| FEAT-032 | Health power-ups | P2 | M (3-6h) | - |
| BUG-006 | Third party "Noops" error on block | P2 | S (1-2h) | - |

**Total Estimated Effort**: 8-16 hours (1-2 days of focused work)

---

## 📝 Story Details

### FEAT-005: Retro Raygun Weapon Visual (M)

**Acceptance Criteria:**
- [ ] Sci-fi style raygun sprite designed (8-bit aesthetic)
- [ ] Raygun visible in all player states (idle, walking, shooting)
- [ ] Raygun rotates to face cursor/aim direction
- [ ] Muzzle flash effect on projectile fire
- [ ] Consistent with game's retro visual style

**Technical Approach:**
- Create raygun sprite in `src/player.py` or separate sprite module
- Add to player rendering in `src/renderer.py`
- Integrate with existing projectile system
- Add visual effects for firing

**Files to Modify:**
- `src/player.py` - Add raygun sprite generation
- `src/renderer.py` - Render raygun with player
- `tests/test_player.py` - Add raygun rendering tests

**Estimated Time**: 3-6 hours

---

### FEAT-031: Arcade Damage - Elimination Penalty (S)

**Acceptance Criteria:**
- [ ] In arcade mode, taking damage subtracts 1 from elimination count
- [ ] Does NOT respawn zombies in arcade mode
- [ ] Visual feedback shows count decrease
- [ ] Works with combo system
- [ ] Teaches "mistakes cost progress"

**Technical Approach:**
- Modify arcade mode damage handler in `src/game_engine.py`
- Check if arcade mode active before respawning zombies
- Subtract from arcade elimination count instead
- Update arcade UI to show penalty

**Files to Modify:**
- `src/game_engine.py` - Arcade damage logic
- `src/arcade_mode.py` - Elimination count management
- `tests/test_arcade_mode.py` - Add damage penalty tests

**Estimated Time**: 1-2 hours

---

### FEAT-032: Health Power-ups (M)

**Acceptance Criteria:**
- [ ] Heart collectible entity created
- [ ] 5% drop chance on zombie elimination
- [ ] Pickup collision detection working
- [ ] Restores 2 HP on pickup (max 10 HP)
- [ ] 10 second despawn timer
- [ ] Visual effects (sparkle, pulse animation)
- [ ] Sound effect placeholder (if audio system exists)

**Technical Approach:**
- Create `HealthPowerup` class (similar to existing powerups)
- Add drop logic to zombie elimination in `src/game_engine.py`
- Implement pickup collision detection
- Add healing logic to player
- Create heart sprite with animation
- Add despawn timer

**Files to Modify:**
- `src/powerup.py` - Add HealthPowerup class
- `src/game_engine.py` - Drop logic and pickup handling
- `src/player.py` - Add heal() method if not exists
- `src/renderer.py` - Render health powerup
- `tests/test_powerup.py` - Add health powerup tests

**Estimated Time**: 3-6 hours

---

### BUG-006: Third Party "Noops" Error on Block (S)

**Acceptance Criteria:**
- [ ] No "Noops" error when blocking third party
- [ ] Third party block action completes successfully
- [ ] Error handling added for edge cases
- [ ] Logs provide useful debugging info
- [ ] All third party tests passing

**Technical Approach:**
- Investigate error in third party block logic
- Check API call in `src/sonrai_client.py`
- Add error handling and validation
- Test with real third party entities
- Add logging for debugging

**Files to Modify:**
- `src/sonrai_client.py` - Fix block API call
- `src/game_engine.py` - Third party interaction logic
- `tests/test_third_party.py` - Add error case tests

**Estimated Time**: 1-2 hours

---

## 🗓️ Day-by-Day Plan

### Day 1 (2025-11-28) - Sprint Kickoff @ 10:00 AM CST

**Morning (10:00 AM - 12:00 PM)**
- Sprint planning ceremony (30 min)
- Create GitHub issues for all stories
- Set up feature branches
- Begin FEAT-005 (Raygun visual) - Design phase

**Afternoon (1:00 PM - 5:00 PM)**
- Complete FEAT-005 (Raygun visual)
- Begin FEAT-031 (Arcade damage penalty)
- Testing and QA

**End of Day**
- Commit all work
- Update GitHub issues
- Status update

### Day 2 (2025-11-29) - Feature Completion

**Morning**
- Complete FEAT-031 (Arcade damage penalty)
- Begin FEAT-032 (Health power-ups)

**Afternoon**
- Complete FEAT-032 (Health power-ups)
- Begin BUG-006 (Third party error)

**End of Day**
- All stories complete
- Integration testing
- Update backlog

### Day 3-10 - Buffer & Polish

**Options:**
1. Pull in additional Sprint 2 stories (FEAT-007, FEAT-009, FEAT-010)
2. Technical debt and refactoring
3. Documentation and demos
4. Start Sprint 3 planning

---

## 📊 Success Criteria

### Sprint Goals
- [ ] All 4 stories completed
- [ ] Raygun visual enhances player experience
- [ ] Arcade mode damage feels fair and educational
- [ ] Health power-ups add strategic depth
- [ ] Third party bug resolved

### Quality Metrics
- [ ] Test coverage maintained (558+ tests)
- [ ] 100% test pass rate
- [ ] 60 FPS maintained
- [ ] Security scans passing
- [ ] No regressions

### Educational Impact
- [ ] Raygun makes combat more engaging
- [ ] Arcade penalty teaches mistake costs
- [ ] Health power-ups teach resource management
- [ ] Overall gameplay more polished

---

## 🔧 Technical Considerations

### Performance
- Raygun rendering should not impact FPS
- Health power-up spawning should be efficient
- Arcade damage logic should be fast

### Testing
- Add unit tests for each feature
- Integration tests for arcade damage
- Visual regression testing for raygun

### Documentation
- Update ARCADE_MODE.md with new mechanics
- Document health power-up system
- Add raygun to player documentation

---

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Raygun visual doesn't match aesthetic | Medium | Low | Review design early, iterate |
| Arcade damage feels unfair | High | Medium | Playtest, adjust penalty amount |
| Health power-ups too common/rare | Medium | Medium | Tune drop rate based on testing |
| Third party bug hard to reproduce | Low | Low | Add comprehensive logging |

---

## 📈 Velocity Tracking

**Sprint 1 Velocity**: 5 stories in 1 day (exceptional)

**Sprint 2 Target**: 4 stories in 2 days (conservative estimate)

**Burndown Chart** (will update daily):
```
Stories Remaining:
Day 1: ████████ 4 stories
Day 2: ████░░░░ 2 stories (projected)
Day 3: ░░░░░░░░ 0 stories (projected)
```

---

## 🎮 Demo Plan

At sprint end, demo:
1. **Raygun Visual** - Show player with new weapon, firing effects
2. **Arcade Damage** - Demonstrate elimination penalty, no respawn
3. **Health Power-ups** - Show drops, pickup, healing
4. **Bug Fix** - Confirm third party blocking works

---

## 📝 Definition of Done Checklist

For each story:
- [ ] Feature implemented per acceptance criteria
- [ ] Unit tests added and passing
- [ ] Integration tests passing
- [ ] Manual QA completed
- [ ] Performance verified (60 FPS)
- [ ] Security scans passing
- [ ] Documentation updated
- [ ] GitHub issue closed
- [ ] Code committed and pushed

---

## 🔗 References

- [Sprint 1 Status](.kiro/specs/sprint-1-status.md)
- [Product Backlog](../docs/BACKLOG.md)
- [Arcade Mode Docs](../docs/ARCADE_MODE.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)

---

## 📅 Sprint Schedule

**Week 1**:
- Mon (Day 1): Sprint kickoff @ 10 AM, FEAT-005, FEAT-031
- Tue (Day 2): FEAT-032, BUG-006, testing
- Wed (Day 3): Buffer/polish
- Thu (Day 4): Additional stories or tech debt
- Fri (Day 5): Week 1 review

**Week 2**:
- Mon (Day 6): Continue work or start Sprint 3 planning
- Tue-Thu (Days 7-9): Final polish, documentation
- Fri (Day 10): Sprint review & retrospective

---

## 🚀 Sprint Kickoff Checklist

**Before 10:00 AM CST**:
- [ ] Review Sprint 2 plan
- [ ] Confirm story priorities with Product Owner
- [ ] Prepare development environment
- [ ] Review Sprint 1 retrospective

**At 10:00 AM CST**:
- [ ] Sprint planning ceremony (30 min)
- [ ] Create GitHub issues
- [ ] Set up feature branches
- [ ] Begin FEAT-005 implementation

---

**Sprint 2 Status: 📋 PLANNED - READY TO START @ 10:00 AM CST**
