# 🎮 Gameplay Evidence Capture Session

> **Interactive guide for capturing screenshots and recordings of Sonrai Zombie Blaster's coolest features for Kiroween submission**

---

## 📸 In-Game Capture Controls

| Action | Keyboard | Controller |
|--------|----------|------------|
| **Screenshot** | F12 | X Button |
| **Start Recording** | F9 | Y Button |
| **Stop Recording** | F9 | Y Button |

**Output Location:** `.kiro/evidence/screenshots/` and `.kiro/evidence/recordings/`

---

## 🎯 Capture Checklist

### 1. AWS Control Tower Landing Zone (Lobby View)
**File:** `lobby_aws_org_view.png`

**How to capture:**
1. Launch game: `python3 src/main.py`
2. Stay in the lobby (don't enter any doors)
3. Pan camera to show the full AWS organization layout
4. Show multiple account doors with zombie counts
5. Press **F12** to capture

**What to show:**
- AWS account doors arranged like an org chart
- Zombie counts on each door
- Player character in the lobby
- The "AWS Control Tower" feel of the landing zone

---

### 2. Photo Booth Feature
**Files:** `photo_booth_consent.png`, `photo_booth_result.png`

**How to capture:**
1. Enter Sandbox level (or use ARCADE cheat)
2. Complete an arcade session (60 seconds)
3. **Screenshot 1:** Capture the consent screen asking about selfie
4. Accept selfie (if webcam available)
5. **Screenshot 2:** Capture the final photo booth composite

**What to show:**
- Consent flow for privacy
- Retro pixel art filter on selfie
- Gameplay screenshot with score
- Zombie icons and branding
- QR code for sharing

---

### 3. Boss Battles

#### 3.1 Scattered Spider (Level 3 - Automation)
**File:** `boss_scattered_spider.png`

**How to capture:**
1. Use cheat: `UNLOCK` then enter Automation account
2. Clear all zombies to trigger boss
3. Capture the 5 mini-spiders swarm attack
4. Show the identity theft theme

**What to show:**
- 5 spider entities working together
- Swarm attack pattern
- Boss health bar
- "SCATTERED SPIDER" name display

#### 3.2 Heartbleed - The Red Queen (Level 2 - Stage)
**File:** `boss_heartbleed.png`

**How to capture:**
1. Use cheat: `UNLOCK` then enter Stage account
2. Clear all zombies to trigger boss
3. Capture the Red Queen with bleeding heart attacks
4. Show the data leak projectiles

**What to show:**
- Red Queen character design
- Black heart on chest (Heartbleed symbol)
- "Bleeding" attack projectiles
- Phase transitions (health-based)

#### 3.3 WannaCry - Wade the Weeper (Level 1 - Sandbox)
**File:** `boss_wannacry.png`

**How to capture:**
1. Enter Sandbox account
2. Clear all zombies to trigger boss
3. Capture Wade crying with tear attacks
4. Show the ransomware-themed water element

**What to show:**
- Wade character (water element, crying)
- Tear drop projectiles spreading
- "WANNACRY - WADE THE WEEPER" name
- Emotional phases (crying → ugly crying)

---

### 4. Side Quest Challenges

#### 4.1 Hacker Challenge (Service Protection Quest)
**File:** `challenge_hacker_race.png`

**How to capture:**
1. Enter Sandbox or Production account
2. Progress until hacker challenge triggers
3. Capture the race to protect Bedrock AgentCore
4. Show timer and hacker approaching service

**What to show:**
- Hacker character racing toward service
- Countdown timer
- Service icon (Bedrock AgentCore)
- "PROTECT THE SERVICE!" message
- Real-time urgency

#### 4.2 Auditor Challenge (JIT Access Quest)
**File:** `challenge_auditor_jit.png`

**How to capture:**
1. Enter a Production account (use UNLOCK cheat)
2. Look for admin roles with crowns
3. Capture the auditor patrolling
4. Show JIT protection in action

**What to show:**
- Auditor character (clipboard, glasses)
- Admin roles with golden crowns
- Purple shields on protected roles
- "ENABLE JIT ACCESS" prompt

---

### 5. Arcade Mode Features

#### 5.1 Arcade Mode Countdown
**File:** `arcade_countdown.png`

**How to capture:**
1. Enter Sandbox, select Arcade Mode
2. Capture the 3...2...1...GO! countdown
3. Show the dramatic start sequence

#### 5.2 Combo System
**File:** `arcade_combo.png`

**How to capture:**
1. During arcade mode, eliminate zombies quickly
2. Build up a combo (5x, 10x, etc.)
3. Capture the combo multiplier display
4. Show the visual feedback

#### 5.3 Results Screen with High Score
**File:** `arcade_results_highscore.png`

**How to capture:**
1. Complete an arcade session
2. If you beat the high score, capture the "🏆 NEW HIGH SCORE!" banner
3. Show the quarantine options

---

### 6. Power-Ups in Action

**File:** `powerups_collection.png`

**How to capture:**
1. Play through a level
2. Collect various power-ups (Shield, Speed, Rapid Fire, Star Power)
3. Capture the visual effects when active

**What to show:**
- AWS-themed power-up icons
- Active power-up effects on player
- Star Power invincibility glow

---

### 7. Purple Shields (Exempted Identities)

**File:** `purple_shields_exempted.png`

**How to capture:**
1. Enter any level with exempted identities
2. Find zombies with purple shields
3. Capture showing they can't be eliminated

**What to show:**
- Purple shield visual effect
- "EXEMPTED" or "PROTECTED" indicator
- Contrast with regular zombies

---

### 8. Third-Party Vendors

**File:** `third_party_vendors.png`

**How to capture:**
1. Look for third-party entities in levels
2. Capture the vendor blocking mechanic
3. Show the different vendor types

---

### 9. Level Entry Mode Selector (NEW!)

**File:** `level_entry_selector.png`

**How to capture:**
1. Approach Sandbox door in lobby
2. Capture the Arcade vs Story mode selection menu
3. Show the mode descriptions

**What to show:**
- Two options: Arcade Mode / Story Mode
- Description of each mode
- Navigation hints (A/ENTER, B/ESC)

---

### 10. re:Invent Stats Tracker

**File:** `reinvent_stats.png`

**How to capture:**
1. Run: `python3 src/reinvent_stats_tracker.py`
2. Capture the cumulative stats display
3. Show the social media post generator

**What to show:**
- Total zombies quarantined
- High score tracking
- Session history
- Auto-generated social post

---

## 🎬 Recording Suggestions

### Short Clips (5-10 seconds each)

1. **Arcade Mode Start** - Countdown and first few eliminations
2. **Boss Entrance** - Dramatic boss spawn animation
3. **Combo Chain** - Building up a high combo
4. **Photo Booth Flow** - Consent → Capture → Result
5. **Hacker Race** - Racing to protect service

### Longer Recording (30-60 seconds)

1. **Full Arcade Session** - Start to finish with results
2. **Boss Battle** - Full fight with phase transitions
3. **Lobby Tour** - Walking through AWS org structure

---

## 📁 Output Organization

After capture session, organize files:

```
.kiro/evidence/
├── gameplay/                    # NEW - Gameplay screenshots
│   ├── lobby_aws_org_view.png
│   ├── photo_booth_consent.png
│   ├── photo_booth_result.png
│   ├── boss_scattered_spider.png
│   ├── boss_heartbleed.png
│   ├── boss_wannacry.png
│   ├── challenge_hacker_race.png
│   ├── challenge_auditor_jit.png
│   ├── arcade_countdown.png
│   ├── arcade_combo.png
│   ├── arcade_results_highscore.png
│   ├── powerups_collection.png
│   ├── purple_shields_exempted.png
│   ├── third_party_vendors.png
│   ├── level_entry_selector.png
│   └── reinvent_stats.png
├── recordings/                  # Gameplay GIFs
│   ├── arcade_full_session.gif
│   ├── boss_battle_wannacry.gif
│   └── hacker_race.gif
└── booth_photos/               # Photo booth outputs
    └── BOOTH_*.png
```

---

## 🌟 Hidden Features to Highlight

These are features judges might not notice but are super cool:

1. **Photo Booth with Retro Filter** - Webcam selfies get pixel art treatment
2. **In-Game Screenshot/Recording** - F12/F9 capture system
3. **High Score Tracking** - Persistent across sessions for re:Invent
4. **Combo System** - Rewards fast eliminations
5. **Dynamic Difficulty** - Zombies respawn faster as you eliminate them
6. **Real API Integration** - Every action triggers actual Sonrai mutations
7. **Boss Dialogue System** - Contextual boss taunts and player responses
8. **Controller Hot-Plug** - Connect controller anytime, auto-detected
9. **Spatial Grid Optimization** - 60 FPS with 500+ entities
10. **Property-Based Testing** - 600+ tests with Hypothesis

---

## 📝 README Updates Needed

Add these sections to README.md:

### Hidden Gems Section
```markdown
## 🎁 Hidden Features

- **📸 Photo Booth** - Take retro-filtered selfies with your high score
- **🎬 Screen Capture** - F12 for screenshots, F9 for recordings
- **🏆 High Score Tracking** - Compete for the top score at re:Invent
- **⚡ Combo System** - Chain eliminations for bonus points
- **🎮 Controller Support** - Hot-plug any Bluetooth/USB controller
```

### Technical Achievements Section
```markdown
## 🔧 Technical Achievements

- **60 FPS** with 500+ entities via spatial grid optimization
- **600+ automated tests** including property-based testing
- **Real-time API integration** with Sonrai GraphQL
- **Spec-driven development** with Kiro AI collaboration
- **11-agent architecture review** for code quality
```

---

## ✅ Capture Session Checklist

- [ ] 1. AWS Control Tower Landing Zone
- [ ] 2. Photo Booth (consent + result)
- [ ] 3.1 Boss: Scattered Spider
- [ ] 3.2 Boss: Heartbleed
- [ ] 3.3 Boss: WannaCry
- [ ] 4.1 Challenge: Hacker Race
- [ ] 4.2 Challenge: Auditor JIT
- [ ] 5.1 Arcade: Countdown
- [ ] 5.2 Arcade: Combo System
- [ ] 5.3 Arcade: High Score Results
- [ ] 6. Power-Ups
- [ ] 7. Purple Shields
- [ ] 8. Third-Party Vendors
- [ ] 9. Level Entry Selector
- [ ] 10. re:Invent Stats

---

*Ready to capture? Launch the game and start checking off items!*
