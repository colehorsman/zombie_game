# Arcade Photo Booth - Implementation Tasks

## Overview

Implementation tasks for the Arcade Photo Booth feature, organized by phase and priority.

**Total Estimated Effort:** 16-24 hours
**Target Completion:** Before AWS re:Invent 2025

---

## Phase 1: Foundation (4-6 hours)

### Task 1.1: Create Photo Booth Module Structure ✅
- [x] Create `src/photo_booth/` directory
- [x] Create `__init__.py` with exports
- [x] Create `config.py` with PhotoBoothConfig dataclass
- [x] Add environment variable loading from .env
- [x] Add default values for all config options

**Files:**
- `src/photo_booth/__init__.py`
- `src/photo_booth/config.py`

**Acceptance Criteria:**
- Config loads from .env ✅
- Defaults work when .env vars missing ✅
- Config is importable from main module ✅

---

### Task 1.2: Implement PhotoBoothController Core ✅
- [x] Create `controller.py` with PhotoBoothController class
- [x] Implement state machine (PhotoBoothState enum)
- [x] Implement `initialize()` for webcam setup
- [x] Implement `cleanup()` for resource release
- [x] Add logging for debugging

**Files:**
- `src/photo_booth/controller.py`

**Acceptance Criteria:**
- Controller initializes without errors ✅
- Webcam opens if available ✅
- Graceful handling if no webcam ✅
- Resources properly released on cleanup ✅

---

### Task 1.3: Implement Consent Flow ✅
- [x] Implement `show_consent_prompt()` method
- [x] Implement `handle_consent_input()` method
- [x] Implement `check_consent_timeout()` method
- [x] Add 5-second timeout logic
- [x] Store opt-in decision

**Files:**
- `src/photo_booth/controller.py`

**Acceptance Criteria:**
- Consent prompt starts timer ✅
- A button sets opted_in = True ✅
- B button sets opted_in = False ✅
- Timeout defaults to opted_in = False ✅

---

## Phase 2: Capture System (3-4 hours)

### Task 2.1: Implement Webcam Capture ✅
- [x] Implement `capture_selfie()` method
- [x] Add OpenCV webcam read
- [x] Convert BGR to RGB for PIL
- [x] Handle capture failures gracefully
- [x] Add camera active indicator flag

**Files:**
- `src/photo_booth/controller.py`

**Dependencies:**
- opencv-python package ✅

**Acceptance Criteria:**
- Captures frame from webcam ✅
- Converts to PIL Image ✅
- Returns False on failure (no crash) ✅
- Works with USB webcams ✅

---

### Task 2.2: Implement Gameplay Capture ✅
- [x] Implement `capture_gameplay()` method
- [x] Convert pygame.Surface to PIL Image
- [x] Handle surface capture errors
- [x] Ensure capture doesn't affect frame rate

**Files:**
- `src/photo_booth/controller.py`

**Acceptance Criteria:**
- Captures current game surface ✅
- Converts to PIL Image correctly ✅
- No performance impact ✅
- Works at any resolution ✅

---

### Task 2.3: Add Flash Effect
- [ ] Create flash effect in renderer
- [ ] Trigger on capture moment
- [ ] Brief white overlay (200ms)
- [ ] Fade out animation

**Files:**
- `src/renderer.py`

**Acceptance Criteria:**
- Flash visible on capture
- Doesn't block gameplay
- Smooth fade out

---

## Phase 3: Retro Filter (2-3 hours)

### Task 3.1: Implement Pixelation Filter ✅
- [x] Create `retro_filter.py` module
- [x] Implement `pixelate()` method
- [x] Downsample to ~64x64 then scale up
- [x] Use NEAREST neighbor for blocky pixels

**Files:**
- `src/photo_booth/retro_filter.py`

**Acceptance Criteria:**
- Creates blocky pixel effect ✅
- Configurable pixel size ✅
- Fast execution (< 200ms) ✅

---

### Task 3.2: Implement Color Reduction ✅
- [x] Define 16-color retro palette
- [x] Implement `reduce_colors()` method
- [x] Map pixels to nearest palette color
- [x] Maintain visual quality

**Files:**
- `src/photo_booth/retro_filter.py`

**Acceptance Criteria:**
- Reduces to 16 colors ✅
- Colors match game theme ✅
- Result looks intentionally retro ✅

---

### Task 3.3: Implement Scanline Effect ✅
- [x] Implement `add_scanlines()` method
- [x] Draw horizontal lines every 2-3 pixels
- [x] Configurable opacity
- [x] CRT monitor aesthetic

**Files:**
- `src/photo_booth/retro_filter.py`

**Acceptance Criteria:**
- Visible scanline effect ✅
- Doesn't obscure content ✅
- Authentic CRT look ✅

---

## Phase 4: Composite Generation (3-4 hours)

