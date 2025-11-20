# Sonrai API Documentation

This directory contains documentation for all Sonrai GraphQL API queries and mutations used in the Zombie Blaster game.

## Overview

The Sonrai Security platform provides a GraphQL API for querying cloud security data and performing remediation actions. This game integrates with several Sonrai API endpoints to fetch unused identities, third-party access, exemptions, and perform quarantine operations.

## API Endpoint

- **URL**: Configured via `SONRAI_API_URL` environment variable
- **Authentication**: Bearer token via `SONRAI_API_TOKEN`
- **Organization**: Specified via `SONRAI_ORG_ID`

## GraphQL Schema

### Downloaded Schema

The complete Sonrai GraphQL schema is available locally in `schema.json`. This includes:
- All 138 available queries
- All 154 available mutations
- 856 total types (objects, inputs, enums, etc.)

**Update the schema:**
```bash
python3 dev_tests/download_sonrai_schema.py
```

### Schema Search Tool

Search the schema for queries, mutations, types, and fields:

```bash
# Search for queries
python3 dev_tests/search_sonrai_schema.py --query CloudHierarchy

# Search for types
python3 dev_tests/search_sonrai_schema.py --type UnusedIdentity

# Search for mutations
python3 dev_tests/search_sonrai_schema.py --mutation Quarantine

# Search for fields across all types
python3 dev_tests/search_sonrai_schema.py --field daysSinceLogin

# Show schema statistics
python3 dev_tests/search_sonrai_schema.py --stats
```

This tool is extremely helpful when building new queries - no more guessing field names!

### Interactive Schema Explorer

Access the web-based GraphQL schema explorer at:
https://app.sonraisecurity.com/App/GraphExplorer

## Available Queries

### Data Fetching Queries

1. **[Cloud Hierarchy](queries/cloud-hierarchy.md)** - Fetch AWS org structure and account scopes (CRITICAL for quarantine)
2. **[Unused Identities](queries/unused-identities.md)** - Fetch unused IAM identities (zombies)
3. **[Third Party Access](queries/third-party-access.md)** - Fetch third-party access to AWS accounts
4. **[Exempted Identities](queries/exempted-identities.md)** - Fetch exempted/protected identities
5. **[Accounts with Unused Identities](queries/accounts-unused-identities.md)** - Get account summary

### Mutation Operations

1. **[Quarantine Identity](queries/quarantine-identity.md)** - Quarantine an unused identity
2. **[Block Third Party](queries/block-third-party.md)** - Block third-party access

## Implementation

All queries are implemented in `src/sonrai_client.py` in the `SonraiAPIClient` class.

## Common Patterns

### Using Real Account Scopes

**CRITICAL**: Always use real scopes from the CloudHierarchyList query. Never construct or fake scopes.

```python
# CORRECT: Fetch real scopes first
account_scopes = client._fetch_all_account_scopes()
scope = account_scopes.get("577945324761")
# Returns: "aws/r-ipxz/ou-ipxz-95f072k5/577945324761"

# WRONG: Never construct scopes manually
scope = f"aws/r-ipxz/ou-fake-id/{account}"  # This triggers alerts!
```

See [Cloud Hierarchy](queries/cloud-hierarchy.md) for details.

### Filtering by Scope

Most queries support filtering by AWS account scope:

```graphql
where: {
    scope: {
        value: "aws/123456789",
        op: "EQ"
    }
}
```

### Pagination

Queries support limiting results:

```graphql
UnusedIdentities(limit: 500) {
    count
    items { ... }
}
```

### Error Handling

All API methods include:
- Retry logic with exponential backoff
- Graceful error handling (return empty lists/false on failure)
- Detailed logging

## Schema Types Reference

Key types used in this game:

- `UnusedIdentity` - Represents an unused IAM identity
- `ThirdParty` - Represents third-party access
- `AppliedExemptedIdentity` - Represents an exempted identity
- `QuarantineResult` - Result of quarantine operation

## Adding New Queries

When adding new Sonrai API queries:

1. **Search the schema** using the search tool to find the right query/type:
   ```bash
   python3 dev_tests/search_sonrai_schema.py --query YourQueryName
   python3 dev_tests/search_sonrai_schema.py --type YourTypeName
   ```
2. **Test the query** in the GraphQL explorer or create a test script
3. **Document it** - Create a new markdown file in `queries/` directory
4. **Implement** in `src/sonrai_client.py`
5. **Update** this README with a link to the documentation

## Troubleshooting

### Common Issues

1. **Field not found errors**: Check the schema explorer for correct field names
2. **Filter type errors**: Verify the filter type matches the query (e.g., `AppliedExemptedIdentitiesFilter`)
3. **Operation errors**: Ensure the operation type (EQ, CONTAINS, etc.) is valid for the field type

### Schema Introspection

To discover available fields on a type:

```graphql
{
  __type(name: "TypeName") {
    fields {
      name
      type { name }
    }
  }
}
```
