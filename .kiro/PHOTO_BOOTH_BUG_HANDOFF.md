# Photo Booth Bug Handoff for Claude Code

## Problem Summary
The photo booth `start_arcade_tracking()` is **never being called** when arcade mode starts with the consent prompt. The log `📸 Photo booth arcade tracking started` never appears, so no gameplay screenshots or selfies are captured.

## Root Cause
In `src/game_engine.py`, when the photo booth consent prompt is shown, the code returns early and expects consent handling to call `_begin_arcade_session()`. But the consent input handling or timeout isn't properly triggering that method.

---

## Files to Fix

### 1. `src/game_engine.py` (main integration)

**Key sections:**
- Lines 790-800: Consent timeout check in `update()` 
- Lines 1380-1430: `_start_arcade_mode()` and `_begin_arcade_session()`
- Lines 2313+: Consent input handling

### 2. `src/photo_booth/controller.py` (PhotoBoothController)

### 3. `src/photo_booth/config.py` (configuration)

---

## Expected Flow
1. User presses Start in arcade door → `_start_arcade_mode()` called
2. Photo booth consent prompt shown → `photo_booth_consent_active = True`, returns early
3. User presses A (yes) or B (no) OR 5-second timeout expires
4. `_begin_arcade_session()` called → `photo_booth.start_arcade_tracking()` called
5. After `screenshot_delay` seconds (default 15s), gameplay captured
6. On arcade end, composite generated

## Actual Behavior
Step 3 → Step 4 is broken. After consent prompt shows, `_begin_arcade_session()` is never called.

---

## Relevant Code Snippets

### From `src/game_engine.py` - The problematic flow:

```python
# Around line 1387-1408 in _start_arcade_mode():
if (
    self.photo_booth
    and PhotoBoothState
    and self.photo_booth.state != PhotoBoothState.DISABLED
):
    self.photo_booth.reset()
    self.photo_booth.show_consent_prompt()
    self.game_state.photo_booth_consent_active = True
    logger.info("📸 Photo booth consent prompt shown - WAITING FOR INPUT")
    # Don't start arcade yet - wait for consent
    return  # <-- RETURNS HERE, expects consent handling to continue
else:
    logger.info("📸 Photo booth disabled or not available - skipping consent")

# Continue with arcade start (only reached if photo booth disabled)
self._begin_arcade_session()
```

### Consent timeout check (around line 795-799):
```python
# Handle photo booth consent timeout
if getattr(self.game_state, "photo_booth_consent_active", False) and self.photo_booth:
    if self.photo_booth.check_consent_timeout():
        logger.info("📸 Photo booth consent timed out")
        self._begin_arcade_session()
```

### `_begin_arcade_session()` (around line 1415-1430):
```python
def _begin_arcade_session(self) -> None:
    """Begin the actual arcade session after consent (if applicable)."""
    try:
        # Clear consent flag
        self.game_state.photo_booth_consent_active = False

        # Start arcade manager
        self.arcade_manager.start_session()
        logger.info(f"🎮 Arcade manager started. Is active: {self.arcade_manager.is_active()}")

        # Start photo booth arcade tracking for timed captures
        if self.photo_booth:
            self.photo_booth.start_arcade_tracking()
            logger.info(f"📸 Photo booth arcade tracking started (consent_complete={self.photo_booth.is_consent_complete()})")
        # ... rest of method
```

---

## From `src/photo_booth/controller.py`:

```python
class PhotoBoothState(Enum):
    """Photo booth state machine states."""
    DISABLED = "disabled"
    INACTIVE = "inactive"
    AWAITING_CONSENT = "awaiting_consent"
    CONSENT_GIVEN = "consent_given"
    CONSENT_DECLINED = "consent_declined"
    CAPTURING = "capturing"
    COMPOSITING = "compositing"
    COMPLETE = "complete"
    ERROR = "error"

def show_consent_prompt(self) -> None:
    """Begin consent prompt flow."""
    if self._state == PhotoBoothState.DISABLED:
        return
    self._state = PhotoBoothState.AWAITING_CONSENT
    self._consent_prompt_start = time.time()
    self._selfie_opted_in = False
    self._logger.info("Showing photo booth consent prompt")

def handle_consent_input(self, opted_in: bool) -> None:
    """Process user's consent decision."""
    if self._state != PhotoBoothState.AWAITING_CONSENT:
        return
    self._selfie_opted_in = opted_in and self._camera_available
    self._state = (
        PhotoBoothState.CONSENT_GIVEN if opted_in else PhotoBoothState.CONSENT_DECLINED
    )

def check_consent_timeout(self) -> bool:
    """Check if consent prompt has timed out."""
    if self._state != PhotoBoothState.AWAITING_CONSENT:
        return False
    if self.consent_time_remaining <= 0:
        self._logger.info("Consent prompt timed out - defaulting to no selfie")
        self.handle_consent_input(opted_in=False)
        return True
    return False

def is_consent_complete(self) -> bool:
    """Check if consent flow is complete."""
    return self._state in (
        PhotoBoothState.CONSENT_GIVEN,
        PhotoBoothState.CONSENT_DECLINED,
    )

def start_arcade_tracking(self) -> None:
    """Start tracking arcade session time for delayed captures."""
    self._arcade_start_time = time.time()
    self._gameplay_captured = False
    self._selfie_captured = False
    self._logger.info("📸 Started arcade time tracking for photo booth")
```

---

## From `src/photo_booth/config.py`:

```python
@dataclass
class PhotoBoothConfig:
    enabled: bool = True
    camera_index: int = 0
    consent_timeout: float = 5.0  # seconds to wait for consent
    min_arcade_time: float = 5.0  # minimum seconds before photo capture
    screenshot_delay: float = 5.0  # seconds into arcade to capture gameplay
    # ... other fields
```

---

## Debugging Clues

The logs show:
- `📸 Photo booth consent prompt shown - WAITING FOR INPUT` appears
- `📸 Photo booth arcade tracking started` NEVER appears
- This means `_begin_arcade_session()` is never called after consent

The consent timeout check at line 795-799 should trigger after 5 seconds, but either:
1. The game state isn't `PLAYING` so `update()` isn't running that code path
2. The `photo_booth_consent_active` flag isn't set correctly
3. The timeout check isn't being reached

---

## Fix Requirements

1. Ensure `_begin_arcade_session()` is called after:
   - User presses A (consent given)
   - User presses B (consent declined)  
   - 5-second timeout expires

2. The consent input handling (around line 2313+) needs to call `_begin_arcade_session()` after `handle_consent_input()`

3. The timeout check needs to run even when showing the consent prompt (game might be in a different state)

---

## Test After Fix

1. Start game, go to arcade door, press Start
2. Should see consent prompt
3. Either press A/B or wait 5 seconds
4. Should see log: `📸 Photo booth arcade tracking started`
5. After 15 seconds of gameplay, should see: `📸 Captured gameplay screenshot`
6. On game over, should see photo composite generated
