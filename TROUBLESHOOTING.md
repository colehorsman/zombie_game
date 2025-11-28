# Troubleshooting Guide

Common issues and solutions for Sonrai Zombie Blaster development.

---

## Setup Issues

### Python Version
**Problem:** `SyntaxError` or `ModuleNotFoundError`
**Cause:** Python version < 3.11
**Solution:**
```bash
python3 --version  # Should be 3.11+
# If not, install Python 3.11+
```

### Virtual Environment
**Problem:** Dependencies not found
**Cause:** Virtual environment not activated
**Solution:**
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Pygame Installation
**Problem:** Pygame won't install
**Cause:** Missing SDL libraries (Linux)
**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev

# macOS (usually not needed)
brew install sdl2 sdl2_image sdl2_mixer
```

---

## Runtime Issues

### Game Won't Start
**Problem:** Black screen or immediate crash
**Cause:** Missing .env file
**Solution:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### API Errors

**Problem:** `401 Unauthorized`
**Cause:** Invalid API token
**Solution:**
1. Check token in `.env`
2. Verify token hasn't expired
3. Test token with curl:
```bash
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"query": "query { __typename }"}' \
     <YOUR_API_URL>
```

**Problem:** `429 Too Many Requests`
**Cause:** Rate limiting
**Solution:** Wait 60 seconds and try again

**Problem:** `Connection timeout`
**Cause:** Network issues or API unavailable
**Solution:**
1. Check internet connection
2. Verify API URL in `.env`
3. Check Sonrai platform status

### Performance Issues

**Problem:** Low FPS (< 30)
**Causes & Solutions:**

1. **Too many zombies**
   - Check zombie count (should be < 500)
   - Reduce MAX_ZOMBIES in .env:
   ```bash
   MAX_ZOMBIES=300
   ```

2. **Debug logging enabled**
   - Disable verbose logging
   - Check console output

3. **System resources**
   - Close other applications
   - Check CPU/memory usage
   - Restart game

### No Zombies Loading

**Problem:** Level loads but no zombies appear
**Causes & Solutions:**

1. **No unused identities in account**
   - Try different AWS account
   - Check Sonrai platform for unused identities

2. **API error**
   - Check console for error messages
   - Verify API credentials

3. **Account not in scope**
   - Check `assets/aws_accounts.csv`
   - Verify account is in your organization

---

## Test Issues

### Tests Won't Run
**Problem:** `pytest: command not found`
**Solution:**
```bash
pip install pytest
# Or reinstall all dependencies
pip install -r requirements.txt
```

### Some Tests Fail
**Problem:** Tests failing with "No such file" or API errors
**Cause:** Tests require specific game state or Sonrai data
**Solution:** This is expected. Run unit tests only:
```bash
pytest tests/ -k "not integration"
```

### Slow Tests
**Problem:** Tests take > 10 seconds
**Cause:** Integration tests hitting real API
**Solution:** Run unit tests only:
```bash
pytest tests/unit/ -v
```

---

## Development Issues

### Pre-commit Hooks Failing
**Problem:** Commit blocked by hooks
**Cause:** Code style or security issues
**Solution:**
```bash
# See what failed
pre-commit run --all-files

# Fix automatically
black src/ tests/
isort src/ tests/

