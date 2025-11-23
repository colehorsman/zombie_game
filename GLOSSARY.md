# Game Development Glossary

This glossary defines game development and Zombie Blaster-specific terms to help you clearly communicate about the codebase.

## General Game Development Terms

### Game Loop & Timing

**Game Loop**
The main execution cycle that runs continuously while the game is active. In this project, it's located in `src/main.py:373-505`. Each iteration: handles input → updates state → renders → displays.

**Delta Time (dt)**
Time elapsed between frames, measured in seconds. Used to make movement speed consistent regardless of frame rate. Example: `player.position.x += velocity * delta_time`. See `src/main.py:375`.

**FPS (Frames Per Second)**
How many times per second the game updates and renders. This game targets 60 FPS (configurable via `TARGET_FPS` in `.env`). See `src/main.py:375`.

**Frame**
A single iteration of the game loop. At 60 FPS, each frame lasts ~16.67ms.

**Tick**
Synonym for frame. `clock.tick(60)` limits the game to 60 frames per second and returns milliseconds since last tick.

### Graphics & Rendering

**Sprite**
A 2D image or animated character in the game. Examples: player character, zombies, projectiles. Sprites have position, size, and visual representation.

**Renderer**
The system responsible for drawing everything to the screen. Located in `src/renderer.py`. Handles sprites, UI, backgrounds, health bars, etc.

**Surface**
A Pygame object representing a rectangular area for drawing. `game_surface` (internal rendering at base resolution) and `display` (actual window/screen).

**Blit**
The operation of drawing one surface onto another. Example: `display.blit(game_surface, (0, 0))` draws the game onto the window.

**Camera**
The viewport that follows the player. Only objects within camera bounds are visible. See `GameMap.camera_x` and `GameMap.camera_y` in `src/game_map.py:69-70`.

**Scroll Offset**
The camera's position in the game world. Used to translate world coordinates to screen coordinates. See `src/renderer.py`.

**Letterboxing / Pillarboxing**
Black bars added to maintain aspect ratio when the window size doesn't match the game's aspect ratio. Letterboxing = horizontal bars (top/bottom), Pillarboxing = vertical bars (left/right). See `src/main.py:62-91`.

**Screen Coordinates vs World Coordinates**
- **Screen Coordinates**: Position on your display (0,0 is top-left corner of window)
- **World Coordinates**: Position in the game world (larger than screen, camera scrolls through it)

### Physics & Movement

**Vector2**
A 2D coordinate (x, y). Used for positions, velocities, and directions. Defined in `src/models.py`.

**Velocity**
Speed and direction of movement, measured in pixels per second. Example: `Vector2(200, 0)` = moving right at 200 px/s.

**Gravity**
Constant downward acceleration in platformer mode. Affects player jumping and zombie falling. See platformer physics in `src/game_engine.py`.

**Collision Detection**
Checking if two game objects (sprites) overlap. This game uses spatial grid optimization for efficient collision checks. See `src/collision.py`.

**Hitbox / Bounding Box**
The rectangular area used for collision detection. May be smaller than the visible sprite.

**Spatial Grid**
Performance optimization that divides the game world into grid cells. Only checks collisions within nearby cells instead of checking every object. See `src/collision.py`.

### Map & Level Design

**Tile**
A small square unit (16x16 pixels) used to build the game world. Maps are measured in tiles. See `src/game_map.py:40`.

**Tile-Based Map**
A map constructed from a grid of tiles. This game uses tile-based design for both lobby and platformer modes.

**Tileset**
Collection of tile graphics (floor, wall, platform, etc.). Currently this game uses programmatically generated tiles.

**Platform**
A solid surface the player can stand on in platformer mode. Platforms are randomly generated. See `src/game_map.py`.

**Level**
A playable stage representing one AWS account. Each level has its own zombies, difficulty, and environment type. See `src/level_manager.py`.

**Room**
A rectangular area in the lobby map. Each room represents one AWS account and is sized based on zombie count. See `src/game_map.py:75-108`.

**Door**
An entrance to a level/room. Walking through a door transitions from lobby to that account's platformer level. See `src/door.py`.

