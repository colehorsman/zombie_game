# Boss Design Document: Cyber Attack Themed Bosses

**Feature**: Cyber Attack Boss Battles
**Created**: 2025-11-26
**Status**: Design Phase

---

## Overview

Transform the boss battle system to feature famous cyber attacks as themed bosses. Each boss represents a real-world attack with:
- **Visual character design** that matches the attack name
- **Dialogue box** with quick facts about the attack
- **Educational content** about how it happened and prevention
- **Identity/cloud security relevance** connecting to the game's theme

---

## Named Cyber Attacks Research

### Tier 1: Perfect Visual + Identity Relevance ⭐⭐⭐

#### 1. Scattered Spider 🕷️
**Type**: Social engineering, identity theft, SIM swapping
**Visual**: Multiple small spiders that must all be defeated (swarm boss)
**Identity Relevance**: ⭐⭐⭐ **PERFECT**
- Targeted identity providers and MFA systems
- Used stolen credentials and session tokens
- Compromised Okta, Azure AD, AWS environments
- Social engineered help desks to reset MFA

**Dialogue**:
```
🕷️ SCATTERED SPIDER APPEARS! 🕷️

Scattered Spider was a sophisticated threat group active in 2023-2024
that specialized in IDENTITY THEFT and SOCIAL ENGINEERING.

HOW THEY ATTACKED:
• Called help desks pretending to be employees
• Bypassed MFA through SIM swapping attacks
• Stole session tokens from identity providers
• Moved laterally through cloud environments

VICTIMS: MGM Resorts, Caesars Entertainment, Okta customers

HOW IT COULD HAVE BEEN PREVENTED:
✓ Just-In-Time (JIT) access limits credential exposure
✓ Session token monitoring and anomaly detection
✓ Phishing-resistant MFA (passkeys, FIDO2)
✓ Help desk verification protocols
✓ Cloud Permissions Firewall to limit lateral movement

BOSS MECHANIC: Defeat all 5 spiders to win!
Each spider represents a different attack vector.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Spawn 5 mini-spiders instead of 1 large boss
- Each spider has 30 HP (150 total, matching current boss HP)
- Spiders use different movement patterns (fast, slow, zigzag, jumping, teleporting)
- Must defeat all 5 to complete the level
- Spiders spawn at different positions across the level

---

#### 2. ALPHV / BlackCat 🐱
**Type**: Ransomware, credential theft, privilege escalation
**Visual**: Large black cat with glowing eyes, ransomware aesthetic
**Identity Relevance**: ⭐⭐⭐ **HIGH**
- Exploited compromised credentials for initial access
- Used privilege escalation techniques
- Targeted cloud backups and identity systems
- Disabled security tools including EDR

**Dialogue**:
```
🐱 ALPHV (BLACKCAT) RANSOMWARE DETECTED! 🐱

BlackCat (ALPHV) was one of the most sophisticated ransomware
operations from 2021-2024, known for using STOLEN CREDENTIALS
and PRIVILEGE ESCALATION.

HOW THEY ATTACKED:
• Purchased stolen credentials from dark web
• Exploited over-privileged service accounts
• Used living-off-the-land techniques (legitimate tools)
• Disabled security monitoring and backups
• Encrypted cloud storage and databases

VICTIMS: Healthcare, critical infrastructure, financial services

HOW IT COULD HAVE BEEN PREVENTED:
✓ Quarantine unused identities (no credential exposure)
✓ Least-privilege access (limit blast radius)
✓ Service account monitoring and rotation
✓ Immutable backups with separate authentication
✓ Cloud Permissions Firewall blocking privilege escalation

BOSS MECHANIC: 9 Lives - Health regenerates 8 times!
You must deplete health 9 times to defeat BlackCat.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Boss has 9 "lives" (health bars)
- When health reaches 0, boss briefly vanishes and respawns with full health
- After 9 defeats, boss is permanently eliminated
- Spawns 2 mini-zombies at lives 6, 3 (like current boss system)
- Gets faster after each respawn

---

#### 3. Midnight Blizzard (APT29 / Cozy Bear) 🐻‍❄️
**Type**: Nation-state, OAuth token theft, supply chain
**Visual**: Large polar bear with Russian aesthetic, icy effects
**Identity Relevance**: ⭐⭐⭐ **HIGH**
- SolarWinds supply chain attack
- OAuth token theft from Microsoft
- Targeted authentication infrastructure
- Long-term credential harvesting

