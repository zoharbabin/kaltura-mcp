"""
Tests for the Kaltura MCP Server media.update tool handler.
"""

import json
from unittest.mock import MagicMock

import pytest

from kaltura_mcp.tools.media import MediaUpdateToolHandler


@pytest.mark.anyio
async def test_media_update_tool(mock_kaltura_client):
    """Test the media.update tool."""
    # Create tool handler
    handler = MediaUpdateToolHandler(mock_kaltura_client)

    # Mock Kaltura API responses
    mock_current_entry = MagicMock()
    mock_current_entry.id = "test_id"
    mock_current_entry.name = "Original Name"
    mock_current_entry.description = "Original Description"
    mock_current_entry.tags = "original, tags"

    mock_updated_entry = MagicMock()
    mock_updated_entry.id = "test_id"
    mock_updated_entry.name = "Updated Name"
    mock_updated_entry.description = "Updated Description"
    mock_updated_entry.tags = "updated, tags"
    mock_updated_entry.createdAt = 1234567890
    mock_updated_entry.updatedAt = 1234567899
    mock_updated_entry.status.value = 2
    mock_updated_entry.mediaType.value = 1
    mock_updated_entry.duration = 60
    mock_updated_entry.thumbnailUrl = "https://example.com/thumbnail.jpg"

    # Set up the mock to return different values for different calls
    mock_kaltura_client.execute_request.side_effect = [
        mock_current_entry,  # media.get
        mock_updated_entry,  # media.update
    ]

    # Call handler
    result = await handler.handle(
        {
            "entry_id": "test_id",
            "name": "Updated Name",
            "description": "Updated Description",
            "tags": "updated, tags",
        }
    )

    # Verify result
    assert len(result) == 1
    assert result[0].type == "text"

    # Parse JSON response
    response = json.loads(result[0].text)

    # Verify response values
    assert response["id"] == "test_id"
    assert response["name"] == "Updated Name"
    assert response["description"] == "Updated Description"
    assert response["tags"] == "updated, tags"
    assert response["createdAt"] == 1234567890
    assert response["updatedAt"] == 1234567899
    assert response["status"] == 2
    assert response["mediaType"] == 1
    assert response["duration"] == 60
    assert response["thumbnailUrl"] == "https://example.com/thumbnail.jpg"
    assert "message" in response

    # Verify Kaltura API calls
    assert mock_kaltura_client.execute_request.call_count == 2

    # Verify media.get call
    call_args = mock_kaltura_client.execute_request.call_args_list[0]
    assert call_args[0][0] == "media"
    assert call_args[0][1] == "get"
    assert call_args[1]["entryId"] == "test_id"

    # Verify media.update call
    call_args = mock_kaltura_client.execute_request.call_args_list[1]
    assert call_args[0][0] == "media"
    assert call_args[0][1] == "update"
    assert call_args[1]["entryId"] == "test_id"
    assert call_args[1]["mediaEntry"].name == "Updated Name"
    assert call_args[1]["mediaEntry"].description == "Updated Description"
    assert call_args[1]["mediaEntry"].tags == "updated, tags"


@pytest.mark.anyio
async def test_media_update_tool_partial_update(mock_kaltura_client):
    """Test the media.update tool with partial update."""
    # Create tool handler
    handler = MediaUpdateToolHandler(mock_kaltura_client)

    # Mock Kaltura API responses
    mock_current_entry = MagicMock()
    mock_current_entry.id = "test_id"
    mock_current_entry.name = "Original Name"
    mock_current_entry.description = "Original Description"
    mock_current_entry.tags = "original, tags"

    mock_updated_entry = MagicMock()
    mock_updated_entry.id = "test_id"
    mock_updated_entry.name = "Updated Name"
    mock_updated_entry.description = "Original Description"  # Unchanged
    mock_updated_entry.tags = "original, tags"  # Unchanged
    mock_updated_entry.createdAt = 1234567890
    mock_updated_entry.updatedAt = 1234567899
    mock_updated_entry.status = MagicMock()
    mock_updated_entry.status.value = 2
    mock_updated_entry.mediaType = MagicMock()
    mock_updated_entry.mediaType.value = 1
    mock_updated_entry.duration = 60
    mock_updated_entry.thumbnailUrl = "https://example.com/thumbnail.jpg"

    # Set up the mock to return different values for different calls
    mock_kaltura_client.execute_request.side_effect = [
        mock_current_entry,  # media.get
        mock_updated_entry,  # media.update
    ]

    # Call handler with only name update
    result = await handler.handle({"entry_id": "test_id", "name": "Updated Name"})

    # Verify result
    assert len(result) == 1

    # Parse JSON response
    response = json.loads(result[0].text)

    # Verify response values
    assert response["name"] == "Updated Name"
    assert response["description"] == "Original Description"  # Should keep original
    assert response["tags"] == "original, tags"  # Should keep original

    # Verify Kaltura API calls
    assert mock_kaltura_client.execute_request.call_count == 2

    # Verify media.update call
    call_args = mock_kaltura_client.execute_request.call_args_list[1]
    assert call_args[1]["mediaEntry"].name == "Updated Name"
    assert call_args[1]["mediaEntry"].description == "Original Description"
    assert call_args[1]["mediaEntry"].tags == "original, tags"


@pytest.mark.anyio
async def test_media_update_tool_missing_params(mock_kaltura_client):
    """Test the media.update tool with missing parameters."""
    # Create tool handler
    handler = MediaUpdateToolHandler(mock_kaltura_client)

    # Call handler with missing entry_id
    with pytest.raises(ValueError, match="Missing required parameter: entry_id"):
        await handler.handle({"name": "Updated Name"})


def test_media_update_tool_definition():
    """Test the media.update tool definition."""
    # Create tool handler
    handler = MediaUpdateToolHandler(None)

    # Get tool definition
    definition = handler.get_tool_definition()

    # Verify definition
    assert definition.name == "kaltura.media.update"
    assert "description" in definition.model_dump()
    assert "inputSchema" in definition.model_dump()

    # Verify input schema
    schema = definition.inputSchema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "entry_id" in schema["properties"]
    assert "name" in schema["properties"]
    assert "description" in schema["properties"]
    assert "tags" in schema["properties"]
    assert "required" in schema
    assert "entry_id" in schema["required"]
