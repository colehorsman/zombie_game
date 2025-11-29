# Account Wall Defense System - Requirements

## Overview

Third-party entities attack account walls instead of the player directly. If walls are breached, the account is compromised and it's game over. This creates strategic gameplay where players must prioritize blocking third-party access to protect their cloud accounts.

## Problem Statement

Currently, third-party entities pose no threat to the player. This misses an educational opportunity to teach that unmanaged third-party access leads to account compromise, not personal harm.

## User Stories

### US-1: Account Wall Health
**As a** player
**I want** to see the health of my account's walls
**So that** I understand the urgency of blocking third-party access

**Acceptance Criteria:**
- [ ] Each level has a wall health value (starts at 100%)
- [ ] Wall health is displayed visually in the HUD
- [ ] Wall health decreases when third parties are active
- [ ] Wall health does NOT regenerate automatically

### US-2: Third Party Wall Attack
**As a** player
**I want** third parties to attack the account walls over time
**So that** I have urgency to block them

**Acceptance Criteria:**
- [ ] Active (unblocked) third parties drain wall health
- [ ] Drain rate is visible/perceivable (not instant)
- [ ] Different third parties may have different drain rates
- [ ] Blocked third parties stop draining immediately
- [ ] Sonrai/exempted third parties do NOT drain walls

### US-3: Visual Wall Damage
**As a** player
**I want** to see visual feedback of wall damage
**So that** I understand the threat level

**Acceptance Criteria:**
- [ ] Walls show progressive damage (cracks, color change)
- [ ] Warning indicators when wall health is low (< 50%, < 25%)
- [ ] Audio/visual alert when wall is critically damaged
- [ ] Clear visual distinction between healthy and damaged walls

### US-4: Account Breach Game Over
**As a** player
**I want** the game to end if walls are fully breached
**So that** I understand the consequence of ignoring third-party threats

**Acceptance Criteria:**
- [ ] Wall health reaching 0% triggers game over
- [ ] Game over message explains "Account Breached!"
- [ ] Shows which third parties caused the breach
- [ ] Options: Retry Level, Return to Lobby

### US-5: Protected Third Parties
**As a** player
**I want** Sonrai and exempted third parties to be safe
**So that** I learn which third parties are trusted

**Acceptance Criteria:**
- [ ] Sonrai third parties have purple shields
- [ ] Exempted third parties have purple shields
- [ ] Protected third parties do NOT attack walls
- [ ] Visual distinction between threats and trusted parties

## Educational Value

This feature teaches:
1. **Third-party risk** - Unmanaged access compromises accounts
2. **Prioritization** - Some threats are more urgent than others
3. **Trust boundaries** - Sonrai/exempted parties are vetted and safe
4. **Proactive security** - Block threats before damage occurs

## Non-Functional Requirements

### Performance
- Wall health updates should not impact 60 FPS
- Visual effects should be lightweight

### UX
- Wall health should be immediately understandable
- Damage progression should feel fair (not instant death)
- Player should have time to react and prioritize

## Out of Scope (Future)

- Wall repair mechanics (powerups that restore wall health)
- Different wall types per account
- Third parties that can be converted to allies
- Multiplayer wall defense
