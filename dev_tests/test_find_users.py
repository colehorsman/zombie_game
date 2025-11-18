#!/usr/bin/env python3
"""Find test-user identities using Sonrai's ExecuteQuery."""

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

# Try to find User resources with test-user in the name
queries_to_try = [
    ("Find all Users", """
    query {
        ExecuteQuery(query: "resourceType = 'User' and account = '577945324761' limit 10") {
            Count
            Items
        }
    }
    """),
    ("Find test-user pattern", """
    query {
        ExecuteQuery(query: "resourceType = 'User' and name contains 'test-user' and account = '577945324761' limit 10") {
            Count
            Items
        }
    }
    """),
    ("Get User details with fields", """
    query {
        Resources(
            where: {
                resourceType: {op: EQ, value: "User"}
                account: {op: EQ, value: "577945324761"}
            }
            limit: 10
        ) {
            count
            items {
                srn
                name
                resourceType
                account
            }
        }
    }
    """),
]

for name, query in queries_to_try:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)

    try:
        response = requests.post(
            api_url,
            json={"query": query},
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("errors"):
                print(f"❌ Error: {data['errors'][0].get('message')}")
            elif data.get("data"):
                print(f"✓ Success!")
                print(json.dumps(data["data"], indent=2))
            else:
                print("Empty response")
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"Exception: {e}")
