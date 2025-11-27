# Scattered Spider Integration Plan

**Date**: 2025-11-26
**Boss**: Scattered Spider (Swarm of 5 spiders)
**Level**: 7 - Organization
**Status**: Planning Phase

---

## Current System Analysis

### Existing Boss Infrastructure

**Files Involved:**
- `src/boss.py` - Old wizard boss (DEPRECATED, preserved)
- `src/game_engine.py` - Boss spawning, update logic, collision
- `src/renderer.py` - Boss rendering, health bar
- `src/main.py` - Main rendering loop

**Current Boss Flow:**
1. **Trigger**: All zombies cleared OR Konami code (↑↑↓↓←→←→)
2. **Spawn**: `_spawn_boss()` creates wizard at position above player
3. **State**: Game transitions to `GameStatus.BOSS_BATTLE`
4. **Update**: `_update_boss_battle()` handles boss AI and projectile collisions
5. **Render**: `render_boss()` and `render_boss_health_bar()` display boss
6. **Victory**: Boss defeated → return to lobby with level marked complete

### Boss Instance Variables in GameEngine
```python
self.boss: Optional[Boss] = None  # Line 210
self.boss_spawned = False         # Line 211
```

### Key Methods

**GameEngine:**
- `_spawn_boss()` (line 2235) - Creates and spawns boss
- `_update_boss_battle(delta_time)` (line 2285) - Update loop for boss battle
- `get_boss()` (line 2078) - Getter for boss instance

**Renderer:**
- `render_boss(boss, game_map)` (line 508) - Renders boss sprite with flash effects
- `render_boss_health_bar(boss, game_map)` (line 554) - Top-center health bar with boss name

### Konami Code System
```python
# Line 214-216
self.konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
                    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT]
self.konami_input = []
```

Activation: Line 1752-1753

---

## Integration Changes Required

### Phase 1: Imports and Infrastructure

**File: `src/game_engine.py`**

**Change 1.1: Update imports**
```python
# OLD (line 20):
from boss import Boss

# NEW:
from boss import Boss  # DEPRECATED - kept for backwards compatibility
from cyber_boss import (
    ScatteredSpiderBoss,
    create_cyber_boss,
    BossType,
    BOSS_LEVEL_MAP,
    get_boss_dialogue
)
```

**Change 1.2: Update boss instance variable**
```python
# OLD (line 210):
self.boss: Optional[Boss] = None

# NEW:
self.boss: Optional[Union[Boss, ScatteredSpiderBoss]] = None  # Union for both types
self.boss_type: Optional[BossType] = None  # Track which boss type
self.boss_dialogue_shown = False  # Track if dialogue has been displayed
```

**Change 1.3: Add dialogue state**
```python
# Add after line 211:
self.showing_boss_dialogue = False
self.boss_dialogue_content: Optional[dict] = None
```

---

### Phase 2: Boss Dialogue System

**File: `src/renderer.py`**

**New Method: `render_boss_dialogue(dialogue_content: dict)`**

Location: After `render_boss_health_bar()` (around line 593)

```python
def render_boss_dialogue(self, dialogue_content: dict) -> None:
    """
    Render educational boss introduction dialogue (Game Boy style).

    Args:
        dialogue_content: Dictionary with title, description, how_attacked,
                         victims, prevention, mechanic
    """
    # Full-screen dialogue box (Game Boy aesthetic)
    # White background with black border
    # Centered text with pixelated font
    # Sections: Title, Description, How They Attacked, Victims, Prevention, Mechanic
    # Footer: "Press ENTER to begin battle..."
```

**Design Spec:**
- **Background**: White rounded rectangle, 90% screen width, 70% screen height
- **Border**: Black, 3px thick
- **Font**: Pixelated retro (size 18 for body, 24 for title)
- **Layout**:
  ```
  [ICON] BOSS NAME [ICON]

  Description (1-2 sentences)

  HOW THEY ATTACKED:
  • Bullet point 1
  • Bullet point 2
  ...

  VICTIMS: [text]

  HOW IT COULD HAVE BEEN PREVENTED:
  ✓ Prevention 1
  ✓ Prevention 2
  ...

  BOSS MECHANIC: [description]

  Press ENTER to begin battle...
  ```

---

### Phase 3: Modified Boss Spawning

**File: `src/game_engine.py`**

**Modify: `_spawn_boss()` method (line 2235)**