# Try commit again
git commit -m "your message"
```

### Import Errors
**Problem:** `ModuleNotFoundError` in tests
**Cause:** Python path not set
**Solution:**
```bash
# Run from project root
cd /path/to/zombie_game
pytest tests/
```

### Hot Reload Not Working
**Problem:** Changes don't appear in game
**Cause:** Game needs restart
**Solution:**
- Restart game after code changes
- (Hot reload not implemented yet)

---

## Platform-Specific Issues

### macOS

**Problem:** "Python quit unexpectedly"
**Cause:** Pygame + macOS compatibility
**Solution:**
```bash
# Use Python from python.org, not system Python
# Or use pyenv
pyenv install 3.11.0
pyenv local 3.11.0
```

**Problem:** Permission denied when running game
**Cause:** macOS security settings
**Solution:**
1. System Preferences → Security & Privacy
2. Allow app to run
3. Try again

### Windows

**Problem:** `venv\Scripts\activate` not found
**Cause:** PowerShell execution policy
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem:** Pygame window not appearing
**Cause:** Windows display scaling
**Solution:**
1. Right-click python.exe
2. Properties → Compatibility
3. Check "Disable display scaling"

### Linux

**Problem:** No sound in game
**Cause:** Missing audio libraries
**Solution:**
```bash
sudo apt install libsdl2-mixer-2.0-0
```

**Problem:** Game crashes on startup
**Cause:** Missing display server
**Solution:**
```bash
# Install X11 or Wayland
sudo apt install xorg
```

---

## Gameplay Issues

### Can't Enter Levels

**Problem:** Doors don't work
**Causes & Solutions:**

1. **Door on cooldown**
   - Wait 2 seconds between entries
   - Look for cooldown indicator

2. **Level not unlocked**
   - Use UNLOCK cheat code
   - Complete previous levels

3. **Collision detection issue**
   - Stand directly in front of door
   - Press UP key

### Quests Not Appearing

**Problem:** Expected quest doesn't show up
**Causes & Solutions:**

1. **Wrong account type**
   - Service Protection: Production accounts only
   - JIT Access: Production accounts only
   - Check account name in level

2. **Prerequisites not met**
   - Check quest requirements
   - Verify Sonrai data exists

3. **Quest already completed**
   - Check quest status in game state
   - Try different account

### Controls Not Working

**Problem:** Player won't move
**Causes & Solutions:**

1. **Wrong input mode**
   - Try keyboard: WASD or Arrow keys
   - Try controller: D-pad or left stick

2. **Controller not detected**
   - Reconnect controller
   - Check controller in system settings
   - Restart game

3. **Game paused**
   - Press ESC to unpause
   - Check for pause menu

---

## Common Error Messages

### `pygame.error: No available video device`
**Cause:** Running in headless environment
**Solution:** Use Xvfb or run on machine with display

### `FileNotFoundError: [Errno 2] No such file or directory: '.env'`
**Cause:** Missing .env file
**Solution:** `cp .env.example .env`

### `ImportError: cannot import name 'GameState' from 'models'`
**Cause:** Circular import
**Solution:** Check import order in files

### `AssertionError: Expected 60 FPS, got 45`
**Cause:** Performance test too strict
**Solution:** This is a known issue, test will be updated

### `GraphQL error: Unauthorized`
**Cause:** Invalid or expired API token
**Solution:** Rotate API token in Sonrai platform and update `.env`

### `GraphQL error: Rate limit exceeded`
**Cause:** Too many API requests
**Solution:** Wait 60 seconds, reduce MAX_ZOMBIES

---

## Debug Mode

### Enable Debug Logging

Add to `.env`:
```bash
LOG_LEVEL=DEBUG
```

This will show:
- API requests and responses
- Collision detection details
- Entity spawn/despawn events
- Quest state transitions

### Performance Profiling

```bash
# Run with profiler
python3 -m cProfile -o profile.stats src/main.py

# Analyze results
python3 -m pstats profile.stats
> sort cumulative
> stats 20
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Run with memory profiler
python3 -m memory_profiler src/main.py
```

---

## Getting More Help

### Before Opening an Issue

1. **Check existing issues:** [GitHub Issues](https://github.com/colehorsman/zombie_game/issues)
2. **Search documentation:** [docs/](docs/)
3. **Try debug mode:** Enable DEBUG logging

### Opening an Issue

Include:
- **What you're trying to do**
- **What you expected**
- **What actually happened**
- **Error messages** (full text)
- **Your environment:**
  - OS (macOS, Windows, Linux)
  - Python version (`python3 --version`)
  - Pygame version (`pip show pygame`)
  - Game version (git commit hash)

### Example Issue

```markdown
**Problem:** Game crashes when entering Production account

**Expected:** Level loads with zombies

**Actual:** Game crashes with error:
```
KeyError: 'identities'
```

**Environment:**
- macOS 14.0
- Python 3.11.5
- Pygame 2.5.2
- Commit: abc123

**Steps to reproduce:**
1. Start game
2. Use UNLOCK cheat
3. Enter Production door
4. Crash occurs
```

---

## Still Stuck?

1. **Check existing issues:** [GitHub Issues](https://github.com/colehorsman/zombie_game/issues)
2. **Search documentation:** [docs/](docs/)
3. **Ask for help:** Open a new issue with details above

---

*Can't find your issue? Open a GitHub issue and we'll add it here!*
