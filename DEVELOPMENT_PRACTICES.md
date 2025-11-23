# Development Practices

This document outlines the development practices and standards for the Sonrai Zombie Blaster project.

## Core Principle: Stability First

**Prefer stability over speed.** It's better to take a little longer to implement a feature correctly than to ship quickly with bugs or edge cases.

### Stability-First Checklist

Before committing any code change, verify:

- ✅ **Dependency Validation**: Check all dependencies exist before using them
- ✅ **Error Handling**: Wrap risky operations in try/except with graceful fallbacks
- ✅ **Edge Cases**: Consider null/empty/missing data scenarios
- ✅ **Backwards Compatibility**: Ensure changes don't break existing functionality
- ✅ **Logging**: Add appropriate log messages for debugging
- ✅ **Testing**: Manually test the change (automated tests when available)

---

## Validation Patterns

### Before Accessing Attributes

Always validate dependencies in order:

```python
# ❌ BAD - Assumes everything exists
result = self.game_map.platform_positions[0]

# ✅ GOOD - Validates each step
if not self.game_map:
    logger.warning("Game map not initialized")
    return

if not hasattr(self.game_map, 'platform_positions'):
    logger.error("Platform positions attribute missing")
    return

if not self.game_map.platform_positions:
    logger.warning("Platform positions empty")
    return

result = self.game_map.platform_positions[0]
```

### Error Recovery

Prefer graceful degradation over crashes:

```python
# ❌ BAD - Crashes if spawn fails
self.spawn_powerups()

# ✅ GOOD - Continues without powerups if spawn fails
try:
    self.spawn_powerups()
    logger.info(f"Spawned {len(self.powerups)} powerups")
except Exception as e:
    logger.error(f"Powerup spawn failed: {e}", exc_info=True)
    self.powerups = []  # Ensure list exists
    logger.warning("Continuing without powerups")
```

### Null/Empty Checks

Always check for both None and empty collections:

```python
# ❌ BAD - Only checks None
if self.zombies:
    process_zombies(self.zombies)

# ✅ GOOD - Checks existence and non-empty
if self.zombies and len(self.zombies) > 0:
    process_zombies(self.zombies)

# ✅ BETTER - More Pythonic
if not self.zombies:
    logger.warning("No zombies to process")
    return

process_zombies(self.zombies)
```

---

## Change Impact Analysis

Before making a change, ask:

1. **What dependencies does this code have?**
   - List all objects, attributes, methods it accesses
   - Verify each dependency exists in all code paths

2. **What could go wrong?**
   - Missing attributes
   - None values
   - Empty collections
   - Network failures (for API calls)
   - File not found errors

3. **Who else uses this?**
   - Search for all references to the code you're changing
   - Check if removing/modifying it breaks other features

4. **What are the edge cases?**
   - First level vs later levels
   - Empty state vs populated state
   - New game vs loaded save
   - Lobby mode vs platformer mode

---

## Code Review Self-Checklist

Before committing, review your changes:

### Validation
- [ ] All dependencies validated before use
- [ ] None/empty checks for all collections
- [ ] hasattr() checks for optional attributes
- [ ] Mode checks (lobby vs platformer)