```python
def _spawn_boss(self) -> None:
    """Spawn cyber attack boss with educational dialogue."""
    if self.boss_spawned:
        return

    # Step 1: Determine boss type based on current level
    current_level_num = self.level_manager.get_current_level_number() if self.level_manager else 1

    # Check if this level has a boss
    if current_level_num not in BOSS_LEVEL_MAP:
        logger.info(f"No boss defined for level {current_level_num}")
        return

    boss_type = BOSS_LEVEL_MAP[current_level_num]

    # Step 2: Show dialogue (pause game, display dialogue)
    if not self.boss_dialogue_shown:
        self.showing_boss_dialogue = True
        self.boss_dialogue_content = get_boss_dialogue(boss_type)
        self.boss_type = boss_type
        # Game pauses, dialogue shows, waiting for ENTER
        logger.info(f"📚 Showing dialogue for {boss_type.value}")
        return  # Don't spawn yet, wait for ENTER

    # Step 3: Spawn boss (after ENTER pressed)
    self.boss_spawned = True

    # Calculate spawn position
    if self.use_map and self.game_map:
        tiles_high = self.game_map.map_height // 16
        ground_height = 8
        ground_y = (tiles_high - ground_height) * 16
        level_width = self.game_map.map_width
    else:
        ground_y = 792
        level_width = 1600

    # Create cyber boss using factory
    self.boss = create_cyber_boss(boss_type, level_width, ground_y)

    if not self.boss:
        logger.error(f"Failed to create boss for type {boss_type}")
        return

    # Transition to boss battle
    self.game_state.status = GameStatus.BOSS_BATTLE
    logger.info(f"🕷️ {boss_type.value} spawned!")
```

**Modify: Handle ENTER key for dialogue dismissal**

Location: In `handle_input()` method (around line 1756)

```python
# Add before existing ENTER handling:
if event.key == pygame.K_RETURN:
    # Check if boss dialogue is showing
    if self.showing_boss_dialogue:
        self.showing_boss_dialogue = False
        self.boss_dialogue_shown = True
        # Now actually spawn the boss
        self._spawn_boss()
        continue  # Don't process other ENTER actions
```

---

### Phase 4: Update Boss Battle Logic

**File: `src/game_engine.py`**

**Modify: `_update_boss_battle()` method (line 2285)**

```python
def _update_boss_battle(self, delta_time: float) -> None:
    """Update game logic during boss battle."""

    # Check if dialogue is showing (pause game)
    if self.showing_boss_dialogue:
        return  # Don't update anything while dialogue shows

    if not self.boss:
        return

    # Check for boss defeat
    is_defeated = False
    if isinstance(self.boss, ScatteredSpiderBoss):
        # Scattered Spider - all spiders must be defeated
        is_defeated = self.boss.is_defeated
    else:
        # Regular boss
        is_defeated = self.boss.is_defeated

    if is_defeated:
        logger.info("🎉 Boss defeated! Returning to lobby...")
        self._return_to_lobby(mark_completed=True)
        return

    # Update player
    self.player.update(delta_time, is_platformer_mode=True)

    # Update boss
    self.boss.update(delta_time, self.player.position, self.game_map)

    # Update projectiles
    for projectile in self.projectiles[:]:
        projectile.update(delta_time)
        if projectile.position.x < 0 or projectile.position.x > self.game_map.map_width:
            self.projectiles.remove(projectile)
        elif projectile.is_off_screen(self.screen_width, self.screen_height, map_mode=False):
            self.projectiles.remove(projectile)

    # Check projectile collisions with boss
    if isinstance(self.boss, ScatteredSpiderBoss):
        # Scattered Spider - check collisions with each spider
        for spider in self.boss.get_all_spiders():
            spider_bounds = spider.get_bounds()
            for projectile in self.projectiles[:]:
                proj_bounds = projectile.get_bounds()
                if proj_bounds.colliderect(spider_bounds):
                    self.projectiles.remove(projectile)
                    spider.take_damage(projectile.damage)
                    break  # Projectile can only hit one spider
    else:
        # Regular boss collision
        boss_bounds = self.boss.get_bounds()
        for projectile in self.projectiles[:]:
            proj_bounds = projectile.get_bounds()
            if proj_bounds.colliderect(boss_bounds):
                self.projectiles.remove(projectile)
                self.boss.take_damage(projectile.damage)

    # Update camera
    if self.use_map and self.game_map:
        if not is_defeated:
            # Center camera on player during boss battle
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
        else:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
```

---

### Phase 5: Rendering Updates

**File: `src/renderer.py`**

**New Method: `render_scattered_spider(boss, game_map)`**

Location: After `render_boss()` (around line 553)

**IMPORTANT**: Hybrid sizing approach uses glow effect for perceived size:
- Spider sprite: 60x80 base
- Glow effect: +30px radius on all sides
- Total perceived size: ~120x140 (satisfies spec)

