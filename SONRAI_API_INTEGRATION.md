# Sonrai API Integration Guide

## Current Status

✅ **FULLY INTEGRATED** - The game is now connected to the Sonrai Security API and uses real data!

## Comprehensive API Documentation

For detailed documentation on all Sonrai API queries and mutations used in this game, see:

**[docs/sonrai-api/README.md](docs/sonrai-api/README.md)**

This includes:
- Complete GraphQL queries with examples
- Response structures and field descriptions
- Implementation details
- Error handling patterns
- Schema type references

## Implemented API Endpoints

### Data Fetching (Queries)

1. **Unused Identities** - `UnusedIdentities` query
   - Fetches unused IAM identities (zombies)
   - [Documentation](docs/sonrai-api/queries/unused-identities.md)
   - Implementation: `SonraiAPIClient.fetch_unused_identities()`

2. **Third Party Access** - `ThirdPartyAccessByAccount` query
   - Fetches third-party access to AWS accounts
   - [Documentation](docs/sonrai-api/queries/third-party-access.md)
   - Implementation: `SonraiAPIClient.fetch_third_parties_by_account()`

3. **Exempted Identities** - `AppliedExemptedIdentities` query
   - Fetches protected/exempted identities
   - [Documentation](docs/sonrai-api/queries/exempted-identities.md)
   - Implementation: `SonraiAPIClient.fetch_exemptions()`

4. **Account Summary** - `AccountsWithUnusedIdentities` query
   - Gets account list with zombie counts
   - [Documentation](docs/sonrai-api/queries/accounts-unused-identities.md)
   - Implementation: `SonraiAPIClient.fetch_accounts_with_unused_identities()`

### Remediation Actions (Mutations)

1. **Quarantine Identity** - `ChangeQuarantineStatus` mutation
   - Quarantines unused identities via CPF
   - [Documentation](docs/sonrai-api/queries/quarantine-identity.md)
   - Implementation: `SonraiAPIClient.quarantine_identity()`

2. **Block Third Party** - `SetThirdPartyControlMode` mutation
   - Blocks third-party access via CPF
   - [Documentation](docs/sonrai-api/queries/block-third-party.md)
   - Implementation: `SonraiAPIClient.block_third_party()`

## Schema Explorer

Access the interactive GraphQL schema explorer at:
https://app.sonraisecurity.com/App/GraphExplorer

Use this to:
- Explore available queries and mutations
- Discover field names and types
- Test queries before implementing
- Introspect schema types

## Adding New Queries

When adding new Sonrai API integration:

1. **Explore the schema** in the GraphQL explorer
2. **Test the query** with sample data
3. **Document it** in `docs/sonrai-api/queries/`
4. **Implement** in `src/sonrai_client.py`
5. **Update** this file with a link to the documentation

## Implementation Location

All Sonrai API integration is in:
- **File**: `src/sonrai_client.py`
- **Class**: `SonraiAPIClient`
- **Methods**: One method per query/mutation

## Running the Game

The game connects to your Sonrai organization using credentials in `.env`:

```bash
python3 src/main.py
```

The game will:
1. Fetch real unused identities from your AWS accounts
2. Load third-party access information
3. Display exempted identities with purple shields
4. Quarantine identities when you eliminate zombies
5. Block third-party access when you eliminate third parties

**⚠️ Warning:** Eliminating zombies and third parties will actually quarantine/block them in Sonrai via the Cloud Permissions Firewall!

## Configuration

Set these environment variables in `.env`:

```bash
SONRAI_API_URL=https://crc.sonraisecurity.com/graphql
SONRAI_ORG_ID=your-org-id
SONRAI_API_TOKEN=your-api-token
```

## Error Handling

All API methods include:
- **Retry logic** with exponential backoff (3 attempts)
- **Graceful degradation** (returns empty lists on failure)
- **Detailed logging** for debugging
- **User-friendly error messages** in the game UI

## Future Enhancements

Potential additional API integrations:
- High-risk entities for boss battles
- Real-time security alerts
- Compliance status
- Risk scoring for difficulty scaling
