#!/usr/bin/env python3
"""Verify if test-user-10 was actually quarantined."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

print("Checking quarantine status of test-user-10")
print("=" * 60)

# Initialize client
client = SonraiAPIClient(
    api_url=os.getenv('SONRAI_API_URL'),
    org_id=os.getenv('SONRAI_ORG_ID'),
    api_token=os.getenv('SONRAI_API_TOKEN')
)

# Fetch current unused identities
print("Fetching current unused identities...")
identities = client.fetch_unused_identities(
    limit=1000,
    scope=None,
    days_since_login="0",
    filter_account="577945324761"
)

# Filter for test-users
test_users = [i for i in identities if 'test-user' in i.identity_name.lower()]
test_user_names = [i.identity_name for i in test_users]

print(f"Total test-user identities found: {len(test_users)}")

# Check if test-user-10 is still there
if "test-user-10" in test_user_names:
    print("\n⚠️  test-user-10 is STILL in the unused identities list!")
    print("   The quarantine might not have removed it from unused identities.")
else:
    print("\n✓ test-user-10 is NOT in the unused identities list!")
    print("  It was successfully removed.")

# Also check a few others for comparison
print("\nChecking some other test users:")
for num in [1, 2, 9, 10, 11, 499]:
    name = f"test-user-{num}"
    status = "Present" if name in test_user_names else "Missing"
    print(f"  test-user-{num}: {status}")
