#!/usr/bin/env python3
"""Check if we can query the quarantine status."""

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

# Try to query quarantined identities
queries_to_try = [
    ("Query QuarantinedIdentities", """
    query {
        QuarantinedIdentities {
            count
            items {
                resourceId
                name
                account
            }
        }
    }
    """),
    ("Query UnusedIdentities with quarantine filter", """
    query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
        UnusedIdentities(where: $filters) {
            items {
                account
                count
                identities {
                    srn
                    quarantined
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
]

for item in queries_to_try:
    if len(item) == 3:
        name, query, variables = item
    else:
        name, query = item
        variables = None

    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

    try:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("errors"):
                error_msg = data['errors'][0].get('message', 'Unknown error')
                print(f"❌ Error: {error_msg}")
            elif data.get("data"):
                print(f"✓ Success!")
                print(json.dumps(data["data"], indent=2)[:500])
            else:
                print("Empty response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
