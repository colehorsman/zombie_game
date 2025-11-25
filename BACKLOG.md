# Product Backlog - Sonrai Zombie Blaster

**Last Updated**: 2025-11-24
**Product Owner**: Cole Horsman
**Status**: Active Development

---

## Legend

| Priority | Label | Description |
|----------|-------|-------------|
| 🔴 P0 | Critical | Blocking issues, must fix immediately |
| 🟠 P1 | High | Important for next release |
| 🟡 P2 | Medium | Should have, schedule when possible |
| 🟢 P3 | Low | Nice to have, future consideration |

| Status | Label |
|--------|-------|
| ✅ | Done |
| 🚧 | In Progress |
| 📋 | Ready for Dev |
| 🔍 | Needs Investigation |
| ⏸️ | On Hold |

---

## ✅ Recently Completed

| ID | Item | Status |
|----|------|--------|
| BUG-001 | Projectiles passing through zombies after quest completion | ✅ Fixed (spatial grid recreation) |
| BUG-002 | Door interaction cooldown causing re-entry | ✅ Fixed |
| BUG-003 | Lobby spawn position incorrect | ✅ Fixed |
| BUG-004 | Controller A/B buttons not dismissing messages | ✅ Fixed |
| FEAT-001 | JIT Access Quest (Production accounts) | ✅ Implemented |
| FEAT-002 | Service Protection Quest (Hacker challenge) | ✅ Implemented |
| FEAT-003 | Health/Damage system (3 HP zombies, 10 HP 3rd parties) | ✅ Implemented |
| FEAT-004 | Spatial grid collision optimization | ✅ Implemented |

---

## 🐛 Bugs

| ID | Priority | Description | Status | Notes |
|----|----------|-------------|--------|-------|
| BUG-005 | 🟠 P1 | Save/Load error: 'Level' object has no attribute 'is_completed' | 📋 Ready | Add attribute to Level class |
| BUG-006 | 🟡 P2 | Third party "Noops" error on block | 🔍 Investigate | Error handling needed |

---

## 🚀 Features - Current Sprint

### Epic: Visual Polish & UX

| ID | Priority | User Story | Status | Acceptance Criteria |
|----|----------|------------|--------|---------------------|
| FEAT-005 | 🟠 P1 | As a player, I want the raygun to look like a real weapon | 📋 Ready | Retro sci-fi style, visible in all states, 8-bit aesthetic |
| FEAT-006 | 🟡 P2 | As a player, I want a clean Zelda-style pause menu | 📋 Ready | Bulleted format, keyboard navigation, semi-transparent overlay |
| FEAT-007 | 🟡 P2 | As a player, I want the hacker to look more threatening | 📋 Ready | Laptop accessory, typing animation, matrix-style effects |

### Epic: Gameplay Enhancements

| ID | Priority | User Story | Status | Acceptance Criteria |
|----|----------|------------|--------|---------------------|
| FEAT-008 | 🟡 P2 | As a player, I want a lasso tool to capture admin roles (JIT quest) | 📋 Ready | Ranged interaction, visual animation, replaces walk-into mechanic |
| FEAT-009 | 🟢 P3 | As a player, I want damage numbers to appear when hitting enemies | 📋 Ready | Rise 30px, fade over 1s, max 20 active |
| FEAT-010 | 🟢 P3 | As a player, I want protected entities to show purple shields | 📋 Ready | Pulsing animation, 50% opacity, tooltip on proximity |

---

## 📋 Features - Backlog

### Epic: Multi-Level System Enhancements

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-011 | 🟢 P3 | Level completion screen with stats | 📋 Ready |
| FEAT-012 | 🟢 P3 | Final victory screen after all levels | 📋 Ready |
| FEAT-013 | 🟢 P3 | Cross-level scoring persistence | 📋 Ready |

### Epic: Boss Battles

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-014 | 🟢 P3 | Boss entity (3x size, 150 HP) from high-risk identities | 📋 Ready |
| FEAT-015 | 🟢 P3 | Boss health bar (top of screen) | 📋 Ready |
| FEAT-016 | 🟢 P3 | Mini-zombie spawning at 75%, 50%, 25% boss health | 📋 Ready |

### Epic: Audio & Music

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-017 | 🟢 P3 | 8-bit background music | ⏸️ On Hold |
| FEAT-018 | 🟢 P3 | Sound effects (laser, hit, victory) | ⏸️ On Hold |

### Epic: Future Quests

| ID | Priority | User Story | Status |
|----|----------|------------|--------|
| FEAT-019 | 🟢 P3 | S3 protection quest (Dev level) | ⏸️ Future |
| FEAT-020 | 🟢 P3 | RDS protection quest (Staging level) | ⏸️ Future |
| FEAT-021 | 🟢 P3 | Quest difficulty scaling by level | ⏸️ Future |

---

## 🧪 QA & Testing

| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| QA-001 | 🟠 P1 | Verify all bug fixes from Nov 24 session | 📋 Ready |
| QA-002 | 🟡 P2 | Property tests for damage/health system | 📋 Ready |
| QA-003 | 🟡 P2 | Cross-level functionality verification | 📋 Ready |
| QA-004 | 🟡 P2 | Integration test suite (test_integration.py) | 📋 Ready |

---

## 🔧 Technical Debt

| ID | Priority | Description | Status |
|----|----------|-------------|--------|
| TECH-001 | 🟡 P2 | Standardize API error handling patterns | 📋 Ready |
| TECH-002 | 🟢 P3 | Update failing unit tests (outdated API signatures) | 📋 Ready |
| TECH-003 | 🟢 P3 | Documentation agent for auto-generating docs | ⏸️ Future |

---

## 📊 Sprint Planning

### Current Sprint Focus
1. **Bug fixes verified** - QA-001
2. **Visual polish** - FEAT-005 (raygun), FEAT-006 (pause menu)
3. **Save/load fix** - BUG-005

### Definition of Done
- [ ] Feature implemented and working
- [ ] No regressions in existing functionality
- [ ] 60 FPS maintained
- [ ] Manual testing passed

---

## 📈 Velocity & Progress

| Metric | Value |
|--------|-------|
| Core Game | ✅ 100% Complete |
| Quests | ✅ 2/2 Implemented |
| Visual Polish | 🟡 60% |
| QA Coverage | 🟡 70% |
| Documentation | 🟡 80% |

---

## 🗺️ Roadmap

```
Current     → Visual Polish, Bug Fixes
Next Sprint → Damage Numbers, Purple Shields, Pause Menu
Future      → Boss Battles, Audio, Additional Quests
```

---

## 📝 Notes

- All Sonrai API integrations require `.env` configuration
- Game targets 60 FPS across all features
- Maintain retro 8-bit aesthetic in all visual updates
- Test with real Sonrai API data before release
