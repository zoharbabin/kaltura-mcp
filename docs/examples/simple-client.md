# Simple Client Example

This example demonstrates how to create a simple client that connects to the Kaltura-MCP Server and performs basic operations.

## Overview

The simple client example demonstrates:

1. Connecting to the Kaltura-MCP Server
2. Listing available tools and resources
3. Calling a tool (kaltura.media.list)
4. Reading a resource (kaltura://media/list)

## Code

```python
#!/usr/bin/env python3
"""
Simple example client for the Kaltura-MCP Server.
"""
import asyncio
import json
import sys
from typing import Dict, Any

from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client

async def main():
    """Run the example client."""
    print("Connecting to Kaltura-MCP Server...")
    
    async with stdio_client() as streams:
        client = Client()
        await client.connect(streams[0], streams[1])
        
        print("Connected to Kaltura-MCP Server")
        
        # List available tools
        print("\nListing available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # List available resources
        print("\nListing available resources:")
        resources = await client.list_resources()
        for resource in resources:
            print(f"- {resource.uri}: {resource.description}")
        
        # Call media.list tool
        print("\nCalling kaltura.media.list tool:")
        try:
            result = await client.call_tool("kaltura.media.list", {
                "page_size": 5,
                "filter": {
                    "nameLike": "test"
                }
            })
            print(json.dumps(json.loads(result[0].text), indent=2))
        except Exception as e:
            print(f"Error calling tool: {e}")
        
        # Read media list resource
        print("\nReading kaltura://media/list resource:")
        try:
            result = await client.read_resource("kaltura://media/list?page_size=5&name_like=test")
            print(json.dumps(json.loads(result), indent=2))
        except Exception as e:
            print(f"Error reading resource: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Explanation

### Importing Dependencies

```python
import asyncio
import json
import sys
from typing import Dict, Any

from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client
```

The example imports:
- `asyncio` for asynchronous programming
- `json` for parsing JSON responses
- `sys` for system operations
- `typing` for type hints
- `mcp.client.lowlevel.Client` for the MCP client
- `mcp.client.stdio.stdio_client` for the stdio transport

### Connecting to the Server

```python
async with stdio_client() as streams:
    client = Client()
    await client.connect(streams[0], streams[1])
    
    print("Connected to Kaltura-MCP Server")
```

This code:
1. Creates a stdio client that connects to the Kaltura-MCP Server
2. Creates an MCP client
3. Connects the client to the server using the stdio streams

### Listing Available Tools

```python
# List available tools
print("\nListing available tools:")
tools = await client.list_tools()
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

This code:
1. Calls the `list_tools` method on the client
2. Iterates through the returned tools
3. Prints the name and description of each tool

### Listing Available Resources

```python
# List available resources
print("\nListing available resources:")
resources = await client.list_resources()
for resource in resources:
    print(f"- {resource.uri}: {resource.description}")
```

This code:
1. Calls the `list_resources` method on the client
2. Iterates through the returned resources
3. Prints the URI and description of each resource

### Calling a Tool

```python
# Call media.list tool
print("\nCalling kaltura.media.list tool:")
try:
    result = await client.call_tool("kaltura.media.list", {
        "page_size": 5,
        "filter": {
            "nameLike": "test"
        }
    })
    print(json.dumps(json.loads(result[0].text), indent=2))
except Exception as e:
    print(f"Error calling tool: {e}")
```

This code:
1. Calls the `call_tool` method on the client with the tool name "kaltura.media.list" and parameters
2. Parses the JSON response
3. Prints the formatted JSON response
4. Handles any exceptions that may occur

### Reading a Resource

```python
# Read media list resource
print("\nReading kaltura://media/list resource:")
try:
    result = await client.read_resource("kaltura://media/list?page_size=5&name_like=test")
    print(json.dumps(json.loads(result), indent=2))
except Exception as e:
    print(f"Error reading resource: {e}")
```

This code:
1. Calls the `read_resource` method on the client with the resource URI "kaltura://media/list?page_size=5&name_like=test"
2. Parses the JSON response
3. Prints the formatted JSON response
4. Handles any exceptions that may occur

## Running the Example

To run the example:

1. Make sure the Kaltura-MCP Server is running:
   ```bash
   kaltura-mcp
   ```

2. In a separate terminal, run the example:
   ```bash
   cd examples
   python simple_client.py
   ```

## Expected Output

The example should produce output similar to:

```
Connecting to Kaltura-MCP Server...
Connected to Kaltura-MCP Server

Listing available tools:
- kaltura.media.list: List media entries with filtering and pagination
- kaltura.media.get: Get details of a specific media entry
- kaltura.media.upload: Upload a new media entry
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

Listing available resources:
- kaltura://media/{entry_id}: Get details of a specific media entry
- kaltura://media/list: List media entries with filtering and pagination
- kaltura://categories/{category_id}: Get details of a specific category
- kaltura://categories/list: List categories with filtering and pagination
- kaltura://users/{user_id}: Get details of a specific user
- kaltura://users/list: List users with filtering and pagination

Calling kaltura.media.list tool:
{
  "objects": [
    {
      "id": "0_abc123",
      "name": "Test Video 1",
      "description": "This is test video 1",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z"
    },
    {
      "id": "0_def456",
      "name": "Test Video 2",
      "description": "This is test video 2",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z"
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}

Reading kaltura://media/list resource:
{
  "objects": [
    {
      "id": "0_abc123",
      "name": "Test Video 1",
      "description": "This is test video 1",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z"
    },
    {
      "id": "0_def456",
      "name": "Test Video 2",
      "description": "This is test video 2",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z"
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}
```

## Next Steps

After understanding this simple example, you can:

1. Explore the [Media Management](media-management.md) example to learn how to use the media management tools and resources in more detail.
2. Explore the [Category Management](category-management.md) example to learn how to use the category management tools and resources.
3. Explore the [User Management](user-management.md) example to learn how to use the user management tools and resources.
4. Read the [API Reference](../api-reference/index.md) to understand the available tools and resources in more detail.
5. Follow the [Guides](../guides/index.md) to learn best practices for using the server effectively.