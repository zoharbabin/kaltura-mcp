"""
Tests for category resources.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from KalturaClient.Plugins.Core import KalturaCategory, KalturaCategoryListResponse

from kaltura_mcp.resources.category import CategoryListResourceHandler, CategoryResourceHandler


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
async def test_category_resource_handler(mock_kaltura_client, mock_category):
    """Test the category resource handler."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_category
    handler = CategoryResourceHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle("kaltura://category/123")

    # Verify
    mock_kaltura_client.execute_request.assert_called_once_with("category", "get", id=123)
    response = json.loads(result[0].text)
    assert response["id"] == 123
    assert response["name"] == "Test Category"
    assert response["description"] == "Test Description"


@pytest.mark.asyncio
async def test_category_resource_handler_invalid_uri(mock_kaltura_client):
    """Test the category resource handler with an invalid URI."""
    # Setup
    handler = CategoryResourceHandler(mock_kaltura_client)

    # Execute and verify
    with pytest.raises(ValueError, match="Invalid category URI"):
        await handler.handle("kaltura://category/")


@pytest.mark.asyncio
async def test_category_list_resource_handler(mock_kaltura_client):
    """Test the category list resource handler."""
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
    handler = CategoryListResourceHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle("kaltura://category/list?page_size=10&page_index=1&name_like=test")

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "category"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "list"
    response = json.loads(result[0].text)
    assert response["totalCount"] == 2
    assert len(response["categories"]) == 2
    assert response["categories"][0]["id"] == 123
    assert response["categories"][1]["id"] == 456


def test_category_resource_handler_matches_uri():
    """Test the category resource handler URI matching."""
    # Setup
    handler = CategoryResourceHandler(None)

    # Execute and verify
    assert handler.matches_uri("kaltura://category/123")
    assert not handler.matches_uri("kaltura://category/")
    assert not handler.matches_uri("kaltura://category/list")
    assert not handler.matches_uri("kaltura://media/123")


def test_category_list_resource_handler_matches_uri():
    """Test the category list resource handler URI matching."""
    # Setup
    handler = CategoryListResourceHandler(None)

    # Execute and verify
    assert handler.matches_uri("kaltura://category/list")
    assert handler.matches_uri("kaltura://category/list?page_size=10")
    assert not handler.matches_uri("kaltura://category/123")
    assert not handler.matches_uri("kaltura://media/list")


def test_category_resource_definition():
    """Test the category resource definition."""
    # Setup
    handler = CategoryResourceHandler(None)

    # Execute
    definition = handler.get_resource_definition()

    # Verify
    assert "category" in str(definition.uri)
    assert "categoryId" in str(definition.uri)
    assert definition.name == "Kaltura Category"
    assert definition.description == "Get details of a specific category"
    assert definition.mimeType == "application/json"


def test_category_list_resource_definition():
    """Test the category list resource definition."""
    # Setup
    handler = CategoryListResourceHandler(None)

    # Execute
    definition = handler.get_resource_definition()

    # Verify
    assert str(definition.uri) == "kaltura://category/list"
    assert definition.name == "Kaltura Category List"
    assert definition.description == "List categories with optional filtering"
    assert definition.mimeType == "application/json"
