# Base Game Specification

This document defines the core requirements and design for the Sonrai Zombie Blaster base game.

## Requirements Summary

### R1: Real Data Visualization
Cloud security administrators see real AWS unused identities visualized as zombies for engaging security posture understanding.

**Acceptance Criteria:**
- Fetch unused identities from Sonrai API on startup
- Create exactly one zombie entity per unused identity (1:1 mapping)
- Display current zombie count in UI
- Show completion message when all zombies eliminated
- Display error and prevent gameplay if API unreachable

### R2: Player Controls
Players control a Mega Man-style character with simple, intuitive controls.

**Acceptance Criteria:**
- Arrow keys or A/D move player left/right
- Space bar fires projectiles
- Player constrained within screen boundaries
- Projectiles travel from player position
- Handle simultaneous inputs without conflicts

### R3: Real Quarantine Actions
Each zombie elimination triggers real quarantine via Sonrai API for actual security improvements.

**Acceptance Criteria:**
- Send quarantine request on zombie elimination
- Permanently remove zombie on successful quarantine
- Show error and restore zombie on failed quarantine
- Prevent re-targeting during pending quarantine
- Display victory screen when all zombies quarantined

### R4: Retro Graphics
Simple retro-style graphics similar to Chrome's dinosaur game for clean visuals and smooth performance.

**Acceptance Criteria:**
- Simple 2D sprites with recognizable features
- Minimal scrolling or static background
- Simple geometric projectiles
- Maintain at least 30 FPS (target 60 FPS)

### R5: Single Looping Level
Continuous single-level gameplay to focus on eliminating all zombies without level transitions.

**Acceptance Criteria:**
- Load single level layout on start
- Scroll background for continuous movement
- Distribute zombies across level space
- Maintain consistent physics during scrolling
- No level transitions (upcoming enhancement)

### R6: Secure API Authentication
Securely authenticate with Sonrai API using protected credentials.

**Acceptance Criteria:**
- Load credentials from environment variables or .env file
- Include valid authentication tokens in API requests
- Display clear error on authentication failure
- Display configuration error if credentials missing
- Never store credentials in source code or version control

### R7: Real-Time Progress Feedback
Clear visual feedback on progress and statistics.

**Acceptance Criteria:**
- Display current zombie count
- Update count within one second of elimination
- Show initial count on start
- Display quarantined identities count
- Show errors without obscuring game elements

### R8: Technology Requirements
Built with appropriate technology for maintainability and performance.

**Acceptance Criteria:**
- Python 3.11+ with Pygame framework
- Efficient game loop, rendering, and input processing
- Complete installation instructions
- Error logging for debugging
- Clean resource cleanup on exit

### R9: Zombie Identification
Display zombie identity information for tracking specific unused identities.

**Acceptance Criteria:**
- Extract numeric identifier from identity name
- Display number above zombie sprite for "test-user-{number}" pattern
- Position text directly above zombie
- Synchronize identifier position with zombie movement
- Show default identifier if pattern doesn't match

### R10: Congratulations Messages
Retro Game Boy-style congratulations messages when eliminating zombies.

**Acceptance Criteria:**
- Pause game on successful elimination
- Display message bubble in retro Game Boy style
- Include text: "You leveraged the Cloud Permissions Firewall to quarantine {zombie-name}"
- Wait for player input to dismiss
- Resume gameplay on message dismissal

## Core Design Properties

These are universal properties that must hold true across all game executions:

1. **One-to-one zombie mapping**: Zombie entities created = unused identities from API
2. **Game state display accuracy**: Displayed counts match actual game state
3. **Quarantine triggers on elimination**: Every elimination sends API request
4. **Successful quarantine removes zombie**: Permanent removal on success
5. **Failed quarantine restoration**: Zombie restored on failure with error
6. **Player boundary constraint**: Player always within screen boundaries
7. **Projectile from player position**: Projectiles created at player location
8. **Collision detection accuracy**: Overlapping bounds detected as collision
9. **Pending quarantine prevents re-targeting**: No duplicate requests
10. **Movement input processing**: Valid inputs move player correctly
11. **Simultaneous input handling**: Multiple inputs processed without conflicts
12. **Background scrolling continuity**: Smooth scrolling maintains playability
13. **Zombie spawn distribution**: Zombies distributed, not clustered
14. **Physics consistency during scroll**: Collision/physics consistent with scroll
15. **API authentication headers**: All requests include valid auth tokens
16. **API credential security**: No credentials in source code
17. **Display update responsiveness**: UI updates within 1 second
18. **Error logging**: All errors logged to logging system
19. **Resource cleanup on exit**: Proper cleanup on all exit scenarios
20. **Test user number extraction**: Correct numeric parsing from identity name
21. **Zombie label position sync**: Labels positioned correctly above zombies
22. **Game pause on elimination**: Transition to PAUSED state on success
23. **Congratulations message format**: Correct message text with identity name
24. **Game resume after dismissal**: Return to PLAYING on message dismissal

## Critical Implementation Notes

### Sonrai API Integration

**GraphQL Endpoint**: Configured via `SONRAI_API_URL`
**Authentication**: Bearer token via `SONRAI_API_TOKEN`
**Organization**: Specified via `SONRAI_ORG_ID`

