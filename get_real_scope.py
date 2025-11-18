#!/usr/bin/env python3
"""Get the real scope path from UnusedIdentities query."""

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

# Query to get the scope information
query = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
            scope
            count
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

print("Fetching scope information from UnusedIdentities...")
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
        items = data["data"]["UnusedIdentities"].get("items", [])

        print(f"\nFound {len(items)} account groups\n")

        for item in items:
            account = item.get("account")
            scope = item.get("scope")
            count = item.get("count")

            if account == "577945324761":
                print(f"✓ Found myhealth sandbox account!")
                print(f"  Account: {account}")
                print(f"  Scope: {scope}")
                print(f"  Count: {count}")

                if scope:
                    # Extract root scope (first two parts)
                    parts = scope.split("/")
                    if len(parts) >= 2:
                        root_scope = "/".join(parts[:2])
                        print(f"  Root Scope: {root_scope}")

                    print(f"\n📋 Use these values for quarantine:")
                    print(f"   scope = \"{scope}\"")
                    print(f"   rootScope = \"{root_scope}\"")
                else:
                    print("  ⚠️  No scope field available!")
                break
        else:
            print("❌ Account 577945324761 not found!")
else:
    print(f"❌ HTTP Error: {response.status_code}")
