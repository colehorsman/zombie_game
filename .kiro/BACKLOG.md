# Product Backlog - Sonrai Zombie Blaster

**Last Updated**: 2025-11-24
**Sprint**: Current Development Cycle

---

## Priority Legend
- 🔴 **P0** - Critical/Blocker (Must have for current sprint)
- 🟠 **P1** - High Priority (Should have for current sprint)
- 🟡 **P2** - Medium Priority (Nice to have)
- 🟢 **P3** - Low Priority (Future consideration)

---

## 🚀 Features

### Epic: Admin & Exemption Management System
**Priority**: 🔴 P0 | **Status**: In Progress | **Sprint Goal**: TODAY

#### F-001: Identify Admin Characters
- **User Story**: As a player, I need to see which identities are admins so I can understand privilege levels
- **Tasks**:
  - [ ] Add `is_admin` flag to identity data model
  - [ ] Query Sonrai API for admin identities (use existing patterns from exemptions API)
  - [ ] Parse and map admin identities to in-game characters
  - [ ] Add visual indicator for admin characters (crown icon or badge)
- **Acceptance Criteria**:
  - Admin identities fetched from Sonrai API
  - All admin characters visually distinguishable
  - Character tooltips show "Admin" designation
- **Dependencies**: Sonrai API client (existing)
- **Related**: Game Enhancements Phase 2 (Protected Identities)

#### F-002: Just-In-Time (JIT) Access System
- **User Story**: As a player, I want to apply JIT access to admin characters to demonstrate time-limited privilege elevation
- **Tasks**:
  - [ ] Add JIT access state to admin character model
  - [ ] Create JIT access API method in SonraiAPIClient
  - [ ] Implement JIT access UI trigger (button/key press near admin)
  - [ ] Add JIT timer countdown display
  - [ ] Handle JIT expiration (revert to normal state)
- **Acceptance Criteria**:
  - JIT can be applied to admin characters
  - Timer counts down visibly
  - Character state changes when JIT expires
  - Real Sonrai API called successfully
- **Dependencies**: F-001 (Admin identification)
- **Related**: JIT Access Quest requirements (.kiro/specs/jit-access-quest/requirements.md)

#### F-003: Purple Shield Effect for Exemption Characters
- **User Story**: As a player, when JIT is active on exemption characters, I should see a purple shield to understand they're protected
- **Tasks**:
  - [ ] Link exemption system with JIT system
  - [ ] Apply purple shield rendering when JIT active on exemption
  - [ ] Add shield pulsing animation (existing code in Phase 2)
  - [ ] Display "Protected (JIT Active)" tooltip
- **Acceptance Criteria**:
  - Purple shield appears only when JIT active
  - Shield matches existing protected entity design
  - Shield disappears when JIT expires
- **Dependencies**: F-002 (JIT system), Game Enhancements Phase 2 Task 11 (Purple shield rendering)
- **Related**: Game Enhancements Phase 2

---

### Epic: Visual Polish & UI Improvements
**Priority**: 🟠 P1 | **Status**: Not Started

#### F-004: Ray Gun Visual Asset Update
- **User Story**: As a player, I want the weapon to look like a real ray gun for better visual appeal
- **Tasks**:
  - [ ] Design new ray gun sprite (retro sci-fi style, 8-bit aesthetic)
  - [ ] Create multiple frames for firing animation
  - [ ] Update player rendering to use new ray gun sprite
  - [ ] Add muzzle flash effect on fire
  - [ ] Test visual alignment with player character
- **Acceptance Criteria**:
  - Ray gun visually recognizable as a weapon
  - Matches game's retro aesthetic
  - Firing animation smooth and satisfying
- **Dependencies**: None
- **Effort**: Medium

#### F-005: Pause Menu Redesign (Zelda-style)
- **User Story**: As a player, I want a clean, structured pause menu for better navigation
- **Tasks**:
  - [ ] Design menu layout (bulleted format, Zelda-style)
  - [ ] Create menu sections: Continue, Inventory, Stats, Settings, Quit
  - [ ] Implement menu navigation with arrow keys
  - [ ] Add menu background overlay (semi-transparent)
  - [ ] Add menu selection cursor/indicator
  - [ ] Implement menu item actions
- **Acceptance Criteria**:
  - Menu is clean and easy to read
  - Navigation is intuitive with keyboard
  - All menu items functional
  - Visual style matches game aesthetic
