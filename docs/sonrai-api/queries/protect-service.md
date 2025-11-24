# Protect Service

Protects AWS services using Sonrai's Cloud Permissions Firewall.

## Mutation

```graphql
mutation protectService($input: ProtectActionInput!) {
    ProtectService(input: $input) {
        success
        serviceName
    }
}
```

## Input

```json
{
  "input": {
    "controlKey": "bedrock",
    "scope": "aws/r-ipxz/ou-ipxz-95f072k5/577945324761",
    "identities": [],
    "ssoActorIds": []
  }
}
```

## Parameters

- **controlKey** (required): Service-specific key ("bedrock", "s3", "rds", "lambda", "sagemaker", "dynamodb")
- **scope** (required): Full AWS scope path from CloudHierarchyList
- **identities**: Array of identity IDs to allow (empty for default protection)
- **ssoActorIds**: Array of SSO actor IDs to allow (empty for default protection)

## CRITICAL: Scope Fetching

**ALWAYS fetch real scopes from CloudHierarchyList - NEVER construct manually!**

Use the `_fetch_all_account_scopes()` method to get accurate scope paths:

```python
account_scopes = self._fetch_all_account_scopes()
scope = account_scopes.get(account_id)
```

Example scope format:
```
aws/r-ipxz/ou-ipxz-95f072k5/577945324761
```

## Response

```json
{
  "data": {
    "ProtectService": {
      "success": true,
      "serviceName": "Bedrock Service"
    }
  }
}
```

## Service Control Keys

| Service | Control Key |
|---------|-------------|
| Amazon Bedrock | `bedrock` |
| Amazon S3 | `s3` |
| Amazon RDS | `rds` |
| AWS Lambda | `lambda` |
| Amazon SageMaker | `sagemaker` |
| Amazon DynamoDB | `dynamodb` |

## Example Usage

### Protect Bedrock Service

```python
result = api_client.protect_service(
    service_type="bedrock",
    account_id="577945324761",
    service_name="Bedrock Service"
)

if result.success:
    print(f"✅ Protected {result.identity_id}")
else:
    print(f"❌ Error: {result.error_message}")
```

### Protect S3 Service

```python
result = api_client.protect_service(
    service_type="s3",
    account_id="577945324761",
    service_name="S3 Buckets"
)
```

### Protect RDS Service

```python
result = api_client.protect_service(
    service_type="rds",
    account_id="613056517323",  # Production account
    service_name="RDS Databases"
)
```

## Error Handling

The method returns a `QuarantineResult` with:
- `success`: Boolean indicating operation success
- `identity_id`: Service name if successful
- `error_message`: Error details if failed

Common errors:
- **Unknown service type**: Invalid service_type parameter
- **No scope found**: Account ID not in CloudHierarchyList
- **GraphQL errors**: API-level errors
- **Network errors**: Connection failures

## Game Integration

In the Service Protection Quest, this API is called when the player wins the race:

```python
# GameEngine._try_protect_service()
result = self.api_client.protect_service(
    service_type=quest.service_type,
    account_id=self.game_state.current_level_account_id,
    service_name=f"{quest.service_type.capitalize()} Service"
)

if result.success:
    # Player won! Service is protected
    service_node.protected = True
    quest.player_won = True
```

## Implementation Notes

1. **Real API Call**: This is NOT a mock - it calls the actual Sonrai API
2. **Scope Fetching**: Always uses CloudHierarchyList for accurate scopes
3. **Error Recovery**: Failed protections allow retry
4. **Timeout**: 30-second timeout for network requests
5. **Logging**: All API calls are logged for debugging

## Related Queries

- [CloudHierarchyList](cloud-hierarchy.md) - Fetch account scopes
- [QuarantineIdentity](quarantine-identity.md) - Quarantine unused identities
- [BlockThirdParty](block-third-party.md) - Block third-party access
