# Extending the Transport Architecture

This guide explains how to extend the Kaltura MCP transport architecture with new transport mechanisms.

## Overview

The Kaltura MCP server uses a modular transport architecture that allows it to support different communication mechanisms. The current implementation includes three transport types:

1. **STDIO Transport**: For direct process-to-process communication
2. **HTTP Transport**: For web-based communication
3. **SSE Transport**: For Server-Sent Events based communication

You can extend this architecture by implementing new transport mechanisms, such as WebSockets, gRPC, or any other protocol that suits your needs.

## Transport Architecture

The transport architecture is based on the following components:

1. **Base Transport Interface**: An abstract base class that defines the common interface for all transport mechanisms
2. **Transport Implementations**: Concrete implementations of the base transport interface
3. **Transport Factory**: A factory class that creates transport instances based on configuration

### Base Transport Interface

The base transport interface is defined in `kaltura_mcp/transport/base.py` and provides the following methods:

- `__init__(config)`: Initialize the transport with configuration
- `initialize()`: Initialize the transport (e.g., set up connections)
- `run(server)`: Run the transport (e.g., start listening for connections)
- `shutdown()`: Shut down the transport (e.g., close connections)

## Creating a New Transport

To create a new transport mechanism, follow these steps:

### 1. Create a New Transport Module

Create a new Python module in the `kaltura_mcp/transport` directory. For example, to create a WebSocket transport, create a file named `websocket.py`:

```python
"""
WebSocket transport for the Kaltura MCP server.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import websockets
from websockets.server import WebSocketServerProtocol

from kaltura_mcp.transport.base import McpTransport


class WebSocketTransport(McpTransport):
    """WebSocket transport for the Kaltura MCP server."""

    def __init__(self, config):
        """
        Initialize the WebSocket transport.

        Args:
            config: The server configuration
        """
        super().__init__(config)
        self.host = config.server.host
        self.port = config.server.port
        self.server = None
        self.connections = set()
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize the WebSocket transport."""
        self.logger.info(f"Initializing WebSocket transport on {self.host}:{self.port}")

    async def run(self, server):
        """
        Run the WebSocket transport.

        Args:
            server: The MCP server instance
        """
        self.logger.info(f"Starting WebSocket transport on {self.host}:{self.port}")
        
        async def handler(websocket, path):
            """Handle WebSocket connections."""
            self.connections.add(websocket)
            try:
                # Send a welcome message
                await websocket.send(json.dumps({
                    "type": "connected",
                    "data": {
                        "id": id(websocket),
                        "server": "Kaltura MCP Server",
                        "transport": "websocket"
                    }
                }))
                
                # Handle incoming messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if "type" not in data:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "data": {
                                    "message": "Missing 'type' field in request"
                                }
                            }))
                            continue
                        
                        if data["type"] == "get_server_info":
                            # Handle get_server_info request
                            info = await server.get_server_info()
                            await websocket.send(json.dumps({
                                "type": "server_info",
                                "data": info
                            }))
                        
                        elif data["type"] == "list_tools":
                            # Handle list_tools request
                            tools = await server.list_tools()
                            await websocket.send(json.dumps({
                                "type": "tools_list",
                                "data": {
                                    "tools": [tool.to_dict() for tool in tools]
                                }
                            }))
                        
                        elif data["type"] == "list_resources":
                            # Handle list_resources request
                            resources = await server.list_resources()
                            await websocket.send(json.dumps({
                                "type": "resources_list",
                                "data": {
                                    "resources": [resource.to_dict() for resource in resources]
                                }
                            }))
                        
                        elif data["type"] == "call_tool":
                            # Handle call_tool request
                            if "name" not in data or "arguments" not in data:
                                await websocket.send(json.dumps({
                                    "type": "error",
                                    "data": {
                                        "message": "Missing 'name' or 'arguments' field in call_tool request"
                                    }
                                }))
                                continue
                            
                            result = await server.call_tool(data["name"], data["arguments"])
                            await websocket.send(json.dumps({
                                "type": "tool_result",
                                "data": result
                            }))
                        
                        elif data["type"] == "read_resource":
                            # Handle read_resource request
                            if "uri" not in data:
                                await websocket.send(json.dumps({
                                    "type": "error",
                                    "data": {
                                        "message": "Missing 'uri' field in read_resource request"
                                    }
                                }))
                                continue
                            
                            resource = await server.read_resource(data["uri"])
                            await websocket.send(json.dumps({
                                "type": "resource_content",
                                "data": resource.to_dict()
                            }))
                        
                        else:
                            # Handle unknown request type
                            await websocket.send(json.dumps({
                                "type": "error",
                                "data": {
                                    "message": f"Unknown request type: {data['type']}"
                                }
                            }))
                    
                    except json.JSONDecodeError:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "data": {
                                "message": "Invalid JSON in request"
                            }
                        }))
                    except Exception as e:
                        self.logger.error(f"Error handling WebSocket message: {e}")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "data": {
                                "message": str(e)
                            }
                        }))
            
            except websockets.exceptions.ConnectionClosed:
                self.logger.info(f"WebSocket connection closed: {id(websocket)}")
            finally:
                self.connections.remove(websocket)
        
        # Start the WebSocket server
        self.server = await websockets.serve(handler, self.host, self.port)
        
        # Keep the server running
        await self.server.wait_closed()

    async def shutdown(self):
        """Shut down the WebSocket transport."""
        self.logger.info("Shutting down WebSocket transport")
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all connections
        for websocket in self.connections:
            await websocket.close()
        self.connections.clear()
```

