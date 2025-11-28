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


### BUG-007: WannaCry Message Box Ugly and Too Verbose
**Severity:** P1
**Component:** Renderer / UI
**Description:** WannaCry boss message uses ugly white box instead of purple theme, text too long
**User Feedback:** "wanna crry message box is ugly and should be more brief with the purple menu background like pause menu"
**Impact:** Inconsistent visual style, poor UX

**Current:** White box with long text
**Desired:** Purple menu style, brief message

**Fix:**
```python
# In game_engine.py where WannaCry message is created:
# Make message brief
message = "💀 WANNACRY DETECTED!\n\nRansomware boss incoming!\n\nPress ENTER/A to continue"

# In renderer.py render_message_bubble:
# Force purple theme for boss messages
is_boss_message = "WANNACRY" in message or "BOSS" in message
if is_boss_message or is_challenge or is_menu:
    self._render_purple_menu(message)
```

---

### BUG-008: Controller A Button Doesn't Dismiss Messages
**Severity:** P0
**Component:** Input System
**Description:** Message says "Press ENTER to continue" but controller A button doesn't work
**User Feedback:** "controller cant dismiss the wannacry message because it says press enter to continue but a doesnt work"
**Impact:** Controller users stuck on message screens

**Root Cause:** A button (0) only dismisses messages in specific game states, not universally

**Fix:**
```python
# In game_engine.py controller input handling (around line 2350):
# A button should universally dismiss messages like ENTER

if event.button == 0:
    # Universal message dismissal (like ENTER key) - PRIORITY
    if self.game_state.congratulations_message:
        self.dismiss_message()
        continue  # Don't process other A button actions
    # ... rest of A button actions (shooting, etc.)
```

**Also update all message text:**
- Change "Press ENTER to continue" → "Press ENTER/A to continue"
- Change "Press SPACE to continue" → "Press SPACE/A to continue"

---

### ENHANCEMENT-002: Standardize A Button = ENTER Throughout Game
**Severity:** P1
**Component:** Input System
**Description:** Make controller A button consistently work like ENTER key everywhere
**User Feedback:** "any menu or controller mapping for the A key should match the enter key... make it consistent throughout the game, make sure the A button as enter wont cause issues elsewhere"
**Impact:** Better controller UX, consistency

**Areas to Check:**
1. ✅ Message dismissal (all message types) - BUG-008
2. Menu confirmation (pause menu, arcade results)
3. Dialog boxes (quest dialogs, boss messages)
4. Level entry (door interaction)
5. Any "Press ENTER" prompts

**Implementation Strategy:**
```python
# Create helper method in GameEngine:
def _is_confirm_button(self, event) -> bool:
    """Check if event is a confirm action (ENTER or A button)."""
    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        return True
    if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
        return True
    return False

# Use throughout codebase
if self._is_confirm_button(event):
    # Handle confirmation
```

**Potential Issues to Avoid:**
- A button shoots projectiles - ensure message dismissal takes priority ✅
- A button in menus vs gameplay - context matters
- Don't break existing shooting mechanics

**Solution:** Process message dismissal FIRST with `continue` to prevent other actions

---

## Updated Implementation Priority

### Phase 1: Critical Fixes (Today)
1. ✅ BUG-001: Fix controller pause button behavior - FIXED
2. ✅ BUG-002: Add controller Konami code support - FIXED
3. 🔄 BUG-008: Controller A button message dismissal - IN PROGRESS
4. BUG-003: Fix pause menu text rendering

### Phase 2: Polish (Tomorrow)
5. BUG-007: WannaCry message styling (purple theme + brief)
6. ENHANCEMENT-002: Standardize A=ENTER throughout
7. BUG-004: Add Sonrai logo to pause menu
8. BUG-005: Fix pause icon display
9. BUG-006: Fix health regeneration
10. ENHANCEMENT-001: Purple theme for all challenge messages

### Phase 3: Testing (Day 3)
11. TEST-001: Test all levels
12. TEST-002: Document arcade mode access
13. Full regression testing with controller

