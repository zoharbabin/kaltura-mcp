# Add Basic Unit Tests - CRITICAL (1.5 hours)

**Complexity**: Simple (upgraded from Medium)  
**Impact**: Critical - Ensures code reliability and prevents regressions  
**Priority**: CRITICAL (blocking safe refactoring)  
**Time Estimate**: 1.5 hours (reduced - focus on business logic only)  
**Note**: No external library testing, no complex mocking, no integration tests  
**Dependencies**: None (this is now a prerequisite)

## Problem
The project lacks test coverage, making it difficult to ensure code quality, prevent regressions, and safely refactor code.

## Solution
Implement focused unit tests for **our business logic only**. No testing of external libraries (MCP, Kaltura SDK, standard library). Focus on validation rules, security checks, tool registry pattern, and error handling that we actually wrote.

## Implementation Steps

### 1. Create Minimal Test Structure (5 minutes)
```bash
# Create test directory
mkdir -p tests

# Create focused test files
touch tests/__init__.py
touch tests/conftest.py
touch tests/test_config.py
touch tests/test_validation.py
touch tests/test_tool_registry.py
touch tests/test_error_handling.py
```

### 2. Create Minimal Fixtures (10 minutes)
**File: `tests/conftest.py`**
```python
"""Minimal pytest fixtures for testing our business logic."""

import pytest

@pytest.fixture
def valid_config_data():
    """Valid configuration data for testing our validation."""
    return {
        "partner_id": 12345,
        "service_url": "https://test.kaltura.com",
        "admin_secret": "test_secret_12345678",
        "user_id": "test@example.com",
        "session_expiry": 86400
    }
```

### 3. Create Configuration Tests (30 minutes)
**File: `tests/test_config.py`**
```python
"""Test our configuration validation logic only."""

import pytest
from kaltura_mcp.config import KalturaConfig


def test_our_kaltura_config_validation_rules(valid_config_data):
    """Test OUR validation rules for Kaltura configuration."""
    
    # Test valid config creates successfully
    config = KalturaConfig(**valid_config_data)
    assert config.partner_id == 12345
    assert config.service_url == "https://test.kaltura.com"
    
    # Test our partner_id validation
    with pytest.raises(ValueError, match="partner_id must be a positive integer"):
        KalturaConfig(partner_id=0, **{k:v for k,v in valid_config_data.items() if k != 'partner_id'})
    
    # Test our service_url validation  
    with pytest.raises(ValueError, match="service_url must start with"):
        KalturaConfig(service_url="invalid-url", **{k:v for k,v in valid_config_data.items() if k != 'service_url'})
    
    # Test our admin_secret length validation
    with pytest.raises(ValueError, match="admin_secret must be at least 8 characters"):
        KalturaConfig(admin_secret="short", **{k:v for k,v in valid_config_data.items() if k != 'admin_secret'})
    
    # Test our session_expiry validation
    with pytest.raises(ValueError, match="session_expiry must be at least 300 seconds"):
        KalturaConfig(session_expiry=100, **{k:v for k,v in valid_config_data.items() if k != 'session_expiry'})


def test_our_credential_masking_logic(valid_config_data):
    """Test OUR credential masking implementation."""
    config = KalturaConfig(**valid_config_data)
    
    # Test our masking logic
    masked = config.mask_secrets()
    assert masked['admin_secret'] == 'tes***'  # Our masking format
    assert 'test_secret_12345678' not in str(masked)  # Secret not exposed
    assert masked['partner_id'] == 12345  # Non-secret values preserved
```

### 4. Create Validation Tests (15 minutes)
**File: `tests/test_validation.py`**
```python
"""Test our input validation security logic."""

import pytest
from kaltura_mcp.tools.utils import validate_entry_id


@pytest.mark.parametrize("entry_id,expected", [
    # Our valid format
    ("123_abc123", True),
    ("999_test", True),
    
    # Our security blocks - path traversal
    ("123_../etc/passwd", False),
    ("123_test/../config", False),
    ("123_..\\windows", False),
    
    # Our security blocks - command injection  
    ("123_$(rm -rf /)", False),
    ("123_`cat /etc/passwd`", False),
    ("123_; rm -rf /", False),
    ("123_&& echo 'pwned'", False),
    ("123_| cat /etc/hosts", False),
    
    # Our format validation
    ("invalid_format", False),    # Must start with number
    ("123", False),               # Must have underscore
    ("", False),                   # Empty string
    ("123_", False),              # Empty after underscore
    
    # Our length validation
    ("1_" + "a" * 100, False),    # Too long (our limit)
    ("1_" + "a" * 47, True),      # Within our limit
])
def test_validate_entry_id_our_security_rules(entry_id, expected):
    """Test OUR entry ID validation and security rules."""
    assert validate_entry_id(entry_id) == expected


def test_validate_entry_id_type_safety():
    """Test our type checking logic."""
    # Our type validation
    assert validate_entry_id(None) is False
    assert validate_entry_id(123) is False
    assert validate_entry_id([]) is False
    assert validate_entry_id({}) is False
```