### 2. Update the Transport Factory

Update the transport factory in `kaltura_mcp/transport/__init__.py` to support your new transport type:

```python
"""
Transport factory for the Kaltura MCP server.
"""
from typing import Dict, Type

from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.stdio import StdioTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.websocket import WebSocketTransport  # Import your new transport


class TransportFactory:
    """Factory for creating transport instances."""

    # Map of transport types to transport classes
    _transport_types: Dict[str, Type[McpTransport]] = {
        "stdio": StdioTransport,
        "http": HttpTransport,
        "sse": SseTransport,
        "websocket": WebSocketTransport,  # Add your new transport
    }

    @classmethod
    def create_transport(cls, config) -> McpTransport:
        """
        Create a transport instance based on configuration.

        Args:
            config: The server configuration

        Returns:
            A transport instance

        Raises:
            ValueError: If the transport type is not supported
        """
        transport_type = config.server.transport.lower()
        if transport_type not in cls._transport_types:
            supported_types = ", ".join(cls._transport_types.keys())
            raise ValueError(
                f"Unsupported transport type: {transport_type}. "
                f"Supported types: {supported_types}"
            )
        
        transport_class = cls._transport_types[transport_type]
        return transport_class(config)
```

### 3. Create a Client Example

Create a client example in `examples/transport_client_examples.py` to demonstrate how to use your new transport:

```python
def websocket_client_example(host: str = "localhost", port: int = 8000) -> None:
    """
    Example of using the WebSocket transport.
    
    Args:
        host: The server host
        port: The server port
    """
    print("=== WebSocket Transport Example ===")
    
    import asyncio
    import websockets
    import json
    
    async def connect():
        uri = f"ws://{host}:{port}/mcp/ws"
        async with websockets.connect(uri) as websocket:
            # Receive the welcome message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Connected: {data}")
            
            # Get server info
            await websocket.send(json.dumps({"type": "get_server_info"}))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Server info: {data['data']}")
            
            # List tools
            await websocket.send(json.dumps({"type": "list_tools"}))
            response = await websocket.recv()
            data = json.loads(response)
            tools = data["data"]["tools"]
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            # List resources
            await websocket.send(json.dumps({"type": "list_resources"}))
            response = await websocket.recv()
            data = json.loads(response)
            resources = data["data"]["resources"]
            print(f"Available resources: {len(resources)}")
            for resource in resources:
                print(f"  - {resource['uri']}: {resource['name']}")
            
            # Call a tool
            if any(tool["name"] == "kaltura.media.list" for tool in tools):
                print("\nCalling kaltura.media.list tool...")
                await websocket.send(json.dumps({
                    "type": "call_tool",
                    "name": "kaltura.media.list",
                    "arguments": {"page_size": 5}
                }))
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Result: {data['data']}")
    
    asyncio.run(connect())
```

### 4. Update the Main Function

Update the main function in `examples/transport_client_examples.py` to support your new transport:

```python
def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python transport_client_examples.py <transport_type> [host] [port]")
        print("  transport_type: stdio, http, sse, or websocket")  # Add your new transport
        print("  host: Server host (default: localhost)")
        print("  port: Server port (default: 8000)")
        sys.exit(1)
    
    transport_type = sys.argv[1].lower()
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    
    if transport_type == "stdio":
        asyncio.run(stdio_client_example())
    elif transport_type == "http":
        http_client_example(host, port)
    elif transport_type == "sse":
        sse_client_example(host, port)
    elif transport_type == "websocket":  # Add your new transport
        websocket_client_example(host, port)
    else:
        print(f"Unsupported transport type: {transport_type}")
        print("Supported types: stdio, http, sse, websocket")  # Add your new transport
        sys.exit(1)
```

### 5. Update the Configuration

Update the configuration to support your new transport type:

```yaml
# Server configuration
server:
  transport: "websocket"  # Add your new transport
  host: "0.0.0.0"
  port: 8000
  debug: false
```

### 6. Add Dependencies

Add any new dependencies to `pyproject.toml`:

```toml
[project]
# ...
dependencies = [
    # ...
    "websockets",  # Add your new dependency
]
```

## Testing Your New Transport

To test your new transport, follow these steps:

1. Install the new dependencies:

```bash
pip install -e .
```

2. Start the server with your new transport:

```bash
KALTURA_MCP_TRANSPORT=websocket kaltura-mcp
```

3. Run the client example:

```bash
python examples/transport_client_examples.py websocket
```

## Best Practices

When implementing a new transport mechanism, consider the following best practices:

1. **Error Handling**: Implement robust error handling to handle connection issues, invalid requests, and other errors.
2. **Logging**: Add detailed logging to help diagnose issues.
3. **Security**: Consider security implications, such as authentication and encryption.
4. **Performance**: Optimize for performance, especially for high-traffic applications.
5. **Testing**: Write comprehensive tests for your new transport.
6. **Documentation**: Document your new transport and provide examples.

## Example: WebSocket Transport

The WebSocket transport example above demonstrates how to implement a new transport mechanism. It provides bidirectional communication between the client and server, which is useful for applications that need real-time updates and interactions.

### WebSocket Protocol

The WebSocket protocol uses a simple message-based communication model:

1. **Client to Server**:
   - `{"type": "get_server_info"}`: Get server information
   - `{"type": "list_tools"}`: List available tools
   - `{"type": "list_resources"}`: List available resources
   - `{"type": "call_tool", "name": "tool_name", "arguments": {...}}`: Call a tool
   - `{"type": "read_resource", "uri": "resource_uri"}`: Read a resource

2. **Server to Client**:
   - `{"type": "connected", "data": {...}}`: Connection established
   - `{"type": "server_info", "data": {...}}`: Server information
   - `{"type": "tools_list", "data": {"tools": [...]}}`: List of tools
   - `{"type": "resources_list", "data": {"resources": [...]}}`: List of resources
   - `{"type": "tool_result", "data": {...}}`: Tool result
   - `{"type": "resource_content", "data": {...}}`: Resource content
   - `{"type": "error", "data": {"message": "..."}}`: Error message

### WebSocket Client

A simple WebSocket client can be implemented using the `websockets` library:

```python
import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8000/mcp/ws"
    async with websockets.connect(uri) as websocket:
        # Receive the welcome message
        response = await websocket.recv()
        print(f"< {response}")
        
        # Get server info
        await websocket.send(json.dumps({"type": "get_server_info"}))
        response = await websocket.recv()
        print(f"< {response}")
        
        # List tools
        await websocket.send(json.dumps({"type": "list_tools"}))
        response = await websocket.recv()
        print(f"< {response}")
        
        # Call a tool
        await websocket.send(json.dumps({
            "type": "call_tool",
            "name": "kaltura.media.list",
            "arguments": {"page_size": 5}
        }))
        response = await websocket.recv()
        print(f"< {response}")

asyncio.run(main())
```

## Conclusion

Extending the Kaltura MCP transport architecture with new transport mechanisms is straightforward. By following the steps outlined in this guide, you can add support for any communication protocol that suits your needs.

The modular design of the transport architecture makes it easy to add new transport types without changing the core server code. This flexibility allows the Kaltura MCP server to be used in a variety of environments and use cases.