```python
def render_scattered_spider(self, boss: 'ScatteredSpiderBoss', game_map: Optional[GameMap] = None) -> None:
    """
    Render Scattered Spider boss (5 individual spiders with glow effects).

    Args:
        boss: ScatteredSpiderBoss instance
        game_map: Game map for coordinate conversion
    """
    if not boss or boss.is_defeated:
        return

    # Render each spider with glow effect
    for spider in boss.get_all_spiders():
        if spider.is_defeated:
            continue

        if game_map:
            # Map mode
            if game_map.is_on_screen(spider.position.x, spider.position.y, spider.width, spider.height):
                screen_x, screen_y = game_map.world_to_screen(spider.position.x, spider.position.y)

                # Step 1: Render glow effect (background, adds perceived size)
                glow_x = screen_x - spider.effect_radius
                glow_y = screen_y - spider.effect_radius
                self.screen.blit(spider.glow_sprite, (glow_x, glow_y))

                # Step 2: Render spider sprite on top
                if spider.is_flashing:
                    flash_sprite = spider.sprite.copy()
                    flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                    self.screen.blit(flash_sprite, (screen_x, screen_y))
                else:
                    self.screen.blit(spider.sprite, (screen_x, screen_y))
        else:
            # Classic mode
            if -100 < spider.position.x < self.width + 100:
                # Step 1: Render glow
                glow_x = int(spider.position.x) - spider.effect_radius
                glow_y = int(spider.position.y) - spider.effect_radius
                self.screen.blit(spider.glow_sprite, (glow_x, glow_y))

                # Step 2: Render spider
                if spider.is_flashing:
                    flash_sprite = spider.sprite.copy()
                    flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                    self.screen.blit(flash_sprite, (int(spider.position.x), int(spider.position.y)))
                else:
                    self.screen.blit(spider.sprite, (int(spider.position.x), int(spider.position.y)))
```

**Modify: `render_boss_health_bar()` to support Scattered Spider**

```python
def render_boss_health_bar(self, boss, game_map: Optional[GameMap] = None) -> None:
    """Render boss health bar at top of screen."""
    if not boss:
        return

    # Get health values
    if isinstance(boss, ScatteredSpiderBoss):
        current_health = boss.get_total_health_remaining()
        max_health = boss.get_max_health()
        boss_name = boss.name
    else:
        if boss.is_defeated:
            return
        current_health = boss.health
        max_health = boss.max_health
        boss_name = boss.name

    # ... rest of rendering logic (same as before)
```

**File: `src/main.py`**

**Modify: Rendering loop to use new render methods**

```python
# Around line 483-486:
boss = game_engine.get_boss()
if boss:
    if isinstance(boss, ScatteredSpiderBoss):
        renderer.render_scattered_spider(boss, game_map)
    else:
        renderer.render_boss(boss, game_map)
    renderer.render_boss_health_bar(boss, game_map)

# Add dialogue rendering
if game_engine.showing_boss_dialogue and game_engine.boss_dialogue_content:
    renderer.render_boss_dialogue(game_engine.boss_dialogue_content)
```

---

### Phase 6: Level Restrictions & Testing

**Konami Code Enhancement for Testing**

Currently: Spawns boss immediately
Needed: Level-specific boss spawning

**No changes needed** - `_spawn_boss()` already checks current level and only spawns appropriate boss.

**Testing Checklist:**
1. ✅ Konami code works in any level
2. ✅ Only correct boss spawns for each level
3. ✅ Scattered Spider only appears in Level 7 (Organization)
4. ✅ Dialogue shows before spawn
5. ✅ ENTER dismisses dialogue and spawns boss
6. ✅ All 5 spiders render correctly
7. ✅ Each spider has unique movement
8. ✅ Health bar shows combined health
9. ✅ Projectiles hit individual spiders
10. ✅ Boss defeated when all spiders eliminated

---

## Risk Analysis

### Potential Issues

**1. Type Conflicts**
- **Risk**: Boss instance variable expects single `Boss` type, but now can be `ScatteredSpiderBoss`
- **Mitigation**: Use `Union[Boss, ScatteredSpiderBoss]` type hint
- **Impact**: Low - Python duck typing handles this

**2. Renderer Import Circular Dependency**
- **Risk**: renderer.py imports `from boss import Boss`, adding cyber_boss might create circular dependency
- **Mitigation**: Use `TYPE_CHECKING` import or string type hints
- **Impact**: Medium - could break imports

**3. Collision Detection with Multiple Spiders**
- **Risk**: Projectile might hit multiple spiders in single frame
- **Mitigation**: `break` after first hit to consume projectile
- **Impact**: Low - easily fixed