### 5. Create Tool Registry Tests (30 minutes)
**File: `tests/test_tool_registry.py`**
```python
"""Test our tool registry pattern."""

import pytest
from kaltura_mcp.tool_registry import ToolRegistry, register_tool
from kaltura_mcp.tools.base import BaseTool


class MockTool(BaseTool):
    """Simple mock tool for testing our registry logic."""
    
    @property
    def name(self):
        return "mock_tool"
    
    @property  
    def description(self):
        return "Test tool for registry"
    
    @property
    def input_schema(self):
        return {"type": "object", "properties": {}}
    
    async def execute(self, manager, **kwargs):
        return '{"test": "result"}'


def test_our_tool_registration():
    """Test OUR tool registration logic."""
    registry = ToolRegistry()
    registry.register(MockTool, "test_category")
    
    # Test our registration worked
    assert "mock_tool" in registry.list_tool_names()
    assert "mock_tool" in registry.get_tools_by_category("test_category")
    assert len(registry.list_tool_names()) == 1


def test_our_duplicate_registration_handling():
    """Test OUR duplicate registration logic."""
    registry = ToolRegistry()
    
    # Register same tool twice
    registry.register(MockTool, "test")
    registry.register(MockTool, "test")  # Should not error
    
    # Should still only have one tool
    assert len(registry.list_tool_names()) == 1


def test_our_tool_discovery():
    """Test OUR auto-discovery logic."""
    registry = ToolRegistry()
    
    # Test our module scanning works
    count = registry.auto_discover("kaltura_mcp.tools")
    assert count > 0
    assert len(registry.list_tool_names()) > 0
    
    # Should find real tools from our codebase
    tool_names = registry.list_tool_names()
    assert any("media" in name or "search" in name for name in tool_names)


def test_our_registry_categories():
    """Test OUR category organization logic."""
    registry = ToolRegistry()
    registry.register(MockTool, "test_category")
    
    # Test our category logic
    categories = registry.get_categories()
    assert "test_category" in categories
    
    tools_in_category = registry.get_tools_by_category("test_category")
    assert "mock_tool" in tools_in_category
```

### 6. Create Error Handling Tests (15 minutes)
**File: `tests/test_error_handling.py`**
```python
"""Test our error response format."""

import json
from kaltura_mcp.tools.utils import handle_kaltura_error


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
    ]
    
    for error, expected_type in test_cases:
        result = handle_kaltura_error(error, "test operation")
        data = json.loads(result)
        assert data["errorType"] == expected_type
        assert "Failed to test operation:" in data["error"]
```

### 7. Running Tests (5 minutes)
```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_config.py -v
pytest tests/test_validation.py -v
pytest tests/test_tool_registry.py -v
pytest tests/test_error_handling.py -v

# Run with verbose output for debugging
pytest tests/ -v -s
```


## Benefits
- ✅ **Focused testing** - Only tests our business logic, not libraries
- ✅ **Fast execution** - No external dependencies or complex mocking
- ✅ **Prevents critical failures** - Tests validation that prevents startup/security issues
- ✅ **Enables safe refactoring** - Core logic is protected
- ✅ **Easy maintenance** - Tests actual behavior we control
- ✅ **Security validation** - Entry ID validation prevents injection attacks
- ✅ **Configuration safety** - Invalid configs are caught early
- ✅ **Registry architecture** - Tool discovery and execution is validated

## Files Created
- `tests/conftest.py` (minimal fixtures)
- `tests/test_config.py` (configuration validation)
- `tests/test_validation.py` (security validation)
- `tests/test_tool_registry.py` (registry pattern)
- `tests/test_error_handling.py` (error format)

## What We Don't Test (And Why)
- ❌ **MCP library** - Not our code, well-tested by Anthropic
- ❌ **Kaltura SDK** - Not our code, tested by Kaltura
- ❌ **Standard library** - JSON, datetime, regex are well-tested
- ❌ **HTTP handling** - FastAPI's responsibility
- ❌ **File operations** - OS responsibility

## Running Tests
```bash
# Run all essential tests
pytest tests/ -v

# Fast smoke test  
pytest tests/test_config.py tests/test_validation.py -v

# Test specific functionality
pytest tests/test_tool_registry.py -v
```

This approach gives us **maximum safety with minimum effort** - testing the 20% of code that prevents 80% of production issues.