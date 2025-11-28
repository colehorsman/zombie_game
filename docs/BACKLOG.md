# Product Backlog - Sonrai Zombie Blaster

**Last Updated**: 2024-11-28
**Product Owner**: Cole Horsman (with 11-Agent Kiro Architecture Review Board)
**Status**: Active Development
**Test Coverage**: 537 tests passing
**Latest Review**: [Architecture Review Board Report](../.kiro/ARCHITECTURE_REVIEW_BOARD_REPORT.md) - 42 recommendations from 11 agents

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

### Sprint 3 Goal
**"Enable External Contributions & Developer Experience"**

Focus: Based on Architecture Review Board recommendations, prioritize developer onboarding and project management infrastructure to enable external contributions.

**Sprint Duration:** 2 weeks
**Estimated Effort:** 20-25 hours
**Review Source:** [Architecture Review Board Report](../.kiro/ARCHITECTURE_REVIEW_BOARD_REPORT.md)

---

### Active Work - Architecture Review Board P0 Items

| ID | Priority | Title | Agent | Estimate | Status |
|----|----------|-------|-------|----------|--------|
| DEVEX-001 | P0 | Create CONTRIBUTING.md | DevEx | M (4-6h) | 📋 Ready |
| DEVEX-002 | P0 | Create TROUBLESHOOTING.md | DevEx | M (3-4h) | 📋 Ready |
| SEC-001 | P0 | Audit API error handling for token exposure | Security | S (2-3h) | 📋 Ready |
| OPS-001 | P0 | Document deployment process | Operations | S (2-3h) | 📋 Ready |
| UX-001 | P0 | Add interactive tutorial | UX/Design | L (2-3d) | 📋 Ready |
| UX-002 | P0 | Add quest objective UI | UX/Design | M (4-6h) | 📋 Ready |

---

### Sprint 3 Backlog - Developer Experience Focus

#### Epic: Developer Onboarding (P0)

**Why**: Enable external contributions by making setup and contribution process clear and fast.

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| DEVEX-001 | Create CONTRIBUTING.md | Setup guide, workflow, standards, < 1 hour to first contribution | M (4-6h) | DevEx |
| DEVEX-002 | Create TROUBLESHOOTING.md | Common issues, solutions, platform-specific fixes | M (3-4h) | DevEx |
| DEVEX-003 | Add VS Code configuration | .vscode/settings.json, launch.json, recommended extensions | S (1-2h) | DevEx |
| DEVEX-004 | Optimize setup time | Script common tasks, reduce from 15-20 min to < 10 min | S (2-3h) | DevEx |

#### Epic: Project Management Infrastructure (P1)

**Why**: Move backlog to GitHub for better tracking and visibility.

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| PM-001 | Migrate backlog to GitHub Issues | Create issues for all P0/P1 items, labels, milestones | M (4-6h) | Product Manager |
| PM-002 | Add sprint tracking | GitHub Projects board, sprint milestones, burndown | S (2-3h) | Product Manager |

#### Epic: Critical Security & Operations (P0)

**Why**: Address critical security and operational gaps before external contributions.

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| SEC-001 | Audit API error handling | Review all error logs, sanitize API responses, no token exposure | S (2-3h) | Security |
| OPS-001 | Document deployment process | DEPLOYMENT.md with step-by-step release guide | S (2-3h) | Operations |

**Sprint 3 Total Estimated Effort:** 20-25 hours

---

## 📋 NEXT - Sprint 4: Architecture & Quality

**Sprint Goal:** "Improve code maintainability and test quality"
**Duration:** 2 weeks
**Estimated Effort:** 30-35 hours
**Focus:** Architecture refactoring, test organization, security hardening

### Epic: Architecture Refactoring (P1)

**Why**: game_engine.py is 1,500+ lines, violates Single Responsibility Principle

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| ARCH-001 | Continue game_engine.py refactoring | Extract PlayerController, ZombieController, CollisionController | L (2-3d) | Architecture |
| ARCH-002 | Implement Event Bus pattern | Create EventBus class, migrate quest triggers to pub/sub | M (6-8h) | Architecture |