**Dialogue**:
```
🐻‍❄️ MIDNIGHT BLIZZARD DETECTED! 🐻‍❄️

Midnight Blizzard (APT29/Cozy Bear) is a Russian nation-state
threat group famous for the SOLARWINDS hack and stealing
OAUTH TOKENS from cloud identity providers.

HOW THEY ATTACKED:
• Compromised SolarWinds build system (supply chain)
• Inserted backdoor into Orion software updates
• Harvested OAuth tokens from Microsoft 365
• Maintained persistent access for months
• Targeted cloud authentication systems

VICTIMS: U.S. Government agencies, Fortune 500, Microsoft

HOW IT COULD HAVE BEEN PREVENTED:
✓ Supply chain security and software signing
✓ OAuth token rotation and monitoring
✓ Anomalous authentication detection
✓ Privileged access workstations (PAWs)
✓ Cloud Permissions Firewall for lateral movement prevention

BOSS MECHANIC: Blizzard Storm!
Boss periodically freezes the screen, limiting visibility.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Boss periodically triggers "blizzard" effect (white overlay, reduced visibility)
- Moves in unpredictable patterns during blizzard
- Spawns ice blocks that temporarily block player movement
- Health: 150 HP with standard mini-zombie spawns at 75%, 50%, 25%

---

### Tier 2: Good Visual + Moderate Identity Relevance ⭐⭐

#### 4. Volt Typhoon ⚡🌊
**Type**: Nation-state, living-off-the-land, credential theft
**Visual**: Electric storm entity with Chinese aesthetic
**Identity Relevance**: ⭐⭐ **MODERATE**
- Used stolen credentials for persistence
- Exploited valid accounts to blend in
- Targeted critical infrastructure

**Dialogue**:
```
⚡ VOLT TYPHOON CRITICAL THREAT! ⚡

Volt Typhoon is a Chinese nation-state group that uses
STOLEN CREDENTIALS and legitimate tools to hide in plain sight.

HOW THEY ATTACKED:
• Harvested credentials from compromised systems
• Used only built-in OS tools (living-off-the-land)
• Blended network traffic with normal activity
• Maintained access through valid accounts
• Avoided malware to evade detection

TARGETS: U.S. critical infrastructure, communications, energy

HOW IT COULD HAVE BEEN PREVENTED:
✓ Continuous credential monitoring
✓ Behavioral analysis of account usage
✓ Network segmentation and zero trust
✓ Privileged access logging and alerts
✓ Cloud Permissions Firewall for anomaly detection

BOSS MECHANIC: Lightning Strikes!
Random lightning bolts damage player during battle.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Periodically shoots lightning bolts that deal area damage
- Fast movement speed (1.5x normal boss speed)
- Creates electric fields that damage player if touched
- Health: 150 HP with mini-zombie spawns

---

#### 5. Sandworm 🪱
**Type**: Nation-state, destructive attacks, NotPetya
**Visual**: Large mechanical sandworm, industrial aesthetic
**Identity Relevance**: ⭐⭐ **MODERATE**
- Used stolen credentials (Mimikatz)
- Exploited EternalBlue vulnerability
- Targeted Ukraine infrastructure and spread globally

**Dialogue**:
```
🪱 SANDWORM DESTRUCTIVE ATTACK! 🪱

Sandworm is a Russian military group responsible for NotPetya,
the most destructive cyberattack in history, using STOLEN
CREDENTIALS and LATERAL MOVEMENT.

HOW THEY ATTACKED:
• Compromised Ukrainian accounting software (supply chain)
• Used Mimikatz to harvest credentials from memory
• Exploited EternalBlue (Windows SMB vulnerability)
• Wiped hard drives disguised as ransomware
• Spread globally through corporate networks

VICTIMS: Maersk, Merck, FedEx, global shipping and logistics

DAMAGE: $10+ billion in global losses

HOW IT COULD HAVE BEEN PREVENTED:
✓ Patch management (EternalBlue fix was available)
✓ Credential protection (Credential Guard, LSASS protection)
✓ Network segmentation (prevent lateral spread)
✓ Privileged account monitoring
✓ Cloud Permissions Firewall limiting privilege escalation

BOSS MECHANIC: Burrowing Attack!
Boss burrows underground and pops up at random locations.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Boss periodically burrows into ground (invulnerable)
- Pops up at random platform locations
- Sends sand waves across platforms that push player back
- Health: 150 HP with mini-zombie spawns

---

### Tier 3: Creative Visual + Loose Identity Relevance ⭐

#### 6. Heartbleed 💔
**Type**: Vulnerability, credential exposure, memory leak
**Visual**: Broken bleeding heart, glitchy aesthetic
**Identity Relevance**: ⭐ **LOOSE**
- Leaked credentials and session tokens from memory
- Exposed private keys and passwords
- Affected authentication systems globally

**Dialogue**:
```
💔 HEARTBLEED VULNERABILITY EXPOSED! 💔

