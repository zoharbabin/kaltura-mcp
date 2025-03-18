#!/usr/bin/env python3
"""
Programmatic Client for Kaltura MCP Server

This script demonstrates how to use the Kaltura MCP server programmatically
with the MCP client library.

Prerequisites:
- Python 3.10 or higher
- MCP client library installed (`pip install mcp`)
- Kaltura MCP server installed
"""
import asyncio
import json
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from mcp import StdioServerParameters
from mcp import ClientSession

class KalturaMcpClient:
    """Client for interacting with the Kaltura MCP server."""
    
    def __init__(self):
        """Initialize the client."""
        self.server_process = None
        self.session = None
    
    async def start_server(self):
        """Start the Kaltura MCP server."""
        print("Starting Kaltura MCP server...")
        
        # Start the server as a subprocess
        self.server_process = subprocess.Popen(
            ["kaltura-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the server to start
        await asyncio.sleep(2)
        
        print("Kaltura MCP server started")
    
    async def connect(self):
        """Connect to the Kaltura MCP server."""
        print("Connecting to Kaltura MCP server...")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="kaltura-mcp",
            args=[],
            env=None
        )
        
        # Create client session
        self.session = ClientSession()
        
        # Connect to the server
        await self.session.connect_stdio(server_params)
        
        # Initialize the session
        await self.session.initialize()
        
        print("Connected to Kaltura MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        print("Listing tools...")
        
        tools_result = await self.session.list_tools()
        
        tools = []
        for tool in tools_result.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        
        return tools
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources."""
        print("Listing resources...")
        
        resources_result = await self.session.list_resources()
        
        resources = []
        for resource in resources_result.resources:
            resources.append({
                "uri": resource.uri,
                "description": resource.description,
                "mime_type": resource.mime_type
            })
        
        return resources
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with the given name and arguments."""
        print(f"Calling tool: {name}")
        
        result = await self.session.call_tool(name, arguments)
        
        if result.content and result.content[0].text:
            return json.loads(result.content[0].text)
        
        return {}
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource with the given URI."""
        print(f"Reading resource: {uri}")
        
        result = await self.session.read_resource(uri)
        
        if result.contents and result.contents[0].text:
            return json.loads(result.contents[0].text)
        
        return {}
    
    async def close(self):
        """Close the client and stop the server."""
        print("Closing client...")
        
        if self.session:
            await self.session.close()
        
        if self.server_process:
            print("Stopping Kaltura MCP server...")
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
        
        print("Client closed")

async def main():
    """Run the Kaltura MCP client example."""
    client = KalturaMcpClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Connect to the server
        await client.connect()
        
        # List tools
        tools = await client.list_tools()
        print("\n=== Available Tools ===")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
        
        # List resources
        resources = await client.list_resources()
        print("\n=== Available Resources ===")
        for resource in resources:
            print(f"- {resource['uri']}: {resource.get('description', 'No description')}")
        
        # Call the media.list tool
        print("\n=== Media Entries ===")
        try:
            media_list = await client.call_tool("kaltura.media.list", {
                "page_size": 5,
                "filter": {}
            })
            print(json.dumps(media_list, indent=2))
        except Exception as e:
            print(f"Error calling media.list tool: {e}")
        
        # Read the media list resource
        print("\n=== Media List Resource ===")
        try:
            media_resource = await client.read_resource("kaltura://media/list?page_size=5")
            print(json.dumps(media_resource, indent=2))
        except Exception as e:
            print(f"Error reading media list resource: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close the client
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())