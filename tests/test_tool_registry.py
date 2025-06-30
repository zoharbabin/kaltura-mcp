"""Test our tool registration and discovery logic."""

import pytest

from kaltura_mcp.server import list_tools


@pytest.mark.asyncio
async def test_our_tool_discovery():
    """Test that our tools are discoverable and properly structured."""
    # Test our current tool listing functionality
    tools = await list_tools()

    # Should find our core tools
    assert len(tools) > 0
    tool_names = [tool.name for tool in tools]

    # Test our expected tools are registered
    expected_tools = [
        "get_media_entry",
        "list_categories",
        "get_analytics",
        "get_download_url",
        "get_thumbnail_url",
        "search_entries",
    ]

    for expected_tool in expected_tools:
        assert (
            expected_tool in tool_names
        ), f"Expected tool {expected_tool} not found in {tool_names}"


@pytest.mark.asyncio
async def test_our_tool_schema_structure():
    """Test that our tools have proper schema structure."""
    tools = await list_tools()

    for tool in tools:
        # Test our tool structure requirements
        assert hasattr(tool, "name"), f"Tool missing name: {tool}"
        assert hasattr(tool, "description"), f"Tool {tool.name} missing description"
        assert hasattr(tool, "inputSchema"), f"Tool {tool.name} missing inputSchema"

        # Test our schema structure
        schema = tool.inputSchema
        assert isinstance(schema, dict), f"Tool {tool.name} schema should be dict"
        assert schema.get("type") == "object", f"Tool {tool.name} schema type should be 'object'"
        assert "properties" in schema, f"Tool {tool.name} schema missing properties"


@pytest.mark.asyncio
async def test_our_required_tools_have_proper_schemas():
    """Test that our critical tools have proper input validation."""
    tools = await list_tools()
    tool_by_name = {tool.name: tool for tool in tools}

    # Test get_media_entry requires entry_id
    media_tool = tool_by_name.get("get_media_entry")
    assert media_tool is not None
    assert "entry_id" in media_tool.inputSchema["properties"]
    assert "entry_id" in media_tool.inputSchema.get("required", [])

    # Test get_analytics requires date range
    analytics_tool = tool_by_name.get("get_analytics")
    assert analytics_tool is not None
    properties = analytics_tool.inputSchema["properties"]
    required = analytics_tool.inputSchema.get("required", [])
    assert "from_date" in properties
    assert "to_date" in properties
    assert "from_date" in required
    assert "to_date" in required


def test_our_tool_imports():
    """Test that our tool functions can be imported."""
    # Test our tool imports work
    from kaltura_mcp.tools import (
        get_analytics,
        get_media_entry,
        handle_kaltura_error,
        list_categories,
        validate_entry_id,
    )

    # Test they are callable
    assert callable(get_media_entry)
    assert callable(list_categories)
    assert callable(get_analytics)
    assert callable(validate_entry_id)
    assert callable(handle_kaltura_error)


def test_our_tool_validation_exists():
    """Test that our validation utilities exist."""
    from kaltura_mcp.tools import validate_entry_id

    # Test our validation function exists and works
    assert validate_entry_id("123_test") is True
    assert validate_entry_id("invalid") is False


def test_our_error_handling_exists():
    """Test that our error handling utilities exist."""
    from kaltura_mcp.tools import handle_kaltura_error

    # Test our error handler exists and works
    error = ValueError("test error")
    result = handle_kaltura_error(error, "test operation")

    # Should return JSON string
    assert isinstance(result, str)
    assert "test error" in result
    assert "test operation" in result
