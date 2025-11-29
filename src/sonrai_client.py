"""Sonrai API client for fetching and quarantining unused identities."""

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List

import requests

from api_validator import APIValidator, ValidationError
from models import QuarantineResult, UnusedIdentity

if TYPE_CHECKING:
    from models import QuarantineReport

logger = logging.getLogger(__name__)

# API Timeout Configuration (SEC-002)
# These timeouts prevent hanging requests and ensure responsive gameplay
API_TIMEOUT_SHORT = 10  # Quick operations (auth, health checks)
API_TIMEOUT_STANDARD = 30  # Standard queries (fetch data)
API_TIMEOUT_MUTATION = 15  # Mutations (quarantine, block)
API_MAX_RETRIES = 3  # Maximum retry attempts for failed requests
API_RETRY_DELAY = 1.0  # Initial delay between retries (seconds)


class SonraiAPIClient:
    """Handles all communication with the Sonrai Security API."""

    def __init__(self, api_url: str, org_id: str, api_token: str):
        """
        Initialize the Sonrai API client.

        Args:
            api_url: GraphQL endpoint URL for the Sonrai API
            org_id: Organization ID
            api_token: API authentication token

        Raises:
            ValidationError: If any parameters are invalid
        """
        # Validate all initialization parameters
        APIValidator.validate_url(api_url, "api_url")
        APIValidator.validate_string_field(org_id, "org_id", allow_empty=False)
        APIValidator.validate_token(api_token, "api_token")

        self.api_url = api_url
        self.org_id = org_id
        self.api_token = api_token
        logger.info("Initialized SonraiAPIClient with validated parameters")

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
                timeout=API_TIMEOUT_SHORT,
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
            "Content-Type": "application/json",
        }

    def _make_request_with_timeout(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        timeout: int = API_TIMEOUT_STANDARD,
        max_retries: int = API_MAX_RETRIES,
    ) -> Dict[str, Any]:
        """
        Make API request with timeout and retry logic.

        Args:
            query: GraphQL query or mutation
            variables: Query variables
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Returns:
            API response data

        Raises:
            requests.exceptions.Timeout: If request times out after all retries
            requests.exceptions.RequestException: If request fails after all retries
        """
        last_exception: Exception = None

        for attempt in range(max_retries):
            try:
                payload: Dict[str, Any] = {"query": query}
                if variables:
                    payload["variables"] = variables

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=timeout,
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(
                    f"API request timeout (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    delay = API_RETRY_DELAY * (2**attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)

            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(
                    f"API request failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    delay = API_RETRY_DELAY * (2**attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)

        # All retries exhausted
        logger.error(f"API request failed after {max_retries} attempts")
        raise last_exception

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
                        "value": "aws/r-ipxz",  # MyHealth organization (CORRECT)
                        "op": "STARTS_WITH",
                    },
                    "daysSinceLastLogin": {"op": "GTE", "value": "0"},
                }
            }

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
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
            root_scope: Root AWS organization scope - MyHealth: "aws/r-ipxz"

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
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Group 3rd parties by account
            # Note: The ThirdParties query returns org-level data,
            # so we'll create entries for all accounts
            third_parties_by_account: Dict[str, List[Dict[str, Any]]] = {}

            if (
                data
                and "data" in data
                and data["data"] is not None
                and isinstance(data["data"], dict)
                and "ThirdParties" in data["data"]
            ):
                items = (
                    data["data"]["ThirdParties"].get("items", [])
                    if data["data"]["ThirdParties"]
                    else []
                )

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
                    status = (
                        status_obj.get("state", "Unknown") if status_obj else "Unknown"
                    )

                    # For now, add to a generic "all" key since we don't have per-account mapping
                    # The caller can distribute these across accounts as needed
                    if "all" not in third_parties_by_account:
                        third_parties_by_account["all"] = []

                    third_parties_by_account["all"].append(
                        {
                            "name": third_party_name,
                            "status": status,
                            "thirdPartyId": item.get("thirdPartyId", ""),
                            "accountCount": item.get("accountCount", 0),
                        }
                    )

            total_parties = sum(
                len(parties) for parties in third_parties_by_account.values()
            )
            logger.info(f"Processed {total_parties} 3rd party entries")
            return third_parties_by_account

        except Exception as e:
            import traceback

            logger.error(f"Failed to fetch 3rd parties: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    def fetch_unused_identities(
        self,
        limit: int = 500,
        scope: str = None,
        days_since_login: str = "0",
        filter_account: str = "577945324761",
    ) -> List[UnusedIdentity]:
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
            # Fetch ALL account scopes ONCE using CloudHierarchyList (REAL organizational scopes with OU paths)
            logger.info("Fetching real account scopes from CloudHierarchyList...")
            account_scopes = self._fetch_all_account_scopes()
            logger.info(
                f"Retrieved {len(account_scopes)} account scopes from CloudHierarchyList"
            )

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
            # If no scope provided, use MyHealth organization scope
            if not scope:
                # MyHealth organization (CORRECT)
                scope_filter = {"value": "aws/r-ipxz", "op": "STARTS_WITH"}
            else:
                scope_filter = {"value": scope, "op": "EQ"}

            variables = {
                "filters": {
                    "scope": scope_filter,
                    "daysSinceLastLogin": {"op": "GTE", "value": days_since_login},
                }
            }

            headers = self._get_headers()
            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Validate response structure
            try:
                APIValidator.validate_graphql_response(
                    data,
                    required_fields=["data.UnusedIdentities.items"],
                    response_type="UnusedIdentities",
                )
            except ValidationError as e:
                logger.error(f"Invalid API response: {e}")
                raise Exception(f"API response validation failed: {e}")

            identities = []

            # Parse GraphQL response
            if (
                data
                and "data" in data
                and data["data"]
                and "UnusedIdentities" in data["data"]
            ):
                items = data["data"]["UnusedIdentities"].get("items", [])

                # Each item represents a group of unused identities by account
                for item in items:
                    account = item.get("account", "unknown")

                    # Filter to only the specified account if provided
                    if filter_account and account != filter_account:
                        continue

                    # Look up the REAL account scope from CloudHierarchyList (includes OU path)
                    account_scope = account_scopes.get(account)

                    if not account_scope:
                        logger.warning(
                            f"No scope found for account {account} in CloudHierarchyList - skipping this account"
                        )
                        continue

                    logger.info(f"Using scope for account {account}: {account_scope}")

                    # Get individual identities
                    identity_list = item.get("identities", [])

                    for identity_data in identity_list:
                        srn = identity_data.get("srn", "")

                        # Extract name from SRN (after last /)
                        name = srn.split("/")[-1] if "/" in srn else srn

                        # Extract resource type from SRN (second to last part)
                        srn_parts = srn.split("/")
                        resource_type = (
                            srn_parts[-2] if len(srn_parts) > 1 else "Unknown"
                        )

                        # Create identity object with REAL account scope from CloudHierarchyList
                        identity = UnusedIdentity(
                            identity_id=srn,
                            identity_name=name,
                            identity_type=resource_type,
                            last_used=None,
                            risk_score=0.0,
                            scope=account_scope,  # Real scope with OU path from CloudHierarchyList
                            account=account,
                        )
                        identities.append(identity)

                logger.info(
                    f"Fetched {len(identities)} unused identities from Sonrai (before limit)"
                )
            else:
                logger.warning("No unused identities found in response")

            # Apply limit and log
            if len(identities) > limit:
                logger.info(f"Limiting from {len(identities)} to {limit} identities")
                return identities[:limit]
            else:
                logger.info(
                    f"Returning all {len(identities)} identities (under limit of {limit})"
                )
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

        variables = {"filters": {"scope": {"value": scope_filter, "op": "EQ"}}}

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers=self._get_headers(),
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()

                    if "errors" in data:
                        logger.error(
                            f"GraphQL errors in exemptions query: {data['errors']}"
                        )
                        return []

                    exemptions_data = (
                        data.get("data", {})
                        .get("AppliedExemptedIdentities", {})
                        .get("items", [])
                    )
                    logger.info(
                        f"Fetched {len(exemptions_data)} exempted identities for account {account}"
                    )
                    return exemptions_data
                else:
                    logger.error(
                        f"Failed to fetch exemptions: HTTP {response.status_code}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return []

            except requests.exceptions.Timeout:
                logger.warning(
                    f"Timeout fetching exemptions (attempt {attempt + 1}/{max_retries})"
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                return []
            except Exception as e:
                logger.error(f"Error fetching exemptions: {e}")
                return []

        return []

    def _fetch_all_account_scopes(self) -> dict:
        """
        Fetch scopes for all AWS accounts in the organization using CloudHierarchyList.
        Only includes the 7 real MyHealth AWS accounts (filters out OUs and root).

        Returns:
            Dictionary mapping account number to full scope path
        """
        try:
            # The 7 MyHealth AWS accounts from aws_accounts.csv
            VALID_MYHEALTH_ACCOUNTS = {
                "160224865296",  # MyHealth - Production Data
                "240768036625",  # MyHealth-WebApp
                "514455208804",  # MyHealth - Stage
                "437154727976",  # Sonrai MyHealth - Org
                "393582650665",  # MyHealth - Automation
                "577945324761",  # MyHealth - Sandbox
                "613056517323",  # MyHealth - Production
            }

            query = """
            query getCloudHierarchyList($filters: CloudHierarchyFilter) {
                CloudHierarchyList(where: $filters) {
                    items {
                        resourceId
                        scope
                        cloudType
                        parentScope
                        scopeFriendlyName
                        name
                    }
                }
            }
            """

            variables = {
                "filters": {
                    "cloudType": {"op": "EQ", "value": "aws"},
                    "scope": {"op": "STARTS_WITH", "value": "aws/r-ipxz"},
                    "entryType": {"op": "NEQ", "value": "managementAccount"},
                    "active": {"op": "EQ", "value": True},
                }
            }

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            account_scopes = {}
            if (
                data
                and "data" in data
                and data["data"]
                and "CloudHierarchyList" in data["data"]
            ):
                items = data["data"]["CloudHierarchyList"].get("items", [])
                for item in items:
                    resource_id = item.get("resourceId")
                    scope = item.get("scope")
                    name = item.get("name", "")

                    # Only include the 7 valid MyHealth accounts (filter out OUs and root)
                    if resource_id and scope and resource_id in VALID_MYHEALTH_ACCOUNTS:
                        account_scopes[resource_id] = scope
                        logger.info(f"Mapped account {resource_id} ({name}) -> {scope}")

            logger.info(
                f"Fetched scopes for {len(account_scopes)} MyHealth accounts (filtered to 7 real accounts)"
            )
            return account_scopes

        except Exception as e:
            logger.error(f"Failed to fetch account scopes: {e}")
            return {}

    def quarantine_identity(
        self,
        identity_id: str,
        identity_name: str = None,
        account: str = None,
        scope: str = None,
        root_scope: str = None,
    ) -> QuarantineResult:
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
            identity_name = (
                identity_id.split("/")[-1] if "/" in identity_id else identity_id
            )

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

        # Scope MUST be provided - never use fake scopes as they trigger alerts
        if not scope:
            error_msg = f"Cannot quarantine without real scope - no scope provided for {identity_id}"
            logger.error(error_msg)
            return QuarantineResult(
                success=False, identity_id=identity_id, error_message=error_msg
            )

        if not root_scope:
            # Extract root scope from full scope if available
            if scope:
                scope_parts = scope.split("/")
                if len(scope_parts) >= 2:
                    root_scope = f"{scope_parts[0]}/{scope_parts[1]}"
            if not root_scope:
                root_scope = "aws/r-ipxz"  # MyHealth root scope (CORRECT)

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
                                "account": account,
                            }
                        ],
                        "action": "ADD",
                        "rootScope": root_scope,
                    }
                }

                # Log the quarantine request details
                logger.info(
                    f"Quarantining {identity_name}: scope={scope}, rootScope={root_scope}, arn={resource_arn}"
                )

                headers = self._get_headers()
                response = requests.post(
                    self.api_url,
                    json={"query": mutation, "variables": variables},
                    headers=headers,
                    timeout=15,
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
                            success=True, identity_id=identity_id, error_message=None
                        )
                    else:
                        raise Exception(
                            f"Quarantine returned success=false, count={result.get('count')}"
                        )

                raise Exception("Unexpected response format")

            except Exception as e:
                logger.warning(
                    f"Quarantine attempt {attempt + 1}/{max_retries} failed for {identity_id}: {e}"
                )

                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep(retry_delay * (2**attempt))
                else:
                    # Final attempt failed
                    error_msg = str(e)
                    logger.error(
                        f"Failed to quarantine identity {identity_id}: {error_msg}"
                    )
                    return QuarantineResult(
                        success=False, identity_id=identity_id, error_message=error_msg
                    )

        # Should not reach here, but return failure just in case
        return QuarantineResult(
            success=False, identity_id=identity_id, error_message="Max retries exceeded"
        )

    def block_third_party(
        self, third_party_id: str, third_party_name: str = None, root_scope: str = None
    ) -> QuarantineResult:
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

        # Use default scope if not provided (MyHealth organization)
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
                variables = {"thirdPartyId": third_party_id, "scope": root_scope}

                # Log the request details (only on first attempt to avoid spam)
                if attempt == 0:
                    logger.info(
                        f"Blocking 3rd party {third_party_name or third_party_id} with ID: {third_party_id[:8]}... scope: {root_scope}"
                    )

                headers = self._get_headers()
                response = requests.post(
                    self.api_url,
                    json={"query": mutation, "variables": variables},
                    headers=headers,
                    timeout=15,
                )
                response.raise_for_status()

                data = response.json()

                # Log the full response if there are errors
                if "errors" in data:
                    logger.info(
                        f"API error response for {third_party_name or third_party_id}: {data}"
                    )

                # Check for GraphQL errors
                if "errors" in data:
                    error_msg = data["errors"][0].get("message", "Unknown error")
                    raise Exception(error_msg)

                # Check if the mutation was successful
                if data.get("data") and data["data"].get("DenyThirdPartyAccess"):
                    result = data["data"]["DenyThirdPartyAccess"]
                    if result.get("success"):
                        logger.info(
                            f"Successfully blocked 3rd party {third_party_name or third_party_id}"
                        )
                        return QuarantineResult(
                            success=True, identity_id=third_party_id, error_message=None
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
                    time.sleep(retry_delay * (2**attempt))
                else:
                    # Final attempt failed
                    error_msg = str(e)
                    logger.error(
                        f"Failed to block 3rd party {third_party_name or third_party_id}: {error_msg}"
                    )
                    return QuarantineResult(
                        success=False,
                        identity_id=third_party_id,
                        error_message=error_msg,
                    )

        # Should not reach here, but return failure just in case
        return QuarantineResult(
            success=False,
            identity_id=third_party_id,
            error_message="Max retries exceeded",
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
                self.api_url, json={"query": query}, headers=headers, timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_unprotected_services(self, account_id: str) -> List[str]:
        """
        Fetch list of unprotected services for a given AWS account.

        Args:
            account_id: AWS account ID to check

        Returns:
            List of service names that are NOT protected (e.g., ["bedrock-agentcore", "s3", "rds"])

        Raises:
            ValidationError: If account_id is invalid
        """
        # Validate account ID parameter
        APIValidator.validate_account_id(account_id)

        try:
            # Fetch real scope for the account
            logger.info(f"Fetching unprotected services for account {account_id}...")
            account_scopes = self._fetch_all_account_scopes()
            scope = account_scopes.get(account_id)

            if not scope:
                logger.warning(f"No scope found for account {account_id}")
                return []

            # Query for protected services in this scope
            query = """
            query getProtectedServices($scope: String!) {
                ProtectedServices(where: { scope: { value: $scope, op: EQ } }) {
                    items {
                        controlKey
                        scope
                        status
                    }
                }
            }
            """

            variables = {"scope": scope}

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Extract protected service control keys
            protected_services = set()
            if (
                data
                and "data" in data
                and data["data"]
                and "ProtectedServices" in data["data"]
            ):
                items = data["data"]["ProtectedServices"].get("items", [])
                for item in items:
                    control_key = item.get("controlKey")
                    status = item.get("status")
                    if control_key and status == "active":
                        protected_services.add(control_key)
                        logger.info(f"  ✅ {control_key} is already protected")

            # List of all possible services we might want to protect
            ALL_SERVICES = {
                "bedrock",
                "bedrock-agentcore",
                "s3",
                "rds",
                "lambda",
                "sagemaker",
                "dynamodb",
            }

            # Return services that are NOT protected
            unprotected = list(ALL_SERVICES - protected_services)
            logger.info(
                f"📋 Unprotected services in account {account_id}: {unprotected}"
            )
            return unprotected

        except Exception as e:
            logger.error(f"Failed to fetch unprotected services: {e}")
            # On error, assume all services are unprotected (safer to show quest)
            return ["bedrock-agentcore", "s3", "rds", "lambda", "sagemaker", "dynamodb"]

    def fetch_permission_sets(self, account_id: str) -> List[dict]:
        """
        Fetch permission sets for a specific AWS account, filtering for ADMIN and PRIVILEGED roles.

        Args:
            account_id: AWS account ID to fetch permission sets for

        Returns:
            List of permission set dictionaries with id, name, identityLabels, userCount, hasJit
        """
        try:
            # Fetch real scope for the account
            logger.info(f"Fetching permission sets for account {account_id}...")
            account_scopes = self._fetch_all_account_scopes()
            scope = account_scopes.get(account_id)

            if not scope:
                logger.warning(f"No scope found for account {account_id}")
                return []

            # Query for permission sets
            query = """
            query getPermissionSets($where: PermissionSetsFilter) {
                PermissionSets(where: $where) {
                    items {
                        id
                        name
                        identityLabels
                        userCount
                        ssoUsers
                    }
                }
            }
            """

            variables = {"where": {"scope": {"value": scope, "op": "EQ"}}}

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            permission_sets = []
            if (
                data
                and "data" in data
                and data["data"]
                and "PermissionSets" in data["data"]
            ):
                items = data["data"]["PermissionSets"].get("items", [])

                # Filter for ADMIN or PRIVILEGED labels
                for item in items:
                    labels = item.get("identityLabels", [])
                    if "ADMIN" in labels or "PRIVILEGED" in labels:
                        permission_sets.append(
                            {
                                "id": item.get("id", ""),
                                "name": item.get("name", "Unknown"),
                                "identityLabels": labels,
                                "userCount": item.get("userCount", 0),
                                "hasJit": False,  # Will be updated by fetch_jit_configuration
                            }
                        )
                        logger.info(
                            f"  Found admin/privileged permission set: {item.get('name')} (labels: {labels})"
                        )

            logger.info(
                f"Found {len(permission_sets)} admin/privileged permission sets in account {account_id}"
            )
            return permission_sets

        except Exception as e:
            logger.error(f"Failed to fetch permission sets: {e}")
            return []

    def fetch_jit_configuration(self, account_id: str) -> dict:
        """
        Fetch JIT configuration for a specific AWS account to see which permission sets are protected.

        Args:
            account_id: AWS account ID to check JIT configuration for

        Returns:
            Dictionary with 'enrolledPermissionSets' list of permission set IDs that have JIT enabled
        """
        try:
            # Fetch real scope for the account
            logger.info(f"Fetching JIT configuration for account {account_id}...")
            account_scopes = self._fetch_all_account_scopes()
            scope = account_scopes.get(account_id)

            if not scope:
                logger.warning(f"No scope found for account {account_id}")
                return {"enrolledPermissionSets": []}

            # Query for JIT configuration
            query = """
            query getJitConfiguration($where: JitConfigurationFilter) {
                JitConfiguration(where: $where) {
                    count
                    items {
                        scope
                        friendlyScope
                        denyFirst
                        permissionSets {
                            id
                            name
                            isFullAccess
                            isInherited
                            status {
                                status
                                isPending
                            }
                        }
                    }
                }
            }
            """

            variables = {"where": {"scope": {"value": scope, "op": "EQ"}}}

            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            enrolled_permission_sets = []
            if (
                data
                and "data" in data
                and data["data"]
                and "JitConfiguration" in data["data"]
            ):
                items = data["data"]["JitConfiguration"].get("items", [])
                for item in items:
                    permission_sets = item.get("permissionSets", [])
                    for ps in permission_sets:
                        ps_id = ps.get("id")
                        ps_name = ps.get("name")
                        if ps_id:
                            enrolled_permission_sets.append(ps_id)
                            logger.info(f"  ✅ {ps_name} ({ps_id}) has JIT enabled")

            logger.info(
                f"Found {len(enrolled_permission_sets)} permission sets with JIT in account {account_id}"
            )
            return {"enrolledPermissionSets": enrolled_permission_sets}

        except Exception as e:
            logger.error(f"Failed to fetch JIT configuration: {e}")
            return {"enrolledPermissionSets": []}

    def apply_jit_protection(
        self, account_id: str, permission_set_id: str, permission_set_name: str = None
    ) -> QuarantineResult:
        """
        Apply JIT protection to a specific permission set.

        Args:
            account_id: AWS account ID
            permission_set_id: ID of the permission set to protect
            permission_set_name: Optional name for logging

        Returns:
            QuarantineResult with success status and error message if any
        """
        try:
            # Fetch real scope for the account
            logger.info(
                f"Applying JIT protection to permission set {permission_set_name or permission_set_id}..."
            )
            account_scopes = self._fetch_all_account_scopes()
            scope = account_scopes.get(account_id)

            if not scope:
                error_msg = f"No scope found for account {account_id}"
                logger.error(error_msg)
                return QuarantineResult(
                    success=False, identity_id="", error_message=error_msg
                )

            logger.info(f"Using scope: {scope}")

            # Call SetJitConfiguration mutation
            mutation = """
            mutation setJitConfiguration($input: SetJitConfigurationInput!) {
                SetJitConfiguration(input: $input) {
                    success
                    addedJitConfigurationIds
                    removedJitConfigurationIds
                }
            }
            """

            variables = {
                "input": {
                    "scope": scope,
                    "isDenyFirst": True,
                    "enrolledPermissionSets": [
                        {"id": permission_set_id, "isFullAccess": False}
                    ],
                }
            }

            logger.info(
                f"Calling SetJitConfiguration API for {permission_set_name or permission_set_id}..."
            )
            logger.info(f"  scope: {scope}")
            logger.info(f"  permissionSetId: {permission_set_id}")

            response = requests.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Log only success status, not full response (security)
            if (
                data
                and "data" in data
                and data["data"]
                and "SetJitConfiguration" in data["data"]
            ):
                result = data["data"]["SetJitConfiguration"]
                success = result.get("success", False)
                logger.info(f"SetJitConfiguration response: success={success}")
            else:
                logger.info("SetJitConfiguration response received")

            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
                logger.error(f"SetJitConfiguration GraphQL error: {error_msg}")
                return QuarantineResult(
                    success=False, identity_id="", error_message=error_msg
                )

            # Extract result
            if (
                data
                and "data" in data
                and data["data"]
                and "SetJitConfiguration" in data["data"]
            ):
                result = data["data"]["SetJitConfiguration"]
                success = result.get("success", False)
                added_ids = result.get("addedJitConfigurationIds", [])

                if success:
                    logger.info(
                        f"✅ SUCCESS! Applied JIT protection to {permission_set_name or permission_set_id}"
                    )
                    logger.info(f"  Added permission sets: {added_ids}")
                    return QuarantineResult(
                        success=True, identity_id=permission_set_id, error_message=None
                    )
                else:
                    logger.warning(f"SetJitConfiguration returned success=false")
                    return QuarantineResult(
                        success=False,
                        identity_id="",
                        error_message="SetJitConfiguration returned success=false",
                    )
            else:
                logger.error("Invalid response structure from SetJitConfiguration")
                return QuarantineResult(
                    success=False, identity_id="", error_message="Invalid API response"
                )

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error applying JIT protection: {str(e)}"
            logger.error(error_msg)
            return QuarantineResult(
                success=False, identity_id="", error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error applying JIT protection: {str(e)}"
            logger.error(error_msg)
            return QuarantineResult(
                success=False, identity_id="", error_message=error_msg
            )

    def protect_service(
        self, service_type: str, account_id: str, service_name: str = None
    ) -> QuarantineResult:
        """
        Protect an AWS service using the Sonrai ProtectService API.

        CRITICAL: This calls the REAL Sonrai API (NOT A MOCK!).
        Always fetches real scopes from CloudHierarchyList - NEVER constructs manually!

        Args:
            service_type: Type of service ("bedrock", "s3", "rds", "lambda", "sagemaker", "dynamodb")
            account_id: AWS account ID
            service_name: Optional service name for logging

        Returns:
            QuarantineResult with success status and error message if any
        """
        # Service type to control key mapping
        SERVICE_CONTROL_KEYS = {
            "bedrock": "bedrock",
            "bedrock-agentcore": "bedrock-agentcore",
            "s3": "s3",
            "rds": "rds",
            "lambda": "lambda",
            "sagemaker": "sagemaker",
            "dynamodb": "dynamodb",
        }

        try:
            # 1. Get control key for service type
            control_key = SERVICE_CONTROL_KEYS.get(service_type)
            if not control_key:
                error_msg = f"Unknown service type: {service_type}"
                logger.error(error_msg)
                return QuarantineResult(
                    success=False, identity_id="", error_message=error_msg
                )

            # 2. Fetch REAL scope from CloudHierarchyList (CRITICAL!)
            logger.info(f"Fetching real scope for account {account_id}...")
            account_scopes = self._fetch_all_account_scopes()
            scope = account_scopes.get(account_id)

            if not scope:
                error_msg = f"No scope found for account {account_id}"
                logger.error(error_msg)
                return QuarantineResult(
                    success=False, identity_id="", error_message=error_msg
                )

            logger.info(f"Using scope: {scope}")

            # 3. Call ProtectService mutation
            mutation = """
            mutation protectService($input: ProtectActionInput!) {
                ProtectService(input: $input) {
                    success
                    serviceName
                }
            }
            """

            variables = {
                "input": {
                    "controlKey": control_key,
                    "scope": scope,  # Real scope from CloudHierarchyList!
                    "identities": [],
                    "ssoActorIds": [],
                }
            }

            logger.info(
                f"Calling ProtectService API for {service_type} in account {account_id}..."
            )
            logger.info(f"📤 SENDING TO API:")
            logger.info(f"  controlKey: {control_key}")
            logger.info(f"  scope: {scope}")
            logger.info(f"  account: {account_id}")
            logger.info(f"  identities: []")
            logger.info(f"  ssoActorIds: []")

            response = requests.post(
                self.api_url,
                json={"query": mutation, "variables": variables},
                headers=self._get_headers(),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Log only success status, not full response (security)
            logger.info(f"📥 RECEIVED FROM API:")
            if (
                data
                and "data" in data
                and data["data"]
                and "ProtectService" in data["data"]
            ):
                result = data["data"]["ProtectService"]
                success = result.get("success", False)
                service_name = result.get("serviceName", "unknown")
                logger.info(
                    f"  ProtectService: success={success}, service={service_name}"
                )
            else:
                logger.info("  ProtectService response received")

            # Check for GraphQL errors
            if "errors" in data:
                error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
                logger.error(f"ProtectService GraphQL error: {error_msg}")
                # Don't log full error object (security)
                return QuarantineResult(
                    success=False, identity_id="", error_message=error_msg
                )

            # Extract result
            if (
                data
                and "data" in data
                and data["data"]
                and "ProtectService" in data["data"]
            ):
                result = data["data"]["ProtectService"]
                success = result.get("success", False)
                service_name_result = result.get(
                    "serviceName", service_name or service_type
                )

                if success:
                    logger.info(
                        f"✅ SUCCESS! Protected {service_type} service in account {account_id}"
                    )
                    return QuarantineResult(
                        success=True,
                        identity_id=service_name_result,
                        error_message=None,
                    )
                else:
                    logger.warning(
                        f"ProtectService returned success=false for {service_type}"
                    )
                    return QuarantineResult(
                        success=False,
                        identity_id="",
                        error_message="ProtectService returned success=false",
                    )
            else:
                logger.error("Invalid response structure from ProtectService")
                return QuarantineResult(
                    success=False, identity_id="", error_message="Invalid API response"
                )

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error protecting service: {str(e)}"
            logger.error(error_msg)
            return QuarantineResult(
                success=False, identity_id="", error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error protecting service: {str(e)}"
            logger.error(error_msg)
            return QuarantineResult(
                success=False, identity_id="", error_message=error_msg
            )

    def batch_quarantine_identities(self, zombies: List) -> "QuarantineReport":
        """
        Quarantine multiple identities in batches with rate limiting.

        Rate limit: 10 API calls per batch with 1-second delay between batches.

        Args:
            zombies: List of Zombie objects to quarantine

        Returns:
            QuarantineReport with success/failure counts
        """
        from models import QuarantineReport

        report = QuarantineReport(
            total_queued=len(zombies), successful=0, failed=0, errors=[]
        )

        if not zombies:
            logger.info("📭 No zombies to quarantine")
            return report

        logger.info(f"🔄 Starting batch quarantine of {len(zombies)} identities...")

        batch_size = 10
        batch_count = (len(zombies) + batch_size - 1) // batch_size

        for batch_idx in range(batch_count):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(zombies))
            batch = zombies[start_idx:end_idx]

            logger.info(
                f"📦 Processing batch {batch_idx + 1}/{batch_count} ({len(batch)} identities)"
            )

            for zombie in batch:
                result = self.quarantine_identity(
                    identity_id=zombie.identity_id,
                    identity_name=zombie.identity_name,
                    account=zombie.account,
                    scope=zombie.scope,
                )

                if result.success:
                    report.successful += 1
                    logger.debug(f"  ✅ {zombie.identity_name}")
                else:
                    report.failed += 1
                    report.errors.append(
                        f"{zombie.identity_name}: {result.error_message}"
                    )
                    logger.warning(
                        f"  ❌ {zombie.identity_name}: {result.error_message}"
                    )

            # Rate limiting: 1-second delay between batches
            if batch_idx < batch_count - 1:
                logger.debug(f"⏸️  Rate limiting: waiting 1 second before next batch...")
                time.sleep(1.0)

        logger.info(
            f"✅ Batch quarantine complete: {report.successful} successful, {report.failed} failed"
        )
        return report
