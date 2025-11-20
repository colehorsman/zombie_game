#!/usr/bin/env python3
"""
Download the complete Sonrai GraphQL schema using introspection.

This script queries the Sonrai API for its complete schema definition and saves it
to docs/sonrai-api/schema.json for reference when building new queries.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SONRAI_API_URL = os.getenv("SONRAI_API_URL")
SONRAI_API_TOKEN = os.getenv("SONRAI_API_TOKEN")
SONRAI_ORG_ID = os.getenv("SONRAI_ORG_ID")

# GraphQL introspection query to get the full schema
INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
"""


def download_schema():
    """Download the Sonrai GraphQL schema via introspection."""
    if not all([SONRAI_API_URL, SONRAI_API_TOKEN, SONRAI_ORG_ID]):
        print("Error: Missing required environment variables")
        print("Please ensure SONRAI_API_URL, SONRAI_API_TOKEN, and SONRAI_ORG_ID are set in .env")
        sys.exit(1)

    print(f"Downloading Sonrai GraphQL schema from {SONRAI_API_URL}...")

    headers = {
        "Authorization": f"Bearer {SONRAI_API_TOKEN}",
        "Content-Type": "application/json",
        "sonrai-org-id": SONRAI_ORG_ID,
    }

    try:
        response = requests.post(
            SONRAI_API_URL,
            json={"query": INTROSPECTION_QUERY},
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        schema_data = response.json()

        if "errors" in schema_data:
            print(f"GraphQL errors: {schema_data['errors']}")
            sys.exit(1)

        # Save to docs/sonrai-api/schema.json
        output_dir = Path(__file__).parent.parent / "docs" / "sonrai-api"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "schema.json"

        with open(output_file, "w") as f:
            json.dump(schema_data, f, indent=2)

        print(f"✅ Schema downloaded successfully to {output_file}")

        # Print some stats
        if "data" in schema_data and "__schema" in schema_data["data"]:
            schema = schema_data["data"]["__schema"]
            types = schema.get("types", [])

            # Count different type kinds
            type_counts = {}
            for t in types:
                kind = t.get("kind", "UNKNOWN")
                type_counts[kind] = type_counts.get(kind, 0) + 1

            print(f"\nSchema Statistics:")
            print(f"  Total types: {len(types)}")
            for kind, count in sorted(type_counts.items()):
                print(f"  {kind}: {count}")

            # Find query and mutation types
            query_type = schema.get("queryType", {}).get("name")
            mutation_type = schema.get("mutationType", {}).get("name")

            if query_type:
                query_type_def = next((t for t in types if t.get("name") == query_type), None)
                if query_type_def:
                    queries = query_type_def.get("fields", [])
                    print(f"\n  Available Queries: {len(queries)}")

            if mutation_type:
                mutation_type_def = next((t for t in types if t.get("name") == mutation_type), None)
                if mutation_type_def:
                    mutations = mutation_type_def.get("fields", [])
                    print(f"  Available Mutations: {len(mutations)}")

        return output_file

    except requests.exceptions.RequestException as e:
        print(f"Error downloading schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    download_schema()
