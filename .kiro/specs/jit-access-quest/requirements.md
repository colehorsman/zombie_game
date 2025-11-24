# JIT Access Quest - Requirements Specification

## Overview

Internal audit has flagged standing admin access in production AWS accounts as a significant deficiency. Players must apply Sonrai Just-In-Time (JIT) access controls to admin permission sets to remediate this audit finding before it becomes a compliance violation.

## Business Context

### The Problem
- **Audit Finding**: Standing admin access in production environments
- **Risk**: Excessive privilege, compliance violations, insider threats
- **Severity**: Significant deficiency → Material weakness if not remediated
- **Solution**: Apply JIT access controls requiring approval workflows

### The Solution
- Apply Sonrai JIT to admin permission sets
- Require approval for admin access elevation
- Convert standing access to time-limited, approval-based access
- Demonstrate compliance through audit-ready evidence

## Gameplay Mechanics

### Quest Trigger
- **Location**: Production Data (Level 5) and Org (Level 7) accounts ONLY
- **Trigger Type**: Automatic when entering level (if admin roles are unprotected)
- **Activation**: Auditor spawns and begins patrol
- **Goal**: Find and protect admin permission sets before audit deadline

### Characters

#### 1. Auditor Character
- **Role**: Neutral observer tracking compliance
- **Appearance**: Similar to 3rd party characters
- **Visual Theme**:
  - Clipboard or checklist in hand
  - Business attire (suit, tie)
  - Magnifying glass or audit badge
  - Professional, serious expression
- **Behavior**:
  - Patrols the level back and forth
  - Does NOT attack player
  - Displays countdown timer overhead
  - Shows disapproval emotes if time runs low
- **Spawn Location**: Near level entrance
- **Movement**: Walks slowly left/right, observing

#### 2. Admin Role Characters
- **Role**: High-privilege permission sets needing JIT protection
- **Appearance**: **CREATIVE DESIGN NEEDED**
  - Should look authoritative/powerful
  - Different from zombies and 3rd parties
  - Ideas:
    - Crown or admin badge on head
    - Golden/yellow color scheme (admin privilege)
    - Keys or access cards visible
    - Larger than normal characters
    - Glowing effect for unprotected
