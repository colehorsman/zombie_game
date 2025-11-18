#!/usr/bin/env python3
"""Test quarantine with the CORRECT scope from Sonrai UI."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

print("Testing with CORRECT scope values from Sonrai UI")
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
print("✓ Authenticated\n")

# Test with test-user-300
test_srn = "srn:aws:iam::577945324761/User/User/test-user-300"
test_name = "test-user-300"

print(f"2. Quarantining: {test_name}")
print(f"   SRN: {test_srn}")
print(f"   Scope: aws/r-ipxz/ou-ipxz-95f072k5/577945324761")
print(f"   Root: aws/r-ipxz\n")

result = client.quarantine_identity(
    identity_id=test_srn,
    identity_name=test_name
)

print(f"3. Result:")
print(f"   Success: {result.success}")
if result.error_message:
    print(f"   Error: {result.error_message}")
else:
    print(f"   ✓ Quarantine successful!")

print("\n" + "=" * 60)
if result.success:
    print("🎉 QUARANTINE WORKING!")
    print("\nNow check Sonrai UI - test-user-300 should be quarantined!")
else:
    print("⚠️  Still failed - check error above")
