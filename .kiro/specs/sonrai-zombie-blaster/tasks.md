# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure: src/, tests/, assets/
  - Create requirements.txt with pygame, requests, python-dotenv, pytest, hypothesis
  - Create .env.example file with required configuration variables
  - Create .gitignore to exclude .env and __pycache__
  - Create README.md with installation and usage instructions
  - _Requirements: 6.1, 6.4, 8.3_

- [x] 2. Implement data models
  - Create src/models.py with UnusedIdentity, GameState, QuarantineResult dataclasses
  - Add Vector2 class for position and velocity
  - Add GameStatus enum (MENU, PLAYING, PAUSED, VICTORY, ERROR)
  - Add congratulations_message field to GameState
  - _Requirements: 1.1, 1.2, 1.3, 10.1_

- [ ]* 2.1 Write property test for game state consistency
  - **Property 2: Game state display accuracy**
  - **Validates: Requirements 1.3, 7.1, 7.4**

- [ ] 3. Implement Sonrai API client
  - Create src/sonrai_client.py with SonraiAPIClient class
  - Implement authentication method with token management
  - Implement fetch_unused_identities method
  - Implement quarantine_identity method with error handling
  - Add retry logic with exponential backoff
  - Add connection status checking
  - _Requirements: 1.1, 3.1, 3.2, 6.1, 6.2_

- [ ]* 3.1 Write property test for API authentication headers
  - **Property 15: API authentication headers**
  - **Validates: Requirements 6.2**

- [ ]* 3.2 Write property test for API credential security
  - **Property 16: API credential security**
  - **Validates: Requirements 6.5**

- [ ]* 3.3 Write unit tests for API client
  - Test authentication success and failure scenarios
  - Test fetch_unused_identities with mocked responses
  - Test quarantine_identity success and error cases
  - Test retry logic and backoff behavior
  - _Requirements: 1.1, 3.1, 3.2, 6.2, 6.3_

- [ ] 4. Implement game entities
  - Create src/player.py with Player class
  - Implement move_left, move_right, fire_projectile methods
  - Create src/zombie.py with Zombie class
  - Add identity_id, identity_name, is_quarantining, display_number fields
  - Implement extract_test_user_number method to parse "test-user-{number}" pattern
  - Create src/projectile.py with Projectile class
  - Implement update methods for all entities with delta time
  - _Requirements: 2.1, 2.2, 2.3, 9.1, 9.2_

- [ ]* 4.1 Write property test for player boundary constraint
  - **Property 6: Player boundary constraint**
  - **Validates: Requirements 2.4**

- [ ]* 4.2 Write property test for projectile creation
  - **Property 7: Projectile creation from player position**
  - **Validates: Requirements 2.2**

- [ ]* 4.3 Write property test for movement input processing
  - **Property 10: Movement input processing**
  - **Validates: Requirements 2.1**

- [ ]* 4.4 Write property test for test user number extraction
  - **Property 20: Test user number extraction**
  - **Validates: Requirements 9.1, 9.2**

- [ ] 5. Implement collision detection
  - Create src/collision.py with bounding box collision functions
  - Implement check_collision(projectile, zombie) method
  - Add spatial partitioning for efficient collision checks with many zombies
  - _Requirements: 2.3_

- [ ]* 5.1 Write property test for collision detection accuracy
  - **Property 8: Collision detection accuracy**
  - **Validates: Requirements 2.3**

- [ ]* 5.2 Write unit tests for collision edge cases
  - Test exact overlap, near miss, corner collision
  - Test collision with off-screen entities
  - _Requirements: 2.3_

- [ ] 6. Implement renderer
  - Create src/renderer.py with Renderer class
  - Implement render_player with simple sprite drawing
  - Implement render_zombies with batch rendering
  - Implement render_zombie_labels to display numbers above zombies
  - Implement render_projectiles
  - Implement render_ui with zombie count, quarantined count, errors
  - Implement render_background with scrolling grid pattern
  - Implement render_message_bubble with retro Game Boy style (white rounded rectangle, black border, pixelated font)
  - Create simple programmatic sprites (rectangles, circles)
  - Add font rendering for zombie labels and message bubbles
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.4, 9.3, 9.4, 10.2, 10.3_

- [ ]* 6.1 Write property test for zombie label position synchronization
  - **Property 21: Zombie label position synchronization**
  - **Validates: Requirements 9.3, 9.4**

- [ ] 7. Implement game engine core
  - Create src/game_engine.py with GameEngine class
  - Implement main game loop with delta time calculation
  - Implement update method for entity updates
  - Implement handle_input for keyboard events (including message dismissal)
  - Add game state management (MENU, PLAYING, PAUSED, VICTORY, ERROR)
  - Integrate collision detection
  - Add zombie elimination logic with game pause
  - Add congratulations message generation with format "You leveraged the Cloud Permissions Firewall to quarantine {zombie-name}"
  - Implement message dismissal and game resume logic
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x]* 7.1 Write property test for simultaneous input handling
  - **Property 11: Simultaneous input handling**
  - **Validates: Requirements 2.5**

