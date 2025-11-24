"""Tests for Sonrai API client JIT-related methods."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

# Add src to path
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sonrai_client import SonraiAPIClient
from models import QuarantineResult


@pytest.fixture
def mock_client():
    """Create a mock Sonrai API client."""
    return SonraiAPIClient(
        api_url="https://test.sonrai.com/graphql",
        org_id="test-org-123",
        api_token="test-token-456"
    )


@pytest.fixture
def mock_account_scopes():
    """Mock account scopes response."""
    return {
        "160224865296": "aws/r-ipxz/ou-ipxz-12345678/160224865296",
        "577945324761": "aws/r-ipxz/ou-ipxz-87654321/577945324761"
    }


class TestFetchPermissionSets:
    """Tests for fetch_permission_sets method."""

    @patch('sonrai_client.requests.post')
    def test_fetch_permission_sets_success(self, mock_post, mock_client, mock_account_scopes):
        """Test successful fetch of permission sets with ADMIN and PRIVILEGED labels."""
        # Mock _fetch_all_account_scopes
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            # Mock API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "PermissionSets": {
                        "items": [
                            {
                                "id": "ps-admin-123",
                                "name": "AdministratorAccess",
                                "identityLabels": ["ADMIN"],
                                "userCount": 5,
                                "ssoUsers": []
                            },
                            {
                                "id": "ps-priv-456",
                                "name": "PowerUserAccess",
                                "identityLabels": ["PRIVILEGED"],
                                "userCount": 10,
                                "ssoUsers": []
                            },
                            {
                                "id": "ps-read-789",
                                "name": "ReadOnlyAccess",
                                "identityLabels": ["READ_ONLY"],
                                "userCount": 50,
                                "ssoUsers": []
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            # Execute
            result = mock_client.fetch_permission_sets("160224865296")

            # Verify
            assert len(result) == 2  # Only ADMIN and PRIVILEGED
            assert result[0]["id"] == "ps-admin-123"
            assert result[0]["name"] == "AdministratorAccess"
            assert result[0]["identityLabels"] == ["ADMIN"]
            assert result[0]["userCount"] == 5
            assert result[0]["hasJit"] is False
            
            assert result[1]["id"] == "ps-priv-456"
            assert result[1]["name"] == "PowerUserAccess"

    @patch('sonrai_client.requests.post')
    def test_fetch_permission_sets_no_scope(self, mock_post, mock_client):
        """Test fetch_permission_sets when account has no scope."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value={}):
            result = mock_client.fetch_permission_sets("999999999999")
            
            assert result == []
            mock_post.assert_not_called()

    @patch('sonrai_client.requests.post')
    def test_fetch_permission_sets_empty_response(self, mock_post, mock_client, mock_account_scopes):
        """Test fetch_permission_sets with empty API response."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "PermissionSets": {
                        "items": []
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.fetch_permission_sets("160224865296")
            
            assert result == []

    @patch('sonrai_client.requests.post')
    def test_fetch_permission_sets_api_error(self, mock_post, mock_client, mock_account_scopes):
        """Test fetch_permission_sets handles API errors gracefully."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_post.side_effect = requests.exceptions.RequestException("API Error")

            result = mock_client.fetch_permission_sets("160224865296")
            
            assert result == []


class TestFetchJitConfiguration:
    """Tests for fetch_jit_configuration method."""

    @patch('sonrai_client.requests.post')
    def test_fetch_jit_configuration_success(self, mock_post, mock_client, mock_account_scopes):
        """Test successful fetch of JIT configuration."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "JitConfiguration": {
                        "count": 1,
                        "items": [
                            {
                                "scope": "aws/r-ipxz/ou-ipxz-12345678/160224865296",
                                "friendlyScope": "Production Data",
                                "denyFirst": True,
                                "permissionSets": [
                                    {
                                        "id": "ps-admin-123",
                                        "name": "AdministratorAccess",
                                        "isFullAccess": False,
                                        "isInherited": False,
                                        "status": {
                                            "status": "ACTIVE",
                                            "isPending": False
                                        }
                                    },
                                    {
                                        "id": "ps-priv-456",
                                        "name": "PowerUserAccess",
                                        "isFullAccess": False,
                                        "isInherited": False,
                                        "status": {
                                            "status": "ACTIVE",
                                            "isPending": False
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.fetch_jit_configuration("160224865296")

            assert "enrolledPermissionSets" in result
            assert len(result["enrolledPermissionSets"]) == 2
            assert "ps-admin-123" in result["enrolledPermissionSets"]
            assert "ps-priv-456" in result["enrolledPermissionSets"]

    @patch('sonrai_client.requests.post')
    def test_fetch_jit_configuration_no_scope(self, mock_post, mock_client):
        """Test fetch_jit_configuration when account has no scope."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value={}):
            result = mock_client.fetch_jit_configuration("999999999999")
            
            assert result == {"enrolledPermissionSets": []}
            mock_post.assert_not_called()

    @patch('sonrai_client.requests.post')
    def test_fetch_jit_configuration_empty(self, mock_post, mock_client, mock_account_scopes):
        """Test fetch_jit_configuration with no JIT configuration."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "JitConfiguration": {
                        "count": 0,
                        "items": []
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.fetch_jit_configuration("160224865296")
            
            assert result == {"enrolledPermissionSets": []}

    @patch('sonrai_client.requests.post')
    def test_fetch_jit_configuration_api_error(self, mock_post, mock_client, mock_account_scopes):
        """Test fetch_jit_configuration handles API errors gracefully."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_post.side_effect = requests.exceptions.RequestException("API Error")

            result = mock_client.fetch_jit_configuration("160224865296")
            
            assert result == {"enrolledPermissionSets": []}


