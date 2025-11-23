# Service Protection Quest - Design

## Architecture Overview

The Service Protection Quest system integrates race-against-time gameplay with real Sonrai API service protection, teaching players about Cloud Permissions Firewall while providing exciting gameplay moments.

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                   GameEngine                            │
│  • Quest initialization                                 │
│  • Quest trigger detection                              │
│  • Race update logic                                    │
│  • Win/lose condition checking                          │
└───────────┬─────────────────────────────────────────────┘
            │
            ├──► ServiceProtectionQuestManager
            │    • Manages all quests
            │    • Tracks active quest
            │    • Handles quest state transitions
            │
            ├──► Hacker (NEW)
            │    • AI movement toward service
            │    • Physics (gravity, ground collision)
            │    • Rendering
            │
            ├──► ServiceNode (NEW)
            │    • Service icon rendering
            │    • Protection status
            │    • Visual states
            │
            ├──► SonraiAPIClient
            │    • protect_service() method
            │    • Scope fetching
            │    • Error handling
            │
            └──► Renderer
                 • Service icon rendering
                 • Race timer display
                 • Hacker character rendering
                 • Service hint messages
```

## Data Models

### ServiceProtectionQuest

```python
@dataclass
class ServiceProtectionQuest:
    """Represents a service protection race quest."""
    quest_id: str  # Unique identifier
    level: int  # Level number (1 or 6)
    service_type: str  # "bedrock", "s3", etc.
    trigger_position: Vector2  # Where quest triggers (x=300)
    service_position: Vector2  # Where service icon is located
    time_limit: float  # Race time limit (60.0 seconds)
    time_remaining: float  # Current countdown
    status: QuestStatus  # NOT_STARTED, TRIGGERED, ACTIVE, COMPLETED
    hacker_spawned: bool  # Whether hacker has been spawned
    player_won: bool  # Race outcome
```

### QuestStatus Enum

```python
class QuestStatus(Enum):
    """Quest progression states."""
    NOT_STARTED = "not_started"  # Quest exists, not triggered
    TRIGGERED = "triggered"  # Dialog shown, waiting for ENTER
    ACTIVE = "active"  # Hacker spawned, race in progress
    COMPLETED = "completed"  # Service protected successfully
```

### ServiceNode

```python
@dataclass
class ServiceNode:
    """Represents a protectable AWS service."""
    service_type: str  # "bedrock", "s3", "rds", etc.
    position: Vector2  # Icon location (x, y)
    protected: bool  # Protection status
    sprite_base: Surface  # Normal sprite (48x48)
    sprite_protected: Surface  # With green shield
    sprite_unprotected: Surface  # With red warning

    def get_current_sprite(self) -> Surface:
        """Returns appropriate sprite based on state."""
        if self.protected:
            return self.sprite_protected
        return self.sprite_base
```

### Hacker

```python
class Hacker:
    """AI character that races to compromise services."""
    position: Vector2  # Current position
    velocity: Vector2  # Movement velocity
    target_position: Vector2  # Service icon position
    speed: float  # 150 pixels/second
    grounded: bool  # Whether on ground
    sprite: Surface  # Red body, black hat, yellow eyes

    def __init__(self, spawn_position: Vector2, target: Vector2):
        """Initialize hacker above target position."""

    def update(self, delta_time: float, game_map) -> None:
        """Update physics and AI movement."""
        # Apply gravity if not grounded
        # Move horizontally toward target
        # Check ground collision

    def render(self, surface: Surface, camera_offset: Vector2) -> None:
        """Draw hacker sprite."""
```

## Quest Flow State Machine

```
NOT_STARTED
    │
    ├─► Player crosses x=300
    │
    ▼
TRIGGERED (Dialog shown)
    │
    ├─► Player presses ENTER
    │
    ▼
ACTIVE (Race begins)
    │
    ├─► Player reaches icon → API call → COMPLETED (WIN)
    │
    ├─► Hacker reaches icon → COMPLETED (LOSE - GAME OVER)
    │
    └─► Timer expires → COMPLETED (LOSE - GAME OVER)
