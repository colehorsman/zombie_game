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

---

## 🚀 Quick Start

<details>
<summary><b>60-Second Setup</b></summary>

```bash
# 1. Clone and navigate
git clone <repository-url> && cd zombie_game

# 2. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env  # Edit with your Sonrai API credentials

# 5. Run the game!
python3 src/main.py
```

**Controls:** WASD/Arrows to move • Space to shoot • Enter to dismiss messages

**Need more details?** See [QUICKSTART.md](docs/guides/QUICKSTART.md) for comprehensive setup guide.

</details>

---

## 🤖 Built with Kiro AI

> **⚡ Built in 11 Days:** This entire production-ready game was built from scratch in just 11 days (Nov 17-28, 2024) with Kiro as Product Manager, Technical Lead, QA Engineer, and Documentation Agent.

**This project showcases Kiro as a full-stack AI pair programmer managing the complete software development lifecycle.**

### Kiro's Roles
- **🎯 Product Manager** - Sprint planning, backlog prioritization, velocity tracking
- **🏗️ Technical Lead** - Architecture decisions, performance optimization (15 FPS → 60 FPS)
- **🧪 QA Engineer** - 191 automated tests, 3-layer testing strategy, 92.7% pass rate
- **📚 Documentation Agent** - 43 markdown files, AWS-style standards, evidence-based claims

### Kiro Integration Stats
- **Built in 11 days** (Nov 17-28, 2024) from scratch
- **9 steering files** (2,432 lines) defining agent roles and workflows
- **6 feature specs** with requirements → design → tasks breakdown
- **7 agent hooks** for automated testing, security scanning, and code review
- **2 complete sprints** with velocity tracking and retrospectives
- **GitHub MCP integration** for issue tracking and CI/CD monitoring

**[📖 See Full Kiro Submission Details](.kiro/KIROWEEN_SUBMISSION.md)**

---

## ✨ Key Features

- **Dual-Mode Gameplay** - Top-down lobby exploration + side-scrolling platformer levels
- **Real API Integration** - Every action triggers actual Sonrai GraphQL mutations
- **Side Quests** - Service Protection (hacker race) + JIT Access (auditor challenge)
- **Performance** - 60 FPS with 500+ entities through spatial grid optimization
- **Comprehensive Testing** - 191 automated tests with 92.7% pass rate

---

## 📖 Documentation

<details>
<summary><b>� Gettinng Started</b></summary>

### Quick Setup
- **[60-Second Quickstart](docs/guides/QUICKSTART.md)** - Get running immediately
- **[Configuration Guide](docs/guides/CONFIGURATION.md)** - Environment variables and settings

### For Developers
- **[Claude AI Guide](docs/guides/CLAUDE.md)** - Working with Claude Code on this project
- **[Development Workflow](.kiro/steering/development-workflow.md)** - Best practices and patterns

</details>

<details>
<summary><b>🏗️ Architecture & Technical Deep Dive</b></summary>

### System Design
- **[System Architecture](docs/architecture/ARCHITECTURE.md)** - Technical deep dive
- **[Performance Optimization](docs/architecture/PERFORMANCE.md)** - Spatial grid and scaling
- **[Design Patterns](docs/architecture/PATTERNS.md)** - State machines, factories, strategies

### Technical Showcase
- **[Project Showcase](docs/architecture/PROJECT_SHOWCASE.md)** - Achievements and innovation
- **[Hackathon Submission](docs/reference/HACKATHON_SUBMISSION.md)** - Complete technical narrative

</details>

<details>
<summary><b>🐛 Bug Reports & Fixes</b></summary>

### Recent Fixes
- **[Collision Bug Fix](docs/bug-reports/BUG_FIX_COLLISION_AFTER_QUEST.md)** - Spatial grid recreation fix
- **[Bug Reports](docs/bug-reports/)** - All documented bugs and resolutions

### Known Issues
See [BACKLOG.md](docs/BACKLOG.md) for current bugs and their status.

</details>

<details>
<summary><b>🔒 Security</b></summary>

### Security Scanning
- **[Security Documentation](docs/reference/SECURITY.md)** - Comprehensive security scanning guide
- **[Public Release Checklist](docs/reference/PUBLIC_RELEASE_CHECKLIST.md)** - Security verification

### Security Tools
- SAST (Bandit, Semgrep)
- Dependency scanning (Safety, pip-audit)
- Secret detection (Gitleaks)
- CI/CD integration

</details>

<details>
<summary><b>📋 Product Backlog</b></summary>

### Current Sprint
- **[Product Backlog](docs/BACKLOG.md)** - Features, bugs, and roadmap
- **[Implementation Status](.kiro/specs/arcade-mode/IMPLEMENTATION_STATUS.md)** - Arcade mode progress

### Priorities
- 🔴 P0: Critical (blocking issues)
- 🟠 P1: High (next release)
- 🟡 P2: Medium (schedule when possible)
- 🟢 P3: Low (future consideration)

</details>

<details>
<summary><b>🤝 Contributing</b></summary>

### How to Contribute
- **[Contribution Guide](docs/community/CONTRIBUTING.md)** - How to contribute
- **[Development Workflow](docs/community/DEVELOPMENT.md)** - Best practices
- **[Code Standards](docs/community/STANDARDS.md)** - Style and quality guidelines

### Testing
- **[Beta Testing Strategy](.kiro/steering/beta-testing-strategy.md)** - Automated testing approach
- **[QA Reports](docs/qa-reports/)** - Quality assurance documentation

