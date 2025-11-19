"""Sonrai API client for fetching and quarantining unused identities."""

import logging
import time
from typing import List, Optional

import requests

from models import UnusedIdentity, QuarantineResult


logger = logging.getLogger(__name__)


class SonraiAPIClient:
    """Handles all communication with the Sonrai Security API."""

    def __init__(self, api_url: str, org_id: str, api_token: str):
        """
        Initialize the Sonrai API client.

        Args:
            api_url: GraphQL endpoint URL for the Sonrai API
            org_id: Organization ID
            api_token: API authentication token
        """
        self.api_url = api_url
        self.org_id = org_id
        self.api_token = api_token

    def authenticate(self) -> bool:
        """
        Verify the API token is valid.

        Returns:
            True if authentication successful, False otherwise
        """
        # For Sonrai GraphQL API, we just verify the token works
        try:
            # Simple query to test authentication
            query = """
            query {
                __typename
            }
            """
            response = requests.post(
                self.api_url,
                json={"query": query},
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            logger.info("Successfully authenticated with Sonrai API")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _get_headers(self) -> dict:
        """
        Get request headers with authentication token.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def fetch_accounts_with_unused_identities(self) -> dict:
        """
        Fetch all AWS accounts in the org with their unused identity counts.

        Returns:
            Dictionary mapping account numbers to counts: {account_num: count}
        """
        try:
            query = """
            query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
                UnusedIdentities(where: $filters) {
                    items {
                        account
                        count
                    }
                }
            }
            """

            variables = {
                "filters": {
                    "scope": {
                        "value": "aws",
                        "op": "STARTS_WITH"
                    },
                    "daysSinceLastLogin": {
                        "op": "GTE",
                        "value": "0"
                    }
                }
            }

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            accounts = {}
            if data and "data" in data and "UnusedIdentities" in data["data"]:
                items = data["data"]["UnusedIdentities"].get("items", [])
                for item in items:
                    account = item.get("account", "Unknown")
                    count = item.get("count", 0)
                    accounts[account] = count

            logger.info(f"Fetched {len(accounts)} accounts with unused identities")
            return accounts

        except Exception as e:
            logger.error(f"Failed to fetch accounts: {e}")
            return {}

    def fetch_third_parties_by_account(self, root_scope: str = "aws/r-ipxz") -> dict:
        """
        Fetch 3rd party access information per AWS account from Sonrai API.

        Args:
            root_scope: Root AWS organization scope (e.g., "aws/r-ipxz")

        Returns:
            Dictionary mapping account numbers to lists of 3rd party info:
            {
                "577945324761": [
                    {"name": "nOps", "status": "Granted"},
                    {"name": "Cloudflare", "status": "Granted"},
                    ...
                ]
            }
        """
        try:
            # Query for 3rd parties using the ThirdParties endpoint
            query = """
            query getThirdParties($scope: String!) {
                ThirdParties(where: { scope: { value: $scope, op: EQ } }) {
                    items {
                        thirdPartyFriendlyName
                        status {
                            state
                        }
                        resources {
                            service
                            resourceType
                            count
                        }
                        accountCount
                        lastAccessed
                        labels {
                            name
                            severity
                        }
                        thirdPartyId
                    }
                }
            }
            """

            variables = {"scope": root_scope}

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Group 3rd parties by account
            # Note: The ThirdParties query returns org-level data, so we'll create entries for all accounts
            third_parties_by_account = {}

            if data and "data" in data and data["data"] is not None and isinstance(data["data"], dict) and "ThirdParties" in data["data"]:
                items = data["data"]["ThirdParties"].get("items", []) if data["data"]["ThirdParties"] else []

                logger.info(f"Fetched {len(items)} 3rd parties from Sonrai API")

                # Since ThirdParties query returns org-level data, we'll need to associate them with accounts
                # For now, we'll return them as a general list that can be distributed across accounts
                # TODO: Query each account individually if needed for account-specific 3rd parties

                for item in items:
                    third_party_name = item.get("thirdPartyFriendlyName", "Unknown")

                    # Skip if name is None or empty
                    if not third_party_name or third_party_name == "Unknown":
                        continue

                    status_obj = item.get("status", {})
                    status = status_obj.get("state", "Unknown") if status_obj else "Unknown"

                    # For now, add to a generic "all" key since we don't have per-account mapping
                    # The caller can distribute these across accounts as needed
                    if "all" not in third_parties_by_account:
                        third_parties_by_account["all"] = []

                    third_parties_by_account["all"].append({
                        "name": third_party_name,
                        "status": status,
                        "thirdPartyId": item.get("thirdPartyId", ""),
                        "accountCount": item.get("accountCount", 0)
                    })

            total_parties = sum(len(parties) for parties in third_parties_by_account.values())
            logger.info(f"Processed {total_parties} 3rd party entries")
            return third_parties_by_account

        except Exception as e:
            import traceback
            logger.error(f"Failed to fetch 3rd parties: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    def fetch_unused_identities(self, limit: int = 500, scope: str = None, days_since_login: str = "0", filter_account: str = "577945324761") -> List[UnusedIdentity]:
        """
        Fetch unused identities from the Sonrai API using the UnusedIdentities query.

        Args:
            limit: Maximum number of identities to fetch
            scope: Full scope path (e.g., "aws/r-xxxxx/ou-xxxx-yyyyy/577945324761")
            days_since_login: Minimum days since last login (default: "0" for all)
            filter_account: AWS account number to filter (default: "577945324761")

        Returns:
            List of UnusedIdentity objects with real identity names from Sonrai
        """
        try:
            # Query for unused identities with individual identity details
            query = """
            query getUnusedIdentities($filters: UnusedIdentitiesFilter!) {
                UnusedIdentities(where: $filters) {
                    items {
                        account
                        count
                        identities {
                            srn
                        }
                    }
                }
            }
            """

            # Build filters - both scope and daysSinceLastLogin are required
            # If no scope provided, try to match the account number
            if not scope:
                # Try matching paths that contain the account number
                scope_filter = {
                    "value": "aws",
                    "op": "STARTS_WITH"
                }
            else:
                scope_filter = {
                    "value": scope,
                    "op": "EQ"
                }

            variables = {
                "filters": {
                    "scope": scope_filter,
                    "daysSinceLastLogin": {
                        "op": "GTE",
                        "value": days_since_login
                    }
                }
            }

            headers = self._get_headers()
            response = requests.post(
                self.api_url,
                json={
                    "query": query,
                    "variables": variables
                },
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            identities = []

            # Check for GraphQL errors
            if data and "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
                logger.error(f"GraphQL error: {error_msg}")
                raise Exception(f"GraphQL error: {error_msg}")

            # Parse GraphQL response
            if data and "data" in data and data["data"] and "UnusedIdentities" in data["data"]:
                items = data["data"]["UnusedIdentities"].get("items", [])

                # Each item represents a group of unused identities by account
                for item in items:
                    account = item.get("account", "unknown")

                    # Filter to only the specified account if provided
                    if filter_account and account != filter_account:
                        continue

                    # Get individual identities
                    identity_list = item.get("identities", [])

                    for identity_data in identity_list:
                        srn = identity_data.get("srn", "")

                        # Extract name from SRN (after last /)
                        name = srn.split("/")[-1] if "/" in srn else srn

                        # Extract resource type from SRN (second to last part)
                        srn_parts = srn.split("/")
                        resource_type = srn_parts[-2] if len(srn_parts) > 1 else "Unknown"

                        # Create identity object
                        identity = UnusedIdentity(
                            identity_id=srn,
                            identity_name=name,
                            identity_type=resource_type,
                            last_used=None,
                            risk_score=0.0
                        )
                        identities.append(identity)

                logger.info(f"Fetched {len(identities)} unused identities from Sonrai (before limit)")
            else:
                logger.warning("No unused identities found in response")

            # Apply limit and log
            if len(identities) > limit:
                logger.info(f"Limiting from {len(identities)} to {limit} identities")
                return identities[:limit]
            else:
                logger.info(f"Returning all {len(identities)} identities (under limit of {limit})")
                return identities

        except Exception as e:
            logger.error(f"Failed to fetch unused identities: {e}")
            raise

    def fetch_exemptions(self, account: str) -> List[dict]:
        """
        Fetch exempted identities for a specific AWS account from Sonrai API.

        Args:
            account: AWS account number to fetch exemptions for

        Returns:
            List of exemption dictionaries with resourceId, resourceName, exemptionReason, expirationDate
        """
        query = """
        query GetExemptedIdentities($filters: AppliedExemptedIdentitiesFilter!) {
            AppliedExemptedIdentities(where: $filters) {
                count
                items {
                    id
                    identity
                    scope
                    scopeFriendlyName
                    approvedBy
                    approvedAt
                    isCoreExemption
                }
            }
        }
        """

        # Build scope filter for the specific account
        scope_filter = f"aws/{account}"
        
        variables = {
            "filters": {
                "scope": {
                    "value": scope_filter,
                    "op": "EQ"
                }
            }
        }

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers=self._get_headers(),
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    
                    if 'errors' in data:
                        logger.error(f"GraphQL errors in exemptions query: {data['errors']}")
                        return []
                    
                    exemptions_data = data.get('data', {}).get('AppliedExemptedIdentities', {}).get('items', [])
                    logger.info(f"Fetched {len(exemptions_data)} exempted identities for account {account}")
                    return exemptions_data
                else:
                    logger.error(f"Failed to fetch exemptions: HTTP {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return []

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching exemptions (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return []
            except Exception as e:
                logger.error(f"Error fetching exemptions: {e}")
                return []

        return []

    def quarantine_identity(self, identity_id: str, identity_name: str = None, account: str = None, scope: str = None, root_scope: str = None) -> QuarantineResult:
        """
        Send a quarantine request for a specific identity using GraphQL mutation.

        Args:
            identity_id: SRN of the identity to quarantine
            identity_name: Name of the identity (extracted from SRN if not provided)
            account: AWS account number (extracted from SRN if not provided)
            scope: Organizational scope path (uses default if not provided)
            root_scope: Root organizational scope (uses default if not provided)

        Returns:
            QuarantineResult with success status and any error message
        """
        max_retries = 3
        retry_delay = 1.0

        # Extract name and account from SRN if not provided
        if not identity_name:
            identity_name = identity_id.split("/")[-1] if "/" in identity_id else identity_id

        if not account:
            # Try to extract account from SRN format: srn:aws:iam::ACCOUNT/...
            parts = identity_id.split("::")
            if len(parts) > 1:
                account = parts[1].split("/")[0]

        # Convert Sonrai SRN to AWS ARN format
        # SRN: srn:aws:iam::577945324761/User/User/test-user-1
        # ARN: arn:aws:iam::577945324761:user/test-user-1
        resource_arn = identity_id
        if identity_id.startswith("srn:"):
            # Extract parts from SRN
            if "/User/" in identity_id:
                resource_arn = f"arn:aws:iam::{account}:user/{identity_name}"
            elif "/Role/" in identity_id:
                resource_arn = f"arn:aws:iam::{account}:role/{identity_name}"

        # Use default scope values if not provided
        # Real scope from Sonrai API (internal IDs, not display names)
        if not scope:
            scope = f"aws/r-ipxz/ou-ipxz-95f072k5/{account}"
        if not root_scope:
            root_scope = "aws/r-ipxz"

        for attempt in range(max_retries):
            try:
                # GraphQL mutation to quarantine the identity
                mutation = """
                mutation quarantine($input: ChangeQuarantineStatusInput!) {
                    ChangeQuarantineStatus(input: $input) {
                        transactionId
                        success
                        count
                    }
                }
                """

                # Build input for the mutation
                variables = {
                    "input": {
                        "identities": [
                            {
                                "resourceId": resource_arn,
                                "scope": scope,
                                "name": identity_name,
                                "account": account
                            }
                        ],
                        "action": "ADD",
                        "rootScope": root_scope
                    }
                }

                headers = self._get_headers()
                response = requests.post(
                    self.api_url,
                    json={
                        "query": mutation,
                        "variables": variables
                    },
                    headers=headers,
                    timeout=15
                )
                response.raise_for_status()

                data = response.json()

                # Check for GraphQL errors
                if "errors" in data:
                    error_msg = data["errors"][0].get("message", "Unknown error")
                    raise Exception(error_msg)

                # Check if the mutation was successful
                if data.get("data") and data["data"].get("ChangeQuarantineStatus"):
                    result = data["data"]["ChangeQuarantineStatus"]
                    if result.get("success"):
                        logger.info(f"Successfully quarantined identity {identity_id}")
                        return QuarantineResult(
                            success=True,
                            identity_id=identity_id,
                            error_message=None
                        )
                    else:
                        raise Exception(f"Quarantine returned success=false, count={result.get('count')}")

                raise Exception("Unexpected response format")

            except Exception as e:
                logger.warning(
                    f"Quarantine attempt {attempt + 1}/{max_retries} failed for {identity_id}: {e}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    # Final attempt failed
                    error_msg = str(e)
                    logger.error(f"Failed to quarantine identity {identity_id}: {error_msg}")
                    return QuarantineResult(
                        success=False,
                        identity_id=identity_id,
                        error_message=error_msg
                    )

        # Should not reach here, but return failure just in case
        return QuarantineResult(
            success=False,
            identity_id=identity_id,
            error_message="Max retries exceeded"
        )

    def block_third_party(self, third_party_id: str, third_party_name: str = None, root_scope: str = None) -> QuarantineResult:
        """
        Block/deny a 3rd party's access using GraphQL mutation.

        Args:
            third_party_id: UUID of the 3rd party to block
            third_party_name: Name of the 3rd party (for logging)
            root_scope: Root organizational scope (uses default if not provided)

        Returns:
            QuarantineResult with success status and any error message
        """
        max_retries = 3
        retry_delay = 1.0

        # Use default scope if not provided
        if not root_scope:
            root_scope = "aws/r-ipxz"

        for attempt in range(max_retries):
            try:
                # GraphQL mutation to block the 3rd party
                mutation = """
                mutation blockThirdParty($thirdPartyId: String!, $scope: String!) {
                    DenyThirdPartyAccess(input: { thirdPartyId: $thirdPartyId, scope: $scope }) {
                        success
                    }
                }
                """

                # Build input for the mutation
                variables = {
                    "thirdPartyId": third_party_id,
                    "scope": root_scope
                }

                # Log the request details (only on first attempt to avoid spam)
                if attempt == 0:
                    logger.info(f"Blocking 3rd party {third_party_name or third_party_id} with ID: {third_party_id[:8]}... scope: {root_scope}")

                headers = self._get_headers()
                response = requests.post(
                    self.api_url,
                    json={
                        "query": mutation,
                        "variables": variables
                    },
                    headers=headers,
                    timeout=15
                )
                response.raise_for_status()

                data = response.json()

                # Log the full response if there are errors
                if "errors" in data:
                    logger.info(f"API error response for {third_party_name or third_party_id}: {data}")

                # Check for GraphQL errors
                if "errors" in data:
                    error_msg = data["errors"][0].get("message", "Unknown error")
                    raise Exception(error_msg)

                # Check if the mutation was successful
                if data.get("data") and data["data"].get("DenyThirdPartyAccess"):
                    result = data["data"]["DenyThirdPartyAccess"]
                    if result.get("success"):
                        logger.info(f"Successfully blocked 3rd party {third_party_name or third_party_id}")
                        return QuarantineResult(
                            success=True,
                            identity_id=third_party_id,
                            error_message=None
                        )
                    else:
                        raise Exception(f"Block returned success=false")

                raise Exception("Unexpected response format")

            except Exception as e:
                logger.warning(
                    f"Block attempt {attempt + 1}/{max_retries} failed for {third_party_name or third_party_id}: {e}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    # Final attempt failed
                    error_msg = str(e)
                    logger.error(f"Failed to block 3rd party {third_party_name or third_party_id}: {error_msg}")
                    return QuarantineResult(
                        success=False,
                        identity_id=third_party_id,
                        error_message=error_msg
                    )

        # Should not reach here, but return failure just in case
        return QuarantineResult(
            success=False,
            identity_id=third_party_id,
            error_message="Max retries exceeded"
        )

    def get_connection_status(self) -> bool:
        """
        Check if the API connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            query = """
            query {
                __typename
            }
            """
            headers = self._get_headers()
            response = requests.post(
                self.api_url,
                json={"query": query},
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
