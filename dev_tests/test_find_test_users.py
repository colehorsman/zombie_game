#!/usr/bin/env python3
"""Find test-user identities from the UnusedIdentities query."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
import json
load_dotenv('.env')

import requests

api_url = os.getenv('SONRAI_API_URL')
api_token = os.getenv('SONRAI_API_TOKEN')

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Get all identities for the target account
query = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
            count
            identities {
                srn
            }
        }
    }
}
"""

variables = {
    "filters": {
        "scope": {"value": "aws", "op": "STARTS_WITH"},
        "daysSinceLastLogin": {"op": "GTE", "value": "0"}
    }
}

try:
    response = requests.post(
        api_url,
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get("errors"):
            print(f"❌ Error: {data['errors'][0].get('message')}")
        elif data.get("data"):
            # Find the target account
            result = data["data"]
            if "UnusedIdentities" in result and "items" in result["UnusedIdentities"]:
                target_account_item = None
                for item in result["UnusedIdentities"]["items"]:
                    if item.get("account") == "577945324761":
                        target_account_item = item
                        break

                if target_account_item and "identities" in target_account_item:
                    all_identities = target_account_item["identities"]
                    print(f"Total identities for account 577945324761: {len(all_identities)}")

                    # Filter for test-user identities
                    test_users = []
                    for identity in all_identities:
                        srn = identity.get("srn", "")
                        # Extract name from SRN (after last /)
                        name = srn.split("/")[-1] if "/" in srn else srn
                        if "test-user" in name.lower():
                            test_users.append({"srn": srn, "name": name})

                    print(f"\nFound {len(test_users)} test-user identities:")
                    for i, user in enumerate(test_users[:20], 1):  # Show first 20
                        print(f"  {i}. {user['name']}")
                        print(f"      SRN: {user['srn']}")

                    if len(test_users) > 20:
                        print(f"\n  ... and {len(test_users) - 20} more")

                    # Also show what other types of identities exist
                    print("\n\nSample of all identity types (first 10):")
                    for i, identity in enumerate(all_identities[:10], 1):
                        srn = identity.get("srn", "")
                        name = srn.split("/")[-1] if "/" in srn else srn
                        resource_type = srn.split("/")[-2] if "/" in srn and len(srn.split("/")) > 1 else "Unknown"
                        print(f"  {i}. {name} (Type: {resource_type})")
                else:
                    print("Account 577945324761 not found or has no identities")
        else:
            print("Empty response")
    else:
        print(f"HTTP Error: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"Exception: {e}")
