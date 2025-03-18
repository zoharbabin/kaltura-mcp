"""
Tests for user resources.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from KalturaClient.Plugins.Core import KalturaUser, KalturaUserListResponse

from kaltura_mcp.resources.user import UserListResourceHandler, UserResourceHandler


@pytest.fixture
def mock_kaltura_client():
    """Create a mock Kaltura client."""
    client = MagicMock()
    client.execute_request = AsyncMock()
    return client


@pytest.fixture
def mock_user():
    """Create a mock user."""
    user = MagicMock(spec=KalturaUser)
    user.id = "test_user_id"
    user.partnerId = 123
    user.screenName = "Test User"
    user.fullName = "Test User Full Name"
    user.email = "test@example.com"
    user.status = MagicMock(value=1)
    user.createdAt = 1615000000
    user.updatedAt = 1615100000
    user.lastLoginTime = 1615200000
    user.roleIds = "1,2,3"
    user.isAdmin = False
    user.type = MagicMock(value=0)
    return user


@pytest.mark.asyncio
async def test_user_resource_handler(mock_kaltura_client, mock_user):
    """Test the user resource handler."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_user
    handler = UserResourceHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle("kaltura://user/test_user_id")

    # Verify
    mock_kaltura_client.execute_request.assert_called_once_with("user", "get", userId="test_user_id")
    response = json.loads(result[0].text)
    assert response["id"] == "test_user_id"
    assert response["fullName"] == "Test User Full Name"
    assert response["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_user_resource_handler_invalid_uri(mock_kaltura_client):
    """Test the user resource handler with an invalid URI."""
    # Setup
    handler = UserResourceHandler(mock_kaltura_client)

    # Execute and verify
    with pytest.raises(ValueError, match="Invalid user URI"):
        await handler.handle("kaltura://user/")


@pytest.mark.asyncio
async def test_user_list_resource_handler(mock_kaltura_client):
    """Test the user list resource handler."""
    # Setup
    mock_response = MagicMock(spec=KalturaUserListResponse)
    mock_response.totalCount = 2

    # Create user objects with proper attributes
    user1 = MagicMock()
    user1.id = "user1"
    user1.partnerId = 123
    user1.screenName = "User 1"
    user1.fullName = "User One"
    user1.email = "user1@example.com"
    user1.status = MagicMock()
    user1.status.value = 1
    user1.createdAt = 1615000000
    user1.updatedAt = 1615100000
    user1.lastLoginTime = 1615200000
    user1.roleIds = "1,2"
    user1.isAdmin = False
    user1.type = MagicMock()
    user1.type.value = 0

    user2 = MagicMock()
    user2.id = "user2"
    user2.partnerId = 123
    user2.screenName = "User 2"
    user2.fullName = "User Two"
    user2.email = "user2@example.com"
    user2.status = MagicMock()
    user2.status.value = 1
    user2.createdAt = 1615000000
    user2.updatedAt = 1615100000
    user2.lastLoginTime = 1615200000
    user2.roleIds = "1,3"
    user2.isAdmin = True
    user2.type = MagicMock()
    user2.type.value = 0

    mock_response.objects = [user1, user2]
    mock_kaltura_client.execute_request.return_value = mock_response
    handler = UserListResourceHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle("kaltura://user/list?page_size=10&page_index=1&id_or_name_starts_with=user")

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "list"
    response = json.loads(result[0].text)
    assert response["totalCount"] == 2
    assert len(response["users"]) == 2
    assert response["users"][0]["id"] == "user1"
    assert response["users"][1]["id"] == "user2"


def test_user_resource_handler_matches_uri():
    """Test the user resource handler URI matching."""
    # Setup
    handler = UserResourceHandler(None)

    # Execute and verify
    assert handler.matches_uri("kaltura://user/test_user_id")
    assert not handler.matches_uri("kaltura://user/")
    assert not handler.matches_uri("kaltura://user/list")
    assert not handler.matches_uri("kaltura://category/test_user_id")


def test_user_list_resource_handler_matches_uri():
    """Test the user list resource handler URI matching."""
    # Setup
    handler = UserListResourceHandler(None)

    # Execute and verify
    assert handler.matches_uri("kaltura://user/list")
    assert handler.matches_uri("kaltura://user/list?page_size=10")
    assert not handler.matches_uri("kaltura://user/test_user_id")
    assert not handler.matches_uri("kaltura://category/list")


def test_user_resource_definition():
    """Test the user resource definition."""
    # Setup
    handler = UserResourceHandler(None)

    # Execute
    definition = handler.get_resource_definition()

    # Verify
    assert "user" in str(definition.uri)
    assert "userId" in str(definition.uri)
    assert definition.name == "Kaltura User"
    assert definition.description == "Get details of a specific user"
    assert definition.mimeType == "application/json"


def test_user_list_resource_definition():
    """Test the user list resource definition."""
    # Setup
    handler = UserListResourceHandler(None)

    # Execute
    definition = handler.get_resource_definition()

    # Verify
    assert str(definition.uri) == "kaltura://user/list"
    assert definition.name == "Kaltura User List"
    assert definition.description == "List users with optional filtering"
    assert definition.mimeType == "application/json"
