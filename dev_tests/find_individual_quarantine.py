#!/usr/bin/env python3
"""Try to find the correct mutation for individual identity quarantine."""

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

test_srn = "srn:aws:iam::577945324761/User/User/test-user-200"
test_arn = "arn:aws:iam::577945324761:user/test-user-200"
test_name = "test-user-200"
account = "577945324761"
scope = f"aws/Sonrai MyHealth - Org/Sandbox/MyHealth - Sandbox/{account}"
root_scope = "aws/Sonrai MyHealth - Org"

# Try different mutation names
mutations_to_try = [
    ("QuarantineIdentity", """
    mutation QuarantineIdentity($srn: ID!) {
        QuarantineIdentity(srn: $srn) {
            success
        }
    }
    """, {"srn": test_srn}),

    ("QuarantineUser", """
    mutation QuarantineUser($srn: ID!) {
        QuarantineUser(srn: $srn) {
            success
        }
    }
    """, {"srn": test_srn}),

    ("QuarantineResource", """
    mutation QuarantineResource($resourceId: ID!) {
        QuarantineResource(resourceId: $resourceId) {
            success
        }
    }
    """, {"resourceId": test_arn}),

    ("AddToQuarantine", """
    mutation AddToQuarantine($srn: ID!) {
        AddToQuarantine(srn: $srn) {
            success
        }
    }
    """, {"srn": test_srn}),
]

print("Testing individual quarantine mutations...\n")

for name, mutation, variables in mutations_to_try:
    print(f"{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

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
                error_msg = data['errors'][0].get('message', '')
                if 'undefined' in error_msg.lower():
                    print(f"❌ {name} doesn't exist")
                else:
                    print(f"❌ Error: {error_msg[:100]}")
            elif data.get("data"):
                print(f"✓ {name} EXISTS!")
                print(json.dumps(data["data"], indent=2))
                print("\n🎉 FOUND THE RIGHT MUTATION!")
                break
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    print()

print("\n" + "="*60)
print("If none worked, check the Sonrai UI network tab!")
print("Or check docs at: https://docs.sonraisecurity.com")
