#!/usr/bin/env python3
"""Test different scope path variations."""

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

mutation = """
mutation quarantine($input: ChangeQuarantineStatusInput!) {
    ChangeQuarantineStatus(input: $input) {
        transactionId
        success
        count
    }
}
"""

test_name = "test-user-101"
test_arn = f"arn:aws:iam::577945324761:user/{test_name}"
account = "577945324761"

# Try different scope variations
scope_variations = [
    {
        "name": "Original with spaces",
        "scope": "aws/Sonrai MyHealth - Org/Sandbox/MyHealth - Sandbox",
        "rootScope": "aws/Sonrai MyHealth - Org"
    },
    {
        "name": "With account appended",
        "scope": f"aws/Sonrai MyHealth - Org/Sandbox/MyHealth - Sandbox/{account}",
        "rootScope": "aws/Sonrai MyHealth - Org"
    },
    {
        "name": "URL encoded spaces",
        "scope": "aws/Sonrai%20MyHealth%20-%20Org/Sandbox/MyHealth%20-%20Sandbox",
        "rootScope": "aws/Sonrai%20MyHealth%20-%20Org"
    },
    {
        "name": "Just aws as scope",
        "scope": "aws",
        "rootScope": "aws"
    },
]

for variation in scope_variations:
    print(f"\n{'='*60}")
    print(f"Testing: {variation['name']}")
    print('='*60)
    print(f"Scope: {variation['scope']}")
    print(f"Root Scope: {variation['rootScope']}")

    variables = {
        "input": {
            "identities": [
                {
                    "resourceId": test_arn,
                    "scope": variation['scope'],
                    "name": test_name,
                    "account": account
                }
            ],
            "action": "ADD",
            "rootScope": variation['rootScope']
        }
    }

    try:
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
                print(f"\n❌ Error: {error_msg[:100]}")
            elif data.get("data"):
                result = data["data"].get("ChangeQuarantineStatus", {})
                print(f"\n✓ Success: {result.get('success')}")
                print(f"  Transaction ID: {result.get('transactionId')}")
                print(f"  Count: {result.get('count')}")
                if result.get('success'):
                    print("\n🎉 THIS VARIATION WORKED!")
                    print(f"Use these values:")
                    print(f"  scope = \"{variation['scope']}\"")
                    print(f"  rootScope = \"{variation['rootScope']}\"")
                    break
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Exception: {e}")
