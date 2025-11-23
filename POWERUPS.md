# Power-Up System

The game features AWS-themed power-ups that spawn on platforms in platformer levels. These power-ups provide temporary advantages to help you quarantine zombies.

## Available Power-Ups

### ⭐ Star Power (Wildcard Power)
**Icon**: Gold 5-pointed star
**AWS Reference**: `*` wildcard in IAM policies
**Duration**: 10 seconds
**Effect**: Invincibility + instant quarantine on touch

When you collect Star Power:
- You become **invincible** - zombies can't damage you
- Any zombie you **touch** is **instantly quarantined** (no shooting required!)
- Best used to clear groups of zombies quickly
- Especially helpful in Sandbox levels with 500+ zombies

**Visual**: Glowing gold star with sparkle effects

---

### λ Lambda Speed
**Icon**: Orange badge with λ symbol
**AWS Reference**: AWS Lambda (serverless computing)
**Duration**: 12 seconds
**Effect**: 2x movement speed

When you collect Lambda Speed:
- Move **twice as fast** horizontally
- Jump distance increases (same jump power, but more horizontal coverage)
- Great for quickly traversing wide levels
- Useful for dodging zombies and reaching distant platforms

**Visual**: Orange circular badge with white λ (lambda) symbol

---

## Power-Up Spawning

**Sandbox Level** (many zombies):
- 6-12 power-ups spawn on platforms
- **70% Star Power**, 30% Lambda Speed
- More stars to help with large zombie counts (500+)

**Production Levels** (fewer zombies):
- 6-12 power-ups spawn on platforms
- **40% Star Power**, 60% Lambda Speed
- More balanced distribution for smaller zombie counts

**Spawn Location**:
- Power-ups appear **on top of platforms**
- Floating ~40 pixels above the platform surface
- Gentle bouncing animation to make them visible
- Collect by touching them (no need to shoot)

---

## Power-Up Mechanics

### Collection
- Walk or jump into a power-up to collect it
- A message appears showing what you collected
- Message displays for 3 seconds

### Stacking
- Multiple power-ups of the **same type** do **NOT stack**
- Collecting another while active **resets the timer** to full duration
- You **CAN** have Star Power and Lambda Speed active simultaneously

### Visual Feedback
- UI shows active power-up icons and remaining time
- Star Power: Player has special visual effect (implementation pending)
- Lambda Speed: Player moves noticeably faster

---

## Strategy Tips

### Star Power Best Practices
- Save for **dense zombie clusters**
- Rush **into** groups rather than around them
- Each zombie touched counts as an elimination (score + progress)
- Don't waste time shooting - just touch and move

### Lambda Speed Best Practices
- Use to **traverse long distances** quickly
- Combine with jumping to **skip difficult platforming**
- Great for **escaping danger** when surrounded
- Useful for **repositioning** to better vantage points

### Combining Power-Ups
- **Star Power + Lambda Speed = Ultimate Clear Mode**
- Rush through entire level touching all zombies
- Cover ground quickly while invincible
- Best combo for speed runs

---

## Technical Details

### Power-Up Types (Enum)
```python
PowerUpType.STAR_POWER    # 10s invincibility + quarantine on touch
PowerUpType.LAMBDA_SPEED  # 12s 2x movement speed
```

### Implementation Files
- `src/powerup.py` - Power-up classes and manager
- `src/game_engine.py` - Power-up spawning and effects
- `src/player.py` - Speed multiplier application

### Spawn Algorithm
1. Calculate number of power-ups: `min(12, max(6, zombies // 50))`
2. Select random platforms (excluding first 100px)
3. Place power-up on platform top
4. Choose type based on zombie count (more zombies = more stars)

---

## Removed Features

**❌ Question Mark Boxes (? blocks)**
- Previously had Mario-style ? boxes
- Removed as they served no purpose and were too derivative
- Replaced entirely with AWS-themed power-ups (stars and lambda)

**❌ Security Group Power-Up**
- Was planned as a health restoration power-up
- Removed because platformer mode has no health system
- Only lobby mode uses health for third-party battles

---

## Future Power-Up Ideas

Potential AWS-themed power-ups for future versions:

- **📦 S3 Bucket**: Collect all nearby zombies into a group
- **🔒 KMS Key**: Encrypt/freeze zombies in place temporarily
- **⚡ EC2 Instance**: Temporary auto-fire/rapid-fire mode
- **🌐 CloudFront**: Teleport to random platform (distribution)
- **📊 CloudWatch**: Reveal all zombie positions on minimap

---

## Developer Notes

### Adding New Power-Ups

1. Add to `PowerUpType` enum in `src/powerup.py`
2. Add duration and effect value in `_get_duration()` and `_get_effect_value()`
3. Add description in `get_description()`
4. Add sprite/icon in `_create_sprite()` (colors and symbols)
5. Implement effect logic in `src/game_engine.py` (update loop)
6. Add icon to power-up selection in `spawn_powerups()`

### Testing Power-Ups

Use cheat codes to unlock all levels and quickly test:
- Type `UNLOCK` in-game to unlock all levels
- Type `SKIP` to complete current level
- See [CHEAT_CODES.md](CHEAT_CODES.md) for full list
