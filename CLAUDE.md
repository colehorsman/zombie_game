# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sonrai Zombie Blaster - A retro-style 2D game that gamifies cloud security by representing unused AWS identities as "zombies". Each elimination triggers real quarantine actions via the Sonrai Security API.

**Dual-mode gameplay:**
- **Lobby Mode** (top-down): Explore a central hub with doors to AWS account levels, fog-of-war mechanics, third-party entities patrolling hallways
- **Level Mode** (platformer): Mario-style side-scrolling inside each AWS account with gravity physics, floating platforms, power-ups

## Common Commands

```bash
# Run the game
python src/main.py

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run a single test file
pytest tests/test_collision.py -v

# Run property-based tests only
pytest -k property

# Manual test launcher with guided plans
python test_launcher.py --feature powerups
python test_launcher.py --list  # See available test plans
```

## Architecture

### Core Components

```
src/
├── main.py           # Entry point, game loop, event handling
├── game_engine.py    # Core logic, dual-mode engine (lobby + level)
├── renderer.py       # Graphics rendering, camera, UI overlays
├── player.py         # Player character, movement, physics
├── zombie.py         # Zombie entity behavior and AI
├── collision.py      # Spatial grid collision detection (O(n) optimization)
├── sonrai_client.py  # GraphQL API integration (queries + mutations)
├── level_manager.py  # Level progression and unlocking
├── save_manager.py   # JSON persistence for game progress
└── models.py         # Data classes (GameState, Vector2, etc.)
```

### Dual-Engine Architecture

The game has two distinct modes managed in `game_engine.py`:
- **Lobby Engine** (~lines 71-100): Top-down, tile-based, fog-of-war, door-based transitions
- **Level Engine** (~lines 328-430): Platformer physics, gravity, dynamic level generation

Mode transitions happen when:
- Player enters a door → Lobby to Level (loads that account's zombies)
- Player returns to entrance → Level to Lobby (preserves progress)

### Key Systems

**Collision Detection** (`collision.py`): Uses spatial grid for O(n) performance with 500+ entities. Critical for 60 FPS with large zombie counts.

**API Integration** (`sonrai_client.py`): GraphQL queries for unused identities, exemptions, third-party access. Mutations for quarantine and blocking.

**Rendering** (`renderer.py`): 1280x720 base resolution with aspect ratio preservation, fullscreen support, camera-based viewport.

## Critical Implementation Rules

### Scope Handling
- **NEVER** construct Sonrai scopes manually
- Always fetch real scopes from CloudHierarchyList API
- Filter to real accounts (exclude OUs and root)

### Protected Entities
- Sonrai third-party access (name === "Sonrai") and exempted identities are invulnerable
- Display purple shields, never quarantine or block

### Damage System
- Zombies: 3 HP, Third parties: 10 HP
- Damage multiplier increases every 10 eliminations

## Testing

Tests are in `tests/` directory. Key test files:
- `test_collision.py` - Spatial grid and collision detection
- `test_projectile.py` - Projectile physics
- `test_zombie.py` - Zombie behavior
- `test_controller_input.py` - Controller/keyboard input handling

Mock pygame and API calls in tests. Use fixtures from `conftest.py`.

## Environment Configuration

Required in `.env`:
```
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here
```

Optional:
```
GAME_WIDTH=1280
GAME_HEIGHT=720
FULLSCREEN=false
TARGET_FPS=60
```

## Cheat Codes (for testing)

Type letter sequences during gameplay:
- `UNLOCK` - Unlock all levels
- `SKIP` - Skip current level

See `docs/CHEAT_CODES.md` for full list.
