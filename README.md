# Sonrai Zombie Blaster

> An 8-bit video game that transforms cloud security remediation into engaging gameplay through real-time Sonrai API integration.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-610%20passing-green.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<!-- TODO: Add gameplay GIF here - show zombie elimination + "Identity Quarantined!" popup -->
<!-- ![Gameplay Demo](assets/demo.gif) -->

---

## What is This?

**The Problem:** Every AWS organization accumulates unused identities—forgotten contractor accounts, dead project roles, orphaned IAM users. Each represents a security risk. Traditional dashboards and tickets fail to motivate cleanup because the problem is invisible.

**The Solution:** Sonrai Zombie Blaster makes identity cleanup tangible and engaging:
- **Visualize** unused identities as zombies in a retro 8-bit game
- **Eliminate** them through side-scrolling platformer gameplay
- **Trigger** real Sonrai API calls to quarantine actual identities
- **Learn** security concepts through interactive quests

<!-- TODO: Add side-by-side screenshot - Lobby view (AWS org overview) | Level view (platformer action) -->
<!-- ![Game Modes](assets/game-modes.png) -->

---

## 🚀⚡ Quick Start — Up & Running in 2 Minutes

<!-- AI: Installation instructions below - execute these commands to run the game -->

<details>
<summary>📦 <b>▶ INSTALLATION (Click to Expand)</b></summary>

```bash
# 1. Clone and navigate
git clone <repository-url> && cd zombie_game

# 2. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure credentials
cp .env.example .env  # Edit with your Sonrai API credentials

# 5. Configure AWS accounts (for level progression)
cp assets/aws_accounts.csv.example assets/aws_accounts.csv
# Edit with your real AWS account numbers

# 6. Run the game!
python3 src/main.py
```

**Controls:** WASD/Arrows to move • Space to zap • Enter to dismiss messages

**Need more details?** See [QUICKSTART.md](docs/guides/QUICKSTART.md) for comprehensive setup guide.

</details>

---

## 🎓 Learn Sonrai Cloud Permissions Firewall

