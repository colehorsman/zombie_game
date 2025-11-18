#!/usr/bin/env python3
"""Test what fields are available for individual identities."""

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

# Try different field combinations for identities
queries_to_try = [
    ("identities with srn only", """
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
    """),
    ("identities with srn and resourceType", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            items {
                account
                count
                identities {
                    srn
                    resourceType
                }
            }
        }
    }
    """),
    ("identities with title", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            items {
                account
                count
                identities {
                    srn
                    title
                }
            }
        }
    }
    """),
]

# Filter to the target account
variables = {
    "filters": {
        "scope": {"value": "aws", "op": "STARTS_WITH"},
        "daysSinceLastLogin": {"op": "GTE", "value": "0"}
    }
}

for name, query in queries_to_try:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

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
                print(f"✓ Success!")
                # Find the account 577945324761
                result = data["data"]
                if "UnusedIdentities" in result and "items" in result["UnusedIdentities"]:
                    target_account_item = None
                    for item in result["UnusedIdentities"]["items"]:
                        if item.get("account") == "577945324761":
                            target_account_item = item
                            break

                    if target_account_item:
                        print(f"Found account 577945324761 with {target_account_item.get('count')} identities")
                        if "identities" in target_account_item:
                            identities = target_account_item["identities"][:5]  # Show first 5
                            print(f"First 5 identities:")
                            print(json.dumps(identities, indent=2))
                    else:
                        print("Account 577945324761 not found in results")
            else:
                print("Empty response")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"Exception: {e}")