### Task 4.1: Create Compositor Core ✅
- [x] Create `compositor.py` module
- [x] Implement PhotoBoothCompositor class
- [x] Define layout constants
- [x] Create base canvas generation

**Files:**
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Creates 1920x1080 canvas ✅
- Dark purple background ✅
- Proper layout spacing ✅

---

### Task 4.2: Implement Panel Layout ✅
- [x] Implement `_create_selfie_panel()` method
- [x] Implement `_create_gameplay_panel()` method
- [x] Handle two-panel vs single-panel layouts
- [x] Center content within panels

**Files:**
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Two panels when selfie present ✅
- Single large panel when no selfie ✅
- Proper aspect ratio preservation ✅

---

### Task 4.3: Implement Score Header ✅
- [x] Implement `_draw_score_header()` method
- [x] Draw zombie count with stars
- [x] Add "60 SECOND CHALLENGE" subtitle
- [x] Use pixel font styling

**Files:**
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Score prominently displayed ✅
- Gold/yellow color for score ✅
- Centered text ✅
- Star decorations ✅

---

### Task 4.4: Implement Footer with Branding ✅
- [x] Implement `_draw_footer()` method
- [x] Add Sonrai logo (left)
- [x] Add event info and hashtag (center)
- [x] Add QR code placeholder (right)

**Files:**
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Logo loads and displays ✅
- Event info from config ✅
- QR code area reserved ✅
- Professional appearance ✅

---

### Task 4.5: Implement File Save ✅
- [x] Create output directory if needed
- [x] Generate filename with timestamp
- [x] Save as PNG (lossless)
- [x] Return file path

**Files:**
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Creates booth_photos directory ✅
- Unique filename per photo ✅
- PNG format, 1080p resolution ✅
- Returns valid path ✅

---

## Phase 5: Game Engine Integration (3-4 hours)

### Task 5.1: Add Arcade State Extensions ✅
- [x] Add PHOTO_CONSENT state to ArcadeState enum
- [x] Add CAPTURING state to ArcadeState enum
- [x] Update state machine transitions
- [x] Add photo_booth controller to GameEngine

**Files:**
- `src/game_engine.py`
- `src/models.py`

**Acceptance Criteria:**
- New states in enum ✅
- Proper state transitions ✅
- Controller initialized ✅

---

### Task 5.2: Integrate Consent Flow ✅
- [x] Modify `start_arcade_mode()` to show consent
- [x] Handle A/B button input for consent
- [x] Handle keyboard Y/N for consent
- [x] Transition to countdown after consent

**Files:**
- `src/game_engine.py`

**Acceptance Criteria:**
- Consent prompt appears before arcade ✅
- Both controller and keyboard work ✅
- Timeout works correctly ✅

---

### Task 5.3: Integrate Capture on Timer End ✅
- [x] Modify arcade timer end logic
- [x] Trigger gameplay capture at timer=0
- [x] Trigger selfie capture if opted in
- [x] Generate composite
- [x] Store photo path for results screen

**Files:**
- `src/game_engine.py`

**Acceptance Criteria:**
- Automatic capture on timer end ✅
- No extra button press needed ✅
- Photo generated successfully ✅

---

### Task 5.4: Render Consent Prompt UI ✅
- [x] Add `render_photo_consent_prompt()` to renderer
- [x] Semi-transparent overlay
- [x] Camera icon and title
- [x] Yes/No options with button hints
- [x] Countdown timer display

**Files:**
- `src/renderer.py`

**Acceptance Criteria:**
- Clear, readable prompt ✅
- Button hints visible ✅
- Timer countdown shown ✅
- Matches game aesthetic ✅

---

### Task 5.5: Render Results with Photo
- [ ] Modify arcade results screen
- [ ] Display photo preview
- [ ] Show "Photo saved" message
- [ ] Add photo path to results

**Files:**
- `src/renderer.py`

**Acceptance Criteria:**
- Photo preview visible
- Save confirmation shown
- Doesn't break existing results

---

## Phase 6: Assets and Polish (2-4 hours)

### Task 6.1: Create Frame Overlay Asset
- [ ] Design arcade cabinet frame (PNG)
- [ ] Transparent center for photos
- [ ] Pixel art border style
- [ ] Match game color palette

**Files:**
- `assets/photo_booth_frame.png`

**Acceptance Criteria:**
- Professional appearance
- Transparent areas correct
- Retro arcade aesthetic

---

### Task 6.2: Create Scanline Overlay Asset
- [ ] Design CRT scanline texture
- [ ] Tileable pattern
- [ ] Subtle effect

**Files:**
- `assets/scanlines.png`

**Acceptance Criteria:**
- Authentic CRT look
- Not too distracting
- Tiles seamlessly

---

