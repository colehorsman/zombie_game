# Implementation Plan: Service Protection Quest

## Phase 1: Foundation - Data Models and Quest System

- [ ] 1. Create QuestStatus enum
  - Add QuestStatus enum to models.py
  - States: NOT_STARTED, TRIGGERED, ACTIVE, COMPLETED
  - _Requirements: 1.2_

- [ ] 2. Create ServiceProtectionQuest data model
  - Add ServiceProtectionQuest dataclass to models.py
  - Fields: quest_id, level, service_type, trigger_position, service_position
  - Fields: time_limit, time_remaining, status, hacker_spawned, player_won
  - _Requirements: 1.4_

- [ ] 3. Create ServiceNode data model
  - Create src/service_protection_quest.py
  - Add ServiceNode dataclass
  - Fields: service_type, position, protected, sprite_base, sprite_protected, sprite_unprotected
  - Add get_current_sprite() method
  - _Requirements: 3.1, 3.3_

- [ ] 4. Create ServiceProtectionQuestManager
  - Add ServiceProtectionQuestManager class to service_protection_quest.py
  - Add quest list and active quest tracking
  - Methods: add_quest(), get_quest_for_level(), get_active_quest()
  - _Requirements: 1.4_

- [ ] 5. Create quest factory function
  - Add create_bedrock_protection_quest() to service_protection_quest.py
  - Parameters: quest_id, level, trigger_pos, service_pos
  - Returns: ServiceProtectionQuest instance with 60s time limit
  - _Requirements: 1.1, 1.4_

- [ ] 6. Add quest state fields to GameState
  - Add quest_message: Optional[str]
  - Add quest_message_timer: float
  - Add service_hint_message: Optional[str]
  - Add service_hint_timer: float
  - Add services_protected: int
  - _Requirements: 6.1, 6.2_

- [ ] 7. Checkpoint - Test quest system data models
  - Ensure all tests pass, ask the user if questions arise

## Phase 2: Bedrock Service Icon

- [ ] 8. Create Bedrock sprite generator
  - Create src/bedrock_sprite.py
  - Function: generate_bedrock_sprite() -> Surface (48x48px)
  - Blue-to-purple gradient hexagonal blocks
  - 8-bit retro style
  - _Requirements: 3.1_

- [ ] 9. Add sprite state variants
  - Function: generate_bedrock_protected() -> Surface with green shield overlay
  - Function: generate_bedrock_unprotected() -> Surface with red warning
  - Shield: Semi-transparent overlay, pulsing effect
  - _Requirements: 3.1_

- [ ] 10. Add sprite generation to ServiceNode creation
  - Update ServiceNode initialization
  - Generate all three sprite variants
  - Store in sprite_base, sprite_protected, sprite_unprotected
  - _Requirements: 3.1, 3.3_

- [ ] 11. Calculate ground position constants
  - Add PLATFORMER_GROUND_Y = 832 constant
  - Add SERVICE_ICON_HEIGHT = 48 constant
  - Add SERVICE_ICON_Y = PLATFORMER_GROUND_Y - SERVICE_ICON_HEIGHT = 784
  - Document position calculations
  - _Requirements: 8.1, 8.2_

- [ ] 12. Checkpoint - Test service icon rendering
  - Ensure all tests pass, ask the user if questions arise

## Phase 3: Hacker Character

- [ ] 13. Create Hacker class
  - Create src/hacker.py
  - Add Hacker class with position, velocity, target_position, speed, grounded
  - Initialize with spawn_position (high in sky) and target (service position)
  - _Requirements: 2.1, 2.2_

- [ ] 14. Implement hacker sprite rendering
  - Add render() method to Hacker class
  - Red body: 24x32 rectangle
  - Black hat: 30x8 rectangle at top
  - Yellow eyes: Two 4x4 rectangles
  - _Requirements: 2.2_

- [ ] 15. Implement hacker physics
  - Add gravity constant: GRAVITY = 500.0
  - Apply gravity when not grounded
  - Check ground collision using game_map
  - Set grounded = True when hitting ground
  - _Requirements: 2.4_

- [ ] 16. Implement hacker AI movement
  - Move horizontally toward target_position
  - Speed: 150 pixels/second
  - Only move horizontally (X axis)
  - Stop when reached target (within 50 pixels)
  - _Requirements: 2.3_