**Fog of War**
Areas of the map hidden until the player explores them. Only used in lobby mode. Zombies are revealed when player gets within `reveal_radius`. See `src/game_map.py:73`.

### Game State & Progression

**Game State**
The current status of all game data: player position, zombie positions, score, health, etc. Defined in `src/models.py`.

**Game Status**
Enum defining the game's operational state: `RUNNING`, `PAUSED`, `GAME_OVER`, `VICTORY`. See `src/models.py`.

**Game Mode**
Whether the player is in lobby (top-down exploration) or level (platformer action). Controlled by `GameMap.mode` in `src/game_map.py:37`.

**Save State**
Persistent game progress stored to disk: completed levels, quarantined identities, score, etc. See `src/save_manager.py`.

**Level Manager**
System that tracks level progression, unlocking, and completion. See `src/level_manager.py`.

**Cheat Code**
Special keyboard sequence that unlocks features or skips content. Examples: "UNLOCK" (all levels), "SKIP" (current level). See `CHEAT_CODES.md`.

### Entities & Objects

**Entity**
Any interactive game object with position and behavior. Examples: player, zombie, projectile, third-party, boss.

**Player**
The character you control (Mega Man-style with ray gun). See `src/player.py`.

**Zombie**
Enemy representing an unused AWS identity. Has 3 HP, can be quarantined. See `src/zombie.py`.

**Third-Party**
Entity representing external organization access to AWS accounts. Has 10 HP, can be blocked. See `src/third_party.py`.

**Boss**
Special high-health enemy that appears in production environments. See `src/boss.py`.

**Projectile**
Bullets fired by the player or enemies. See `src/projectile.py`.

**Power-Up / Collectible**
Items that grant temporary abilities (rapid fire, speed boost, invincibility, etc.). Spawn on ~15% of platforms in levels. See `src/powerup.py` and `src/collectible.py`.

**Protected Entity**
A zombie or third-party that cannot be eliminated (purple shield). Includes Sonrai-managed identities and exempted identities. See `src/shield.py`.

### Game Mechanics

**Health Points (HP)**
Damage an entity can take before being eliminated. Zombies: 3 HP, Third-parties: 10 HP, Bosses: variable.

**Damage**
Amount of HP removed when an entity is hit. Currently 1 damage per projectile hit.

**Damage Multiplier**
Score bonus that increases every 10 eliminations. Affects points earned per kill.

**Quarantine**
The action of eliminating a zombie, which triggers a real Sonrai API call to quarantine that AWS identity. See `src/sonrai_client.py`.

**Elimination**
Reducing an entity's HP to 0. For zombies, triggers quarantine. For third-parties, triggers blocking.

**Spawn**
Creating a new entity in the game world at a specific position.

