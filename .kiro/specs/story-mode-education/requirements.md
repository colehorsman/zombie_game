# Requirements Document

## Introduction

This feature enhances Story Mode with educational content that teaches players about cloud security concepts through comic book-style 8-bit dialogue bubbles (similar to Zelda). The goal is to make Story Mode a guided learning experience where players understand WHY they're eliminating zombies and WHAT happens when they do.

## Glossary

- **Story Mode**: The educational game mode in Sandbox account focused on teaching security concepts
- **Dialogue Bubble**: A comic book-style 8-bit text bubble that appears during gameplay to explain concepts
- **Zombie**: An unused IAM identity (User or Role) that hasn't been used for a specified period
- **Quarantine**: The action of disabling an unused identity via Sonrai's Cloud Permissions Firewall
- **Educational Trigger**: A gameplay event that triggers an educational dialogue (first kill, specific zombie type, etc.)
- **Identity Metadata**: Information about a zombie including name, type, days since login, and account

## Requirements

### Requirement 1: Dialogue Bubble System

**User Story:** As a player in Story Mode, I want to see comic book-style dialogue bubbles that explain security concepts, so that I learn while playing.

#### Acceptance Criteria

1. WHEN the player enters Story Mode for the first time THEN the System SHALL display a welcome dialogue bubble explaining the mission
2. WHEN a dialogue bubble is displayed THEN the System SHALL render it in an 8-bit comic book style with a pointed tail toward the relevant entity
3. WHEN a dialogue bubble is active THEN the System SHALL pause gameplay until the player dismisses it with the action button
4. WHEN multiple dialogue messages exist for a trigger THEN the System SHALL display them sequentially with page indicators
5. WHEN the player presses the action button on the final dialogue page THEN the System SHALL dismiss the bubble and resume gameplay

### Requirement 2: First Zombie Elimination Education

**User Story:** As a new player, I want to learn what happens when I eliminate my first zombie, so that I understand the real-world impact of my actions.

#### Acceptance Criteria

1. WHEN the player eliminates their first zombie in Story Mode THEN the System SHALL display an educational dialogue explaining quarantine
2. WHEN explaining quarantine THEN the System SHALL describe that the identity is being disabled via Cloud Permissions Firewall
3. WHEN the first zombie is eliminated THEN the System SHALL display the zombie's name and type in the educational message
4. WHEN the first zombie is eliminated THEN the System SHALL explain that this prevents the unused identity from being compromised
5. IF the player has already eliminated a zombie in a previous session THEN the System SHALL skip the first-kill education

### Requirement 3: Zombie Metadata Display

**User Story:** As a player, I want to see information about the zombies I eliminate, so that I understand what each identity represents.

#### Acceptance Criteria

1. WHEN a zombie is eliminated THEN the System SHALL display a brief info panel showing the identity name
2. WHEN displaying zombie info THEN the System SHALL show the identity type (User or Role)
3. WHEN displaying zombie info THEN the System SHALL show days since last login if available
4. WHEN the identity type is Role THEN the System SHALL explain that roles are used by services and applications
5. WHEN the identity type is User THEN the System SHALL explain that users are human accounts

### Requirement 4: Educational Progress Tracking

**User Story:** As a returning player, I want the game to remember what I've learned, so that I don't see the same tutorials repeatedly.

#### Acceptance Criteria

1. WHEN an educational trigger fires THEN the System SHALL check if the player has seen this education before
2. WHEN the player completes an educational sequence THEN the System SHALL persist this to the save file
3. WHEN loading a saved game THEN the System SHALL restore the player's educational progress
4. WHERE the player wants to replay tutorials THEN the System SHALL provide an option to reset educational progress
5. WHEN tracking educational progress THEN the System SHALL store completion status for each unique trigger type

### Requirement 5: Contextual Security Tips

**User Story:** As a player progressing through Story Mode, I want to receive contextual security tips at key moments, so that I build comprehensive security knowledge.

#### Acceptance Criteria

1. WHEN the player eliminates 5 zombies THEN the System SHALL display a tip about the importance of regular identity audits
2. WHEN the player encounters a Role-type zombie THEN the System SHALL explain service account security on first occurrence
3. WHEN the player encounters a User-type zombie THEN the System SHALL explain human identity lifecycle on first occurrence
4. WHEN the player completes a level THEN the System SHALL display a summary of security concepts learned
5. WHEN displaying tips THEN the System SHALL use varied messaging to maintain engagement

### Requirement 6: Permission Display via AWS API

**User Story:** As an advanced player, I want to see the permissions of identities I eliminate, so that I understand the risk they posed.

#### Acceptance Criteria

1. WHEN a zombie is eliminated THEN the System SHALL extract the AWS ARN from the Sonrai SRN
2. WHEN the ARN is available THEN the System SHALL query AWS IAM API for attached policies
3. WHEN policies are retrieved THEN the System SHALL display a simplified permission summary in the dialogue
4. WHEN displaying permissions THEN the System SHALL highlight high-risk permissions (e.g., AdministratorAccess, IAMFullAccess)
5. IF the AWS API call fails THEN the System SHALL gracefully degrade to showing only basic identity info
6. WHEN displaying User permissions THEN the System SHALL show both inline and attached managed policies
7. WHEN displaying Role permissions THEN the System SHALL show the trust policy and attached policies

## Technical Notes

**ARN Extraction from SRN:**
- Sonrai SRN format: `srn:aws:iam::577945324761/User/User/test-user-1`
- AWS ARN format: `arn:aws:iam::577945324761:user/test-user-1`
- Conversion is straightforward string manipulation

**AWS IAM API Calls Needed:**
- For Users: `iam.list_attached_user_policies()`, `iam.list_user_policies()` (inline)
- For Roles: `iam.list_attached_role_policies()`, `iam.list_role_policies()` (inline), `iam.get_role()` (trust policy)

**High-Risk Policies to Highlight:**
- AdministratorAccess
- IAMFullAccess
- PowerUserAccess
- Any policy with `*` actions on `*` resources

**Performance Consideration:**
- AWS API calls should be async/cached to avoid blocking gameplay
- Consider fetching on first elimination, caching for subsequent displays
- Timeout after 2 seconds, show basic info if slow
