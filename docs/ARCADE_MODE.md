# Arcade Mode Guide

## Overview

Arcade Mode is a 60-second elimination challenge where you eliminate as many zombies as possible without making API calls. At the end, you can batch quarantine all eliminated identities at once.

---

## Activation

### Method 1: Cheat Code
1. Enter the **Sandbox** account (MyHealth - Sandbox)
2. Press the sequence: **UP, UP, DOWN, DOWN, A, B**
3. See confirmation: "🎮 ARCADE MODE ACTIVATED!"

### Method 2: Pause Menu
1. Enter the **Sandbox** account
2. Press **ESC** (keyboard) or **Start** (controller)
3. Select **"🎮 Arcade Mode"**
4. Press **ENTER** or **A** to confirm

> **Note:** Arcade mode is only available in the Sandbox account (577945324761)

---

## Gameplay

### Phase 1: Countdown (3 seconds)
- Large countdown appears: **3...2...1...GO!**
- Prepare for action
- Zombies are active but timer hasn't started

### Phase 2: Elimination Challenge (60 seconds)
- **Timer:** Counts down from 60 seconds
  - White text: 60-11 seconds
  - Orange text: 10-6 seconds
  - Red text: 5-0 seconds
  
- **Objective:** Eliminate as many zombies as possible
  
- **Combo System:**
  - Eliminate zombies within 3 seconds of each other
  - Build combo counter (shown on screen)
  - Reach 5+ combo for **1.5x multiplier** (gold text)
  
- **Dynamic Spawning:**
  - Eliminated zombies respawn after 2 seconds
  - Spawn 500 pixels away from player
  - Minimum 20 zombies maintained
  
- **Power-Ups:**
  - **LASER_BEAM:** 10 seconds of continuous fire
  - **BURST_SHOT:** 3 one-shot kills
  - Higher spawn rate in arcade mode

### Phase 3: Results Screen
- **Statistics Displayed:**
  - Total eliminations
  - Eliminations per second
  - Highest combo achieved
  - Power-ups collected
  
- **Quarantine Options:**
  - **Yes - Quarantine All:** Batch quarantine all eliminated identities
  - **No - Discard Queue:** Discard queue and return to lobby
  - **Replay:** Start a new arcade session
  - **Exit to Lobby:** Return to lobby

---

## Controls

### Keyboard
- **Arrow Keys:** Move
- **Space:** Shoot
- **UP UP DOWN DOWN A B:** Activate arcade mode
- **ESC:** Pause
- **ENTER/SPACE:** Confirm menu selections
- **↑/↓:** Navigate menus

### Controller (8BitDo SN30 Pro)
- **D-Pad:** Move
- **A Button:** Shoot
- **UP UP DOWN DOWN A B:** Activate arcade mode
- **Start:** Pause
- **A Button:** Confirm menu selections
- **D-Pad ↑/↓:** Navigate menus

---

## Batch Quarantine

When you select **"Yes - Quarantine All"**:

1. **Progress Message:** "🔄 Quarantining X identities..."
2. **Processing:** API calls made in batches of 10
3. **Rate Limiting:** 1-second delay between batches
4. **Results:** Shows successful/failed counts
5. **Confirmation:** Press ENTER/SPACE to continue

### Example Output
```
✅ Batch Quarantine Complete!

Successful: 45/50
Failed: 5/50

Press ENTER/SPACE to continue
```

---

## Tips & Strategies

### Maximize Eliminations
1. **Build Combos:** Keep eliminating within 3 seconds for multiplier
2. **Collect Power-Ups:** LASER_BEAM and BURST_SHOT are game-changers
3. **Stay Mobile:** Zombies respawn near you, keep moving
4. **Use Platforms:** Higher ground gives better shooting angles

### Combo Mastery
- Combo window: 3 seconds
- Multiplier activates at 5+ combo
- Gold text indicates active multiplier
- Track highest combo for bragging rights

### Power-Up Priority
1. **LASER_BEAM:** Best for sustained eliminations
2. **BURST_SHOT:** Great for quick combo building
3. **STAR_POWER:** Instant eliminations on touch
4. **LAMBDA_SPEED:** Faster movement for positioning

---

## Technical Details

### Performance
- **Frame Rate:** Stable 60 FPS
- **Zombie Count:** 20+ zombies maintained
- **Respawn Delay:** 2 seconds
- **Combo Window:** 3 seconds
- **Batch Size:** 10 API calls per batch

### API Integration
- **No API calls during gameplay** (queued for batch)
- **Rate-limited batch processing** (10 calls/batch)
- **1-second delay between batches**
- **Retry logic** for failed calls
- **Progress tracking** and error reporting

---

## Troubleshooting

### "Arcade mode only available in Sandbox account"
- You're not in the Sandbox account
- Navigate to "MyHealth - Sandbox" door
- Enter the level before activating

### Cheat code not working
- Make sure you're in a level (not lobby)
- Press keys in correct sequence: UP UP DOWN DOWN A B
- Don't wait too long between presses (2-second timeout)
- Try using pause menu instead

### Zombies not respawning
- Check if you have 20+ zombies already
- Respawn has 2-second delay
- Zombies spawn 500px away from player

### Batch quarantine failed
- Check network connection
- Review error messages in results
- Failed identities can be retried manually
- Check Sonrai API credentials

---

## FAQ

**Q: Can I use arcade mode in other accounts?**
A: No, arcade mode is restricted to Sandbox account for safety.

**Q: Do eliminations count toward my score?**
A: Arcade mode has separate statistics. Regular game score is not affected.

**Q: What happens if I leave during arcade mode?**
A: Session ends immediately. You'll see results screen with option to quarantine.

**Q: Can I pause during arcade mode?**
A: Yes, press ESC or Start. Timer pauses during pause menu.

**Q: How many zombies can I eliminate?**
A: Unlimited! Zombies respawn after 2 seconds for continuous action.

**Q: Does combo multiplier affect score?**
A: Multiplier is tracked but doesn't affect elimination count. It's for bragging rights!

---

## See Also

- [Quickstart Guide](QUICKSTART.md)
- [Power-Ups Guide](POWERUPS.md)
- [Cheat Codes](CHEAT_CODES.md)
- [Architecture Documentation](architecture/ARCHITECTURE.md)

---

**Have fun and set high scores!** 🎮