### Error Handling
- [ ] Try/except around risky operations
- [ ] Meaningful error messages logged
- [ ] Graceful fallbacks (don't crash the game)
- [ ] exc_info=True for debugging stack traces

### Logging
- [ ] Info logs for successful operations
- [ ] Warning logs for degraded functionality
- [ ] Error logs for failures
- [ ] Debug logs for diagnostic info

### Testing
- [ ] Manually tested the happy path
- [ ] Tested with empty/missing data
- [ ] Tested mode transitions (lobby ↔ level)
- [ ] Checked logs for errors/warnings

---

## Examples from Recent Changes

### ✅ Good Example: Powerup Spawning (Stability-First)

```python
def spawn_powerups(self) -> None:
    """
    Spawn AWS-themed power-ups ON platforms.

    Validates all dependencies before spawning to ensure stability.
    Gracefully handles missing platforms or invalid game state.
    """
    # Validation 1: Check map mode
    if not self.use_map:
        logger.debug("Not using map mode - powerups skipped")
        return

    # Validation 2: Game map exists
    if not self.game_map:
        logger.warning("Cannot spawn powerups - no game map")
        return

    # Validation 3: Platform positions attribute exists
    if not hasattr(self.game_map, 'platform_positions'):
        logger.error("GameMap missing platform_positions")
        return

    # Validation 4: Platforms not empty
    if not self.game_map.platform_positions:
        logger.warning("No platforms available")
        return

    # Validation 5: Verify platformer mode
    if hasattr(self.game_map, 'mode') and self.game_map.mode != "platformer":
        logger.debug(f"Powerups only in platformer mode")
        return

    try:
        # ... actual spawn logic ...
        logger.info(f"✨ Spawned {len(self.powerups)} powerups")
    except Exception as e:
        logger.error(f"Powerup spawn failed: {e}", exc_info=True)
        self.powerups = []  # Ensure list exists
```

**Why this is good:**
- 5 levels of validation before attempting spawn
- Clear error messages for each failure case
- Try/except catches unexpected errors
- Ensures `self.powerups` always exists
- Logs every outcome (debug, warning, error, info)

### ✅ Good Example: Level Entry Error Recovery

```python
logger.info(f"🚪 Step 13: Spawning power-ups for level")
try:
    self.spawn_powerups()
    logger.info(f"✅ Power-up spawning completed: {len(self.powerups)} powerups")
except Exception as e:
    logger.error(f"⚠️  Power-up spawning failed: {e}", exc_info=True)
    self.powerups = []  # Continue without powerups rather than crash
    logger.warning("Continuing level entry without powerups")
```

**Why this is good:**
- Level continues loading even if powerups fail
- Player can still play the level (just without powerups)
- Clear logging of what happened
- Ensures game state remains valid

---

## When to Prioritize Speed

Stability-first doesn't mean never moving fast. Speed is appropriate for:

- **Prototyping**: Quick experiments to test ideas
- **Documentation**: README updates, comments
- **Trivial changes**: Typo fixes, log message updates
- **Low-risk changes**: Adding new optional features that don't affect existing code

**But always switch to stability-first for:**
- **Core game logic**: Anything affecting gameplay
- **State management**: Save files, level progression
- **API integration**: Sonrai API calls
- **Bug fixes**: Especially crashes or data corruption

---

## QA Process

### Before Every Commit

1. **Self-review** using the checklist above
2. **Manual testing** of the changed functionality
3. **Log review** - check for warnings/errors in output
4. **Edge case testing** - try to break your change

### Before Every Release

1. **Full playthrough** from lobby through at least one level
2. **Save/load test** - verify progress persists
3. **API validation** - test with real Sonrai data
4. **Performance check** - verify 60 FPS with 500+ zombies

---

## Anti-Patterns to Avoid

### ❌ Assuming Data Exists

```python
# DON'T assume attributes exist
position = self.game_map.platform_positions[0]

# DO validate first
if self.game_map and hasattr(self.game_map, 'platform_positions'):
    if self.game_map.platform_positions:
        position = self.game_map.platform_positions[0]
```

### ❌ Swallowing Errors Silently

```python
# DON'T hide failures
try:
    critical_operation()
except:
    pass

# DO log and handle
try:
    critical_operation()
except Exception as e:
    logger.error(f"Critical operation failed: {e}", exc_info=True)
    # Take appropriate recovery action
```

### ❌ Optimistic Programming

```python
# DON'T assume best case
zombies = fetch_zombies()  # Assumes this works
for zombie in zombies:     # Crashes if None
    process(zombie)

# DO validate responses
zombies = fetch_zombies()
if not zombies:
    logger.warning("No zombies fetched")
    return

for zombie in zombies:
    process(zombie)
```

---

## Dependency Checking Workflow

When adding a new feature or modifying existing code:

### Step 1: List Dependencies

What does this code need to work?
- Objects (self.game_map, self.player, etc.)
- Attributes (platform_positions, zombies, etc.)
- External state (mode, level number, etc.)

### Step 2: Validate Each Dependency

Add checks in logical order:
1. Object exists
2. Attribute exists (hasattr)
3. Value not None
4. Collection not empty (if applicable)
5. Value in valid state (mode check, etc.)

### Step 3: Add Error Handling

Wrap risky operations:
- API calls
- File I/O
- Complex calculations
- External library calls

### Step 4: Ensure Graceful Fallback

What should happen if this fails?
- Continue with degraded functionality
- Use default values
- Return to safe state
- Log clear error message

---

## Testing Philosophy

While we don't have comprehensive automated tests yet, follow these principles:

### Manual Testing Standards

**Every change requires:**
1. **Happy path test** - Feature works as intended
2. **Empty state test** - Works with no data
3. **Mode transition test** - Works across lobby/level changes
4. **Save/load test** - Doesn't corrupt save files

### When Automated Tests Are Added

- **Test behavior, not implementation**
- **Mock external dependencies** (API, file I/O)
- **Test edge cases** explicitly
- **Keep tests fast** (milliseconds, not seconds)

---

## Version Control Practices

### Commit Message Standards

```
Brief summary of change (50 chars or less)

**What changed:**
- List specific changes made

**Why:**
- Explain the reasoning

**Impact:**
- Note any breaking changes or side effects

**Testing:**
- Describe how this was tested

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Branch Strategy

- `main` - Production-ready code
- `v1` - Simpler top-down version (maintained long-term)
- `fix/*` - Bug fixes (e.g., `fix/powerup-system`)
- `feature/*` - New features
- `refactor/*` - Code cleanup

---

## When in Doubt

**Ask these questions:**

1. "What happens if this is None?"
2. "What happens if this is empty?"
3. "What happens if this fails?"
4. "How will I debug this if it breaks?"
5. "Is there a safer way to do this?"

**If the answer is "I don't know" or "it might crash":**
→ Add validation, error handling, or ask for review

---

## Summary

**The Golden Rule:**
> It's better to ship stable code a bit slower than to ship fast code that crashes.

**Stability-First Means:**
- ✅ Validate dependencies
- ✅ Handle errors gracefully
- ✅ Log clearly
- ✅ Test thoroughly
- ✅ Prefer safety over brevity

**The game should never crash.** Features can degrade, powerups can fail to spawn, but the player should always be able to continue playing.
