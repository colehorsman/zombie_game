# 🧟 Sonrai Zombie Blaster

> **Turn cloud security into an 8-bit adventure—eliminate zombie IAM identities with real API calls**

[![Category: Resurrection](https://img.shields.io/badge/Category-🧟%20Resurrection-purple)](https://kiroween.devpost.com)
[![Built with Kiro](https://img.shields.io/badge/Built%20with-Kiro%20AI-blue)](https://kiro.dev)
[![Tests](https://img.shields.io/badge/Tests-667%20passing-green)](tests/)
[![Performance](https://img.shields.io/badge/Performance-60%20FPS-orange)](docs/architecture/PERFORMANCE.md)

---

## 🎯 TL;DR for Judges

| What | Evidence |
|------|----------|
| **The Game** | 8-bit arcade game where shooting zombies triggers **real Sonrai API calls** to quarantine unused AWS identities |
| **Kiro Usage** | All 5 features: vibe coding, specs, steering, hooks, MCP |
| **Unique Factor** | **12-agent Architecture Review Board**—Kiro as PM, Architect, QA Lead, Security Lead, and 8 more |
| **Results** | Built in 11 days • 667 tests • 60 FPS • Zero P0 bugs |

**⏱️ 30-Second Demo:** Clone → `python3 src/main.py` → Type `ARCADE` → Blast zombies → Watch real API calls quarantine cloud identities

---

## 💡 The Inspiration

**Cloud security is invisible and intimidating.**

After years of watching security teams struggle to explain "unused IAM identities" to stakeholders, we asked: *What if we made it a game?*

The metaphor clicked instantly:
- 🧟 **Zombies** = Unused AWS identities (the "dead" accounts that should be eliminated)
- 🔫 **Shooting zombies** = Real API calls that quarantine actual cloud resources
- 🛡️ **Purple shields** = Protected identities (Sonrai's Cloud Permissions Firewall)
- 🎮 **Retro gaming** = Making complex topics approachable and fun

**The resurrection works on two levels:** We resurrected retro gaming AND we're eliminating "zombie" identities that should be dead.

---

## 📊 By The Numbers

```
┌─────────────────────────────────────────────────────────────┐
│  🚀 BUILT IN 11 DAYS WITH KIRO                              │
├─────────────────────────────────────────────────────────────┤
│  8,000 lines of code      │  667 automated tests           │
│  60 FPS (4× improvement)  │  15+ Sonrai API operations     │
│  15+ steering files       │  6 complete feature specs      │
│  7 agent hooks            │  43 documentation files        │
│  12-agent ARB review      │  Zero P0 bugs in production    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 How We Used Kiro (All 5 Features)

### 1. 💬 Vibe Coding: 45 Minutes Instead of 8 Hours

**The Challenge:** Build arcade mode with dynamic spawning, combo system, and batch quarantine.

**The Conversation:**
> **Me:** "I need an arcade mode where zombie spawn rates increase over time, with combo multipliers and a results screen"
>
> **Kiro:** *Generated 800 lines of production code with state machine, dynamic spawning algorithm, combo tracking, and results screen*

**The Impact:**
| Traditional | With Kiro | Savings |
|-------------|-----------|---------|
| 6-8 hours | 45 minutes | **90%** |

**Other Vibe Coding Wins:**
- JIT Access Quest with auditor patrol AI
- Photo booth with retro pixel filters
- Spatial grid collision (15 FPS → 60 FPS)

---

### 2. 📋 Specs: Zero P0 Bugs Through Structure

**The Process:**
```
requirements.md → design.md → tasks.md → implementation → tests
     ↓               ↓            ↓            ↓           ↓
  User stories   Architecture   15 steps    800 lines   105 tests
```

**6 Complete Specs:**

| Spec | What It Does | Tests |
|------|--------------|-------|
| **Arcade Mode** | 60-second timed challenge with combos | 105 |
| **Service Protection Quest** | Race hackers to protect services | 25 |
| **JIT Access Quest** | Protect admin roles from auditors | 25 |
| **Photo Booth** | Retro selfies with game stats | 20 |
| **Account Wall Defense** | Tower defense mechanics | 30 |
| **Level Progression** | Unlock system with difficulty scaling | 15 |

**The Magic:** Property-based tests caught **3 edge cases** before they became bugs.

---

### 3. 📜 Steering: From Generic to Domain Expert

**15+ Steering Files Defining Agent Roles:**

```
.kiro/steering/
├── product-manager.md      # Sprint planning, backlog prioritization
├── architecture-agent.md   # Design patterns, performance standards
├── security-agent.md       # SAST, secret detection, best practices
├── sonrai-agent.md         # API integration, brand alignment
├── documentation-agent.md  # AWS-style documentation standards
├── kiroween-submission-agent.md  # Deadline-focused prioritization
└── ... (9 more specialized agents)
```

**Before vs After:**

| Without Steering | With Steering |
|------------------|---------------|
| Generic code suggestions | Domain-specific patterns |
| Inconsistent architecture | Unified design language |
| Random documentation style | AWS-style standards |
| No performance awareness | 60 FPS requirement enforced |

---

### 4. 🔄 Hooks: Automated Quality Gates

**7 Hooks Catching Problems Before Commit:**

| Hook | Trigger | What It Does | Impact |
|------|---------|--------------|--------|
| `qa-review-src-changes` | File save | Runs relevant tests | 5s vs 30s feedback |
| `sync-arb-with-backlog` | Backlog edit | Updates quality scores | Automated tracking |
| `pre-commit-security` | Git commit | SAST + secret scan | Zero secrets leaked |
| `test-api-integration` | API changes | Validates Sonrai calls | Catches errors early |
| `generate-coverage-report` | Test run | Tracks coverage gaps | Identifies blind spots |

**Measured Result:** Test-debug cycle reduced from **30 seconds to 5 seconds**.

---

### 5. 🔌 MCP: GitHub Without Leaving the IDE

**Operations Used:**
- `create_issue` → Backlog items become GitHub issues
- `list_commits` → Track development progress
- `get_pull_request_status` → Monitor CI/CD
- `search_code` → Find implementation patterns
- `create_branch` → Feature branch management

**The Workflow:**
```
Kiro: "Create issue for arcade mode timer"
  ↓
GitHub MCP creates issue #42
  ↓
Kiro implements feature
  ↓
GitHub MCP creates PR
  ↓
Kiro monitors CI/CD status
  ↓
GitHub MCP merges after tests pass
```

**Impact:** **40% reduction** in context switching between IDE and browser.

---

## 🏛️ THE DIFFERENTIATOR: 12-Agent Architecture Review Board

**What makes this submission unique:**

Kiro conducted a comprehensive architecture review acting as **12 specialized agents**:

| Agent | Domain | Key Contribution |
|-------|--------|------------------|
| 1. Product Manager | Planning | Sprint velocity, backlog prioritization |
| 2. Architecture Lead | Design | Patterns, code organization |
| 3. QA Lead | Testing | 667 tests, coverage analysis |
| 4. Security Lead | Security | SAST, vulnerability assessment |
| 5. Operations Lead | Reliability | Deployment, monitoring |
| 6. DevEx Lead | DX | Onboarding, tooling |
| 7. UX/Design Lead | UX | Accessibility, usability |
| 8. Documentation Lead | Docs | Standards, maintenance |
| 9. DevOps Lead | CI/CD | Branch management, automation |
| 10. Standards Lead | Quality | Code consistency |
| 11. Product Vision Lead | Strategy | Roadmap, market fit |
| 12. Kiroween Lead | Deadline | Submission optimization |

**The Output:**
- **47 recommendations** across all domains
- **7.4/10 quality score** with detailed breakdown
- **4-5 sprint improvement roadmap**
- **160-200 hours** of identified improvements

**Why This Matters:** This demonstrates Kiro as a **complete development organization**, not just autocomplete.

---

## 🚧 Challenges We Conquered

### Challenge 1: Performance Bottleneck
| Problem | Solution | Result |
|---------|----------|--------|
| 15 FPS with 100 zombies | Spatial grid collision (O(n²) → O(n)) | **60 FPS with 500+ entities** |

### Challenge 2: API Rate Limiting
| Problem | Solution | Result |
|---------|----------|--------|
| Batch quarantine hitting limits | 10 calls/batch with 1s delays | **Reliable batch operations** |

### Challenge 3: Deadline Pressure
| Problem | Solution | Result |
|---------|----------|--------|
| 11 days to build production game | Kiro's spec-driven development | **Zero P0 bugs, 667 tests** |

---

## 🏆 Why We Should Win: Resurrection Category

### Perfect Thematic Fit

| Resurrection Element | Our Implementation |
|---------------------|-------------------|
| **Dead Technology** | 8-bit/16-bit retro gaming aesthetic |
| **Brought Back to Life** | Modern cloud security education |
| **Zombie Theme** | Literal zombies = "dead" unused identities |
| **Halloween Vibes** | Spooky arcade action with real consequences |

### Technical Excellence

✅ **Real API Integration** — Not mock data, actual Sonrai GraphQL calls
✅ **Production Quality** — 667 tests, 60 FPS, comprehensive error handling
✅ **Professional Architecture** — State machines, spatial grids, event systems

### Business Value

✅ **Market** — $X billion security training gap
✅ **Audience** — 9-year-olds to CISOs
✅ **Scalability** — Platform adapts to any security concept
✅ **Partnership** — Built on Sonrai Security's Cloud Permissions Firewall

---

## 🎯 Judging Criteria Alignment

### Potential Value (33%)

| Criteria | Our Evidence |
|----------|--------------|
| Solves Real Problem | Cloud security training gap—abstract concepts made tangible |
| Widely Useful | Education, corporate training, conference demos, recruitment |
| Easy to Use | Game interface vs technical documentation |
| Accessible | 9-year-olds to CISOs can understand and enjoy |

### Implementation (33%)

| Criteria | Our Evidence |
|----------|--------------|
| Extensive Kiro Usage | All 5 features: vibe, specs, steering, hooks, MCP |
| Multiple Capabilities | 12-agent ARB demonstrates sophistication |
| Clear Documentation | 43 files in .kiro directory with evidence |
| Sophisticated Integration | Real API calls, not mock data |

### Quality & Design (33%)

| Criteria | Our Evidence |
|----------|--------------|
| Polished Aesthetic | Consistent retro 8-bit visual style |
| Performance | 60 FPS with 500+ entities (4× improvement) |
| Testing | 667 automated tests, 100% pass rate |
| Documentation | AWS-style standards, evidence-based claims |

---

## 📁 Evidence Location

**Judges: Everything is in the `.kiro/` directory!**

```
.kiro/
├── steering/                    # 15+ agent role definitions
│   ├── product-manager.md       # 400+ lines
│   ├── architecture-agent.md    # 350+ lines
│   ├── security-agent.md        # 200+ lines
│   └── ... (12 more)
├── specs/                       # 6 complete feature specs
│   ├── arcade-mode/
│   ├── jit-access-quest/
│   ├── service-protection-quest/
│   └── ... (3 more)
├── hooks/                       # 7 automated workflows
└── ARCHITECTURE_REVIEW_BOARD_REPORT.md  # 12-agent review
```

---

## 🎬 Try It Yourself

```bash
# Clone and setup (2 minutes)
git clone https://github.com/colehorsman/zombie_game.git
cd zombie_game
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add Sonrai credentials if available

# Run the game
python3 src/main.py

# Run tests (667 passing)
pytest tests/ -v
```

**🎮 Cheat Codes:**
- `UNLOCK` — Access all levels
- `GOD` — Invincibility mode
- `ARCADE` — Jump to arcade mode

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| **GitHub Repository** | https://github.com/colehorsman/zombie_game |
| **Demo Video** | [YouTube - to be added] |
| **Developer** | Cole Horsman (cole.horsman@sonraisecurity.com) |
| **Company** | Sonrai Security |

---

## 🏁 Conclusion

**Sonrai Zombie Blaster proves Kiro is more than autocomplete—it's a complete development organization.**

| Role | What Kiro Did |
|------|---------------|
| **Product Manager** | 2 sprints, backlog, velocity tracking |
| **Technical Lead** | Architecture, 4× performance improvement |
| **QA Engineer** | 667 tests, 100% pass rate |
| **Security Lead** | SAST, zero secrets committed |
| **Documentation Lead** | 43 files, AWS standards |
| **+ 7 More Agents** | 12-agent ARB with 47 recommendations |

**Built in 11 days. 667 tests. 60 FPS. Zero P0 bugs.**

**This isn't autocomplete. This is AI-powered software development lifecycle management.**

---

**Built with Kiro. Powered by Sonrai. Ready for production.** 🎮🧟🚀

*#BuildWithKiro #Kiroween2025 #hookedonkiro*
