#!/usr/bin/env python3
"""Test the final updated quarantine method."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

print("Testing final quarantine_identity method")
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

# Test with a test-user identity (using a higher number that likely wasn't quarantined yet)
test_srn = "srn:aws:iam::577945324761/User/User/test-user-499"
test_name = "test-user-499"

print(f"2. Testing quarantine for: {test_name}")
print(f"   SRN: {test_srn}\n")

result = client.quarantine_identity(
    identity_id=test_srn,
    identity_name=test_name
)

print(f"3. Result:")
print(f"   Success: {result.success}")
if result.error_message:
    print(f"   Error: {result.error_message}")
else:
    print(f"   ✓ Identity successfully quarantined!")

print("\n" + "=" * 60)
if result.success:
    print("🎉 QUARANTINE WORKING! The game is ready!")
    print("\nYou can now run the game and zap zombies to quarantine them:")
    print("  python3 src/main.py")
else:
    print("⚠️  Quarantine failed. Check the error above.")
