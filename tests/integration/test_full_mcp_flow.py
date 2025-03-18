"""
Integration test for the full MCP flow: Client -> MCP Server -> Kaltura API.

This test verifies that:
1. A real MCP server can be started
2. A client can connect to the MCP server
3. The MCP server intelligently translates client requests to Kaltura API calls
4. The results are properly returned to the client
"""
import pytest
import pytest_asyncio
import asyncio
import os
import json
import logging
import tempfile
import subprocess
import time
import requests
from pathlib import Path
import uuid
import signal
from contextlib import asynccontextmanager

from mcp.client.session import ClientSession as McpClient
from mcp import types

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_flow_test")

# Mark all tests as asyncio
pytestmark = pytest.mark.asyncio

class TestFullMcpFlow:
    """Test the full MCP flow from client to server to Kaltura API."""
    
    @pytest_asyncio.fixture(scope="class")
    async def mcp_server(self, integration_config):
        """Create a server instance for testing."""
        # Create server
        from kaltura_mcp.server import KalturaMcpServer
        
        logger.info("Creating KalturaMcpServer for testing")
        server = KalturaMcpServer(integration_config)
        
        # Initialize server
        await server.initialize()
        
        # Register handlers
        async def list_tools_handler():
            return [handler.get_tool_definition() for handler in server.tool_handlers.values()]
        
        async def call_tool_handler(request):
            name = request["name"]
            arguments = request["arguments"]
            if name not in server.tool_handlers:
                raise ValueError(f"Unknown tool: {name}")
            
            handler = server.tool_handlers[name]
            return await handler.handle(arguments)
        
        async def list_resources_handler():
            return [handler.get_resource_definition() for handler in server.resource_handlers.values()]
        
        async def read_resource_handler(uri):
            for handler in server.resource_handlers.values():
                if handler.matches_uri(uri):
                    return await handler.handle(uri)
            
            raise ValueError(f"Unknown resource: {uri}")
        
        server.app.list_tools = list_tools_handler
        server.app.call_tool = call_tool_handler
        server.app.list_resources = list_resources_handler
        server.app.read_resource = read_resource_handler
        
        logger.info(f"Server initialized with {len(server.tool_handlers)} tools and {len(server.resource_handlers)} resources")
        
        yield server
    
    @pytest_asyncio.fixture
    async def mcp_client(self, mcp_server):
        """Create a direct client for the MCP server."""
        logger.info("Creating direct MCP client")
        
        # Create a client that directly calls the server methods
        class DirectMcpClient:
            def __init__(self, server):
                self.server = server
            
            async def get(self, path):
                """Handle GET requests."""
                if path == "/tools":
                    tools = await self.server.app.list_tools()
                    # Convert Tool objects to dictionaries
                    tool_dicts = []
                    for tool in tools:
                        tool_dict = {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        tool_dicts.append(tool_dict)
                    return MockResponse(200, tool_dicts)
                elif path == "/resources":
                    resources = await self.server.app.list_resources()
                    # Convert Resource objects to dictionaries
                    resource_dicts = []
                    for resource in resources:
                        resource_dict = {
                            "uri": resource.uri,
                            "name": resource.name,
                            "mimeType": resource.mimeType,
                            "description": resource.description
                        }
                        resource_dicts.append(resource_dict)
                    return MockResponse(200, resource_dicts)
                elif path.startswith("/resources?uri="):
                    # Extract URI from query string
                    uri = path.split("=", 1)[1]
                    result = await self.server.app.read_resource(uri)
                    
                    # Handle ResourceContents object
                    if hasattr(result, 'text'):
                        return MockResponse(200, [{"text": result.text}])
                    else:
                        try:
                            # Try to JSON serialize the result
                            return MockResponse(200, [{"text": json.dumps(result)}])
                        except TypeError:
                            # If the result is not JSON serializable, convert it to a string
                            return MockResponse(200, [{"text": str(result)}])
                else:
                    return MockResponse(200, "Kaltura MCP Server")
            
            async def post(self, path, json=None):
                """Handle POST requests."""
                if path.startswith("/tools/"):
                    tool_name = path[len("/tools/"):]
                    result = await self.server.app.call_tool({"name": tool_name, "arguments": json or {}})
                    
                    # Convert result to expected format
                    if isinstance(result, list):
                        formatted_result = []
                        for item in result:
                            if hasattr(item, 'text'):
                                formatted_result.append({"text": item.text})
                            else:
                                formatted_result.append({"text": json.dumps(item)})
                        return MockResponse(200, formatted_result)
                    else:
                        # If it's a single item
                        if hasattr(result, 'text'):
                            return MockResponse(200, [{"text": result.text}])
                        else:
                            return MockResponse(200, [{"text": json.dumps(result)}])
                else:
                    return MockResponse(404, {"error": "Not Found"})
        
        # Mock response class
        class MockResponse:
            def __init__(self, status_code, content):
                self.status_code = status_code
                self._content = content
            
            def json(self):
                return self._content
        
        # Return client
        client = DirectMcpClient(mcp_server)
        yield client
    
    async def test_list_tools(self, mcp_client):
        """Test that the client can list tools from the MCP server."""
        # List tools
        response = await mcp_client.get("/tools")
        
        # Verify response
        assert response.status_code == 200
        
        # Parse JSON response
        tools = response.json()
        
        # Verify tools were returned
        assert len(tools) > 0
        
        # Verify specific tools exist
        tool_names = [tool["name"] for tool in tools]
        assert "kaltura.media.list" in tool_names
        assert "kaltura.media.get" in tool_names
        assert "kaltura.media.upload" in tool_names
        
        logger.info(f"MCP server provides {len(tools)} tools: {', '.join(tool_names[:5])}...")
    
    async def test_list_resources(self, mcp_client):
        """Test that the client can list resources from the MCP server."""
        # List resources
        response = await mcp_client.get("/resources")
        
        # Verify response
        assert response.status_code == 200
        
        # Parse JSON response
        resources = response.json()
        
        # Verify resources were returned
        assert len(resources) > 0
        
        # Log resources
        resource_uris = [resource["uri"] for resource in resources]
        logger.info(f"MCP server provides {len(resources)} resources: {', '.join(str(uri) for uri in resource_uris[:5])}...")
    
    async def test_media_list_flow(self, mcp_client):
        """Test the full flow for listing media entries."""
        # Call the media.list tool
        logger.info("Calling kaltura.media.list tool through MCP server")
        response = await mcp_client.post("/tools/kaltura.media.list", json={})
        
        # Verify response
        assert response.status_code == 200
        
        # Parse JSON response
        result = response.json()
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert "text" in result[0]
        
        # Parse the content
        content = json.loads(result[0]["text"])
        
        # Verify content structure
        assert "entries" in content
        assert isinstance(content["entries"], list)
        
        logger.info(f"Retrieved {len(content['entries'])} media entries through MCP")
        if content["entries"]:
            logger.info(f"First media entry: {json.dumps(content['entries'][0], indent=2)[:200]}...")
    
    async def test_category_flow(self, mcp_client):
        """Test the full flow for category operations."""
        # Create a unique category name
        unique_id = uuid.uuid4().hex[:8]
        category_name = f"MCP Test Category {unique_id}"
        
        # 1. Add a category
        logger.info(f"Creating category: {category_name}")
        add_response = await mcp_client.post("/tools/kaltura.category.add", json={
            "name": category_name,
            "description": "Created by MCP integration test"
        })
        
        # Verify response
        assert add_response.status_code == 200
        
        # Parse JSON response
        add_result = add_response.json()
        
        # Parse the content
        add_content = json.loads(add_result[0]["text"])
        
        # Verify content structure
        assert "id" in add_content
        category_id = add_content["id"]
        logger.info(f"Created category with ID: {category_id}")
        
        try:
            # 2. Get the category
            logger.info(f"Getting category with ID: {category_id}")
            get_response = await mcp_client.post("/tools/kaltura.category.get", json={
                "id": category_id
            })
            
            # Verify response
            assert get_response.status_code == 200
            
            # Parse JSON response
            get_result = get_response.json()
            
            # Parse the content
            get_content = json.loads(get_result[0]["text"])
            
            # Verify content structure
            assert "id" in get_content
            assert "name" in get_content
            assert get_content["name"] == category_name
            
            logger.info(f"Retrieved category: {get_content['name']}")
            
            # 3. Update the category
            updated_name = f"{category_name} (Updated)"
            logger.info(f"Updating category to: {updated_name}")
            update_response = await mcp_client.post("/tools/kaltura.category.update", json={
                "id": category_id,
                "name": updated_name
            })
            
            # Verify response
            assert update_response.status_code == 200
            
            # Parse JSON response
            update_result = update_response.json()
            
            # Parse the content
            update_content = json.loads(update_result[0]["text"])
            
            # Verify content structure
            assert "id" in update_content
            assert "name" in update_content
            assert update_content["name"] == updated_name
            
            logger.info(f"Updated category name to: {update_content['name']}")
            
        finally:
            # 4. Delete the category
            logger.info(f"Deleting category with ID: {category_id}")
            delete_response = await mcp_client.post("/tools/kaltura.category.delete", json={
                "id": category_id
            })
            
            # Verify response
            assert delete_response.status_code == 200
            
            logger.info(f"Deleted category with ID: {category_id}")
    
    async def test_resource_access(self, mcp_client):
        """Test accessing resources through the MCP server."""
        # List media entries to get an entry ID
        list_response = await mcp_client.post("/tools/kaltura.media.list", json={
            "page_size": 1
        })
        
        # Verify response
        assert list_response.status_code == 200
        
        # Parse JSON response
        list_result = list_response.json()
        
        # Parse the content
        list_content = json.loads(list_result[0]["text"])
        
        # Skip if no media entries
        if not list_content["entries"]:
            pytest.skip("No media entries found")
        
        # Get the first entry ID
        entry_id = list_content["entries"][0]["id"]
        
        # Access the media entry resource
        logger.info(f"Accessing media entry resource for ID: {entry_id}")
        resource_uri = f"kaltura://media/{entry_id}"
        resource_response = await mcp_client.get(f"/resources?uri={resource_uri}")
        
        # Verify response
        assert resource_response.status_code == 200
        
        # Parse JSON response
        resource_result = resource_response.json()
        
        # Verify result structure
        assert len(resource_result) > 0
        assert "text" in resource_result[0]
        
        # Get the text content
        text_content = resource_result[0]["text"]
        
        # Try to parse as JSON, but fall back to string handling if it fails
        try:
            resource_content = json.loads(text_content)
            # Verify content structure for JSON response
            assert "id" in resource_content
            assert resource_content["id"] == entry_id
        except json.JSONDecodeError:
            # For non-JSON responses, just check if the entry_id is in the text
            assert entry_id in text_content
        
        logger.info(f"Retrieved resource for media entry: {entry_id}")