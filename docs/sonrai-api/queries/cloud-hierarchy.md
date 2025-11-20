# CloudHierarchyList Query

## Purpose

Fetches the AWS organizational hierarchy to retrieve accurate account scopes with full organizational unit (OU) paths. This query is critical for getting real scope paths needed for quarantine operations, as fake scopes trigger security alerts.

## Why This Query Is Important

When quarantining identities, Sonrai requires the **exact scope path** including the full OU hierarchy (e.g., `aws/r-ipxz/ou-ipxz-95f072k5/577945324761`). Using incorrect or fabricated scopes will:
- Trigger security alerts in Sonrai
- Cause quarantine operations to fail
- Create false positive notifications

This query ensures we always use real, API-provided scopes.

## Query

```graphql
query getCloudHierarchyList($filters: CloudHierarchyFilter) {
    CloudHierarchyList(where: $filters) {
        items {
            resourceId
            scope
            cloudType
            parentScope
            scopeFriendlyName
            name
        }
    }
}
```

## Variables

```json
{
    "filters": {
        "cloudType": {
            "op": "EQ",
            "value": "aws"
        },
        "scope": {
            "op": "STARTS_WITH",
            "value": "aws/r-ipxz"
        },
        "entryType": {
            "op": "NEQ",
            "value": "managementAccount"
        },
        "active": {
            "op": "EQ",
            "value": true
        }
    }
}
```

### Filter Parameters

- **`cloudType`**: Filter to AWS accounts only
- **`scope`**: Filter to specific organization root (e.g., `aws/r-ipxz` for MyHealth)
- **`entryType`**: Exclude management account entries
- **`active`**: Only include active accounts/OUs

## Response Structure

```json
{
    "data": {
        "CloudHierarchyList": {
            "items": [
                {
                    "resourceId": "577945324761",
                    "scope": "aws/r-ipxz/ou-ipxz-95f072k5/577945324761",
                    "cloudType": "aws",
                    "parentScope": "aws/r-ipxz/ou-ipxz-95f072k5",
                    "scopeFriendlyName": "MyHealth - Sandbox",
                    "name": "MyHealth - Sandbox"
                }
            ]
        }
    }
}
```

### Response Fields

- **`resourceId`**: AWS account number (12 digits)
- **`scope`**: Full scope path with OU hierarchy (USE THIS for quarantine operations)
- **`cloudType`**: Cloud provider (aws, azure, gcp)
- **`parentScope`**: Parent OU or root scope
- **`scopeFriendlyName`**: Human-readable name
- **`name`**: Account name

## Implementation

Located in `src/sonrai_client.py` in the `_fetch_all_account_scopes()` method.

### Usage Pattern

```python
# Fetch all account scopes once at startup
account_scopes = self._fetch_all_account_scopes()

# Look up scope by account number
account_number = "577945324761"
full_scope = account_scopes.get(account_number)
# Returns: "aws/r-ipxz/ou-ipxz-95f072k5/577945324761"

# Use this scope for quarantine operations
self.quarantine_identity(
    identity_id=identity.identity_id,
    identity_name=identity.identity_name,
    scope=full_scope,  # Real scope from CloudHierarchyList
    root_scope="aws/r-ipxz"  # Extracted from full scope
)
```

## Filtering to Real Accounts

The implementation filters results to only include real AWS accounts, excluding:
- Organizational units (OUs)
- Root management account
- Inactive accounts

Example for MyHealth organization:
```python
VALID_MYHEALTH_ACCOUNTS = {
    "160224865296",  # MyHealth - Production Data
    "240768036625",  # MyHealth-WebApp
    "514455208804",  # MyHealth - Stage
    "437154727976",  # Sonrai MyHealth - Org
    "393582650665",  # MyHealth - Automation
    "577945324761",  # MyHealth - Sandbox
    "613056517323",  # MyHealth - Production
}
```

## Common Patterns

### Extracting Root Scope from Full Scope

```python
# From: "aws/r-ipxz/ou-ipxz-95f072k5/577945324761"
# To: "aws/r-ipxz"

scope_parts = full_scope.split("/")
if len(scope_parts) >= 2:
    root_scope = f"{scope_parts[0]}/{scope_parts[1]}"
```

### Caching Scopes

Fetch all scopes once at initialization to avoid repeated API calls:

```python
# In __init__ or startup
self.account_scopes = self._fetch_all_account_scopes()
logger.info(f"Cached {len(self.account_scopes)} account scopes")

# Later, quick lookup
scope = self.account_scopes.get(account_number)
```

## Error Handling

```python
# Always verify scope exists before quarantine
account_scope = account_scopes.get(account_number)
if not account_scope:
    logger.warning(f"No scope found for account {account_number} - cannot quarantine")
    return QuarantineResult(success=False, error_message="No scope found")
```

## Troubleshooting

### Issue: Too many results including OUs

**Solution**: Filter by `resourceId` to only include 12-digit AWS account numbers:
```python
if resource_id and len(resource_id) == 12 and resource_id.isdigit():
    # It's a real AWS account
    account_scopes[resource_id] = scope
```

### Issue: Scope format doesn't match expected pattern

**Solution**: Validate scope format:
```python
# Expected format: aws/r-xxxxx/ou-xxxxx-xxxxxxxx/123456789012
scope_parts = scope.split("/")
if len(scope_parts) >= 3:  # At minimum: cloud/root/account
    # Valid scope
```

### Issue: Different organizations have different root IDs

**Solution**: Make root scope configurable:
```python
root_scope = "aws/r-ipxz"  # MyHealth
# or
root_scope = "aws/r-ui1v"  # Different organization
```

## Related Queries

- **[Unused Identities](unused-identities.md)** - Uses scope for filtering
- **[Quarantine Identity](quarantine-identity.md)** - Requires accurate scope
- **[Third Party Access](third-party-access.md)** - Uses root scope filtering

## Notes

- This query should be called **once** at startup and results cached
- Scope paths are internal Sonrai IDs, not AWS-native paths
- Always use API-provided scopes, never construct them manually
- The scope format may vary between different Sonrai installations
