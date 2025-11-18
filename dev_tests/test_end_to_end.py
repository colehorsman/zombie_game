#!/usr/bin/env python3
"""Test the complete end-to-end integration."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient
from zombie import Zombie
from models import Vector2

print("=" * 60)
print("END-TO-END INTEGRATION TEST")
print("=" * 60)

# Step 1: Initialize API client
print("\n1. Initializing Sonrai API client...")
client = SonraiAPIClient(
    api_url=os.getenv('SONRAI_API_URL'),
    org_id=os.getenv('SONRAI_ORG_ID'),
    api_token=os.getenv('SONRAI_API_TOKEN')
)

# Step 2: Authenticate
print("2. Authenticating with Sonrai API...")
if not client.authenticate():
    print("✗ Authentication failed!")
    sys.exit(1)
print("✓ Authentication successful")

# Step 3: Fetch unused identities
print("\n3. Fetching unused identities from Sonrai...")
try:
    identities = client.fetch_unused_identities(
        limit=1000,
        scope=None,
        days_since_login="0",
        filter_account="577945324761"
    )
    print(f"✓ Fetched {len(identities)} total identities")
except Exception as e:
    print(f"✗ Failed to fetch identities: {e}")
    sys.exit(1)

# Step 4: Filter for test-user identities
print("\n4. Filtering for test-user identities...")
test_user_identities = [i for i in identities if 'test-user' in i.identity_name.lower()]
print(f"✓ Found {len(test_user_identities)} test-user identities")

if len(test_user_identities) == 0:
    print("✗ No test-user identities found!")
    sys.exit(1)

# Step 5: Create zombie entities
print("\n5. Creating zombie entities...")
zombies = []
for identity in test_user_identities[:10]:  # Just first 10 for testing
    zombie = Zombie(
        identity_id=identity.identity_id,
        identity_name=identity.identity_name,
        position=Vector2(100, 100)
    )
    zombies.append(zombie)
print(f"✓ Created {len(zombies)} zombie entities")

# Step 6: Verify zombie data
print("\n6. Verifying zombie data...")
for i, zombie in enumerate(zombies[:5], 1):
    print(f"\nZombie {i}:")
    print(f"  Name: {zombie.identity_name}")
    print(f"  Display Number: {zombie.display_number}")
    print(f"  SRN: {zombie.identity_id}")
    print(f"  Position: ({zombie.position.x}, {zombie.position.y})")
    print(f"  Size: {zombie.width}x{zombie.height}")

# Step 7: Verify label extraction
print("\n7. Verifying label extraction from identity names...")
test_cases = [
    ("test-user-1", 1),
    ("test-user-42", 42),
    ("test-user-100", 100),
    ("test-user-499", 499),
]

all_passed = True
for name, expected_number in test_cases:
    # Find a zombie with this name or create a test one
    test_zombie = Zombie(
        identity_id=f"srn:test/{name}",
        identity_name=name,
        position=Vector2(0, 0)
    )
    actual_number = test_zombie.display_number

    if actual_number == expected_number:
        print(f"✓ {name} → {actual_number}")
    else:
        print(f"✗ {name} → {actual_number} (expected {expected_number})")
        all_passed = False

if not all_passed:
    print("\n✗ Some label extraction tests failed!")
    sys.exit(1)

# Step 8: Summary
print("\n" + "=" * 60)
print("END-TO-END TEST SUMMARY")
print("=" * 60)
print(f"✓ API Connection: Working")
print(f"✓ Identity Fetching: Working ({len(test_user_identities)} test-users)")
print(f"✓ Zombie Creation: Working")
print(f"✓ Label Extraction: Working")
print("\n✓ All tests passed! The game is ready to run.")
print("\nTo start the game, run:")
print("  python3 src/main.py")
