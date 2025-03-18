"""
Tests for the Kaltura MCP Server media.delete tool handler.
"""

import json
from unittest.mock import MagicMock

import pytest

from kaltura_mcp.tools.media import MediaDeleteToolHandler


@pytest.mark.anyio
async def test_media_delete_tool(mock_kaltura_client):
    """Test the media.delete tool."""
    # Create tool handler
    handler = MediaDeleteToolHandler(mock_kaltura_client)

    # Mock Kaltura API responses
    mock_entry = MagicMock()
    mock_entry.id = "test_id"
    mock_entry.name = "Test Entry"

    # Set up the mock to return different values for different calls
    mock_kaltura_client.execute_request.side_effect = [
        mock_entry,  # media.get
        None,  # media.delete (returns None on success)
    ]

    # Call handler
    result = await handler.handle({"entry_id": "test_id"})

    # Verify result
    assert len(result) == 1
    assert result[0].type == "text"

    # Parse JSON response
    response = json.loads(result[0].text)

    # Verify response values
    assert response["id"] == "test_id"
    assert response["name"] == "Test Entry"
    assert "message" in response
    assert "deleted successfully" in response["message"]

    # Verify Kaltura API calls
    assert mock_kaltura_client.execute_request.call_count == 2

    # Verify media.get call
    call_args = mock_kaltura_client.execute_request.call_args_list[0]
    assert call_args[0][0] == "media"
    assert call_args[0][1] == "get"
    assert call_args[1]["entryId"] == "test_id"

    # Verify media.delete call
    call_args = mock_kaltura_client.execute_request.call_args_list[1]
    assert call_args[0][0] == "media"
    assert call_args[0][1] == "delete"
    assert call_args[1]["entryId"] == "test_id"


@pytest.mark.anyio
async def test_media_delete_tool_error(mock_kaltura_client):
    """Test the media.delete tool with an error."""
    # Create tool handler
    handler = MediaDeleteToolHandler(mock_kaltura_client)

    # Mock Kaltura API error
    mock_kaltura_client.execute_request.side_effect = Exception("Entry not found")

    # Call handler
    result = await handler.handle({"entry_id": "nonexistent_id"})

    # Verify result
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error deleting media entry" in result[0].text


@pytest.mark.anyio
async def test_media_delete_tool_missing_params(mock_kaltura_client):
    """Test the media.delete tool with missing parameters."""
    # Create tool handler
    handler = MediaDeleteToolHandler(mock_kaltura_client)

    # Call handler with missing entry_id
    with pytest.raises(ValueError, match="Missing required parameter: entry_id"):
        await handler.handle({})


def test_media_delete_tool_definition():
    """Test the media.delete tool definition."""
    # Create tool handler
    handler = MediaDeleteToolHandler(None)

    # Get tool definition
    definition = handler.get_tool_definition()

    # Verify definition
    assert definition.name == "kaltura.media.delete"
    assert "description" in definition.model_dump()
    assert "inputSchema" in definition.model_dump()

    # Verify input schema
    schema = definition.inputSchema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "entry_id" in schema["properties"]
    assert "required" in schema
    assert "entry_id" in schema["required"]
