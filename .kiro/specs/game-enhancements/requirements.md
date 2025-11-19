# Requirements Document: Game Enhancements

## Introduction

This specification defines enhancements to the existing Sonrai Zombie Blaster game, transforming it from a single-level experience into a multi-level progression system with boss battles, a damage/health system, protected identities, and improved documentation. These enhancements build upon the working base game to create a more engaging and feature-rich experience.

## Glossary

- **Level**: A game stage representing a single AWS account that must be cleared of zombies
- **Boss**: A powerful enemy entity that appears after clearing a level, representing high-risk security threats
- **Health Points (HP)**: The amount of damage an entity can sustain before being eliminated
- **Damage Multiplier**: A scoring-based modifier that increases projectile damage
- **Protected Identity**: An exempted or authorized entity (like Sonrai 3rd party) that should not be targeted
- **Purple Shield**: A visual indicator showing an entity is protected and invulnerable
- **Environment Type**: Classification of AWS accounts (sandbox, development, staging, production)
- **Exemption**: An identity that has been explicitly marked as authorized in Sonrai

## Requirements

### Requirement 1: Multi-Level Progression System

**User Story:** As a cloud security administrator, I want to progress through multiple AWS accounts from sandbox to production, so that I can systematically clean up my entire cloud environment.

#### Acceptance Criteria

1. WHEN the Game System starts, THE Game System SHALL load AWS account data from the assets/aws_accounts.csv file
2. WHEN ordering levels, THE Game System SHALL sort accounts by environment type with sandbox accounts first and production accounts last
3. WHEN a level starts, THE Game System SHALL load zombies only from the current level's AWS account
4. WHEN displaying the UI, THE Game System SHALL show the current level number, account number, and environment type
5. WHEN all zombies in a level are eliminated, THE Game System SHALL display a level completion screen
6. WHEN the player dismisses the level completion screen, THE Game System SHALL progress to the next level
7. WHEN the final production level is completed, THE Game System SHALL display a special victory screen

### Requirement 2: Boss Battle System

**User Story:** As a player, I want to face challenging boss battles after each level, so that the game has exciting climactic moments and tests my skills.

#### Acceptance Criteria

1. WHEN all zombies in a level are eliminated, THE Game System SHALL spawn a boss entity before level completion
2. WHEN rendering a boss, THE Game System SHALL display a sprite that is 3 to 4 times larger than regular zombies
3. WHEN a boss is active, THE Game System SHALL display a health bar at the top of the screen showing boss HP
4. WHEN a boss takes damage, THE Game System SHALL update the health bar to reflect remaining HP
5. WHEN a boss is defeated, THE Game System SHALL display a special congratulations message and allow level progression
6. WHEN a boss is active, THE Game System SHALL execute boss AI behavior including movement and attack patterns
7. WHEN a boss spawns mini-zombies, THE Game System SHALL create new zombie entities that must be eliminated

### Requirement 3: Damage and Health System

**User Story:** As a player, I want entities to have health points and require multiple hits to eliminate, so that combat is more strategic and engaging.

#### Acceptance Criteria

1. WHEN a regular zombie is created, THE Game System SHALL assign it 3 health points
2. WHEN a 3rd party entity is created, THE Game System SHALL assign it 10 health points
3. WHEN a projectile hits an entity, THE Game System SHALL reduce the entity's health by the projectile's damage value
4. WHEN an entity's health reaches zero, THE Game System SHALL eliminate the entity and trigger quarantine
5. WHEN an entity takes damage, THE Game System SHALL display visual feedback including a flash effect and floating damage number
6. WHEN rendering entities with health, THE Game System SHALL display a health bar above the entity showing current and maximum HP
7. WHEN an entity is hit but not eliminated, THE Game System SHALL NOT pause the game or show congratulations message

### Requirement 4: Scoring and Damage Multiplier System

**User Story:** As a player, I want to earn points and increase my damage output, so that I feel progression and can eliminate enemies faster as I improve.

#### Acceptance Criteria

1. WHEN the game starts, THE Game System SHALL initialize player damage at 1 point per projectile
2. WHEN a zombie is successfully quarantined, THE Game System SHALL increment the player's score
3. WHEN the player's score reaches a multiple of 10, THE Game System SHALL increase the damage multiplier by 1
4. WHEN displaying the UI, THE Game System SHALL show the current score and damage multiplier
5. WHEN a projectile is created, THE Game System SHALL set its damage value to the current damage multiplier

### Requirement 5: Protected Identities with Visual Indicators

**User Story:** As a cloud security administrator, I want to see which identities are protected or exempted, so that I don't accidentally target authorized entities.

#### Acceptance Criteria

1. WHEN loading 3rd party data, THE Game System SHALL identify entities with the name "Sonrai" or "Sonrai Security"
2. WHEN a Sonrai 3rd party entity is identified, THE Game System SHALL mark it as protected
3. WHEN loading level data, THE Game System SHALL fetch exempted identities from the Sonrai API for the current account
4. WHEN an exempted identity is fetched, THE Game System SHALL create a protected entity similar to 3rd party entities
5. WHEN rendering a protected entity, THE Game System SHALL display a purple shield visual indicator overlaid on the entity
6. WHEN a projectile collides with a protected entity, THE Game System SHALL ignore the collision and not apply damage
7. WHEN the player hovers near a protected entity, THE Game System SHALL display a tooltip showing "Protected: [reason]"
8. WHEN rendering the purple shield, THE Game System SHALL apply a pulsing or shimmering effect for visibility