**Respawn**
Not currently implemented in this game (zombies don't respawn after quarantine).

### Difficulty & Progression

**Environment Type**
Category of AWS account: sandbox, staging, production, etc. Determines difficulty settings. See `src/difficulty_config.py`.

**Difficulty Configuration**
Settings that vary by environment type: zombie speed, health, reveal radius, etc. Production is hardest. See `src/difficulty_config.py`.

**Approval Collectible**
Special item required in production environments. You must collect approvals before eliminating zombies. See `src/approval.py`.

**Level Unlocking**
Progression system where levels must be completed sequentially. Sandbox is always unlocked. See `src/level_manager.py:147-159`.

## Zombie Blaster-Specific Terms

### Dual-Engine Architecture

**Lobby Mode**
Top-down exploration mode where you navigate between AWS account doors. Uses `GameMap` in "lobby" mode with fog-of-war. See `src/game_engine.py:71-100`.

**Level Mode / Platformer Mode**
Side-scrolling Mario-style gameplay inside an AWS account. Uses `GameMap` in "platformer" mode with gravity physics. See `src/game_engine.py:328-430`.

**Mode Transition**
Switching between lobby and level modes. Triggered by entering/exiting doors. See `src/game_engine.py:718-856`.

**Level Entry**
Process of transitioning from lobby into a specific account's platformer level. Loads zombies for that account only.

**Level Exit**
Returning from platformer level to lobby. Triggered by returning to the entrance platform.

**Landing Zone**
Starting position in lobby (bottom-left quadrant, near Sandbox door). See `src/game_engine.py:94-98`.

**Entrance Platform**
Special platform at the left edge of platformer levels. Returning here exits the level back to lobby.

### API Integration

**Sonrai API Client**
Service that communicates with Sonrai Security platform. Fetches identities, sends quarantine requests, etc. See `src/sonrai_client.py`.

**Identity**
An AWS IAM user, role, or service account. Unused identities become zombies in the game. See `src/models.py`.

**Unused Identity**
An AWS identity that hasn't logged in recently (configurable threshold). These are fetched from Sonrai and represented as zombies.

**Quarantine Action**
Sonrai API mutation that disables an unused identity. Triggered when a zombie is eliminated. See `docs/sonrai-api/queries/quarantine-identity.md`.

**Exemption**
An identity marked in Sonrai as exempt from quarantine. Shows as protected (purple shield) in game.

**Third-Party Access**
External organization with permissions to AWS resources. Can be blocked if unneeded. See `docs/sonrai-api/queries/third-party-access.md`.

### Technical Architecture

**Game Engine**
Core game logic and state management. Orchestrates player, zombies, collisions, and API calls. See `src/game_engine.py`.

**Event System**
Pygame's event queue for handling keyboard, mouse, window events. Processed in `game_engine.handle_input()`.

**Configuration Management**
Environment variables loaded from `.env` file. Includes API credentials and game settings. See `src/main.py:28-59`.

**Display Scaling**
System for rendering at base resolution (1280x720) and scaling to any window size while preserving aspect ratio. See `src/main.py:62-136`.

**Fullscreen Toggle**
Switching between windowed and fullscreen modes via F11, F key, or CMD+F. See `src/main.py:381-403`.

## Common Coordinate Systems

- **Tile Coordinates**: Position in grid units (e.g., room at tile 10, 5)
- **Pixel Coordinates**: Position in pixels (e.g., sprite at 160px, 80px)
- **Screen Coordinates**: Position relative to window (0,0 = top-left of window)
- **World Coordinates**: Position in the full game map (may be larger than screen)

## Performance Concepts

**Spatial Grid Optimization**
Dividing the world into cells and only checking collisions within nearby cells. Critical for handling 500+ zombies. See `src/collision.py`.

**Rendering Optimization**
Only drawing objects within camera view. Objects outside camera are skipped.

**Frame Budget**
Time available per frame (16.67ms at 60 FPS). If game logic exceeds budget, FPS drops.

## File Organization

```
src/
├── main.py              # Entry point, game loop, initialization
├── game_engine.py       # Core game logic, state management
├── game_map.py          # Map generation (lobby + platformer)
├── level_manager.py     # Level progression and unlocking
├── renderer.py          # All graphics rendering
├── player.py            # Player character logic
├── zombie.py            # Zombie entity behavior
├── third_party.py       # Third-party entity behavior
├── boss.py              # Boss entity behavior
├── projectile.py        # Bullet/projectile physics
├── collision.py         # Collision detection system
├── sonrai_client.py     # Sonrai API integration
├── models.py            # Data models (GameState, Vector2, etc.)
├── door.py              # Door entities for level transitions
├── powerup.py           # Power-up collectible system
├── approval.py          # Approval collectible system
├── save_manager.py      # Save/load game progress
├── difficulty_config.py # Difficulty settings per environment
└── shield.py            # Purple shield rendering for protected entities
```

## Quick Reference: Key Files

- **Game initialization**: `src/main.py:215-514`
- **Lobby engine logic**: `src/game_engine.py:71-100`
- **Level engine logic**: `src/game_engine.py:328-430`
- **Mode transitions**: `src/game_engine.py:718-856`
- **Collision system**: `src/collision.py`
- **Rendering pipeline**: `src/renderer.py`
- **API calls**: `src/sonrai_client.py`
- **Level progression**: `src/level_manager.py`
