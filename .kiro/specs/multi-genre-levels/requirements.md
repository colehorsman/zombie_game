# Requirements Document

## Introduction

This feature transforms the level system from a single gameplay style into a "Choose Your Own Adventure" experience where players can select different classic arcade game genres for each AWS account/level. Each genre (Mario platformer, Asteroids shooter, Pac-Man maze, Mortal Kombat fighter) provides a unique way to eliminate zombies while maintaining the core educational mission. This increases replayability and appeals to different player preferences.

## Glossary

- **Genre**: A classic arcade game style (Platformer, Space Shooter, Maze Chase, Fighting)
- **Level Template**: The base gameplay mechanics and visual style for a specific genre
- **AWS Account World**: An AWS account represented as a playable level in any chosen genre
- **Zombie Adaptation**: How zombies behave and appear within each genre's mechanics
- **Genre Selector**: The UI that allows players to choose their preferred gameplay style for a level
- **Wally**: The AI agent mascot character used in Pac-Man style levels
- **Boss Battle**: A Mortal Kombat-style one-on-one fight against a level's main threat

## Requirements

### Requirement 1: Genre Selection System

**User Story:** As a player with multiple AWS accounts, I want to choose how I play each level, so that I can enjoy my preferred gameplay style.

#### Acceptance Criteria

1. WHEN the player selects an AWS account door in the lobby THEN the System SHALL display a genre selection menu
2. WHEN displaying the genre selector THEN the System SHALL show available genres with preview icons
3. WHEN the player selects a genre THEN the System SHALL load the level using that genre's template
4. WHEN a genre is selected THEN the System SHALL remember the choice for that account in the save file
5. WHERE the player wants to change genres THEN the System SHALL allow re-selection from the lobby

### Requirement 2: Platformer Genre (Mario-Style) - Default

**User Story:** As a player, I want to play side-scrolling platformer levels, so that I can experience classic Mario-style gameplay while eliminating zombies.

#### Acceptance Criteria

1. WHEN the Platformer genre is selected THEN the System SHALL load a side-scrolling level layout
2. WHEN playing Platformer THEN the System SHALL enable jumping, running, and shooting mechanics
3. WHEN zombies spawn in Platformer THEN the System SHALL place them on platforms throughout the level
4. WHEN the player reaches the end of the level THEN the System SHALL trigger level completion
5. WHEN playing Platformer THEN the System SHALL maintain the existing visual style and controls

### Requirement 3: Space Shooter Genre (Asteroids-Style)

**User Story:** As a player, I want to play space shooter levels, so that I can experience Asteroids/Galaga-style gameplay while eliminating zombies.

#### Acceptance Criteria

1. WHEN the Space Shooter genre is selected THEN the System SHALL load a vertical scrolling space environment
2. WHEN playing Space Shooter THEN the System SHALL render the player as an AWS-themed spacecraft at the bottom
3. WHEN zombies spawn in Space Shooter THEN the System SHALL spawn them at the top moving downward
4. WHEN the player shoots in Space Shooter THEN the System SHALL fire projectiles upward toward zombies
5. WHEN all zombies are eliminated THEN the System SHALL trigger level completion
6. WHEN a zombie reaches the bottom THEN the System SHALL damage the player

### Requirement 4: Maze Chase Genre (Pac-Man Style)

**User Story:** As a player, I want to play maze chase levels as Wally the AI agent, so that I can experience Pac-Man-style gameplay while chomping zombies.

#### Acceptance Criteria

1. WHEN the Maze Chase genre is selected THEN the System SHALL load a maze-based level layout
2. WHEN playing Maze Chase THEN the System SHALL render the player as Wally the AI agent
3. WHEN Wally moves into a zombie THEN the System SHALL eliminate the zombie with a chomping animation
4. WHEN zombies move in Maze Chase THEN the System SHALL use maze pathfinding AI
5. WHEN all zombies are eliminated THEN the System SHALL trigger level completion
6. WHEN a zombie touches Wally from behind THEN the System SHALL damage the player

### Requirement 5: Fighting Genre (Mortal Kombat Style)

**User Story:** As a player, I want to face level bosses in one-on-one combat, so that I can experience fighting game mechanics against high-risk identities.

#### Acceptance Criteria

