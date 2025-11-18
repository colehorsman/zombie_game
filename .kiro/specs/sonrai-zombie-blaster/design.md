# Design Document

## Overview

The Sonrai Zombie Blaster is a 2D retro-style game built with Python and Pygame that integrates with the Sonrai Security API to visualize and remediate unused AWS identities. The game features a side-scrolling shooter mechanic where each zombie represents a real unused identity, and eliminating zombies triggers actual quarantine actions through the API.

The architecture follows a clean separation between game logic, rendering, and API integration, allowing the game to function as both an engaging visualization tool and a practical security remediation interface.

## Architecture

The system is organized into the following layers:

```
┌─────────────────────────────────────────┐
│         Game Loop & Main Entry          │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼─────────┐
│  Game Engine   │    │   API Client     │
│  - Physics     │    │   - Auth         │
│  - Collision   │    │   - Queries      │
│  - State Mgmt  │    │   - Quarantine   │
└───────┬────────┘    └────────┬─────────┘
        │                      │
┌───────▼────────┐    ┌────────▼─────────┐
│   Renderer     │    │   Data Models    │
│  - Sprites     │    │   - Zombie       │
│  - UI          │    │   - Player       │
│  - Animation   │    │   - Projectile   │
└────────────────┘    └──────────────────┘
```

### Technology Stack

- **Language**: Python 3.11+
- **Game Framework**: Pygame 2.5+
- **HTTP Client**: requests library for Sonrai API integration
- **Configuration**: python-dotenv for environment variable management
- **Testing**: pytest for unit tests, Hypothesis for property-based testing

## Components and Interfaces

### 1. Game Engine (`game_engine.py`)

The core game loop and state management component.

```python
class GameEngine:
    def __init__(self, api_client: SonraiAPIClient)
    def start() -> None
    def update(delta_time: float) -> None
    def handle_input(events: List[Event]) -> None
    def is_running() -> bool
    def get_game_state() -> GameState
```

**Responsibilities:**
- Main game loop execution (target 60 FPS)
- Delta time calculation for frame-independent physics
- Input event processing and delegation
- Game state transitions (menu, playing, victory, error)
- Collision detection between projectiles and zombies
- Zombie elimination and API quarantine coordination

### 2. Sonrai API Client (`sonrai_client.py`)

Handles all communication with the Sonrai Security API.

```python
class SonraiAPIClient:
    def __init__(self, api_url: str, api_key: str, api_secret: str)
    def authenticate() -> bool
    def fetch_unused_identities(limit: int = 1000) -> List[UnusedIdentity]
    def quarantine_identity(identity_id: str) -> QuarantineResult
    def get_connection_status() -> bool
```

**Responsibilities:**
- API authentication and token management
- Fetching unused identity data
- Sending quarantine requests
- Error handling and retry logic
- Connection health monitoring

### 3. Renderer (`renderer.py`)

Manages all visual output using Pygame.

```python
class Renderer:
    def __init__(self, screen: pygame.Surface)
    def render_player(player: Player) -> None
    def render_zombies(zombies: List[Zombie]) -> None
    def render_zombie_labels(zombies: List[Zombie]) -> None
    def render_projectiles(projectiles: List[Projectile]) -> None
    def render_ui(game_state: GameState) -> None
    def render_background() -> None
    def render_message_bubble(message: str) -> None
    def clear_screen() -> None
```

**Responsibilities:**
- Sprite rendering with simple 2D graphics
- Zombie numeric identifier rendering above sprites
- Retro Game Boy-style message bubble rendering
- UI overlay (zombie count, errors, statistics)
- Background scrolling effect
- Frame buffer management

### 4. Player (`player.py`)

Represents the controllable character.

```python
class Player:
    position: Vector2
    velocity: Vector2
    sprite: pygame.Surface
    
    def move_left() -> None
    def move_right() -> None
    def fire_projectile() -> Projectile
    def update(delta_time: float) -> None
    def get_bounds() -> Rect
```

### 5. Zombie (`zombie.py`)

Represents an unused identity as a game entity.

```python
class Zombie:
    identity_id: str
    identity_name: str
    position: Vector2
    sprite: pygame.Surface
    is_quarantining: bool
    display_number: Optional[int]
    
    def update(delta_time: float) -> None
    def get_bounds() -> Rect
    def mark_for_quarantine() -> None
    def extract_test_user_number() -> Optional[int]
```

### 6. Projectile (`projectile.py`)

Represents fired shots from the player.

```python
class Projectile:
    position: Vector2
    velocity: Vector2
    
    def update(delta_time: float) -> None
    def get_bounds() -> Rect
    def is_off_screen() -> bool
```

