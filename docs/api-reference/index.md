# API Reference

This section provides detailed reference documentation for the Kaltura-MCP Server API.

## Table of Contents

- [Server API](server-api.md): Documentation for the main server API
- [Tool Handlers](tool-handlers.md): Documentation for all available tool handlers
- [Resource Handlers](resource-handlers.md): Documentation for all available resource handlers
- [Context Management](context-management.md): Documentation for context management strategies
- [Kaltura Client](kaltura-client.md): Documentation for the Kaltura client wrapper

## Overview

The Kaltura-MCP Server provides a Model Context Protocol (MCP) interface to the Kaltura API. It exposes a set of tools and resources that can be used by MCP clients to interact with the Kaltura API.

### Tools

Tools are functions that can be called by MCP clients to perform operations on the Kaltura API. Each tool has a name, a description, and a set of parameters. Tools are grouped by the Kaltura service they interact with:

- **Media Tools**: Tools for managing media entries
- **Category Tools**: Tools for managing categories
- **User Tools**: Tools for managing users

### Resources

Resources are data sources that can be accessed by MCP clients. Each resource has a URI, a description, and a MIME type. Resources are also grouped by the Kaltura entity they represent:

- **Media Resources**: Resources for accessing media entries
- **Category Resources**: Resources for accessing categories
- **User Resources**: Resources for accessing users

### Context Management

Context management strategies are used to optimize the data returned to LLMs, ensuring that it fits within context windows while maintaining relevance:

- **Pagination Strategy**: Handles large result sets by paginating them into manageable chunks
- **Selective Context Strategy**: Filters data to include only the fields that are relevant to the current context
- **Summarization Strategy**: Summarizes long text fields to provide concise information

## API Structure

The Kaltura-MCP Server API follows a consistent structure:

```
kaltura-mcp-server
├── tools
│   ├── kaltura.media.*
│   ├── kaltura.category.*
│   └── kaltura.user.*
└── resources
    ├── kaltura://media/*
    ├── kaltura://categories/*
    └── kaltura://users/*
```

## Using the API

To use the API, you need to:

1. Connect to the Kaltura-MCP Server using an MCP client
2. List available tools and resources
3. Call tools or read resources as needed

For example, using the Python MCP client:

```python
from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client() as streams:
        client = Client()
        await client.connect(streams[0], streams[1])
        
        # List available tools
        tools = await client.list_tools()
        
        # Call a tool
        result = await client.call_tool("kaltura.media.list", {
            "page_size": 10
        })
        
        # Read a resource
        data = await client.read_resource("kaltura://media/list?page_size=10")
```

## Next Steps

Explore the detailed documentation for each component:

- [Server API](server-api.md)
- [Tool Handlers](tool-handlers.md)
- [Resource Handlers](resource-handlers.md)
- [Context Management](context-management.md)
- [Kaltura Client](kaltura-client.md)