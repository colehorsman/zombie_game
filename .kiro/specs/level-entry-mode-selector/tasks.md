# Implementation Plan

## Overview
Implement a level entry mode selector that appears when entering Sandbox, allowing players to choose between Arcade Mode (API-light) and Story Mode (standard gameplay).

---

- [x] 1. Create LevelEntryMenuController
  - [x] 1.1 Create `src/level_entry_menu_controller.py` with LevelEntryAction enum and LevelEntryMenuController class
    - Implement OPTIONS and DESCRIPTIONS class attributes
    - Implement `__init__` with enabled and default_mode parameters
    - Implement `show(level_name)`, `hide()`, `navigate(direction)`, `select()`, `cancel()` methods
    - Implement `build_message(level_name)` with selection indicator and description
    - Implement `active` and `enabled` properties
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_

  - [x] 1.2 Write property tests for LevelEntryMenuController
    - **Property 1: Default Selection Respects Configuration**
    - **Validates: Requirements 1.1, 5.3**

  - [x] 1.3 Write property test for navigation
    - **Property 2: Navigation Wraps Within Bounds**
    - **Validates: Requirements 2.1, 2.4**

  - [x] 1.4 Write property test for selection
    - **Property 3: Selection Returns Correct Action**
    - **Validates: Requirements 2.2**

  - [x] 1.5 Write property test for cancel
    - **Property 4: Cancel Always Returns Cancel Action**
    - **Validates: Requirements 2.3**

  - [x] 1.6 Write property tests for message building
    - **Property 5: Message Contains Level Name**
    - **Property 6: Message Shows Correct Selection Indicator**
    - **Validates: Requirements 4.2, 2.4**

- [x] 2. Integrate with GameEngine
  - [x] 2.1 Add configuration reading in GameEngine.__init__
    - Read LEVEL_ENTRY_MODE_SELECTOR_ENABLED from environment (default: true)
    - Read DEFAULT_LEVEL_ENTRY_MODE from environment (default: "arcade")
    - Initialize LevelEntryMenuController with configuration
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 2.2 Modify door collision handling for Sandbox level
    - In `_handle_door_collision` or equivalent, check if entering Sandbox
    - If menu enabled, show LevelEntryMenuController instead of direct entry
    - Store pending level info for after selection
    - _Requirements: 3.1_

  - [x] 2.3 Add input handling for level entry menu
    - In `handle_input`, check if level_entry_menu_controller.active
    - Route UP/DOWN to navigate()
    - Route A/ENTER to select() and handle returned action
    - Route B/ESC to cancel() and return to lobby
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.4 Implement action handlers
    - ARCADE_MODE: Call existing `_begin_arcade_session()` flow (with photo booth if available)
    - STORY_MODE: Call existing `_enter_level()` with stored level info
    - CANCEL: Return to LOBBY status, clear pending level
    - _Requirements: 1.5, 3.2, 3.3, 3.4_

- [x] 3. Update Renderer
  - [x] 3.1 Add level entry menu rendering
    - Check if level_entry_menu_controller.active in render loop
    - Render menu message as overlay (reuse existing congratulations_message rendering)
    - Ensure purple theme consistency
    - _Requirements: 4.1, 4.3, 4.4_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Write integration tests
  - [ ] 5.1 Test door collision triggers menu for Sandbox
    - _Requirements: 3.1_
  - [ ] 5.2 Test arcade mode selection flows correctly
    - _Requirements: 1.5, 3.2_
  - [ ] 5.3 Test story mode selection flows correctly
    - _Requirements: 3.3_
  - [ ] 5.4 Test cancel returns to lobby
    - _Requirements: 3.4_
  - [ ] 5.5 Test disabled configuration skips menu
    - _Requirements: 5.2_

- [ ] 6. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