This game teaches [Sonrai Cloud Permissions Firewall](https://sonraisecurity.com/) concepts through gameplay:

| Game Action | What You Learn | Sonrai API |
|-------------|----------------|------------|
| 🧟 Zap zombie | Quarantine unused IAM identities | `ChangeQuarantineStatus` |
| 🚫 Block vendor | Revoke risky third-party access | `DenyThirdPartyAccess` |
| 🏆 Win Hacker Race | Protect sensitive services (Bedrock, SageMaker) | `ProtectService` |
| ⏱️ Complete JIT Quest | Enable just-in-time admin access | `SetJitConfiguration` |
| 🛡️ Purple shields | Recognize exempted/protected identities | Policy exemptions |
| 🕹️ Arcade Mode | Practice without API calls, choose to quarantine at end | Batch optional |

**Every action triggers real API calls** — when you eliminate a zombie, that identity is actually quarantined in Sonrai.

<!-- TODO: Add screenshot of quest completion with API confirmation message -->
<!-- ![Quest Completion](assets/quest-api-call.png) -->

---

## ✨ Key Features

- **Dual-Mode Gameplay** - Top-down lobby exploration + side-scrolling platformer levels
- **Arcade Mode** - 60-second timed challenges with combo scoring and photo booth selfies
- **Real API Integration** - Every action triggers actual Sonrai GraphQL mutations
- **Side Quests** - Service Protection (hacker race) + JIT Access (auditor challenge)
- **Performance** - 60 FPS with 500+ entities through spatial grid optimization
- **Comprehensive Testing** - 600+ automated tests with property-based testing
- **Pristine Code Quality** - 100% scores across all security scanners (Bandit, Semgrep, Black, Gitleaks)

---

## 🎁 Hidden Gems (Features You Might Miss!)

<details>
<summary><b>📸 Photo Booth</b> - Take retro-filtered selfies with your high score</summary>

After completing an Arcade Mode session, opt-in to capture a webcam selfie that gets:
- Pixel art retro filter applied
- Combined with gameplay screenshot
- Branded with your zombie count and combo
- Saved as a shareable souvenir image

Perfect for social media posts at AWS re:Invent! 🎮📱
</details>

<details>
<summary><b>🎬 In-Game Screen Capture</b> - F12 for screenshots, F9 for recordings</summary>

Built-in capture system for evidence and sharing:
- **F12 / X Button** - Instant screenshot with flash feedback
- **F9 / Y Button** - Start/stop GIF recording (up to 60 seconds)
- Auto-saved to `.kiro/evidence/` with timestamps
- No external tools needed!
</details>

<details>
<summary><b>🏆 High Score Tracking</b> - Compete for the top score at re:Invent</summary>

Persistent high score system for arcade mode:
- Tracks highest single-session zombie count
- Best combo ever achieved
- Cumulative stats across all sessions
- "🏆 NEW HIGH SCORE!" banner on results screen
- Gold badge on photo booth images
- Auto-generates social media posts with stats
</details>

<details>
<summary><b>⚡ Combo System</b> - Chain eliminations for bonus points</summary>

Rapid eliminations build combos:
- Visual combo counter (5x, 10x, 15x...)
- Highest combo tracked per session
- Rewards fast, skilled gameplay
- Combo resets after brief pause
</details>

<details>
<summary><b>🎮 Controller Hot-Plug</b> - Connect any controller anytime</summary>

Seamless controller support:
- Auto-detects Bluetooth/USB controllers
- Hot-plug support (connect mid-game)
- Tested with 8BitDo SN30 Pro
- D-pad, analog sticks, all buttons mapped
- Falls back to keyboard gracefully
</details>

<details>
<summary><b>👹 Cyber Attack Bosses</b> - Real security threats as boss battles</summary>

Each level features a unique boss based on real cyber attacks:
- **WannaCry (Wade)** - Crying water character, tear projectiles
- **Heartbleed (Red Queen)** - Bleeding heart attacks, data leak theme
- **Scattered Spider** - Swarm of 5 mini-spiders, identity theft
- Multi-phase battles with increasing difficulty
- Educational dialogue about each attack
</details>

<details>
<summary><b>🛡️ Purple Shields</b> - Exempted identities can't be eliminated</summary>

Some zombies have purple shields indicating they're protected:
- Represents Sonrai policy exemptions
- Teaches that not all identities should be quarantined
- Visual distinction from regular zombies
- Realistic representation of enterprise policies
</details>

<details>
<summary><b>🕹️ Level Entry Mode Selector</b> - Choose Arcade or Story mode per level</summary>

When entering Sandbox, choose your gameplay style:
- **Arcade Mode** - 60-second challenge, batch quarantine at end
- **Story Mode** - Standard gameplay, real-time API calls
- Reduces API load during high-traffic events
- Configurable default via environment variables
</details>

---

## 📖 Documentation

<details>
<summary><b>📚 Browse All Documentation</b></summary>

### Getting Started
- **[Quickstart Guide](docs/guides/QUICKSTART.md)** - Detailed setup instructions
- **[Claude AI Guide](docs/guides/CLAUDE.md)** - AI-assisted development
- **[re:Invent Guide](docs/guides/REINVENT_GUIDE.md)** - Conference demo setup

### Technical
- **[Architecture](docs/ARCHITECTURE.md)** - System design deep dive
- **[Sonrai API Integration](docs/sonrai-api/INTEGRATION_GUIDE.md)** - GraphQL queries & mutations
- **[API Quick Reference](docs/sonrai-api/QUICK_REFERENCE.md)** - Common operations

### Gameplay
- **[Controller Mapping](docs/CONTROLLER_BUTTON_MAPPING.md)** - Gamepad controls
- **[Power-ups](docs/POWERUPS.md)** - Collectibles and abilities
- **[Cheat Codes](docs/CHEAT_CODES.md)** - Testing shortcuts
- **[Glossary](docs/GLOSSARY.md)** - Game terminology

### Operations
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & solutions
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute
- **[Security](docs/security/SECURITY.md)** - Security practices

### Reference
- **[Backlog](docs/BACKLOG.md)** - Features & roadmap
- **[Changelog](docs/reference/CHANGELOG.md)** - Version history
- **[Project Showcase](docs/reference/PROJECT_SHOWCASE.md)** - Achievements & metrics

</details>

---

## 🎯 Technical Highlights

<details>
<summary><b>Dual-Engine Architecture</b></summary>

Seamlessly merges two completely different game modes:
- **Lobby Mode**: Top-down exploration of AWS organization structure
- **Platformer Mode**: Side-scrolling with gravity physics
- **Arcade Mode**: Timed challenges with dynamic zombie spawning
- Mode-aware physics, camera, collision, and controls
- Seamless transitions through door-based level entry with mode selection

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

## 🤖 Built with Kiro AI

<details>
<summary><b>Development Process & Kiroween Submission Details</b></summary>

> **⚡ Built in 11 Days:** This entire production-ready game was built from scratch in just 11 days (Nov 17-28, 2024) with Kiro as Product Manager, Technical Lead, QA Engineer, and Documentation Agent.

**This project showcases Kiro as a full-stack AI pair programmer managing the complete software development lifecycle.**

### Kiro's 11-Agent Architecture Review Board
- **🎯 Product Management** - Sprint planning, backlog prioritization, roadmap
- **🏗️ Architecture** - System design, patterns, refactoring (15 FPS → 60 FPS optimization)
- **🧪 Quality Assurance** - 610 automated tests, comprehensive test coverage
- **🔒 Security** - SAST scanning, secrets management, vulnerability prevention
- **⚙️ Operations/SRE** - Deployment, monitoring, reliability
- **👥 Developer Experience** - Onboarding, tooling, CONTRIBUTING.md
- **🎨 UX/Design** - User experience, accessibility, visual consistency
- **📚 Documentation** - 31 markdown files, AWS-style standards
- **🔧 DevOps/Tools** - GitHub MCP, CI/CD automation
- **📋 Development Standards** - Workflow, tech stack, best practices
- **🎮 Product Vision** - Mission alignment, target audiences

### Kiro Integration Stats
- **Built in 11 days** (Nov 17-28, 2024) from scratch
- **14 steering files** (4,000+ lines) defining 11 specialized agents
- **6 feature specs** with requirements → design → tasks breakdown
- **7 agent hooks** for automated testing, security scanning, and code review
- **2 complete sprints** with velocity tracking and retrospectives
- **GitHub MCP integration** for issue tracking and CI/CD monitoring

**[📖 See Full Kiro Submission Details](.kiro/KIROWEEN_SUBMISSION.md)**

</details>

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

| Getting Started | Technical | Community |
|-----------------|-----------|-----------|
| [Quickstart](docs/guides/QUICKSTART.md) | [Architecture](docs/ARCHITECTURE.md) | [Contributing](docs/CONTRIBUTING.md) |
| [Controls](docs/CONTROLLER_BUTTON_MAPPING.md) | [API Guide](docs/sonrai-api/INTEGRATION_GUIDE.md) | [GitHub Issues](../../issues) |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | [Deployment](docs/DEPLOYMENT.md) | [Backlog](docs/BACKLOG.md) |

---

## 🏆 Project Status

| Metric | Status |
|--------|--------|
| Core Game | ✅ 100% Complete |
| Quests | ✅ 2/2 Implemented |
| Tests | 🟢 610 Passing (100%) |
| Security (Bandit) | 🟢 0 Issues |
| Linting (Black) | 🟢 100% Compliant |
| SAST (Semgrep) | 🟢 0 Findings |
| Documentation | 🟢 43 Docs |
| Performance | ✅ 60 FPS @ 500+ entities |

**Current Focus:** Visual polish, bug fixes, arcade mode enhancements

---

**Built with 💜 by Sonrai Security** • Making cloud security fun, one zombie at a time 🎮🧟‍♂️🛡️