- [ ] 17. Add hacker update method
  - Add update(delta_time, game_map) method
  - Apply gravity if not grounded
  - Move toward target if grounded
  - Update position based on velocity
  - _Requirements: 2.3, 2.4_

- [ ] 18. Checkpoint - Test hacker character
  - Ensure all tests pass, ask the user if questions arise

## Phase 4: Quest Integration into GameEngine

- [ ] 19. Initialize quest manager in GameEngine
  - Add self.quest_manager to GameEngine.__init__()
  - Create ServiceProtectionQuestManager instance
  - Add self.hacker = None for active hacker
  - _Requirements: 1.1_

- [ ] 20. Create quest initialization method
  - Add _initialize_quests() to GameEngine
  - Create Sandbox quest: level=1, trigger=300, service=600
  - Create Production quest: level=6, trigger=300, service=800
  - Both at y=784 (on ground)
  - Call from __init__() after level manager setup
  - _Requirements: 1.1, 8.2, 8.3, 8.4_

- [ ] 21. Add service nodes list to GameEngine
  - Add self.service_nodes: List[ServiceNode] = []
  - Create service nodes when entering platformer levels
  - Clear service nodes when returning to lobby
  - _Requirements: 3.3, 6.3_

- [ ] 22. Implement quest trigger detection
  - In _update_playing(), check for active quest
  - If quest is NOT_STARTED and player.position.x > trigger_position.x
  - Set quest.status = TRIGGERED
  - Show warning dialog message
  - _Requirements: 1.1, 1.3_

- [ ] 23. Implement hacker spawn on ENTER
  - In handle_input(), check for ENTER key
  - If quest.status == TRIGGERED, dismiss dialog
  - Spawn hacker at service_position.x, y=100 (sky)
  - Set quest.status = ACTIVE
  - Set quest.hacker_spawned = True
  - _Requirements: 1.2, 2.1_

- [ ] 24. Add quest update logic
  - In _update_playing(), update active quest
  - Decrement quest.time_remaining by delta_time
  - Check if time_remaining <= 0 → Handle failure
  - Update hacker if spawned
  - _Requirements: 4.1, 4.4_

- [ ] 25. Checkpoint - Test quest trigger and spawn
  - Ensure all tests pass, ask the user if questions arise

## Phase 5: Race Mechanics

- [ ] 26. Implement distance calculation helper
  - Add _distance(pos1: Vector2, pos2: Vector2) -> float method
  - Calculate Euclidean distance between two positions
  - Used for player/hacker proximity to service
  - _Requirements: 4.5_

- [ ] 27. Check hacker reaching service
  - In quest update, calculate distance(hacker.position, service_position)
  - If distance < 50 pixels → Hacker won
  - Call _handle_quest_failure(quest, "Hacker reached service first!")
  - _Requirements: 4.4_

- [ ] 28. Implement auto-protection check
  - Calculate distance(player.position, service_position)
  - If distance < 80 pixels AND service not protected
  - Call _try_protect_service(quest)
  - _Requirements: 4.2_

- [ ] 29. Create _try_protect_service() method
  - Add method to GameEngine
  - Get service node from service_nodes list
  - Check if already protected (skip if true)
  - Call api_client.protect_service(service_type, account_id, service_name)
  - Handle success → Set protected=True, quest.status=COMPLETED, player_won=True
  - Handle failure → Show error message
  - _Requirements: 4.2, 4.3, 5.1_

- [ ] 30. Create _handle_quest_failure() method
  - Add method to GameEngine
  - Parameters: quest, reason (string)
  - Set quest.status = COMPLETED, player_won = False
  - Remove hacker (self.hacker = None)
  - Show game over message with reason
  - _Requirements: 4.4_

- [ ] 31. Checkpoint - Test race mechanics
  - Ensure all tests pass, ask the user if questions arise

## Phase 6: Sonrai API Integration

- [ ] 32. Add protect_service() to SonraiAPIClient
  - Create protect_service(service_type, account_id, service_name) method
  - Map service types to control keys (bedrock → "bedrock")
  - Fetch real scope from _fetch_all_account_scopes()
  - Call ProtectService mutation
  - Return QuarantineResult with success/error
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 33. Implement service type mapping
  - Create SERVICE_CONTROL_KEYS dictionary
  - Map: bedrock, s3, rds, lambda, sagemaker, dynamodb
  - Validate service_type before API call
  - _Requirements: 5.2_

