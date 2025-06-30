"""Test our error response format."""

import json

from kaltura_mcp.tools import handle_kaltura_error


def test_our_error_response_structure():
    """Test OUR error response format and structure."""
    error = ValueError("Test error message")
    result = handle_kaltura_error(error, "test operation", {"context_key": "context_value"})

    # Test our response format
    data = json.loads(result)
    assert data["error"] == "Failed to test operation: Test error message"
    assert data["errorType"] == "ValueError"
    assert data["operation"] == "test operation"
    assert data["context_key"] == "context_value"


def test_our_error_type_handling():
    """Test our error type classification."""
    test_cases = [
        (ValueError("Value error"), "ValueError"),
        (TypeError("Type error"), "TypeError"),
        (RuntimeError("Runtime error"), "RuntimeError"),
        (KeyError("Key error"), "KeyError"),
        (AttributeError("Attribute error"), "AttributeError"),
    ]

    for error, expected_type in test_cases:
        result = handle_kaltura_error(error, "test operation")
        data = json.loads(result)
        assert data["errorType"] == expected_type
        assert "Failed to test operation:" in data["error"]


def test_our_error_context_handling():
    """Test our context inclusion in error responses."""
    error = Exception("Test error")
    context = {
        "entry_id": "1_test123",
        "user_id": "test@example.com",
        "operation_details": {"type": "search", "params": {"limit": 20}},
    }

    result = handle_kaltura_error(error, "complex operation", context)
    data = json.loads(result)

    # Test our context preservation
    assert data["entry_id"] == "1_test123"
    assert data["user_id"] == "test@example.com"
    assert data["operation_details"]["type"] == "search"
    assert data["operation_details"]["params"]["limit"] == 20


def test_our_error_handling_without_context():
    """Test our error handling when no context provided."""
    error = Exception("Simple error")
    result = handle_kaltura_error(error, "simple operation")

    data = json.loads(result)
    assert data["error"] == "Failed to simple operation: Simple error"
    assert data["errorType"] == "Exception"
    assert data["operation"] == "simple operation"

    # Should only have required keys when no context
    required_keys = {"error", "errorType", "operation"}
    extra_keys = set(data.keys()) - required_keys
    # May have timestamp or other standard fields, that's OK
    assert len(extra_keys) <= 2  # Allow for timestamp and maybe one other standard field


def test_our_error_handling_with_empty_context():
    """Test our error handling with empty context."""
    error = Exception("Empty context error")
    result = handle_kaltura_error(error, "empty context operation", {})

    data = json.loads(result)
    assert data["error"] == "Failed to empty context operation: Empty context error"
    assert data["errorType"] == "Exception"
    assert data["operation"] == "empty context operation"


def test_our_error_message_format():
    """Test our specific error message formatting."""
    test_cases = [
        (
            "API connection failed",
            "connect to API",
            "Failed to connect to API: API connection failed",
        ),
        ("Invalid entry ID", "validate input", "Failed to validate input: Invalid entry ID"),
        ("Permission denied", "access resource", "Failed to access resource: Permission denied"),
    ]

    for error_msg, operation, expected_format in test_cases:
        error = Exception(error_msg)
        result = handle_kaltura_error(error, operation)
        data = json.loads(result)
        assert data["error"] == expected_format


def test_our_error_handling_preserves_error_details():
    """Test that our error handling preserves important error information."""
    # Test with detailed error
    detailed_error = ValueError("Invalid partner_id: must be positive integer, got 0")
    result = handle_kaltura_error(detailed_error, "validate config")

    data = json.loads(result)
    assert "must be positive integer" in data["error"]
    assert "got 0" in data["error"]
    assert data["errorType"] == "ValueError"
