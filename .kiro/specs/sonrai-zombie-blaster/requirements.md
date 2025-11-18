# Requirements Document

## Introduction

The Sonrai Zombie Blaster is a retro-style video game that visualizes and gamifies the process of identifying and remediating unused AWS identities (zombies) through the Sonrai API. The game features simple 2D graphics reminiscent of Chrome's offline dinosaur game, with a Mega Man-inspired character eliminating zombies that represent real unused AWS identities detected by Sonrai's permissions firewall.

## Glossary

- **Game System**: The complete video game application including graphics, game loop, and API integration
- **Sonrai API**: The external REST API provided by Sonrai Security for querying and managing cloud security data
- **Zombie**: An unused AWS identity (IAM user, role, or service account) that has been inactive or has excessive permissions
- **Player Character**: The controllable Mega Man-style character that eliminates zombies
- **Quarantine Action**: The process of remediating or isolating an unused identity through the Sonrai API
- **Game Session**: A single playthrough from start (1000 zombies) to completion (0 zombies)
- **Zombie Entity**: The in-game representation of a real AWS unused identity with a 1:1 mapping

## Requirements

### Requirement 1

**User Story:** As a cloud security administrator, I want to see my real AWS unused identities visualized as zombies in a game, so that I can understand the scope of my security posture in an engaging way.

#### Acceptance Criteria

1. WHEN the Game System starts, THE Game System SHALL fetch unused identity data from the Sonrai API
2. WHEN unused identities are retrieved, THE Game System SHALL create exactly one Zombie Entity for each unused identity returned by the API
3. WHEN displaying the zombie count, THE Game System SHALL show the current number of Zombie Entities remaining
4. WHEN the Sonrai API returns zero unused identities, THE Game System SHALL display a completion message
5. WHEN the Game System cannot connect to the Sonrai API, THE Game System SHALL display an error message and prevent gameplay

### Requirement 2

**User Story:** As a player, I want to control a Mega Man-style character with a ray gun, so that I can eliminate zombies through simple and intuitive controls.

#### Acceptance Criteria

1. WHEN the player presses the movement keys, THE Game System SHALL move the Player Character left or right within the game boundaries
2. WHEN the player presses the fire key, THE Game System SHALL create a projectile that travels from the Player Character position
3. WHEN a projectile collides with a Zombie Entity, THE Game System SHALL remove that Zombie Entity from the game
4. WHEN the Player Character moves beyond the screen boundary, THE Game System SHALL constrain the Player Character position to remain visible
5. WHEN multiple keys are pressed simultaneously, THE Game System SHALL process all valid inputs without conflicts

### Requirement 3

**User Story:** As a cloud security administrator, I want each eliminated zombie to trigger a quarantine action via the Sonrai API, so that the game actions result in real security improvements.

#### Acceptance Criteria

1. WHEN a Zombie Entity is eliminated, THE Game System SHALL send a quarantine request to the Sonrai API for the corresponding unused identity
2. WHEN the Sonrai API confirms successful quarantine, THE Game System SHALL permanently remove the Zombie Entity from the game
3. WHEN the Sonrai API returns an error for a quarantine request, THE Game System SHALL display an error notification and restore the Zombie Entity
4. WHEN a quarantine request is pending, THE Game System SHALL prevent the same Zombie Entity from being targeted again
5. WHEN all Zombie Entities are eliminated and quarantined, THE Game System SHALL display a victory screen with statistics

### Requirement 4

**User Story:** As a player, I want simple retro-style graphics similar to Chrome's dinosaur game, so that the game is visually clean and runs smoothly without complex rendering.

#### Acceptance Criteria

1. WHEN rendering the Player Character, THE Game System SHALL display a simple 2D sprite with recognizable Mega Man-style features
2. WHEN rendering Zombie Entities, THE Game System SHALL display simple 2D sprites that are visually distinct from the Player Character
3. WHEN rendering the game background, THE Game System SHALL use a minimal scrolling or static background
4. WHEN rendering projectiles, THE Game System SHALL display simple geometric shapes or small sprites
5. WHEN the game runs, THE Game System SHALL maintain a frame rate of at least 30 frames per second on standard hardware

