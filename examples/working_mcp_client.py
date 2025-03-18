#!/usr/bin/env python3
"""
Working Kaltura MCP Client Example

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
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters, stdio_client


async def main():
    """Run the Kaltura MCP client example."""
    print("Connecting to Kaltura MCP Server...")

    # Set up server parameters
    server_params = StdioServerParameters(
        command="kaltura-mcp",  # Command to start the server
        args=[],  # Command line arguments
        env=None,  # Environment variables
    )

    try:
        # Create a client session
        async with stdio_client(server_params) as streams:
            session = ClientSession()
            await session.connect(streams[0], streams[1])

            print("Connected to Kaltura MCP Server")

            # Initialize the session
            await session.initialize()

            # List available tools
            print("\n=== Available Tools ===")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            # List available resources
            print("\n=== Available Resources ===")
            resources_result = await session.list_resources()
            for resource in resources_result.resources:
                print(f"- {resource.uri}: {resource.description}")

            # Call the media.list tool
            print("\n=== Media Entries ===")
            try:
                result = await session.call_tool("kaltura.media.list", {"page_size": 5, "filter": {}})
                print(json.dumps(json.loads(result.content[0].text), indent=2))
            except Exception as e:
                print(f"Error calling media.list tool: {e}")

            # Read the media list resource
            print("\n=== Media List Resource ===")
            try:
                result = await session.read_resource("kaltura://media/list?page_size=5")
                for content in result.contents:
                    print(json.dumps(json.loads(content.text), indent=2))
            except Exception as e:
                print(f"Error reading media list resource: {e}")

    except Exception as e:
        print(f"Error connecting to Kaltura MCP Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