- [ ]* 7.2 Write property test for game pause on elimination
  - **Property 22: Game pause on zombie elimination**
  - **Validates: Requirements 10.1, 10.2**

- [ ]* 7.3 Write property test for congratulations message format
  - **Property 23: Congratulations message format**
  - **Validates: Requirements 10.3**

- [ ]* 7.4 Write property test for game resume after dismissal
  - **Property 24: Game resume after message dismissal**
  - **Validates: Requirements 10.4, 10.5**

- [ ] 8. Integrate API with game engine
  - Add zombie-to-API mapping in GameEngine
  - Implement quarantine request on zombie elimination
  - Handle successful quarantine (remove zombie permanently)
  - Handle failed quarantine (restore zombie, show error)
  - Implement pending quarantine state to prevent re-targeting
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x]* 8.1 Write property test for quarantine triggers
  - **Property 3: Quarantine triggers on elimination**
  - **Validates: Requirements 3.1**

- [ ]* 8.2 Write property test for successful quarantine
  - **Property 4: Successful quarantine removes zombie**
  - **Validates: Requirements 3.2**

- [ ]* 8.3 Write property test for failed quarantine restoration
  - **Property 5: Failed quarantine restoration**
  - **Validates: Requirements 3.3**

- [ ]* 8.4 Write property test for pending quarantine prevention
  - **Property 9: Pending quarantine prevents re-targeting**
  - **Validates: Requirements 3.4**

- [ ] 9. Implement level and scrolling
  - Add background scrolling logic to GameEngine
  - Implement zombie spawn distribution across level space
  - Ensure physics consistency during scrolling
  - Add single level loop (no level transitions)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 9.1 Write property test for background scrolling
  - **Property 12: Background scrolling continuity**
  - **Validates: Requirements 5.2**

- [ ]* 9.2 Write property test for zombie spawn distribution
  - **Property 13: Zombie spawn distribution**
  - **Validates: Requirements 5.3**

- [ ]* 9.3 Write property test for physics consistency during scroll
  - **Property 14: Physics consistency during scroll**
  - **Validates: Requirements 5.4**

- [ ] 10. Implement game initialization and startup
  - Create src/main.py as entry point
  - Load configuration from .env file
  - Initialize Pygame display and audio
  - Create SonraiAPIClient instance
  - Fetch initial unused identities from API
  - Create zombie entities from API data (one-to-one mapping)
  - Handle API connection errors and missing configuration
  - Initialize GameEngine with API client and zombies
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 6.1, 6.3, 6.4_

- [ ]* 10.1 Write property test for one-to-one zombie mapping
  - **Property 1: One-to-one zombie mapping**
  - **Validates: Requirements 1.2**

- [ ]* 10.2 Write unit tests for initialization
  - Test configuration loading from .env
  - Test missing configuration error handling
  - Test API connection failure handling
  - Test empty identity list handling
  - _Requirements: 1.4, 1.5, 6.3, 6.4_

- [ ] 11. Implement UI updates and responsiveness
  - Add display update logic in renderer
  - Ensure zombie count updates within one second of elimination
  - Add error notification display system
  - Add victory screen with statistics
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x]* 11.1 Write property test for display update responsiveness
  - **Property 17: Display update responsiveness**
  - **Validates: Requirements 7.2**

- [ ] 12. Implement error handling and logging
  - Add logging configuration in main.py
  - Add error logging throughout the codebase
  - Implement graceful error handling for API failures
  - Implement graceful error handling for Pygame failures
  - Add user-friendly error messages
  - _Requirements: 1.5, 3.3, 6.3, 6.4, 8.4_

- [ ]* 12.1 Write property test for error logging
  - **Property 18: Error logging**
  - **Validates: Requirements 8.4**

- [ ] 13. Implement resource cleanup
  - Add cleanup logic in GameEngine
  - Ensure API connections are closed on exit
  - Ensure Pygame resources are released on exit
  - Handle cleanup for both normal and error exits
  - _Requirements: 8.5_

- [ ]* 13.1 Write property test for resource cleanup
  - **Property 19: Resource cleanup on exit**
  - **Validates: Requirements 8.5**

- [x] 14. Final integration and polish
  - Wire all components together in main game loop
  - Test full game flow from start to victory
  - Adjust sprite sizes and colors for visibility
  - Fine-tune movement speeds and projectile velocity
  - Add keyboard controls documentation to README
  - _Requirements: All_

- [x] 15. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