## Data Models

### UnusedIdentity

Represents data from the Sonrai API about an unused AWS identity.

```python
@dataclass
class UnusedIdentity:
    identity_id: str
    identity_name: str
    identity_type: str  # IAM user, role, service account
    last_used: Optional[datetime]
    risk_score: float
```

### GameState

Tracks the current state of the game.

```python
@dataclass
class GameState:
    status: GameStatus  # MENU, PLAYING, PAUSED, VICTORY, ERROR
    zombies_remaining: int
    zombies_quarantined: int
    total_zombies: int
    error_message: Optional[str]
    congratulations_message: Optional[str]
    play_time: float
```

### QuarantineResult

Response from API quarantine operation.

```python
@dataclass
class QuarantineResult:
    success: bool
    identity_id: str
    error_message: Optional[str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: One-to-one zombie mapping

*For any* game session, the number of Zombie Entities created should equal the number of unused identities returned by the Sonrai API
**Validates: Requirements 1.2**

### Property 2: Game state display accuracy

*For any* game state, the displayed zombie count should equal zombies_remaining, the displayed quarantined count should equal zombies_quarantined, and the sum of zombies_remaining and zombies_quarantined should equal total_zombies
**Validates: Requirements 1.3, 7.1, 7.4**

### Property 3: Quarantine triggers on elimination

*For any* Zombie Entity that is eliminated by projectile collision, a quarantine request should be sent to the Sonrai API with the correct identity_id
**Validates: Requirements 3.1**

### Property 4: Successful quarantine removes zombie

*For any* quarantine request that succeeds, the corresponding Zombie Entity should be permanently removed from the game
**Validates: Requirements 3.2**

### Property 5: Failed quarantine restoration

*For any* quarantine request that fails, the corresponding Zombie Entity should remain in or be restored to the game and an error notification should be displayed
**Validates: Requirements 3.3**

### Property 6: Player boundary constraint

*For any* player movement input, the Player Character position should remain within the defined screen boundaries
**Validates: Requirements 2.4**

### Property 7: Projectile creation from player position

*For any* player position, when the fire action is triggered, a projectile should be created at the Player Character's current position
**Validates: Requirements 2.2**

### Property 8: Collision detection accuracy

*For any* projectile and zombie with overlapping bounding boxes, the collision detection should identify them as colliding and trigger zombie elimination
**Validates: Requirements 2.3**

### Property 9: Pending quarantine prevents re-targeting

*For any* Zombie Entity with a pending quarantine request, the Game System should prevent that zombie from being targeted by additional projectiles until the request completes
**Validates: Requirements 3.4**

### Property 10: Movement input processing

*For any* valid movement input (left or right), the Player Character should move in the corresponding direction at a consistent speed
**Validates: Requirements 2.1**

### Property 11: Simultaneous input handling

*For any* combination of simultaneous valid inputs (movement and fire), the Game System should process all inputs without conflicts or dropped commands
**Validates: Requirements 2.5**

### Property 12: Background scrolling continuity

*For any* player position near the visible area edge, the background should scroll to maintain the player within the playable zone and create continuous movement
**Validates: Requirements 5.2**

### Property 13: Zombie spawn distribution

*For any* set of spawned Zombie Entities, their positions should be distributed across the level space rather than clustered in a single location
**Validates: Requirements 5.3**

### Property 14: Physics consistency during scroll

*For any* scroll state, collision detection and physics calculations should produce consistent results regardless of the current scroll offset
**Validates: Requirements 5.4**

### Property 15: API authentication headers

*For any* API request made to the Sonrai API, the request headers should include valid authentication tokens
**Validates: Requirements 6.2**

### Property 16: API credential security

*For any* source code file in the repository, API credentials should not be hardcoded in the file contents
**Validates: Requirements 6.5**

### Property 17: Display update responsiveness

*For any* game state change (zombie elimination, quarantine completion), the displayed counts should update within one second
**Validates: Requirements 7.2**

### Property 18: Error logging

*For any* error condition encountered during game execution, error details should be logged to the logging system
**Validates: Requirements 8.4**

### Property 19: Resource cleanup on exit

*For any* game exit scenario (normal or error), all resources (API connections, file handles, display) should be properly closed and cleaned up
**Validates: Requirements 8.5**

### Property 20: Test user number extraction

*For any* identity name matching the pattern "test-user-{number}", the extracted display number should equal the numeric portion of the identity name
**Validates: Requirements 9.1, 9.2**

### Property 21: Zombie label position synchronization

*For any* zombie position and scroll offset, the rendered numeric label should be positioned directly above the zombie sprite at the correct screen coordinates
**Validates: Requirements 9.3, 9.4**

### Property 22: Game pause on zombie elimination

*For any* successful zombie elimination, the game should transition to PAUSED state and display a congratulations message
**Validates: Requirements 10.1, 10.2**

### Property 23: Congratulations message format

*For any* eliminated zombie with identity name, the congratulations message should contain the text "You leveraged the Cloud Permissions Firewall to quarantine" followed by the zombie's identity name
**Validates: Requirements 10.3**

### Property 24: Game resume after message dismissal

*For any* paused game state with a congratulations message, when the player provides dismissal input, the game should transition back to PLAYING state
**Validates: Requirements 10.4, 10.5**

## Error Handling

### API Connection Errors

- **Scenario**: Sonrai API is unreachable or returns connection errors
- **Handling**: Display error overlay, prevent game start, provide retry option
- **User Feedback**: "Unable to connect to Sonrai API. Check your network connection and credentials."

### Authentication Failures

- **Scenario**: Invalid API credentials or expired tokens
- **Handling**: Display configuration error, exit gracefully, log error details
- **User Feedback**: "Authentication failed. Please check your API credentials in the .env file."

### Quarantine Request Failures

- **Scenario**: Individual quarantine request fails (permissions, network, etc.)
- **Handling**: Show notification, restore zombie, log error, allow retry
- **User Feedback**: "Failed to quarantine identity: {identity_name}. Error: {error_message}"

### Missing Configuration

- **Scenario**: Required environment variables are not set
- **Handling**: Display helpful error message with setup instructions, exit gracefully
- **User Feedback**: "Missing configuration. Please create a .env file with SONRAI_API_URL, SONRAI_API_KEY, and SONRAI_API_SECRET."

### Pygame Initialization Failures

- **Scenario**: Pygame cannot initialize display or audio
- **Handling**: Log error details, attempt fallback configuration, exit if critical
- **User Feedback**: "Failed to initialize game display. Please check your graphics drivers."

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

- **API Client**: Test authentication flow, error responses, retry logic
- **Collision Detection**: Test boundary cases (exact overlap, near miss, corner collision)
- **Player Movement**: Test boundary constraints, input handling
- **Game State**: Test state transitions, counter updates
- **Configuration Loading**: Test missing variables, invalid formats

### Property-Based Testing

Property-based tests will use Hypothesis to verify universal properties across many inputs:

- **Framework**: Hypothesis 6.0+ for Python
- **Configuration**: Minimum 100 iterations per property test
- **Tagging**: Each test will reference its design document property using the format:
  `# Feature: sonrai-zombie-blaster, Property {N}: {property_text}`

