# Arcade Mode Testing Guide

## 🎮 How to Test Arcade Mode

### Prerequisites
- Game is installed and configured
- `.env` file has valid Sonrai credentials
- Python virtual environment is activated

---

## Step-by-Step Testing Instructions

### Step 1: Launch the Game
```bash
# Make sure you're in the project directory
cd /path/to/zombie_game

# Activate virtual environment (if not already active)
source venv/bin/activate

# Launch the game
python3 src/main.py
```

**Expected**: Game window opens, you see the lobby (top-down view)

---

### Step 2: Navigate to Sandbox Door

**Controls**:
- **WASD** or **Arrow Keys**: Move player
- **Look for**: Door labeled "MyHealth - Sandbox"

**Tips**:
- The Sandbox door should be visible in the lobby
- It's the first/leftmost door (Account ID: 577945324761)
- Fog-of-war reveals as you move around

**Expected**: You can see the Sandbox door

---

### Step 3: Enter Sandbox Level

**Action**: Walk up to the Sandbox door and press **SPACE** or **ENTER**

**Expected**: 
- Screen transitions to side-scrolling platformer view
- You see zombies (unused identities)
- Level name shows "MyHealth - Sandbox"

---

### Step 4: Activate Arcade Mode (Method 1 - Pause Menu)

**Action**: Press **ESC** to open pause menu

**Expected Pause Menu**:
```
⏸️  PAUSED

▶ Return to Game
  🎮 Arcade Mode      ← Should be visible!
  Return to Lobby
  Save Game
  Quit Game
```

**Action**: 
1. Use **Arrow Keys** to navigate to "🎮 Arcade Mode"
2. Press **ENTER** to select

**Expected**: 
- Pause menu closes
- 3-second countdown appears: "3... 2... 1... GO!"
- Arcade mode starts

---

### Step 4 (Alternative): Activate Arcade Mode (Method 2 - Cheat Code)

**Action**: While in Sandbox level, press this sequence:
```
UP, UP, DOWN, DOWN, A, B
```

**Keyboard Mapping**:
- **UP**: Up Arrow
- **DOWN**: Down Arrow
- **A**: A key
- **B**: B key

**Expected**: 
- Message appears: "🎮 ARCADE MODE ACTIVATED!"
- 3-second countdown: "3... 2... 1... GO!"
- Arcade mode starts

---

### Step 5: Play Arcade Mode (60 seconds)

**What You Should See**:
- **Timer**: Large countdown from 60 seconds (top of screen)
- **Elimination Counter**: Shows zombies eliminated
- **Combo Counter**: Shows current combo (turns gold at 5+)
- **Zombies**: Continuously respawn after elimination

**Controls**:
- **WASD/Arrows**: Move
- **SPACE**: Shoot
- **ESC**: Pause (ends arcade session early)

**What to Test**:
1. **Eliminate Zombies**: Shoot zombies, watch elimination count increase
2. **Build Combos**: Eliminate zombies within 3 seconds of each other
3. **Combo Multiplier**: Get 5+ combo, see gold color and "1.5x" indicator
4. **Power-ups**: Collect power-ups if they spawn
5. **Dynamic Spawning**: Watch zombies respawn after 2 seconds
6. **Timer Colors**: 
   - White at 60-11 seconds
   - Orange at 10-6 seconds
   - Red at 5-0 seconds

**Expected**: Smooth 60 FPS gameplay, timer counts down, zombies respawn

---

### Step 6: Results Screen

**When Timer Reaches 0**:
- Arcade session ends automatically
- Results screen appears

**Expected Results Screen**:
```
🎯 ARCADE MODE RESULTS

📊 Your Performance:
   Eliminations: 47
   Highest Combo: 12x
   Power-ups: 3
   Duration: 60.0s
   EPS: 0.78

What would you like to do?
▶ Play Again
  Return to Game
  Return to Lobby
```

**What to Test**:
1. **Statistics Accuracy**: Check if numbers make sense
2. **Navigation**: Use Arrow Keys to navigate options
3. **Play Again**: Select "Play Again" → Should start new session
4. **Return to Game**: Select "Return to Game" → Back to normal level
5. **Return to Lobby**: Select "Return to Lobby" → Back to lobby

---

## 🧪 Test Checklist

