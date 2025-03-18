"""
Integration tests for the Kaltura MCP Server category tools.
"""
import json
import pytest
import uuid
from typing import Dict, Any

import mcp.types as types

@pytest.mark.anyio
class TestCategoryIntegration:
    """Integration tests for category tools."""
    
    async def test_category_list_tool(self, server):
        """Test the category.list tool."""
        # Call the category.list tool
        result = await server.app.call_tool("kaltura.category.list", {
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
        assert "totalCount" in content
        assert "categories" in content
        assert "pageSize" in content
        assert "pageIndex" in content

    async def test_category_get_tool(self, server, kaltura_client):
        """Test the category.get tool."""
        # First, list categories to get a category ID
        list_result = await server.app.call_tool("kaltura.category.list", {
            "page_size": 1,
            "page": 1
        })
        
        # Parse the JSON content
        list_content = json.loads(list_result[0].text)
        
        # Skip if no categories found
        if not list_content["categories"]:
            pytest.skip("No categories found for testing")
        
        # Get the first category ID
        category_id = list_content["categories"][0]["id"]
        
        # Call the category.get tool
        result = await server.app.call_tool("kaltura.category.get", {
            "id": category_id
        })
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], types.TextContent)
        
        # Parse the JSON content
        content = json.loads(result[0].text)
        
        # Verify content structure
        assert "id" in content
        assert content["id"] == category_id
        assert "name" in content
        assert "description" in content
        assert "createdAt" in content

    async def test_category_add_update_delete_flow(self, server):
        """Test the complete category flow: add, update, delete."""
        # Generate a unique name for the test category
        unique_id = uuid.uuid4().hex[:8]
        category_name = f"Test Category {unique_id}"
        
        # 1. Add a new category
        add_result = await server.app.call_tool("kaltura.category.add", {
            "name": category_name,
            "description": "Created by integration test",
            "tags": "test,integration"
        })
        
        # Verify add result
        assert isinstance(add_result, list)
        assert len(add_result) > 0
        assert isinstance(add_result[0], types.TextContent)
        
        # Parse the JSON content
        add_content = json.loads(add_result[0].text)
        
        # Verify content structure
        assert "id" in add_content
        category_id = add_content["id"]
        assert "name" in add_content
        assert add_content["name"] == category_name
        
        try:
            # 2. Update the category
            update_result = await server.app.call_tool("kaltura.category.update", {
                "id": category_id,
                "name": f"Updated {category_name}",
                "description": "Updated by integration test"
            })
            
            # Verify update result
            assert isinstance(update_result, list)
            assert len(update_result) > 0
            assert isinstance(update_result[0], types.TextContent)
            
            # Parse the JSON content
            update_content = json.loads(update_result[0].text)
            
            # Verify content structure
            assert "id" in update_content
            assert update_content["id"] == category_id
            assert "name" in update_content
            assert update_content["name"] == f"Updated {category_name}"
            assert "description" in update_content
            assert update_content["description"] == "Updated by integration test"
            
            # 3. Delete the category
            delete_result = await server.app.call_tool("kaltura.category.delete", {
                "id": category_id
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
            
            # 4. Verify the category is deleted by trying to get it
            # Use a direct call to the handler to ensure the exception is propagated
            from kaltura_mcp.tools.category import CategoryGetToolHandler
            handler = CategoryGetToolHandler(server.kaltura_client)
            with pytest.raises(ValueError):  # Using a more specific exception type
                await handler.handle({"id": category_id})
        
        finally:
            # Clean up in case the test fails
            try:
                await server.app.call_tool("kaltura.category.delete", {
                    "id": category_id
                })
            except:
                pass

    async def test_category_resource_access(self, server, kaltura_client):
        """Test accessing category resources."""
        # First, list categories to get a category ID
        list_result = await server.app.call_tool("kaltura.category.list", {
            "page_size": 1,
            "page": 1
        })
        
        # Parse the JSON content
        list_content = json.loads(list_result[0].text)
        
        # Skip if no categories found
        if not list_content["categories"]:
            pytest.skip("No categories found for testing")
        
        # Get the first category ID
        category_id = list_content["categories"][0]["id"]
        
        # Access the category resource
        category_resource = await server.app.read_resource(f"kaltura://category/{category_id}")
        
        # Verify resource structure
        assert isinstance(category_resource, list)
        assert len(category_resource) > 0
        assert isinstance(category_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        content = json.loads(category_resource[0].text)
        
        # Verify content structure
        assert "id" in content
        assert content["id"] == category_id
        assert "name" in content
        assert "description" in content
        assert "createdAt" in content
        
        # Access the category list resource
        list_resource = await server.app.read_resource("kaltura://category/list")
        
        # Verify resource structure
        assert isinstance(list_resource, list)
        assert len(list_resource) > 0
        assert isinstance(list_resource[0], types.ResourceContents)
        
        # Parse the JSON content
        list_content = json.loads(list_resource[0].text)
        
        # Verify content structure
        assert "categories" in list_content
        assert "totalCount" in list_content
        assert isinstance(list_content["categories"], list)
        assert isinstance(list_content["totalCount"], int)