#!/usr/bin/env python
"""
Test client for the enhanced MCP server.

This script connects to a running MCP server and makes various requests
to demonstrate the full flow from client to MCP server to Kaltura API.
"""
import os
import sys
import json
import logging
import asyncio
import uuid
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import MCP client
from mcp.client.session import ClientSession as McpClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("test_mcp_client")

async def run_client_tests(server_url="http://127.0.0.1:8765"):
    """Run tests against the MCP server."""
    logger.info(f"Connecting to MCP server at {server_url}")
    
    try:
        # Create and initialize client
        client = McpClient(server_url)
        await client.initialize()
        logger.info("Client initialized")
        
        # Test 1: List tools
        logger.info("\n=== Test 1: List Tools ===")
        tools = await client.list_tools()
        logger.info(f"Server provides {len(tools)} tools")
        for i, tool in enumerate(tools[:5]):  # Show first 5 tools
            logger.info(f"Tool {i+1}: {tool.name} - {tool.description}")
        
        # Test 2: List resources
        logger.info("\n=== Test 2: List Resources ===")
        resources = await client.list_resources()
        logger.info(f"Server provides {len(resources)} resources")
        for i, resource in enumerate(resources[:5]):  # Show first 5 resources
            logger.info(f"Resource {i+1}: {resource.uri} - {resource.name}")
        
        # Test 3: List media entries
        logger.info("\n=== Test 3: List Media Entries ===")
        result = await client.call_tool("kaltura.media.list", {
            "page_size": 5  # Limit to 5 entries
        })
        content = json.loads(result[0].text)
        logger.info(f"Retrieved {len(content['items'])} media entries")
        for i, item in enumerate(content['items']):
            logger.info(f"Media {i+1}: {item['id']} - {item['name']}")
        
        # Test 4: Create, update, and delete a category
        logger.info("\n=== Test 4: Category CRUD Operations ===")
        unique_id = uuid.uuid4().hex[:8]
        category_name = f"MCP Test Category {unique_id}"
        
        # Create category
        logger.info(f"Creating category: {category_name}")
        add_result = await client.call_tool("kaltura.category.add", {
            "name": category_name,
            "description": "Created by MCP test client"
        })
        add_content = json.loads(add_result[0].text)
        category_id = add_content["id"]
        logger.info(f"Created category with ID: {category_id}")
        
        # Get category
        logger.info(f"Getting category with ID: {category_id}")
        get_result = await client.call_tool("kaltura.category.get", {
            "id": category_id
        })
        get_content = json.loads(get_result[0].text)
        logger.info(f"Retrieved category: {get_content['name']}")
        
        # Update category
        updated_name = f"{category_name} (Updated)"
        logger.info(f"Updating category to: {updated_name}")
        update_result = await client.call_tool("kaltura.category.update", {
            "id": category_id,
            "name": updated_name
        })
        update_content = json.loads(update_result[0].text)
        logger.info(f"Updated category name to: {update_content['name']}")
        
        # Delete category
        logger.info(f"Deleting category with ID: {category_id}")
        delete_result = await client.call_tool("kaltura.category.delete", {
            "id": category_id
        })
        logger.info(f"Deleted category with ID: {category_id}")
        
        # Test 5: Access a resource
        if content['items']:
            logger.info("\n=== Test 5: Access Resource ===")
            entry_id = content['items'][0]['id']
            resource_uri = f"kaltura://media/{entry_id}"
            logger.info(f"Accessing resource: {resource_uri}")
            resource_result = await client.read_resource(resource_uri)
            resource_content = json.loads(resource_result[0].text)
            logger.info(f"Retrieved resource for media entry: {entry_id}")
            logger.info(f"Media name: {resource_content['name']}")
        
        logger.info("\nAll tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error during client tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close client
        if 'client' in locals():
            await client.close()
    
    return 0

if __name__ == "__main__":
    # Get server URL from command line or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
    
    try:
        exit_code = asyncio.run(run_client_tests(server_url))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Client stopped by user")