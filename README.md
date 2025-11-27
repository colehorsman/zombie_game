# Sonrai Zombie Blaster

**An 8-bit cloud identity cleanup game powered by the Sonrai Cloud Permissions Firewall**

What if least privilege wasn't a spreadsheet or a backlog item…
but a zombie shooter?

**Sonrai Zombie Blaster** is a retro 8-bit style game that connects to a *real* Sonrai Security tenant and uses the **Cloud Permissions Firewall** to clean up your cloud:

- Every **zombie** = a real unused AWS identity from your Sonrai org
- Every **shot** = a real quarantine request via GraphQL
- Every **side quest** = real service protections and Just-In-Time (JIT) access flows

As far as we're aware, this is one of the **first 8-bit cybersecurity video games that drives live cloud remediation through real APIs**, not mocks or fake data.

---

## TL;DR

```bash
# Clone, setup, play
git clone <repository-url> && cd zombie_game
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your Sonrai API credentials
python3 src/main.py
```

**Controls:** WASD/Arrows to move, Space to shoot, Enter to dismiss messages, walk into doors to enter levels.

---

## The Story: Your Cloud Is Full of Zombies

Your AWS org has been running for years. Projects shipped, projects died, contractors left, third parties came and went.

The result?

- **Unused IAM users and roles** lingering with real permissions
- **Third-party access** that nobody remembers approving
- **Privileged services** (like Bedrock) wide open to abuse
- **Standing admin access** in production that auditors hate

In Sonrai, those are all surfaced by the **Cloud Permissions Firewall** — which can quarantine identities, block third parties, lock down services/regions, and enforce JIT access with automated ChatOps approvals.

Zombie Blaster turns that control plane into a playable map.

---

<details>
<summary><h2>Installation Runbook</h2></summary>

### Prerequisites

- **OS**: macOS, Linux, or Windows
- **Python**: 3.11 or higher
- **Sonrai Security**: Active account with API access

### Step 1: Get the Code

```bash
# Clone from git
git clone <repository-url>
cd zombie_game

# Or extract from zip
unzip zombie_game.zip
cd zombie_game
```

### Step 2: Verify Python Version

```bash
python3 --version  # Should be 3.11+
```