### Requirement 5

**User Story:** As a player, I want the game to loop continuously on a single level, so that I can focus on eliminating all zombies without level transitions.

#### Acceptance Criteria

1. WHEN the game starts, THE Game System SHALL load a single level layout
2. WHEN the Player Character reaches the end of the visible area, THE Game System SHALL scroll the background to create continuous movement
3. WHEN Zombie Entities are spawned, THE Game System SHALL distribute them across the level space
4. WHEN the level scrolls, THE Game System SHALL maintain consistent physics and collision detection
5. WHEN all Zombie Entities are eliminated, THE Game System SHALL not transition to a new level

### Requirement 6

**User Story:** As a developer, I want the game to authenticate with the Sonrai API securely, so that API credentials are protected and the integration is reliable.

#### Acceptance Criteria

1. WHEN the Game System initializes, THE Game System SHALL load Sonrai API credentials from environment variables or a configuration file
2. WHEN making API requests, THE Game System SHALL include valid authentication tokens in request headers
3. WHEN authentication fails, THE Game System SHALL display a clear error message and prevent gameplay
4. WHEN API credentials are missing, THE Game System SHALL display a configuration error message with instructions
5. WHEN storing API credentials, THE Game System SHALL never include them in source code or version control

### Requirement 7

**User Story:** As a player, I want to see real-time feedback on my progress, so that I understand how many zombies remain and how many I've eliminated.

#### Acceptance Criteria

1. WHEN the game is running, THE Game System SHALL display the current count of remaining Zombie Entities
2. WHEN a Zombie Entity is eliminated, THE Game System SHALL update the displayed count within one second
3. WHEN the game starts, THE Game System SHALL display the initial count of 1000 or the actual number from the API
4. WHEN displaying statistics, THE Game System SHALL show the number of successfully quarantined identities
5. WHEN an error occurs, THE Game System SHALL display error information without obscuring critical game elements

### Requirement 9

**User Story:** As a cloud security administrator, I want to see the test user number displayed above each zombie, so that I can identify which specific unused identity each zombie represents.

#### Acceptance Criteria

1. WHEN a Zombie Entity is rendered, THE Game System SHALL extract the numeric identifier from the identity name
2. WHEN the identity name follows the pattern "test-user-{number}", THE Game System SHALL display the number above the zombie sprite
3. WHEN rendering the numeric identifier, THE Game System SHALL ensure the text is readable and positioned directly above the zombie
4. WHEN a zombie moves or scrolls, THE Game System SHALL keep the numeric identifier synchronized with the zombie position
5. WHEN the identity name does not match the expected pattern, THE Game System SHALL display a default identifier or the full name

### Requirement 10

**User Story:** As a player, I want to see a retro Game Boy-style congratulations message when I eliminate a zombie, so that I feel rewarded and understand the security impact of my action.

#### Acceptance Criteria

1. WHEN a Zombie Entity is successfully eliminated, THE Game System SHALL pause the game
2. WHEN the game is paused for elimination, THE Game System SHALL display a message bubble in retro Game Boy style
3. WHEN displaying the congratulations message, THE Game System SHALL include the text "You leveraged the Cloud Permissions Firewall to quarantine {zombie-name}"
4. WHEN the message bubble is displayed, THE Game System SHALL wait for player input to dismiss the message
5. WHEN the player dismisses the message, THE Game System SHALL resume normal gameplay

### Requirement 8

**User Story:** As a developer, I want the game built with appropriate technology for 2D game development, so that it is maintainable and performs well.

#### Acceptance Criteria

1. WHEN selecting a programming language, THE Game System SHALL use Python with Pygame or a similar 2D game framework
2. WHEN the game runs, THE Game System SHALL handle game loop timing, rendering, and input processing efficiently
3. WHEN packaging the game, THE Game System SHALL include all dependencies and provide clear installation instructions
4. WHEN the game encounters errors, THE Game System SHALL log error details for debugging purposes
5. WHEN the game exits, THE Game System SHALL clean up resources and close API connections properly