### Core Functionality
- [ ] Game launches successfully
- [ ] Can navigate to Sandbox door
- [ ] Can enter Sandbox level
- [ ] Pause menu shows "🎮 Arcade Mode" option
- [ ] Cheat code (UP UP DOWN DOWN A B) works
- [ ] 3-second countdown displays (3...2...1...GO!)
- [ ] 60-second timer counts down
- [ ] Timer changes color (orange at 10s, red at 5s)

### Gameplay
- [ ] Can eliminate zombies
- [ ] Elimination counter increases
- [ ] Combo counter works (3-second window)
- [ ] Combo multiplier activates at 5+ (gold color, 1.5x)
- [ ] Zombies respawn after ~2 seconds
- [ ] Power-ups spawn and can be collected
- [ ] Game maintains 60 FPS

### Results Screen
- [ ] Results screen appears when timer reaches 0
- [ ] Statistics display correctly
- [ ] Can navigate options with arrow keys
- [ ] "Play Again" starts new session
- [ ] "Return to Game" goes back to level
- [ ] "Return to Lobby" exits to lobby

### Edge Cases
- [ ] Pressing ESC during arcade ends session early
- [ ] Results show correct duration if ended early
- [ ] Can't activate arcade in non-Sandbox accounts
- [ ] Arcade mode option NOT in pause menu outside Sandbox
- [ ] Cheat code doesn't work outside Sandbox

---

## 🐛 Common Issues & Solutions

### Issue: "🎮 Arcade Mode" not in pause menu
**Solution**: Make sure you're in the Sandbox level (MyHealth - Sandbox)

### Issue: Cheat code doesn't work
**Solution**: 
- Make sure you're in Sandbox level
- Press keys in exact sequence: UP UP DOWN DOWN A B
- Try using arrow keys instead of WASD

### Issue: No zombies spawning
**Solution**: 
- Check `.env` has valid Sonrai credentials
- Try using UNLOCK cheat code first (type UNLOCK)
- Verify Sandbox account has unused identities

### Issue: Game crashes or freezes
**Solution**:
- Check terminal for error messages
- Verify Python 3.11+ is installed
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Issue: Timer not visible
**Solution**: 
- Check screen resolution (game designed for 1280x720)
- Try fullscreen mode (F11)

---

## 📊 Expected Performance

### Frame Rate
- **Target**: 60 FPS
- **With 20+ zombies**: Should maintain 60 FPS
- **With power-ups**: Should maintain 60 FPS

### Timing
- **Countdown**: Exactly 3 seconds (3, 2, 1, GO)
- **Session**: Exactly 60 seconds
- **Respawn Delay**: ~2 seconds per zombie
- **Combo Window**: 3 seconds between eliminations

### Statistics
- **Eliminations**: Accurate count of zombies eliminated
- **Combo**: Highest combo achieved during session
- **EPS**: Eliminations per second (eliminations / duration)
- **Power-ups**: Count of power-ups collected

---

## 🎯 Success Criteria

Arcade mode is working correctly if:

✅ Can activate via pause menu OR cheat code
✅ 3-second countdown displays properly
✅ 60-second timer counts down accurately
✅ Zombies respawn dynamically
✅ Combo system tracks consecutive eliminations
✅ Combo multiplier activates at 5+ combo
✅ Results screen shows accurate statistics
✅ Can replay or exit from results screen
✅ Game maintains 60 FPS throughout
✅ No crashes or errors

---

## 📝 Testing Notes

**Record Your Results**:
- Eliminations achieved: _______
- Highest combo: _______
- Any bugs found: _______
- Performance issues: _______
- Suggestions: _______

**Share Feedback**:
- Report bugs in GitHub Issues
- Share high scores with team
- Suggest improvements

---

## 🚀 Advanced Testing

### Stress Test
1. Play multiple arcade sessions back-to-back
2. Try to get 100+ eliminations
3. Build 20+ combo chains
4. Collect all power-ups

### Edge Cases
1. End session at exactly 30 seconds (ESC)
2. Die during arcade mode (if damage implemented)
3. Try arcade in other accounts (should fail)
4. Activate arcade during active quest

### Performance Test
1. Monitor FPS during entire session
2. Check memory usage
3. Verify no memory leaks after multiple sessions
4. Test with 50+ zombies on screen

---

**Happy Testing! 🎮**
