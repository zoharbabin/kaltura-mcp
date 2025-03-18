"""
Tests for the Kaltura MCP Server resource handlers.
"""

import json
from unittest.mock import MagicMock

import pytest

from kaltura_mcp.resources.media import MediaEntryResourceHandler, MediaListResourceHandler


def test_media_entry_resource_uri_pattern():
    """Test the media entry resource URI pattern."""
    # Create resource handler
    handler = MediaEntryResourceHandler(None)

    # Test valid URIs
    assert handler.matches_uri("kaltura://media/123456")
    assert handler.matches_uri("kaltura://media/abc_123")

    # Test invalid URIs
    assert not handler.matches_uri("kaltura://media")
    assert not handler.matches_uri("kaltura://media/")
    assert not handler.matches_uri("kaltura://media/123/456")
    assert not handler.matches_uri("kaltura://categories/123")


def test_media_list_resource_uri_pattern():
    """Test the media list resource URI pattern."""
    # Create resource handler
    handler = MediaListResourceHandler(None)

    # Test valid URIs
    assert handler.matches_uri("kaltura://media/list")
    assert handler.matches_uri("kaltura://media/list?page_size=10")
    assert handler.matches_uri("kaltura://media/list?page_size=10&page_index=2")
    assert handler.matches_uri("kaltura://media/list?name_like=test")

    # Test invalid URIs
    assert not handler.matches_uri("kaltura://media")
    assert not handler.matches_uri("kaltura://media/")
    assert not handler.matches_uri("kaltura://media/123")
    assert not handler.matches_uri("kaltura://categories/list")


@pytest.mark.anyio
async def test_media_entry_resource_handler(mock_kaltura_client):
    """Test the media entry resource handler."""
    # Create resource handler
    handler = MediaEntryResourceHandler(mock_kaltura_client)

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
    result = await handler.handle("kaltura://media/test_id")

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
async def test_media_list_resource_handler(mock_kaltura_client):
    """Test the media list resource handler."""
    # Create resource handler
    handler = MediaListResourceHandler(mock_kaltura_client)

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
    result = await handler.handle("kaltura://media/list?page_size=10&page_index=2&name_like=test")

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
    assert response["pageIndex"] == 2
    assert len(response["entries"]) == 1

    # Verify entry values
    entry = response["entries"][0]
    assert entry["id"] == "test_id"
    assert entry["name"] == "Test Entry"

    # Verify Kaltura API call
    mock_kaltura_client.execute_request.assert_called_once()
    args = mock_kaltura_client.execute_request.call_args[0]
    kwargs = mock_kaltura_client.execute_request.call_args[1]

    assert args[0] == "media"
    assert args[1] == "list"
    assert "filter" in kwargs
    assert "pager" in kwargs
    assert kwargs["pager"].pageSize == 10
    assert kwargs["pager"].pageIndex == 2
    assert kwargs["filter"].nameLike == "test"
