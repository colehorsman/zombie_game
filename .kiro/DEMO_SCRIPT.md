# Kiro Demo Script (5 Minutes)

> **Goal:** Show judges how Kiro managed the entire development lifecycle, not just code generation

---

## Pre-Demo Setup (Do Before Recording)

### Terminal Setup
```bash
# Open 2 terminal windows
# Terminal 1: Project root (for commands)
cd ~/zombie_game

# Terminal 2: Game window (for demo)
cd ~/zombie_game
source venv/bin/activate
```

### VS Code Setup
- Open project in VS Code
- Have `.kiro/` folder visible in sidebar
- Close all other files
- Set zoom to 150% for visibility

### Browser Setup
- GitHub repo open (for MCP demo)
- Sonrai dashboard open (for API demo)

---

## Demo Flow

### Part 1: The Hook (30 seconds)

**Script:**
> "I built a cloud security game that makes AWS identity remediation fun. But this isn't a story about building a game—it's about building WITH Kiro AI as my Product Manager, Technical Lead, and QA Engineer."

**Actions:**
1. Show game running (10 seconds of gameplay)
2. Show zombie elimination
3. Show API call in logs: "Quarantining identity..."

**Key Message:** This is production-ready, not a toy project

---

### Part 2: Kiro as Product Manager (60 seconds)

**Script:**
> "Kiro didn't just write code—it planned the entire project. Let me show you the sprint planning."

**Actions:**

1. **Show Sprint Status** (20s)
   ```bash
   cat .kiro/specs/sprint-1-status.md
   ```
   - Scroll to "Sprint Metrics" section
   - Point out: "35 story points completed, sprint goal achieved"
   - Show velocity tracking

2. **Show Backlog** (20s)
   ```bash
   cat docs/BACKLOG.md | head -50
   ```
   - Point out P0/P1/P2/P3 prioritization
   - Show story breakdown with estimates
   - Highlight "Definition of Done" checklist

3. **Show GitHub MCP Integration** (20s)
   - Open `.kiro/steering/github-mcp-priority.md`
   - Scroll to "Workflow Examples"
   - Point out: "Kiro creates issues, tracks PRs, monitors CI/CD"

**Key Message:** Kiro managed the project like a real PM

---

### Part 3: Spec-Driven Development (90 seconds)

**Script:**
> "Before writing any code, Kiro creates comprehensive specs. Here's the arcade mode feature—800 lines of code, 105 tests, built in 5 days."

**Actions:**

1. **Show Spec Folder Structure** (20s)
   ```bash
   ls -la .kiro/specs/arcade-mode/
   ```
   - Point out: requirements.md, design.md, tasks.md
   - Show completion reports

2. **Show Requirements** (20s)
   ```bash
   cat .kiro/specs/arcade-mode/requirements.md | head -40
   ```
   - Scroll to user stories
   - Point out acceptance criteria
   - Highlight success metrics

3. **Show Design** (25s)
   - Open `.kiro/specs/arcade-mode/design.md` in VS Code
   - Scroll to "Architecture" section
   - Point out: "Kiro designed the state machine, data models, performance considerations"

4. **Show Final Summary** (25s)
   ```bash
   cat .kiro/specs/arcade-mode/FINAL_SUMMARY.md | head -60
   ```
   - Point out: "105 tests, 100% passing"
   - Show metrics: "800 lines production, 1,200 lines tests"
   - Highlight: "5 days of development"

**Key Message:** Specs → Design → Implementation → Testing → Documentation

---

### Part 4: Kiro as QA Engineer (60 seconds)

**Script:**
> "Kiro generated 191 automated tests using a 3-layer testing strategy. Let me show you."

**Actions:**

1. **Show Testing Strategy** (20s)
   ```bash
   cat .kiro/steering/beta-testing-strategy.md | head -50
   ```
   - Point out: "Layer 1: Unit tests, Layer 2: Integration, Layer 3: Manual"
   - Show test pyramid diagram

