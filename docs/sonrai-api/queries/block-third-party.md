# Block Third Party Mutation

Blocks third-party access to AWS accounts using the Cloud Permissions Firewall.

## Mutation Name

`SetThirdPartyControlMode`

## Purpose

Block or allow third-party access to AWS resources. In the game, this is called when you "eliminate" a third-party entity.

## GraphQL Mutation

```graphql
mutation BlockThirdParty($input: SetThirdPartyControlModeInput!) {
    SetThirdPartyControlMode(value: $input) {
        success
        errorMessage
    }
}
```

## Variables

```graphql
{
  "input": {
    "thirdPartyId": "tp-uuid-123",
    "mode": "BLOCK",
    "scope": "aws/123456789"
  }
}
```

## Response Structure

### Success

```json
{
  "data": {
    "SetThirdPartyControlMode": {
      "success": true,
      "errorMessage": null
    }
  }
}
```

### Failure

```json
{
  "data": {
    "SetThirdPartyControlMode": {
      "success": false,
      "errorMessage": "Third party not found or already blocked"
    }
  }
}
```

## Input Fields

- `thirdPartyId` (String) - UUID of the third party to block
- `mode` (String) - Control mode: "BLOCK", "ALLOW", or "MONITOR"
- `scope` (String) - AWS account scope (e.g., "aws/123456789")

## Control Modes

- `BLOCK` - Completely block third-party access
- `ALLOW` - Allow third-party access
- `MONITOR` - Monitor but don't block (audit mode)

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `block_third_party(third_party_id, third_party_name)`

## Notes

- Requires the third party UUID (obtained from `fetch_third_parties_by_account`)
- Blocking is applied at the account level
- Can be reversed by setting mode to "ALLOW"
- Game always uses "BLOCK" mode

## Game Flow

1. Player shoots third party 10 times (health reaches 0)
2. Game pauses and shows congratulations message
3. Player presses ENTER to dismiss message
4. `block_third_party()` is called
5. If successful: third party is removed from game
6. If failed: third party is restored (not blocked)

## Error Handling

The game handles failures gracefully:
- Logs error message
- Shows error to player in UI
- Restores third party's `is_blocking` flag to `false`
- Player can try again

## Protected Third Parties

**Important**: The "Sonrai" or "Sonrai Security" third party is marked as protected in the game and cannot be blocked (it's your security platform!). It displays a purple shield and projectiles pass through it.

## Related Types

- `SetThirdPartyControlModeInput` - Input type
- `SetThirdPartyControlModeResponse` - Response type
- `ThirdPartyAccessMode` - Enum for control modes

## Cloud Permissions Firewall

This mutation leverages Sonrai's Cloud Permissions Firewall (CPF) to:
- Block third-party IAM roles and access
- Prevent external service access to AWS resources
- Maintain audit trail of block action
- Can be reversed if needed
