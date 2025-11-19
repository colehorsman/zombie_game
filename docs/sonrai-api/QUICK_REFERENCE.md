# Sonrai API Quick Reference

Quick lookup for all Sonrai API calls used in Zombie Blaster.

## Queries (Data Fetching)

| Query Name | Purpose | Method | Doc Link |
|------------|---------|--------|----------|
| `UnusedIdentities` | Fetch zombies | `fetch_unused_identities()` | [Link](queries/unused-identities.md) |
| `ThirdPartyAccessByAccount` | Fetch 3rd parties | `fetch_third_parties_by_account()` | [Link](queries/third-party-access.md) |
| `AppliedExemptedIdentities` | Fetch exemptions | `fetch_exemptions()` | [Link](queries/exempted-identities.md) |
| `AccountsWithUnusedIdentities` | Account summary | `fetch_accounts_with_unused_identities()` | [Link](queries/accounts-unused-identities.md) |

## Mutations (Actions)

| Mutation Name | Purpose | Method | Doc Link |
|---------------|---------|--------|----------|
| `ChangeQuarantineStatus` | Quarantine identity | `quarantine_identity()` | [Link](queries/quarantine-identity.md) |
| `SetThirdPartyControlMode` | Block 3rd party | `block_third_party()` | [Link](queries/block-third-party.md) |

## Common Filter Patterns

### By AWS Account

```graphql
where: {
    account: { value: "123456789", op: EQ }
}
```

### By Scope

```graphql
where: {
    scope: { value: "aws/123456789", op: EQ }
}
```

### By Days Since Login

```graphql
where: {
    daysSinceLogin: { value: "90", op: GTE }
}
```

## Common Response Patterns

### List Response

```graphql
{
    QueryName {
        count
        items { ... }
    }
}
```

### Mutation Response

```graphql
{
    MutationName {
        success
        errorMessage
    }
}
```

## Key Types

- `UnusedIdentity` - Zombie entity
- `ThirdParty` - Third-party access entity
- `AppliedExemptedIdentity` - Protected entity
- `QuarantineResult` - Quarantine operation result

## Error Handling

All methods include:
- ✅ Retry logic (3 attempts, exponential backoff)
- ✅ Graceful error handling (return empty/false on failure)
- ✅ Detailed logging
- ✅ Timeout protection (30 seconds)

## Schema Explorer

https://app.sonraisecurity.com/App/GraphExplorer
