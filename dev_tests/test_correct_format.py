#!/usr/bin/env python3
"""Test with the correct format from the example."""

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

# First, let's try to get the scope path by querying the UnusedIdentities
# to see if we can extract it from there
print("Step 1: Getting scope information from UnusedIdentities query...")

scope_query = """
query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
    UnusedIdentities(where: $filters) {
        items {
            account
            scope
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

response = requests.post(
    api_url,
    json={"query": scope_query, "variables": variables},
    headers=headers,
    timeout=30
)

scope_path = None
root_scope = None

if response.status_code == 200:
    data = response.json()
    if data.get("data") and "UnusedIdentities" in data["data"]:
        items = data["data"]["UnusedIdentities"].get("items", [])
        for item in items:
            if item.get("account") == "577945324761":
                scope_path = item.get("scope")
                if scope_path:
                    # Extract root scope (e.g., "aws/r-xxxxx" from "aws/r-xxxxx/ou-xxxxx/123456")
                    parts = scope_path.split("/")
                    if len(parts) >= 2:
                        root_scope = "/".join(parts[:2])
                    print(f"✓ Found scope: {scope_path}")
                    print(f"✓ Root scope: {root_scope}")
                    break

if not scope_path:
    print("⚠️  Couldn't get scope from API, using placeholder")
    scope_path = "aws/r-xxxxx/ou-xxxxx-yyyyy/577945324761"
    root_scope = "aws/r-xxxxx"

# Now test quarantine with correct format
print("\nStep 2: Testing quarantine with correct format...")

mutation = """
mutation quarantine($input: ChangeQuarantineStatusInput!) {
    ChangeQuarantineStatus(input: $input) {
        transactionId
        success
        count
    }
}
"""

# Convert Sonrai SRN to AWS ARN
# SRN: srn:aws:iam::577945324761/User/User/test-user-1
# ARN: arn:aws:iam::577945324761:user/test-user-1

test_name = "test-user-1"
test_arn = f"arn:aws:iam::577945324761:user/{test_name}"

variables = {
    "input": {
        "identities": [
            {
                "resourceId": test_arn,
                "scope": scope_path,
                "name": test_name,
                "account": "577945324761"
            }
        ],
        "action": "ADD",
        "rootScope": root_scope
    }
}

print(f"Using variables:")
print(json.dumps(variables, indent=2))
print()

response = requests.post(
    api_url,
    json={"query": mutation, "variables": variables},
    headers=headers,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get("errors"):
        error_msg = data['errors'][0].get('message', 'Unknown error')
        print(f"❌ GraphQL Error: {error_msg}")
        if 'extensions' in data['errors'][0]:
            print(f"   Classification: {data['errors'][0]['extensions'].get('classification')}")
    elif data.get("data"):
        result = data["data"].get("ChangeQuarantineStatus", {})
        print(f"✓ Success: {result.get('success')}")
        print(f"  Transaction ID: {result.get('transactionId')}")
        print(f"  Count: {result.get('count')}")
        if result.get('success'):
            print("\n🎉 QUARANTINE WORKED!")
    else:
        print("Empty response")
else:
    print(f"❌ HTTP Error: {response.status_code}")
