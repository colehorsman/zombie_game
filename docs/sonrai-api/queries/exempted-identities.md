# Exempted Identities Query

Fetches exempted/protected identities that should not be quarantined.

## Query Name

`AppliedExemptedIdentities`

## Purpose

Retrieve identities that have been explicitly exempted from quarantine. These appear as protected entities with purple shields in the game.

## GraphQL Query

```graphql
query GetExemptedIdentities($filters: AppliedExemptedIdentitiesFilter!) {
    AppliedExemptedIdentities(where: $filters) {
        count
        items {
            id
            identity
            scope
            scopeFriendlyName
            approvedBy
            approvedAt
            isCoreExemption
        }
    }
}
```

## Variables

```json
{
  "filters": {
    "scope": {
      "value": "aws/123456789",
      "op": "EQ"
    }
  }
}
```

## Response Structure

```json
{
  "data": {
    "AppliedExemptedIdentities": {
      "count": 2,
      "items": [
        {
          "id": "exemption-id-123",
          "identity": "srn:aws:iam::123456789:user/protected-user",
          "scope": "aws/123456789",
          "scopeFriendlyName": "Production Account",
          "approvedBy": "admin@company.com",
          "approvedAt": "2024-01-15T10:30:00Z",
          "isCoreExemption": false
        }
      ]
    }
  }
}
```

## Available Fields

The `AppliedExemptedIdentity` type includes:

- `id` (String) - Unique exemption ID
- `identity` (String) - Identity SRN
- `scope` (String) - Scope path (e.g., "aws/123456789")
- `scopeFriendlyName` (String) - Human-readable scope name
- `approvedBy` (String) - Who approved the exemption
- `approvedAt` (DateTime) - When it was approved
- `inTransaction` (Boolean) - Whether in a pending transaction
- `isCoreExemption` (Boolean) - Whether it's a core exemption
- `isSso` (Boolean) - SSO exemption flag
- `serviceProtect` (Boolean) - Service protection flag
- `serviceBlock` (Boolean) - Service block flag
- `quarantine` (Boolean) - Quarantine exemption flag
- `regionBlock` (Boolean) - Region block flag
- `jit` (Boolean) - JIT exemption flag
- `tamperProtect` (Boolean) - Tamper protection flag
- `icon` (IdentityIcon) - Icon information

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `fetch_exemptions(account)`

## Notes

- Filters by scope to get exemptions for a specific AWS account
- Uses `EQ` operator for exact scope matching
- Returns empty list on error (graceful degradation)
- Includes retry logic with exponential backoff

## Related Types

- `AppliedExemptedIdentity` - Response item type
- `AppliedExemptedIdentitiesFilter` - Filter input type
- `AppliedExemptedIdentitiesResponse` - Response wrapper type

## Game Integration

Protected entities in the game:
1. Exempted identities from this query
2. Sonrai third-party entity (hardcoded protection)

Both display purple shields and are invulnerable to projectiles.