---

## Testing Checklist After New Fixes

- [ ] Controller A button dismisses all messages
- [ ] WannaCry message uses purple theme
- [ ] WannaCry message is brief and clear
- [ ] A button doesn't interfere with shooting
- [ ] A button works in all menus
- [ ] All "Press ENTER" text updated to "Press ENTER/A"
- [ ] Controller UX feels consistent


### BUG-009: Start Button Doesn't Pause During Boss Battle
**Severity:** P0
**Component:** Input System / Boss Battle
**Description:** Controller Start button doesn't pause when facing boss in MyHealth Sandbox
**User Feedback:** "the start button doesnt pause when im facing the boss in the myhealth sandbox account"
**Impact:** Can't pause during boss fights with controller

**Investigation Status:** Code looks correct, BOSS_BATTLE is included in pause condition

**Current Code (line ~2400):** ✅ Correct
```python
elif event.button == 7:
    if self.game_state.status == GameStatus.PAUSED:
        self.dismiss_message()
    elif self.game_state.status in (
        GameStatus.PLAYING,
        GameStatus.BOSS_BATTLE,  # ✅ This IS included
    ):
        self._show_pause_menu()
```

**Possible Causes:**
1. **Boss dialogue blocking input** - If boss dialogue is showing, might intercept Start button
2. **Event handling order** - Boss dialogue might consume event before pause check
3. **Game state not actually BOSS_BATTLE** - Might still be PLAYING during boss fight
4. **Controller event not reaching handler** - Some other code consuming the event

**Next Steps:**
1. Add logging to confirm game state during boss battle
2. Add logging when Start button pressed
3. Check if boss dialogue is active when Start pressed
4. Test with keyboard ESC key - does that work?

**Temporary Workaround:** Use keyboard ESC key to pause during boss battle

---

### BUG-010: WannaCry Flash Doesn't Damage Player
**Severity:** P1
**Component:** Boss Battle / Combat System
**Description:** WannaCry flash attack should damage player (1 heart) but does nothing
**User Feedback:** "when the wannacry flash happens it should impact my health one heart but it doesnt do anything"
**Impact:** Boss fight too easy, no challenge

**Root Cause Found:** ❌ **NO BOSS-TO-PLAYER COLLISION DETECTION IMPLEMENTED**
- Boss can take damage from player projectiles ✅
- Player CANNOT take damage from boss ❌
- No collision detection between boss and player
- Boss has no attack methods that damage player

**Expected Behavior:**
- WannaCry flash attack hits player
- Player loses 1 health (1 heart)
- Visual feedback (player flashes red)
- Invincibility frames after hit

**Implementation Needed:**
```python
# In game_engine.py _update_boss_battle method, add:

# Check boss-to-player collision
if self.boss and not self.boss.is_defeated:
    boss_bounds = self.boss.get_bounds()
    player_bounds = self.player.get_bounds()
    
    if boss_bounds.colliderect(player_bounds):
        # Boss touching player - deal damage
        if not self.player.is_invincible():
            self.player.take_damage(1)  # 1 heart damage
            logger.info("💔 Player hit by boss!")
            
            # Optional: Knockback effect
            # Push player away from boss
```

**Also need to implement:**
1. Player invincibility frames (0.5-1 second after hit)
2. Player visual feedback (flash red when hit)
3. Boss attack patterns (not just collision damage)
4. WannaCry specific "flash" attack with area of effect

---


### BUG-011: Hacker Challenge Message Ugly and Too Verbose
**Severity:** P1
**Component:** UI / Quest System
**Description:** Hacker challenge message (Service Protection Quest) uses ugly white box, too much text
**User Feedback:** "the hacker challenge meggage is ugly should be more brief, more bubble like and purple"
**Impact:** Inconsistent visual style, poor UX

**Current:** White box with long text
**Desired:** Purple bubble theme, brief message

