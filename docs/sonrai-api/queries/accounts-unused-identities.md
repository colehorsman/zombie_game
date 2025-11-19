# Accounts with Unused Identities Query

Fetches a summary of all AWS accounts with their unused identity counts.

## Query Name

`AccountsWithUnusedIdentities`

## Purpose

Get a high-level overview of which AWS accounts have unused identities and how many. Used for level selection and progression in the game.

## GraphQL Query

```graphql
query GetAccountsWithUnusedIdentities {
    AccountsWithUnusedIdentities {
        account
        unusedCount
        environmentType
    }
}
```

## Variables

None required.

## Response Structure

```json
{
  "data": {
    "AccountsWithUnusedIdentities": [
      {
        "account": "577945324761",
        "unusedCount": 520,
        "environmentType": "production"
      },
      {
        "account": "613056517323",
        "unusedCount": 48,
        "environmentType": "development"
      },
      {
        "account": "240768036625",
        "unusedCount": 1,
        "environmentType": "sandbox"
      }
    ]
  }
}
```

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `fetch_accounts_with_unused_identities()`

## Notes

- Returns all accounts in the organization with unused identities
- Includes count of unused identities per account
- Environment type helps with level ordering (sandbox → dev → staging → prod)
- Used to populate the multi-level progression system

## Game Integration

This query is used to:
1. Determine how many levels the game has
2. Order levels by environment type (sandbox first, production last)
3. Show zombie count per level in the UI
4. Load the appropriate account's zombies for each level

## Related Types

- `AccountSummary` - Response item type
- `AccountsWithUnusedIdentitiesResponse` - Response wrapper

## CSV Alternative

The game also supports loading account data from `assets/aws_accounts.csv` as an alternative to this API call.
