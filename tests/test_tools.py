"""
Tests for the Kaltura MCP Server tool handlers.
"""

import json
from unittest.mock import MagicMock

import pytest

from kaltura_mcp.tools.media import MediaListToolHandler


@pytest.mark.anyio
async def test_media_list_tool(mock_kaltura_client):
    """Test the media.list tool."""
    # Create tool handler
    handler = MediaListToolHandler(mock_kaltura_client)

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

    mock_result = MagicMock()
    mock_result.objects = [mock_entry]
    mock_result.totalCount = 1

    mock_kaltura_client.execute_request.return_value = mock_result

    # Call handler
    result = await handler.handle({"page_size": 10, "page_index": 1, "filter": {"nameLike": "test"}})

    # Verify result
    assert len(result) == 1
    assert result[0].type == "text"

    # Parse JSON response
    response = json.loads(result[0].text)

    # Verify response structure
    assert "totalCount" in response
    assert "entries" in response
    assert "pageSize" in response
    assert "pageIndex" in response

    # Verify response values
    assert response["totalCount"] == 1
    assert response["pageSize"] == 10
    assert response["pageIndex"] == 1
    assert len(response["entries"]) == 1

    # Verify entry values
    entry = response["entries"][0]
    assert entry["id"] == "test_id"
    assert entry["name"] == "Test Entry"
    assert entry["description"] == "Test Description"
    assert entry["createdAt"] == 1234567890
    assert entry["updatedAt"] == 1234567890
    assert entry["status"] == 2
    assert entry["mediaType"] == 1
    assert entry["duration"] == 60
    assert entry["thumbnailUrl"] == "https://example.com/thumbnail.jpg"

    # Verify Kaltura API call
    mock_kaltura_client.execute_request.assert_called_once()
    args = mock_kaltura_client.execute_request.call_args[0]
    kwargs = mock_kaltura_client.execute_request.call_args[1]

    assert args[0] == "media"
    assert args[1] == "list"
    assert "filter" in kwargs
    assert "pager" in kwargs


def test_media_list_tool_definition():
    """Test the media.list tool definition."""
    # Create tool handler
    handler = MediaListToolHandler(None)

    # Get tool definition
    definition = handler.get_tool_definition()

    # Verify definition
    assert definition.name == "kaltura.media.list"
    assert "description" in definition.model_dump()
    assert "inputSchema" in definition.model_dump()

    # Verify input schema
    schema = definition.inputSchema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "filter" in schema["properties"]
    assert "page_size" in schema["properties"]
    assert "page_index" in schema["properties"]
