# Bugs to Fix - Priority List

**Created:** November 28, 2024
**Status:** Active Development
**Target:** Fix before re:Invent demo

---

## P0 - Critical (Must Fix)

### BUG-001: Controller Pause Button Exits to Lobby
**File:** `src/game_engine.py` lines 2543-2556
**Issue:** Button 6 (Select) and Button 10 (Star/Home) return to lobby instead of pausing
**Root Cause:** User expects Start button (7) to pause, but accidentally hits Select (6) or Star (10)
**Impact:** Controller users can't reliably pause, accidentally exit levels

**Fix:**
```python
# Current problematic code (lines 2543-2556):
elif event.button == 6:  # Select button
    if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
        logger.info("🔙 Select button pressed - returning to lobby")
        self._return_to_lobby()

elif event.button == 10:  # Star/Home button
    if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
        logger.info("⭐ Star button pressed - returning to lobby")
        self._return_to_lobby()

# Proposed fix:
# Option 1: Remove instant lobby return, require pause menu
# Option 2: Add confirmation dialog
# Option 3: Only allow lobby return from pause menu
```

**Recommendation:** Remove buttons 6 and 10 instant lobby return. Force users to use pause menu (Start → Return to Lobby). This prevents accidental exits.

---

### BUG-002: Konami Code Doesn't Work with Controller
**File:** `src/cheat_code_controller.py` lines 54-64
**Issue:** Konami code only checks keyboard keys (pygame.K_UP, etc.), not controller D-pad
**Root Cause:** No controller D-pad input handling in cheat code system
**Impact:** Can't spawn boss with controller

**Fix:**
```python
# Need to add controller D-pad support to CheatCodeController
# D-pad buttons: 11=UP, 12=DOWN, 13=LEFT, 14=RIGHT

# Add new method:
def process_controller_input(self, button: int, current_time: float) -> CheatCodeResult:
    """Process controller button for cheat codes."""
    # Map D-pad buttons to directions
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14

    # Check for timeout
    if current_time - self.last_konami_time > self.INPUT_TIMEOUT:
        self.konami_buffer = []

    self.last_konami_time = current_time

    # Add to Konami buffer (using button numbers)
    self.konami_buffer.append(button)
    if len(self.konami_buffer) > 8:
        self.konami_buffer = self.konami_buffer[-8:]

    # Check Konami sequence: UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT
    KONAMI_SEQUENCE = [11, 11, 12, 12, 13, 14, 13, 14]
    if len(self.konami_buffer) >= 8 and self.konami_buffer[-8:] == KONAMI_SEQUENCE:
        self.konami_buffer = []
        return CheatCodeResult(
            action=CheatCodeAction.SPAWN_BOSS,
            message="🎮 KONAMI CODE! Boss incoming..."
        )

    return CheatCodeResult(action=CheatCodeAction.NONE)
```

**Also need to call this from game_engine.py controller input handling**

---

### BUG-003: Pause Menu Text Not Rendering Properly
**File:** `src/renderer.py` lines 1645-1850
**Issue:** "Return to Game" and "Arcade Mode" text garbled/missing
**Root Cause:** Likely font not loaded or text encoding issue
**Impact:** Pause menu looks broken

**Debug Steps:**
1. Check if `self.combo_font` is properly initialized
2. Check if font file exists and loads
3. Add error handling for font rendering
4. Test with different font sizes

**Fix:**
```python
# In renderer.py __init__, verify fonts load:
try:
    self.combo_font = pygame.font.Font(None, 32)
    logger.info("✅ Combo font loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load combo font: {e}")
    self.combo_font = pygame.font.Font(None, 24)  # Fallback

# Add error handling in _render_purple_menu:
try:
    text_surface = self.combo_font.render(display_text, True, text_color)
except Exception as e:
    logger.error(f"❌ Failed to render text '{display_text}': {e}")
    # Try fallback font
    text_surface = pygame.font.Font(None, 24).render(display_text, True, text_color)
```

**Also check:** Unicode characters (🎮 emoji) might not render in some fonts. Consider using ASCII alternatives.

---

### BUG-004: Missing Sonrai Logo on Pause Menu
**File:** `src/renderer.py` _render_purple_menu method
**Issue:** No Sonrai logo displayed on pause menu
**Assets:** `assets/sonrai_logo.png` or `assets/Sonrai logo_stacked_purple-black.png`
**Impact:** Missing branding opportunity

