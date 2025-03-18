# Using Kaltura MCP with the MCP CLI Tool

This guide explains how to use the Kaltura MCP server with the MCP CLI tool for development and testing.

## Prerequisites

- Python 3.10 or higher
- MCP CLI tool installed (`pip install mcp[cli]`)
- Kaltura MCP server installed and configured

## Starting the Server

First, start the Kaltura MCP server:

```bash
# Navigate to the Kaltura MCP directory
cd /path/to/kaltura-mcp-public

# Activate your virtual environment (if using one)
source venv/bin/activate

# Start the server
kaltura-mcp
```

## Using the MCP CLI Tool

The MCP CLI tool provides several commands for interacting with MCP servers. Here are some examples:

### Inspecting the Server

Use the `mcp dev` command to inspect the server:

```bash
# Start the MCP Inspector with the Kaltura MCP server
mcp dev kaltura-mcp
```

This will open the MCP Inspector, which allows you to:
- Browse available tools and resources
- Execute tools with different parameters
- View resource contents
- Test the server's functionality

### Listing Tools

To list the available tools:

```bash
mcp tools list
```

Example output:
```
Available tools:
- kaltura.media.list: List media entries with filtering and pagination
- kaltura.media.get: Get details of a specific media entry
- kaltura.media.upload: Upload a file to Kaltura
- kaltura.media.update: Update a media entry
- kaltura.media.delete: Delete a media entry
- kaltura.category.list: List categories with filtering and pagination
- kaltura.category.get: Get details of a specific category
- kaltura.category.add: Add a new category
- kaltura.category.update: Update a category
- kaltura.category.delete: Delete a category
- kaltura.user.list: List users with filtering and pagination
- kaltura.user.get: Get details of a specific user
- kaltura.user.add: Add a new user
- kaltura.user.update: Update a user
- kaltura.user.delete: Delete a user
```

### Calling a Tool

To call a specific tool:

```bash
# List media entries
mcp tools call kaltura.media.list '{"page_size": 5, "filter": {"nameLike": "test"}}'

# Get a specific media entry
mcp tools call kaltura.media.get '{"entryId": "0_abc123"}'

# Upload a media file
mcp tools call kaltura.media.upload '{"file_path": "/path/to/video.mp4", "name": "My Video", "description": "A test video", "tags": "test,video"}'
```

### Listing Resources

To list the available resources:

```bash
mcp resources list
```

Example output:
```
Available resources:
- kaltura://media/{entryId}: Access a specific media entry
- kaltura://media/list: List media entries
- kaltura://category/{categoryId}: Access a specific category
- kaltura://category/list: List categories
- kaltura://user/{userId}: Access a specific user
- kaltura://user/list: List users
```

### Reading a Resource

To read a specific resource:

```bash
# Read a media entry
mcp resources read "kaltura://media/0_abc123"

# List media entries with filtering
mcp resources read "kaltura://media/list?page_size=5&name_like=test"
```

## Example Script

Here's a Python script that uses the MCP client library to interact with the Kaltura MCP server:

```python
#!/usr/bin/env python3
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters

async def main():
    # Set up server parameters
    server_params = StdioServerParameters(
        command="kaltura-mcp",
        args=[],
        env=None,
    )
    
    # Create a client session
    async with ClientSession.create_stdio(server_params) as session:
        # Initialize the session
        await session.initialize()
        
        # List available tools
        print("=== Available Tools ===")
        tools = await session.list_tools()
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # List available resources
        print("\n=== Available Resources ===")
        resources = await session.list_resources()
        for resource in resources:
            print(f"- {resource.uri}: {resource.description}")
        
        # Call the media.list tool
        print("\n=== Media Entries ===")
        result = await session.call_tool("kaltura.media.list", {
            "page_size": 5,
            "filter": {}
        })
        print(json.dumps(json.loads(result[0].text), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `kaltura_mcp_client.py` and run it:

```bash
python kaltura_mcp_client.py
```

## Conclusion

The MCP CLI tool and client library provide powerful ways to interact with the Kaltura MCP server for development, testing, and integration purposes. You can explore the available tools and resources, call tools with different parameters, and read resources with various filters.