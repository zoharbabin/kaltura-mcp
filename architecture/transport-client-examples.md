# Transport Client Examples

This document provides example implementations for clients that connect to the Kaltura MCP server using different transport mechanisms.

## File: `examples/transport_client_examples.py`

```python
#!/usr/bin/env python3
"""
Examples of using different transport mechanisms with Kaltura MCP.

This script demonstrates how to connect to a Kaltura MCP server using
different transport mechanisms: STDIO, HTTP, and SSE.
"""
import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import requests
import sseclient
from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client


async def stdio_example() -> None:
    """Example of using STDIO transport."""
    print("\n=== STDIO Transport Example ===")
    
    try:
        # Connect to the server using STDIO
        print("Connecting to Kaltura MCP Server using STDIO...")
        
        async with stdio_client() as streams:
            client = Client()
            await client.connect(streams[0], streams[1])
            
            print("Connected to Kaltura MCP Server")
            
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
            
            # Call a tool
            print("\nCalling kaltura.media.list tool:")
            try:
                result = await client.call_tool("kaltura.media.list", {"page_size": 5})
                print(json.dumps(json.loads(result[0].text), indent=2))
            except Exception as e:
                print(f"Error calling tool: {e}")
    except Exception as e:
        print(f"Error in STDIO example: {e}")


def http_example() -> None:
    """Example of using HTTP transport."""
    print("\n=== HTTP Transport Example ===")
    
    # Base URL for the server
    base_url = "http://localhost:8000"
    
    try:
        # Test connection to the server
        print("Connecting to Kaltura MCP Server using HTTP...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print(f"Connected to Kaltura MCP Server: {response.text}")
        else:
            print(f"Failed to connect to server: {response.status_code}")
            return
        
        # List available tools
        print("\nListing available tools:")
        response = requests.get(f"{base_url}/mcp/tools")
        if response.status_code == 200:
            tools = response.json()["tools"]
            for tool in tools:
                print(f"- {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print(f"Failed to list tools: {response.status_code}")
        
        # List available resources
        print("\nListing available resources:")
        response = requests.get(f"{base_url}/mcp/resources")
        if response.status_code == 200:
            resources = response.json()["resources"]
            for resource in resources:
                print(f"- {resource['uri']}: {resource.get('description', 'No description')}")
        else:
            print(f"Failed to list resources: {response.status_code}")
        
        # Call a tool
        print("\nCalling kaltura.media.list tool:")
        response = requests.post(
            f"{base_url}/mcp/tools/call",
            json={"name": "kaltura.media.list", "arguments": {"page_size": 5}},
        )
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to call tool: {response.status_code}")
    except Exception as e:
        print(f"Error in HTTP example: {e}")


def sse_example() -> None:
    """Example of using SSE transport."""
    print("\n=== SSE Transport Example ===")
    
    # Base URL for the server
    base_url = "http://localhost:8000"
    
    try:
        # Test connection to the server
        print("Connecting to Kaltura MCP Server using SSE...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print(f"Connected to Kaltura MCP Server: {response.text}")
        else:
            print(f"Failed to connect to server: {response.status_code}")
            return
        
        # Establish SSE connection
        print("\nEstablishing SSE connection...")
        try:
            response = requests.get(f"{base_url}/mcp/sse", stream=True)
            client = sseclient.SSEClient(response)
            
            # Start a thread to listen for SSE events
            def listen_for_events():
                for event in client.events():
                    print(f"Received SSE event: {event.event}")
                    print(f"Event data: {event.data}")
            
            import threading
            event_thread = threading.Thread(target=listen_for_events)
            event_thread.daemon = True
            event_thread.start()
            
            print("SSE connection established, listening for events...")
            
            # Call a tool to trigger an event
            print("\nCalling kaltura.media.list tool to trigger an event:")
            response = requests.post(
                f"{base_url}/mcp/tools/call",
                json={"name": "kaltura.media.list", "arguments": {"page_size": 5}},
            )
            if response.status_code == 200:
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"Failed to call tool: {response.status_code}")
            
            # Wait for events
            print("\nWaiting for events (press Ctrl+C to stop)...")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping SSE example...")
        except Exception as e:
            print(f"Error in SSE connection: {e}")
    except Exception as e:
        print(f"Error in SSE example: {e}")


class KalturaMcpClient:
    """Client for Kaltura MCP Server with support for different transports."""
    
    def __init__(self, transport_type="stdio", host=None, port=None):
        """
        Initialize the client.
        
        Args:
            transport_type: The transport type to use (stdio, http, sse)
            host: The host to connect to (for HTTP and SSE)
            port: The port to connect to (for HTTP and SSE)
        """
        self.transport_type = transport_type.lower()
        self.host = host or "localhost"
        self.port = port or 8000
        self.client = None
        self.base_url = f"http://{self.host}:{self.port}"
    
    async def connect(self):
        """Connect to the server."""
        if self.transport_type == "stdio":
            return await self._connect_stdio()
        elif self.transport_type == "http":
            return self._connect_http()
        elif self.transport_type == "sse":
            return self._connect_sse()
        else:
            raise ValueError(f"Unsupported transport type: {self.transport_type}")
    
    async def _connect_stdio(self):
        """Connect using STDIO transport."""
        streams = await stdio_client().__aenter__()
        self.client = Client()
        await self.client.connect(streams[0], streams[1])
        return self.client
    
    def _connect_http(self):
        """Connect using HTTP transport."""
        # For HTTP, we don't need to establish a persistent connection
        # We'll just make requests as needed
        response = requests.get(self.base_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to connect to server: {response.status_code}")
        return self
    
    def _connect_sse(self):
        """Connect using SSE transport."""
        # Establish SSE connection
        response = requests.get(f"{self.base_url}/mcp/sse", stream=True)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to establish SSE connection: {response.status_code}")
        
        self.sse_client = sseclient.SSEClient(response)
        
        # Start a thread to listen for SSE events
        def listen_for_events():
            for event in self.sse_client.events():
                print(f"Received SSE event: {event.event}")
                print(f"Event data: {event.data}")
        
        import threading
        self.event_thread = threading.Thread(target=listen_for_events)
        self.event_thread.daemon = True
        self.event_thread.start()
        
        return self
    
    async def list_tools(self):
        """List available tools."""
        if self.transport_type == "stdio":
            return await self.client.list_tools()
        else:
            response = requests.get(f"{self.base_url}/mcp/tools")
            if response.status_code != 200:
                raise Exception(f"Failed to list tools: {response.status_code}")
            return response.json()["tools"]
    
    async def list_resources(self):
        """List available resources."""
        if self.transport_type == "stdio":
            return await self.client.list_resources()
        else:
            response = requests.get(f"{self.base_url}/mcp/resources")
            if response.status_code != 200:
                raise Exception(f"Failed to list resources: {response.status_code}")
            return response.json()["resources"]
    
    async def call_tool(self, name, arguments=None):
        """Call a tool."""
        if arguments is None:
            arguments = {}
        
        if self.transport_type == "stdio":
            return await self.client.call_tool(name, arguments)
        else:
            response = requests.post(
                f"{self.base_url}/mcp/tools/call",
                json={"name": name, "arguments": arguments},
            )
            if response.status_code != 200:
                raise Exception(f"Failed to call tool: {response.status_code}")
            return response.json()
    
    async def read_resource(self, uri):
        """Read a resource."""
        if self.transport_type == "stdio":
            return await self.client.read_resource(uri)
        else:
            response = requests.get(f"{self.base_url}/mcp/resources/read?uri={uri}")
            if response.status_code != 200:
                raise Exception(f"Failed to read resource: {response.status_code}")
            return response.json()


async def unified_client_example():
    """Example of using the unified client."""
    print("\n=== Unified Client Example ===")
    
    # Create clients for different transports
    stdio_client = KalturaMcpClient(transport_type="stdio")
    http_client = KalturaMcpClient(transport_type="http", host="localhost", port=8000)
    sse_client = KalturaMcpClient(transport_type="sse", host="localhost", port=8000)
    
    # Connect to the server using STDIO
    print("\n--- STDIO Transport ---")
    try:
        print("Connecting to Kaltura MCP Server using STDIO...")
        await stdio_client.connect()
        
        print("Listing tools...")
        tools = await stdio_client.list_tools()
        print(f"Found {len(tools)} tools")
        
        print("Calling kaltura.media.list tool...")
        result = await stdio_client.call_tool("kaltura.media.list", {"page_size": 5})
        print(f"Got {len(json.loads(result[0].text)['objects'])} media entries")
    except Exception as e:
        print(f"Error with STDIO client: {e}")
    
    # Connect to the server using HTTP
    print("\n--- HTTP Transport ---")
    try:
        print("Connecting to Kaltura MCP Server using HTTP...")
        http_client.connect()
        
        print("Listing tools...")
        tools = await http_client.list_tools()
        print(f"Found {len(tools)} tools")
        
        print("Calling kaltura.media.list tool...")
        result = await http_client.call_tool("kaltura.media.list", {"page_size": 5})
        print(f"Got {len(result['objects'])} media entries")
    except Exception as e:
        print(f"Error with HTTP client: {e}")
    
    # Connect to the server using SSE
    print("\n--- SSE Transport ---")
    try:
        print("Connecting to Kaltura MCP Server using SSE...")
        sse_client.connect()
        
        print("Listing tools...")
        tools = await sse_client.list_tools()
        print(f"Found {len(tools)} tools")
        
        print("Calling kaltura.media.list tool...")
        result = await sse_client.call_tool("kaltura.media.list", {"page_size": 5})
        print(f"Got {len(result['objects'])} media entries")
        
        print("Waiting for SSE events (press Ctrl+C to stop)...")
        try:
            await asyncio.sleep(10)  # Wait for 10 seconds to receive events
        except KeyboardInterrupt:
            print("\nStopping SSE client...")
    except Exception as e:
        print(f"Error with SSE client: {e}")


async def main():
    """Run the examples."""
    # Get the example to run from command line
    if len(sys.argv) > 1:
        example = sys.argv[1].lower()
    else:
        example = "all"
    
    if example == "stdio" or example == "all":
        await stdio_example()
    
    if example == "http" or example == "all":
        http_example()
    
    if example == "sse" or example == "all":
        sse_example()
    
    if example == "unified" or example == "all":
        await unified_client_example()


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Components

1. **Individual Transport Examples**:
   - `stdio_example()`: Demonstrates using the STDIO transport
   - `http_example()`: Demonstrates using the HTTP transport
   - `sse_example()`: Demonstrates using the SSE transport

2. **Unified Client**:
   - `KalturaMcpClient`: A client class that supports all transport types
   - `unified_client_example()`: Demonstrates using the unified client with different transports

3. **Main Function**:
   - Parses command line arguments to determine which examples to run
   - Runs the specified examples

## How to Use the Examples

### Running Individual Examples

```bash
# Run all examples
python examples/transport_client_examples.py

