#!/usr/bin/env python3
"""
Direct STDIO Client for Kaltura MCP Server

This script demonstrates how to communicate with the Kaltura MCP server
using direct STDIO communication with the JSON-RPC protocol.

Prerequisites:
- Python 3.10 or higher
- Kaltura MCP server installed
"""
import asyncio
import json
import subprocess
import sys

async def read_line(stream):
    """Read a line from the stream."""
    line = await stream.readline()
    return line.decode('utf-8').strip()

async def write_line(stream, data):
    """Write a line to the stream."""
    line = json.dumps(data) + '\n'
    stream.write(line.encode('utf-8'))
    await stream.drain()

async def main():
    """Run the direct STDIO client."""
    print("Starting Kaltura MCP Server...")
    
    # Start the Kaltura MCP server as a subprocess
    process = await asyncio.create_subprocess_exec(
        "kaltura-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Wait for the server to start
        await asyncio.sleep(2)
        
        print("Kaltura MCP Server started")
        
        # Initialize the server
        print("\nInitializing server...")
        await write_line(process.stdin, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "capabilities": {}
            }
        })
        
        # Read the response
        response = await read_line(process.stdout)
        print(f"Initialize response: {response}")
        
        # List tools
        print("\nListing tools...")
        await write_line(process.stdin, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "listTools",
            "params": {}
        })
        
        # Read the response
        response = await read_line(process.stdout)
        tools_response = json.loads(response)
        
        if "result" in tools_response:
            print("\n=== Available Tools ===")
            for tool in tools_response["result"]["tools"]:
                print(f"- {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print(f"Error: {tools_response.get('error', 'Unknown error')}")
        
        # List resources
        print("\nListing resources...")
        await write_line(process.stdin, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "listResources",
            "params": {}
        })
        
        # Read the response
        response = await read_line(process.stdout)
        resources_response = json.loads(response)
        
        if "result" in resources_response:
            print("\n=== Available Resources ===")
            for resource in resources_response["result"]["resources"]:
                print(f"- {resource['uri']}: {resource.get('description', 'No description')}")
        else:
            print(f"Error: {resources_response.get('error', 'Unknown error')}")
        
        # Call a tool
        print("\nCalling kaltura.media.list tool...")
        await write_line(process.stdin, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "callTool",
            "params": {
                "name": "kaltura.media.list",
                "arguments": {
                    "page_size": 5,
                    "filter": {}
                }
            }
        })
        
        # Read the response
        response = await read_line(process.stdout)
        call_response = json.loads(response)
        
        if "result" in call_response:
            print("\n=== Media List Result ===")
            print(json.dumps(call_response["result"], indent=2))
        else:
            print(f"Error: {call_response.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Terminate the process
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(main())