**Key Queries:**
1. `CloudHierarchyList` - Fetch real account scopes (CRITICAL)
2. `UnusedIdentities` - Fetch zombies
3. `ThirdPartyAccessByAccount` - Fetch 3rd parties
4. `AppliedExemptedIdentities` - Fetch protected entities
5. `AccountsWithUnusedIdentities` - Account summary

**Key Mutations:**
1. `ChangeQuarantineStatus` - Quarantine identity
2. `SetThirdPartyControlMode` - Block third party

**Schema Reference**:
- 856 types total
- 138 available queries
- 154 available mutations
- Full schema in `docs/sonrai-api/schema.json`
- Use `search_sonrai_schema.py` to find field names

### Scope Handling (CRITICAL)

**ALWAYS** use real scopes from CloudHierarchyList API:
```python
# CORRECT
account_scopes = client._fetch_all_account_scopes()
scope = account_scopes.get("577945324761")
# Returns: "aws/r-ipxz/ou-ipxz-95f072k5/577945324761"

# WRONG - Never do this!
scope = f"aws/r-ipxz/ou-fake-id/{account}"  # Triggers alerts!
```

Fake scopes trigger security alerts in Sonrai. Always fetch from API.

### Damage and Health System

**Entity Health Points:**
- Regular zombies: 3 HP
- Third parties: 10 HP
- Protected entities: Invulnerable

**Damage:**
- Base damage: 1 per projectile
- Damage multiplier: +1 every 10 successful quarantines
- Projectile damage = base damage × multiplier

**Elimination:**
- Only eliminate when HP reaches 0
- Don't pause game for non-killing hits
- Only show congratulations on actual elimination

### Protected Entities

**Types:**
1. Sonrai third-party (identified by name "Sonrai" or "Sonrai Security")
2. Exempted identities (fetched from API per account)

**Visual Indicator:**
- Purple shield overlay (hexagon or circle)
- Purple color: (160, 32, 240) at 50% opacity
- Pulsing effect: Scale 1.0x to 1.1x over 1.0s
- Shield size: 1.2x entity size

**Behavior:**
- Ignore all projectile collisions
- Never apply damage
- Never quarantine/block

### Game State Machine

```
MENU → PLAYING ⇄ PAUSED → VICTORY
  ↓       ↓
ERROR ← ERROR
```

**State Transitions:**
- MENU: Initial state, show title screen
- PLAYING: Active gameplay
- PAUSED: Congratulations message displayed
- VICTORY: All zombies eliminated
- ERROR: API failure, critical error

### Visual Specifications

**Sprites:**
- Player: 32x32px blue rectangle with gun
- Zombie: 24x24px green rectangle
- Third Party: 28x28px yellow rectangle
- Projectile: 8x8px yellow circle
- Protected Shield: Purple hexagon overlay

**Health Bars:**
- Size: 30px wide × 4px tall
- Position: Above entity, 5px gap
- Colors: Red health, gray background, black border
- Animation: Smooth depletion over 0.2s

**Message Bubble:**
- Style: Retro Game Boy white rounded rectangle
- Border: Black, 2px
- Font: Pixelated retro font
- Background: White with subtle texture

### Configuration (.env)

```bash
# Sonrai API (REQUIRED)
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id
SONRAI_API_TOKEN=your_api_token

# Game Settings (OPTIONAL)
GAME_WIDTH=800
GAME_HEIGHT=600
TARGET_FPS=60
```

### Error Handling Patterns

**API Connection Errors:**
- Display: "Unable to connect to Sonrai API. Check network and credentials."
- Action: Prevent game start, provide retry option

**Authentication Failures:**
- Display: "Authentication failed. Check API credentials in .env"
- Action: Exit gracefully, log error details

**Quarantine Failures:**
- Display: "Failed to quarantine {identity_name}. Error: {message}"
- Action: Show notification, restore zombie, allow retry

**Missing Configuration:**
- Display: "Missing configuration. Create .env with required variables."
- Action: Exit gracefully with setup instructions

## Testing Strategy

### Unit Tests
- API client authentication and queries
- Collision detection edge cases
- Player movement and boundaries
- Game state transitions
- Configuration loading

### Property-Based Tests (Hypothesis)
- Minimum 100 iterations per test
- Tag format: `# Feature: sonrai-zombie-blaster, Property {N}: {text}`
- Test all 24 design properties
- Generate random game states, positions, collisions, API responses

### Integration Tests
- Full game loop with mocked API
- API client with Sonrai sandbox
- Rendering with headless Pygame

### Manual Tests
- Visual verification of sprites
- Gameplay feel and responsiveness
- End-to-end with real Sonrai API

## Performance Targets

- **Frame Rate**: 60 FPS target, minimum 30 FPS
- **API Response**: Quarantine requests complete within 2 seconds
- **UI Updates**: State changes reflected within 1 second
- **Memory**: Stable with 1000 zombie entities
- **Collision**: Spatial partitioning for efficient detection

## Known Limitations

- Single-level gameplay (multi-level is planned enhancement)
- No boss battles (planned enhancement)
- No level progression system (planned enhancement)
- Simple AI (zombies don't move strategically)
- No save/load system
- No difficulty settings
