# Service Protection Quest - Requirements

## Overview

A race-against-time sidequest where players compete with a hacker to protect critical AWS services (Bedrock) using the Sonrai Cloud Permissions Firewall API. Combines education about service protection with exciting gameplay.

## 1. Quest System

### 1.1 Quest Triggers
- Quest triggers when player walks past x=300 in specific levels
- Available in:
  - Sandbox (Level 1)
  - Production (Level 6)

### 1.2 Quest States
- NOT_STARTED: Quest exists but not triggered
- TRIGGERED: Warning dialog shown, waiting for ENTER key
- ACTIVE: Hacker spawned, race in progress
- COMPLETED: Service protected successfully

### 1.3 Warning Dialog
- Dramatic alert appears when quest triggers
- Message: "You have 60 SECONDS to protect the Bedrock service before a hacker deletes Bedrock guardrails allowing PROMPT INJECTION!"
- Dismissible with ENTER key
- Game continues (not paused)

### 1.4 Quest Data Model
- ServiceProtectionQuest class with:
  - quest_id: str
  - level: int (1 for Sandbox, 6 for Production)
  - service_type: str (e.g., "bedrock")
  - trigger_position: Vector2 (x=300)
  - service_position: Vector2 (icon location)
  - time_limit: float (60.0 seconds)
  - status: QuestStatus enum

## 2. Hacker Character

### 2.1 Spawn Behavior
- Spawns when player presses ENTER on warning dialog
- Falls from sky above Bedrock icon position
- Lands on ground using gravity physics

### 2.2 Appearance
- Red body with black hat ("black hat hacker")
- Yellow eyes for visibility
- Size: Similar to player character
- Distinctive enough to identify quickly

### 2.3 Movement AI
- Horizontal movement toward service icon
- Speed: 150 pixels/second (slightly slower than player)
- Lands on ground and walks horizontally
- No jumping or obstacle avoidance

### 2.4 Physics
- Subject to gravity when falling
- Collides with ground
- Continues horizontal movement after landing

## 3. Service Node System

### 3.1 Service Icon
- Bedrock service icon: 48x48 pixels
- Blue-to-purple gradient hexagonal blocks (8-bit style)
- Three visual states:
  - Base: Normal appearance
  - Protected: Green shield overlay
  - Unprotected: Red warning indicator

### 3.2 Icon Positioning
- Y position: 784 (ground_y - icon_height)
- Must sit ON ground, not below it
- Sandbox quest: x=600, y=784
- Production quest: x=800, y=784

### 3.3 Service Node Data
- ServiceNode class with:
  - service_type: str
  - position: Vector2
  - protected: bool
  - sprite: Surface (48x48px)

### 3.4 Visual Feedback
- Pulsing animation when quest is active
- Shield overlay when protected
- Visible in platformer levels only

## 4. Race Mechanics

### 4.1 Timer System
- 60-second countdown displayed at top of screen
- Color coding:
  - Green: >30 seconds remaining
  - Orange: 15-30 seconds remaining
  - Red: <15 seconds remaining
- Precise to tenths of a second

### 4.2 Auto-Protection
- Player walks within 80 pixels of service icon
- Automatically triggers protection (no key press required)
- Calls Sonrai API: protect_service(service_type, account_id, service_name)
- Shows success/failure message

### 4.3 Win Condition
- Player reaches icon before hacker
- Service protection API call succeeds
- Success message: "🛡️ SERVICE PROTECTED! The Bedrock service is now safe!"
- Quest status → COMPLETED

### 4.4 Lose Conditions
- Hacker reaches icon first → GAME OVER
- Timer expires → GAME OVER
- Game over message: "💀 GAME OVER - The hacker compromised the Bedrock service!"

### 4.5 Race Detection
- Check distance between hacker and service icon
- Check distance between player and service icon
- Compare which entity is closer
- Winner is first to reach within range

## 5. Sonrai API Integration

### 5.1 ProtectService Mutation
- Mutation: `ProtectService(input: ProtectActionInput!)`
- Input fields:
  - controlKey: Service-specific key (e.g., "bedrock")
  - scope: Real AWS scope from CloudHierarchyList
  - identities: [] (empty array)
  - ssoActorIds: [] (empty array)

### 5.2 Service Type Mapping
- bedrock → "bedrock"
- s3 → "s3"
- rds → "rds"
- lambda → "lambda"
- sagemaker → "sagemaker"
- dynamodb → "dynamodb"

