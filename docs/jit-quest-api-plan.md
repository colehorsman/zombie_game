# JIT Access Quest - API Integration Plan

## API Endpoints Discovered

### 1. Query Permission Sets
**Query:** `PermissionSets`
**Purpose:** Fetch all permission sets in an account

```graphql
query PermissionSets($where: PermissionSetsFilter) {
  PermissionSets(where: $where) {
    items {
      id
      name
      identityLabels
      userCount
      ssoUsers
    }
  }
}
```

**Filter by scope:**
```json
{
  "where": {
    "scope": {
      "op": "EQUALS",
      "value": "aws/r-ipxz/160224865296"
    }
  }
}
```

**Key field:** `identityLabels` - Array containing "ADMIN" or "PRIVILEGED"

### 2. Query JIT Configuration
**Query:** `JitConfiguration`
**Purpose:** Check which permission sets already have JIT enabled

```graphql
query JitConfiguration($where: JitConfigurationFilter) {
  JitConfiguration(where: $where) {
    count
    items {
      scope
      friendlyScope
      denyFirst
      permissionSets {
        id
        name
        isFullAccess
        isInherited
        status {
          status
          isPending
        }
      }
    }
  }
}
```

**Filter by scope:**
```json
{
  "where": {
    "scope": {
      "op": "EQUALS",
      "value": "aws/r-ipxz/160224865296"
    }
  }
}
```

### 3. Apply JIT Protection
**Mutation:** `SetJitConfiguration`
**Purpose:** Enroll permission sets in JIT

```graphql
mutation SetJitConfiguration($input: SetJitConfigurationInput!) {
  SetJitConfiguration(input: $input) {
    success
    addedJitConfigurationIds
    removedJitConfigurationIds
  }
}
```

**Input:**
```json
{
  "input": {
    "scope": "aws/r-ipxz/160224865296",
    "isDenyFirst": true,
    "enrolledPermissionSets": [
      {
        "id": "permission-set-id-here",
        "isFullAccess": false
      }
    ]
  }
}
```

## Implementation Plan

### Phase 1: API Client Methods (src/sonrai_client.py)

Add three new methods to `SonraiAPIClient`:

1. `fetch_permission_sets(account_scope: str) -> List[PermissionSet]`
   - Query all permission sets for an account
   - Filter for ADMIN or PRIVILEGED labels
   - Return list of permission set objects

2. `fetch_jit_configuration(account_scope: str) -> JitConfiguration`
   - Query existing JIT configuration
   - Return which permission sets are already enrolled
   - Used to show purple shields on protected roles

3. `apply_jit_protection(account_scope: str, permission_set_ids: List[str]) -> bool`
   - Apply JIT to specified permission sets
   - Return success/failure
   - Triggered when player interacts with admin role character

### Phase 2: Data Models (src/models.py)

Add new classes:

```python
@dataclass
class PermissionSet:
    id: str
    name: str
    identity_labels: List[str]
    user_count: int
    has_jit: bool = False  # Populated from JIT config query

@dataclass
class JitQuestState:
    active: bool = False
    auditor_position: Tuple[float, float] = (0, 0)
    admin_roles: List[PermissionSet] = field(default_factory=list)
    protected_count: int = 0
    total_count: int = 0
    quest_completed: bool = False
    quest_failed: bool = False
```

Add to `GameState`:
```python
jit_quest: Optional[JitQuestState] = None
```

### Phase 3: Entity Classes

Create `src/jit_access_quest.py`:

```python
class Auditor:
    """Auditor character that patrols the level"""
    - Position, velocity, bounds
    - Patrol behavior (similar to zombie movement)
    - Suit visual (gray/black with clipboard)
    
class AdminRole:
    """Admin role character with crown"""
    - Position, bounds
    - Crown visual indicator
    - Purple shield if JIT protected
    - Interaction logic
```

### Phase 4: Quest Logic (src/game_engine.py)

Add quest initialization:
- Check if account is production (160224865296, 613056517323, 437154727976)
- Query permission sets with ADMIN/PRIVILEGED labels
- Query JIT configuration to mark protected roles
- Only create quest if unprotected admin roles exist
- Spawn Auditor and AdminRole entities

Add quest interaction:
- Player collides with AdminRole
- Trigger API call to apply JIT
- Update AdminRole to show purple shield
- Check if all roles protected → quest success
- If player leaves level without completing → quest failed

### Phase 5: Rendering (src/renderer.py)

Add rendering for:
- Auditor character (suit, clipboard)
- AdminRole character (crown)
- Purple shield overlay (reuse from third party)
- Quest UI (optional: show progress "3/5 roles protected")

## Target Accounts

From `assets/aws_accounts.csv`:
- **160224865296** - MyHealth - Production Data
- **613056517323** - MyHealth - Production  
- **437154727976** - Sonrai MyHealth - Org

Scope format: `aws/r-ipxz/{account_id}`

## Success/Failure Messages

**Success:** "Audit Deficiency Prevented! Admin access now requires JIT approval."
**Failure:** "Audit Failed! Standing admin access remains a critical finding."

## Testing Checklist

- [ ] Query permission sets from production accounts
- [ ] Query JIT configuration
- [ ] Apply JIT protection via mutation
- [ ] Verify purple shields appear after protection
- [ ] Test quest only appears in production accounts
- [ ] Test quest doesn't appear if all roles already protected
- [ ] Test success message
- [ ] Test failure message when leaving level
