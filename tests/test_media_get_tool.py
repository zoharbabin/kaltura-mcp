"""
Tests for the Kaltura MCP Server media.get tool handler.
"""

import json
from unittest.mock import MagicMock

import pytest

from kaltura_mcp.tools.media import MediaGetToolHandler


@pytest.mark.anyio
async def test_media_get_tool(mock_kaltura_client):
    """Test the media.get tool."""
    # Create tool handler
    handler = MediaGetToolHandler(mock_kaltura_client)

    # Mock Kaltura API response
    mock_entry = MagicMock()
    mock_entry.id = "test_id"
    mock_entry.name = "Test Entry"
    mock_entry.description = "Test Description"
    mock_entry.createdAt = 1234567890
    mock_entry.updatedAt = 1234567890
    mock_entry.status.value = 2
    mock_entry.mediaType.value = 1
    mock_entry.duration = 60
    mock_entry.thumbnailUrl = "https://example.com/thumbnail.jpg"
    mock_entry.downloadUrl = "https://example.com/download.mp4"
    mock_entry.plays = 100
    mock_entry.views = 200
    mock_entry.width = 1280
    mock_entry.height = 720
    mock_entry.tags = "tag1, tag2"

    mock_kaltura_client.execute_request.return_value = mock_entry

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
    assert response["description"] == "Test Description"
    assert response["createdAt"] == 1234567890
    assert response["updatedAt"] == 1234567890
    assert response["status"] == 2
    assert response["mediaType"] == 1
    assert response["duration"] == 60
    assert response["thumbnailUrl"] == "https://example.com/thumbnail.jpg"
    assert response["downloadUrl"] == "https://example.com/download.mp4"
    assert response["plays"] == 100
    assert response["views"] == 200
    assert response["width"] == 1280
    assert response["height"] == 720
    assert response["tags"] == "tag1, tag2"

    # Verify Kaltura API call
    mock_kaltura_client.execute_request.assert_called_once()
    args = mock_kaltura_client.execute_request.call_args[0]
    kwargs = mock_kaltura_client.execute_request.call_args[1]

    assert args[0] == "media"
    assert args[1] == "get"
    assert kwargs["entryId"] == "test_id"


@pytest.mark.anyio
async def test_media_get_tool_missing_params(mock_kaltura_client):
    """Test the media.get tool with missing parameters."""
    # Create tool handler
    handler = MediaGetToolHandler(mock_kaltura_client)

    # Call handler with missing parameters
    with pytest.raises(ValueError, match="Missing required parameter: entry_id"):
        await handler.handle({})


def test_media_get_tool_definition():
    """Test the media.get tool definition."""
    # Create tool handler
    handler = MediaGetToolHandler(None)

    # Get tool definition
    definition = handler.get_tool_definition()

    # Verify definition
    assert definition.name == "kaltura.media.get"
    assert "description" in definition.model_dump()
    assert "inputSchema" in definition.model_dump()

    # Verify input schema
    schema = definition.inputSchema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "entry_id" in schema["properties"]
    assert "required" in schema
    assert "entry_id" in schema["required"]
