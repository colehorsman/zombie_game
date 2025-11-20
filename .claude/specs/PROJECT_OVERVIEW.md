# Sonrai Zombie Blaster - Project Overview

## Vision

A retro-style 2D game that visualizes and gamifies cloud security remediation by representing unused AWS identities as "zombies" that must be eliminated through the Sonrai Security API. Each zombie elimination triggers real quarantine actions, making cloud security engaging and interactive.

## Current Implementation Status

### ✅ Completed (Base Game)
- Core game loop with 60 FPS target
- Player character with movement and shooting
- Zombie entities mapped 1:1 to real Sonrai unused identities
- Projectile physics and collision detection
- Real-time Sonrai API integration
- Quarantine actions via Cloud Permissions Firewall
- Retro Game Boy-style congratulations messages
- Health system (zombies: 3 HP, third parties: 10 HP)
- Protected entities with purple shields (Sonrai + exemptions)
- Third-party access visualization and blocking
- Damage multiplier system (increases every 10 eliminations)
- Real account scope handling via CloudHierarchyList API

### 🚧 Planned Enhancements
- Multi-level progression (AWS accounts as levels)
- Boss battles (high-risk entities)
- Level transition screens
- Enhanced visual feedback (damage numbers, animations)
- Boss AI with minion spawning
- Comprehensive gameplay screenshots

## Technology Stack

- **Language**: Python 3.11+
- **Game Framework**: Pygame 2.5+
- **API Client**: requests
- **Configuration**: python-dotenv
- **Testing**: pytest, Hypothesis (property-based testing)

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         Game Loop & Main Entry          │
│           (src/main.py)                 │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼─────────┐
│  Game Engine   │    │   API Client     │
│  - Physics     │    │   - Auth         │
│  - Collision   │    │   - Queries      │
│  - State Mgmt  │    │   - Quarantine   │
│  - Level Mgmt  │    │   - Exemptions   │
│  - Damage Sys  │    │   - Scopes       │
└───────┬────────┘    └────────┬─────────┘
        │                      │
┌───────▼────────┐    ┌────────▼─────────┐
│   Renderer     │    │   Data Models    │
│  - Sprites     │    │   - Zombie       │
│  - UI          │    │   - Player       │
│  - Health Bars │    │   - ThirdParty   │
│  - Shields     │    │   - Protected    │
└────────────────┘    └──────────────────┘
```

## Core Gameplay Loop

1. Fetch unused identities from Sonrai API
2. Create zombie entities (1:1 mapping)
3. Player moves and shoots zombies
4. Zombies take damage (3 hits to eliminate)
5. On elimination, send quarantine request to Sonrai
6. Display retro congratulations message
7. Score increases, damage multiplier grows
8. Continue until all zombies eliminated

## Key Design Principles

1. **1:1 Mapping**: Each zombie represents exactly one real unused identity
2. **Real Actions**: Every elimination triggers actual Sonrai quarantine
3. **Simple Retro Graphics**: Chrome dinosaur game aesthetic
4. **Frame-Independent Physics**: Delta time for smooth gameplay
5. **Graceful Error Handling**: Never crash, always inform user
6. **Property-Based Testing**: Verify correctness properties across all inputs
7. **Real Scopes Only**: Always use CloudHierarchyList for accurate scope paths

## Critical Implementation Details

### Scope Handling
- **NEVER** construct scopes manually
- Always fetch real scopes from CloudHierarchyList API
- Filter to real accounts (exclude OUs and root)
- Cache scopes at startup for performance

### Protected Entities
- Sonrai third-party access (identified by name "Sonrai")
- Exempted identities from Sonrai API
- Display purple shields (invulnerable to damage)
- Never quarantine or block protected entities

### Damage System
- Regular zombies: 3 HP
- Third parties: 10 HP
- Base damage: 1 per projectile
- Damage multiplier: +1 every 10 successful quarantines
- Only eliminate at 0 HP

## File Organization

```
zombie_game/
├── src/                      # Source code
│   ├── main.py              # Entry point
│   ├── game_engine.py       # Core game logic
│   ├── sonrai_client.py     # Sonrai API integration
│   ├── renderer.py          # Graphics rendering
│   ├── player.py            # Player character
│   ├── zombie.py            # Zombie entities
│   ├── third_party.py       # Third-party entities
│   ├── projectile.py        # Projectiles
│   ├── collision.py         # Collision detection
│   ├── models.py            # Data models
│   └── shield.py            # Shield rendering
├── assets/                   # Game assets
│   ├── aws_accounts.csv     # AWS account data
│   ├── sonrai_logo.png      # Branding
│   └── screenshots/         # Gameplay screenshots
├── docs/                     # Documentation
│   └── sonrai-api/          # API documentation
│       ├── README.md        # API docs index
│       ├── INTEGRATION_GUIDE.md
│       ├── QUICK_REFERENCE.md
│       ├── queries/         # Query documentation
│       └── schema.json      # Downloaded GraphQL schema
├── dev_tests/               # Development test scripts
│   ├── download_sonrai_schema.py
│   └── search_sonrai_schema.py
├── tests/                   # Unit and property tests
├── .claude/                 # Claude Code configuration
│   └── specs/              # This directory
├── .env                     # Configuration (not in git)
├── .env.example            # Example configuration
├── requirements.txt        # Python dependencies
├── README.md               # User-facing documentation
└── QUICKSTART.md           # Quick start guide
```

## Development Workflow

1. **Check Schema**: Use `search_sonrai_schema.py` to find correct query/type names
2. **Document First**: Create API query documentation in `docs/sonrai-api/queries/`
3. **Implement**: Add functionality to appropriate source file
4. **Test**: Write property-based tests for correctness properties
5. **Update Docs**: Add to README and integration guide

## Quick Reference Commands

### Development
```bash
# Run the game
python3 src/main.py

# Search GraphQL schema
python3 dev_tests/search_sonrai_schema.py --query CloudHierarchy
python3 dev_tests/search_sonrai_schema.py --type UnusedIdentity

# Download latest schema
python3 dev_tests/download_sonrai_schema.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run property tests only
pytest -k property
```

## Next Development Priorities

See `ENHANCEMENTS.md` for detailed enhancement specifications including:
- Multi-level progression system
- Boss battles with AI
- Enhanced visual feedback
- Level transition screens
- Comprehensive documentation with screenshots
