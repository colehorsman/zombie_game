#!/usr/bin/env python3
"""Test getting detailed info from UnusedIdentities query."""

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

# Try to get more fields from UnusedIdentities
queries_to_try = [
    ("UnusedIdentities with identities field", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            items {
                account
                count
                identities {
                    srn
                    name
                    resourceType
                }
            }
        }
    }
    """, {
        "filters": {
            "scope": {"value": "aws", "op": "STARTS_WITH"},
            "daysSinceLastLogin": {"op": "GTE", "value": "0"}
        }
    }),
    ("UnusedIdentities with srns field", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            items {
                account
                count
                srns
            }
        }
    }
    """, {
        "filters": {
            "scope": {"value": "aws", "op": "STARTS_WITH"},
            "daysSinceLastLogin": {"op": "GTE", "value": "0"}
        }
    }),
    ("UnusedIdentities with all available fields", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            count
            items {
                account
                count
            }
        }
    }
    """, {
        "filters": {
            "scope": {"value": "aws", "op": "STARTS_WITH"},
            "daysSinceLastLogin": {"op": "GTE", "value": "0"}
        }
    }),
]

for name, query, variables in queries_to_try:
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
                # Show first 2 items to keep output manageable
                result = data["data"]
                if "UnusedIdentities" in result and "items" in result["UnusedIdentities"]:
                    result["UnusedIdentities"]["items"] = result["UnusedIdentities"]["items"][:2]
                print(json.dumps(result, indent=2))
            else:
                print("Empty response")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"Exception: {e}")
