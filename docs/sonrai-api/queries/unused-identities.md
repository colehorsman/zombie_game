# Unused Identities Query

Fetches unused IAM identities (zombies) from AWS accounts.

## Query Name

`UnusedIdentities`

## Purpose

Retrieve IAM identities that haven't been used for a specified number of days. These are the "zombies" in the game.

## GraphQL Query

```graphql
query GetUnusedIdentities($limit: Int!, $scope: String, $daysSinceLogin: String, $filterAccount: String) {
    UnusedIdentities(
        limit: $limit
        where: {
            scope: { value: $scope, op: CONTAINS }
            daysSinceLogin: { value: $daysSinceLogin, op: GTE }
            account: { value: $filterAccount, op: EQ }
        }
    ) {
        count
        items {
            srn
            resourceId
            resourceName
            resourceType
            account
            title
            lastLogin
            daysSinceLogin
            scope
        }
    }
}
```

## Variables

```json
{
  "limit": 500,
  "scope": "aws",
  "daysSinceLogin": "0",
  "filterAccount": "123456789"
}
```

## Response Structure

```json
{
  "data": {
    "UnusedIdentities": {
      "count": 10,
      "items": [
        {
          "srn": "srn:aws:iam::123456789:user/test-user-1",
          "resourceId": "AIDAI...",
          "resourceName": "test-user-1",
          "resourceType": "aws.iam.user",
          "account": "123456789",
          "title": "test-user-1",
          "lastLogin": "2024-01-01T00:00:00Z",
          "daysSinceLogin": "90",
          "scope": "aws/123456789"
        }
      ]
    }
  }
}
```

## Implementation

**File**: `src/sonrai_client.py`

**Method**: `fetch_unused_identities(limit, scope, days_since_login, filter_account)`

## Notes

- Default limit is 500 to avoid overwhelming the game
- `daysSinceLogin` filter helps focus on truly unused identities
- `scope` filter narrows to specific cloud provider (aws, azure, gcp)
- `account` filter gets identities for a specific AWS account

## Related Types

- `UnusedIdentity` - Response item type
- `UnusedIdentitiesFilter` - Filter input type
