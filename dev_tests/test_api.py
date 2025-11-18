#!/usr/bin/env python3
"""Test script to verify Sonrai API connection."""

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
        # Fetch with account filter
        identities = client.fetch_unused_identities(limit=1000, scope=None, days_since_login="0", filter_account="577945324761")
        print(f'✓ Found {len(identities)} unused identities')
        if identities:
            print('\nFirst 10 identities:')
            for i, identity in enumerate(identities[:10]):
                print(f'  {i+1}. {identity.identity_name} (Type: {identity.identity_type})')
                print(f'      SRN: {identity.identity_id}')
        else:
            print('\n⚠️  No unused identities found')
            print('Try checking the scope path in Sonrai UI')
    except Exception as e:
        print(f'✗ Error fetching identities: {e}')
else:
    print('✗ Authentication failed')
