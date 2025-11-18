#!/usr/bin/env python3
"""Test different ID formats for quarantine."""

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

# Try different ID formats
test_cases = [
    {
        "name": "Sonrai SRN format",
        "resourceId": "srn:aws:iam::577945324761/User/User/test-user-1",
        "account": "577945324761",
        "userName": "test-user-1"
    },
    {
        "name": "AWS ARN format",
        "resourceId": "arn:aws:iam::577945324761:user/test-user-1",
        "account": "577945324761",
        "userName": "test-user-1"
    },
    {
        "name": "Just the user name",
        "resourceId": "test-user-1",
        "account": "577945324761",
        "userName": "test-user-1"
    },
]

mutation = """
mutation quarantine($input: ChangeQuarantineStatusInput!) {
    ChangeQuarantineStatus(input: $input) {
        transactionId
        success
        count
    }
}
"""

for test_case in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {test_case['name']}")
    print('='*60)
    print(f"Resource ID: {test_case['resourceId']}")

    variables = {
        "input": {
            "action": "ADD",
            "identities": [
                {
                    "resourceId": test_case["resourceId"],
                    "account": test_case["account"],
                    "name": test_case["userName"]
                }
            ]
        }
    }

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
                    classification = data['errors'][0]['extensions'].get('classification', '')
                    print(f"   Classification: {classification}")
            elif data.get("data"):
                result = data["data"].get("ChangeQuarantineStatus", {})
                print(f"✓ Success: {result.get('success')}")
                print(f"  Transaction ID: {result.get('transactionId')}")
                print(f"  Count: {result.get('count')}")
            else:
                print("Empty response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")