2. **Show Test Files** (15s)
   ```bash
   ls -la tests/ | grep test_arcade
   ```
   - Count: "6 test files just for arcade mode"
   - Show file sizes

3. **Run Tests** (25s)
   ```bash
   pytest tests/test_arcade_mode.py -v
   ```
   - Let it run (should take ~2 seconds)
   - Point out: "32 tests passing"
   - Show test names: "test_countdown_display, test_timer_color_changes, etc."

**Key Message:** Comprehensive testing, not just happy path

---

### Part 5: Performance Optimization (60 seconds)

**Script:**
> "The game was running at 15 FPS with 100 zombies. Kiro optimized it to 60 FPS with 500+ zombies. Here's how."

**Actions:**

1. **Show Performance Doc** (30s)
   ```bash
   cat docs/architecture/PERFORMANCE.md | head -80
   ```
   - Scroll to "Spatial Grid Optimization"
   - Point out: "O(n²) → O(n) complexity"
   - Show mathematical proof
   - Highlight: "15 FPS → 60 FPS (4× improvement)"

2. **Show Code** (30s)
   - Open `src/collision.py` in VS Code
   - Scroll to `SpatialGrid` class
   - Point out: "100×100 pixel cells, O(1) lookup"
   - Show `get_nearby_entities()` method

**Key Message:** Kiro doesn't just write code—it optimizes and proves it

---

### Part 6: Agent Hooks (45 seconds)

**Script:**
> "Kiro automates best practices with agent hooks. Every time I save a file, Kiro reviews it. Every commit is scanned for secrets."

**Actions:**

1. **Show Hooks Folder** (15s)
   ```bash
   ls -la .kiro/hooks/
   ```
   - Count: "7 automated workflows"

2. **Show QA Hook** (15s)
   ```bash
   cat .kiro/hooks/qa-review-src-changes.kiro.hook
   ```
   - Point out: "Triggers on file save"
   - Show: "Reviews code for bugs and improvements"

3. **Show Pre-commit Hook** (15s)
   ```bash
   cat .pre-commit-config.yaml | head -30
   ```
   - Point out: "Gitleaks, Bandit, Semgrep"
   - Show: "Blocks secrets and vulnerabilities"

**Key Message:** Automation beats discipline

---

### Part 7: Live Game Demo (60 seconds)

**Script:**
> "Let's see it in action. This is a real game with real API integration."

**Actions:**

1. **Launch Game** (10s)
   ```bash
   python3 src/main.py
   ```
   - Wait for game to load

2. **Navigate to Sandbox** (10s)
   - Walk to "MyHealth - Sandbox" door
   - Press SPACE to enter

3. **Activate Arcade Mode** (10s)
   - Press: UP UP DOWN DOWN A B
   - Show: "Arcade Mode Activated!" message
   - Show: 3...2...1...GO! countdown

4. **Play for 30 seconds** (30s)
   - Eliminate zombies
   - Show combo counter
   - Show zombies respawning
   - Let timer run down

5. **Show Results** (10s)
   - Results screen appears
   - Point out: "23 eliminations, 8 combo, 2 power-ups"
   - Show: "Quarantine All?" option

**Key Message:** Production-ready game with real gameplay

---

### Part 8: The Impact (30 seconds)

**Script:**
> "In 6 weeks with Kiro, I built a production-ready game with 8,000 lines of code, 191 automated tests, 60 FPS performance, and real AWS integration. Kiro managed the entire development lifecycle—from sprint planning to deployment."

**Actions:**

1. **Show Kiro Submission** (15s)
   ```bash
   cat .kiro/KIROWEEN_SUBMISSION.md | head -40
   ```
   - Point out key stats:
     - "6 weeks of development"
     - "191 automated tests"
     - "9 steering files, 2,432 lines"
     - "6 feature specs"
     - "7 agent hooks"

2. **Show Final Stats** (15s)
   - Terminal: `find src -name "*.py" | xargs wc -l | tail -1`
   - Terminal: `find tests -name "*.py" | xargs wc -l | tail -1`
   - Terminal: `find .kiro -name "*.md" | wc -l`
   - Point out: "8,000 lines of code, 43 documentation files"

