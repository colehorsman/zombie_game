# Sonrai Zombie Blaster (v2 - Hybrid Mode)

> **Branch: v2** - The ultimate hybrid experience combining top-down lobby exploration with Mario-style platformer levels!
> Looking for other versions? Check out `v1` for original top-down only or `levels` for platformer only.

A retro-style video game that visualizes and gamifies the process of identifying and remediating unused AWS identities through the Sonrai API. Blast zombies representing real unused identities and watch your cloud security posture improve!

## About This Version

This is **v2 - the hybrid dual-mode version** combining the best of both worlds:

### Lobby Mode (Top-Down)
- Explore a central hub with doors to each AWS account
- Top-down navigation with fog-of-war mechanics
- Third-party entities patrol hallways around production rooms
- Walk through doors to enter account-specific platformer levels

### Level Mode (Platformer)
- Mario-style side-scrolling gameplay inside each AWS account
- Jump between randomized floating platforms
- Gravity-based physics for player and zombies
- Dynamic level width scaling (512 zombies = 27,200px wide!)
- Power-ups scattered on ~15% of platforms
- No fog-of-war - see all zombies from the start

### Progression System
- 🔒 Levels unlock linearly after completing previous levels
- 🏖️ Sandbox account always unlocked (great for learning)
- ✅ Complete a level by quarantining all zombies and returning to lobby
- 🔓 **Cheat codes** for testing: `UNLOCK` (all levels) and `SKIP` (current level)

## Key Features

- 🎮 **Dual-mode gameplay**: Lobby exploration + platformer action
- 🔫 Mega Man-style character with ray gun
- 🧟 Each zombie represents a real unused AWS identity from Sonrai
- 🔒 Eliminating zombies triggers real quarantine actions via Sonrai API
- 💜 Protected entities with purple shields (Sonrai + exempted identities)
- 💥 Damage system with health points (zombies: 3 HP, third parties: 10 HP)
- 📈 Score tracking with damage multiplier (increases every 10 eliminations)
- 📊 Real-time progress tracking and statistics
- 🎯 Third-party access visualization and blocking in lobby
- 💬 Retro Game Boy-style congratulations messages
- 🎪 Randomized platform layouts for varied gameplay
- 🎁 Power-up collectibles in platformer levels
- 🔓 Admin cheat codes for testing (see [CHEAT_CODES.md](CHEAT_CODES.md))

## Screenshots

*Coming soon! Screenshots of gameplay, protected entities with purple shields, damage system, and more.*

<!-- Placeholder for screenshots - to be added -->
<!--
![Main Gameplay](assets/screenshots/gameplay.png)
*Main gameplay showing player shooting zombies with UI elements*

![Congratulations Message](assets/screenshots/congratulations.png)
*Retro Game Boy-style congratulations message when eliminating a zombie*

![Protected Entities](assets/screenshots/protected_entities.png)
*Purple shields indicating protected Sonrai and exempted entities*

![Damage System](assets/screenshots/damage_system.png)
*Health bars and damage numbers in action*
-->

## Requirements

### System Requirements
- **OS**: macOS, Linux, or Windows
- **Python**: 3.11 or higher
- **Display**: 800x600 minimum resolution

### Sonrai Requirements
- Active Sonrai Security account
- API access token (see Configuration section)
- Organization ID
- GraphQL API URL

### Python Dependencies
- pygame 2.5+
- python-dotenv
- requests

## Installation Runbook

Follow these steps to set up the game on your machine:

### Step 1: Extract the Project

If you received a zip file:
```bash
unzip zombie_game.zip
cd zombie_game
```

If you're cloning from git:
```bash
git clone <repository-url>
cd zombie_game
```

### Step 2: Verify Python Version

Check that you have Python 3.11 or higher:
```bash
python3 --version
```

