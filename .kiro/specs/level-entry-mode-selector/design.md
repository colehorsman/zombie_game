# Design Document: Level Entry Mode Selector

## Overview

This feature introduces a mode selection menu when players enter levels, allowing them to choose between Arcade Mode (API-light, timed gameplay) and Story Mode (standard gameplay with real-time quarantine). The primary goal is to reduce Sonrai API load during AWS re:Invent 2025 by encouraging Arcade Mode play.

## Architecture

The feature follows the existing controller pattern used throughout the codebase (PauseMenuController, ArcadeResultsController, GameOverMenuController). A new `LevelEntryMenuController` will manage menu state, navigation, and selection.

```
┌─────────────────────────────────────────────────────────────┐
│                      GameEngine                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Door Collision Detection                │    │
│  │  (detects player entering Sandbox door)              │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           LevelEntryMenuController                   │    │
│  │  - show(level_name) → message                        │    │
│  │  - navigate(direction) → message                     │    │
│  │  - select() → LevelEntryAction                       │    │
│  │  - cancel() → LevelEntryAction.CANCEL                │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│            ┌────────────┼────────────┐                      │
│            ▼            ▼            ▼                      │
│     ARCADE_MODE    STORY_MODE     CANCEL                    │
│         │              │            │                       │
│         ▼              ▼            ▼                       │
│  _begin_arcade    _enter_level   return to                  │
│    _session()         ()          lobby                     │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### LevelEntryMenuController

```python
class LevelEntryAction(Enum):
    NONE = auto()
    ARCADE_MODE = auto()
    STORY_MODE = auto()
    CANCEL = auto()

class LevelEntryMenuController:
    """Manages level entry mode selection menu."""

    OPTIONS = ["🕹️ ARCADE MODE", "📖 STORY MODE"]
    DESCRIPTIONS = {
        0: "60-second timed challenge! Eliminate zombies for points.\nChoose to quarantine at the end.",
        1: "Standard gameplay. Each elimination triggers\nreal-time quarantine via Sonrai API."
    }

    def __init__(self, enabled: bool = True, default_mode: str = "arcade"):
        """Initialize with configuration."""

    def show(self, level_name: str) -> str:
        """Activate menu and return initial message."""

    def hide(self) -> None:
        """Deactivate menu."""

    def navigate(self, direction: int) -> str:
        """Navigate selection (-1=up, 1=down), return updated message."""

    def select(self) -> LevelEntryAction:
        """Confirm current selection, return action."""

    def cancel(self) -> LevelEntryAction:
        """Cancel menu, return CANCEL action."""

    def build_message(self, level_name: str) -> str:
        """Build menu message with current selection highlighted."""

    @property
    def active(self) -> bool:
        """Check if menu is currently active."""

    @property
    def enabled(self) -> bool:
        """Check if menu is enabled via configuration."""
```

### Integration Points

1. **Door Collision Handler** (`_handle_door_collision`):
   - Check if entering Sandbox level
   - If menu enabled, show LevelEntryMenuController instead of direct entry
   - Set game state to show menu overlay

2. **Input Handler** (`handle_input`):
   - When menu active, route input to menu navigation
   - Handle confirm (A/ENTER) and cancel (B/ESC)

3. **Renderer** (`renderer.py`):
   - Render menu overlay when active (reuse existing message rendering)

## Data Models

### Configuration

```python
# Environment variables (read in game_engine.py __init__)
LEVEL_ENTRY_MODE_SELECTOR_ENABLED = os.getenv("LEVEL_ENTRY_MODE_SELECTOR_ENABLED", "true").lower() == "true"
DEFAULT_LEVEL_ENTRY_MODE = os.getenv("DEFAULT_LEVEL_ENTRY_MODE", "arcade")  # "arcade" or "story"
```

### Game State Extension

```python
# Add to GameState or GameEngine
level_entry_menu_active: bool = False
pending_level_entry: Optional[str] = None  # Level name waiting for mode selection
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Default Selection Respects Configuration
*For any* valid default_mode configuration ("arcade" or "story"), when the menu is shown, the initial selected_index SHALL correspond to that mode (0 for arcade, 1 for story).
**Validates: Requirements 1.1, 5.3**

### Property 2: Navigation Wraps Within Bounds
*For any* starting selection index and navigation direction, the resulting selection index SHALL always be within [0, len(OPTIONS)-1] and SHALL change by exactly 1 position (with wrapping).
**Validates: Requirements 2.1, 2.4**

### Property 3: Selection Returns Correct Action
*For any* valid selection index, calling select() SHALL return the corresponding LevelEntryAction (index 0 → ARCADE_MODE, index 1 → STORY_MODE).
**Validates: Requirements 2.2**

### Property 4: Cancel Always Returns Cancel Action
*For any* menu state (any selection index, any level name), calling cancel() SHALL always return LevelEntryAction.CANCEL.
**Validates: Requirements 2.3**

### Property 5: Message Contains Level Name
*For any* level name string, the build_message output SHALL contain that level name.
**Validates: Requirements 4.2**

### Property 6: Message Shows Correct Selection Indicator
*For any* selection index, the build_message output SHALL contain "▶" prefix only for the selected option and "  " prefix for non-selected options.
**Validates: Requirements 2.4**

## Error Handling

1. **Invalid Configuration**: If DEFAULT_LEVEL_ENTRY_MODE is not "arcade" or "story", default to "arcade"
2. **Menu Already Active**: If show() called when already active, reset selection to default
3. **Navigation When Inactive**: Ignore navigation calls when menu is not active

## Testing Strategy

### Unit Tests
- Test controller initialization with various configurations
- Test navigation wrapping behavior
- Test selection returns correct actions
- Test message building with different selections
- Test enabled/disabled configuration

### Property-Based Tests (using Hypothesis)
- **Property 1**: Generate random valid configurations, verify default selection
- **Property 2**: Generate random starting indices and directions, verify bounds
- **Property 3**: Generate random selection indices, verify action mapping
- **Property 4**: Generate random menu states, verify cancel always returns CANCEL
- **Property 5**: Generate random level names, verify inclusion in message
- **Property 6**: Generate random selection indices, verify prefix placement

### Integration Tests
- Test door collision triggers menu for Sandbox
- Test arcade mode selection flows to photo booth/arcade session
- Test story mode selection flows to standard level entry
- Test cancel returns to lobby

### Testing Framework
- **Unit/Integration**: pytest
- **Property-Based**: hypothesis (already configured in project)
- **Minimum iterations**: 100 per property test
