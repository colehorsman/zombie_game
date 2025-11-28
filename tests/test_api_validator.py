"""Tests for API input/output validation."""

import pytest
from api_validator import APIValidator, ValidationError


class TestURLValidation:
    """Tests for URL validation."""

    def test_valid_https_url(self):
        """Valid HTTPS URL should pass."""
        APIValidator.validate_url("https://api.sonraisecurity.com/graphql")

    def test_valid_http_url(self):
        """Valid HTTP URL should pass."""
        APIValidator.validate_url("http://localhost:8080/api")

    def test_empty_url_fails(self):
        """Empty URL should fail."""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            APIValidator.validate_url("")

    def test_missing_scheme_fails(self):
        """URL without scheme should fail."""
        with pytest.raises(ValidationError, match="must include a scheme"):
            APIValidator.validate_url("api.sonraisecurity.com")

    def test_invalid_scheme_fails(self):
        """URL with invalid scheme should fail."""
        with pytest.raises(ValidationError, match="must use http or https"):
            APIValidator.validate_url("ftp://api.example.com")


class TestTokenValidation:
    """Tests for API token validation."""

    def test_valid_token(self):
        """Valid token should pass."""
        APIValidator.validate_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

    def test_empty_token_fails(self):
        """Empty token should fail."""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            APIValidator.validate_token("")

    def test_too_short_token_fails(self):
        """Very short token should fail."""
        with pytest.raises(ValidationError, match="appears too short"):
            APIValidator.validate_token("abc")

    def test_whitespace_only_token_fails(self):
        """Whitespace-only token should fail."""
        with pytest.raises(ValidationError, match="cannot be only whitespace"):
            APIValidator.validate_token("           ")


class TestAccountIDValidation:
    """Tests for AWS account ID validation."""

    def test_valid_account_id(self):
        """Valid 12-digit account ID should pass."""
        APIValidator.validate_account_id("577945324761")

    def test_empty_account_id_fails(self):
        """Empty account ID should fail."""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            APIValidator.validate_account_id("")

    def test_too_short_account_id_fails(self):
        """Account ID with less than 12 digits should fail."""
        with pytest.raises(ValidationError, match="must be exactly 12 digits"):
            APIValidator.validate_account_id("12345")

    def test_too_long_account_id_fails(self):
        """Account ID with more than 12 digits should fail."""
        with pytest.raises(ValidationError, match="must be exactly 12 digits"):
            APIValidator.validate_account_id("1234567890123")

    def test_non_numeric_account_id_fails(self):
        """Account ID with non-numeric characters should fail."""
        with pytest.raises(ValidationError, match="must be exactly 12 digits"):
            APIValidator.validate_account_id("12345678901a")


class TestScopeValidation:
    """Tests for Sonrai scope validation."""

    def test_valid_scope(self):
        """Valid scope should pass."""
        APIValidator.validate_scope("aws/r-ipxz/ou-xxxx-12345678/577945324761")

    def test_minimal_valid_scope(self):
        """Minimal valid scope should pass."""
        APIValidator.validate_scope("aws/r-ipxz")

    def test_empty_scope_fails(self):
        """Empty scope should fail."""
        with pytest.raises(ValidationError, match="must be a non-empty string"):
            APIValidator.validate_scope("")

    def test_wrong_prefix_fails(self):
        """Scope without aws/ prefix should fail."""
        with pytest.raises(ValidationError, match="must start with 'aws/'"):
            APIValidator.validate_scope("gcp/project-123")

    def test_single_part_scope_fails(self):
        """Scope with only one part should fail."""
        with pytest.raises(ValidationError, match="must start with 'aws/'"):
            APIValidator.validate_scope("aws")