# Run only the STDIO example
python examples/transport_client_examples.py stdio

# Run only the HTTP example
python examples/transport_client_examples.py http

# Run only the SSE example
python examples/transport_client_examples.py sse

# Run only the unified client example
python examples/transport_client_examples.py unified
```

### Using the Unified Client

The unified client provides a consistent interface for all transport types:

```python
# Create a client with the desired transport
client = KalturaMcpClient(transport_type="http", host="localhost", port=8000)

# Connect to the server
await client.connect()

# List available tools
tools = await client.list_tools()

# Call a tool
result = await client.call_tool("kaltura.media.list", {"page_size": 5})

# Read a resource
resource = await client.read_resource("kaltura://media/0_abc123")
```

## STDIO Transport Example

The STDIO transport example demonstrates:

1. Connecting to the server using the STDIO transport
2. Listing available tools
3. Listing available resources
4. Calling a tool

This example uses the MCP SDK's `stdio_client` context manager to establish a connection to the server.

## HTTP Transport Example

The HTTP transport example demonstrates:

1. Connecting to the server using HTTP
2. Listing available tools
3. Listing available resources
4. Calling a tool

This example uses the `requests` library to make HTTP requests to the server.

## SSE Transport Example

The SSE transport example demonstrates:

1. Connecting to the server using HTTP
2. Establishing an SSE connection
3. Listening for SSE events
4. Calling a tool to trigger an event

This example uses the `sseclient` library to establish an SSE connection and listen for events.

## Unified Client

The unified client provides a consistent interface for all transport types. It abstracts away the differences between the transports, allowing you to use the same code regardless of the transport type.

The unified client supports:

1. Connecting to the server
2. Listing available tools
3. Listing available resources
4. Calling tools
5. Reading resources

## Error Handling

Each example includes error handling to catch and report any exceptions that occur during execution. The unified client also includes error handling for each transport type.

## Dependencies

The examples require the following dependencies:

- `requests`: For HTTP requests
- `sseclient`: For SSE connections
- `mcp.client.lowlevel`: For the MCP client
- `mcp.client.stdio`: For the STDIO transport

These dependencies should be installed in your Python environment.