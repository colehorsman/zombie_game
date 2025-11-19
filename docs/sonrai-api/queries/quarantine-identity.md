# Quarantine Identity Mutation

Quarantines an unused IAM identity using the Cloud Permissions Firewall.

## Mutation Name

`ChangeQuarantineStatus`

## Purpose

Apply quarantine to an unused identity, preventing it from being used. This is the core remediation action in the game - when you "eliminate" a zombie, this mutation is called.

## GraphQL Mutation

```graphql
mutation QuarantineIdentity($input: ChangeQuarantineStatusInput!) {
    ChangeQuarantineStatus(value: $input) {
        success
        errorMessage
        transactionId
    }
}
```

## Variables

```json
{
  "input": {
    "identities": [
      "srn:aws:iam::123456789:user/test-user-1"
    ],
    "quarantine": true,
    "scope": "aws/123456789"
  }
}
```

## Response Structure

### Success

```json
{
  "data": {
    "ChangeQuarantineStatus": {
      "success": true,
      "errorMessage": null,
      "transactionId": "txn-abc123"
    }
  }
}
```

### Failure

```json
{
  "data": {
    "ChangeQuarantineStatus": {
      "success": false,
      "errorMessage": "Identity not found or already quarantined",
      "transactionId": null
    }
  }
}
```

## Input Fields

- `identities` (Array[String]) - List of identity SRNs to quarantine
- `quarantine` (Boolean) - `true` to quarantine, `false` to un-quarantine
- `scope` (String) - AWS account scope (e.g., "aws/123456789")

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `quarantine_identity(identity_id, identity_name, account, scope, root_scope)`

## Notes

- Can quarantine multiple identities in one call (game uses single identity per call)
- Returns `success: true` if quarantine was applied
- Returns `errorMessage` if operation failed
- `transactionId` can be used to track the quarantine operation
- Scope is automatically extracted from identity SRN if not provided

## Game Flow

1. Player shoots zombie 3 times (health reaches 0)
2. Game pauses and shows congratulations message
3. Player presses ENTER to dismiss message
4. `quarantine_identity()` is called
5. If successful: zombie is removed from game
6. If failed: zombie is restored (not quarantined)

## Error Handling

The game handles failures gracefully:
- Logs error message
- Shows error to player in UI
- Restores zombie's `is_quarantining` flag to `false`
- Player can try again

## Related Types

- `ChangeQuarantineStatusInput` - Input type
- `ChangeQuarantineStatusResponse` - Response type
- `QuarantineResult` - Wrapped result (used in game code)

## Cloud Permissions Firewall

This mutation leverages Sonrai's Cloud Permissions Firewall (CPF) to:
- Block the identity from performing any actions
- Prevent credential usage
- Maintain audit trail of quarantine action
