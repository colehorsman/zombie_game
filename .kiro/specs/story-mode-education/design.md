# Design Document: Story Mode Educational Enhancements

## Overview

This feature adds an educational layer to Story Mode through comic book-style dialogue bubbles that teach players about cloud security concepts. The system triggers contextual education at key gameplay moments (first kill, milestone achievements, identity type encounters) and displays real identity metadata to make learning tangible.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Game Engine                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Story Mode     │  │  Education      │  │  Dialogue       │  │
│  │  Controller     │──│  Manager        │──│  Renderer       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                   │                    │             │
│           ▼                   ▼                    ▼             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Event Bus      │  │  Progress       │  │  AWS IAM        │  │
│  │  (Triggers)     │  │  Tracker        │  │  Client         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                               │                    │             │
│                               ▼                    ▼             │
│                       ┌─────────────────┐  ┌─────────────────┐  │
│                       │  Save Manager   │  │  Sonrai Client  │  │
│                       └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. EducationManager

Manages educational triggers, progress tracking, and content delivery.

```python
class EducationManager:
    def __init__(self, save_manager: SaveManager):
        self.progress = EducationalProgress()
        self.save_manager = save_manager
        self.active_dialogue = None

    def check_trigger(self, trigger_type: str, context: dict) -> Optional[DialogueSequence]:
        """Check if an educational trigger should fire."""

    def mark_completed(self, trigger_type: str) -> None:
        """Mark an educational sequence as completed."""

    def reset_progress(self) -> None:
        """Reset all educational progress for replay."""

    def load_progress(self, save_data: dict) -> None:
        """Load educational progress from save file."""

    def save_progress(self) -> dict:
        """Export educational progress for saving."""
```

### 2. DialogueRenderer

Renders 8-bit comic book-style dialogue bubbles.

```python
class DialogueRenderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = load_8bit_font()

    def render_bubble(self, dialogue: DialogueMessage, target_pos: tuple) -> None:
        """Render a dialogue bubble pointing at target position."""

    def render_page_indicator(self, current: int, total: int) -> None:
        """Render page dots for multi-page dialogues."""

    def calculate_bubble_position(self, target_pos: tuple, text_size: tuple) -> tuple:
        """Calculate optimal bubble position to avoid screen edges."""
```

### 3. DialogueSequence

Represents a multi-page educational dialogue.

```python
@dataclass
class DialogueMessage:
    text: str
    speaker: str = "SONRAI"  # Who is "speaking"
    highlight_words: List[str] = field(default_factory=list)  # Words to emphasize

@dataclass
class DialogueSequence:
    trigger_type: str
    messages: List[DialogueMessage]
    current_page: int = 0

    def next_page(self) -> bool:
        """Advance to next page. Returns False if at end."""

    def is_complete(self) -> bool:
        """Check if all pages have been viewed."""
```

### 4. EducationalProgress

Tracks which educational content the player has seen.

```python
@dataclass
class EducationalProgress:
    completed_triggers: Set[str] = field(default_factory=set)
    zombies_eliminated: int = 0
    first_role_seen: bool = False
    first_user_seen: bool = False

    def has_seen(self, trigger_type: str) -> bool:
        """Check if player has seen this education."""

    def to_dict(self) -> dict:
        """Serialize for save file."""

    @classmethod
    def from_dict(cls, data: dict) -> 'EducationalProgress':
        """Deserialize from save file."""
```

### 5. AWSIAMClient

Fetches permission data from AWS IAM API.

```python
class AWSIAMClient:
    def __init__(self, session: boto3.Session = None):
        self.iam = session.client('iam') if session else boto3.client('iam')
        self.cache = {}  # Cache policy lookups

    def get_user_policies(self, user_name: str) -> PermissionSummary:
        """Fetch attached and inline policies for a user."""

    def get_role_policies(self, role_name: str) -> PermissionSummary:
        """Fetch attached policies and trust policy for a role."""

    def is_high_risk(self, policy_name: str) -> bool:
        """Check if a policy is considered high-risk."""

    @staticmethod
    def srn_to_arn(srn: str) -> str:
        """Convert Sonrai SRN to AWS ARN format."""
```

### 6. PermissionSummary

Represents simplified permission information.

```python
@dataclass
class PermissionSummary:
    identity_name: str
    identity_type: str  # "User" or "Role"
    attached_policies: List[str]
    inline_policies: List[str]
    high_risk_policies: List[str]
    trust_policy: Optional[str] = None  # For roles only
    fetch_error: Optional[str] = None  # If API call failed
```

## Data Models

### Educational Trigger Types

