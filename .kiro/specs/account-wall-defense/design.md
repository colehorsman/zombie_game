# Account Wall Defense System - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Level/Account                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Account Walls                      │   │
│  │  health: 100%  ████████████████████████████████████ │   │
│  │                                                      │   │
│  │   [Player]     [Zombies]     [Third Parties]        │   │
│  │      👤           🧟🧟🧟         👾 → attacks wall   │   │
│  │                               🛡️ → protected        │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↓ if health = 0                     │
│                    GAME OVER: Account Breached!             │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### AccountWall Class

```python
@dataclass
class AccountWall:
    """Represents the defensive walls of an AWS account."""

    max_health: int = 100
    current_health: int = 100
    damage_rate_per_second: float = 2.0  # Base damage per active third party

    # Visual state
    damage_level: int = 0  # 0=healthy, 1=damaged, 2=critical, 3=breached

    # Warning thresholds
    WARNING_THRESHOLD = 50  # Yellow warning
    CRITICAL_THRESHOLD = 25  # Red warning

    def take_damage(self, amount: float) -> bool:
        """Apply damage to wall. Returns True if wall is breached."""
        self.current_health = max(0, self.current_health - amount)
        self._update_damage_level()
        return self.current_health <= 0

    def _update_damage_level(self):
        """Update visual damage level based on health."""
        if self.current_health <= 0:
            self.damage_level = 3  # Breached
        elif self.current_health <= self.CRITICAL_THRESHOLD:
            self.damage_level = 2  # Critical
        elif self.current_health <= self.WARNING_THRESHOLD:
            self.damage_level = 1  # Damaged
        else:
            self.damage_level = 0  # Healthy

    @property
    def health_percentage(self) -> float:
        return (self.current_health / self.max_health) * 100

    @property
    def is_breached(self) -> bool:
        return self.current_health <= 0
```

### ThirdParty Updates

```python
# Add to ThirdParty class
class ThirdParty:
    # ... existing fields ...

    # New fields for wall attack
    wall_damage_rate: float = 2.0  # Damage per second to walls
    is_attacking_wall: bool = True  # False if blocked or protected

    def get_wall_damage(self, delta_time: float) -> float:
        """Calculate damage to apply to wall this frame."""
        if self.is_blocked or self.is_protected or self.is_hidden:
            return 0.0
        return self.wall_damage_rate * delta_time
```

### GameState Updates

```python
# Add to GameState
class GameState:
    # ... existing fields ...

    # New field for wall defense
    account_wall: Optional[AccountWall] = None
```

## Game Loop Integration

### Wall Damage Update (in game_engine.py)

```python
def _update_wall_damage(self, delta_time: float):
    """Update wall health based on active third parties."""
    if not self.game_state.account_wall:
        return

    total_damage = 0.0
    attacking_parties = []

    for third_party in self.third_parties:
        damage = third_party.get_wall_damage(delta_time)
        if damage > 0:
            total_damage += damage
            attacking_parties.append(third_party)

    if total_damage > 0:
        is_breached = self.game_state.account_wall.take_damage(total_damage)

        if is_breached:
            self._trigger_wall_breach_game_over(attacking_parties)
```

### Wall Breach Game Over

```python
def _trigger_wall_breach_game_over(self, attacking_parties: List[ThirdParty]):
    """Handle game over when wall is breached."""
    party_names = [p.identity_name for p in attacking_parties[:3]]

    message = (
        "🔓 ACCOUNT BREACHED!\n\n"
        "Third parties have compromised your account!\n\n"
        f"Attackers: {', '.join(party_names)}\n\n"
        "All data is now exposed!\n"
        "All permissions are compromised!\n\n"
        "▶ Retry Level\n"
        "  Return to Lobby"
    )

    self._show_game_over_screen(message, breach_type="wall")
```

## Visual Design

### Wall Health HUD

