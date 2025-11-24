# Feature Backlog

## 🚀 Planned Features

### 1. JIT Access Quest - Internal Audit Challenge
**Type**: Feature
**Priority**: High
**Target Branch**: `feature/jit-access-quest`

#### Description
Internal audit has flagged standing admin access in production accounts. Players must apply Sonrai JIT (Just-In-Time) access to admin roles to prevent a significant audit deficiency.

#### Requirements
- **Trigger**: Side quest in Production Data and Org accounts only
- **Characters**:
  - **Auditor**: Similar appearance to 3rd party characters, patrols the level
  - **Admin Role**: Creative character design representing standing admin access (needs unique look)
- **Mechanics**:
  - Find and interact with admin role characters
  - Apply JIT protection via Sonrai API
  - Already-protected roles show purple shield (like Sonrai 3rd party)
- **Visual Indicators**:
  - Unprotected admin roles: Warning indicator
  - Protected admin roles: Purple shield overlay
  - Auditor: Clipboard/checklist visual theme
- **API Integration**:
  - Query permission sets from Sonrai API
  - Apply JIT protection to admin roles
  - Display already-enrolled JIT roles with shields
- **Success Message**: "Audit Deficiency Prevented! Admin access now requires JIT approval."
- **Failure Message**: "Audit Failed! Standing admin access remains a critical finding."

#### Technical Notes
- Similar architecture to Service Protection Quest
- Check JIT enrollment status via API before creating quest
- Only show quest if admin roles are unprotected
- Reference screenshot shows available permission sets (need to review)

#### Acceptance Criteria
- [x] Quest only appears in Production Data and Org accounts
- [x] Auditor character spawns and patrols level
- [x] Admin role characters have unique visual design (gold crown)
- [x] Already-protected roles show purple shields
- [x] JIT protection API call works correctly
- [x] Success/failure dialogues display properly
- [x] Quest resets when returning to lobby

#### Implementation Status
✅ **COMPLETED** - All phases implemented and tested
- Phase 1: API integration (fetch_permission_sets, fetch_jit_configuration, apply_jit_protection)
- Phase 2: Data models (PermissionSet, JitQuestState, Auditor, AdminRole)
- Phase 3: Game logic (quest initialization, player interaction, success/failure handling)
- Phase 4: Rendering (auditor with suit, admin roles with crowns, purple shields)

---

### 2. JIT Quest - Lasso/Net Interaction
**Type**: Enhancement
**Priority**: Medium
**Target Branch**: `feature/jit-lasso-interaction`

#### Description
Replace the current "walk into admin role" interaction with a more thematic lasso/net tool for capturing elevated access and applying JIT protection.

#### Current Behavior
- Player walks into admin role character
- JIT protection applied automatically on collision

#### Desired Behavior
- Player uses a lasso/net tool (new button/key)
- Throw lasso at admin role from a distance
- Visual animation of lasso capturing the role
- JIT protection applied when captured
- More engaging and thematic interaction

#### Design Ideas
- **Lasso Tool**: Press SPACE to throw lasso, aim with arrow keys
- **Net Tool**: Press N to deploy net, captures roles in area
- **Capture Animation**: Lasso wraps around role, pulls them down if floating
- **Visual Feedback**: Sparkle effect when JIT applied
- **Sound Effects**: Lasso whoosh, capture sound

#### Technical Notes
- Add new input handling for lasso/net
- Create projectile-like lasso entity
- Add collision detection between lasso and admin roles
- Animation system for capture sequence
- Update tutorial/hints to explain new mechanic

#### Acceptance Criteria
- [ ] Lasso/net tool can be activated with key press
- [ ] Tool has visual representation (rope, net sprite)
- [ ] Captures admin roles from a distance
- [ ] Smooth animation when capturing
- [ ] JIT protection applied on successful capture
- [ ] Tutorial explains new mechanic

---

### 3. Improved Raygun Visual
**Type**: Enhancement
**Priority**: Medium
**Target Branch**: `feature/improved-raygun`

#### Description
The current raygun weapon looks like just a circle in the character's hand. It needs to be more defined and recognizable as a weapon.

#### Requirements
- **Current State**: Circle shape in player's hand
- **Desired State**: Detailed retro-style raygun with:
  - Barrel/nozzle extending forward
  - Grip/handle visible
  - Classic sci-fi raygun aesthetic
  - 8-bit/16-bit sprite style
  - Matches game's retro aesthetic

#### Design Ideas
- Mega Man-style arm cannon
- Classic sci-fi raygun (Buck Rogers style)
- Laser pistol with visible energy chamber
- Retro-futuristic design with antenna/coils

#### Technical Notes
- Update player rendering in `src/player.py`
- Add directional sprites (left-facing, right-facing)
- Ensure raygun is visible in both idle and firing states
- Maintain performance (simple sprite, not complex)

#### Acceptance Criteria
- [ ] Raygun is clearly recognizable as a weapon
- [ ] Maintains retro aesthetic
- [ ] Visible in all player states (idle, moving, jumping, firing)
- [ ] Performance remains stable
- [ ] Looks good in both lobby and platformer modes

---

## 📝 Notes

- Features should be developed on separate branches
- Each feature should include comprehensive testing
- Documentation should be updated when features are merged
- Consider user feedback during implementation

---

**Last Updated**: 2025-11-23
