# Changelog

All notable changes to Sonrai Zombie Blaster are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Batch quarantine for Arcade Mode
- Enhanced raygun visual design
- Zelda-style pause menu
- Damage numbers on hit
- Additional service protection quests (S3, RDS)

## [2.0.0] - 2024-11-27

### Added - Major Features

#### Arcade Mode System
- **Arcade Mode Manager** - 60-second timed elimination challenges
- **Elimination Queue** - Queue identities for batch quarantine
- **Combo System** - Track consecutive eliminations with multiplier
- **Power-Up Integration** - Power-ups affect arcade performance
- **Results Screen** - Post-game statistics and menu system
- **Menu Navigation** - Keyboard and controller support for results menu

#### Quest System Enhancements
- **Service Protection Quest** - Timed race against AI hacker
- **JIT Access Quest** - Protect admin roles with JIT enrollment
- **Quest State Machine** - Robust state management (NOT_STARTED → TRIGGERED → ACTIVE → COMPLETED/FAILED)
- **Quest Failure Handling** - Proper cleanup and state reset

#### Performance Optimizations
- **Spatial Grid Collision** - 18.5× speedup (O(n²) → O(n))
- **Frustum Culling** - Only render visible entities
- **Efficient Physics** - Optimized gravity and collision calculations

### Added - Quality of Life

#### Controller Support
- **8BitDo SN30 Pro** - Full button mapping
- **Xbox Controllers** - Native support
- **PlayStation Controllers** - Native support
- **Hot-Plug Support** - Connect controllers during gameplay

#### Save System
- **Autosave** - Every 30 seconds
- **Progress Persistence** - Level completion tracking
- **State Recovery** - Resume from last position

#### Visual Enhancements
- **Purple Shields** - Protected entity indicators
- **Health Bars** - Damage visualization
- **Flash Effects** - Hit feedback
- **Fog-of-War** - Lobby exploration mechanic

### Fixed - Critical Bugs

#### Collision Detection
- **Zombie Invulnerability Bug** - Projectiles passing through zombies after quest completion
- **Spatial Grid Recreation** - Grid now recreates when entering levels
- **Quarantine Flag Reset** - Proper cleanup on quest success/failure
- **Hidden Flag Management** - Zombies properly visible after quest

#### Door Interaction
- **Re-Entry Cooldown** - 1-second cooldown prevents immediate re-entry
- **Lobby Spawn Position** - Player spawns at center, away from doors
- **Door Collision** - Improved collision detection for level entry

#### Quest System
- **State Cleanup** - All zombie flags reset on quest completion
- **Timer Management** - Proper countdown and expiration handling
- **Hacker Spawning** - Correct spawn position and pathfinding
- **Message Dismissal** - ENTER/SPACE keys properly dismiss quest dialogs

### Changed - Improvements

#### Architecture
- **Dual-Engine System** - Seamless lobby ↔ platformer transitions
- **Mode-Aware Physics** - Different physics for each mode
- **Modular Quest System** - Easy to add new quests
- **Event-Driven Updates** - Cleaner state management

#### API Integration
- **Scope Validation** - Always use real CloudHierarchy scopes
- **Error Handling** - Exponential backoff retry logic
- **Graceful Degradation** - Game continues on API errors
- **Request Logging** - Better debugging information

#### Testing
- **191 Total Tests** - Comprehensive test coverage
- **92.7% Pass Rate** - 177 passing tests
- **Integration Tests** - Gameplay scenario simulation
- **Property Tests** - Collision detection validation

### Performance

#### Benchmarks
- **60 FPS** - Maintained with 500+ entities
- **<100ms** - Average API response time
- **~75 MB** - Memory usage with 500 zombies
- **18.5×** - Collision detection speedup

#### Scalability
- **512 Zombies** - Tested maximum in single level
- **27,200px** - Maximum level width generated
- **170 Platforms** - Procedurally generated
- **60 FPS** - Performance maintained throughout

## [1.0.0] - 2024-11-15

### Added - Initial Release

#### Core Gameplay
- **Top-Down Lobby** - Explore AWS organization hallway
- **Platformer Levels** - Side-scrolling account cleanup
- **Zombie Entities** - Unused AWS identities
- **Third-Party Entities** - External access visualization
- **Boss Battles** - High-risk identity encounters