- **Dependencies**: None
- **Effort**: Medium

#### F-006: Enhanced Hacker Character Details
- **User Story**: As a developer, I want the hacker character to be more visually interesting
- **Tasks**:
  - [ ] Add laptop accessory sprite
  - [ ] Add animated typing motion
  - [ ] Add "hacking" particle effects (scrolling code, green matrix-style)
  - [ ] Add facial expression changes based on race progress
  - [ ] Enhance color palette for better contrast
- **Acceptance Criteria**:
  - Hacker visually distinct from other characters
  - Animations smooth and performant
  - Character personality evident from visuals
- **Dependencies**: Service Protection Quest Task 14 (Hacker sprite rendering)
- **Related**: Service Protection Quest Phase 3
- **Effort**: Medium

---

### Epic: Developer Experience & Automation
**Priority**: 🔴 P0 | **Status**: In Progress

#### F-007: QA Agent Auto-Run in Kiro
- **User Story**: As a developer, I need the QA agent to automatically run tests when code changes
- **Tasks**:
  - [x] Create QA testing agent steering document
  - [x] Create QA review hook for src/ changes
  - [ ] Verify hook triggers on file edits
  - [ ] Test hook with actual code changes
  - [ ] Document QA agent usage in README
- **Acceptance Criteria**:
  - Hook triggers when src/ files modified
  - Tests run automatically without manual intervention
  - Test results reported clearly
  - Hook is reliable and doesn't cause false positives
- **Dependencies**: None
- **Status**: Mostly complete, needs validation
- **Related**: .kiro/hooks/qa-review-src-changes.kiro.hook

#### F-008: Documentation Agent for Kiro
- **User Story**: As a developer, I want an agent that auto-generates documentation from code
- **Tasks**:
  - [ ] Create documentation agent steering document
  - [ ] Define documentation standards and templates
  - [ ] Create hook to trigger on code changes
  - [ ] Implement docstring extraction and formatting
  - [ ] Generate markdown documentation files
  - [ ] Add documentation to git commits automatically
- **Acceptance Criteria**:
  - Agent generates accurate documentation
  - Documentation matches code structure
  - Runs automatically in Kiro environment
  - Output is readable and useful
- **Dependencies**: None
- **Effort**: Large
- **Status**: Not Started

#### F-009: Sonrai MCP Configuration Demo
- **User Story**: As a stakeholder, I want to see the Sonrai MCP build process in action
- **Tasks**:
  - [ ] Review existing MCP configuration (.kiro/settings/mcp.json)
  - [ ] Document MCP setup steps
  - [ ] Create demo script showing build process
  - [ ] Add visual feedback for MCP operations in game
  - [ ] Prepare presentation materials
- **Acceptance Criteria**:
  - MCP configuration is documented
  - Demo runs without errors
  - Build process is clearly visible
  - Stakeholders can follow along
- **Dependencies**: None
- **Effort**: Small
- **Status**: Not Started

---

## 🐛 Bugs & Fixes

### B-001: Save/Load Error with Level Object
- **Priority**: 🟠 P1
- **Description**: 'Level' object has no attribute 'is_completed'
- **Steps to Reproduce**:
  1. Complete a level
  2. Try to save game
  3. Error occurs
- **Tasks**:
  - [ ] Add `is_completed` attribute to Level class
  - [ ] Update save logic to serialize is_completed
  - [ ] Update load logic to deserialize is_completed
  - [ ] Test save/load flow end-to-end
- **Related**: Service Protection Quest Task 64

### B-002: [Placeholder for discovered bugs]
- **Priority**: TBD
- **Description**: No known bugs at this time
- **Note**: Add bugs here as they are discovered during testing

---

## 🧪 QA & Testing

### QA-001: Property Tests for Game Enhancements Phase 1
- **Priority**: 🟠 P1
- **Description**: Complete property tests for damage and health system
- **Tasks**:
  - [ ] Task 1.1: Health depletion accuracy test
  - [ ] Task 1.2: Entity health initialization test
  - [ ] Task 1.3: Elimination only at zero health test
  - [ ] Task 4.1: Damage number lifecycle test
- **Dependencies**: Game Enhancements Phase 1 complete
- **Related**: .kiro/specs/game-enhancements/tasks.md

