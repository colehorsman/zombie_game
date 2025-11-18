#!/usr/bin/env python3
"""Test quarantine with real scope values."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

print("Testing quarantine with REAL scope values")
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

# Test with test-user-100 (so we don't re-test 10 or 499)
test_srn = "srn:aws:iam::577945324761/User/User/test-user-100"
test_name = "test-user-100"

print(f"2. Testing quarantine for: {test_name}")
print(f"   SRN: {test_srn}")
print(f"   Scope: aws/Sonrai MyHealth - Org/Sandbox/MyHealth - Sandbox")
print(f"   Root Scope: aws/Sonrai MyHealth - Org\n")

result = client.quarantine_identity(
    identity_id=test_srn,
    identity_name=test_name
)

print(f"3. Result:")
print(f"   Success: {result.success}")
if result.error_message:
    print(f"   Error: {result.error_message}")
else:
    print(f"   ✓ API call succeeded!")

print("\n" + "=" * 60)
if result.success:
    print("🎯 Quarantine API call successful!")
    print("\nNow check in Sonrai UI:")
    print("  - Go to myhealth sandbox quarantined identities")
    print("  - Look for test-user-100")
    print("  - It should appear there now!")
else:
    print("⚠️  Quarantine failed. Check the error above.")
