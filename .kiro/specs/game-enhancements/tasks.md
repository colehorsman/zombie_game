# Implementation Plan: Game Enhancements

## Phase 1: Damage and Health System (Foundation)

- [ ] 1. Implement health system for entities
  - Add `health` and `max_health` attributes to Zombie class
  - Add `health` and `max_health` attributes to ThirdParty class (if not already present)
  - Initialize regular zombies with health=3, max_health=3
  - Initialize 3rd parties with health=10, max_health=10
  - Add `take_damage(damage: int) -> bool` method that returns True if eliminated
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 1.1 Write property test for health depletion accuracy
  - **Property 3: Health depletion accuracy**
  - **Validates: Requirements 3.3**

- [ ]* 1.2 Write property test for entity health initialization
  - **Property 13: Entity health initialization**
  - **Validates: Requirements 3.1, 3.2**

- [ ]* 1.3 Write property test for elimination only at zero health
  - **Property 14: Elimination only at zero health**
  - **Validates: Requirements 3.4**

- [ ] 2. Add damage attribute to projectiles
  - Add `damage` attribute to Projectile class
  - Initialize projectiles with damage=1 by default
  - Allow damage to be set when creating projectile
  - _Requirements: 3.3, 4.5_

- [ ] 3. Modify collision detection for damage system
  - Update collision handling to call `take_damage()` instead of instant removal
  - Only eliminate entity when `take_damage()` returns True (health reaches 0)
  - Keep projectile removal on hit
  - Only pause game and show message when entity is eliminated (health = 0)
  - _Requirements: 3.3, 3.4, 3.7_

- [ ] 4. Create damage number system
  - Create src/damage_system.py with DamageSystem class
  - Implement `create_damage_number(position, damage)` method
  - Add DamageNumber dataclass with position, damage, lifetime, velocity
  - Implement `update_damage_numbers(delta_time)` to animate numbers
  - Numbers should rise 30px over 1.0 second and fade out
  - Limit to 20 active damage numbers maximum
  - _Requirements: 8.1_

- [ ]* 4.1 Write property test for damage number lifecycle
  - **Property 10: Damage number animation lifecycle**
  - **Validates: Requirements 8.1**

- [ ] 5. Add health bar rendering
  - Add `render_health_bar(entity, surface, camera_offset)` to Renderer
  - Health bar: 30px wide x 4px tall, centered above entity
  - Colors: gray background, red health, black border
  - Only show health bar if entity health < max_health
  - Animate health bar depletion smoothly over 0.2 seconds
  - _Requirements: 3.6_

- [ ] 6. Add visual damage feedback
  - Add flash effect when entity takes damage (0.1 second white overlay)
  - Add `is_flashing` and `flash_timer` to entity classes
  - Update entity rendering to apply flash effect
  - Integrate damage number creation on hit
  - _Requirements: 3.5, 8.1, 8.2_

- [ ] 7. Integrate damage system into game engine
  - Add DamageSystem instance to GameEngine
  - Update collision handling to use damage system
  - Call damage number update and render in game loop
  - Test with existing game to ensure zombies require 3 hits
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ] 8. Checkpoint - Test damage system
  - Ensure all tests pass, ask the user if questions arise

## Phase 2: Protected Identities

- [ ] 9. Add exemptions API method
  - Add `fetch_exemptions(account: str)` to SonraiAPIClient
  - Implement GraphQL query for Exemptions endpoint
  - Parse response to extract resourceId, resourceName, exemptionReason, expirationDate
  - Handle API errors gracefully (log and return empty list)
  - Add retry logic with exponential backoff
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ]* 9.1 Write property test for exemption data completeness
  - **Property 7: Exemption data completeness**
  - **Validates: Requirements 6.2**

- [ ]* 9.2 Write unit tests for exemptions API
  - Test successful fetch with mocked response
  - Test API error handling
  - Test empty response handling
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 10. Create protected entity class
  - Create src/protected_entity.py with ProtectedEntity class
  - Add identity_id, name, position, protection_reason attributes
  - Add is_protected=True flag
  - Create sprite similar to 3rd party entities
  - Add `get_bounds()` method for collision detection
  - _Requirements: 5.4_