1. WHEN the Fighting genre is selected THEN the System SHALL load a fighting arena environment
2. WHEN playing Fighting THEN the System SHALL present zombies as sequential opponents
3. WHEN in combat THEN the System SHALL enable punch, kick, and special move controls
4. WHEN the player defeats an opponent THEN the System SHALL quarantine that identity
5. WHEN all opponents are defeated THEN the System SHALL trigger level completion
6. WHEN the player's health reaches zero THEN the System SHALL trigger game over

### Requirement 6: Genre-Specific Visual Themes

**User Story:** As a player, I want each genre to have distinct visual styling, so that the experience feels authentic to each classic game type.

#### Acceptance Criteria

1. WHEN loading Space Shooter THEN the System SHALL render a starfield background with AWS/cloud-themed elements
2. WHEN loading Maze Chase THEN the System SHALL render a maze with cloud infrastructure visual motifs
3. WHEN loading Fighting THEN the System SHALL render a dramatic arena with versus-style presentation
4. WHEN rendering any genre THEN the System SHALL maintain the 8-bit retro aesthetic
5. WHEN transitioning between genres THEN the System SHALL use appropriate loading screens

### Requirement 7: Zombie Behavior Adaptation

**User Story:** As a player, I want zombies to behave appropriately for each genre, so that gameplay feels authentic to each style.

#### Acceptance Criteria

1. WHEN in Platformer THEN zombies SHALL patrol platforms and chase the player horizontally
2. WHEN in Space Shooter THEN zombies SHALL descend in formation patterns like Galaga enemies
3. WHEN in Maze Chase THEN zombies SHALL navigate the maze using ghost-like AI behaviors
4. WHEN in Fighting THEN zombies SHALL use fighting game attack patterns and combos
5. WHEN adapting zombie behavior THEN the System SHALL preserve identity metadata for educational display

### Requirement 8: AWS Account Theming

**User Story:** As a player, I want each AWS account to have thematic elements that connect to its purpose, so that levels feel unique and meaningful.

#### Acceptance Criteria

1. WHEN loading a Production account THEN the System SHALL use more intense visual themes
2. WHEN loading a Sandbox account THEN the System SHALL use friendlier, tutorial-oriented themes
3. WHEN loading any account THEN the System SHALL display the account name and purpose
4. WHEN theming a level THEN the System SHALL incorporate the account's zombie count into difficulty
5. WHEN the account has special characteristics THEN the System SHALL reflect them in level design

### Requirement 9: Cross-Genre Progression

**User Story:** As a player, I want my progress to be tracked regardless of which genre I choose, so that I can switch styles without losing advancement.

#### Acceptance Criteria

1. WHEN a zombie is eliminated in any genre THEN the System SHALL record it in the unified progress tracker
2. WHEN viewing account status THEN the System SHALL show total zombies eliminated across all genres
3. WHEN an account is cleared THEN the System SHALL mark it complete regardless of genre used
4. WHEN loading the lobby THEN the System SHALL display completion status for each account
5. WHEN saving progress THEN the System SHALL persist genre preferences and completion data

### Requirement 10: Genre Unlock System

**User Story:** As a new player, I want to unlock new genres as I progress, so that I have goals to work toward and don't get overwhelmed initially.

#### Acceptance Criteria

1. WHEN a new player starts THEN the System SHALL have Platformer genre unlocked by default
2. WHEN the player completes their first level THEN the System SHALL unlock Space Shooter genre
3. WHEN the player eliminates 50 zombies THEN the System SHALL unlock Maze Chase genre
4. WHEN the player completes 3 levels THEN the System SHALL unlock Fighting genre
5. WHEN a genre is unlocked THEN the System SHALL display a celebratory notification

## Design Considerations

### AWS Service Theming Ideas

**Space Shooter (Asteroids):**
- Player ship could be styled after AWS Lambda (serverless = rocket fast)
- Or AWS Step Functions (state machine = mission control)
- Background could show constellation patterns of AWS service icons

**Maze Chase (Pac-Man):**
- Maze walls could be styled as VPC network boundaries
- Power pellets could be IAM policies that give temporary invincibility
- Wally chomping = AI-powered identity cleanup

**Fighting (Mortal Kombat):**
- Arena could be styled as CloudWatch dashboard
- Health bars show "Risk Score" instead of HP
- Special moves named after security actions (Quarantine Uppercut, Policy Punch)

### Technical Considerations

- Each genre needs its own game loop variant or state machine
- Zombie spawning logic must be abstracted to support different patterns
- Collision detection varies significantly between genres
- Save system must track per-account genre preferences
- Performance must remain at 60 FPS regardless of genre