**Key Message:** This is what AI pair programming should be

---

## Closing (15 seconds)

**Script:**
> "Kiro isn't just an autocomplete tool—it's a full-stack development partner. Check out the full submission at .kiro/KIROWEEN_SUBMISSION.md. Thanks for watching!"

**Actions:**
- Show GitHub repo URL
- Show .kiro/ folder one more time
- End recording

---

## Recording Tips

### Technical Setup
- **Screen Resolution:** 1920×1080 (Full HD)
- **Recording Tool:** QuickTime (macOS) or OBS Studio
- **Frame Rate:** 30 FPS minimum
- **Audio:** Clear microphone, no background noise
- **Zoom:** 150% in VS Code for readability

### Presentation Tips
- **Pace:** Speak clearly, not too fast
- **Pauses:** Pause after each section for emphasis
- **Mouse:** Use mouse to highlight important text
- **Scrolling:** Scroll slowly so text is readable
- **Transitions:** Clear transitions between sections

### Common Mistakes to Avoid
- ❌ Scrolling too fast
- ❌ Text too small to read
- ❌ Mumbling or unclear speech
- ❌ Too much technical jargon
- ❌ Forgetting to show the game running

### What to Emphasize
- ✅ Kiro as Product Manager (sprint planning)
- ✅ Spec-driven development (requirements → design → tasks)
- ✅ Comprehensive testing (191 tests, 3 layers)
- ✅ Performance optimization (15 FPS → 60 FPS)
- ✅ Agent hooks (automation)
- ✅ Production-ready quality

---

## Post-Recording Checklist

- [ ] Video is 5 minutes or less
- [ ] Audio is clear and understandable
- [ ] Text is readable (not too small)
- [ ] All key points covered
- [ ] Game demo shows actual gameplay
- [ ] Stats are visible and accurate
- [ ] GitHub repo URL shown
- [ ] .kiro/ folder structure visible

---

## Upload Instructions

### YouTube
- **Title:** "Building a Cloud Security Game with Kiro AI - Full Development Lifecycle"
- **Description:** See below
- **Tags:** Kiro AI, AI pair programming, cloud security, AWS, game development, Kiroween 2024
- **Thumbnail:** Screenshot of game + "Built with Kiro AI" text

### Description Template
```
I built Sonrai Zombie Blaster, a cloud security game that makes AWS identity remediation fun, using Kiro AI as my Product Manager, Technical Lead, and QA Engineer.

In this 5-minute demo, I show:
• Sprint planning and backlog management
• Spec-driven development (requirements → design → tasks)
• 191 automated tests with 3-layer testing strategy
• Performance optimization (15 FPS → 60 FPS)
• Agent hooks for automated workflows
• Live gameplay with real API integration

Project Stats:
• 6 weeks of development with Kiro
• 8,000 lines of code (production + tests)
• 191 automated tests (92.7% pass rate)
• 60 FPS with 500+ entities
• 9 steering files (2,432 lines)
• 6 feature specs
• 7 agent hooks

Links:
• GitHub: https://github.com/colehorsman/zombie_game
• Kiro Submission: .kiro/KIROWEEN_SUBMISSION.md
• Blog Post: [link]

#KiroAI #Kiroween2024 #CloudSecurity #GameDevelopment #AI
```

---

## Alternative: 3-Minute Version

If 5 minutes is too long, use this condensed version:

1. **Hook** (20s) - Game demo + "Built with Kiro"
2. **Sprint Planning** (30s) - Show sprint status + backlog
3. **Spec-Driven Dev** (40s) - Show arcade mode spec folder
4. **Testing** (30s) - Run tests, show 191 passing
5. **Performance** (30s) - Show 15 FPS → 60 FPS proof
6. **Impact** (30s) - Stats + closing

Total: 3 minutes

---

*This script provides a clear, structured demo that showcases Kiro's full capabilities beyond code generation. Practice once before recording to ensure smooth delivery.*