- [ ] 11. Implement purple shield rendering
  - Create shield sprite: purple hexagon/circle, 1.2x entity size
  - Color: RGB(160, 32, 240) with 50% opacity
  - Add pulsing animation: scale between 1.0x and 1.1x over 1.0 second
  - Add outer glow effect (2px radius)
  - Add `render_shield(surface, camera_offset)` method
  - _Requirements: 5.5, 5.8_

- [ ]* 11.1 Write property test for purple shield visibility
  - **Property 6: Purple shield visibility**
  - **Validates: Requirements 5.5**

- [ ] 12. Identify and mark Sonrai 3rd party as protected
  - When loading 3rd party data, check for "Sonrai" or "Sonrai Security" in name
  - Add `is_protected` flag to 3rd party entities
  - Set protection_reason = "Sonrai Security Platform"
  - _Requirements: 5.1, 5.2_

- [ ] 13. Load exemptions and create protected entities
  - In level initialization, call `fetch_exemptions(account)`
  - Create ProtectedEntity for each exemption
  - Position protected entities on map similar to 3rd parties
  - Add to game engine's protected entities list
  - _Requirements: 5.3, 5.4, 6.3_

- [ ] 14. Modify collision detection for protected entities
  - Update collision detection to check `is_protected` flag
  - Skip damage application for protected entities
  - Optionally: bounce projectile off or pass through
  - _Requirements: 5.6_

- [ ]* 14.1 Write property test for protected entity invulnerability
  - **Property 5: Protected entity invulnerability**
  - **Validates: Requirements 5.6**

- [ ] 15. Add tooltip rendering for protected entities
  - Add tooltip display when player is near protected entity (within 50px)
  - Show "Protected: [reason]" text in small bubble
  - Position tooltip above entity
  - _Requirements: 5.7_

- [ ] 16. Integrate protected entities into renderer
  - Add `render_protected_entities()` method to Renderer
  - Render protected entity sprites
  - Render purple shields with pulsing animation
  - Render tooltips when player is nearby
  - Update UI to show protected entities count
  - _Requirements: 5.5, 5.7, 5.8, 6.5_

- [ ] 17. Checkpoint - Test protected identities
  - Ensure all tests pass, ask the user if questions arise

## Phase 3: Multi-Level System

- [ ] 18. Create level manager class
  - Create src/level_manager.py with LevelManager class
  - Add `load_accounts(csv_path)` method to parse CSV
  - Add `get_current_level()` to return current AccountLevel
  - Add `advance_level()` to progress to next level
  - Add `is_final_level()` to check if on last level
  - Add `get_level_stats()` to return level statistics
  - _Requirements: 1.1, 1.2, 1.6_

- [ ]* 18.1 Write property test for level progression order
  - **Property 1: Level progression order**
  - **Validates: Requirements 1.2, 1.6**

- [ ] 19. Implement CSV account loading
  - Parse assets/aws_accounts.csv file
  - Extract account_number and environment_type columns
  - Sort accounts: sandbox first, then dev, staging, prod last
  - Handle missing file error gracefully
  - Handle invalid rows (log warning, skip row)
  - Log total accounts loaded
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 19.1 Write property test for CSV account loading completeness
  - **Property 12: CSV account loading completeness**
  - **Validates: Requirements 11.2**

- [ ]* 19.2 Write unit tests for CSV loading
  - Test valid CSV parsing
  - Test missing file error
  - Test invalid data handling
  - Test empty file handling
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 20. Add AccountLevel data model
  - Create AccountLevel dataclass in models.py
  - Fields: account_number, environment_type, level_number, zombie_count
  - _Requirements: 1.1, 1.2_

- [ ] 21. Modify game engine for level-based loading
  - Add LevelManager instance to GameEngine
  - Modify zombie loading to fetch only from current level's account
  - Add level transition logic
  - Track level-specific statistics (zombies eliminated, time, score)
  - _Requirements: 1.3, 1.4_

- [ ] 22. Add level information to UI
  - Display current level number in UI
  - Display account number in UI
  - Display environment type (Sandbox/Dev/Staging/Prod) in UI
  - Update UI layout to accommodate new information
  - _Requirements: 1.4_

