"""
Integration tests for user tools and resources.

These tests verify that the user tools and resources work correctly together
with the Kaltura API. They require a valid Kaltura API configuration.
"""
import pytest
import os
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from mcp import types

# Skip these tests if no integration test config is available
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not os.path.exists("tests/integration/config.json"),
        reason="Integration test config not found"
    )
]

class TestUserIntegration:
    """Integration tests for user tools and resources."""
    
    async def test_user_list_tool(self, server):
        """Test the user.list tool."""
        # Call the user.list tool
        result = await server.app.call_tool("kaltura.user.list", {
            "page_size": 10,
            "page": 1
        })
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        # Parse the JSON content
        content = json.loads(result[0].text)
        
        # Verify content structure
        assert "users" in content
        assert "totalCount" in content
        assert isinstance(content["users"], list)
        assert isinstance(content["totalCount"], int)
    
    async def test_user_get_tool(self, server, kaltura_client):
        """Test the user.get tool."""
        # First, list users to get a user ID
        list_result = await server.app.call_tool("kaltura.user.list", {
            "page_size": 1,
            "page": 1
        })
        
        # Parse the JSON content
        list_content = json.loads(list_result[0].text)
        
        # Skip if no users found
        if not list_content["users"]:
            pytest.skip("No users found for testing")
        
        # Get the first user ID
        user_id = list_content["users"][0]["id"]
        
        # Call the user.get tool
        result = await server.app.call_tool("kaltura.user.get", {
            "id": user_id
        })
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        # Parse the JSON content
        content = json.loads(result[0].text)
        
        # Verify content structure
        assert "id" in content
        assert content["id"] == user_id
        assert "screenName" in content
        assert "email" in content
        assert "createdAt" in content
    
    async def test_user_add_update_delete_flow(self, server):
        """Test the complete user flow: add, update, delete."""
        # Generate a unique user ID and email
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        user_id = f"test_user_{unique_id}"
        email = f"test_{unique_id}@example.com"
        
        # 1. Add the user
        add_result = await server.app.call_tool("kaltura.user.add", {
            "id": user_id,
            "screenName": f"Test User {unique_id}",
            "email": email,
            "first_name": "Test",
            "last_name": "User"
        })
        
        # Verify add result
        assert isinstance(add_result, list)
        assert len(add_result) > 0
        assert isinstance(add_result[0], types.TextContent)
        
        # Parse the JSON content
        add_content = json.loads(add_result[0].text)
        
        # Verify content structure
        assert "id" in add_content
        assert add_content["id"] == user_id
        assert "screenName" in add_content
        # Accept any screenName that contains "Test User"
        assert "Test User" in add_content["screenName"]
        assert "email" in add_content
        assert add_content["email"] == email
        
        # 2. Update the user
        update_result = await server.app.call_tool("kaltura.user.update", {
            "id": user_id,
            "screenName": f"Updated Test User {unique_id}",
            "first_name": "Updated",
            "last_name": "User"
        })
        
        # Verify update result
        assert isinstance(update_result, list)
        assert len(update_result) > 0
        assert isinstance(update_result[0], types.TextContent)
        
        # Parse the JSON content
        update_content = json.loads(update_result[0].text)
        
        # Verify content structure
        assert "id" in update_content
        assert update_content["id"] == user_id
        # Check for either screenName or screen_name
        assert "screenName" in update_content or "screen_name" in update_content
        if "screenName" in update_content:
            assert "Updated Test User" in update_content["screenName"]
        else:
            assert "Updated Test User" in update_content["screen_name"]
        assert "first_name" in update_content
        assert update_content["first_name"] == "Updated"
        
        # 3. Delete the user
        delete_result = await server.app.call_tool("kaltura.user.delete", {
            "id": user_id
        })
        
        # Verify delete result
        assert isinstance(delete_result, list)
        assert len(delete_result) > 0
        assert isinstance(delete_result[0], types.TextContent)
        
        # Parse the JSON content
        delete_content = json.loads(delete_result[0].text)
        
        # Verify content structure
        assert "success" in delete_content
        assert delete_content["success"] is True
        
        # 4. Verify the user is deleted by trying to get it
        get_result = await server.app.call_tool("kaltura.user.get", {
            "id": user_id
        })
        
        # Check that we got an error response
        assert isinstance(get_result, list)
        assert len(get_result) > 0
        assert isinstance(get_result[0], types.TextContent)
        
        # Parse the JSON content
        get_content = json.loads(get_result[0].text)
        assert "error" in get_content
        assert "Invalid user id" in get_content["error"]
    
    async def test_user_resource_access(self, server, kaltura_client):
        """Test accessing user resources."""
        # First, list users to get a user ID
        list_result = await server.app.call_tool("kaltura.user.list", {
            "page_size": 1,
            "page": 1
        })
        
        # Parse the JSON content
        list_content = json.loads(list_result[0].text)
        
        # Skip if no users found
        if not list_content["users"]:
            pytest.skip("No users found for testing")
        
        # Get the first user ID
        user_id = list_content["users"][0]["id"]
        
        # Access the user resource
        user_resource = await server.app.read_resource(f"kaltura://user/{user_id}")
        
        # Verify resource structure
        assert isinstance(user_resource, list)
        assert len(user_resource) > 0
        assert isinstance(user_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        content = json.loads(user_resource[0].text)
        assert len(user_resource) > 0
        assert isinstance(user_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        content = json.loads(user_resource[0].text)
        assert len(user_resource) > 0
        assert isinstance(user_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        content = json.loads(user_resource[0].text)
        
        # Verify content structure
        assert "id" in content
        assert content["id"] == user_id
        assert "screenName" in content
        assert "email" in content
        assert "createdAt" in content
        
        # Access the user list resource
        list_resource = await server.app.read_resource("kaltura://user/list")
        
        # Verify resource structure
        assert isinstance(list_resource, list)
        assert len(list_resource) > 0
        assert isinstance(list_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        list_content = json.loads(list_resource[0].text)
        
        # Verify content structure
        assert "users" in list_content
        assert "totalCount" in list_content
        assert isinstance(list_content["users"], list)
        assert isinstance(list_content["totalCount"], int)