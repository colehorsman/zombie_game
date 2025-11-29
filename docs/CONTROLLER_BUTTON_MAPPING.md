# Controller Button Mapping Reference

**Last Updated:** November 28, 2024
**Purpose:** Complete reference for controller button mappings used in Sonrai Zombie Blaster

---

## User's Controller (Primary - Cole's Controller)

Based on testing, this appears to be a standard Bluetooth controller with the following mapping:

| Button | Number | Function in Game |
|--------|--------|------------------|
| A | 0 | Fire / Confirm / Dismiss messages |
| B | 1 | Jump / Cancel / Dismiss messages |
| X | 2 | (unused) |
| Y | 3 | (unused) |
| L1 (Left Shoulder) | 9 | Part of unlock combo |
| R1 (Right Shoulder) | 10 | Part of unlock combo |
| L2 (Left Trigger) | ? | (unused) |
| R2 (Right Trigger) | ? | (unused) |
| Select/Back | 6 | Pause menu (same as Start) |
| Start | 6 | Pause menu |
| L3 (Left Stick Click) | ? | (unused) |
| R3 (Right Stick Click) | ? | (unused) |
| D-Pad Up | 11 | Menu navigation / Movement |
| D-Pad Down | 12 | Menu navigation / Movement |
| D-Pad Left | 13 | Movement |
| D-Pad Right | 14 | Movement |
| Star/Home | 10 | (disabled - prevents accidental exits) |

---

## 8BitDo SN30 Pro (Secondary Reference)

| Button | Number | Function in Game |
|--------|--------|------------------|
| A (East) | 0 | Fire / Confirm / Dismiss messages |
| B (South) | 1 | Jump / Cancel / Dismiss messages |
| X (North) | 2 | (unused) |
| Y (West) | 3 | (unused) |
| L1 (Left Shoulder) | 4 | Part of unlock combo |
| R1 (Right Shoulder) | 5 | Part of unlock combo |
| L2 (Left Trigger) | 6 | (unused) |
| R2 (Right Trigger) | 7 | (unused) |
| Select | 6 | Pause menu |
| Start | 7 | Pause menu |
| L3 (Left Stick Click) | 8 | (unused) |
| R3 (Right Stick Click) | 9 | (unused) |
| D-Pad Up | 11 | Menu navigation / Movement |
| D-Pad Down | 12 | Menu navigation / Movement |
| D-Pad Left | 13 | Movement |
| D-Pad Right | 14 | Movement |
| Star/Home | 10 | (disabled) |

---

## Xbox-Style Controllers (Generic Reference)

| Button | Number | Function in Game |
|--------|--------|------------------|
| A | 0 | Fire / Confirm / Dismiss messages |
| B | 1 | Jump / Cancel / Dismiss messages |
| X | 2 | (unused) |
| Y | 3 | (unused) |
| LB (Left Bumper) | 4 | Part of unlock combo |
| RB (Right Bumper) | 5 | Part of unlock combo |
| Back/View | 6 | Pause menu |
| Start/Menu | 7 or 9 | Pause menu |
| LS (Left Stick Click) | 8 | (unused) |
| RS (Right Stick Click) | 9 | (unused) |
| D-Pad Up | Hat 0 or 11 | Menu navigation / Movement |
| D-Pad Down | Hat 0 or 12 | Menu navigation / Movement |
| D-Pad Left | Hat 0 or 13 | Movement |
| D-Pad Right | Hat 0 or 14 | Movement |
| Xbox Button | 10 | (disabled) |

---

## Game Controls Summary

### Movement (Lobby - Top-Down)
- **D-Pad / Left Stick**: Move in 4 directions
- **Keyboard**: Arrow keys or WASD

### Movement (Level - Side-Scrolling)
- **D-Pad Left/Right / Left Stick**: Move left/right
- **B Button**: Jump
- **Keyboard**: Arrow keys or WASD, Space to jump

### Combat
- **A Button**: Fire raygun
- **Keyboard**: Space or Enter to fire

### Menus
- **D-Pad Up/Down**: Navigate menu options
- **A Button**: Confirm selection
- **B Button**: Cancel / Go back
- **Start**: Open pause menu
- **Keyboard**: Arrow keys to navigate, Enter to confirm, ESC to pause

### Cheat Codes

| Cheat | Controller | Keyboard |
|-------|------------|----------|
| Unlock All Levels | L1 + R1 + Start (hold) | Type "UNLOCK" |
| Spawn Boss (Konami) | D-Pad: ↑↑↓↓←→←→ | Arrow keys: ↑↑↓↓←→←→ |
| Start Arcade Mode | N/A | Type "ARCADE" (in Sandbox only) |
| Skip Level | N/A | Type "SKIP" |

---

## Button Detection for New Controllers

If a new controller doesn't work as expected, use this debug process:

1. **Enable debug logging** in `src/cheat_code_controller.py`:
   ```python
   check_controller_unlock_combo(joystick, debug=True)
   ```

2. **Press buttons one at a time** and check the logs for:
   ```
   🎮 Buttons currently pressed: [X]
   ```

3. **Update the button mappings** in `check_controller_unlock_combo()` if needed

4. **Document the new controller** in this file

---

## Code References

### Button Handling Locations

| Feature | File | Method/Location |
|---------|------|-----------------|
| Pause (Start/Select) | `game_engine.py` | Event loop, buttons 6, 7, 9 |
| A Button (Fire/Confirm) | `game_engine.py` | Event loop, button 0 |
| B Button (Jump/Cancel) | `game_engine.py` | Event loop, button 1 |
| D-Pad Navigation | `game_engine.py` | Event loop, buttons 11-14 |
| Unlock Combo | `cheat_code_controller.py` | `check_controller_unlock_combo()` |
| Konami Code | `cheat_code_controller.py` | `process_controller_button()` |
| Movement | `game_engine.py` | Continuous input section |

### Adding Support for New Buttons

1. **For event-based actions** (single press):
   ```python
   elif event.type == pygame.JOYBUTTONDOWN:
       if event.button == NEW_BUTTON_NUMBER:
           # Handle action
   ```

2. **For continuous actions** (held buttons):
   ```python
   if self.joystick:
       if self.joystick.get_button(NEW_BUTTON_NUMBER):
           # Handle continuous action
   ```

3. **For button combos**:
   ```python
   button1 = joystick.get_button(NUM1)
   button2 = joystick.get_button(NUM2)
   if button1 and button2:
       # Handle combo
   ```

---

## Troubleshooting

### Controller Not Detected
- Ensure controller is connected before starting game
- Check console for "🎮 Detected X controller(s)" message
- Try disconnecting and reconnecting

### Buttons Not Working
- Check button mapping in this document
- Enable debug logging to see actual button numbers
- Verify controller is in correct mode (some have D-input/X-input switch)

### D-Pad Not Working
- Some controllers use Hat (analog) for D-pad, others use buttons
- Game checks both Hat and buttons 11-14
- Try both D-pad and left analog stick

### Pause Not Working
- Game checks buttons 6, 7, and 9 for pause
- If none work, check debug logs for actual Start button number
- Add new button number to the pause check in `game_engine.py`

---

## Future Improvements

- [ ] Add controller configuration screen in-game
- [ ] Allow button remapping
- [ ] Save controller preferences
- [ ] Add vibration/rumble support
- [ ] Support for more controller types

---

**Maintained by:** DevEx Agent
**Related Files:**
- `src/game_engine.py` (input handling)
- `src/cheat_code_controller.py` (cheat codes)
- `docs/guides/REINVENT_GUIDE.md` (user guide)