Heartbleed was a critical OpenSSL vulnerability that leaked
CREDENTIALS, SESSION TOKENS, and PRIVATE KEYS from server memory.

WHAT IT WAS:
• Bug in OpenSSL heartbeat function (2012-2014)
• Allowed attackers to read server memory
• Exposed up to 64KB of sensitive data per request
• Could be exploited repeatedly without detection

EXPOSURE: Passwords, session cookies, private keys, user data

IMPACT: 17% of ALL secure web servers were vulnerable

HOW IT COULD HAVE BEEN PREVENTED/MITIGATED:
✓ Rapid patching and vulnerability management
✓ Credential rotation after patch
✓ Certificate revocation and reissuance
✓ Memory protection and bounds checking
✓ Short-lived session tokens (reduces exposure window)

BOSS MECHANIC: Memory Leak!
Boss drops "memory fragments" that damage on contact.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Boss continuously spawns damaging memory fragment projectiles
- Fragments fall from above and bounce around
- Boss health slowly regenerates over time (leak mechanic)
- Health: 150 HP with mini-zombie spawns

---

#### 7. WannaCry 😭
**Type**: Ransomware worm, EternalBlue, NHS attack
**Visual**: Crying face emoji, ransomware aesthetic with lock symbols
**Identity Relevance**: ⭐ **LOOSE**
- Used EternalBlue (vulnerability exploitation, not identity-focused)
- Some lateral movement via credentials
- More about unpatched systems than identity

**Dialogue**:
```
😭 WANNACRY RANSOMWARE OUTBREAK! 😭

WannaCry was a global ransomware worm that spread using
the ETERNALBLUE exploit, crippling hospitals and businesses
worldwide in May 2017.

HOW IT SPREAD:
• Exploited unpatched Windows SMB vulnerability (EternalBlue)
• Self-propagated like a worm (no user interaction needed)
• Encrypted files and demanded Bitcoin ransom
• Spread to 150+ countries in hours
• Caused $4+ billion in damages

VICTIMS: UK's NHS, FedEx, Renault, Deutsche Bahn, Telefónica

STOPPED BY: Accidental kill switch domain registration

HOW IT COULD HAVE BEEN PREVENTED:
✓ Patch management (MS17-010 was available for months)
✓ Network segmentation (prevent worm spread)
✓ Backup and recovery processes
✓ Legacy system upgrades (many ran Windows XP)
✓ Incident response planning

BOSS MECHANIC: Worm Spread!
Boss spawns copies of itself periodically.

Press ENTER to begin battle...
```

**Boss Mechanics**:
- Boss spawns smaller "worm copies" every 10 seconds
- Copies have 20 HP each, maximum 3 active at once
- Must defeat main boss (150 HP) to win
- Copies disappear when main boss defeated

---

## Level Assignment Strategy

Map bosses to levels (accounts) based on environment type and attack sophistication:

### Level 1: Sandbox (Tutorial Level)
**Boss**: **WannaCry** 😭
- **Reasoning**: Well-known, simpler mechanics, good introduction
- **Educational Value**: Teaches patching importance
- **Difficulty**: Easy - copying mechanic is manageable

### Level 2: Development
**Boss**: **Heartbleed** 💔
- **Reasoning**: Vulnerability-focused, dev environment theme
- **Educational Value**: Teaches secure coding and patching
- **Difficulty**: Easy-Medium - memory leak mechanic