**4. Camera During Boss Battle**
- **Risk**: Camera currently centers between player and single boss, doesn't work with 5 spiders
- **Mitigation**: Center on player position during Scattered Spider battle
- **Impact**: Low - better UX anyway

**5. Dialogue Blocking Game Loop**
- **Risk**: Dialogue pause might not properly pause all game elements
- **Mitigation**: Check `showing_boss_dialogue` flag in all update methods
- **Impact**: Medium - could cause weird behavior if missed

### Backwards Compatibility

**Old Wizard Boss:**
- Code preserved in `boss.py` with DEPRECATED marker
- Still works if someone creates `Boss()` directly
- Game engine can handle both old and new boss types
- **No breaking changes** for existing functionality

---

## Sonrai Permissions Firewall Alignment

### Educational Messaging

**Scattered Spider Dialogue:**
- ✅ Emphasizes **identity theft** (core to CPF mission)
- ✅ Highlights **MFA bypass** (authentication security)
- ✅ Mentions **session tokens** (credential management)
- ✅ References **lateral movement** (what CPF prevents)
- ✅ Promotes **JIT access** (CPF solution)
- ✅ Explicitly names **Cloud Permissions Firewall**

### Gameplay-to-Security Mapping

| Gameplay Element | Security Concept | CPF Feature |
|------------------|------------------|-------------|
| 5 different spiders | Multiple attack vectors | Multi-layered defense |
| Each spider unique movement | Different TTPs per attack | Detection variety |
| Must defeat all 5 | Complete remediation needed | Comprehensive coverage |
| Teleporting spider | Unpredictable threats | Anomaly detection |
| Swarm mechanic | Coordinated attack campaign | Incident response |

### Prevention Messaging

**Direct CPF Mentions in Dialogue:**
1. "Cloud Permissions Firewall to limit lateral movement"
2. "Just-In-Time (JIT) access limits credential exposure"
3. "Session token monitoring and anomaly detection"

**Alignment**: ✅ STRONG - Scattered Spider is the most identity-focused cyber attack, making it the perfect final boss for a cloud identity security game.

---

## Implementation Order

### Phase 1: Foundation (Completed ✅)
- [x] Create `cyber_boss.py` with `ScatteredSpiderBoss`
- [x] Implement 5 spider mechanics
- [x] Create spider sprites
- [x] Add dialogue content

### Phase 2: Integration (Current)
- [ ] Update imports in `game_engine.py`
- [ ] Modify `_spawn_boss()` for cyber bosses
- [ ] Update `_update_boss_battle()` for swarm
- [ ] Add dialogue state variables
- [ ] Implement ENTER handling for dialogue

### Phase 3: Rendering
- [ ] Create `render_boss_dialogue()` in `renderer.py`
- [ ] Create `render_scattered_spider()` in `renderer.py`
- [ ] Update `render_boss_health_bar()` for swarm
- [ ] Update `main.py` rendering loop
- [ ] Add dialogue rendering call

### Phase 4: Testing
- [ ] Test dialogue display
- [ ] Test ENTER dismissal
- [ ] Test spider spawning in Level 7
- [ ] Test Konami code in different levels
- [ ] Test all 5 spider movement types
- [ ] Test collision detection
- [ ] Test health bar display
- [ ] Test victory condition

### Phase 5: Documentation
- [ ] Update BACKLOG.md
- [ ] Document Konami code usage
- [ ] Add boss testing guide
- [ ] Update game-enhancements/tasks.md

---

## Success Criteria

**Must Have:**
- ✅ Dialogue displays before boss spawn
- ✅ ENTER dismisses dialogue and spawns boss
- ✅ All 5 spiders spawn in Level 7 (Organization)
- ✅ Each spider has unique movement pattern
- ✅ Projectiles can hit and damage individual spiders
- ✅ Health bar shows combined health of remaining spiders
- ✅ Boss defeated when all 5 spiders eliminated
- ✅ Level marked complete on victory
- ✅ No crashes or errors
- ✅ Konami code works for testing

**Nice to Have:**
- Spider-specific sound effects
- Individual spider health bars
- Spider count indicator (e.g., "5/5 remaining")
- Animated dialogue text (typewriter effect)

---

## Next Steps

1. Implement Phase 2 (Integration) changes
2. Test integration without breaking existing boss system
3. Implement Phase 3 (Rendering) changes
4. Comprehensive testing in Level 7
5. Document and commit
6. Move to next boss (Queen of Hearts / Heartbleed)

---

## Notes

- Take time to test thoroughly at each phase
- Don't rush - quality over speed
- Preserve old wizard boss code (don't delete)
- Ensure backwards compatibility
- Keep commits atomic and well-documented
