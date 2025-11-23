# Product Overview

Sonrai Zombie Blaster is a retro-style video game that gamifies cloud security remediation. The game visualizes unused AWS identities as zombies and allows players to "eliminate" them by triggering real quarantine actions through the Sonrai Security API.

## Core Concept

- Each zombie represents a real unused AWS identity from Sonrai
- Eliminating zombies triggers actual quarantine requests via Sonrai API
- Third-party entities can be blocked to improve security posture
- Protected entities (Sonrai + exempted identities) display purple shields and are invulnerable

## Game Modes

**v2 - Hybrid Mode** (current branch):
- **Lobby Mode**: Top-down exploration of a central hub with doors to AWS accounts
- **Level Mode**: Mario-style side-scrolling platformer gameplay inside each account
- Linear progression system with unlockable levels
- Sandbox account always available for learning

## Key Features

- Dual-mode gameplay (lobby + platformer)
- Real-time integration with Sonrai Security API
- Damage system with health points
- Score tracking with multiplier mechanics
- Power-up collectibles in platformer levels
- Approval system for production environments
- Save/load game state with autosave
- Cheat codes for testing (UNLOCK, SKIP)
- Controller support (8-bit style)