```
┌──────────────────────────────────────┐
│ ACCOUNT WALL                         │
│ ████████████████████░░░░░░░░░░  75%  │
└──────────────────────────────────────┘

Health States:
- 100-51%: Green bar, no visual damage
- 50-26%:  Yellow bar, cracks appear on level border
- 25-1%:   Red bar, heavy cracks, warning pulse
- 0%:      Breach animation, game over
```

### Wall Damage Visuals

```python
def _render_wall_damage(self, surface: pygame.Surface):
    """Render wall damage effects on level border."""
    wall = self.game_state.account_wall
    if not wall:
        return

    # Draw cracks based on damage level
    if wall.damage_level >= 1:  # Damaged
        self._draw_wall_cracks(surface, intensity=1)

    if wall.damage_level >= 2:  # Critical
        self._draw_wall_cracks(surface, intensity=2)
        self._draw_warning_pulse(surface)

    if wall.damage_level >= 3:  # Breached
        self._draw_breach_effect(surface)
```

### Third Party Attack Indicator

```python
def _render_third_party_attack(self, third_party: ThirdParty, surface: pygame.Surface):
    """Show visual indicator that third party is attacking wall."""
    if third_party.is_blocked or third_party.is_protected:
        return

    # Draw attack line from third party to nearest wall
    # Pulsing red line or particle effect
    self._draw_attack_beam(
        start=third_party.position,
        end=self._get_nearest_wall_point(third_party.position),
        color=RED,
        pulse=True
    )
```

## Balancing

### Damage Rates

| Third Party Type | Damage/Second | Time to Breach (solo) |
|------------------|---------------|----------------------|
| Standard         | 2.0           | 50 seconds           |
| Aggressive       | 4.0           | 25 seconds           |
| Stealthy         | 1.0           | 100 seconds          |

### Multiple Third Parties

With multiple active third parties, damage stacks:
- 1 third party: 50 seconds to breach
- 2 third parties: 25 seconds to breach
- 3 third parties: ~17 seconds to breach
- 5 third parties: 10 seconds to breach

This creates urgency to block multiple threats quickly.

### Protected Third Parties

- **Sonrai**: Always protected (purple shield), 0 damage
- **Exempted**: Protected by policy (purple shield), 0 damage
- **Blocked**: Player blocked them, 0 damage

## State Transitions

```
Level Start
    │
    ▼
┌─────────────────┐
│ Wall: 100%      │◄──────────────────────┐
│ Status: Healthy │                       │
└────────┬────────┘                       │
         │ Third parties active           │
         ▼                                │
┌─────────────────┐                       │
│ Wall: 50-99%    │  Player blocks        │
│ Status: Damaged │──third parties────────┤
└────────┬────────┘                       │
         │ More damage                    │
         ▼                                │
┌─────────────────┐                       │
│ Wall: 1-49%     │  Player blocks        │
│ Status: Critical│──all third parties────┘
└────────┬────────┘
         │ Wall reaches 0%
         ▼
┌─────────────────┐
│ Wall: 0%        │
│ Status: BREACHED│──► GAME OVER
└─────────────────┘
```

## Integration Points

### Level Initialization

```python
def _enter_level(self, level: Level):
    """Initialize level with wall defense."""
    # ... existing code ...

    # Initialize account wall
    self.game_state.account_wall = AccountWall(
        max_health=100,
        current_health=100
    )
```

### Level Exit

```python
def _return_to_lobby(self):
    """Clean up wall state when leaving level."""
    # ... existing code ...

    # Clear wall state
    self.game_state.account_wall = None
```

### Third Party Blocking

```python
def _block_third_party(self, third_party: ThirdParty):
    """Block third party - stops wall damage."""
    # ... existing API call ...

    # Stop wall attack
    third_party.is_blocked = True
    third_party.is_attacking_wall = False
```

## Testing Strategy

### Unit Tests
- AccountWall damage calculation
- Damage level transitions
- Protected third party filtering
- Breach detection

### Integration Tests
- Wall damage accumulation over time
- Game over trigger on breach
- Third party blocking stops damage
- Protected parties don't damage

### Manual Tests
- Visual damage progression
- HUD health bar accuracy
- Game over screen displays correctly
- Retry/lobby options work
