# Product Backlog - Sonrai Zombie Blaster

**Last Updated**: 2025-11-27
**Product Owner**: Cole Horsman
**Status**: Active Development
**Test Coverage**: 537 tests passing

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Now](#-now---current-sprint) | Active work, immediate priorities |
| [Next](#-next---ready-for-sprint) | Refined, ready to pull |
| [Later](#-later---backlog) | Future work, needs refinement |
| [Icebox](#-icebox) | Parked ideas, low priority |

---

## Priority Framework

| Priority | SLA | Description |
|----------|-----|-------------|
| P0 | Immediate | Blocking production/demo, drop everything |
| P1 | This Sprint | Core functionality, customer-facing |
| P2 | Next Sprint | Important but not urgent |
| P3 | Backlog | Nice to have, future consideration |

---

## 🔥 NOW - Current Sprint

### Sprint Goal
**"Player consequences that teach security fundamentals"**

Focus: Add meaningful player damage system that reinforces the educational message that security mistakes have real costs.

---

### Active Work

| ID | Priority | Title | Owner | Status | Notes |
|----|----------|-------|-------|--------|-------|
| BUG-005 | P1 | Save/Load error: 'Level' object missing 'is_completed' | - | 📋 Ready | Blocking save functionality |

---

### Sprint Backlog

#### Epic: Player Damage & Consequences (P1)

**Why**: Players currently have no risk. Adding damage teaches that security incidents have costs and defensive positioning matters.

| ID | Story | Acceptance Criteria | Estimate |
|----|-------|---------------------|----------|
| FEAT-027 | Player takes damage when zombies touch | Collision detection, 1 HP damage per zombie touch | S |
| FEAT-028 | Health system with visual display | 10 HP starting, 5 hearts UI in top-left, half-heart states | M |
| FEAT-029 | Damage consequence: zombie unquarantine | Each hit = 1 zombie respawns, teaches "incidents undo work" | M |
| FEAT-030 | Death triggers level restart | 0 HP = all zombies respawn, player returns to start | S |
| FEAT-031 | Invincibility frames after damage | 1.5s invincibility, sprite flashing, prevents stunlock | S |

**MVP Definition**: FEAT-027 + FEAT-028 + FEAT-029 = playable damage system

---

## 📋 NEXT - Ready for Sprint

*Refined stories ready to pull when capacity allows*

### Epic: Visual Polish (P2)

| ID | Story | Acceptance Criteria | Estimate |
|----|-------|---------------------|----------|
| FEAT-005 | Retro raygun weapon visual | Sci-fi style, visible in all player states, 8-bit aesthetic | M |
| FEAT-007 | Threatening hacker appearance | Laptop accessory, typing animation, matrix effects | M |
| FEAT-009 | Damage numbers on hit | Float up 30px, fade over 1s, max 20 concurrent | S |
| FEAT-010 | Purple shields on protected entities | Pulsing animation, 50% opacity | S |

### Epic: Arcade Mode Enhancements (P2)

| ID | Story | Acceptance Criteria | Estimate |
|----|-------|---------------------|----------|
| FEAT-031 | Arcade damage: elimination penalty | 1 hit = -1 elimination count (not respawn) | S |
| FEAT-032 | Health power-ups | Heart drops (5% chance), restore 2 HP, 10s despawn | M |

### Tech Debt (P2)

| ID | Description | Estimate |
|----|-------------|----------|
| TECH-001 | Standardize API error handling patterns | M |
| BUG-006 | Third party "Noops" error on block | S |

---

## 📦 LATER - Backlog

*Needs refinement before sprint-ready*

### Epic: Production Outage Simulation (P2)

**Vision**: Simulate real-world production incidents teaching incident response through gameplay.

| ID | Feature | Educational Value |
|----|---------|-------------------|
| FEAT-019 | Change Freeze mode | Teaches change management during incidents |
| FEAT-020 | API Rate Limiting simulation | Teaches AWS API throttling constraints |
| FEAT-021 | War Room mode (approval required) | Teaches incident command structure |
| FEAT-022 | Rollback scenario | Teaches change reversibility |

**Refinement Needed**: Detailed designs exist in archive. Need to break into implementable stories.

### Epic: Boss Battles (P3)

| ID | Feature | Notes |
|----|---------|-------|
| FEAT-014 | Boss entity (3x size, 150 HP) | High-risk identity visualization |
| FEAT-015 | Boss health bar (top of screen) | Standard boss UX |
| FEAT-016 | Mini-zombie spawning at health thresholds | 75%, 50%, 25% spawn waves |

### Epic: Multi-Level Polish (P3)

| ID | Feature |
|----|---------|
| FEAT-011 | Level completion stats screen |
| FEAT-012 | Final victory screen after all levels |
| FEAT-013 | Cross-level scoring persistence |

---

## 🧊 ICEBOX

*Parked. Will revisit based on customer feedback.*

| ID | Feature | Reason Parked |
|----|---------|---------------|
| FEAT-017 | 8-bit background music | Nice-to-have, not core to educational mission |
| FEAT-018 | Sound effects | Same as above |
| FEAT-008 | Lasso tool for JIT quest | Current walk-into mechanic works, low priority |
| FEAT-024 | S3 protection quest | Future expansion, needs API work |
| FEAT-025 | RDS protection quest | Future expansion |
| FEAT-026 | Quest difficulty scaling | Premature optimization |
| TECH-003 | Documentation auto-generation | Low ROI currently |

---

## ✅ Done (Recent)

| ID | Item | Completed |
|----|------|-----------|
| REFACTOR-001 | Extract PauseMenuController | 2025-11-27 |
| REFACTOR-002 | Extract ArcadeResultsController | 2025-11-27 |
| REFACTOR-003 | Extract CheatCodeController | 2025-11-27 |
| REFACTOR-004 | Extract BossDialogueController | 2025-11-27 |
| BUG-007 | Renderer font initialization | 2025-11-27 |
| DOC-001 | Architecture documentation | 2025-11-27 |
| BUG-001 | Projectiles passing through zombies | 2025-11-24 |
| BUG-002 | Door interaction cooldown | 2025-11-24 |
| FEAT-001 | JIT Access Quest | 2025-11-24 |
| FEAT-002 | Service Protection Quest | 2025-11-24 |

---

## 📊 Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test Coverage | 537 tests | Maintain |
| Core Game | 100% | - |
| Quests Implemented | 2/2 | - |
| Open P0 Bugs | 0 | 0 |
| Open P1 Bugs | 1 | 0 |

---

## 🎯 Roadmap

```
Q4 2025
├── Sprint 1 (Current): Player Damage System
├── Sprint 2: Visual Polish + Health Power-ups
└── Sprint 3: Production Outage MVP (Change Freeze + Rate Limiting)

Q1 2026
├── Sprint 4: Boss Battles
├── Sprint 5: Audio + Final Polish
└── Sprint 6: Public Release Prep
```

---

## 📝 Definition of Done

- [ ] Feature implemented and functional
- [ ] Unit tests added (maintain 500+ total)
- [ ] No regressions (all tests pass)
- [ ] 60 FPS maintained
- [ ] Manual QA passed
- [ ] Code reviewed (if applicable)

---

## 🔗 References

- [Architecture Guide](./ARCHITECTURE.md) - Controller pattern documentation
- [Quickstart Guide](./guides/QUICKSTART.md) - Developer setup
- [Security Policy](./reference/SECURITY.md) - Security considerations

---

## Archive

<details>
<summary>Production Outage Feature - Detailed Design (Click to expand)</summary>

### Outage Types

1. **Change Freeze**: 10-15s, no quarantine allowed
2. **API Rate Limiting**: 15-20s, quarantine delayed 2-3s
3. **War Room Mode**: 20s, approval required for each action
4. **Rollback Required**: 10s, last 5 quarantines undone
5. **Degraded Performance**: 15s, player speed -30%
6. **Compliance Audit**: 20s, must categorize each quarantine

See git history for full design document.

</details>

<details>
<summary>Player Damage System - Detailed Design (Click to expand)</summary>

### Core Mechanics

- **Starting Health**: 10 HP (5 hearts)
- **Zombie Touch**: 1 HP damage
- **Third-Party Touch**: 2 HP damage
- **Boss Touch**: 3 HP damage
- **Invincibility**: 1.5s after damage
- **Death**: All zombies respawn, level restart

### Difficulty Scaling

| Account | Starting HP | Respawn/Hit | Health Drop % |
|---------|-------------|-------------|---------------|
| Sandbox | 10 | 1 | 5% |
| Dev | 10 | 1 | 4% |
| Staging | 8 | 2 | 3% |
| Production | 6 | 2 | 2% |

See git history for full design document.

</details>
