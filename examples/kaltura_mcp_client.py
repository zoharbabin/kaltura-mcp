#!/usr/bin/env python3
"""
Kaltura MCP Client Example

This script demonstrates how to use the MCP client library to interact with the Kaltura MCP server.
It shows how to:
- Connect to the server
- List available tools and resources
- Call tools with parameters
- Read resources with filters

Prerequisites:
- Python 3.10 or higher
- MCP client library installed (`pip install mcp`)
- Kaltura MCP server installed and running
- Configuration file set up (config.yaml)
"""
import asyncio
import json
import os
import sys

from mcp import StdioServerParameters
from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client


async def main():
    """Run the Kaltura MCP client example."""
    print("Connecting to Kaltura MCP Server...")

    # Get config path from environment or use default
    config_path = os.environ.get("KALTURA_MCP_CONFIG", "config.yaml")

    # Set up server parameters
    server_params = StdioServerParameters(
        command="kaltura-mcp",  # Command to start the server
        args=[],  # Command line arguments
        env={"KALTURA_MCP_CONFIG": config_path},  # Pass config path to server
    )

    try:
        # Create a client session using stdio transport
        async with stdio_client(server_params) as streams:
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

            # Call the media.list tool
            print("\n=== Media Entries ===")
            try:
                result = await client.call_tool("kaltura.media.list", {"page_size": 5, "filter": {}})
                print(json.dumps(json.loads(result[0].text), indent=2))
            except Exception as e:
                print(f"Error calling media.list tool: {e}")

            # Read the media list resource
            print("\n=== Media List Resource ===")
            try:
                result = await client.read_resource("kaltura://media/list?page_size=5")
                print(json.dumps(json.loads(result), indent=2))
            except Exception as e:
                print(f"Error reading media list resource: {e}")

            # Call the category.list tool
            print("\n=== Categories ===")
            try:
                result = await client.call_tool("kaltura.category.list", {"page_size": 5, "filter": {}})
                print(json.dumps(json.loads(result[0].text), indent=2))
            except Exception as e:
                print(f"Error calling category.list tool: {e}")

            # Call the user.list tool
            print("\n=== Users ===")
            try:
                result = await client.call_tool("kaltura.user.list", {"page_size": 5, "filter": {}})
                print(json.dumps(json.loads(result[0].text), indent=2))
            except Exception as e:
                print(f"Error calling user.list tool: {e}")

    except Exception as e:
        print(f"Error connecting to Kaltura MCP Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