### Requirement 6: Exemptions API Integration

**User Story:** As a developer, I want to fetch exempted identities from the Sonrai API, so that the game accurately reflects authorized entities.

#### Acceptance Criteria

1. WHEN fetching exemptions, THE Game System SHALL call the Sonrai API with the current account number
2. WHEN the API returns exemption data, THE Game System SHALL parse the resource ID, name, and exemption reason
3. WHEN creating exempted entities, THE Game System SHALL use the exemption data to populate entity properties
4. WHEN the API call fails, THE Game System SHALL log the error and continue without exemptions
5. WHEN exemptions are loaded, THE Game System SHALL display the count in the UI

### Requirement 7: Boss Entity Data from API

**User Story:** As a developer, I want to fetch high-risk entities from the Sonrai API to use as boss data, so that bosses represent real security threats.

#### Acceptance Criteria

1. WHEN spawning a boss, THE Game System SHALL query the Sonrai API for high-risk entities in the current account
2. WHEN high-risk entities are returned, THE Game System SHALL select the entity with the highest risk score
3. WHEN no high-risk entities are found, THE Game System SHALL create a generic boss with placeholder data
4. WHEN creating a boss, THE Game System SHALL use the entity's name and risk factors for display
5. WHEN a boss is defeated, THE Game System SHALL include the entity name in the congratulations message

### Requirement 8: Enhanced Visual Feedback

**User Story:** As a player, I want clear visual feedback for damage, health, and game events, so that I understand what's happening during gameplay.

#### Acceptance Criteria

1. WHEN an entity takes damage, THE Game System SHALL display a floating damage number that rises and fades
2. WHEN an entity takes damage, THE Game System SHALL flash the entity sprite for 0.1 seconds
3. WHEN rendering health bars, THE Game System SHALL use a red bar for current health and a gray background for maximum health
4. WHEN health changes, THE Game System SHALL animate the health bar smoothly over 0.2 seconds
5. WHEN the damage multiplier increases, THE Game System SHALL display a notification message for 2 seconds

### Requirement 9: Level Transition Screens

**User Story:** As a player, I want clear transition screens between levels, so that I understand my progress and can prepare for the next challenge.

#### Acceptance Criteria

1. WHEN a level is completed, THE Game System SHALL display a level completion screen with statistics
2. WHEN displaying level completion, THE Game System SHALL show zombies eliminated, time taken, and score earned
3. WHEN the player presses a key, THE Game System SHALL dismiss the level completion screen
4. WHEN transitioning to the next level, THE Game System SHALL display a "Loading Level X" message
5. WHEN the final level is completed, THE Game System SHALL display a victory screen with total game statistics

### Requirement 10: Documentation and Screenshots

**User Story:** As a new player or developer, I want comprehensive documentation with screenshots, so that I can understand the game features and how to play.

#### Acceptance Criteria

1. WHEN viewing the README, THE README SHALL include a Screenshots section with at least 4 gameplay images
2. WHEN viewing the README, THE README SHALL document the multi-level progression system
3. WHEN viewing the README, THE README SHALL explain the damage and health system
4. WHEN viewing the README, THE README SHALL describe protected identities and purple shields
5. WHEN viewing the README, THE README SHALL include a Gameplay section explaining scoring and damage multipliers
6. WHEN screenshots are captured, THE Game System SHALL save them to the assets/screenshots/ directory
7. WHEN viewing the README, THE README SHALL use relative paths to display screenshot images

### Requirement 11: CSV Account Data Loading

**User Story:** As a developer, I want to load AWS account data from a CSV file, so that account configuration is easy to manage and update.

#### Acceptance Criteria

1. WHEN the Game System starts, THE Game System SHALL read the assets/aws_accounts.csv file
2. WHEN parsing the CSV, THE Game System SHALL extract account number and environment type columns
3. WHEN the CSV file is missing, THE Game System SHALL display an error message and exit gracefully
4. WHEN the CSV contains invalid data, THE Game System SHALL log a warning and skip invalid rows
5. WHEN accounts are loaded, THE Game System SHALL log the total number of accounts and levels

### Requirement 12: Boss AI and Attack Patterns

**User Story:** As a player, I want bosses to have interesting attack patterns and behaviors, so that boss battles are challenging and engaging.

#### Acceptance Criteria

1. WHEN a boss is active, THE Game System SHALL move the boss toward the player at a slower speed than regular zombies
2. WHEN a boss reaches a spawn threshold (every 25% health lost), THE Game System SHALL spawn 3 mini-zombies
3. WHEN mini-zombies are spawned, THE Game System SHALL position them near the boss
4. WHEN a boss is defeated, THE Game System SHALL remove all remaining mini-zombies
5. WHEN a boss moves, THE Game System SHALL ensure it respects map boundaries and collision detection