class TestApplyJitProtection:
    """Tests for apply_jit_protection method."""

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_success(self, mock_post, mock_client, mock_account_scopes):
        """Test successful application of JIT protection."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "SetJitConfiguration": {
                        "success": True,
                        "addedJitConfigurationIds": ["ps-admin-123"],
                        "removedJitConfigurationIds": []
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id="ps-admin-123",
                permission_set_name="AdministratorAccess"
            )

            assert isinstance(result, QuarantineResult)
            assert result.success is True
            assert result.identity_id == "ps-admin-123"
            assert result.error_message is None

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_no_scope(self, mock_post, mock_client):
        """Test apply_jit_protection when account has no scope."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value={}):
            result = mock_client.apply_jit_protection(
                account_id="999999999999",
                permission_set_id="ps-admin-123"
            )
            
            assert result.success is False
            assert "No scope found" in result.error_message
            mock_post.assert_not_called()

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_graphql_error(self, mock_post, mock_client, mock_account_scopes):
        """Test apply_jit_protection handles GraphQL errors."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "errors": [
                    {
                        "message": "Permission set not found"
                    }
                ]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id="ps-invalid-999"
            )

            assert result.success is False
            assert "Permission set not found" in result.error_message

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_api_returns_false(self, mock_post, mock_client, mock_account_scopes):
        """Test apply_jit_protection when API returns success=false."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {
                    "SetJitConfiguration": {
                        "success": False,
                        "addedJitConfigurationIds": [],
                        "removedJitConfigurationIds": []
                    }
                }
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id="ps-admin-123"
            )

            assert result.success is False
            assert "success=false" in result.error_message

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_network_error(self, mock_post, mock_client, mock_account_scopes):
        """Test apply_jit_protection handles network errors."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id="ps-admin-123"
            )

            assert result.success is False
            assert "Network error" in result.error_message

    @patch('sonrai_client.requests.post')
    def test_apply_jit_protection_invalid_response(self, mock_post, mock_client, mock_account_scopes):
        """Test apply_jit_protection handles invalid API response structure."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": {}  # Missing SetJitConfiguration
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id="ps-admin-123"
            )

            assert result.success is False
            assert "Invalid API response" in result.error_message


class TestJitIntegration:
    """Integration tests for JIT workflow."""

    @patch('sonrai_client.requests.post')
    def test_jit_workflow_fetch_and_protect(self, mock_post, mock_client, mock_account_scopes):
        """Test complete workflow: fetch permission sets, check JIT config, apply protection."""
        with patch.object(mock_client, '_fetch_all_account_scopes', return_value=mock_account_scopes):
            # Setup mock responses for multiple calls
            responses = [
                # First call: fetch_permission_sets
                Mock(
                    status_code=200,
                    json=lambda: {
                        "data": {
                            "PermissionSets": {
                                "items": [
                                    {
                                        "id": "ps-admin-123",
                                        "name": "AdministratorAccess",
                                        "identityLabels": ["ADMIN"],
                                        "userCount": 5,
                                        "ssoUsers": []
                                    }
                                ]
                            }
                        }
                    },
                    raise_for_status=Mock()
                ),
                # Second call: fetch_jit_configuration
                Mock(
                    status_code=200,
                    json=lambda: {
                        "data": {
                            "JitConfiguration": {
                                "count": 0,
                                "items": []
                            }
                        }
                    },
                    raise_for_status=Mock()
                ),
                # Third call: apply_jit_protection
                Mock(
                    status_code=200,
                    json=lambda: {
                        "data": {
                            "SetJitConfiguration": {
                                "success": True,
                                "addedJitConfigurationIds": ["ps-admin-123"],
                                "removedJitConfigurationIds": []
                            }
                        }
                    },
                    raise_for_status=Mock()
                )
            ]
            mock_post.side_effect = responses

            # Execute workflow
            permission_sets = mock_client.fetch_permission_sets("160224865296")
            assert len(permission_sets) == 1
            assert permission_sets[0]["id"] == "ps-admin-123"

            jit_config = mock_client.fetch_jit_configuration("160224865296")
            assert len(jit_config["enrolledPermissionSets"]) == 0

            result = mock_client.apply_jit_protection(
                account_id="160224865296",
                permission_set_id=permission_sets[0]["id"],
                permission_set_name=permission_sets[0]["name"]
            )
            assert result.success is True