If you need to install Python 3.11+:
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt install python3.11` (or use your package manager)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Step 3: Create Virtual Environment

Create and activate a Python virtual environment:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

Install all required Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Configure Sonrai API Credentials

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your Sonrai API credentials:
   - Log into your Sonrai Security account
   - Navigate to **Settings** → **API Tokens**
   - Create a new API token with `read:data` and `read:platform` scopes
   - Copy your token, org ID, and GraphQL URL

3. Edit `.env` with your credentials:
```bash
# Open in your preferred editor
nano .env
# or
vim .env
# or
code .env  # VS Code
```

4. Update these values:
```
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here
```

**Note**: Keep your `.env` file private! It contains sensitive credentials.

### Step 6: Verify Installation

Test that everything is set up correctly:
```bash
python3 src/main.py
```

If successful, you should see the game window open!

## Configuration

The `.env` file controls both API access and game settings:

```env
# Sonrai API Configuration (REQUIRED)
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here

# Game Configuration (OPTIONAL - defaults shown)
GAME_WIDTH=800
GAME_HEIGHT=600
TARGET_FPS=60
```

## Troubleshooting

### "SONRAI_API_TOKEN is required in .env file"
- Make sure you copied `.env.example` to `.env`
- Verify your `.env` file has valid credentials
- Check that there are no extra spaces around the `=` signs

### "Failed to authenticate with Sonrai API"
- Verify your API token is still valid (check expiration date)
- Confirm your organization ID is correct
- Test your token using the Sonrai GraphQL explorer

### "ModuleNotFoundError: No module named 'pygame'"
- Make sure your virtual environment is activated (`source venv/bin/activate`)
- Re-run `pip install -r requirements.txt`

### Game window doesn't open / black screen
- Check that your display resolution is at least 800x600
- Try updating pygame: `pip install --upgrade pygame`
- On Linux, you may need to install SDL libraries: `sudo apt install libsdl2-dev`

### "No zombies found" / Empty game
- Verify your AWS account has unused identities
- Check the `AWS_ACCOUNT` filter in your `.env` file
- Try adjusting `DAYS_SINCE_LAST_LOGIN` in `.env`

## Usage

Run the game:
```bash
python src/main.py
```

## Controls

### Lobby Mode (Top-Down)
- **Arrow Keys or WASD**: Move in 8 directions
- **Space**: Fire ray gun at third-party entities
- **Walk into doors**: Enter account levels

### Platformer Mode (Side-Scrolling)
- **Arrow Keys (← →) or A/D**: Move left/right
- **Up Arrow or W**: Jump (gravity-based physics)
- **Space**: Fire ray gun at zombies
- **Return to entrance**: Complete level and return to lobby

### Universal Controls
- **Enter**: Dismiss messages and continue
- **ESC**: Pause/quit game
- **Cheat Codes**: Type letter sequences (see [CHEAT_CODES.md](CHEAT_CODES.md))

The player character will automatically stop when you release the movement keys.

## How It Works

1. The game fetches unused AWS identities from your Sonrai account
2. Each zombie in the game represents one unused identity
3. When you eliminate a zombie (3 hits), the game sends a quarantine request to Sonrai
4. Successfully quarantined identities are permanently removed from the game
5. Third-party entities patrol the map and can be blocked (10 hits)
6. Protected entities (exemptions + Sonrai) display purple shields and are invulnerable
7. Your goal: eliminate all zombies and improve your cloud security!

## Sonrai API Integration

This game integrates with the Sonrai Security platform using GraphQL queries and mutations.

**Full API Documentation**: [docs/sonrai-api/README.md](docs/sonrai-api/README.md)

Quick links:
- [Unused Identities Query](docs/sonrai-api/queries/unused-identities.md) - Fetch zombies
- [Quarantine Mutation](docs/sonrai-api/queries/quarantine-identity.md) - Eliminate zombies
- [Third Party Query](docs/sonrai-api/queries/third-party-access.md) - Fetch 3rd parties
- [Exemptions Query](docs/sonrai-api/queries/exempted-identities.md) - Protected entities
- [Quick Reference](docs/sonrai-api/QUICK_REFERENCE.md) - All API calls at a glance

See [Integration Guide](docs/sonrai-api/INTEGRATION_GUIDE.md) for detailed integration information.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run property-based tests only
pytest -k property
```

### Project Structure

```
sonrai-zombie-blaster/
├── src/
│   ├── main.py              # Entry point
│   ├── game_engine.py       # Core game loop
│   ├── sonrai_client.py     # API integration
│   ├── renderer.py          # Graphics rendering
│   ├── models.py            # Data models
│   ├── player.py            # Player character
│   ├── zombie.py            # Zombie entities
│   ├── projectile.py        # Projectiles
│   └── collision.py         # Collision detection
├── tests/                   # Test files
├── .env                     # Configuration (not in git)
├── .env.example             # Example configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## License

[Your License Here]

## Credits

Built with Python and Pygame. Integrates with Sonrai Security's Cloud Permissions Firewall.

---

## Engineering & Architecture

This section provides technical details about the game's implementation, architecture, and technology stack.

### Technology Stack

**Core Technologies**
- **Language**: Python 3.11+
- **Game Engine**: Pygame 2.5+ (2D game framework with SDL bindings)
- **API Integration**: Sonrai GraphQL API via `requests` library
- **Configuration**: python-dotenv for environment variable management
- **State Persistence**: JSON-based save system

**Total Codebase**: ~8,380 lines of Python across 21 modules

### Architecture Overview

#### Dual-Engine System

The game features a unique **dual-mode architecture** that seamlessly transitions between two distinct gameplay modes:

1. **Lobby Engine** (Top-Down Mode)
   - Location: `src/game_engine.py:71-100`
   - Camera-based map exploration with fog-of-war mechanics
   - Tile-based collision detection (16x16 pixel tiles)
   - Zombie distribution across AWS account rooms
   - Third-party entities patrolling hallways
   - Door-based level transitions

2. **Level Engine** (Platformer Mode)
   - Location: `src/game_engine.py:328-430`
   - Mario-style side-scrolling physics with gravity
   - Randomly generated floating platform layouts
   - Dynamic level width scaling (512 zombies = 27,200px wide)
   - Power-up collectibles spawning on ~15% of platforms
   - Account-specific zombie loading

**Mode Transitions**: `src/game_engine.py:718-856`
- Entering a door: Lobby → Level (loads that account's zombies only)
- Returning to entrance: Level → Lobby (preserves progress)

#### Core Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                      Main Loop                          │
│                   (src/main.py)                         │
│  • Event handling                                       │
│  • Delta time calculation (60 FPS)                      │
│  • Display scaling & fullscreen                         │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌─────────────┐         ┌──────────────┐
│ Game Engine │◄────────│  Renderer    │
│  (Logic)    │         │  (Graphics)  │
└──────┬──────┘         └──────────────┘
       │
       ├─► GameMap (lobby/platformer map generation)
       │
       ├─► LevelManager (progression & unlocking)
       │
       ├─► Player (character controls & physics)
       │
       ├─► Zombie/ThirdParty/Boss (entity behavior)
       │
       ├─► Collision (spatial grid optimization)
       │
       ├─► SonraiAPIClient (GraphQL integration)
       │
       └─► SaveManager (persistence)
```

#### Key Subsystems

**1. Rendering Pipeline** (`src/renderer.py`)
- Base resolution: 1280x720 (configurable via `GAME_WIDTH`/`GAME_HEIGHT`)
- Aspect ratio preservation with letterboxing/pillarboxing
- Fullscreen support (toggle with F11, F, or CMD+F)
- Camera-based viewport with world-to-screen coordinate transformation
- Minimap overlay (lobby mode only)
- Health bars, shields, damage numbers, UI overlays

**2. Collision Detection** (`src/collision.py`)
- **Spatial Grid Optimization**: O(n) instead of O(n²) for 500+ entities
- Divides world into grid cells, only checks nearby entities
- Handles player-zombie, player-projectile, projectile-zombie collisions
- Platform collision detection in platformer mode

**3. Physics System**
- **Lobby Mode**: 8-directional movement, diagonal normalization
- **Platformer Mode**: Gravity-based jumping, horizontal acceleration/deceleration
- Delta time-based movement for frame-rate independence
- Velocity measured in pixels/second

**4. API Integration** (`src/sonrai_client.py`)
- GraphQL queries: unused identities, third-party access, exemptions
- GraphQL mutations: quarantine identities, block third-parties
- JWT token authentication
- Error handling and retry logic
- Full API documentation: `docs/sonrai-api/`

**5. State Management**
- **GameState** (`src/models.py`): score, eliminations, play time, status
- **Save System** (`src/save_manager.py`): JSON persistence of progress, quarantined identities, completed levels
- **Level Progression** (`src/level_manager.py`): linear unlocking, level completion tracking

**6. Difficulty System** (`src/difficulty_config.py`)
- Environment-based difficulty: sandbox → staging → production
- Configurable: zombie speed, health, reveal radius, boss battles
- Production environments require approval collectibles before quarantine

### Controller Support

**Supported Input Devices**
- Keyboard (primary): Arrow keys, WASD, Space, Enter, ESC
- Wireless game controllers: Xbox, PlayStation, Nintendo Switch Pro
- D-Pad navigation: 8-directional movement in lobby
- Analog stick support: Smooth directional input
- Button mapping: A/Cross = Jump, X/Square = Shoot

**Controller Configuration**
- Button debouncing for reliable input
- Dead zone handling for analog sticks
- Tested with:
  - Xbox Wireless Controller
  - PlayStation DualShock/DualSense
  - Nintendo Switch Pro Controller

**Test Files**: `tests/test_controller.py`, `tests/dpad_test.py`, `tests/quick_controller_test.py`

### File Structure

```
zombie_game/
├── src/                     # Source code (8,380 lines)
│   ├── main.py             # Entry point & game loop
│   ├── game_engine.py      # Core game logic (lobby + level engines)
│   ├── game_map.py         # Map generation (both modes)
│   ├── level_manager.py    # Level progression system
│   ├── renderer.py         # Graphics rendering pipeline
│   ├── player.py           # Player character behavior
│   ├── zombie.py           # Zombie entity AI
│   ├── third_party.py      # Third-party entity AI
│   ├── boss.py             # Boss entity (production levels)
│   ├── projectile.py       # Bullet physics
│   ├── collision.py        # Spatial grid collision system
│   ├── sonrai_client.py    # API integration
│   ├── models.py           # Data models (GameState, Vector2, etc.)
│   ├── door.py             # Level transition triggers
│   ├── powerup.py          # Power-up system
│   ├── approval.py         # Approval collectibles
│   ├── save_manager.py     # Save/load persistence
│   ├── difficulty_config.py # Environment difficulty settings
│   └── shield.py           # Protected entity shields
│
├── tests/                   # Test suite
│   ├── test_controller.py  # Controller input tests
│   ├── dpad_test.py        # D-pad navigation tests
│   └── quick_controller_test.py # Quick controller validation
│
├── assets/                  # Game assets
│   ├── reinvent_floorplan.png # Lobby background map
│   └── aws_accounts.csv    # Account metadata (7 levels)
│
├── docs/                    # Documentation
│   └── sonrai-api/         # API integration docs
│       ├── README.md       # API overview
│       ├── queries/        # GraphQL queries & mutations
│       └── INTEGRATION_GUIDE.md
│
├── .env                     # Configuration (API credentials)
├── .env.example            # Configuration template
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── GLOSSARY.md             # Game development term definitions
└── CHEAT_CODES.md          # Developer cheat codes
```

### Development Status & Roadmap

**Current Status: v2 (Hybrid Mode) - Fully Functional** ✅

**Implemented Features**
- ✅ Dual-mode gameplay (lobby + platformer)
- ✅ 7-level progression system with unlocking
- ✅ Sonrai API integration (fetch, quarantine, block)
- ✅ Save/load system with progress persistence
- ✅ Controller support (keyboard + gamepad)
- ✅ Difficulty scaling by environment type
- ✅ Power-up system with 5+ collectible types
- ✅ Boss battles in production environments
- ✅ Protected entity system (exemptions + Sonrai identities)
- ✅ Fullscreen support with aspect ratio preservation
- ✅ Spatial grid collision optimization
- ✅ Fog-of-war mechanics (lobby only)
- ✅ Dynamic level generation based on zombie count
- ✅ Damage multiplier scoring system
- ✅ Third-party access blocking
- ✅ Approval collectible system (production)

**Known Limitations**
- Single-player only (no multiplayer)
- No audio/music (intentionally minimal for demo)
- Limited to Pygame's 2D rendering (no 3D)
- Requires local Python installation (not web-based)

**Future Considerations**

*Cloud Deployment*
- **AWS Hosting**: Not currently planned, but technically feasible
  - Option 1: Package as Lambda function with VNC/framebuffer (complex, high latency)
  - Option 2: EC2 instance with remote desktop (simpler, better performance)
  - Option 3: Convert to web game (requires complete rewrite in JavaScript/WebGL)
- **Current Recommendation**: Keep as local desktop application
  - Lower latency (critical for 60 FPS gameplay)
  - No cloud costs for compute
  - Easier to maintain and debug
  - Better suited for internal tool/demo use

*Potential Enhancements*
- Audio system (background music, sound effects)
- Additional power-up types
- Boss variety (different bosses per environment)
- Achievements/statistics tracking
- Leaderboard integration
- Co-op multiplayer (requires significant architecture changes)

### Performance Characteristics

**Scalability**
- Tested with 500+ zombies simultaneously
- 60 FPS maintained on modern hardware (2020+ MacBook Pro)
- Spatial grid keeps collision checks efficient even with large entity counts
- Level width scales dynamically (largest level: 27,200px wide for 512 zombies)

**Memory Footprint**
- ~50-100 MB RAM typical usage
- Scales with zombie count and map size
- Save files: <100 KB per save

**Network Requirements**
- Initial API calls: ~2-5 seconds for full account fetch
- Quarantine/block operations: <500ms per action
- Offline mode: Not supported (requires API connection)

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run with debug logging
LOG_LEVEL=DEBUG python src/main.py

# Run tests
pytest tests/

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Environment Variables

```env
# Required - Sonrai API
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here

# Optional - Display Settings
GAME_WIDTH=1280              # Base rendering width
GAME_HEIGHT=720              # Base rendering height
FULLSCREEN=false             # Start in fullscreen mode
TARGET_FPS=60                # Frame rate target

# Optional - Gameplay
MAX_ZOMBIES=1000             # Max zombies per account
```

### Architecture Decisions & Rationale

**Why Pygame?**
- Lightweight 2D framework with good Python integration
- Easy to prototype and iterate quickly
- No need for Unity/Unreal complexity for a 2D demo
- Cross-platform (macOS, Linux, Windows)

**Why Dual-Engine?**
- Lobby provides context (see all accounts, understand scope)
- Platformer provides engaging action gameplay
- Hybrid approach offers best of both worlds
- Matches SDLC progression metaphor (lobby = org overview, levels = per-account work)

**Why Spatial Grid?**
- Naive O(n²) collision checking fails at 100+ entities
- Spatial grid reduces to O(n) with constant-factor overhead
- Critical for 500+ zombie levels to maintain 60 FPS

**Why Save System?**
- Game sessions can be interrupted (real-world work)
- Prevents re-quarantining already handled identities
- Preserves sense of progression and achievement
- Enables iterative gameplay (clear accounts one at a time)

### Contributing & Development

**Code Style**
- PEP 8 compliant
- Type hints where appropriate
- Docstrings for all public functions/classes
- Logging via Python's `logging` module

**Testing**
- Unit tests for core logic
- Integration tests for API calls
- Controller input validation tests

**Dependencies**
- Minimal external dependencies (3 total: pygame, python-dotenv, requests)
- All dependencies pinned in `requirements.txt`

### Glossary

For detailed definitions of game development terms used in this project, see **[GLOSSARY.md](GLOSSARY.md)**.

Quick examples:
- **Sprite**: 2D game character/object (player, zombie, projectile)
- **Game Loop**: The main execution cycle (input → update → render)
- **Delta Time**: Time between frames, used for smooth movement
- **Spatial Grid**: Performance optimization for collision detection
- **Game Mode**: Lobby (top-down) vs Level (platformer)

---
