#!/usr/bin/env python3
"""Test different Sonrai GraphQL queries to find unused identities."""

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

# Try different query patterns
queries_to_try = [
    ("Try ExecuteQuery", """
    {
        ExecuteQuery(query: "has(srn) and resourceType = 'User' limit 10") {
            Count
            Items
        }
    }
    """),
    ("Try SearchResources", """
    {
        SearchResources(query: "resourceType = 'User' limit 10") {
            count
            items {
                srn
                name
            }
        }
    }
    """),
    ("Try simple query", """
    {
        query(query: "has(srn) limit 5") {
            Count
            Items
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