- [ ] 23. Create level completion screen
  - Add LEVEL_COMPLETE state to GameStatus enum
  - Create level completion screen rendering
  - Display: level number, zombies eliminated, time taken, score earned
  - Show "Press ENTER to continue" message
  - _Requirements: 1.5, 9.1, 9.2, 9.3_

- [ ]* 23.1 Write property test for level completion statistics
  - **Property 11: Level completion statistics accuracy**
  - **Validates: Requirements 9.2**

- [ ] 24. Implement level transition logic
  - When all zombies eliminated, transition to LEVEL_COMPLETE state
  - On ENTER key, call `advance_level()`
  - Load next level's zombies
  - Display "Loading Level X" message during transition
  - Reset level-specific statistics
  - _Requirements: 1.5, 1.6, 9.3, 9.4_

- [ ] 25. Create final victory screen
  - Check `is_final_level()` before advancing
  - If final level, show special victory screen
  - Display total game statistics: all zombies quarantined, total time, final score
  - Show congratulations message
  - _Requirements: 1.7, 9.5_

- [ ] 26. Checkpoint - Test multi-level system
  - Ensure all tests pass, ask the user if questions arise

## Phase 4: Boss Battles

- [ ] 27. Create boss entity class
  - Create src/boss.py with Boss class
  - Add identity_id, name, position, health, max_health attributes
  - Add risk_score, risk_factors attributes
  - Add minion_spawn_thresholds list [0.75, 0.50, 0.25]
  - Add is_defeated flag
  - Initialize boss with health = 50 * 3 = 150 (50x regular zombie)
  - _Requirements: 2.1, 2.2_

- [ ] 28. Add high-risk entities API method
  - Add `fetch_high_risk_entities(account: str)` to SonraiAPIClient
  - Implement GraphQL query for HighRiskIdentities endpoint
  - Filter for risk_score >= 7.0
  - Parse response to extract resourceId, resourceName, riskScore, riskFactors
  - Handle API errors gracefully (return empty list)
  - _Requirements: 7.1, 7.2, 7.3_

- [ ]* 28.1 Write unit tests for high-risk entities API
  - Test successful fetch with mocked response
  - Test API error handling
  - Test empty response handling
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 29. Implement boss sprite rendering
  - Create boss sprite: 120px x 120px (3x zombie size)
  - Use darker, more saturated colors than regular zombies
  - Add crown or special marker to indicate boss
  - Make visually distinct and menacing
  - _Requirements: 2.2_

- [ ] 30. Add boss health bar rendering
  - Create boss health bar: 400px wide x 20px tall
  - Position at top center of screen, 20px from top
  - Colors: dark gray background, red gradient health, gold border
  - Display boss name above health bar
  - Update health bar when boss takes damage
  - _Requirements: 2.3, 2.4_

- [ ]* 30.1 Write property test for boss health bar accuracy
  - **Property 8: Boss health bar accuracy**
  - **Validates: Requirements 2.3, 2.4**

- [ ] 31. Implement boss AI movement
  - Add `update(delta_time, player_pos)` method to Boss
  - Move boss toward player at 0.5x zombie speed
  - Respect map boundaries and collision detection
  - Update boss position each frame
  - _Requirements: 12.1, 12.5_

- [ ] 32. Implement mini-zombie spawning
  - Track boss health percentage
  - Spawn 3 mini-zombies when health crosses 75%, 50%, 25%
  - Position mini-zombies near boss (random offset within 100px)
  - Mark thresholds as triggered to prevent duplicate spawns
  - _Requirements: 12.2, 12.3_

- [ ]* 32.1 Write property test for mini-zombie spawn thresholds
  - **Property 9: Mini-zombie spawn thresholds**
  - **Validates: Requirements 12.2**

- [ ] 33. Integrate boss spawn into level completion
  - After all zombies eliminated, check if boss already defeated
  - If not, spawn boss using high-risk entity data
  - If no high-risk data, create generic boss with placeholder name
  - Add BOSS_BATTLE state to GameStatus enum
  - Transition to BOSS_BATTLE state instead of LEVEL_COMPLETE
  - _Requirements: 2.1, 7.1, 7.2, 7.3, 7.4_

- [ ]* 33.1 Write property test for boss spawn after level clear
  - **Property 2: Boss spawn after level clear**
  - **Validates: Requirements 2.1**