- [ ] 34. Add ProtectService mutation
  - GraphQL mutation in protect_service()
  - Input: controlKey, scope, identities[], ssoActorIds[]
  - Response: success, serviceName
  - _Requirements: 5.1_

- [ ] 35. Implement scope fetching
  - Call _fetch_all_account_scopes() to get real scopes
  - Look up scope by account_id
  - NEVER construct scope manually (critical!)
  - Error if scope not found
  - _Requirements: 5.3_

- [ ] 36. Add error handling
  - Handle network errors gracefully
  - Handle invalid service type
  - Handle missing scope
  - Log all errors with context
  - Return error messages to caller
  - _Requirements: 5.4_

- [ ] 37. Create API documentation
  - Create docs/sonrai-api/queries/protect-service.md
  - Document ProtectService mutation
  - Include examples for all service types
  - Document scope requirements
  - Add to API docs index
  - _Requirements: 5.1_

- [ ] 38. Checkpoint - Test API integration
  - Ensure all tests pass, ask the user if questions arise

## Phase 7: Rendering System

- [ ] 39. Add service node rendering to Renderer
  - Create render_service_nodes() method
  - Only render in platformer levels
  - Calculate screen position with camera offset
  - Render current sprite (base/protected/unprotected)
  - _Requirements: 7.1_

- [ ] 40. Add pulsing animation for active quests
  - In render_service_nodes(), check if quest is active
  - Apply sine wave scale: scale = sin(time * 3.0) * 0.1 + 1.0
  - Scale sprite using pygame.transform.scale()
  - Center scaled sprite on position
  - _Requirements: 7.1_

- [ ] 41. Create race timer rendering
  - Add render_race_timer() method to Renderer
  - Only render when quest is ACTIVE
  - Display at top center of screen
  - Format: "XX.X seconds"
  - _Requirements: 7.3_

- [ ] 42. Add timer color coding
  - Green: time_remaining > 30 seconds
  - Orange: 15 < time_remaining <= 30
  - Red: time_remaining <= 15
  - Apply color to text and border
  - _Requirements: 7.3_

- [ ] 43. Add service hint rendering
  - Create render_service_hint() method
  - Display at bottom of screen
  - Show when player is near service icon (within 100 pixels)
  - Message: "Walk close to protect the service!"
  - Auto-dismiss when protected
  - _Requirements: 7.4_

- [ ] 44. Integrate hacker rendering
  - Add hacker rendering to main render loop
  - Only render when self.hacker is not None
  - Call hacker.render(surface, camera_offset)
  - _Requirements: 7.2_

- [ ] 45. Add render calls to main.py
  - Call renderer.render_service_nodes() in platformer levels
  - Call renderer.render_race_timer() when quest active
  - Call hacker.render() when hacker exists
  - Order: service nodes → hacker → player → UI
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 46. Checkpoint - Test rendering
  - Ensure all tests pass, ask the user if questions arise

## Phase 8: Level Integration

- [ ] 47. Create service nodes when entering levels
  - In _enter_level(), check if level has quest (1 or 6)
  - If quest exists, create ServiceNode for that quest
  - Position at quest.service_position
  - Add to self.service_nodes list
  - _Requirements: 3.3, 6.3_

- [ ] 48. Clear service nodes when returning to lobby
  - In _return_to_lobby(), clear self.service_nodes list
  - Remove hacker if active
  - Reset quest state to NOT_STARTED
  - _Requirements: 6.3_

- [ ] 49. Add quest reset on level restart
  - When re-entering a level, reset quest to NOT_STARTED
  - Reset time_remaining to time_limit
  - Clear hacker and service protection status
  - _Requirements: 6.3_

- [ ] 50. Checkpoint - Test level integration
  - Ensure all tests pass, ask the user if questions arise

## Phase 9: Polish and Testing

- [ ] 51. Add quest messages and timers
  - Update quest_message and quest_message_timer in GameState
  - Show trigger warning dialog
  - Show success message on win
  - Show game over message on loss
  - _Requirements: 1.3, 4.3, 4.4_

- [ ] 52. Tune hacker speed and timing
  - Test race difficulty
  - Adjust HACKER_SPEED if too easy/hard
  - Adjust AUTO_PROTECT_RANGE if needed
  - Ensure fair but challenging
  - _Requirements: 2.3, 4.2_

- [ ] 53. Add sound effects (optional)
  - Warning sound when quest triggers
  - Tick sound for timer
  - Success fanfare on win
  - Alarm sound on loss
  - _Future Enhancement_

