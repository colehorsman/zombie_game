#!/usr/bin/env python3
"""Test quarantine with scope fields."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
import json
load_dotenv('.env')

import requests

api_url = os.getenv('SONRAI_API_URL')
api_token = os.getenv('SONRAI_API_TOKEN')
org_id = os.getenv('SONRAI_ORG_ID')

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

# Try different scope configurations
test_cases = [
    {
        "name": "With rootScope only",
        "variables": {
            "input": {
                "action": "ADD",
                "rootScope": "aws",
                "identities": [
                    {
                        "resourceId": "srn:aws:iam::577945324761/User/User/test-user-1",
                        "account": "577945324761",
                        "name": "test-user-1"
                    }
                ]
            }
        }
    },
    {
        "name": "With scope in identity",
        "variables": {
            "input": {
                "action": "ADD",
                "identities": [
                    {
                        "resourceId": "srn:aws:iam::577945324761/User/User/test-user-1",
                        "scope": "aws/r-xxxx/ou-xxxx-xxxxx/577945324761",
                        "account": "577945324761",
                        "name": "test-user-1"
                    }
                ]
            }
        }
    },
    {
        "name": "With both rootScope and scope",
        "variables": {
            "input": {
                "action": "ADD",
                "rootScope": f"aws/{org_id}",
                "identities": [
                    {
                        "resourceId": "srn:aws:iam::577945324761/User/User/test-user-1",
                        "scope": "aws",
                        "account": "577945324761",
                        "name": "test-user-1"
                    }
                ]
            }
        }
    },
]

for test_case in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {test_case['name']}")
    print('='*60)
    print(f"Variables: {json.dumps(test_case['variables'], indent=2)}")

    try:
        response = requests.post(
            api_url,
            json={
                "query": mutation,
                "variables": test_case["variables"]
            },
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("errors"):
                error_msg = data['errors'][0].get('message', 'Unknown error')
                print(f"\n❌ GraphQL Error: {error_msg}")
            elif data.get("data"):
                result = data["data"].get("ChangeQuarantineStatus", {})
                print(f"\n✓ Success: {result.get('success')}")
                print(f"  Transaction ID: {result.get('transactionId')}")
                print(f"  Count: {result.get('count')}")
                if result.get('success'):
                    print("\n🎉 QUARANTINE WORKED!")
                    break
            else:
                print("\nEmpty response")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Exception: {e}")
