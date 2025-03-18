#!/usr/bin/env python3
"""
Demo client for the Kaltura MCP Server.

This script demonstrates how to connect to the Kaltura MCP Server and use its tools and resources.
"""
import asyncio
import json
from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client

async def main():
    """Run the demo client."""
    print("Connecting to Kaltura MCP Server...")
    
    # Connect to the server
    async with stdio_client() as streams:
        client = Client()
        await client.connect(streams[0], streams[1])
        
        print("Connected to Kaltura MCP Server")
        
        # List available tools
        print("\n=== Available Tools ===")
        tools = await client.list_tools()
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # List available resources
        print("\n=== Available Resources ===")
        resources = await client.list_resources()
        for resource in resources:
            print(f"- {resource.uri}: {resource.description}")
        
        # Call media.list tool with a small page size
        print("\n=== Calling kaltura.media.list tool ===")
        try:
            result = await client.call_tool("kaltura.media.list", {
                "page_size": 3,
                "filter": {}
            })
            print(json.dumps(json.loads(result[0].text), indent=2))
        except Exception as e:
            print(f"Error calling tool: {e}")
        
        # Read media list resource
        print("\n=== Reading kaltura://media/list resource ===")
        try:
            result = await client.read_resource("kaltura://media/list?page_size=3")
            print(json.dumps(json.loads(result), indent=2))
        except Exception as e:
            print(f"Error reading resource: {e}")

if __name__ == "__main__":
    asyncio.run(main())