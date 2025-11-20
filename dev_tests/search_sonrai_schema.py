#!/usr/bin/env python3
"""
Search the Sonrai GraphQL schema for types, queries, mutations, and fields.

Usage:
    python3 dev_tests/search_sonrai_schema.py --query CloudHierarchy
    python3 dev_tests/search_sonrai_schema.py --type UnusedIdentity
    python3 dev_tests/search_sonrai_schema.py --mutation Quarantine
    python3 dev_tests/search_sonrai_schema.py --field daysSinceLogin
"""

import json
import argparse
from pathlib import Path


def load_schema():
    """Load the downloaded schema."""
    schema_file = Path(__file__).parent.parent / "docs" / "sonrai-api" / "schema.json"
    if not schema_file.exists():
        print(f"Error: Schema file not found at {schema_file}")
        print("Run: python3 dev_tests/download_sonrai_schema.py")
        return None

    with open(schema_file, "r") as f:
        return json.load(f)


def format_type_ref(type_ref):
    """Format a type reference for display."""
    if not type_ref:
        return "Unknown"

    kind = type_ref.get("kind")
    name = type_ref.get("name")

    if kind == "NON_NULL":
        inner = format_type_ref(type_ref.get("ofType"))
        return f"{inner}!"
    elif kind == "LIST":
        inner = format_type_ref(type_ref.get("ofType"))
        return f"[{inner}]"
    elif name:
        return name
    else:
        return format_type_ref(type_ref.get("ofType"))


def search_queries(schema, pattern):
    """Search for queries matching a pattern."""
    types = schema["data"]["__schema"]["types"]
    query_type_name = schema["data"]["__schema"]["queryType"]["name"]
    query_type = next((t for t in types if t.get("name") == query_type_name), None)

    if not query_type:
        print("No query type found")
        return

    queries = query_type.get("fields", [])
    matching = [q for q in queries if pattern.lower() in q.get("name", "").lower()]

    if not matching:
        print(f"No queries found matching '{pattern}'")
        return

    for query in matching:
        print(f"\n{'='*80}")
        print(f"Query: {query['name']}")
        if query.get("description"):
            print(f"Description: {query['description']}")
        print(f"Returns: {format_type_ref(query.get('type'))}")

        args = query.get("args", [])
        if args:
            print(f"\nArguments:")
            for arg in args:
                arg_type = format_type_ref(arg.get("type"))
                arg_desc = f" - {arg['description']}" if arg.get("description") else ""
                print(f"  {arg['name']}: {arg_type}{arg_desc}")


def search_mutations(schema, pattern):
    """Search for mutations matching a pattern."""
    types = schema["data"]["__schema"]["types"]
    mutation_type_name = schema["data"]["__schema"]["mutationType"]["name"]
    mutation_type = next((t for t in types if t.get("name") == mutation_type_name), None)

    if not mutation_type:
        print("No mutation type found")
        return

    mutations = mutation_type.get("fields", [])
    matching = [m for m in mutations if pattern.lower() in m.get("name", "").lower()]

    if not matching:
        print(f"No mutations found matching '{pattern}'")
        return

    for mutation in matching:
        print(f"\n{'='*80}")
        print(f"Mutation: {mutation['name']}")
        if mutation.get("description"):
            print(f"Description: {mutation['description']}")
        print(f"Returns: {format_type_ref(mutation.get('type'))}")

        args = mutation.get("args", [])
        if args:
            print(f"\nArguments:")
            for arg in args:
                arg_type = format_type_ref(arg.get("type"))
                arg_desc = f" - {arg['description']}" if arg.get("description") else ""
                print(f"  {arg['name']}: {arg_type}{arg_desc}")


