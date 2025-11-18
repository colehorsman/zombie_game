#!/usr/bin/env python3
"""Test ChangeQuarantineStatus mutation."""

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

# The SRN from a real test-user identity
test_srn = "srn:aws:iam::577945324761/User/User/test-user-1"
account = "577945324761"

print(f"Testing ChangeQuarantineStatus mutation for: {test_srn}")
print()

# Try different input formats
mutations_to_try = [
    ("Basic ChangeQuarantineStatus", """
    mutation quarantine($input: ChangeQuarantineStatusInput!) {
        ChangeQuarantineStatus(input: $input) {
            transactionId
            success
            count
        }
    }
    """, {
        "input": {
            "action": "ADD",
            "identities": [
                {
                    "resourceId": test_srn,
                    "account": account,
                    "name": "test-user-1"
                }
            ]
        }
    }),
    ("With rootScope", """
    mutation quarantine($input: ChangeQuarantineStatusInput!) {
        ChangeQuarantineStatus(input: $input) {
            transactionId
            success
            count
        }
    }
    """, {
        "input": {
            "action": "ADD",
            "rootScope": "aws",
            "identities": [
                {
                    "resourceId": test_srn,
                    "scope": "aws",
                    "account": account,
                    "name": "test-user-1"
                }
            ]
        }
    }),
]

for name, mutation, variables in mutations_to_try:
    print(f"{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    print(f"Variables: {json.dumps(variables, indent=2)}")
    print()

    try:
        response = requests.post(
            api_url,
            json={
                "query": mutation,
                "variables": variables
            },
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("errors"):
                error_msg = data['errors'][0].get('message', 'Unknown error')
                print(f"❌ GraphQL Error: {error_msg}")
                if 'extensions' in data['errors'][0]:
                    print(f"Extensions: {json.dumps(data['errors'][0]['extensions'], indent=2)}")
            elif data.get("data"):
                print(f"✓ Success!")
                print(json.dumps(data["data"], indent=2))
            else:
                print("Empty response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()
