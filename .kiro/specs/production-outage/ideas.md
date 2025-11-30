# Production Outage Feature Ideas

## Core Concept
Random "production outage" during gameplay that freezes the player while they "fix prod" - with escalating visual chaos. Every developer knows that feeling of having to drop everything.

---

## Option 1: Basic Freeze + Alert (MVP)
**Complexity:** Low | **Time:** 1-2 hours

- Player freezes for 5 seconds
- Red flashing border overlay
- Text: "🚨 PRODUCTION OUTAGE 🚨" / "Fixing prod..."
- Progress bar showing "deploy" progress
- Simple implementation using existing effect systems

**Implementation:**
- Add `ProductionOutageManager` class
- ~0.5% chance per second during gameplay
- Disable player input when active
- Red overlay + message bubble

---

## Option 2: PagerDuty Chaos (Target)
**Complexity:** Medium-High | **Time:** 4-6 hours

- Screen shakes violently (leverage existing boss shake code)
- Multiple alert popups spawn across screen (like Slack notifications)
- Phone vibration sound effect
- Terminal-style text scrolling: `ERROR: NullPointerException at line 42069`
- Player mashes a key to "type faster" and reduce freeze time

**Visual Elements:**
- Slack-style notification boxes appearing randomly
- PagerDuty-red color scheme
- Glitch/static effect on screen edges
- Fake terminal window with scrolling errors

**Interactive Element:**
- Mash SPACE or a key to "deploy fix faster"
- Each press reduces remaining time slightly
- Adds engagement instead of just waiting

---

## Option 3: Incident Response Mini-Game
**Complexity:** High | **Time:** 6-8 hours

- Quick-time event: Press the flashing keys to "fix the bug"
- Success = 3 second freeze, Failure = 7 second freeze
- Shows fake error logs scrolling
- Could show "git blame" pointing at player

**Mechanics:**
- Random keys flash on screen (W, A, S, D, SPACE)
- Player must press them in sequence
- Faster completion = shorter outage
- Adds skill element to random event

---

## Option 4: "The Manager is Calling" Variant
**Complexity:** Medium | **Time:** 3-4 hours

- Phone icon appears, screen dims
- Player stuck in "meeting" while zombies close in
- Text: "Can you explain what happened?"
- Progress bar: "Explaining to stakeholders..."

**Humor Elements:**
- Meeting invite popup
- "This could have been an email"
- Calendar notification style
- Zoom-style interface mockup

---

## Visual Effects Available in Codebase

| Effect | Location | Can Reuse? |
|--------|----------|------------|
| Screen shake | `renderer.py:1118-1121` | Yes - boss battle shake |
| Flash overlay | `renderer.py:78` | Yes - damage flash |
| Message bubbles | `renderer.py:1821-1840` | Yes - quest messages |
| Lightning/glitch | `game_map.py:712-747` | Maybe - repurpose for glitch |
| Progress bars | Health bar rendering | Yes - similar pattern |

---

## Technical Implementation Notes

### Key Integration Points:
```python
# In game_engine.py _update_playing()
if self.outage_manager.is_active():
    self.outage_manager.update(delta_time)
else:
    # Check for random trigger
    if self.outage_manager.should_trigger(delta_time):
        self.outage_manager.activate()
        self.player.velocity.x = 0
        self.player.velocity.y = 0

# In handle_input() - skip movement if outage active
if not self.outage_manager.is_active():
    # Process movement...
```

### Trigger Logic:
- Base chance: ~0.5% per second (0.00833% per frame at 60fps)
- Cooldown: Minimum 30 seconds between outages
- Level scaling: Higher levels = slightly higher chance
- Not during boss battles or quests

### Files to Modify:
1. `src/production_outage.py` (new) - OutageManager class
2. `src/game_engine.py` - Trigger and input blocking
3. `src/renderer.py` - Visual effects
4. `src/main.py` - Render outage overlay

---

## Implementation Plan

### Phase 1: MVP (Option 1)
- [ ] Create `ProductionOutageManager` class
- [ ] Add random trigger in game loop
- [ ] Block player input during outage
- [ ] Add red overlay effect
- [ ] Add "Fixing prod..." message
- [ ] Add progress bar

### Phase 2: Enhanced (Option 2)
- [ ] Add screen shake during outage
- [ ] Add multiple alert popup sprites
- [ ] Add terminal-style error text
- [ ] Add key mashing to speed up fix
- [ ] Add sound effects (if available)
- [ ] Add glitch visual effect

### Phase 3: Polish
- [ ] Balance trigger frequency
- [ ] Add variety to error messages
- [ ] Add achievements ("Survived 5 outages")
- [ ] Add stats tracking (total outage time)

---

## Fun Error Messages to Display

```
ERROR: NullPointerException at line 42069
CRITICAL: Database connection timeout
ALERT: Memory usage at 99.7%
WARNING: Certificate expires in -3 days
ERROR: Cannot read property 'undefined' of undefined
FATAL: Segmentation fault (core dumped)
PANIC: Kernel panic - not syncing
ERROR: It works on my machine ¯\_(ツ)_/¯
CRITICAL: Have you tried turning it off and on again?
ALERT: The cloud is on fire
ERROR: 404 - Production not found
WARNING: This is fine. Everything is fine.
```

---

## Decision Log

- **2024-11-30:** Chose to start with Option 1 (MVP), then iterate toward Option 2 (PagerDuty Chaos)
- Rationale: Get core mechanic working first, add visual polish incrementally