def search_types(schema, pattern):
    """Search for types matching a pattern."""
    types = schema["data"]["__schema"]["types"]
    matching = [t for t in types if pattern.lower() in t.get("name", "").lower()]

    if not matching:
        print(f"No types found matching '{pattern}'")
        return

    for type_def in matching:
        print(f"\n{'='*80}")
        print(f"Type: {type_def['name']} ({type_def['kind']})")
        if type_def.get("description"):
            print(f"Description: {type_def['description']}")

        fields = type_def.get("fields")
        if fields:
            print(f"\nFields ({len(fields)}):")
            for field in fields[:20]:  # Limit to first 20 fields
                field_type = format_type_ref(field.get("type"))
                field_desc = f" - {field['description']}" if field.get("description") else ""
                print(f"  {field['name']}: {field_type}{field_desc}")
            if len(fields) > 20:
                print(f"  ... and {len(fields) - 20} more fields")

        input_fields = type_def.get("inputFields")
        if input_fields:
            print(f"\nInput Fields ({len(input_fields)}):")
            for field in input_fields[:20]:
                field_type = format_type_ref(field.get("type"))
                field_desc = f" - {field['description']}" if field.get("description") else ""
                print(f"  {field['name']}: {field_type}{field_desc}")
            if len(input_fields) > 20:
                print(f"  ... and {len(input_fields) - 20} more fields")

        enum_values = type_def.get("enumValues")
        if enum_values:
            print(f"\nEnum Values:")
            for val in enum_values:
                val_desc = f" - {val['description']}" if val.get("description") else ""
                print(f"  {val['name']}{val_desc}")


def search_fields(schema, pattern):
    """Search for fields across all types."""
    types = schema["data"]["__schema"]["types"]
    results = []

    for type_def in types:
        # Search in object fields
        fields = type_def.get("fields", [])
        for field in fields:
            if pattern.lower() in field.get("name", "").lower():
                results.append((type_def["name"], field))

        # Search in input fields
        input_fields = type_def.get("inputFields", [])
        for field in input_fields:
            if pattern.lower() in field.get("name", "").lower():
                results.append((f"{type_def['name']} (input)", field))

    if not results:
        print(f"No fields found matching '{pattern}'")
        return

    print(f"\nFound {len(results)} fields matching '{pattern}':")
    for type_name, field in results[:50]:  # Limit to 50 results
        field_type = format_type_ref(field.get("type"))
        print(f"\n  {type_name}.{field['name']}: {field_type}")
        if field.get("description"):
            print(f"    {field['description']}")

    if len(results) > 50:
        print(f"\n  ... and {len(results) - 50} more matches")


def main():
    parser = argparse.ArgumentParser(description="Search the Sonrai GraphQL schema")
    parser.add_argument("--query", "-q", help="Search for queries")
    parser.add_argument("--mutation", "-m", help="Search for mutations")
    parser.add_argument("--type", "-t", help="Search for types")
    parser.add_argument("--field", "-f", help="Search for fields")
    parser.add_argument("--stats", "-s", action="store_true", help="Show schema statistics")

    args = parser.parse_args()

    schema = load_schema()
    if not schema:
        return

    if args.query:
        search_queries(schema, args.query)
    elif args.mutation:
        search_mutations(schema, args.mutation)
    elif args.type:
        search_types(schema, args.type)
    elif args.field:
        search_fields(schema, args.field)
    elif args.stats:
        types = schema["data"]["__schema"]["types"]
        queries = schema["data"]["__schema"]["queryType"]
        mutations = schema["data"]["__schema"]["mutationType"]

        query_type = next((t for t in types if t.get("name") == queries["name"]), None)
        mutation_type = next((t for t in types if t.get("name") == mutations["name"]), None)

        print(f"\nSonrai GraphQL Schema Statistics:")
        print(f"  Total Types: {len(types)}")
        print(f"  Available Queries: {len(query_type.get('fields', []))}")
        print(f"  Available Mutations: {len(mutation_type.get('fields', []))}")

        # Count by kind
        type_counts = {}
        for t in types:
            kind = t.get("kind", "UNKNOWN")
            type_counts[kind] = type_counts.get(kind, 0) + 1

        print(f"\nTypes by Kind:")
        for kind, count in sorted(type_counts.items()):
            print(f"  {kind}: {count}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
