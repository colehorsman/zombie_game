# Third Party Access Query

Fetches third-party access to AWS accounts.

## Query Name

`ThirdPartyAccessByAccount`

## Purpose

Retrieve information about third-party services (like Cloudflare, Datadog, etc.) that have access to AWS accounts. These appear as patrolling entities in the game.

## GraphQL Query

```graphql
query GetThirdPartyAccess($rootScope: String!) {
    ThirdPartyAccessByAccount(rootScope: $rootScope) {
        account
        thirdParties {
            thirdPartyId
            thirdPartyName
            accessCount
        }
    }
}
```

## Variables

```json
{
  "rootScope": "aws/r-ipxz"
}
```

## Response Structure

```json
{
  "data": {
    "ThirdPartyAccessByAccount": [
      {
        "account": "123456789",
        "thirdParties": [
          {
            "thirdPartyId": "tp-uuid-123",
            "thirdPartyName": "Cloudflare",
            "accessCount": 5
          },
          {
            "thirdPartyId": "tp-uuid-456",
            "thirdPartyName": "Datadog",
            "accessCount": 3
          }
        ]
      }
    ]
  }
}
```

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `fetch_third_parties_by_account(root_scope)`

## Notes

- `rootScope` typically refers to the AWS organization root (e.g., "aws/r-ipxz")
- Returns third-party access grouped by AWS account
- Each third party includes:
  - `thirdPartyId`: UUID for API operations
  - `thirdPartyName`: Display name (e.g., "Cloudflare")
  - `accessCount`: Number of access points

## Game Integration

Third parties in the game:
- Appear as corporate-suited entities (vs zombie appearance)
- Patrol along walls in the map
- Have 10 HP (vs 3 HP for zombies)
- Worth 50 points when blocked (vs 10 for zombies)
- Can be blocked via API (similar to quarantine)

## Special Case: Sonrai Third Party

The "Sonrai" or "Sonrai Security" third party is automatically marked as protected and displays a purple shield (it's your security platform!).

## Related Types

- `ThirdPartyAccessByAccountResponse` - Response type
- `ThirdPartyEntry` - Individual third party entry
- `ThirdParty` - Full third party details