**Fix:**
```python
# In game_engine.py where hacker quest message is created:
# Make it brief and use purple theme

# Current (verbose):
message = "Long explanation about hacker race..."

# New (brief):
message = "⚠️ SERVICE PROTECTION CHALLENGE!\n\nHacker detected!\nProtect services before hacker reaches them!\n\nPress ENTER/A to start"

# In renderer.py:
# Add "CHALLENGE" keyword detection for purple theme
is_challenge = any(word in message for word in [
    "CHALLENGE", "QUEST", "MISSION", "OBJECTIVE", 
    "SUCCESS", "FAILED", "HACKER", "PROTECTION"
])
```

---

### FEATURE-001: Game Over Screen Missing
**Severity:** P0
**Component:** Game Over System
**Description:** When player health reaches 0, health just resets - no game over screen
**User Feedback:** "i depleted my health bar and nothing happened but my health starte over. probably should be like game over message again purple and somethign like all zombies have been released, all 3rd parties are now allowd and services have been iunprotected or something like that - i dont think that was in previously so thats a feature"
**Impact:** No consequence for dying, breaks game loop

**Expected Behavior:**
1. Player health reaches 0
2. Game over screen appears (purple theme)
3. Show consequences message
4. Options: Retry Level, Return to Lobby

**Game Over Message:**
```
💀 SECURITY BREACH!

All zombies have been released!
All 3rd parties are now allowed!
Services are unprotected!

Your Score: [score]
Zombies Eliminated: [count]

▶ Retry Level
  Return to Lobby
```

**Implementation:**
```python
# In game_engine.py, check player health:
def _update_playing(self, delta_time):
    # ... existing code ...
    
    # Check if player died
    if self.player.health <= 0:
        self._show_game_over_screen()

def _show_game_over_screen(self):
    """Show game over screen with consequences."""
    self.game_state.previous_status = self.game_state.status
    self.game_state.status = GameStatus.PAUSED
    
    message = (
        "💀 SECURITY BREACH!\n\n"
        "All zombies have been released!\n"
        "All 3rd parties are now allowed!\n"
        "Services are unprotected!\n\n"
        f"Zombies Eliminated: {self.game_state.zombies_eliminated}\n\n"
        "▶ Retry Level\n"
        "  Return to Lobby"
    )
    
    self.game_state.congratulations_message = message
    self.game_over_menu_active = True
    logger.info("💀 Game Over - Player died!")
```

**Menu Options:**
- Retry Level: Reset level, restore health, try again
- Return to Lobby: Go back to lobby, keep progress

---

## Updated Implementation Priority

### Phase 1: Critical Fixes (Today) - URGENT
1. ✅ BUG-001: Fix controller pause button behavior - FIXED
2. ✅ BUG-002: Add controller Konami code support - FIXED
3. ✅ BUG-008: Controller A button message dismissal - FIXED
4. 🔥 **FEATURE-001: Game Over Screen** - CRITICAL MISSING FEATURE
5. 🔍 BUG-009: Start button pause during boss battle - INVESTIGATING
6. BUG-003: Fix pause menu text rendering

### Phase 2: Polish (Tomorrow)
7. BUG-011: Hacker challenge message styling (purple + brief)
8. BUG-007: WannaCry message styling (purple + brief)
9. BUG-010: Boss damage to player (collision detection)
10. ENHANCEMENT-002: Standardize A=ENTER throughout
11. BUG-004: Add Sonrai logo to pause menu
12. BUG-005: Fix pause icon display
13. BUG-006: Fix health regeneration
14. ENHANCEMENT-001: Purple theme for all challenge messages

---

## Testing Checklist After New Fixes

### Game Over System
- [ ] Player dies when health reaches 0
- [ ] Game over screen appears (purple theme)
- [ ] Consequences message displays
- [ ] Can retry level
- [ ] Can return to lobby
- [ ] Health resets on retry
- [ ] Progress preserved

### Message Styling
- [ ] Hacker challenge uses purple theme
- [ ] Hacker challenge is brief
- [ ] WannaCry message uses purple theme
- [ ] WannaCry message is brief
- [ ] All challenge messages consistent
- [ ] All messages dismissible with A button

---