- **Behavior**:
  - Static/stationary (don't move)
  - Positioned on platforms throughout level
  - Multiple admin roles per level (1-3)
- **States**:
  - **Unprotected**: Yellow glow, warning icon above head
  - **Protected**: Purple shield overlay (like Sonrai 3rd party)

### Quest Flow

#### 1. Entry (Auto-trigger)
```
Player enters Production Data or Org account
  ↓
Game checks: Are there unprotected admin permission sets?
  ↓
YES: Spawn auditor + admin role characters
NO: Skip quest (all admin roles already have JIT)
```

#### 2. Quest Active
```
Auditor patrols level
Admin roles visible with status indicators
Player navigates to each admin role
Player presses SPACE when near admin role (80px range)
  ↓
API call: Apply JIT protection to permission set
  ↓
Admin role gains purple shield
  ↓
Repeat until all admin roles protected OR time expires
```

#### 3. Success Condition
```
All admin permission sets protected before timer expires (180 seconds)
  ↓
Auditor shows approval emote
  ↓
Success message displays
  ↓
Quest marked complete
  ↓
Continue level normally
```

#### 4. Failure Condition
```
Timer expires with unprotected admin roles remaining
  ↓
Auditor shows failure emote
  ↓
Failure message displays
  ↓
Must restart level
```

## API Integration

### Required Queries

#### 1. Get Permission Sets
```graphql
query getPermissionSets($scope: String!) {
  PermissionSets(where: { scope: { value: $scope, op: EQ } }) {
    items {
      permissionSetName
      permissionSetArn
      jitEnrolled
      isAdmin
    }
  }
}
```

**Purpose**: Fetch all permission sets for the account
**Filter**: Only admin permission sets (isAdmin == true)
**Return**: List of admin permission sets and their JIT status

#### 2. Apply JIT Protection
```graphql
mutation applyJIT($input: JITProtectionInput!) {
  ApplyJITProtection(input: $input) {
    success
    permissionSetName
  }
}
```

**Purpose**: Enroll permission set in JIT access controls
**Input**:
- permissionSetArn
- scope
- approvalWorkflow (default: ChatOps)

### Dynamic Quest Creation

```python
def _initialize_jit_quests(self):
    # Only for Production Data (Level 5) and Org (Level 7)
    for level in [5, 7]:
        level_obj = level_manager.get_level(level)

        # Check which admin permission sets lack JIT
        permission_sets = api_client.get_permission_sets(level_obj.account_id)
        admin_sets = [ps for ps in permission_sets if ps.isAdmin]
        unprotected_admin = [ps for ps in admin_sets if not ps.jitEnrolled]

        if unprotected_admin:
            # Create JIT quest with admin role characters
            quest = create_jit_access_quest(
                quest_id=f"jit_admin_{level}",
                level=level,
                admin_roles=unprotected_admin,
                time_limit=180.0  # 3 minutes
            )
```

## Visual Requirements

### Admin Role Sprite
- **Size**: 48x48 pixels (larger than zombies at 32x32)
- **Color Scheme**: Gold/yellow for unprotected, purple shield when protected
- **Features**:
  - Crown or admin badge
  - Keys or access card
  - Authority symbols
  - Glowing outline when unprotected

### Auditor Sprite
- **Size**: 32x48 pixels (taller than player)
- **Color Scheme**: Gray/blue professional
- **Features**:
  - Clipboard in hand
  - Business attire
  - Serious expression
  - Countdown timer overhead (white text on dark background)

### UI Elements
- **Timer Display**: Top-center, below race timer
  - "⏱ Audit Deadline: 180s"
  - Color: Red (<30s), Yellow (<60s), White (>60s)
- **Admin Role Indicator**: Appears near admin roles
  - Unprotected: "⚠️ Admin Access - Apply JIT"
  - Protected: "✅ JIT Enrolled"

## Message Text

### Trigger Message (Level Entry)
```
🔍 INTERNAL AUDIT ALERT 🔍

Standing admin access detected in production!

Auditors are reviewing your environment. Apply
JIT access controls to admin permission sets
before they file a significant deficiency.

Time remaining: 3:00

Press SPACE near admin roles to apply JIT.
```

### Success Message
```
✅ AUDIT PASSED - NO DEFICIENCIES

You successfully applied JIT access controls to
all admin permission sets!

Admin access now requires ChatOps approval through
Slack or Teams. Time-limited access prevents standing
privilege and satisfies audit requirements.

Compliance status: PASS ✅

Press ENTER to continue
```

### Failure Message
```
❌ AUDIT FAILED - SIGNIFICANT DEFICIENCY

Auditors documented standing admin access as a
significant deficiency!

This finding will be escalated to senior management
and may become a material weakness in your next
compliance review.

Remediation required: Apply JIT to ALL admin roles.

Press ENTER to restart level
```

### Interaction Hint (Near Admin Role)
```
Press SPACE to apply JIT access controls
```

## Level Integration

### Production Data (Level 5)
- **Admin Roles**: 2-3 permission sets
- **Layout**: Scattered across platforms
- **Difficulty**: Medium (more zombies, longer distance)
- **Timer**: 180 seconds

### Org (Level 7)
- **Admin Roles**: 1-2 permission sets
- **Layout**: Positioned strategically
- **Difficulty**: High (boss may be present)
- **Timer**: 180 seconds

## Technical Architecture

### New Files

#### `src/auditor.py`
- Auditor character class
- Patrol movement logic
- Timer display
- Emote system

#### `src/admin_role.py`
- Admin permission set character
- JIT protection state
- Visual states (protected/unprotected)
- Sprite generation

#### `src/jit_access_quest.py`
- Quest management system
- API integration for permission sets
- Quest state machine
- Level integration

#### `src/jit_sprite.py`
- Admin role sprite generation
- Auditor sprite generation
- Shield overlay for protected roles

### Modified Files

#### `src/game_engine.py`
- Add JIT quest initialization
- Quest update loop
- Player interaction detection
- Quest success/failure handling

#### `src/sonrai_client.py`
- Add `get_permission_sets()` method
- Add `apply_jit_protection()` method
- Parse JIT enrollment status

#### `src/renderer.py`
- Render auditor character
- Render admin role characters
- Display audit timer
- Show interaction hints

#### `src/models.py`
- Add `JITAccessQuest` dataclass
- Add `AdminRole` dataclass
- Add `Auditor` dataclass

## Data Models

```python
@dataclass
class JITAccessQuest:
    quest_id: str
    level: int
    admin_roles: List[AdminRole]
    time_limit: float
    time_remaining: float
    status: QuestStatus
    auditor_spawned: bool
    roles_protected: int
    total_roles: int

@dataclass
class AdminRole:
    permission_set_name: str
    permission_set_arn: str
    position: Vector2
    protected: bool  # JIT enrolled
    sprite_base: pygame.Surface
    sprite_protected: pygame.Surface

@dataclass
class Auditor:
    position: Vector2
    velocity: Vector2
    patrol_left: float  # Left boundary
    patrol_right: float  # Right boundary
    direction: int  # 1 = right, -1 = left
    speed: float
```

## Success Criteria

### Functional Requirements
- [ ] Quest only appears in Production Data and Org accounts
- [ ] Quest checks API for unprotected admin permission sets
- [ ] Auditor character spawns and patrols correctly
- [ ] Admin role characters display at correct positions
- [ ] Purple shields show on already-protected roles
- [ ] Player can interact with admin roles (SPACE key, 80px range)
- [ ] JIT protection API call succeeds
- [ ] Admin role gains purple shield after protection
- [ ] Quest succeeds when all roles protected
- [ ] Quest fails when timer expires
- [ ] Timer displays correctly with color coding
- [ ] Success/failure messages display properly
- [ ] Quest resets when returning to lobby

### Technical Requirements
- [ ] No performance degradation with multiple admin roles
- [ ] API error handling (network failures, invalid responses)
- [ ] Proper cleanup when exiting level
- [ ] Save/load compatibility
- [ ] Consistent with existing quest architecture

### Visual Requirements
- [ ] Admin role sprite is unique and recognizable
- [ ] Auditor sprite conveys professional authority
- [ ] Purple shields match existing Sonrai 3rd party style
- [ ] Timer is clearly visible
- [ ] Interaction hints are readable

## Future Enhancements

### Phase 2 (Optional)
- Multiple permission set types (not just admin)
- Approval workflow customization
- JIT duration settings (4hr, 8hr, 24hr)
- Audit report summary at quest end
- Leaderboard for fastest audit remediation
- Additional auditor emotes and reactions

## Notes

### Permission Set Details (From Screenshot)

**Already Protected (Show Purple Shields)**:
- AdministratorAccess (inherited) - Should display with purple shield
- DataScientist - Should display with purple shield

**High-Privilege Roles Needing JIT (Quest Objectives)**:
- PowerUserAccessPrivileged - Primary quest target
- DataScientistPrivileged - Primary quest target

**Other Unprotected Roles** (Lower priority):
- Billing
- DenyCreateAccessKey
- EC2Admin-SSO-Terraform-Test
- ReadOnlyAccessPrivileged
- SecurityAudit
- ViewOnlyAccess
- ViewOnlyAccess_Matt

**Quest Logic**:
- Focus on "Privileged" permission sets (PowerUser, DataScientist)
- AdministratorAccess already protected → show as success example
- Player must protect PowerUserAccessPrivileged and DataScientistPrivileged
- These represent standing admin-level access that violates audit requirements

### Creative Design Decisions
- Admin role character design needs finalization
- Auditor emote system (approval/disapproval)
- Timer countdown sounds/alerts
- Celebration animation on success

---

**Status**: Draft - Ready for Review
**Next Steps**: Review screenshot, finalize character designs, create tasks.md