#### API Integration
- **Sonrai GraphQL** - Real-time cloud data
- **Quarantine Mutations** - Actual identity quarantine
- **Third-Party Blocking** - Real access revocation
- **Exemption Handling** - Protected entity support

#### Game Systems
- **Physics Engine** - Gravity, jumping, collision
- **Camera System** - Follow player, smooth scrolling
- **Level Generation** - Procedural platform placement
- **Power-Up System** - 6 AWS-themed power-ups

#### Visual Systems
- **8-Bit Sprites** - Retro aesthetic
- **Particle Effects** - Explosions, impacts
- **UI/HUD** - Score, health, timer display
- **Message System** - Quest dialogs, notifications

### Technical

#### Architecture
- **Game Engine** - 60 FPS game loop
- **Renderer** - Pygame-based graphics
- **Collision System** - Rectangle-based detection
- **State Management** - Centralized game state

#### Development
- **Python 3.11+** - Modern Python features
- **Pygame 2.5** - Hardware acceleration
- **Type Hints** - Full type safety
- **Documentation** - Comprehensive docs

## Version History

### v2.0.0 (Current) - Hybrid Mode
- Dual-engine architecture
- Quest system with side quests
- Arcade mode
- Performance optimizations
- Comprehensive testing

### v1.0.0 - Initial Release
- Top-down lobby
- Platformer levels
- Basic API integration
- Core gameplay mechanics

## Migration Guides

### Upgrading from v1.0.0 to v2.0.0

**Breaking Changes:**
- Save file format changed (automatic migration)
- API client interface updated
- Game state structure modified

**New Features:**
- Arcade mode available in all levels
- Quest system triggers automatically
- Controller support enabled by default

**Configuration:**
```bash
# Update .env with new optional settings
ARCADE_MODE_ENABLED=true
QUEST_SYSTEM_ENABLED=true
```

## Development Statistics

### Code Metrics
- **Total Lines:** 8,380
- **Modules:** 21
- **Classes:** 45
- **Functions:** 180
- **Test Files:** 28

### Commit History
- **Total Commits:** 250+
- **Contributors:** 3
- **Branches:** 5 (main, v1, v2, levels, feature/*)
- **Pull Requests:** 45

### Test Coverage
- **Unit Tests:** 134 (70%)
- **Integration Tests:** 48 (25%)
- **Manual Tests:** 9 (5%)
- **Total Coverage:** 85%+

## Acknowledgments

### Contributors
- Cole Horsman - Lead Developer
- Sonrai Security Team - Product guidance
- Beta Testers - QA and feedback

### Technologies
- **Python** - Core language
- **Pygame** - Game engine
- **Sonrai API** - Cloud data
- **pytest** - Testing framework

### Inspiration
- **Mega Man** - Platformer mechanics
- **The Legend of Zelda** - Top-down exploration
- **Contra** - Run-and-gun gameplay
- **Sonrai Security** - Cloud security platform

## Future Roadmap

### v2.1.0 - Visual Polish (Q1 2025)
- Enhanced raygun sprite
- Improved hacker character
- Zelda-style pause menu
- Damage numbers
- Better visual effects

### v2.2.0 - Additional Quests (Q2 2025)
- S3 bucket protection quest
- RDS database protection quest
- Lambda function protection quest
- Quest difficulty scaling

### v3.0.0 - Multiplayer (Q3 2025)
- Co-op gameplay
- Shared progress
- Competitive leaderboards
- Team challenges

### v4.0.0 - Multi-Cloud (Q4 2025)
- Azure AD support
- GCP service accounts
- Multi-cloud org view
- Unified remediation

## Links

- **Repository:** [GitHub](https://github.com/sonrai-security/zombie-blaster)
- **Documentation:** [Docs](./DOCUMENTATION_INDEX.md)
- **Issues:** [GitHub Issues](https://github.com/sonrai-security/zombie-blaster/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sonrai-security/zombie-blaster/discussions)

---

**Note:** This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles and [Semantic Versioning](https://semver.org/).
