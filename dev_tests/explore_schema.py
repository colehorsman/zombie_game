#!/usr/bin/env python3
"""Explore Sonrai GraphQL schema to find unused identities and quarantine operations."""

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

# Introspection query to explore the schema
introspection_query = """
{
  __schema {
    queryType {
      fields {
        name
        description
      }
    }
    mutationType {
      fields {
        name
        description
      }
    }
  }
}
"""

print("Fetching GraphQL schema...")
response = requests.post(
    api_url,
    json={"query": introspection_query},
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response text: {response.text[:500]}")

if response.status_code == 200:
    try:
        data = response.json()
    except:
        print("Failed to parse JSON")
        sys.exit(1)
    
    if not data:
        print("Empty response")
        sys.exit(1)
    
    print("\n=== QUERY FIELDS (searching for 'unused', 'identity', 'zombie') ===")
    if data and data.get("data") and data["data"].get("__schema") and data["data"]["__schema"].get("queryType"):
        for field in data["data"]["__schema"]["queryType"]["fields"]:
            name = field["name"].lower()
            desc = (field.get("description") or "").lower()
            if any(keyword in name or keyword in desc for keyword in ["unused", "identity", "zombie", "user", "permission"]):
                print(f"\n{field['name']}")
                if field.get("description"):
                    print(f"  Description: {field['description']}")
    
    print("\n\n=== MUTATION FIELDS (searching for 'quarantine', 'delete', 'remove') ===")
    if data.get("data", {}).get("__schema", {}).get("mutationType"):
        for field in data["data"]["__schema"]["mutationType"]["fields"]:
            name = field["name"].lower()
            desc = (field.get("description") or "").lower()
            if any(keyword in name or keyword in desc for keyword in ["quarantine", "delete", "remove", "disable"]):
                print(f"\n{field['name']}")
                if field.get("description"):
                    print(f"  Description: {field['description']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
