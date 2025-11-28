"""Input validation for API requests and responses."""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class APIValidator:
    """Validates API inputs, outputs, and configuration."""

    @staticmethod
    def validate_url(url: str, param_name: str = "url") -> None:
        """
        Validate a URL is well-formed and uses HTTPS.

        Args:
            url: URL to validate
            param_name: Name of the parameter for error messages

        Raises:
            ValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError(f"{param_name} must be a non-empty string")

        parsed = urlparse(url)
        if not parsed.scheme:
            raise ValidationError(f"{param_name} must include a scheme (http/https)")
        if parsed.scheme not in ["http", "https"]:
            raise ValidationError(f"{param_name} must use http or https scheme")
        if not parsed.netloc:
            raise ValidationError(f"{param_name} must include a valid domain")

        logger.debug(f"Validated {param_name}: {url}")

    @staticmethod
    def validate_token(token: str, param_name: str = "token") -> None:
        """
        Validate an API token is present and properly formatted.

        Args:
            token: Token to validate
            param_name: Name of the parameter for error messages

        Raises:
            ValidationError: If token is invalid
        """
        if not token or not isinstance(token, str):
            raise ValidationError(f"{param_name} must be a non-empty string")

        if len(token) < 10:
            raise ValidationError(f"{param_name} appears too short to be valid")

        if token.isspace():
            raise ValidationError(f"{param_name} cannot be only whitespace")

        logger.debug(f"Validated {param_name} (length: {len(token)})")

    @staticmethod
    def validate_timeout(timeout: Union[int, float], param_name: str = "timeout") -> None:
        """
        Validate a timeout value is positive and reasonable.

        Args:
            timeout: Timeout in seconds
            param_name: Name of the parameter for error messages

        Raises:
            ValidationError: If timeout is invalid
        """
        if not isinstance(timeout, (int, float)):
            raise ValidationError(f"{param_name} must be a number")

        if timeout <= 0:
            raise ValidationError(f"{param_name} must be positive")

        if timeout > 300:
            logger.warning(f"{param_name} is very large ({timeout}s), may cause hangs")

        logger.debug(f"Validated {param_name}: {timeout}s")

    @staticmethod
    def validate_account_id(account_id: str, param_name: str = "account_id") -> None:
        """
        Validate an AWS account ID is 12 digits.

        Args:
            account_id: AWS account ID
            param_name: Name of the parameter for error messages

        Raises:
            ValidationError: If account ID is invalid
        """
        if not account_id or not isinstance(account_id, str):
            raise ValidationError(f"{param_name} must be a non-empty string")

        if not re.match(r"^\d{12}$", account_id):
            raise ValidationError(f"{param_name} must be exactly 12 digits")

        logger.debug(f"Validated {param_name}: {account_id}")

    @staticmethod
    def validate_scope(scope: str, param_name: str = "scope") -> None:
        """
        Validate a Sonrai scope path format.

        Args:
            scope: Scope path (e.g., "aws/r-ipxz/ou-xxxx/123456789012")
            param_name: Name of the parameter for error messages

        Raises:
            ValidationError: If scope is invalid
        """
        if not scope or not isinstance(scope, str):
            raise ValidationError(f"{param_name} must be a non-empty string")

        if not scope.startswith("aws/"):
            raise ValidationError(f"{param_name} must start with 'aws/'")

        parts = scope.split("/")
        if len(parts) < 2:
            raise ValidationError(f"{param_name} must have at least two parts (aws/...)")

        logger.debug(f"Validated {param_name}: {scope}")

    @staticmethod
    def validate_graphql_response(response_data: Dict, required_fields: List[str],
                                   response_type: str = "API response") -> None:
        """
        Validate a GraphQL response has required structure and fields.

        Args:
            response_data: The parsed JSON response
            required_fields: List of dot-notation paths that must exist (e.g., "data.UnusedIdentities.items")
            response_type: Type of response for error messages

        Raises:
            ValidationError: If response is missing required fields or has errors
        """
        if not isinstance(response_data, dict):
            raise ValidationError(f"{response_type} must be a dictionary, got {type(response_data)}")

        # Check for GraphQL errors
        if "errors" in response_data:
            errors = response_data["errors"]
            if errors and len(errors) > 0:
                error_msg = errors[0].get("message", "Unknown GraphQL error")
                raise ValidationError(f"GraphQL error in {response_type}: {error_msg}")

        # Check required fields exist
        for field_path in required_fields:
            parts = field_path.split(".")
            current = response_data

            for part in parts:
                if not isinstance(current, dict):
                    raise ValidationError(
                        f"{response_type} missing required field '{field_path}' - "
                        f"'{part}' parent is not a dict"
                    )

                if part not in current:
                    raise ValidationError(
                        f"{response_type} missing required field '{field_path}' - "
                        f"'{part}' not found"
                    )

                current = current[part]

        logger.debug(f"Validated {response_type} with fields: {required_fields}")

    @staticmethod
    def validate_list_response(items: Any, min_items: int = 0, max_items: Optional[int] = None,
                               list_name: str = "items") -> None:
        """
        Validate a response contains a list with expected size constraints.

        Args:
            items: The items to validate
            min_items: Minimum number of items expected
            max_items: Maximum number of items allowed (None for no limit)
            list_name: Name of the list for error messages

        Raises:
            ValidationError: If list is invalid
        """
        if not isinstance(items, list):
            raise ValidationError(f"{list_name} must be a list, got {type(items)}")

        if len(items) < min_items:
            raise ValidationError(f"{list_name} must contain at least {min_items} items, got {len(items)}")

        if max_items is not None and len(items) > max_items:
            raise ValidationError(f"{list_name} must contain at most {max_items} items, got {len(items)}")

        logger.debug(f"Validated {list_name}: {len(items)} items")

    @staticmethod
    def validate_string_field(value: Any, field_name: str, allow_empty: bool = False,
                             max_length: Optional[int] = None) -> None:
        """
        Validate a field is a string with expected properties.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            allow_empty: Whether empty strings are allowed
            max_length: Maximum allowed length (None for no limit)

        Raises:
            ValidationError: If value is not a valid string
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be None")

        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string, got {type(value)}")

        if not allow_empty and not value:
            raise ValidationError(f"{field_name} cannot be empty")

        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")

        logger.debug(f"Validated {field_name}: '{value}'")

    @staticmethod
    def validate_integer_field(value: Any, field_name: str, min_value: Optional[int] = None,
                               max_value: Optional[int] = None) -> None:
        """
        Validate a field is an integer within expected bounds.

        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            min_value: Minimum allowed value (None for no minimum)
            max_value: Maximum allowed value (None for no maximum)

        Raises:
            ValidationError: If value is not a valid integer
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValidationError(f"{field_name} must be an integer, got {type(value)}")

        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}, got {value}")

        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be at most {max_value}, got {value}")

        logger.debug(f"Validated {field_name}: {value}")

    @staticmethod
    def sanitize_log_message(message: str, max_length: int = 500) -> str:
        """
        Sanitize a message for safe logging (remove sensitive data, limit length).

        Args:
            message: Message to sanitize
            max_length: Maximum length to truncate to

        Returns:
            Sanitized message safe for logging
        """
        if not message:
            return ""

        # Remove potential tokens/secrets (common patterns)
        patterns = [
            (r"Bearer\s+[\w\-\.]+", "Bearer [REDACTED]"),
            (r'"api_token":\s*"[^"]+"', '"api_token": "[REDACTED]"'),
            (r'"password":\s*"[^"]+"', '"password": "[REDACTED]"'),
            (r'Authorization:\s*[^\s]+', 'Authorization: [REDACTED]'),
        ]

        sanitized = message
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... (truncated)"

        return sanitized