### QA-002: General QA Testing File Setup
- **Priority**: 🔴 P0
- **Description**: Ensure comprehensive QA testing file is in place
- **Tasks**:
  - [ ] Create tests/test_integration.py for end-to-end tests
  - [ ] Add smoke tests for critical paths
  - [ ] Document test coverage requirements
  - [ ] Set up CI/CD test automation (if applicable)
- **Acceptance Criteria**:
  - All critical features have tests
  - Test coverage > 70%
  - Tests run in < 2 minutes
- **Status**: Partially complete (unit tests exist)

### QA-003: Cross-Level Functionality Verification
- **Priority**: 🟠 P1
- **Description**: Verify sandbox-confirmed functionality works across all levels
- **Test Scenarios**:
  - [ ] Damage system works in all levels (1-6)
  - [ ] Health bars render correctly in all levels
  - [ ] Collision detection consistent across levels
  - [ ] Protected entities appear correctly in applicable levels
  - [ ] Service protection quests trigger in levels 1 and 6
  - [ ] Boss battles work in all levels
  - [ ] Scoring system accumulates across levels
- **Acceptance Criteria**:
  - All features work consistently
  - No level-specific bugs
  - Performance maintained across all levels (60 FPS)
- **Dependencies**: Multi-level system (Game Enhancements Phase 3)

---

## 📋 Technical Debt

### TD-001: Refactor Collision System
- **Priority**: 🟡 P2
- **Description**: Current collision system could be optimized with spatial partitioning
- **Impact**: Performance improvement for large zombie counts
- **Effort**: Medium
- **Related**: Sonrai Zombie Blaster Task 5

### TD-002: API Error Handling Consistency
- **Priority**: 🟡 P2
- **Description**: Standardize error handling patterns across all API calls
- **Impact**: Better reliability and debugging
- **Effort**: Small

---

## 🎯 Current Sprint Goals

### Sprint: Admin JIT & Visual Polish
**Duration**: TBD
**Goal**: Implement admin character identification, JIT access system, and key visual improvements

**Sprint Backlog**:
1. 🔴 F-001: Identify Admin Characters
2. 🔴 F-002: Just-In-Time (JIT) Access System
3. 🔴 F-003: Purple Shield Effect for Exemption Characters
4. 🔴 F-007: QA Agent Auto-Run Validation
5. 🟠 F-004: Ray Gun Visual Asset Update
6. 🟠 F-005: Pause Menu Redesign
7. 🟠 QA-003: Cross-Level Functionality Verification

**Success Criteria**:
- [ ] All admin characters identified and marked
- [ ] JIT access can be applied and expires correctly
- [ ] Purple shields display on exemptions with JIT
- [ ] QA agent runs automatically on code changes
- [ ] Ray gun looks like a real weapon
- [ ] Pause menu is clean and functional
- [ ] All levels tested and verified working

---

## 🗺️ Roadmap

### Current Sprint (This Week)
- Admin & Exemption Management System
- Visual Polish (Ray Gun, Pause Menu, Hacker)
- QA Infrastructure Validation

### Next Sprint
- Complete Game Enhancements Phase 2 (Protected Identities)
- Service Protection Quest (Start Phase 1-3)
- Documentation Agent

### Future Sprints
- Game Enhancements Phase 3-6 (Multi-level, Boss Battles, Scoring)
- Service Protection Quest (Complete all phases)
- Audio & Music (Phase 7)
- Final Polish & Performance Optimization

---

## 📊 Backlog Statistics

- **Total Features**: 9
- **Total Bugs**: 1 known
- **Total QA Tasks**: 3
- **Total Technical Debt**: 2
- **P0 Items**: 4
- **P1 Items**: 5
- **Completion**: ~60% core game, 20% enhancement features

---

## 📝 Notes

- Property tests marked with `*` in task files are optional but recommended
- All Sonrai API integrations require .env configuration
- Game maintains 60 FPS target across all features
- Retro 8-bit aesthetic must be maintained in all visual updates
- Test coverage requirement: >70% for critical paths

---

## 🔗 Related Documents

- [Game Enhancements Tasks](.kiro/specs/game-enhancements/tasks.md)
- [Service Protection Quest Tasks](.kiro/specs/service-protection-quest/tasks.md)
- [JIT Access Quest Requirements](.kiro/specs/jit-access-quest/requirements.md)
- [QA Agent Guide](.kiro/QA_AGENT_GUIDE.md)
- [QA Setup Status](.kiro/QA_SETUP_STATUS.md)
