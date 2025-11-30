# Requirements Document

## Introduction

This feature adds a mode selection menu when entering levels (starting with Sandbox). Players choose between "Arcade Mode" (timed gameplay, no API calls) or "Story Mode" (standard gameplay with real quarantine actions). This is critical for AWS re:Invent 2025 to reduce Sonrai API load while maintaining engaging gameplay for booth visitors.

## Glossary

- **Level_Entry_Menu**: A modal dialog displayed when a player enters a level through a door, presenting gameplay mode options
- **Arcade_Mode**: Time-limited gameplay mode where zombie eliminations are queued but not sent to Sonrai API until session end (player chooses whether to quarantine)
- **Story_Mode**: Standard gameplay where zombie eliminations trigger immediate Sonrai API quarantine calls
- **Mode_Selector**: The UI component that displays mode options and handles player selection

## Requirements

### Requirement 1

**User Story:** As a booth operator at re:Invent, I want players to be encouraged to play Arcade Mode, so that the Sonrai API is not overwhelmed by continuous quarantine requests from multiple simultaneous players.

#### Acceptance Criteria

1. WHEN a player enters the Sandbox level door THEN the Level_Entry_Menu SHALL display with Arcade Mode as the default/highlighted option
2. WHEN the Level_Entry_Menu is displayed THEN the Mode_Selector SHALL show "🕹️ ARCADE MODE" and "📖 STORY MODE" as selectable options
3. WHEN Arcade Mode is highlighted THEN the Level_Entry_Menu SHALL display a description: "60-second timed challenge! Eliminate zombies for points. Choose to quarantine at the end."
4. WHEN Story Mode is highlighted THEN the Level_Entry_Menu SHALL display a description: "Standard gameplay. Each elimination triggers real-time quarantine via Sonrai API."
5. WHEN the player selects Arcade Mode THEN the system SHALL proceed to the existing photo booth consent flow (if available) or directly start arcade session

### Requirement 2

**User Story:** As a player, I want to navigate the mode selection menu with keyboard or controller, so that I can choose my preferred gameplay experience.

#### Acceptance Criteria

1. WHEN the Level_Entry_Menu is active THEN the system SHALL accept UP/DOWN navigation via keyboard (arrow keys, W/S) and controller (D-pad)
2. WHEN the player presses A button or ENTER THEN the system SHALL confirm the highlighted selection
3. WHEN the player presses B button or ESC THEN the system SHALL cancel and return to the lobby
4. WHEN navigation occurs THEN the Mode_Selector SHALL provide visual feedback by highlighting the selected option with "▶" prefix

### Requirement 3

**User Story:** As a developer, I want the mode selection to integrate cleanly with existing door entry logic, so that the feature can be implemented without major refactoring.

#### Acceptance Criteria

1. WHEN a door collision is detected for Sandbox level THEN the system SHALL pause normal door entry and display the Level_Entry_Menu
2. WHEN the player confirms Arcade Mode THEN the system SHALL call the existing `_begin_arcade_session()` flow
3. WHEN the player confirms Story Mode THEN the system SHALL proceed with standard level loading via `_enter_level()`
4. WHEN the player cancels THEN the system SHALL return to LOBBY status without entering the level

### Requirement 4

**User Story:** As a booth operator, I want the menu to be visually clear and quick to navigate, so that players don't get confused or delayed at the booth.

#### Acceptance Criteria

1. WHEN the Level_Entry_Menu is displayed THEN the system SHALL render it as a centered modal overlay with semi-transparent background
2. WHEN the menu is displayed THEN the system SHALL show the level name at the top (e.g., "ENTERING: SANDBOX")
3. WHEN the menu is displayed THEN the system SHALL show controller hints at the bottom (e.g., "A/ENTER: Select | B/ESC: Cancel")
4. WHEN the menu renders THEN the system SHALL use the existing purple theme consistent with other game menus

### Requirement 5

**User Story:** As a system administrator, I want the mode selector to be configurable, so that we can enable/disable it or change default behavior without code changes.

#### Acceptance Criteria

1. WHEN the game initializes THEN the system SHALL read a `LEVEL_ENTRY_MODE_SELECTOR_ENABLED` configuration (default: True)
2. WHEN `LEVEL_ENTRY_MODE_SELECTOR_ENABLED` is False THEN the system SHALL skip the menu and proceed directly to Story Mode (legacy behavior)
3. WHEN the configuration specifies `DEFAULT_MODE` THEN the Mode_Selector SHALL highlight that mode by default (default: "arcade")