```

## Implementation Details

### 1. Quest Initialization (GameEngine.__init__)

```python
def _initialize_quests(self):
    """Create quests for Sandbox and Production levels."""
    self.quest_manager = ServiceProtectionQuestManager()

    # Sandbox quest (Level 1)
    sandbox_quest = create_bedrock_protection_quest(
        quest_id="sandbox_bedrock",
        level=1,
        trigger_pos=Vector2(300, 400),
        service_pos=Vector2(600, 784)  # On ground!
    )
    self.quest_manager.add_quest(sandbox_quest)

    # Production quest (Level 6)
    prod_quest = create_bedrock_protection_quest(
        quest_id="production_bedrock",
        level=6,
        trigger_pos=Vector2(300, 400),
        service_pos=Vector2(800, 784)  # On ground!
    )
    self.quest_manager.add_quest(prod_quest)
```

### 2. Quest Trigger Detection (GameEngine._update_playing)

```python
def _update_playing(self, delta_time: float):
    # ... existing update logic ...

    # Check for quest triggers
    if self.quest_manager:
        active_quest = self.quest_manager.get_quest_for_level(
            self.game_state.current_level
        )

        if active_quest and active_quest.status == QuestStatus.NOT_STARTED:
            # Check if player crossed trigger position
            if self.player.position.x > active_quest.trigger_position.x:
                # Show warning dialog
                active_quest.status = QuestStatus.TRIGGERED
                self.game_state.quest_message = (
                    "⚠️ WARNING! ⚠️\n\n"
                    f"You have {active_quest.time_limit:.0f} SECONDS to protect "
                    "the Bedrock service before a hacker deletes Bedrock "
                    "guardrails allowing PROMPT INJECTION!\n\n"
                    "Press ENTER to begin the race!"
                )
                self.game_state.quest_message_timer = 999.0  # Show until dismissed
```

### 3. Hacker Spawn (GameEngine.handle_input)

```python
def handle_input(self, events: List[pygame.event.Event]):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Check if quest triggered and waiting for ENTER
                active_quest = self.quest_manager.get_active_quest()
                if active_quest and active_quest.status == QuestStatus.TRIGGERED:
                    # Dismiss dialog
                    self.game_state.quest_message = None

                    # Spawn hacker
                    spawn_x = active_quest.service_position.x
                    spawn_y = 100  # High in the sky
                    self.hacker = Hacker(
                        spawn_position=Vector2(spawn_x, spawn_y),
                        target=active_quest.service_position
                    )

                    # Start race
                    active_quest.status = QuestStatus.ACTIVE
                    active_quest.hacker_spawned = True

                    logger.info(f"🎮 Quest {active_quest.quest_id} started - race begins!")
```

### 4. Race Update Logic (GameEngine._update_playing)

```python
def _update_playing(self, delta_time: float):
    # ... existing logic ...

    # Update active quest
    if self.quest_manager:
        active_quest = self.quest_manager.get_active_quest()

        if active_quest and active_quest.status == QuestStatus.ACTIVE:
            # Update timer
            active_quest.time_remaining -= delta_time

            # Check time expired
            if active_quest.time_remaining <= 0:
                self._handle_quest_failure(active_quest, "Timer expired!")
                return

            # Update hacker
            if self.hacker:
                self.hacker.update(delta_time, self.game_map)

                # Check if hacker reached service
                hacker_dist = self._distance(
                    self.hacker.position,
                    active_quest.service_position
                )
                if hacker_dist < 50:  # Hacker reached icon
                    self._handle_quest_failure(active_quest, "Hacker reached service first!")
                    return

            # Check if player near service (auto-protect)
            player_dist = self._distance(
                self.player.position,
                active_quest.service_position
            )
            if player_dist < 80:  # Auto-protect range
                self._try_protect_service(active_quest)