- [ ] 54. Write unit tests for quest system
  - Test quest state transitions
  - Test distance calculations
  - Test auto-protection range
  - Test timer countdown
  - _Requirements: 9.2_

- [ ] 55. Write integration tests
  - Test full quest flow (trigger → race → win)
  - Test quest failure scenarios
  - Test API integration with mocks
  - Test position calculations
  - _Requirements: 9.1, 9.2_

- [ ] 56. Manual testing checklist
  - ✓ Enter Sandbox level
  - ✓ Walk past x=300 → Dialog appears
  - ✓ Press ENTER → Hacker spawns, timer starts
  - ✓ Walk to icon → Auto-protects within 80px
  - ✓ Verify win message and quest completion
  - ✓ Test hacker winning (don't reach icon in time)
  - ✓ Test timer expiry
  - ✓ Icon positioned correctly on ground (y=784)
  - ✓ Hacker lands on ground properly
  - ✓ Repeat in Production level
  - _Requirements: 9.1, 9.3_

- [ ] 57. Update README documentation
  - Add Service Protection Quest section
  - Document quest triggers and mechanics
  - Update controls (auto-protection)
  - Add quest flow diagram
  - _Documentation_

- [ ] 58. Final checkpoint - Complete testing
  - Ensure all tests pass, ask the user if questions arise
  - Verify no regressions in existing gameplay
  - Check performance (60 FPS maintained)
  - Verify API integration works with real Sonrai account

## Phase 10: Future Enhancements (Post-MVP)

- [ ] 59. Add S3 protection quest
  - Create S3 service icon sprite
  - Add S3 quest to Development level (Level 2)
  - S3-specific protection message
  - _Future Enhancement_

- [ ] 60. Add RDS protection quest
  - Create RDS service icon sprite
  - Add RDS quest to Staging level (Level 5)
  - Database-specific messaging
  - _Future Enhancement_

- [ ] 61. Add difficulty scaling
  - Shorter timer in Production (45 seconds)
  - Faster hacker in higher levels
  - Multiple hackers in Production
  - _Future Enhancement_

- [ ] 62. Add achievements
  - "Speed Protector" - Win with >50s remaining
  - "Close Call" - Win with <5s remaining
  - "Perfect Protection" - Win all quests
  - Track in save file
  - _Future Enhancement_

- [ ] 63. Add co-op helper
  - Friendly AI character helps block hacker
  - Spawns when player struggling
  - Educational about defense in depth
  - _Future Enhancement_

## Known Issues to Address

- [ ] 64. Fix save/load error
  - Issue: 'Level' object has no attribute 'is_completed'
  - Add is_completed attribute to Level class
  - Update save/load logic
  - _Requirements: 10.1_

## Property Tests (Optional but Recommended)

- [ ]* 65. Write property test for quest state machine
  - **Property: Quest state transitions are valid**
  - Test: NOT_STARTED → TRIGGERED → ACTIVE → COMPLETED
  - No invalid transitions allowed

- [ ]* 66. Write property test for race winner detection
  - **Property: Only one winner per race**
  - Test: Either player OR hacker wins, never both
  - Timer expiry always results in hacker win

- [ ]* 67. Write property test for auto-protection range
  - **Property: Protection triggers within 80px**
  - Test: distance < 80 → protect called
  - Test: distance >= 80 → protect not called

- [ ]* 68. Write property test for timer countdown
  - **Property: Timer decrements accurately**
  - Test: time_remaining = initial - elapsed
  - Test: Timer never goes negative

- [ ]* 69. Write property test for scope fetching
  - **Property: Scopes are never manually constructed**
  - Test: All scopes come from _fetch_all_account_scopes()
  - Test: Scope format matches CloudHierarchyList pattern

## Success Criteria Summary

When all tasks are complete:
- ✅ Quest triggers at x=300 in Sandbox and Production
- ✅ Warning dialog displays and dismisses with ENTER
- ✅ Hacker spawns and races toward service icon
- ✅ 60-second timer counts down with color changes
- ✅ Auto-protection works within 80 pixels
- ✅ Real Sonrai API called with correct parameters
- ✅ Win/lose conditions detected and handled
- ✅ Service icon positioned correctly on ground (y=784)
- ✅ No crashes or errors during gameplay
- ✅ All tests pass
- ✅ Documentation updated