### Epic: Test Quality & Organization (P1)

**Why**: 537 tests in flat structure, 14 tests failing, needs organization

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| QA-001 | Reorganize test structure | Create tests/unit/, tests/integration/, tests/property/ | M (4-6h) | QA/Testing |
| QA-002 | Fix failing tests | Investigate and fix 14 failing tests, restore 100% pass rate | M (6-8h) | QA/Testing |

### Epic: Security Hardening (P1)

**Why**: Prevent API hangs and rate limiting issues

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| SEC-002 | Add request timeouts to all API calls | Add timeout parameter to all requests, handle timeouts | S (2-3h) | Security |
| SEC-003 | Implement API rate limiting | Rate limiter with exponential backoff | M (4-6h) | Security |

### Epic: Operations & Monitoring (P1)

**Why**: Need visibility into production errors and incidents

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| OPS-002 | Add error tracking (Sentry) | Integrate Sentry SDK, configure error reporting | M (4-6h) | Operations |
| OPS-003 | Create operational runbooks | Document common tasks (restart, rollback, debug) | M (4-6h) | Operations |

**Sprint 4 Total Estimated Effort:** 30-35 hours

---

## 📦 LATER - Sprint 5: UX & Polish

**Sprint Goal:** "Improve player experience and accessibility"
**Duration:** 2 weeks
**Estimated Effort:** 30-35 hours

### Epic: UX Improvements (P1)

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| UX-003 | Add visual feedback for actions | Damage numbers, elimination effects, sound cues | M (6-8h) | UX/Design |
| UX-004 | Improve text contrast | Add text outlines, adjust colors for readability | S (2-3h) | UX/Design |

### Epic: Educational Content (P1)

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| VISION-001 | Add educational tooltips | Pop-ups explaining security terms during gameplay | M (6-8h) | Product Vision |
| VISION-002 | Add breach story interludes | Between-level screens with real breach examples | M (4-6h) | Product Vision |

### Epic: DevOps & Deployment (P1)

| ID | Story | Acceptance Criteria | Estimate | Agent |
|----|-------|---------------------|----------|-------|
| DEVOPS-001 | Add deployment pipeline | GitHub Actions workflow for releases | M (6-8h) | DevOps/Tools |
| DEVOPS-002 | Add release artifact building | PyInstaller for executables | M (4-6h) | DevOps/Tools |

---

## 📦 BACKLOG - Sprint 6+: Future Work

### Epic: Architecture Improvements (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| ARCH-003 | Extract rendering logic into RenderingSystem | M (4-6h) | Architecture |
| ARCH-004 | Create QuestManager to handle all quests | M (6-8h) | Architecture |

### Epic: Test Improvements (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| QA-003 | Add performance benchmarks | S (2-3h) | QA/Testing |
| QA-004 | Standardize test naming | S (2-3h) | QA/Testing |

### Epic: UX Accessibility (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| UX-005 | Add colorblind mode | M (4-6h) | UX/Design |
| UX-006 | Add settings menu | M (6-8h) | UX/Design |

### Epic: Documentation (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| DOC-001 | Consolidate re:Invent documentation | S (2-3h) | Documentation |
| DOC-002 | Add documentation navigation map | S (1-2h) | Documentation |
| DOC-003 | Add API reference documentation | M (4-6h) | Documentation |

### Epic: Operations (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| OPS-004 | Add performance monitoring | M (6-8h) | Operations |
| OPS-005 | Implement save file backup strategy | S (2-3h) | Operations |

### Epic: Development Standards (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| STD-001 | Add commit message linting | S (1-2h) | Dev Standards |
| STD-002 | Create PR templates | S (1-2h) | Dev Standards |
| STD-003 | Add code review checklist | S (1h) | Dev Standards |

### Epic: Product Vision (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| VISION-003 | Implement achievement system | L (1-2d) | Product Vision |

### Epic: Project Management (P2)

| ID | Story | Estimate | Agent |
|----|-------|----------|-------|
| PM-003 | Implement velocity tracking | S (2-3h) | Product Manager |

---

## 🎮 ORIGINAL BACKLOG - Player Damage System