class TestGraphQLResponseValidation:
    """Tests for GraphQL response validation."""

    def test_valid_response(self):
        """Valid GraphQL response should pass."""
        response = {
            "data": {
                "UnusedIdentities": {
                    "items": []
                }
            }
        }
        APIValidator.validate_graphql_response(
            response,
            required_fields=["data.UnusedIdentities.items"]
        )

    def test_graphql_error_response_fails(self):
        """Response with GraphQL errors should fail."""
        response = {
            "errors": [{"message": "Invalid query"}]
        }
        with pytest.raises(ValidationError, match="GraphQL error"):
            APIValidator.validate_graphql_response(response, required_fields=[])

    def test_missing_required_field_fails(self):
        """Response missing required field should fail."""
        response = {
            "data": {
                "UnusedIdentities": {}
            }
        }
        with pytest.raises(ValidationError, match="missing required field"):
            APIValidator.validate_graphql_response(
                response,
                required_fields=["data.UnusedIdentities.items"]
            )

    def test_non_dict_response_fails(self):
        """Non-dictionary response should fail."""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            APIValidator.validate_graphql_response(
                "not a dict",
                required_fields=[]
            )


class TestListResponseValidation:
    """Tests for list response validation."""

    def test_valid_list(self):
        """Valid list should pass."""
        APIValidator.validate_list_response([1, 2, 3])

    def test_empty_list_allowed(self):
        """Empty list should pass when min_items=0."""
        APIValidator.validate_list_response([], min_items=0)

    def test_too_few_items_fails(self):
        """List with too few items should fail."""
        with pytest.raises(ValidationError, match="must contain at least"):
            APIValidator.validate_list_response([1], min_items=2)

    def test_too_many_items_fails(self):
        """List with too many items should fail."""
        with pytest.raises(ValidationError, match="must contain at most"):
            APIValidator.validate_list_response([1, 2, 3], max_items=2)

    def test_non_list_fails(self):
        """Non-list should fail."""
        with pytest.raises(ValidationError, match="must be a list"):
            APIValidator.validate_list_response({"key": "value"})


class TestStringFieldValidation:
    """Tests for string field validation."""

    def test_valid_string(self):
        """Valid string should pass."""
        APIValidator.validate_string_field("test string", "field")

    def test_empty_string_allowed(self):
        """Empty string should pass when allow_empty=True."""
        APIValidator.validate_string_field("", "field", allow_empty=True)

    def test_empty_string_fails(self):
        """Empty string should fail when allow_empty=False."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            APIValidator.validate_string_field("", "field", allow_empty=False)

    def test_none_fails(self):
        """None value should fail."""
        with pytest.raises(ValidationError, match="cannot be None"):
            APIValidator.validate_string_field(None, "field")

    def test_too_long_string_fails(self):
        """String exceeding max_length should fail."""
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            APIValidator.validate_string_field("toolong", "field", max_length=3)


class TestIntegerFieldValidation:
    """Tests for integer field validation."""

    def test_valid_integer(self):
        """Valid integer should pass."""
        APIValidator.validate_integer_field(42, "count")

    def test_below_minimum_fails(self):
        """Integer below minimum should fail."""
        with pytest.raises(ValidationError, match="must be at least"):
            APIValidator.validate_integer_field(5, "count", min_value=10)

    def test_above_maximum_fails(self):
        """Integer above maximum should fail."""
        with pytest.raises(ValidationError, match="must be at most"):
            APIValidator.validate_integer_field(100, "count", max_value=50)

    def test_non_integer_fails(self):
        """Non-integer should fail."""
        with pytest.raises(ValidationError, match="must be an integer"):
            APIValidator.validate_integer_field("42", "count")

    def test_boolean_fails(self):
        """Boolean should fail (bools are subclass of int in Python)."""
        with pytest.raises(ValidationError, match="must be an integer"):
            APIValidator.validate_integer_field(True, "count")


class TestLogMessageSanitization:
    """Tests for log message sanitization."""

    def test_sanitize_bearer_token(self):
        """Bearer token should be redacted."""
        message = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        sanitized = APIValidator.sanitize_log_message(message)
        assert "[REDACTED]" in sanitized
        assert "eyJhbGciOi" not in sanitized

    def test_sanitize_api_token_json(self):
        """API token in JSON should be redacted."""
        message = '{"api_token": "secret123", "data": "value"}'
        sanitized = APIValidator.sanitize_log_message(message)
        assert "[REDACTED]" in sanitized
        assert "secret123" not in sanitized

    def test_truncate_long_message(self):
        """Long message should be truncated."""
        message = "x" * 1000
        sanitized = APIValidator.sanitize_log_message(message, max_length=100)
        assert len(sanitized) <= 120  # 100 + "... (truncated)"
        assert "truncated" in sanitized
