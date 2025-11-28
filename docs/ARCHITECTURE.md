# Architecture Guide

This document explains the architectural patterns used in the zombie game codebase, particularly the controller extraction pattern used to improve maintainability.

## Controller Pattern

The codebase uses a **controller extraction pattern** to manage UI state and actions. This pattern was introduced to reduce the complexity of `game_engine.py` (originally 2,919 lines) and improve testability.

### Pattern Overview

Each controller:
1. Manages **state** for a specific UI element (visibility, options, selection)
2. Provides **actions** via an enum that the GameEngine can respond to
3. Has **no side effects** - the GameEngine handles all state changes
4. Is **independently testable** with comprehensive unit tests

### Controllers

#### PauseMenuController
**File:** `src/pause_menu_controller.py`
**Tests:** `tests/test_pause_menu_controller.py`

Manages the pause menu state including:
- Menu visibility
- Option selection and navigation
- Save confirmation dialog
- Dynamic options (arcade mode option for sandbox)

```python
class PauseMenuAction(Enum):
    NONE = auto()
    RESUME = auto()
    START_ARCADE = auto()
    RETURN_TO_LOBBY = auto()
    SAVE_GAME = auto()
    QUIT_GAME = auto()
```

#### ArcadeResultsController
**File:** `src/arcade_results_controller.py`
**Tests:** `tests/test_arcade_results_controller.py`

Manages the arcade mode results screen:
- Display of session statistics
- Menu navigation for post-game options
- Quarantine queue management UI

```python
class ArcadeResultsAction(Enum):
    NONE = auto()
    QUARANTINE_ALL = auto()
    DISCARD_QUEUE = auto()
    REPLAY = auto()
    EXIT_TO_LOBBY = auto()
```

#### CheatCodeController
**File:** `src/cheat_code_controller.py`
**Tests:** `tests/test_cheat_code_controller.py`

Handles cheat code detection:
- UNLOCK code (all levels)
- SKIP code (skip level)
- Konami code (spawn boss)
- Arcade code (start arcade mode)

```python
class CheatCodeAction(Enum):
    NONE = auto()
    UNLOCK_ALL_LEVELS = auto()
    SKIP_LEVEL = auto()
    SPAWN_BOSS = auto()
    START_ARCADE = auto()
```

#### BossDialogueController
**File:** `src/boss_dialogue_controller.py`
**Tests:** `tests/test_boss_dialogue_controller.py`

Manages boss introduction dialogues:
- Educational content about cyber attacks
- Formatted message building
- Dialogue state tracking

### Integration with GameEngine

Controllers are instantiated in `GameEngine.__init__()` and expose **backwards-compatible properties**:

```python
# GameEngine provides property delegates for compatibility
@property
def pause_menu_options(self) -> List[str]:
    return self.pause_menu_controller.options

@pause_menu_options.setter
def pause_menu_options(self, value: List[str]) -> None:
    self.pause_menu_controller.options = value
```

### Action Dispatch Pattern

The GameEngine handles side effects based on controller actions:

```python
def _execute_pause_menu_option(self) -> None:
    action = self.pause_menu_controller.select()

    if action == PauseMenuAction.RESUME:
        self._resume_game()
    elif action == PauseMenuAction.START_ARCADE:
        self._start_arcade_mode()
    elif action == PauseMenuAction.RETURN_TO_LOBBY:
        self._return_to_lobby()
    # ... handle other actions
```

## Key Design Principles

1. **Single Responsibility**: Each controller handles one UI element
2. **No Side Effects**: Controllers return actions, GameEngine executes them
3. **Testability**: Controllers can be tested without pygame or API mocks
4. **Backwards Compatibility**: Property delegates maintain existing API
5. **Enum-Based Actions**: Type-safe action handling with exhaustive matching

## Testing Strategy

Each controller has comprehensive tests covering:
- Initial state
- State transitions (show/hide)
- Navigation (up/down selection)
- Action selection
- Edge cases (empty options, invalid indices)
- Message building/formatting

Example test structure:
```python
class TestPauseMenuController:
    def test_initial_state(self): ...
    def test_show_with_arcade_option(self): ...
    def test_navigate_wraps_around(self): ...
    def test_select_returns_correct_action(self): ...
```

## File Structure

```
src/
├── game_engine.py           # Main game loop, action dispatch
├── pause_menu_controller.py # Pause menu state management
├── arcade_results_controller.py
├── cheat_code_controller.py
├── boss_dialogue_controller.py
└── ...

tests/
├── test_pause_menu_controller.py
├── test_arcade_results_controller.py
├── test_cheat_code_controller.py
├── test_boss_dialogue_controller.py
└── ...
```

## Future Refactoring Opportunities

Additional controllers that could be extracted:
- `GameStateController` - Level transitions, game status
- `InputController` - Keyboard/controller input handling
- `CollisionController` - Collision detection logic
- `ProjectileController` - Projectile management

The pattern scales well for future extractions while maintaining GameEngine as the central coordinator.