### Task 6.3: Add Pixel Font
- [ ] Find/create pixel font (TTF)
- [ ] Add to assets/fonts/
- [ ] Update compositor to use font
- [ ] Fallback to system font

**Files:**
- `assets/fonts/pixel.ttf`
- `src/photo_booth/compositor.py`

**Acceptance Criteria:**
- Retro pixel font style
- Readable at all sizes
- Fallback works

---

### Task 6.4: Implement QR Code Generation
- [ ] Add qrcode package to requirements
- [ ] Generate QR code from config URL
- [ ] Embed in composite footer
- [ ] Style to match aesthetic

**Files:**
- `src/photo_booth/compositor.py`
- `requirements.txt`

**Acceptance Criteria:**
- QR code scannable
- Links to correct URL
- Fits in footer area

---

## Phase 7: Testing (2-3 hours)

### Task 7.1: Unit Tests for RetroFilter ✅
- [x] Test pixelation
- [x] Test color reduction
- [x] Test scanline effect
- [x] Test full effect chain

**Files:**
- `tests/test_photo_booth.py`

**Acceptance Criteria:**
- All filter tests pass ✅
- Edge cases covered ✅
- Performance acceptable ✅

---

### Task 7.2: Unit Tests for Compositor ✅
- [x] Test with selfie
- [x] Test without selfie
- [x] Test score rendering
- [x] Test footer rendering

**Files:**
- `tests/test_photo_booth.py`

**Acceptance Criteria:**
- Both layouts work ✅
- Output correct size ✅
- All elements present ✅

---

### Task 7.3: Integration Tests
- [ ] Test full flow with mock webcam
- [ ] Test consent timeout
- [ ] Test file save
- [ ] Test error handling

**Files:**
- `tests/test_photo_booth_integration.py`

**Acceptance Criteria:**
- Full flow works
- Errors handled gracefully
- Files saved correctly

---

### Task 7.4: Manual Testing
- [ ] Test with real webcam
- [ ] Test at booth setup
- [ ] Test various lighting conditions
- [ ] Test with multiple players

**Acceptance Criteria:**
- Works in real conditions
- Photos look good
- No crashes or hangs

---

## Phase 8: Documentation (1-2 hours)

### Task 8.1: Update README
- [ ] Add photo booth feature description
- [ ] Document configuration options
- [ ] Add setup instructions for webcam

**Files:**
- `README.md`

---

### Task 8.2: Update .env.example
- [ ] Add all PHOTO_BOOTH_* variables
- [ ] Add comments explaining each
- [ ] Set sensible defaults

**Files:**
- `.env.example`

---

### Task 8.3: Create Booth Operator Guide
- [ ] Setup instructions
- [ ] Troubleshooting guide
- [ ] Camera configuration
- [ ] Photo retrieval

**Files:**
- `docs/guides/PHOTO_BOOTH_GUIDE.md`

---

## Dependencies to Add

```bash
# Add to requirements.txt
opencv-python>=4.8.0
qrcode>=7.4.0
```

---

## Task Summary

| Phase | Tasks | Estimated Hours |
|-------|-------|-----------------|
| 1. Foundation | 3 | 4-6 |
| 2. Capture System | 3 | 3-4 |
| 3. Retro Filter | 3 | 2-3 |
| 4. Composite Generation | 5 | 3-4 |
| 5. Game Engine Integration | 5 | 3-4 |
| 6. Assets and Polish | 4 | 2-4 |
| 7. Testing | 4 | 2-3 |
| 8. Documentation | 3 | 1-2 |
| **Total** | **30** | **16-24** |

---

## Implementation Order

**Recommended sequence for fastest path to working feature:**

1. Task 1.1 → 1.2 → 1.3 (Foundation)
2. Task 2.1 → 2.2 (Capture)
3. Task 4.1 → 4.2 → 4.5 (Basic Composite)
4. Task 5.1 → 5.2 → 5.3 (Integration)
5. Task 5.4 → 5.5 (UI)
6. Task 3.1 → 3.2 → 3.3 (Retro Filter)
7. Task 4.3 → 4.4 (Polish Composite)
8. Task 6.1 → 6.2 → 6.3 → 6.4 (Assets)
9. Task 7.1 → 7.2 → 7.3 → 7.4 (Testing)
10. Task 8.1 → 8.2 → 8.3 (Documentation)

---

## Success Criteria

Feature is complete when:
- [ ] Consent prompt appears before arcade mode
- [ ] Selfie captured if opted in
- [ ] Gameplay captured automatically
- [ ] 8-bit filter applied to selfie
- [ ] Composite generated with all elements
- [ ] Photo saved to booth_photos folder
- [ ] Results screen shows photo preview
- [ ] All tests passing
- [ ] Documentation complete

---

*Let's build the most memorable booth experience at re:Invent 2025!* 🎮📸🧟
