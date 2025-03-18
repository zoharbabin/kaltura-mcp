#!/usr/bin/env python3
"""
Simple demo client for the Kaltura MCP Server.

This script demonstrates how to connect to the Kaltura MCP Server using the MCP client library.
"""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters

async def main():
    """Run the demo client."""
    print("Connecting to Kaltura MCP Server...")
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command="kaltura-mcp",  # Command to start the server
        args=[],                # Command line arguments
        env=None,               # Environment variables
    )
    
    try:
        # Create a client using stdio transport
        async with await asyncio.create_subprocess_exec(
            server_params.command,
            *server_params.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=server_params.env
        ) as process:
            # Create a client session
            session = ClientSession(process.stdout, process.stdin)
            
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
                result = await session.call_tool("kaltura.media.list", {
                    "page_size": 5,
                    "filter": {}
                })
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
            
            # Close the session
            await session.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())