### Level 3: Test/QA
**Boss**: **Sandworm** 🪱
- **Reasoning**: Testing theme, destructive testing analogy
- **Educational Value**: Supply chain and patching
- **Difficulty**: Medium - burrowing mechanic requires strategy

### Level 4: Staging
**Boss**: **Volt Typhoon** ⚡
- **Reasoning**: Pre-production, critical infrastructure theme
- **Educational Value**: Living-off-the-land, credential monitoring
- **Difficulty**: Medium-Hard - lightning mechanics

### Level 5: Production Data
**Boss**: **ALPHV/BlackCat** 🐱
- **Reasoning**: Ransomware targets production, 9 lives fits challenge
- **Educational Value**: Ransomware prevention, backup strategy
- **Difficulty**: Hard - 9 lives requires persistence

### Level 6: Production
**Boss**: **Midnight Blizzard** 🐻‍❄️
- **Reasoning**: Sophisticated APT, OAuth tokens, highest stakes
- **Educational Value**: Nation-state threats, supply chain
- **Difficulty**: Hard - visibility reduction mechanic

### Level 7: Organization (Final Boss)
**Boss**: **Scattered Spider** 🕷️
- **Reasoning**: Most identity-focused attack, swarm finale
- **Educational Value**: Identity theft, MFA, JIT access (core theme!)
- **Difficulty**: Very Hard - Must defeat 5 separate targets
- **Perfect Thematic Conclusion**: The game is about identity security, and Scattered Spider is THE identity attack

---

## Dialogue System Design

### Dialogue Box Specifications

**Visual Design**:
- **Style**: Retro Game Boy aesthetic (matching congratulations messages)
- **Size**: Full-width banner at top of screen, 150px tall
- **Background**: White rounded rectangle with black border (3px)
- **Font**: Pixelated retro font (8-bit style)
- **Colors**: Black text on white, emoji-style boss icon
- **Animation**: Slide down from top when triggered

**Content Structure**:
```
[BOSS ICON] [BOSS NAME] [BOSS ICON]

[Brief description of the attack/group - 1-2 sentences]

HOW THEY ATTACKED:
• [Bullet point 1]
• [Bullet point 2]
• [Bullet point 3-5]

VICTIMS/IMPACT: [Notable incidents]

HOW IT COULD HAVE BEEN PREVENTED:
✓ [Prevention 1]
✓ [Prevention 2]
✓ [Prevention 3-5]
✓ Cloud Permissions Firewall [specific use case]

BOSS MECHANIC: [Special attack description]

Press ENTER to begin battle...
```

### Dialogue Trigger Points

1. **When**: All regular zombies eliminated in level
2. **Action**:
   - Pause game
   - Display dialogue box with boss information
   - Play dramatic sound effect (optional)
3. **Dismissal**: Player presses ENTER
4. **After Dismissal**:
   - Remove dialogue box
   - Spawn boss at center of level
   - Play boss battle music (if implemented)
   - Resume game in BOSS_BATTLE state

### Educational Goals

Each dialogue should:
- ✅ Explain the real-world attack in simple terms
- ✅ Connect to identity/cloud security where possible
- ✅ Provide actionable prevention advice
- ✅ Reference the Cloud Permissions Firewall naturally
- ✅ Make cybersecurity concepts accessible and memorable
- ✅ Reinforce the game's educational mission

---

## Boss Sprite Design Concepts

### Scattered Spider 🕷️
```
Mini-Spider Sprite (24x24px):
- Black body with 8 legs
- Red eyes (2px each)
- Simple 8-bit spider silhouette
- 5 different color variants (black, red, green, blue, purple)
```

### ALPHV/BlackCat 🐱
```
Boss Sprite (120x120px):
- Black cat silhouette
- Glowing green/yellow eyes
- Ransomware aesthetic: binary code pattern on body
- Tail swishing animation (2-3 frames)
```

### Midnight Blizzard 🐻‍❄️
```
Boss Sprite (120x120px):
- Polar bear standing upright
- White/light blue coloring
- Ice/snow particle effects
- Russian ushanka hat (optional easter egg)
```

### Volt Typhoon ⚡
```
Boss Sprite (120x120px):
- Cloud/storm entity (no solid body)
- Electric yellow/blue colors
- Lightning bolt emanating from core
- Flowing/morphing animation
```