```python
class TriggerType(Enum):
    STORY_MODE_WELCOME = "story_mode_welcome"
    FIRST_ZOMBIE_KILL = "first_zombie_kill"
    FIRST_ROLE_ENCOUNTER = "first_role_encounter"
    FIRST_USER_ENCOUNTER = "first_user_encounter"
    MILESTONE_5_KILLS = "milestone_5_kills"
    MILESTONE_10_KILLS = "milestone_10_kills"
    LEVEL_COMPLETE = "level_complete"
```

### Educational Content Templates

```python
EDUCATION_CONTENT = {
    TriggerType.FIRST_ZOMBIE_KILL: [
        DialogueMessage(
            text="You just quarantined {zombie_name}!",
            highlight_words=["quarantined"]
        ),
        DialogueMessage(
            text="This {zombie_type} hasn't been used in {days} days.",
            highlight_words=["{zombie_type}"]
        ),
        DialogueMessage(
            text="Sonrai's Cloud Permissions Firewall has disabled this identity.",
            highlight_words=["Cloud Permissions Firewall"]
        ),
        DialogueMessage(
            text="Unused identities are security risks - attackers can compromise them!",
            highlight_words=["security risks"]
        ),
    ],
    # ... more content templates
}
```

### Save File Schema Extension

```python
# Added to existing save structure
{
    "educational_progress": {
        "completed_triggers": ["story_mode_welcome", "first_zombie_kill"],
        "zombies_eliminated": 15,
        "first_role_seen": True,
        "first_user_seen": True
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Dialogue Pause Behavior
*For any* active dialogue bubble, the game state SHALL be paused, and pressing the action button on the final page SHALL dismiss the dialogue and resume gameplay.
**Validates: Requirements 1.3, 1.5**

### Property 2: First Kill Education Trigger
*For any* player with no prior zombie eliminations in Story Mode, eliminating their first zombie SHALL trigger the quarantine education dialogue containing the zombie's name and type.
**Validates: Requirements 2.1, 2.3, 2.5**

### Property 3: Zombie Info Panel Completeness
*For any* eliminated zombie, the info panel SHALL display the identity name, type (User or Role), and days since last login when available.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Educational Progress Round-Trip
*For any* educational progress state, saving and then loading SHALL restore the exact same completion status for all trigger types.
**Validates: Requirements 4.2, 4.3**

### Property 5: Progress Tracking Independence
*For any* set of educational triggers, completing one trigger type SHALL NOT affect the completion status of other trigger types.
**Validates: Requirements 4.1, 4.5**

### Property 6: Milestone Trigger Accuracy
*For any* player reaching exactly 5 zombie eliminations, the identity audit tip SHALL be triggered exactly once.
**Validates: Requirements 5.1**

### Property 7: Type-Specific Education
*For any* first encounter with a Role-type zombie, the service account explanation SHALL trigger; *for any* first encounter with a User-type zombie, the human identity explanation SHALL trigger.
**Validates: Requirements 5.2, 5.3**

### Property 8: SRN to ARN Conversion
*For any* valid Sonrai SRN, converting to AWS ARN and back SHALL preserve the identity information (account, type, name).
**Validates: Requirements 6.1**

### Property 9: AWS Permission Retrieval
*For any* valid AWS ARN, the system SHALL either return a PermissionSummary with policy data OR gracefully degrade to basic identity info on failure.
**Validates: Requirements 6.2, 6.3, 6.5**

### Property 10: High-Risk Policy Detection
*For any* policy list containing AdministratorAccess or IAMFullAccess, those policies SHALL be flagged as high-risk in the summary.
**Validates: Requirements 6.4**

## Error Handling

### AWS API Failures
- Timeout after 2 seconds for AWS IAM calls
- Cache successful lookups to reduce API calls
- Show basic identity info (name, type, days) if permission fetch fails
- Log errors for debugging but don't interrupt gameplay

### Missing Data
- If `daysSinceLogin` is null, display "Unknown" in info panel
- If identity type cannot be determined, default to "Identity"
- If dialogue content template is missing, skip that trigger

### Save/Load Errors
- If educational progress is corrupted, reset to defaults
- Log warning but don't prevent game from loading

## Testing Strategy

### Unit Tests
- DialogueSequence page navigation
- EducationalProgress serialization/deserialization
- SRN to ARN conversion for various identity types
- High-risk policy detection logic
- Trigger condition evaluation

### Property-Based Tests (Hypothesis)
- Round-trip testing for educational progress save/load
- SRN/ARN conversion preserves identity data
- Trigger independence (completing one doesn't affect others)
- Milestone triggers fire at exact thresholds

### Integration Tests
- Full dialogue flow from trigger to dismissal
- AWS IAM client with mocked responses
- Save manager integration with educational progress
- Game pause/resume during dialogue

### Manual Testing
- Visual verification of 8-bit dialogue bubble style
- Dialogue positioning near screen edges
- Multi-page dialogue flow with page indicators
- Permission display formatting
