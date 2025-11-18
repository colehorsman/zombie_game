#!/usr/bin/env python3
"""Test different remediation/bot approaches in Sonrai."""

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

print(f"Testing remediation approaches for: {test_srn}")
print()

# Try different remediation approaches
mutations_to_try = [
    ("CreateTicket mutation", """
    mutation CreateTicket($input: CreateTicketInput!) {
        CreateTicket(value: $input) {
            ticket
        }
    }
    """, {
        "input": {
            "resourceId": test_srn,
            "title": "Quarantine unused identity",
            "botId": "quarantine-bot"
        }
    }),
    ("RunBot mutation", """
    mutation RunBot($srn: ID!, $botId: ID!) {
        RunBot(srn: $srn, botId: $botId) {
            success
        }
    }
    """, {"srn": test_srn, "botId": "quarantine-unused-identity"}),
    ("ExecuteBot mutation", """
    mutation ExecuteBot($resourceSrn: ID!) {
        ExecuteBot(resourceSrn: $resourceSrn) {
            success
        }
    }
    """, {"resourceSrn": test_srn}),
    ("Simple CreateTicket", """
    mutation {
        CreateTicket(value: {
            resourceId: "%s"
            title: "Quarantine test-user-1"
        }) {
            ticket
        }
    }
    """ % test_srn, None),
]

for item in mutations_to_try:
    if len(item) == 3:
        name, mutation, variables = item
    else:
        name, mutation = item
        variables = None

    print(f"{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

    try:
        payload = {"query": mutation}
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
                print(f"❌ GraphQL Error: {error_msg}")
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
