#!/usr/bin/env python3
"""Find the cpf-zombie identities to see their properties."""

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

# Get all identities and find the cpf-zombie ones
query = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
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

print("Looking for cpf-zombie identities...")
response = requests.post(
    api_url,
    json={"query": query, "variables": variables},
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get("data"):
        items = data["data"]["UnusedIdentities"].get("items", [])

        for item in items:
            if item.get("account") == "577945324761":
                identities = item.get("identities", [])

                # Find cpf-zombie identities
                cpf_zombies = [i for i in identities if 'cpf-zombie' in i.get('srn', '').lower()]

                print(f"Found {len(cpf_zombies)} cpf-zombie identities:")
                for z in cpf_zombies:
                    srn = z.get('srn')
                    print(f"\n  SRN: {srn}")

                    # Extract name and type from SRN
                    parts = srn.split("/")
                    if len(parts) >= 2:
                        resource_type = parts[-2]
                        name = parts[-1]
                        print(f"  Type: {resource_type}")
                        print(f"  Name: {name}")

                        # Convert to ARN format
                        if resource_type.lower() == "role":
                            arn = f"arn:aws:iam::577945324761:role/{name}"
                            print(f"  ARN: {arn}")

                break
else:
    print(f"❌ HTTP Error: {response.status_code}")