*Moved to future sprint after Architecture Review Board prioritization*

### Epic: Player Damage & Consequences (P2)

**Why**: Players currently have no risk. Adding damage teaches that security incidents have costs.

| ID | Story | Acceptance Criteria | Estimate |
|----|-------|---------------------|----------|
| FEAT-027 | Player takes damage when zombies touch | Collision detection, 1 HP damage per zombie touch | S |
| FEAT-028 | Health system with visual display | 10 HP starting, 5 hearts UI in top-left, half-heart states | M |
| FEAT-029 | Damage consequence: zombie unquarantine | Each hit = 1 zombie respawns, teaches "incidents undo work" | M |
| FEAT-030 | Death triggers level restart | 0 HP = all zombies respawn, player returns to start | S |
| FEAT-031 | Invincibility frames after damage | 1.5s invincibility, sprite flashing, prevents stunlock | S |

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
| BUG-005 | Save/Load error: 'Level' object missing 'is_completed' | S |
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
| Test Coverage | 537 tests | Maintain 500+ |
| Test Pass Rate | High | 100% |
| Core Game | 100% | - |
| Quests Implemented | 2/2 | - |
| Open P0 Items | 6 | 0 |
| Open P1 Items | 14 | < 5 |
| Architecture Review | 7.5/10 | 9/10 |
| Documentation Files | 43 | Maintain |

---

## 🎯 Updated Roadmap (Post-Architecture Review)

```
Q4 2024
├── Sprint 3 (Current): Developer Experience & Onboarding
│   └── Focus: CONTRIBUTING.md, TROUBLESHOOTING.md, GitHub Issues
├── Sprint 4: Architecture & Quality
│   └── Focus: Refactor game_engine.py, Test organization, Security
└── Sprint 5: UX & Polish
    └── Focus: Tutorial, Visual feedback, Educational tooltips

Q1 2025
├── Sprint 6: Operations & Deployment
│   └── Focus: Monitoring, Deployment pipeline, Runbooks
├── Sprint 7: Player Damage System
│   └── Focus: Health system, Damage mechanics, Consequences
└── Sprint 8: Production Outage Simulation
    └── Focus: Change Freeze, Rate Limiting, War Room mode
```

**Roadmap Changes:** Architecture Review Board identified critical gaps in developer experience, code organization, and operational maturity. Prioritizing these foundational improvements before adding new gameplay features.

---

## 📝 Definition of Done

- [ ] Feature implemented and functional
- [ ] Unit tests added (maintain 500+ total)
- [ ] No regressions (all tests pass)
- [ ] 60 FPS maintained
- [ ] Manual QA passed
- [ ] Code reviewed (if applicable)
- [ ] Documentation updated
- [ ] Security scan passed (pre-commit hooks)
- [ ] GitHub issue updated/closed

---

## 🔗 References

- **[Architecture Review Board Report](../.kiro/ARCHITECTURE_REVIEW_BOARD_REPORT.md)** - 11-agent comprehensive review
- [Architecture Guide](./ARCHITECTURE.md) - Controller pattern documentation
- [Quickstart Guide](./guides/QUICKSTART.md) - Developer setup
- [Security Policy](./reference/SECURITY.md) - Security considerations

---

## 📋 Architecture Review Board Summary

**Review Date:** November 28, 2024
**Agents:** 11 specialized agents
**Total Recommendations:** 42 items
**Project Health:** 7.5/10

**Key Findings:**
- ✅ Strong foundation: Production-ready code, comprehensive testing, excellent docs
- ⚠️ Needs improvement: Code organization, developer onboarding, operational maturity

**Priority Distribution:**
- **P0 Critical:** 6 items (Developer experience, Security, Operations, UX)
- **P1 High:** 19 items (Architecture, Testing, Security, Operations, UX, DevOps)
- **P2 Medium:** 17 items (Documentation, Standards, Product vision)

**Sprint Plan:** 4 sprints (8 weeks) to address all P0/P1 items

See [full report](../.kiro/ARCHITECTURE_REVIEW_BOARD_REPORT.md) for detailed recommendations from each agent.

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
