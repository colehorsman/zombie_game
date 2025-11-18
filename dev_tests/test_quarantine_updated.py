#!/usr/bin/env python3
"""Test the updated quarantine_identity method."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

print("Testing updated quarantine_identity method")
print("=" * 60)

# Initialize client
client = SonraiAPIClient(
    api_url=os.getenv('SONRAI_API_URL'),
    org_id=os.getenv('SONRAI_ORG_ID'),
    api_token=os.getenv('SONRAI_API_TOKEN')
)

# Authenticate
print("1. Authenticating...")
if not client.authenticate():
    print("✗ Authentication failed!")
    sys.exit(1)
print("✓ Authenticated")

# Test quarantine with a test-user identity
test_srn = "srn:aws:iam::577945324761/User/User/test-user-500"
test_name = "test-user-500"

print(f"\n2. Testing quarantine for: {test_name}")
print(f"   SRN: {test_srn}")

result = client.quarantine_identity(
    identity_id=test_srn,
    identity_name=test_name,
    account="577945324761"
)

print(f"\n3. Result:")
print(f"   Success: {result.success}")
if result.error_message:
    print(f"   Error: {result.error_message}")
else:
    print(f"   ✓ Identity successfully quarantined!")

# Verify it's quarantined by checking if it's still in the unused list
print(f"\n4. Verifying quarantine...")
identities = client.fetch_unused_identities(
    limit=1000,
    scope=None,
    days_since_login="0",
    filter_account="577945324761"
)

test_users = [i for i in identities if 'test-user' in i.identity_name.lower()]
if result.success:
    if test_name not in [i.identity_name for i in test_users]:
        print(f"   ✓ {test_name} is no longer in the unused identities list!")
    else:
        print(f"   ⚠️  {test_name} is still in the unused identities list (may take time to update)")
else:
    print(f"   Skipping verification due to quarantine failure")

print(f"\nTotal test-user identities remaining: {len(test_users)}")