```

### 5. Service Protection (GameEngine._try_protect_service)

```python
def _try_protect_service(self, quest: ServiceProtectionQuest) -> None:
    """Attempt to protect service via Sonrai API."""
    try:
        # Get service node
        service_node = self._get_service_node(quest.service_position)
        if service_node.protected:
            return  # Already protected

        # Call Sonrai API
        result = self.api_client.protect_service(
            service_type=quest.service_type,
            account_id=self.game_state.current_level_account_id,
            service_name=f"{quest.service_type.capitalize()} Service"
        )

        if result.success:
            # Success! Player won
            service_node.protected = True
            quest.status = QuestStatus.COMPLETED
            quest.player_won = True
            self.game_state.services_protected += 1

            # Stop hacker
            self.hacker = None

            # Show success message
            self.game_state.quest_message = (
                f"🛡️ SERVICE PROTECTED!\n\n"
                f"The {quest.service_type.capitalize()} service is now safe "
                "from unauthorized access!\n\n"
                "Press ENTER to continue"
            )
            self.game_state.quest_message_timer = 999.0

            logger.info(f"✅ PLAYER WON THE RACE! Service protected!")

        else:
            # API error
            logger.error(f"Failed to protect service: {result.error_message}")
            self.game_state.quest_message = (
                f"⚠️ Protection failed: {result.error_message}\n\n"
                "Try again!"
            )
            self.game_state.quest_message_timer = 3.0

    except Exception as e:
        logger.error(f"Exception protecting service: {e}")
        self.game_state.quest_message = f"Error: {str(e)}"
        self.game_state.quest_message_timer = 3.0
```

### 6. Quest Failure (GameEngine._handle_quest_failure)

```python
def _handle_quest_failure(self, quest: ServiceProtectionQuest, reason: str) -> None:
    """Handle quest failure (hacker won or time expired)."""
    quest.status = QuestStatus.COMPLETED
    quest.player_won = False

    # Remove hacker
    self.hacker = None

    # Show game over message
    self.game_state.congratulations_message = (
        "💀 GAME OVER\n\n"
        f"{reason}\n\n"
        "The hacker compromised the Bedrock service and injected "
        "malicious prompts into the AI system!\n\n"
        "Press ESC to return to lobby"
    )

    logger.info(f"❌ QUEST FAILED: {reason}")

    # Optionally: Force return to lobby or restart level
```

## Sonrai API Integration

### ProtectService Mutation

```graphql
mutation protectService($input: ProtectActionInput!) {
    ProtectService(input: $input) {
        success
        serviceName
    }
}
```

### Service Type to Control Key Mapping

```python
SERVICE_CONTROL_KEYS = {
    "bedrock": "bedrock",
    "s3": "s3",
    "rds": "rds",
    "lambda": "lambda",
    "sagemaker": "sagemaker",
    "dynamodb": "dynamodb"
}
```

### Scope Fetching (CRITICAL)

```python
def protect_service(self, service_type: str, account_id: str, service_name: str):
    """Protect an AWS service via Sonrai API."""
    # 1. Get control key
    control_key = SERVICE_CONTROL_KEYS.get(service_type)
    if not control_key:
        return QuarantineResult(False, "", f"Unknown service type: {service_type}")

    # 2. Fetch REAL scope from API (NEVER construct manually!)
    scope = self._fetch_all_account_scopes().get(account_id)
    if not scope:
        return QuarantineResult(False, "", f"No scope found for account {account_id}")

    # 3. Call ProtectService mutation
    mutation = """
        mutation protectService($input: ProtectActionInput!) {
            ProtectService(input: $input) {
                success
                serviceName
            }
        }
    """

    variables = {
        "input": {
            "controlKey": control_key,
            "scope": scope,  # Real scope from CloudHierarchyList!
            "identities": [],
            "ssoActorIds": []
        }
    }

    # Execute and return result
```

## Rendering Components

### 1. Service Icon Rendering (Renderer.render_service_nodes)

```python
def render_service_nodes(self, surface: Surface, camera_offset: Vector2):
    """Render service protection icons."""
    if not self.game_engine.service_nodes:
        return

    for node in self.game_engine.service_nodes:
        # Calculate screen position
        screen_x = node.position.x - camera_offset.x
        screen_y = node.position.y - camera_offset.y

        # Pulsing animation if quest is active
        scale = 1.0
        if self._is_quest_active_for_node(node):
            pulse = math.sin(time.time() * 3.0) * 0.1 + 1.0
            scale = pulse

        # Scale sprite
        sprite = node.get_current_sprite()
        if scale != 1.0:
            new_size = (int(48 * scale), int(48 * scale))
            sprite = pygame.transform.scale(sprite, new_size)

        # Center scaled sprite
        x = screen_x - sprite.get_width() // 2
        y = screen_y - sprite.get_height() // 2

        surface.blit(sprite, (x, y))
