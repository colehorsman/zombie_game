#!/usr/bin/env python3
"""Test that we're fetching test-user identities correctly."""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
import os
load_dotenv('.env')

from sonrai_client import SonraiAPIClient

client = SonraiAPIClient(
    api_url=os.getenv('SONRAI_API_URL'),
    org_id=os.getenv('SONRAI_ORG_ID'),
    api_token=os.getenv('SONRAI_API_TOKEN')
)

print('Testing authentication...')
if client.authenticate():
    print('✓ Authentication successful')
    print('\nFetching unused identities from myhealth sandbox (577945324761)...')
    try:
        # Fetch all identities
        identities = client.fetch_unused_identities(limit=1000, scope=None, days_since_login="0", filter_account="577945324761")
        print(f'✓ Found {len(identities)} total unused identities')

        # Filter for test-user identities
        test_users = [i for i in identities if 'test-user' in i.identity_name.lower()]
        print(f'\n✓ Found {len(test_users)} test-user identities')

        if test_users:
            print('\nFirst 20 test-user identities:')
            # Sort by number for better display
            import re
            def get_number(identity):
                match = re.search(r'test-user-(\d+)', identity.identity_name, re.IGNORECASE)
                return int(match.group(1)) if match else 999999

            test_users_sorted = sorted(test_users, key=get_number)

            for i, identity in enumerate(test_users_sorted[:20]):
                print(f'  {i+1}. {identity.identity_name} (Type: {identity.identity_type})')
                print(f'      SRN: {identity.identity_id}')

            # Check if we have the expected ones
            print('\n✓ Verifying specific test users exist:')
            for num in [1, 10, 100, 499]:
                found = any(f'test-user-{num}' == i.identity_name for i in test_users)
                status = '✓' if found else '✗'
                print(f'  {status} test-user-{num}')

        else:
            print('\n⚠️  No test-user identities found')

        # Show distribution of identity types
        print('\nIdentity type distribution:')
        from collections import Counter
        type_counts = Counter(i.identity_type for i in identities)
        for identity_type, count in type_counts.most_common():
            print(f'  {identity_type}: {count}')

    except Exception as e:
        print(f'✗ Error fetching identities: {e}')
else:
    print('✗ Authentication failed')
