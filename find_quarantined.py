#!/usr/bin/env python3
"""Try to find quarantined identities including test-user-10."""

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

# Query to get identities with quarantine status
# Let's try to see if there's a status field
query = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
            count
            quarantinedCount
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

print("Checking for quarantinedCount field...")
response = requests.post(
    api_url,
    json={"query": query, "variables": variables},
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get("errors"):
        print(f"❌ quarantinedCount field doesn't exist")
        print(f"   Error: {data['errors'][0].get('message')}")
    elif data.get("data"):
        print(f"✓ Success!")
        items = data["data"]["UnusedIdentities"].get("items", [])
        for item in items:
            if item.get("account") == "577945324761":
                print(f"\nAccount 577945324761:")
                print(f"  Total count: {item.get('count')}")
                print(f"  Quarantined count: {item.get('quarantinedCount', 'N/A')}")

                # Check if any of the identities are the known quarantined ones
                identities = item.get("identities", [])
                cpf_zombies = [i for i in identities if 'cpf-zombie' in i.get('srn', '')]
                test_user_10 = [i for i in identities if 'test-user-10' in i.get('srn', '')]

                print(f"\nFound {len(cpf_zombies)} cpf-zombie identities")
                for z in cpf_zombies[:5]:
                    print(f"  - {z.get('srn')}")

                if test_user_10:
                    print(f"\n✓ test-user-10 found in results")
                else:
                    print(f"\n⚠️  test-user-10 NOT found in results")
else:
    print(f"❌ HTTP Error: {response.status_code}")

# Alternative: Try to query with a status filter
print("\n" + "="*60)
print("Trying to filter by quarantine status...")

query2 = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
            count
        }
    }
}
"""

# Try with quarantineStatus filter
variables2 = {
    "filters": {
        "scope": {"value": "aws", "op": "STARTS_WITH"},
        "daysSinceLastLogin": {"op": "GTE", "value": "0"},
        "quarantineStatus": {"value": "QUARANTINED", "op": "EQ"}
    }
}

response2 = requests.post(
    api_url,
    json={"query": query2, "variables": variables2},
    headers=headers,
    timeout=30
)

if response2.status_code == 200:
    data2 = response2.json()
    if data2.get("errors"):
        print(f"❌ quarantineStatus filter doesn't exist")
    elif data2.get("data"):
        print(f"✓ quarantineStatus filter works!")
        print(json.dumps(data2["data"], indent=2))
