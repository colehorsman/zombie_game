# Screenshot & Recording System - Requirements

## Overview

Built-in screenshot and screen recording capabilities to capture gameplay evidence for Kiroween submission and future demos. This feature makes evidence gathering seamless during gameplay.

## Problem Statement

Currently, capturing gameplay evidence requires external tools (macOS screenshot, OBS, etc.). This breaks immersion and makes it difficult to capture the perfect moment. A built-in system allows instant capture with controller support.

## User Stories

### US-1: Screenshot Capture
**As a** player  
**I want** to capture screenshots with a button press  
**So that** I can save memorable moments instantly

**Acceptance Criteria:**
- [ ] Press X button (controller) or F12 (keyboard) to capture
- [ ] Screenshot saved to `.kiro/evidence/screenshots/`
- [ ] Filename format: `ZB_YYYYMMDD_HHMMSS.png`
- [ ] Visual flash feedback when captured
- [ ] Audio feedback (optional shutter sound)
- [ ] Works in all game states (lobby, level, pause, menus)

### US-2: Screen Recording
**As a** player  
**I want** to record gameplay clips  
**So that** I can create demo videos easily

**Acceptance Criteria:**
- [ ] Press Y button (controller) or F9 (keyboard) to start/stop
- [ ] Recording saved to `.kiro/evidence/recordings/`
- [ ] Filename format: `ZB_YYYYMMDD_HHMMSS.gif` or `.mp4`
- [ ] Visual indicator when recording (red dot in corner)
- [ ] Maximum recording length: 60 seconds (configurable)
- [ ] Auto-stop at max length with notification

### US-3: Recording Status Indicator
**As a** player  
**I want** to see when recording is active  
**So that** I know my gameplay is being captured

**Acceptance Criteria:**
- [ ] Red recording dot in top-right corner when active
- [ ] "REC" text next to dot
- [ ] Timer showing recording duration
- [ ] Dot pulses/blinks for visibility

### US-4: Evidence Organization
**As a** developer  
**I want** evidence files organized clearly  
**So that** I can find and use them easily

**Acceptance Criteria:**
- [ ] Screenshots in `.kiro/evidence/screenshots/`
- [ ] Recordings in `.kiro/evidence/recordings/`
- [ ] Consistent naming: `ZB_YYYYMMDD_HHMMSS.ext`
- [ ] Files sorted chronologically by name
- [ ] README.md in evidence folder explaining structure

## Controller Button Mapping

Based on controller mapping analysis:

| Action | Controller Button | Keyboard | Notes |
|--------|------------------|----------|-------|
| Screenshot | X (button 2) | F12 | Currently unused |
| Start/Stop Recording | Y (button 3) | F9 | Currently unused |

**Why these buttons:**
- X and Y are unused in current gameplay
- Easy to reach during gameplay
- Won't interfere with combat (A) or movement (D-pad)
- Star/Home (10) disabled to prevent accidental exits

## Technical Requirements

### Performance
- Screenshot capture < 50ms (no frame drop)
- Recording at 30 FPS (half of game's 60 FPS)
- Memory usage < 100MB for 60-second recording
- No impact on gameplay performance

### File Formats
- Screenshots: PNG (lossless, good for evidence)
- Recordings: GIF (simple, universal) or MP4 (better quality)

### Storage
- Location: `.kiro/evidence/` (within project)
- Auto-create directories if missing
- No cleanup (user manages files)

## Out of Scope (Future)

- Video editing within game
- Cloud upload
- Social media sharing
- Audio recording (game has no audio yet)
- Replay system