Property tests will generate:
- Random game states with varying zombie counts
- Random player positions and velocities
- Random collision scenarios with multiple entities
- Random API responses (success, failure, empty)
- Random delta time values for frame independence testing

### Integration Testing

- Test full game loop with mocked API responses
- Test API client with Sonrai API sandbox/test environment
- Test rendering pipeline with headless Pygame mode

### Manual Testing

- Visual verification of sprite rendering and animations
- Gameplay feel and responsiveness testing
- End-to-end flow with real Sonrai API (in development environment)

## Implementation Notes

### Pygame Setup

The game will use a fixed resolution of 800x600 pixels with simple pixel art sprites. The player sprite will be approximately 32x32 pixels, zombies 24x24 pixels, and projectiles 8x8 pixels.

### API Rate Limiting

The Sonrai API client will implement exponential backoff for failed requests and respect any rate limits specified in API responses.

### Sprite Design

All sprites will be created programmatically using Pygame's drawing functions to maintain the simple retro aesthetic:
- Player: Blue rectangle with a small "gun" protrusion
- Zombie: Green rectangle with simple facial features
- Projectile: Yellow circle
- Background: Scrolling gray grid pattern
- Message Bubble: White rounded rectangle with black border and retro pixelated font, styled like classic Game Boy dialog boxes

### Configuration

The game will use a `.env` file for configuration:
```
SONRAI_API_URL=https://api.sonraisecurity.com
SONRAI_API_KEY=your_api_key
SONRAI_API_SECRET=your_api_secret
GAME_WIDTH=800
GAME_HEIGHT=600
TARGET_FPS=60
```

### Performance Considerations

- Zombie entities will be spatially partitioned for efficient collision detection
- Sprites will be cached and reused rather than recreated each frame
- API calls will be asynchronous to prevent blocking the game loop
- Maximum of 1000 zombies will be rendered with simple culling for off-screen entities