**Need Python 3.11+?**
- macOS: `brew install python@3.11`
- Linux: `sudo apt install python3.11`
- Windows: [python.org/downloads](https://www.python.org/downloads/)

### Step 3: Create Virtual Environment

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

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Sonrai API

1. Copy the example config:
   ```bash
   cp .env.example .env
   ```

2. Get your Sonrai credentials:
   - Log into Sonrai Security
   - Navigate to **Settings** → **API Tokens**
   - Create a token with `read:data` and `read:platform` scopes

3. Edit `.env` with your credentials:
   ```env
   SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
   SONRAI_ORG_ID=your_org_id_here
   SONRAI_API_TOKEN=your_api_token_here
   ```

### Step 6: Launch the Game

```bash
python3 src/main.py
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `SONRAI_API_TOKEN is required` | Check `.env` file exists and has valid credentials |
| `Failed to authenticate` | Verify token hasn't expired, check org ID |
| `ModuleNotFoundError: pygame` | Activate venv: `source venv/bin/activate` |
| Black screen | Update pygame: `pip install --upgrade pygame` |
| No zombies found | Check AWS account has unused identities |

</details>

---

<details>
<summary><h2>How the Game Maps to Real Cloud Controls</h2></summary>

Under the hood, this isn't a toy simulation:

1. The game connects to your **Sonrai tenant** using GraphQL.
2. It pulls:
   - **Unused identities** → become zombies on the map
   - **Third-party access** → become patrolling "suit" characters
   - **Exempted identities** → become protected entities with **purple shields**
3. When you:
   - **Eliminate a zombie** (3 hits) → the game calls a **Quarantine Identity** mutation
   - **Neutralize a third-party** (10 hits) → the game calls **Block Third Party**
   - **Win a Service Protection Quest** → the game calls a service-protection mutation to lock down a real AWS service via the Permissions Firewall
4. The game strictly uses **real CloudHierarchy scopes** and enforces never constructing scopes by hand (matching Sonrai best practices).

In other words: **your inputs are fun and 8-bit; the outputs are real policy changes in your cloud.**

> **Production Warning**
> This game can trigger real quarantine and protection actions. Use a **sandbox / lab org** or heavily scoped test environment, not your primary production org.

### How This Reflects the Cloud Permissions Firewall

Sonrai's **Cloud Permissions Firewall** provides:

- **Quarantine of unused identities** (our zombies) with one-click global policies
- **Blocking of third-party access** at org / OU / account
- **Disabling unused services & regions** while allowing reactivation via ChatOps
- **Just-In-Time Access** for high-risk permissions with request/approval flows
- **Privilege-on-Demand** and AI-summarized session activity

Zombie Blaster visualizes that model as:

| Game Element | Cloud Control |
|--------------|---------------|
| Zombies | Unused identities waiting to be quarantined |
| Third-party suits | External orgs that can be blocked |
| Bedrock service node | Service protections (most sensitive permissions) |
| Auditor / Admin roles | JIT and audit remediation of standing access |
| Purple shields | Exemptions, Sonrai system identities, JIT-protected roles |

If you play this from start to finish against a real Sonrai org, you've effectively run a **gamified least-privilege enforcement pass** across unused identities, third-party access, and key services.

</details>

---

<details>
<summary><h2>Core Gameplay</h2></summary>

### Lobby Mode – Cloud Org Map (Top-Down)

The lobby is your **cloud org hallway**:

- Each **door** represents an AWS account (sandbox, dev, stage, prod, org, etc.).
- **Fog-of-war** hides what's down the hall until you explore.
- **Third-party entities** in suits patrol near production doors.
- Purple-shielded characters represent Sonrai systems and exempted identities that **must never be quarantined**.

Walk into a door to dive into that account's level.

### Platformer Mode – Account Levels (Side-Scrolling)

Inside each account you get a **Mario-style platformer**:

- Level width scales with zombie count (hundreds of unused identities = huge maps).
- Zombies spawn across floating platforms with simple physics.
- Power-ups (Star Power, Lambda Speed, etc.) give you bursts of clearance speed.

**Win condition for a level:**

1. Eliminate (quarantine) every zombie in that account
2. Navigate back to the entrance platform
3. Return to the lobby with that account now "clean"

Behind the scenes, each zombie kill corresponds to a **real quarantine mutation** against the identity it represents.

### Controls

**Lobby (Top-Down):**
- Arrow keys / WASD → Move
- Space → Fire ray gun
- Walk into doors → Enter account levels

**Platformer:**
- Left/Right (Arrow keys / A,D) → Move
- Up / W → Jump
- Space → Fire
- Return to entrance platform → Exit level

**Universal:**
- Enter → Dismiss messages (including quest prompts)
- ESC → Pause / Quit
- F / F11 / CMD+F → Toggle fullscreen
- Hidden cheat codes (`UNLOCK` / `SKIP`) for testing

</details>

---

<details>
<summary><h2>Side Quests</h2></summary>

The main loop is "clean up unused identities." The side quests bring in **service protection** and **JIT access / audit**.

### 1. Hacker Race – Service Protection Quest (Bedrock)

The **Service Protection Quest** is a timed race against a hacker AI to protect a critical service (for example, Amazon Bedrock) with the Permissions Firewall.

**What happens:**

1. In Sandbox (Level 1) and Production (Level 6), when you cross a trigger point in the level, a warning pops up:
   > "You have 60 SECONDS to protect the Bedrock service before a hacker deletes guardrails allowing prompt injection!"
2. You hit **ENTER** to accept the quest.
3. A **black-hat hacker** drops from the sky near the Bedrock service node and starts sprinting toward it.
4. A big countdown timer appears (color-coded: green → orange → red as time drops).
5. Your job: **reach the service node before the hacker**. Get within range and the game will:
   - Call a **ProtectService** mutation via `SonraiAPIClient`
   - Mark the service as protected
   - Update its sprite to show a green shield

**Win:**
- Service icon shows a **green shield**
- Quest status → COMPLETED
- You continue the level with the Bedrock service now protected by the Permissions Firewall and reflected in Sonrai

**Lose:**
- Hacker reaches the service first or the timer expires
- Service is compromised
- You get a **GAME OVER** and must replay the level

This models Sonrai's real-world **service protection** capability — locking down privileged permissions on specific services (like Bedrock, S3, RDS, etc.) and relying on exemptions/JIT for legitimate access.

---

### 2. Auditor Challenge – JIT Access Quest

The **JIT Access Quest** brings the internal audit and JIT story into the game.

**Cloud problem it represents:**
- Standing admin access in production
- Audit findings about excessive privileges and lack of approvals
- Need to move to **Just-In-Time (JIT)** access with proper evidence and workflows

**How it works in-game:**
- Triggered in **Production Data** and **Org** levels when unprotected admin roles exist.
- An **Auditor character** (clipboard, suit, serious expression) spawns and patrols the level watching you.
- **Admin Role characters** (crown / gold motif) represent high-privilege permission sets that should be JIT-protected.
- Unprotected roles glow with warning icons; JIT-enrolled ones show **purple shields** (just like exempted entities and Sonrai-managed identities).

**Quest flow:**

1. The game checks Sonrai via API for admin permission sets and their current JIT status.
2. If there are **unprotected admin sets**:
   - Auditor spawns
   - Timer starts (for example, 180 seconds)
   - Admin role characters appear on platforms
3. You navigate to each admin role and interact (e.g., within range + action key):
   - The game calls Sonrai APIs to **apply JIT protection** to that permission set
   - The character gains a purple shield and becomes "compliant"
4. **Success:** all admin roles are protected before the timer expires →
   - Auditor shows an approval emote
   - You get an "Audit Deficiency Prevented!" message
   - Quest is marked complete
5. **Failure:** timer runs out with unprotected roles →
   - Auditor shows a failure emote
   - You get an "Audit Failed!" message
   - You must replay the level

Conceptually, this quest mirrors Sonrai's **JIT Access** feature: converting standing privileges into time-bound access with approvals, session tracking, and audit-friendly evidence, typically fronted by ChatOps workflows in Slack/Teams.

</details>

---

<details>
<summary><h2>Architecture & Technical Details</h2></summary>

### Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Game Engine | Pygame 2.5+ (SDL bindings) |
| API | Sonrai GraphQL via `requests` |
| Config | python-dotenv |
| Persistence | JSON-based save system |

**Total Codebase**: ~8,380 lines of Python across 21 modules

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Main Loop                          │
│                   (src/main.py)                         │
│  • Event handling • Delta time (60 FPS) • Scaling       │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌─────────────┐         ┌──────────────┐
│ Game Engine │◄────────│  Renderer    │
│  (Logic)    │         │  (Graphics)  │
└──────┬──────┘         └──────────────┘
       │
       ├─► GameMap (lobby/platformer generation)
       ├─► LevelManager (progression & unlocking)
       ├─► Player (controls & physics)
       ├─► Zombie/ThirdParty/Boss (entity behavior)
       ├─► Collision (spatial grid optimization)
       ├─► SonraiAPIClient (GraphQL integration)
       └─► SaveManager (persistence)
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `src/main.py` | Entry point, config, window scaling |
| `src/game_engine.py` | Lobby + platformer engine, quest orchestration |
| `src/sonrai_client.py` | GraphQL client (identities, third parties, exemptions, protect service, JIT) |
| `src/player.py` | Mega Man-style 8-bit character |
| `src/zombie.py` | Zombie entity AI and rendering |
| `src/third_party.py` | Third-party patrol entities |
| `src/collision.py` | Spatial grid collision (O(n) for 500+ entities) |
| `src/service_protection_quest.py` | Hacker race quest logic |
| `src/jit_access_quest.py` | Auditor/JIT quest logic |

### Dual-Engine System

The game features a unique **dual-mode architecture**:

**Lobby Engine (Top-Down)**
- Camera-based exploration with fog-of-war
- Tile-based collision (16x16 pixel tiles)
- Zombie distribution across AWS account rooms
- Door-based level transitions

**Level Engine (Platformer)**
- Mario-style physics with gravity
- Randomly generated floating platforms
- Dynamic level width (512 zombies = 27,200px wide)
- Power-ups on ~15% of platforms

### Performance

- **Tested with 500+ zombies** at 60 FPS
- **Spatial grid collision** keeps checks efficient (O(n) vs O(n²))
- **Memory**: ~50-100 MB typical
- **API latency**: Initial fetch ~2-5s, mutations <500ms

### Project Structure

```
zombie_game/
├── src/                     # Source code (~8,380 lines)
│   ├── main.py             # Entry point
│   ├── game_engine.py      # Core game logic
│   ├── sonrai_client.py    # API integration
│   ├── player.py           # Player character
│   ├── zombie.py           # Zombie entities
│   ├── collision.py        # Spatial grid collision
│   └── ...                 # Other modules
├── tests/                   # Test suite
├── docs/                    # Documentation
│   ├── sonrai-api/         # API integration docs
│   ├── CHEAT_CODES.md      # Admin cheats
│   └── POWERUPS.md         # Power-up reference
├── assets/                  # Game assets
├── .env.example            # Config template
├── requirements.txt        # Dependencies
├── QUICKSTART.md           # Quick start guide
└── BACKLOG.md              # Feature backlog
```

### Controller Support

- **Keyboard**: Arrow keys, WASD, Space, Enter, ESC
- **Gamepad**: Xbox, PlayStation, Nintendo Switch Pro
- D-Pad and analog stick support
- Button mapping: A/Cross = Jump, X/Square = Shoot

### Environment Variables

```env
# Required - Sonrai API
SONRAI_API_URL=https://YOUR_ORG-graphql-server.sonraisecurity.com/graphql
SONRAI_ORG_ID=your_org_id_here
SONRAI_API_TOKEN=your_api_token_here

# Optional - Display
GAME_WIDTH=1280
GAME_HEIGHT=720
FULLSCREEN=false
TARGET_FPS=60

# Optional - Gameplay
MAX_ZOMBIES=1000
```

</details>

---

<details>
<summary><h2>Development & Testing</h2></summary>

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Property-based tests only
pytest -k property
```

### Test Launcher

For manual QA testing with guided test plans:

```bash
# Launch with current test plan
python test_launcher.py

# Test specific features
python test_launcher.py --feature powerups
python test_launcher.py --feature level_entry
python test_launcher.py --feature full

# Watch logs during testing
python test_launcher.py --watch-logs

# List available plans
python test_launcher.py --list
```

### Debug Mode

```bash
LOG_LEVEL=DEBUG python src/main.py
```

### Documentation

| Doc | Purpose |
|-----|---------|
| [QUICKSTART.md](QUICKSTART.md) | Quick start for new players |
| [docs/CHEAT_CODES.md](docs/CHEAT_CODES.md) | Admin cheats for testing |
| [docs/POWERUPS.md](docs/POWERUPS.md) | Power-up types and effects |
| [docs/sonrai-api/](docs/sonrai-api/) | Sonrai API integration |
| [BACKLOG.md](BACKLOG.md) | Feature backlog |

</details>

---

## Who This Is For

- **Cloud & Identity Security teams** wanting an interactive way to explain Sonrai and least privilege
- **Developers & DevOps** who want to "see" unused identities, third parties, and service protections instead of reading another deck
- **Sales engineers & field teams** who need a memorable demo of the Cloud Permissions Firewall
- **Security leaders** who want to show boards and auditors that identity risk can be both measurable and… oddly fun

---

## Other Branches

- `v1` – original top-down lobby-only version
- `levels` – platformer-only variation

---

## License & Credits

**License**: MIT (see LICENSE)

Built with Python, Pygame, and the Sonrai Cloud Permissions Firewall.

If you build new quests, power-ups, or integrations (e.g., S3/RDS protection quests, ChatOps visualizations, scoreboards tied to real JIT requests), PRs are very welcome.

Happy hunting — and happy identity cleanup.