**Fix:**
```python
# In Renderer.__init__, load logo:
try:
    self.sonrai_logo = pygame.image.load("assets/sonrai_logo.png")
    # Scale to appropriate size (e.g., 100x50)
    self.sonrai_logo = pygame.transform.scale(self.sonrai_logo, (100, 50))
    logger.info("✅ Sonrai logo loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load Sonrai logo: {e}")
    self.sonrai_logo = None

# In _render_purple_menu, add logo at top:
if self.sonrai_logo:
    logo_x = menu_x + (menu_width - self.sonrai_logo.get_width()) // 2
    logo_y = menu_y + 10
    self.screen.blit(self.sonrai_logo, (logo_x, logo_y))
    current_y = logo_y + self.sonrai_logo.get_height() + 10
else:
    current_y = menu_y + padding
```

---

### BUG-005: Missing Icons in Front of "Paused"
**File:** `src/renderer.py` _render_purple_menu method
**Issue:** Icons not showing before "PAUSED" text
**Expected:** ⏸️ icon or similar visual indicator
**Impact:** Less visual polish

**Fix:**
```python
# The icon is in the message string: "⏸️  PAUSED"
# Issue might be font doesn't support emoji

# Option 1: Use ASCII art instead
title_lines = ["=== PAUSED ==="]

# Option 2: Load pause icon as image
try:
    self.pause_icon = pygame.image.load("assets/pause_icon.png")
    self.pause_icon = pygame.transform.scale(self.pause_icon, (32, 32))
except:
    self.pause_icon = None

# Render icon before title
if self.pause_icon:
    icon_x = menu_x + (menu_width - self.pause_icon.get_width()) // 2
    self.screen.blit(self.pause_icon, (icon_x, current_y))
    current_y += 40
```

---

## P1 - High Priority

### BUG-006: Health Regenerates in Lobby
**File:** `src/game_engine.py` _return_to_lobby method
**Issue:** Player health resets to max when returning to lobby
**Root Cause:** Likely resetting player state on lobby entry
**Impact:** Removes consequence of taking damage

**Fix:**
```python
# Find where player health is reset in _return_to_lobby
# Remove or comment out:
# self.player.health = self.player.max_health  # DON'T DO THIS

# Health should only restore from:
# 1. Health powerups
# 2. Level completion
# 3. New game start
```

---

### ENHANCEMENT-001: Challenge Messages Should Match Pause Menu Style
**File:** `src/renderer.py` render_message_bubble method
**Issue:** Challenge messages use white box, pause menu uses purple
**Desired:** Consistent purple theme for all messages
**Impact:** Visual consistency

**Fix:**
```python
# In render_message_bubble, check message type:
def render_message_bubble(self, message: str) -> None:
    # Check if this is a challenge/quest message
    is_challenge = any(word in message for word in [
        "CHALLENGE", "QUEST", "MISSION", "OBJECTIVE", "SUCCESS", "FAILED"
    ])

    if is_challenge or is_menu:
        self._render_purple_menu(message)  # Use purple theme
    else:
        self._render_message_box(message)  # Use white box for other messages
```

---

## P2 - Medium Priority

### TEST-001: Verify Zombie Quarantine in All Levels
**Status:** Needs testing
**Tested:** MyHealth Sandbox ✅
**Not Tested:** Production accounts, other sandboxes
**Action:** Manual testing required

---

### TEST-002: How to Launch Arcade Mode
**Issue:** User doesn't know how to launch arcade mode
**Current:** Type "ARCADE" cheat code
**Improvement:** Add to pause menu as option (already implemented!)
**Action:** Document in quick reference

---

## Implementation Priority

### Phase 1: Critical Fixes (Today)
1. ✅ BUG-001: Fix controller pause button behavior - FIXED
2. ✅ BUG-002: Add controller Konami code support - FIXED
3. BUG-003: Fix pause menu text rendering - IN PROGRESS

### Phase 2: Polish (Tomorrow)
4. BUG-004: Add Sonrai logo to pause menu
5. BUG-005: Fix pause icon display
6. BUG-006: Fix health regeneration
7. ENHANCEMENT-001: Purple theme for challenge messages

### Phase 3: Testing (Day 3)
8. TEST-001: Test all levels
9. TEST-002: Document arcade mode access
10. Full regression testing

---

## Testing Checklist After Fixes

- [ ] Controller Start button pauses game
- [ ] Controller Select/Star buttons don't exit to lobby
- [ ] Controller Konami code spawns boss
- [ ] Pause menu text renders correctly
- [ ] Sonrai logo appears on pause menu
- [ ] Pause icon displays
- [ ] Health doesn't regenerate in lobby
- [ ] Challenge messages use purple theme
- [ ] All levels tested for quarantine
- [ ] Arcade mode accessible from pause menu

---

**Next Steps:**
1. Implement Phase 1 fixes
2. Test with controller
3. Document changes
4. Update test results
