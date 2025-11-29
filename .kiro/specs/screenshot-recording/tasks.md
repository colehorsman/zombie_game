# Screenshot & Recording System - Tasks

## Phase 1: Core Infrastructure (30 min)

### Task 1.1: Create EvidenceCapture Module
**File:** `src/evidence_capture.py`
**Effort:** 20 min

- [ ] Create EvidenceCapture class with dataclass
- [ ] Add directory constants and auto-creation
- [ ] Implement `_generate_filename()` method
- [ ] Add state tracking (is_recording, flash_alpha, etc.)
- [ ] Add `__post_init__` to create directories

### Task 1.2: Add Pillow Dependency
**File:** `requirements.txt`
**Effort:** 5 min

- [ ] Add `Pillow>=10.0.0` to requirements.txt
- [ ] Test import works

### Task 1.3: Update Evidence README
**File:** `.kiro/evidence/README.md`
**Effort:** 5 min

- [ ] Document screenshots/ folder
- [ ] Document recordings/ folder
- [ ] Explain naming convention

---

## Phase 2: Screenshot Feature (30 min)

### Task 2.1: Implement Screenshot Capture
**File:** `src/evidence_capture.py`
**Effort:** 15 min

- [ ] Implement `take_screenshot(screen)` method
- [ ] Save PNG to screenshots directory
- [ ] Trigger flash effect (set flash_alpha = 255)
- [ ] Return filename for logging
- [ ] Add error handling with try/except

### Task 2.2: Implement Flash Effect
**File:** `src/evidence_capture.py`
**Effort:** 10 min

- [ ] Implement `update_flash(delta_time)` method
- [ ] Fade flash_alpha from 255 to 0 over 0.15 seconds
- [ ] Add `render_flash(screen)` method for white overlay

### Task 2.3: Add Screenshot Input Handling
**File:** `src/game_engine.py`
**Effort:** 5 min

- [ ] Import EvidenceCapture
- [ ] Initialize in `__init__`
- [ ] Handle X button (2) for controller
- [ ] Handle F12 key for keyboard
- [ ] Log screenshot filename

---

## Phase 3: Recording Feature (45 min)

### Task 3.1: Implement Recording Start/Stop
**File:** `src/evidence_capture.py`
**Effort:** 15 min

- [ ] Implement `start_recording(current_time)` method
- [ ] Implement `stop_recording()` method
- [ ] Implement `toggle_recording(current_time)` method
- [ ] Track recording_start_time and recording_frames list

### Task 3.2: Implement Frame Capture
**File:** `src/evidence_capture.py`
**Effort:** 15 min

- [ ] Implement `capture_frame(screen, current_time)` method
- [ ] Capture at 30 FPS (every other game frame)
- [ ] Copy screen surface to frames list
- [ ] Check max duration (60 seconds) and auto-stop

### Task 3.3: Implement GIF Saving
**File:** `src/evidence_capture.py`
**Effort:** 15 min

- [ ] Implement `_save_recording()` method
- [ ] Convert pygame surfaces to PIL Images
- [ ] Save as animated GIF with correct frame duration
- [ ] Implement `_save_frames_as_pngs()` fallback
- [ ] Clear frames list after saving

---

## Phase 4: Visual Feedback (20 min)

### Task 4.1: Render Recording Indicator
**File:** `src/renderer.py`
**Effort:** 15 min

- [ ] Add `render_recording_indicator(screen, evidence_capture, current_time)` method
- [ ] Draw pulsing red dot in top-right corner
- [ ] Draw "REC" text next to dot
- [ ] Draw timer showing MM:SS duration
- [ ] Only show when is_recording is True

### Task 4.2: Render Screenshot Flash
**File:** `src/renderer.py`
**Effort:** 5 min

- [ ] Add `render_screenshot_flash(screen, evidence_capture)` method
- [ ] Draw white overlay with flash_alpha transparency
- [ ] Only show when flash_alpha > 0

---

