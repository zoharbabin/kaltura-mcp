"""
Tests for user tools.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from KalturaClient.Plugins.Core import KalturaUser, KalturaUserListResponse

from kaltura_mcp.tools.user import (
    UserAddToolHandler,
    UserDeleteToolHandler,
    UserGetToolHandler,
    UserListToolHandler,
    UserUpdateToolHandler,
)


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
async def test_user_get_tool(mock_kaltura_client, mock_user):
    """Test the user get tool."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_user
    handler = UserGetToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": "test_user_id"})

    # Verify
    mock_kaltura_client.execute_request.assert_called_once_with("user", "get", userId="test_user_id")
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == "test_user_id"
    assert response["fullName"] == "Test User Full Name"


@pytest.mark.asyncio
async def test_user_add_tool(mock_kaltura_client, mock_user):
    """Test the user add tool."""
    # Setup
    mock_kaltura_client.execute_request.return_value = mock_user
    handler = UserAddToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle(
        {
            "id": "test_user_id",
            "email": "test@example.com",
            "full_name": "Test User Full Name",
            "screenName": "Test User",
            "role_ids": "1,2,3",
            "is_admin": False,
        }
    )

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "add"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == "test_user_id"
    assert response["email"] == "test@example.com"
    assert "message" in response


@pytest.mark.asyncio
async def test_user_update_tool(mock_kaltura_client, mock_user):
    """Test the user update tool."""
    # Setup
    mock_kaltura_client.execute_request.side_effect = [mock_user, mock_user]
    handler = UserUpdateToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": "test_user_id", "email": "updated@example.com", "full_name": "Updated User Name"})

    # Verify
    assert mock_kaltura_client.execute_request.call_count == 2
    assert mock_kaltura_client.execute_request.call_args_list[0][0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args_list[0][0][1] == "get"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][1] == "update"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == "test_user_id"
    assert "message" in response


@pytest.mark.asyncio
async def test_user_delete_tool(mock_kaltura_client, mock_user):
    """Test the user delete tool."""
    # Setup
    mock_kaltura_client.execute_request.side_effect = [mock_user, True]
    handler = UserDeleteToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"id": "test_user_id"})

    # Verify
    assert mock_kaltura_client.execute_request.call_count == 2
    assert mock_kaltura_client.execute_request.call_args_list[0][0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args_list[0][0][1] == "get"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args_list[1][0][1] == "delete"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["id"] == "test_user_id"
    assert "message" in response


@pytest.mark.asyncio
async def test_user_list_tool(mock_kaltura_client):
    """Test the user list tool."""
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
    handler = UserListToolHandler(mock_kaltura_client)

    # Execute
    result = await handler.handle({"page_size": 10, "page_index": 1, "filter": {"idOrScreenNameStartsWith": "user"}})

    # Verify
    mock_kaltura_client.execute_request.assert_called_once()
    assert mock_kaltura_client.execute_request.call_args[0][0] == "user"
    assert mock_kaltura_client.execute_request.call_args[0][1] == "list"
    assert len(result) == 1
    assert result[0].type == "text"
    response = json.loads(result[0].text)
    assert response["totalCount"] == 2
    assert len(response["users"]) == 2
    assert response["users"][0]["id"] == "user1"
    assert response["users"][1]["id"] == "user2"
