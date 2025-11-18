# Sonrai API Integration Guide

## Current Status

The game is currently using **mock data** to generate test-user-1 through test-user-500 zombies.

To integrate with real Sonrai unused identities, you need to:

1. **Find the correct GraphQL query** for unused identities in Sonrai
2. **Find the correct GraphQL mutation** for quarantining/deleting identities
3. **Update the API client** with the correct queries

## What We Need

### 1. Query for Unused Identities

We need the GraphQL query that returns unused AWS identities. It might look something like:

```graphql
query {
  UnusedIdentities(limit: 500) {
    items {
      srn
      name
      resourceType
      # other fields...
    }
  }
}
```

**Location to update:** `src/sonrai_client.py` in the `fetch_unused_identities()` method

### 2. Mutation for Quarantining

We need the GraphQL mutation to quarantine/delete an identity:

```graphql
mutation QuarantineIdentity($srn: ID!) {
  QuarantineIdentity(srn: $srn) {
    success
    message
  }
}
```

**Location to update:** `src/sonrai_client.py` in the `quarantine_identity()` method

## How to Find the Correct Queries

### Option 1: Sonrai Documentation
Check the Sonrai API documentation for:
- Unused identity queries
- Quarantine/remediation mutations

### Option 2: Sonrai UI Network Tab
1. Open Sonrai UI in your browser
2. Open Developer Tools (F12) → Network tab
3. Navigate to unused identities view
4. Look for GraphQL requests
5. Copy the query/mutation from the request payload

### Option 3: Ask Sonrai Support
Contact Sonrai support for the correct GraphQL schema for:
- Querying unused identities
- Quarantining identities

## Current Mock Implementation

The game currently generates mock identities in `src/sonrai_client.py`:

```python
for i in range(1, 501):
    identity = UnusedIdentity(
        identity_id=f"srn:{self.org_id}::User/test-user-{i}",
        identity_name=f"test-user-{i}",
        identity_type="User",
        last_used=None,
        risk_score=0.0
    )
```

## Testing the Game

You can test the game with mock data right now:

```bash
python3 src/main.py
```

The game will work with 500 mock zombies named test-user-1 through test-user-500.

## Once You Have the Correct Queries

1. Update `src/sonrai_client.py` with the real queries
2. The game will automatically use real Sonrai data
3. Quarantine actions will affect real identities in your Sonrai account

**⚠️ Warning:** Once connected to real data, eliminating zombies will actually quarantine identities in Sonrai!