## Phase 5: Game Loop Integration (15 min)

### Task 5.1: Initialize EvidenceCapture
**File:** `src/game_engine.py`
**Effort:** 5 min

- [ ] Import EvidenceCapture at top of file
- [ ] Create instance in `__init__`: `self.evidence_capture = EvidenceCapture()`

### Task 5.2: Add Input Handling
**File:** `src/game_engine.py`
**Effort:** 5 min

- [ ] In JOYBUTTONDOWN handler, add button 2 (X) for screenshot
- [ ] In JOYBUTTONDOWN handler, add button 3 (Y) for recording toggle
- [ ] In KEYDOWN handler, add F12 for screenshot
- [ ] In KEYDOWN handler, add F9 for recording toggle

### Task 5.3: Integrate Rendering
**File:** `src/game_engine.py`
**Effort:** 5 min

- [ ] Call `evidence_capture.capture_frame()` each frame when recording
- [ ] Call `evidence_capture.update_flash()` each frame
- [ ] Call renderer methods for indicator and flash
- [ ] Ensure rendering happens after game content, before flip

---

## Phase 6: Testing & Polish (20 min)

### Task 6.1: Manual Testing
**Effort:** 10 min

- [ ] Test screenshot with F12 key
- [ ] Test screenshot with X button (controller)
- [ ] Verify PNG saved to correct location
- [ ] Verify flash effect visible
- [ ] Test recording start/stop with F9 key
- [ ] Test recording with Y button (controller)
- [ ] Verify GIF saved and plays correctly
- [ ] Verify recording indicator visible

### Task 6.2: Update Controller Mapping Docs
**File:** `docs/CONTROLLER_BUTTON_MAPPING.md`
**Effort:** 5 min

- [ ] Add X button (2) = Screenshot
- [ ] Add Y button (3) = Start/Stop Recording
- [ ] Add F12 and F9 keyboard shortcuts

### Task 6.3: Commit and Document
**Effort:** 5 min

- [ ] Commit all changes
- [ ] Update README if needed
- [ ] Add to BACKLOG.md as completed

---

## Implementation Order

**Recommended sequence:**
1. Phase 1 (Infrastructure) - Foundation
2. Phase 2 (Screenshot) - Quick win, immediately useful
3. Phase 5.1-5.2 (Integration) - Wire up screenshot
4. Test screenshot works
5. Phase 3 (Recording) - More complex feature
6. Phase 4 (Visual Feedback) - Polish
7. Phase 5.3 (Full Integration) - Complete
8. Phase 6 (Testing) - Validation

**Total Estimated Effort:** 2-2.5 hours

---

## Quick Start (MVP - Screenshot Only)

For minimal viable implementation:

1. **Task 1.1** - EvidenceCapture class (20 min)
2. **Task 2.1** - Screenshot capture (15 min)
3. **Task 5.1** - Initialize (5 min)
4. **Task 5.2** - Input handling (5 min)

**MVP Total:** ~45 minutes

This gives you:
- ✅ Screenshot with X button / F12
- ✅ Files saved to `.kiro/evidence/screenshots/`
- ✅ Logging of saved files

Recording and visual effects can be added after.

---

## Files to Create/Modify

| File | Action | Changes |
|------|--------|---------|
| `src/evidence_capture.py` | CREATE | New module with EvidenceCapture class |
| `src/game_engine.py` | MODIFY | Import, init, input handling, render calls |
| `src/renderer.py` | MODIFY | Add indicator and flash rendering |
| `requirements.txt` | MODIFY | Add Pillow dependency |
| `.kiro/evidence/README.md` | MODIFY | Document new folders |
| `docs/CONTROLLER_BUTTON_MAPPING.md` | MODIFY | Add X/Y button mappings |

---

## Button Summary

| Action | Controller | Keyboard | Status |
|--------|------------|----------|--------|
| Screenshot | X (button 2) | F12 | Currently unused ✅ |
| Recording | Y (button 3) | F9 | Currently unused ✅ |