### 5.3 Scope Fetching
- CRITICAL: ALWAYS fetch real scopes from CloudHierarchyList
- NEVER construct scopes manually
- Use _fetch_all_account_scopes() method
- Format: "aws/r-{org}/{ou}/{account_id}"

### 5.4 Error Handling
- Handle API failures gracefully
- Show error message if protection fails
- Don't crash game on API errors
- Log errors with context

### 5.5 Success Response
- Returns: { success: bool, serviceName: str }
- success=true → Service protected
- success=false → Show error, allow retry

## 6. Game State Integration

### 6.1 Quest Messages
- quest_message: Optional[str] - Current quest message
- quest_message_timer: float - Time to display message
- service_hint_message: Optional[str] - Hint at bottom of screen
- service_hint_timer: float - Time to display hint

### 6.2 Service Statistics
- services_protected: int - Count of protected services
- Track across entire game session
- Display in UI/stats

### 6.3 Level-Specific Behavior
- Only trigger in Sandbox (Level 1) and Production (Level 6)
- No quests in other levels
- Quest state persists until completed or failed

## 7. Rendering Requirements

### 7.1 Service Icon Rendering
- Render in platformer levels only
- Layer: Above ground, below player
- Animation: Pulsing scale effect
- Position: Precise ground placement

### 7.2 Hacker Rendering
- Render only when quest is ACTIVE
- Standard entity rendering
- Same layer as zombies

### 7.3 Race Timer Display
- Top-center of screen
- Large, readable font
- Color-coded by time remaining
- Format: "XX.X seconds"

### 7.4 Service Hint Display
- Bottom banner below game area
- Shows when near service icon
- Message: "Walk close to protect the service!"
- Auto-dismiss when protected

## 8. Position Calculations

### 8.1 Ground Level
- Platformer ground: Y = 832
- Calculation: (60 tiles × 16) - (8 ground tiles × 16)
- Consistent across all platformer levels

### 8.2 Icon Placement
- Icon height: 48 pixels
- Icon Y position: ground_y - icon_height = 784
- Ensures icon sits ON ground, not below

### 8.3 Trigger Positions
- All quests: trigger at x=300
- Triggers shortly after level spawn
- Y position: 400 (mid-height)

### 8.4 Service Positions
- Sandbox: x=600 (early in level)
- Production: x=800 (slightly later)
- Both at y=784 (on ground)

## 9. Testing Requirements

### 9.1 Quest Flow Testing
1. Enter Sandbox level
2. Walk past x=300 → Dialog appears
3. Press ENTER → Hacker spawns, timer starts
4. Walk to Bedrock icon → Auto-protects when within 80px
5. Verify win/lose conditions

### 9.2 API Integration Testing
- Mock API for unit tests
- Real API for integration tests
- Verify scope fetching works
- Test error handling

### 9.3 Position Accuracy
- Icon must be on ground (not floating or buried)
- Hacker must land on ground
- Trigger must fire at correct x position

### 9.4 Timer Accuracy
- Countdown must be precise
- Color changes at correct thresholds
- Game over on timer expiry

## 10. Known Issues (From Previous Implementation)

### 10.1 Save/Load Error (Minor)
- Issue: 'Level' object has no attribute 'is_completed'
- Status: Non-critical, doesn't affect gameplay
- Game works fine, save/load still functional

### 10.2 Resolved Issues
- ✅ FIXED: Icon below ground (was Y=800, now Y=784)
- ✅ FIXED: E key not working (changed to auto-trigger)
- ✅ FIXED: Font crash (use self.ui_font instead of self.font)

## 11. Configuration

### 11.1 Quest Parameters
```python
QUEST_TIME_LIMIT = 60.0  # seconds
HACKER_SPEED = 150.0  # pixels/second
AUTO_PROTECT_RANGE = 80.0  # pixels
TRIGGER_X = 300.0  # pixels
```

### 11.2 Service Positions
```python
# Sandbox (Level 1)
SANDBOX_SERVICE_POS = Vector2(600, 784)

# Production (Level 6)
PRODUCTION_SERVICE_POS = Vector2(800, 784)
```

## Success Criteria

- ✅ Quest triggers at correct position in Sandbox and Production
- ✅ Warning dialog displays and dismisses correctly
- ✅ Hacker spawns and moves toward service icon
- ✅ Timer displays and counts down accurately
- ✅ Auto-protection works when player approaches icon
- ✅ Real Sonrai API called with correct parameters
- ✅ Win/lose conditions detected correctly
- ✅ Service icon positioned correctly on ground
- ✅ No crashes or errors during normal gameplay
- ✅ Quest state persists correctly until completion
