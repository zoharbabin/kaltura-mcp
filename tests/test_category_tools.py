"""
Tests for category tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from KalturaClient.Plugins.Core import KalturaCategory, KalturaCategoryListResponse

from kaltura_mcp.tools.category import (
    CategoryAddToolHandler,
    CategoryDeleteToolHandler,
    CategoryGetToolHandler,
    CategoryListToolHandler,
    CategoryUpdateToolHandler,
)


@pytest.fixture
def mock_kaltura_client():
    """Create a mock Kaltura client."""
    client = MagicMock()
    client.execute_request = AsyncMock()
    return client


@pytest.fixture
def mock_category():
    """Create a mock category."""
    category = MagicMock(spec=KalturaCategory)
    category.id = 123
    category.name = "Test Category"
    category.fullName = "Test Category"
    category.description = "Test Description"
    category.tags = "test,category"
    category.status = MagicMock(value=2)
    category.createdAt = 1615000000
    category.updatedAt = 1615100000
    category.parentId = 0
    category.depth = 1
    category.entriesCount = 10
    category.fullIds = "123"
    category.privacyContext = ""
    category.privacy = 0
    category.membersCount = 0
    category.pendingMembersCount = 0
    category.owner = "admin"
    return category


@pytest.mark.asyncio
async def test_category_get_tool(mock_kaltura_client, mock_category):
    """Test the category get tool."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_category
    handler = CategoryGetToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": 123})

    # Verify
    mock_kaltura_client.execute_request.assert_called_once_with("category", "get", id=123)
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == 123
    assert response["name"] == "Test Category"


@pytest.mark.asyncio
async def test_category_add_tool(mock_kaltura_client, mock_category):
    """Test the category add tool."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_category
    handler = CategoryAddToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle(
        {
            "name": "Test Category",
            "description": "Test Description",
            "tags": "test,category",
            "parent_id": 0,
        }
    )

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "add"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == 123
    assert response["name"] == "Test Category"
    assert "message" in response


@pytest.mark.asyncio
async def test_category_update_tool(mock_kaltura_client, mock_category):
    """Test the category update tool."""
    # Setup
    mock_kaltura_client.execute_request.side_effect = [mock_category, mock_category]
    handler = CategoryUpdateToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": 123, "name": "Updated Category", "description": "Updated Description"})

    # Verify
    assert mock_kaltura_client.execute_request.call_count == 2
    assert mock_kaltura_client.execute_request.call_args_list[0][0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args_list[0][0][1] == "get"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][1] == "update"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == 123
    assert "message" in response


@pytest.mark.asyncio
async def test_category_delete_tool(mock_kaltura_client, mock_category):
    """Test the category delete tool."""
    # Setup
    mock_kaltura_client.execute_request.side_effect = [mock_category, True]
    handler = CategoryDeleteToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": 123, "move_entries_to_parent": True})

    # Verify
    assert mock_kaltura_client.execute_request.call_count == 2
    assert mock_kaltura_client.execute_request.call_args_list[0][0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args_list[0][0][1] == "get"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][1] == "delete"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == 123
    assert "message" in response


@pytest.mark.asyncio
async def test_category_list_tool(mock_kaltura_client):
    """Test the category list tool."""
    # Setup
    mock_response = MagicMock(spec=KalturaCategoryListResponse)
    mock_response.totalCount = 2

    # Create category objects with proper attributes
    category1 = MagicMock()
    category1.id = 123
    category1.name = "Category 1"
    category1.fullName = "Category 1"
    category1.description = "Description 1"
    category1.tags = "tag1"
    category1.status = MagicMock()
    category1.status.value = 2
    category1.createdAt = 1615000000
    category1.updatedAt = 1615100000
    category1.parentId = 0
    category1.depth = 1
    category1.entriesCount = 5
    category1.fullIds = "123"

    category2 = MagicMock()
    category2.id = 456
    category2.name = "Category 2"
    category2.fullName = "Category 2"
    category2.description = "Description 2"
    category2.tags = "tag2"
    category2.status = MagicMock()
    category2.status.value = 2
    category2.createdAt = 1615000000
    category2.updatedAt = 1615100000
    category2.parentId = 0
    category2.depth = 1
    category2.entriesCount = 10
    category2.fullIds = "456"

    mock_response.objects = [category1, category2]
    mock_kaltura_client.execute_request.return_value = mock_response
    handler = CategoryListToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"page_size": 10, "page_index": 1, "filter": {"nameLike": "test"}})

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "list"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["totalCount"] == 2
    assert len(response["categories"]) == 2
    assert response["categories"][0]["id"] == 123
    assert response["categories"][1]["id"] == 456