</details>

<details>
<summary><b>📚 API Reference</b></summary>

### Sonrai Integration
- **[API Integration Guide](docs/sonrai-api/INTEGRATION_GUIDE.md)** - Complete integration docs
- **[Quick Reference](docs/sonrai-api/QUICK_REFERENCE.md)** - Common queries and mutations
- **[Query Examples](docs/sonrai-api/queries/)** - GraphQL query library

### Game Mechanics
- **[Game Mechanics](docs/reference/MECHANICS.md)** - Power-ups, quests, controls
- **[Cheat Codes](docs/CHEAT_CODES.md)** - Testing shortcuts

</details>

<details>
<summary><b>🎯 Project Information</b></summary>

### Overview
- **[Project Summary](docs/reference/PROJECT_SUMMARY.md)** - Executive summary
- **[Repository Structure](docs/reference/REPOSITORY_STRUCTURE.md)** - Codebase organization
- **[Changelog](docs/reference/CHANGELOG.md)** - Version history

### Documentation Hub
- **[Complete Documentation](docs/README.md)** - Central documentation hub
- **[Documentation Standards](docs/DOCUMENTATION_STANDARDS.md)** - Writing guidelines

</details>

<details>
<summary><b>🔧 Troubleshooting</b></summary>

### Common Issues
- **[Troubleshooting Guide](docs/reference/TROUBLESHOOTING.md)** - Solutions to common problems
- **[QA Reports](docs/qa-reports/)** - Test results and known issues

### Support
- [GitHub Issues](../../issues) - Report bugs
- [Discussions](../../discussions) - Ask questions

</details>

---

## 🎯 Technical Highlights

<details>
<summary><b>Dual-Engine Architecture</b></summary>

Seamlessly merges two completely different game modes:
- **Lobby Mode**: Top-down exploration with fog-of-war
- **Platformer Mode**: Side-scrolling with gravity physics
- Mode-aware physics, camera, collision, and controls
- Seamless transitions through door-based level entry

</details>

<details>
<summary><b>Performance Optimization</b></summary>

**Spatial Grid Collision Detection**
- Reduces complexity from O(n²) to O(n)
- 18.5× speedup enables 60 FPS with 500+ entities
- Only checks nearby cells instead of all entities

**Mathematical Impact:**
```
Naive: n × m checks (500 × 10 = 5,000 per frame)
Spatial Grid: n × 9k checks (10 × 9 × 3 = 270 per frame)
Speedup: 5,000 / 270 ≈ 18.5×
```

</details>

<details>
<summary><b>Real API Integration</b></summary>

Every game action triggers actual Sonrai GraphQL mutations:
- **Quarantine Identity** - Eliminate zombie → `ChangeQuarantineStatus`
- **Block Third Party** - Neutralize entity → `DenyThirdPartyAccess`
- **Protect Service** - Win quest → `ProtectService`
- **Apply JIT** - Secure admin role → `SetJitConfiguration`

**Reliability Features:**
- Exponential backoff retry logic
- Graceful degradation on API errors
- Real CloudHierarchy scopes (never constructed manually)

</details>

---

## 💼 Use Cases

- **Security Training** - Onboard new hires through interactive gameplay
- **Conference Demos** - Memorable alternative to PowerPoint at AWS re:Invent
- **Executive Presentations** - Visual representation of identity sprawl
- **Team Building** - Competitive cleanup challenges with real impact
- **Compliance Audits** - Demonstrate proactive identity management

---

## 📋 Requirements

**System Requirements:**
- Python 3.11+
- 4 GB RAM minimum
- macOS, Linux, or Windows

**Sonrai Requirements:**
- Sonrai Security account with API access
- API token with `read:data` and `read:platform` scopes
- AWS organization with unused identities

**Optional:**
- Bluetooth/wired game controller (8BitDo tested)
- Fullscreen display for best experience

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

This project is open source and available for:
- Educational purposes
- Security training
- Conference demonstrations
- Community contributions

---

## 🔗 Quick Links

### Documentation
- **[Complete Documentation Hub](docs/README.md)** - Central navigation
- **[60-Second Quickstart](docs/guides/QUICKSTART.md)** - Get running immediately
- **[Hackathon Submission](docs/reference/HACKATHON_SUBMISSION.md)** - Full technical narrative

### Development
- **[Product Backlog](docs/BACKLOG.md)** - Features and roadmap
- **[Claude AI Guide](docs/guides/CLAUDE.md)** - AI-assisted development
- **[Security Scanning](docs/reference/SECURITY.md)** - Security tools and processes

### Community
- **[GitHub Issues](../../issues)** - Bug reports and feature requests
- **[Discussions](../../discussions)** - Questions and ideas
- **[Contributing Guide](docs/community/CONTRIBUTING.md)** - How to contribute

---

## 🏆 Project Status

| Metric | Status |
|--------|--------|
| Core Game | ✅ 100% Complete |
| Quests | ✅ 2/2 Implemented |
| Tests | 🟢 177/191 Passing (92.7%) |
| Documentation | 🟢 Comprehensive |
| Performance | ✅ 60 FPS Target Met |

**Current Focus:** Visual polish, bug fixes, arcade mode enhancements

---

**Built with ❤️ by Sonrai Security** • Making cloud security fun, one zombie at a time 🎮🧟‍♂️🛡️