### Sandworm 🪱
```
Boss Sprite (variable size):
- Segmented worm body (5-7 segments)
- Metallic/industrial texture
- Drill-like head
- Brown/rust coloring
```

### Heartbleed 💔
```
Boss Sprite (120x120px):
- Broken heart shape (two halves)
- Red with dark "blood" drips
- Glitch effect (scanlines, corruption)
- Pulsing animation
```

### WannaCry 😭
```
Boss Sprite (120x120px):
- Large crying emoji face
- Lock symbol on forehead
- Blue-tinted tears
- Padlock chain wrapping around
```

---

## Technical Implementation Notes

### Required Changes to Existing System

**Files to Modify**:
1. `src/boss.py` - Update Boss class to support custom mechanics
2. `src/game_engine.py` - Integrate dialogue system before boss spawn
3. `src/renderer.py` - Add dialogue box rendering
4. `src/models.py` - Add BossType enum, dialogue data structures

**New Files to Create**:
1. `src/boss_dialogue.py` - Centralized dialogue content and management
2. `src/boss_mechanics.py` - Custom mechanics for each boss type

### Boss Mechanic Implementation

**Scattered Spider (Swarm)**:
```python
class ScatteredSpiderBoss:
    def __init__(self):
        self.spiders = []
        for i in range(5):
            spider = MiniSpider(
                position=get_spawn_position(i),
                health=30,
                movement_type=['fast', 'slow', 'zigzag', 'jumping', 'teleport'][i]
            )
            self.spiders.append(spider)

    def is_defeated(self):
        return all(spider.is_dead for spider in self.spiders)
```

**BlackCat (9 Lives)**:
```python
class BlackCatBoss:
    def __init__(self):
        self.lives_remaining = 9
        self.health = 150
        self.respawn_timer = 0

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0 and self.lives_remaining > 0:
            self.lives_remaining -= 1
            self.respawn()
```

**Midnight Blizzard (Visibility)**:
```python
class MidnightBlizzardBoss:
    def __init__(self):
        self.blizzard_active = False
        self.blizzard_timer = 0

    def update(self, delta_time):
        self.blizzard_timer += delta_time
        if self.blizzard_timer > 10.0:  # Every 10 seconds
            self.trigger_blizzard()

    def trigger_blizzard(self):
        # Apply white overlay to screen for 5 seconds
        # Reduce visibility, boss movement erratic
```

---

## Priority Boss Implementation Order

### Phase 1 (MVP):
1. **Scattered Spider** - Signature boss, core identity theme
2. **BlackCat** - Unique 9-lives mechanic, good contrast
3. **Dialogue System** - Essential for educational value

### Phase 2:
4. **Midnight Blizzard** - Adds variety with visibility mechanic
5. **Sandworm** - Burrowing adds vertical gameplay

### Phase 3:
6. **Volt Typhoon** - Polish with lightning effects
7. **Heartbleed** - Memory leak projectile system
8. **WannaCry** - Copying mechanic refinement

---

## Success Criteria

- ✅ 7 unique bosses themed after real cyber attacks
- ✅ Each boss has educational dialogue with facts and prevention
- ✅ Boss mechanics reflect attack characteristics
- ✅ Scattered Spider uses swarm mechanic (5 spiders)
- ✅ Strong connection to identity/cloud security theme
- ✅ Dialogue integrates Cloud Permissions Firewall naturally
- ✅ 8-bit retro aesthetic maintained in sprites and UI
- ✅ Engaging and memorable cybersecurity education

---

## References

**Attack Research Sources**:
- MITRE ATT&CK Framework
- CISA Cybersecurity Advisories
- CrowdStrike Threat Intelligence
- Mandiant APT Reports
- Cybersecurity news archives (2014-2024)

**Identity-Focused Attacks**:
- Scattered Spider: Okta breach analysis, MGM incident reports
- BlackCat: Ransomware credential usage analysis
- Midnight Blizzard: SolarWinds post-mortem, Microsoft OAuth breach
- Volt Typhoon: CISA critical infrastructure advisory

---

## Next Steps

1. Review and approve boss designs
2. Prioritize implementation order
3. Create detailed sprite mockups
4. Implement dialogue system infrastructure
5. Build Scattered Spider (swarm) boss first
6. Iterate based on gameplay testing
7. Add remaining bosses in priority order