```

### 2. Race Timer Display (Renderer.render_race_timer)

```python
def render_race_timer(self, surface: Surface):
    """Render countdown timer at top of screen."""
    active_quest = self.game_engine.quest_manager.get_active_quest()
    if not active_quest or active_quest.status != QuestStatus.ACTIVE:
        return

    # Choose color based on time remaining
    time_left = active_quest.time_remaining
    if time_left > 30:
        color = (0, 255, 0)  # Green
    elif time_left > 15:
        color = (255, 165, 0)  # Orange
    else:
        color = (255, 0, 0)  # Red

    # Render timer text
    timer_text = f"{time_left:.1f} seconds"
    text_surface = self.ui_font.render(timer_text, True, color)

    # Position at top center
    x = (surface.get_width() - text_surface.get_width()) // 2
    y = 20

    # Background for readability
    bg_rect = text_surface.get_rect(topleft=(x - 5, y - 5))
    bg_rect.inflate_ip(10, 10)
    pygame.draw.rect(surface, (0, 0, 0), bg_rect)
    pygame.draw.rect(surface, color, bg_rect, 2)

    surface.blit(text_surface, (x, y))
```

### 3. Hacker Rendering (Hacker.render)

```python
def render(self, surface: Surface, camera_offset: Vector2):
    """Render hacker character."""
    screen_x = self.position.x - camera_offset.x
    screen_y = self.position.y - camera_offset.y

    # Red body (24x32)
    body_rect = pygame.Rect(screen_x, screen_y, 24, 32)
    pygame.draw.rect(surface, (200, 0, 0), body_rect)

    # Black hat (30x8)
    hat_rect = pygame.Rect(screen_x - 3, screen_y - 8, 30, 8)
    pygame.draw.rect(surface, (0, 0, 0), hat_rect)

    # Yellow eyes (4x4 each)
    left_eye = pygame.Rect(screen_x + 6, screen_y + 8, 4, 4)
    right_eye = pygame.Rect(screen_x + 14, screen_y + 8, 4, 4)
    pygame.draw.rect(surface, (255, 255, 0), left_eye)
    pygame.draw.rect(surface, (255, 255, 0), right_eye)
```

## File Structure

```
src/
├── hacker.py (NEW)                     # Hacker AI and rendering
├── service_protection_quest.py (NEW)   # Quest system
├── bedrock_sprite.py (NEW)             # Bedrock icon generation
├── game_engine.py (MODIFIED)           # Quest integration
├── sonrai_client.py (MODIFIED)         # protect_service() method
├── renderer.py (MODIFIED)              # Service/timer rendering
├── models.py (MODIFIED)                # Quest state fields
└── main.py (MODIFIED)                  # Render calls

docs/sonrai-api/queries/
└── protect-service.md (NEW)            # API documentation
```

## Performance Considerations

- Quest updates only run when quest is ACTIVE
- Hacker physics runs at same rate as other entities
- Service icon rendering is lightweight (pre-generated sprites)
- Timer display updates every frame (minimal overhead)

## Error Handling

### API Errors
- Network failures → Show error message, allow retry
- Invalid scope → Log error, don't crash
- Missing service type → Validate before API call

### Game Errors
- Quest not found → Skip quest logic
- Missing hacker → Check for null before update
- Invalid positions → Use default fallbacks

## Testing Strategy

### Unit Tests
- Quest state transitions
- Hacker AI movement
- Distance calculations
- Service node creation

### Integration Tests
- Full quest flow from trigger to completion
- API calls with mocked responses
- Timer countdown accuracy
- Win/lose condition detection

### Manual Tests
- Visual verification of icon placement
- Hacker spawn and movement
- Timer color changes
- Dialog appearance and dismissal

## Future Enhancements

- Multiple hacker types (faster, smarter)
- Co-op mode (player + AI helper)
- More services (S3, RDS, Lambda quests)
- Difficulty scaling (shorter timers in Production)
- Achievements (win all races, win with <10s remaining)