- [ ] 34. Implement boss defeat logic
  - When boss health reaches 0, mark as defeated
  - Remove all remaining mini-zombies
  - Show special congratulations message with boss name
  - Transition to LEVEL_COMPLETE state
  - _Requirements: 2.5, 12.4_

- [ ] 35. Add boss battle to game engine
  - Add boss instance to GameEngine
  - Update boss in game loop
  - Handle boss collision detection
  - Render boss sprite and health bar
  - Handle boss defeat and level progression
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [ ] 36. Checkpoint - Test boss battles
  - Ensure all tests pass, ask the user if questions arise

## Phase 5: Scoring and Damage Multipliers

- [ ] 37. Add scoring system to game state
  - Add `score` attribute to GameState (initialize to 0)
  - Add `damage_multiplier` attribute to GameState (initialize to 1)
  - _Requirements: 4.1, 4.2_

- [ ] 38. Implement score increment on quarantine
  - When zombie is successfully quarantined, increment score by 1
  - Update score in UI
  - _Requirements: 4.2_

- [ ]* 38.1 Write property test for score increment
  - **Property 15: Score increment on quarantine**
  - **Validates: Requirements 4.2**

- [ ] 39. Implement damage multiplier calculation
  - Calculate damage_multiplier = 1 + floor(score / 10)
  - Update damage_multiplier when score changes
  - _Requirements: 4.3_

- [ ]* 39.1 Write property test for damage multiplier progression
  - **Property 4: Damage multiplier progression**
  - **Validates: Requirements 4.3**

- [ ] 40. Update projectile damage based on multiplier
  - When creating projectile, set damage = current damage_multiplier
  - Ensure projectiles use updated damage value
  - _Requirements: 4.5_

- [ ] 41. Add score and multiplier to UI
  - Display current score in UI
  - Display current damage multiplier in UI (e.g., "Damage: x3")
  - Position in top-left or top-right corner
  - _Requirements: 4.4_

- [ ] 42. Add damage multiplier increase notification
  - When damage_multiplier increases, show notification message
  - Display "Damage Increased! x[N]" for 2 seconds
  - Position notification in center of screen
  - _Requirements: 8.5_

- [ ] 43. Checkpoint - Test scoring system
  - Ensure all tests pass, ask the user if questions arise

## Phase 6: Documentation and Polish

- [ ] 44. Capture gameplay screenshots
  - Take screenshot of main gameplay with zombies and player
  - Take screenshot of boss battle with health bar
  - Take screenshot of level completion screen
  - Take screenshot of protected entities with purple shields
  - Take screenshot showing damage numbers and health bars
  - Save screenshots to assets/screenshots/ directory
  - Use pygame.image.save() to capture screenshots
  - _Requirements: 10.1, 10.6_

- [ ] 45. Update README with new features
  - Add "Screenshots" section with gameplay images
  - Update "Features" section to include:
    - Multi-level progression system
    - Boss battles after each level
    - Damage and health system
    - Scoring and damage multipliers
    - Protected identities with purple shields
  - Use relative paths for images: `![Screenshot](assets/screenshots/gameplay.png)`
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.7_

- [ ] 46. Add gameplay guide to README
  - Add "Gameplay" section explaining:
    - How to progress through levels
    - Damage system (zombies need 3 hits, 3rd parties need 10 hits)
    - Scoring and damage multipliers (every 10 zombies = +1 damage)
    - Protected entities (purple shield = invulnerable)
    - Boss battles (appear after clearing level)
  - _Requirements: 10.5_

- [ ] 47. Update controls documentation
  - Document any new controls (if added)
  - Update existing controls section
  - _Requirements: 10.3_

- [ ] 48. Update "How It Works" section
  - Explain multi-level progression
  - Explain boss battle mechanics
  - Explain damage and health system
  - Explain protected identities
  - _Requirements: 10.5_

- [ ] 49. Final integration and testing
  - Test complete game flow from first level to final victory
  - Verify all features work together
  - Check performance with all enhancements enabled
  - Ensure 60 FPS maintained
  - Test with real Sonrai API data
  - _Requirements: All_

- [ ] 50. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise
