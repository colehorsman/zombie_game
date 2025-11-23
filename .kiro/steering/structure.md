# Project Structure

## Directory Layout

```
sonrai-zombie-blaster/
├── src/                      # Main source code
├── assets/                   # Game assets and resources
├── docs/                     # Documentation
├── tests/                    # Test files
├── dev_tests/               # Development utilities
├── .kiro/                   # Kiro AI configuration
├── .claude/                 # Claude AI specs (legacy)
└── .vscode/                 # VS Code settings
```

## Source Code (`src/`)

Core game modules organized by responsibility:

- `main.py` - Entry point, initialization, game loop
- `game_engine.py` - Core game loop and state management (1500+ lines)
- `renderer.py` - Graphics rendering and display
- `models.py` - Data models and game state
- `player.py` - Player character logic
- `zombie.py` - Zombie entity behavior
- `projectile.py` - Projectile physics
- `collision.py` - Collision detection with spatial grid
- `sonrai_client.py` - Sonrai API integration
- `game_map.py` - Map navigation and level layout
- `level_manager.py` - Level progression system
- `difficulty_config.py` - Environment-specific difficulty settings
- `door.py` - Door entities for level transitions
- `third_party.py` - Third-party entity logic
- `boss.py` - Boss battle mechanics
- `powerup.py` - Power-up collectibles
- `shield.py` - Shield rendering for protected entities
- `approval.py` - Approval system for production environments
- `save_manager.py` - Save/load game state
- `collectible.py` - Collectible items

## Assets (`assets/`)

- `reinvent_floorplan.png` - Lobby map background
- `Floor Plan - Updated.pdf` - Reference floor plan
- `aws_accounts.csv` - AWS account metadata for levels
- `screenshots/` - Game screenshots
- `sonrai_logo.png` - Branding assets

## Documentation (`docs/`)

### Sonrai API Documentation (`docs/sonrai-api/`)

Comprehensive API integration guides:
- `README.md` - Overview of Sonrai integration
- `INTEGRATION_GUIDE.md` - Detailed integration instructions
- `QUICK_REFERENCE.md` - Quick API reference
- `schema.json` - GraphQL schema
- `queries/` - Example queries and mutations
  - `unused-identities.md` - Fetch zombies
  - `quarantine-identity.md` - Eliminate zombies
  - `third-party-access.md` - Fetch third parties
  - `exempted-identities.md` - Protected entities
  - `block-third-party.md` - Block third parties
  - `cloud-hierarchy.md` - Account hierarchy
  - `accounts-unused-identities.md` - Account-level queries

## Development Tools (`dev_tests/`)

- `download_sonrai_schema.py` - Download GraphQL schema
- `search_sonrai_schema.py` - Search schema definitions

## Configuration Files

- `.env` - Environment variables (not in git)
- `.env.example` - Template for environment setup
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- `CHEAT_CODES.md` - Admin cheat codes

## Architecture Patterns

### Game State Management
- Centralized `GameState` model in `models.py`
- State transitions: LOBBY → PLAYING → BOSS_BATTLE → LOBBY
- Persistent state via `SaveManager`

### Entity System
- Base entity classes with position, velocity, bounds
- Spatial grid for efficient collision detection
- Component-based power-up system

### API Integration
- `SonraiAPIClient` handles all GraphQL operations
- Async-style error handling with logging
- Real-time quarantine actions on zombie elimination

### Rendering Pipeline
- Separate game surface (base resolution) and display surface (scaled)
- Aspect ratio preservation with letterboxing/pillarboxing
- Camera system for map scrolling and player tracking
