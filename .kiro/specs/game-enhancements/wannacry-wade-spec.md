# WannaCry Boss - "Wade" Character Specification

**Date**: 2025-11-27
**Boss Type**: WannaCry
**Level**: 1 (Sandbox)
**Theme**: Crying water character inspired by Wade Ripple from Pixar's Elemental

---

## Visual Design Concept

### Character Inspiration: Wade Ripple
Wade from Elemental is a water element character with these key traits:
- **Shape**: Teardrop/water blob form - rounded, fluid, organic
- **Color**: Blue-cyan water colors with transparency
- **Personality**: Extremely emotional, cries easily and often
- **Appearance**:
  - Large expressive eyes that constantly water
  - Tear streaks running down face
  - Translucent watery body
  - Rippling, wave-like surface
  - Droplets and splashes around him

### WannaCry "Wade" Boss Adaptation

**Base Design**:
- **Shape**: Rounded teardrop/water blob (wider at middle, pointed at top)
- **Size**: 60x80 base sprite + 30px glow = ~120x140 total perceived size
- **Colors**:
  - Primary: Cyan blue (#00CED1, #1E90FF)
  - Highlights: Light cyan (#E0FFFF)
  - Shadows: Deep blue (#00008B)
  - Tears: Lighter blue with alpha transparency
- **Transparency**: Semi-transparent sprite (alpha 200-220) for watery effect

**Facial Features**:
- **Eyes**:
  - Large, sad puppy-dog eyes
  - Constantly watering with tear streaks
  - Anime-style "crying" eyes (sparkles/shine)
- **Mouth**:
  - Downturned, wobbly frown
  - Quivering lower lip (animated)
  - Opens wider when sobbing

**Surface Details**:
- Wave-like ripples across body
- Water droplet texture
- Lighter highlights for wet, reflective surface
- Drips and drops along edges

---

## Visual Effects System

### 1. Constant Crying Tears
- **Tear Streams**: 2 continuous streams from eyes
- **Tear Droplets**: Individual tears fall and splash on ground
- **Puddles**: Tears accumulate into damaging puddle zones
- **Color**: Light blue (#87CEEB) with alpha fade

### 2. Watery Glow Effect
- **Type**: Rippling blue aura
- **Animation**: Pulsing wave effect
- **Color Gradient**:
  - Outer: Cyan (#00FFFF, alpha 20)
  - Middle: Sky blue (#87CEEB, alpha 35)
  - Inner: Deep cyan (#00CED1, alpha 50)
- **Behavior**: Expands and contracts like water ripples

### 3. Sob Wave Attack
- **Visual**: Circular wave of tears radiating outward
- **Effect**: Blue ring expanding from boss
- **Particles**: Hundreds of tiny water droplets
- **Sound Cue**: "WAAAHHH!" (cry sound)

### 4. Body Ripple Animation
- **Idle**: Gentle wobble/jiggle (like gelatin)
- **Damaged**: Violent ripple across surface
- **Sobbing**: Intense shaking/quivering
- **Phases**: More unstable ripples as health decreases

### 5. Tear Puddles
- **Appearance**: Circular blue puddles on ground
- **Size**: 40x20 pixels (oval)
- **Effect**: Damage player on contact
- **Lifetime**: 5 seconds before evaporating
- **Max Puddles**: 10 active at once

---

## Boss Mechanics

### Core Stats
- **Health**: 150 HP
- **Speed**: 60.0 (slower than Heartbleed, faster than player)
- **Damage**: 15 per tear projectile, 5 per puddle tick

### Phase System (Emotional Escalation)

#### Phase 1: Sniffling (150-101 HP)
- **Behavior**: Occasional crying, slow tears
- **Attack Rate**: 3.0s cooldown
- **Sob Wave**: Every 12 seconds
- **Mood**: "I'm fine... *sniff*"

#### Phase 2: Crying (100-51 HP)
- **Behavior**: Constant tears, faster movement
- **Attack Rate**: 2.0s cooldown
- **Sob Wave**: Every 8 seconds
- **Puddles**: Start spawning
- **Mood**: "WAHHH! This hurts!"

#### Phase 3: Ugly Crying (50-1 HP)
- **Behavior**: Uncontrollable sobbing, erratic movement
- **Attack Rate**: 1.0s cooldown (rapid tears)
- **Sob Wave**: Every 5 seconds
- **Puddles**: Maximum accumulation
- **Speed**: +20 (80.0 total) - running while crying
- **Mood**: "I CAN'T STOP CRYING!!!"

### Attack Patterns

#### 1. Tear Projectiles
- **Type**: Falling tear droplets
- **Pattern**: Arcs toward player like thrown water
- **Speed**: Medium-fast projectile
- **Visual**: Teardrop shape with trail
- **Damage**: 15 HP
- **Frequency**: Based on phase

#### 2. Sob Wave (Special Attack)
- **Trigger**: Periodic timer based on phase
- **Effect**: Circular wave of tears expands from boss
- **Range**: 300px radius
- **Damage**: 20 HP if hit by wave
- **Pushback**: Knocks player back
- **Visual Warning**: Boss starts shaking, eyes squeeze shut
- **Animation**: 1 second charge, 0.5 second release

#### 3. Crying Puddles
- **Creation**: Tears that hit ground become puddles
- **Duration**: 5 seconds
- **Damage**: 5 HP per second standing in puddle
- **Strategy**: Forces player to keep moving
- **Max Active**: 10 puddles (oldest despawn first)

### Movement AI
- **Target**: Move toward player
- **Pathfinding**: Straight line (water flows)
- **Obstacle Response**: Bounces/splashes against walls
- **Speed Variance**: Slows down when sobbing, speeds up in phase 3
- **Crying Effect**: Slight wobble/sway while moving

---

## Educational Content

### WannaCry Ransomware (2017)

**Dialogue Content**:

**Title**: "😭💧 WANNACRY APPEARS! 💧😭"

**Description**:
"WannaCry was a devastating ransomware attack in May 2017 that spread across the globe like tears, encrypting files and demanding Bitcoin ransoms."

**How They Attacked**:
- Exploited EternalBlue (MS17-010) Windows SMB vulnerability
- Worm-like self-propagation across networks
- Encrypted user files with RSA-2048 encryption
- Displayed ransom note demanding $300-600 in Bitcoin
- Spread to 150+ countries in 4 days

**Victims**:
- UK National Health Service (NHS) - 80 trusts affected
- FedEx, Telefónica, Deutsche Bahn
- 200,000+ computers across 150 countries
- Estimated $4 billion in damages worldwide

**Prevention**:
- Patch MS17-010 immediately (critical security updates)
- Disable SMBv1 protocol on all systems
- Network segmentation to prevent lateral movement
- Regular offline backups (ransomware protection)
- Email filtering and user security training
- Endpoint detection and response (EDR) tools
- Cloud Permissions Firewall to limit blast radius

**Boss Mechanic**:
"Wade cries tears that spread like WannaCry ransomware!
Avoid the sob waves and don't stand in the puddles of tears.
The more you hurt him, the more he cries!"

---

## Sprite Specification

### Body Construction (60x80 pixels)

**Shape Layers**:
1. **Base Blob** (40x60): Rounded teardrop
2. **Top Point** (10x20): Tapered top like water drop
3. **Wave Ripples** (3-4 horizontal waves): Surface texture
4. **Highlight** (15x30): Wet reflection on left side

**Face Details** (positioned in upper-middle):
- **Eyes** (8x8 each): Large circles with shine spots
  - Position: 15px from sides, 20px from top
  - Pupils: Small dots, looking slightly down (sad)
  - Tear ducts: Small darker area at inner corners
- **Tear Streams**: 2 lines flowing down from eyes
  - Width: 3px, alpha gradient
  - Length: Extends to bottom of body
- **Mouth** (12px wide): Wobbly downturned arc
  - Position: 15px below eyes
  - Quivering effect: Multiple frames

**Transparency Map**:
- Center: 85% opaque
- Edges: 60% opaque (fading)
- Highlights: 95% opaque
- Shadows: 75% opaque

### Animation Frames

**Idle Animation** (3 frames, 0.3s each):
1. Normal wobble
2. Slight compress (bottom wider)
3. Slight stretch (top higher)

**Crying Animation** (2 frames, 0.2s each):
1. Eyes squeezed, mouth open
2. Eyes wide, fresh tears

**Sobbing Animation** (4 frames, 0.15s each):
1. Compress + eyes shut
2. Shake left
3. Shake right
4. Expand + mouth wide open

---

## Technical Implementation Notes

### Particle Systems

**Tear Particles**:
```python
{
    'type': 'tear',
    'x': float,
    'y': float,
    'vx': float (horizontal velocity),
    'vy': float (falling velocity),
    'lifetime': 2.0 seconds,
    'alpha': 255 → 0 (fade),
    'size': 4x6 pixels (teardrop)
}
```

**Sob Wave Particles**:
```python
{
    'type': 'wave',
    'radius': 0 → 300 (expanding),
    'thickness': 10 pixels,
    'alpha': 255 → 0 (fade as expands),
    'lifetime': 1.0 second
}
```

**Puddle Objects**:
```python
{
    'x': float,
    'y': float,
    'lifetime': 5.0 seconds,
    'alpha': 200,
    'radius': 20 pixels
}
```

### Rendering Order
1. Puddles (ground layer)
2. Watery glow effect
3. Sob wave particles (if active)
4. Boss body sprite
5. Tear stream overlay
6. Falling tear particles
7. Flash effect (if damaged)

### Collision Detection
- **Boss Body**: Standard rectangular hitbox (60x80)
- **Tear Projectiles**: Small circular hitbox (4px radius)
- **Sob Wave**: Expanding circular hitbox
- **Puddles**: Circular ground hazard (20px radius)

---

## WannaCry Metaphors in Design

| WannaCry Behavior | Wade Boss Mechanic |
|------------------|-------------------|
| Rapid network spread | Tears spreading across battlefield |
| File encryption | Puddles "lock down" ground space |
| Ransom demand | Boss demands you cry with him |
| Global impact | Sob wave affects entire screen |
| Self-propagating worm | Each tear creates more puddles |
| NHS system crashes | Healthcare = healing denied |
| $4B in damages | Emotional damage from crying |

---

## Success Criteria

✅ **Visual**:
- Wade looks like a crying water character (Elemental-inspired)
- Tears flow constantly from eyes
- Watery, translucent appearance
- Wobbles and ripples like liquid

✅ **Gameplay**:
- 3 distinct emotional phases
- Tear projectiles arc toward player
- Sob wave attack is dramatic and fair to dodge
- Puddles create environmental hazards

✅ **Educational**:
- Dialogue teaches WannaCry history
- Mechanics metaphorically represent ransomware spread
- Clear connection to identity/permissions (Cloud Firewall prevents spread)

✅ **Performance**:
- Particle system doesn't lag (max 50 active particles)
- Transparent sprite renders correctly
- Smooth animations at 60fps

---

## Implementation Checklist

- [ ] WannaCryBoss class with phase system
- [ ] Crying water sprite with transparency
- [ ] Tear particle system
- [ ] Sob wave attack animation
- [ ] Puddle spawning and management
- [ ] Wobble/ripple animation system
- [ ] render_wannacry_boss() function
- [ ] Dialogue content
- [ ] Factory integration
- [ ] Level 1 mapping
- [ ] Collision detection
- [ ] Testing in Sandbox level

---

**Design Philosophy**: "A boss that makes you feel bad for attacking him while teaching about the emotional and financial devastation of WannaCry ransomware. The more you hurt Wade, the more he cries - just like WannaCry spread faster as it infected more systems."
