# Sonrai Zombie Blaster

> An 8-bit video game that transforms cloud security remediation into engaging gameplay through real-time Sonrai API integration.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-177%2F191%20passing-green.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What is This?

Every AWS organization accumulates unused identities—forgotten contractor accounts, dead project roles, orphaned IAM users. Each represents a security risk. Traditional dashboards and tickets fail to motivate cleanup because the problem is invisible.

**Sonrai Zombie Blaster** makes identity cleanup tangible and engaging:
- **Visualize** unused identities as zombies in a retro 8-bit game
- **Eliminate** them through side-scrolling platformer gameplay  
- **Trigger** real Sonrai API calls to quarantine actual identities
- **Learn** security concepts through interactive quests

## Quick Start

```bash
# Setup (2 minutes)
git clone <repository-url> && cd zombie_game
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your Sonrai credentials
python3 src/main.py
```

**Controls:** WASD/Arrows to move • Space to shoot • Enter to dismiss messages

## Key Features

- **Dual-Mode Gameplay** - Top-down lobby exploration + side-scrolling platformer levels
- **Real API Integration** - Every action triggers actual Sonrai GraphQL mutations
- **Side Quests** - Service Protection (hacker race) + JIT Access (auditor challenge)
- **Performance** - 60 FPS with 500+ entities through spatial grid optimization
- **Comprehensive Testing** - 191 automated tests with 92.7% pass rate

## Documentation

<details>
<summary><b>📖 Getting Started</b></summary>

- **[Quick Start Guide](docs/guides/QUICKSTART.md)** - Get running in 60 seconds
- **[Installation Guide](docs/guides/INSTALLATION.md)** - Detailed setup instructions
- **[Configuration Guide](docs/guides/CONFIGURATION.md)** - Environment variables and settings

</details>

<details>
<summary><b>🏗️ Architecture & Design</b></summary>

- **[System Architecture](docs/architecture/ARCHITECTURE.md)** - Technical deep dive
- **[Performance Optimization](docs/architecture/PERFORMANCE.md)** - Spatial grid and scaling
- **[Design Patterns](docs/architecture/PATTERNS.md)** - State machines, factories, strategies

</details>

<details>
<summary><b>🤝 Contributing</b></summary>

- **[Contribution Guide](docs/community/CONTRIBUTING.md)** - How to contribute
- **[Development Workflow](docs/community/DEVELOPMENT.md)** - Best practices
- **[Code Standards](docs/community/STANDARDS.md)** - Style and quality guidelines

</details>

<details>
<summary><b>📚 Reference</b></summary>

- **[API Reference](docs/reference/API.md)** - Sonrai GraphQL integration
- **[Game Mechanics](docs/reference/MECHANICS.md)** - Power-ups, quests, controls
- **[Changelog](docs/reference/CHANGELOG.md)** - Version history
- **[Troubleshooting](docs/reference/TROUBLESHOOTING.md)** - Common issues

</details>

<details>
<summary><b>🎯 Project Info</b></summary>

- **[Project Overview](docs/reference/PROJECT_SUMMARY.md)** - Executive summary
- **[Technical Showcase](docs/architecture/PROJECT_SHOWCASE.md)** - Achievements and innovation
- **[Repository Structure](docs/reference/REPOSITORY_STRUCTURE.md)** - Codebase organization

</details>

## Technical Highlights

**Dual-Engine Architecture**
- Seamlessly merges top-down exploration with side-scrolling platformer
- Mode-aware physics, camera, collision, and controls

**Performance Optimization**  
- Spatial grid reduces collision detection from O(n²) to O(n)
- 18.5× speedup enables 60 FPS with 500+ entities

**Real API Integration**
- Actual Sonrai GraphQL mutations, not mocks
- Exponential backoff retry logic with graceful degradation

## Use Cases

- **Security Training** - Onboard new hires through gameplay
- **Conference Demos** - Memorable alternative to PowerPoint
- **Executive Presentations** - Visual representation of identity sprawl
- **Team Building** - Competitive cleanup challenges

## Requirements

- Python 3.11+
- Sonrai Security account with API access
- 4 GB RAM minimum
- macOS, Linux, or Windows

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **[Full Documentation](docs/README.md)** - Complete documentation hub
- **[GitHub Issues](../../issues)** - Bug reports and feature requests
- **[Discussions](../../discussions)** - Questions and ideas

---

**Built with ❤️ by Sonrai Security** • Making cloud security fun, one zombie at a time 🎮🧟‍♂️🛡️
