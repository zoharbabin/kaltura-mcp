# SSE Transport Implementation

This document provides the detailed implementation for the Server-Sent Events (SSE) transport in the Kaltura MCP server.

## File: `kaltura_mcp/transport/sse.py`

```python
"""
Server-Sent Events (SSE) transport implementation for Kaltura MCP Server.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from mcp.server.lowlevel import Server

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


class SseTransport(McpTransport):
    """Server-Sent Events based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the SSE transport.
        
        Args:
            config: Server configuration dictionary
        """
        super().__init__(config)
        self.host = config["server"]["host"]
        self.port = config["server"]["port"]
        self.app = None
        self.server_instance = None
        self.mcp_server = None
        self.active_connections = set()
    
    async def initialize(self) -> None:
        """Initialize the SSE transport."""
        await super().initialize()
        logger.info(f"SSE transport will listen on {self.host}:{self.port}")
    
    async def run(self, server: Server) -> None:
        """
        Run the server using SSE transport.
        
        Args:
            server: The MCP server instance
        """
        logger.info(f"Starting server with SSE transport on {self.host}:{self.port}")
        
        try:
            # Store the server instance
            self.mcp_server = server
            
            # Create the ASGI app
            self.app = self._create_app()
            
            # Run the server
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server_instance = uvicorn.Server(config)
            await self.server_instance.serve()
        except Exception as e:
            logger.error(f"Error running server with SSE transport: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the SSE server."""
        await super().shutdown()
        
        if self.server_instance:
            logger.info("Shutting down SSE server")
            await self.server_instance.shutdown()
    
    def _create_app(self) -> Starlette:
        """Create the ASGI app."""
        routes = [
            Route("/", self._handle_root),
            Route("/mcp/info", self._handle_info),
            Route("/mcp/tools", self._handle_list_tools),
            Route("/mcp/resources", self._handle_list_resources),
            Route("/mcp/resources/read", self._handle_read_resource),
            Route("/mcp/tools/call", self._handle_call_tool, methods=["POST"]),
            Route("/mcp/sse", self._handle_sse_connection),
        ]
        
        return Starlette(routes=routes)
    
    async def _handle_root(self, request: Request) -> Response:
        """Handle root endpoint."""
        return Response("Kaltura MCP Server", media_type="text/plain")
    
    async def _handle_info(self, request: Request) -> JSONResponse:
        """Handle info endpoint."""
        info = {
            "name": "Kaltura MCP Server",
            "version": "1.0.0",
            "transport": "sse",
        }
        return JSONResponse(info)
    
    async def _handle_list_tools(self, request: Request) -> JSONResponse:
        """Handle list tools endpoint."""
        if not self.mcp_server:
            return JSONResponse({"error": "Server not initialized"}, status_code=500)
        
        try:
            tools = await self.mcp_server.list_tools()
            return JSONResponse({"tools": tools})
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def _handle_list_resources(self, request: Request) -> JSONResponse:
        """Handle list resources endpoint."""
        if not self.mcp_server:
            return JSONResponse({"error": "Server not initialized"}, status_code=500)
        
        try:
            resources = await self.mcp_server.list_resources()
            return JSONResponse({"resources": resources})
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def _handle_read_resource(self, request: Request) -> JSONResponse:
        """Handle read resource endpoint."""
        if not self.mcp_server:
            return JSONResponse({"error": "Server not initialized"}, status_code=500)
        
        try:
            # Get URI from query parameters
            uri = request.query_params.get("uri")
            if not uri:
                return JSONResponse({"error": "Missing uri parameter"}, status_code=400)
            
            resource = await self.mcp_server.read_resource(uri)
            return JSONResponse(resource)
        except Exception as e:
            logger.error(f"Error reading resource: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def _handle_call_tool(self, request: Request) -> JSONResponse:
        """Handle call tool endpoint."""
        if not self.mcp_server:
            return JSONResponse({"error": "Server not initialized"}, status_code=500)
        
        try:
            # Get tool name and arguments from request
            request_data = await request.json()
            name = request_data.get("name")
            if not name:
                return JSONResponse({"error": "Missing name parameter"}, status_code=400)
            
            arguments = request_data.get("arguments", {})
            
            result = await self.mcp_server.call_tool(name, arguments)
            
            # Notify all connected clients about the tool call
            await self._notify_clients({
                "event": "tool_called",
                "data": {
                    "name": name,
                    "arguments": arguments
                }
            })
            
            return JSONResponse(result)
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    
    async def _handle_sse_connection(self, request: Request) -> Response:
        """Handle SSE connection."""
        if not self.mcp_server:
            return Response("Server not initialized", status_code=500)
        
        connection_id = id(request)
        
        async def event_generator():
            """Generate SSE events."""
            # Add this connection to active connections
            self.active_connections.add(connection_id)
            
            try:
                # Send initial connection event
                yield f"event: connected\ndata: {json.dumps({'id': connection_id})}\n\n"
                
                # Keep the connection alive
                while True:
                    # Send a ping every 30 seconds
                    await asyncio.sleep(30)
                    yield "event: ping\ndata: {}\n\n"
            finally:
                # Remove this connection when done
                self.active_connections.discard(connection_id)
        
        return Response(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    
    async def _notify_clients(self, data: Dict[str, Any]) -> None:
        """
        Notify all connected SSE clients.
        
        Args:
            data: The data to send to clients
        """
        # This would be implemented to send events to all connected clients
        # In a real implementation, we would need a way to send events to the
        # event generators for each client connection
        logger.info(f"Would notify {len(self.active_connections)} clients: {data}")
```

## Key Components

1. **SseTransport Class**: Implements the `McpTransport` interface for Server-Sent Events (SSE) communication.

2. **ASGI Application**: Uses Starlette to create an ASGI application that handles HTTP requests and SSE connections.

3. **Endpoint Handlers**:
   - `_handle_root()`: Handles requests to the root endpoint
   - `_handle_info()`: Provides server information
   - `_handle_list_tools()`: Lists available tools
   - `_handle_list_resources()`: Lists available resources
   - `_handle_read_resource()`: Reads a specific resource
   - `_handle_call_tool()`: Calls a specific tool
   - `_handle_sse_connection()`: Establishes an SSE connection

4. **SSE Connection Management**: Tracks active SSE connections and provides a mechanism to notify all connected clients.

## SSE API Endpoints

The SSE transport exposes the following endpoints:

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Root endpoint, returns a simple message | None |
| `/mcp/info` | GET | Returns server information | None |
| `/mcp/tools` | GET | Lists available tools | None |
| `/mcp/resources` | GET | Lists available resources | None |
| `/mcp/resources/read` | GET | Reads a specific resource | `uri` (query parameter) |
| `/mcp/tools/call` | POST | Calls a specific tool | `name`, `arguments` (JSON body) |
| `/mcp/sse` | GET | Establishes an SSE connection | None |

## How SSE Transport Works

The SSE transport uses Server-Sent Events to enable real-time communication from the server to clients:

1. The server listens for HTTP requests on the configured host and port
2. Clients can establish an SSE connection by sending a GET request to the `/mcp/sse` endpoint
3. The server keeps the connection open and sends events to the client as they occur
4. Clients can also make regular HTTP requests to other endpoints to interact with the MCP server

This transport is particularly useful for:
- Real-time updates and notifications
- Web applications that need to display live data
- Monitoring and dashboard applications

## SSE Events

The SSE transport sends the following events to connected clients:

| Event | Description | Data |
|-------|-------------|------|
| `connected` | Sent when a client establishes a connection | `{ "id": connection_id }` |
| `ping` | Sent periodically to keep the connection alive | `{}` |
| `tool_called` | Sent when a tool is called | `{ "name": tool_name, "arguments": tool_arguments }` |

## Advantages of SSE Transport

1. **Real-time Updates**: Provides real-time updates to clients without polling
2. **Efficiency**: More efficient than polling for updates
3. **Compatibility**: Works with standard web technologies
4. **Simplicity**: Simpler than WebSockets for one-way communication

## Limitations of SSE Transport

1. **One-way Communication**: Only supports server-to-client communication
2. **Connection Limits**: Browsers typically limit the number of concurrent SSE connections
3. **Overhead**: Keeps connections open, which can consume server resources
4. **Complexity**: More complex to implement and maintain than HTTP transport

## Usage Example

```python
# Server side (configured to use SSE transport)
server = KalturaMcpServer(config)
await server.initialize()
await server.run()

# Client side (using JavaScript)
const eventSource = new EventSource('http://localhost:8000/mcp/sse');

eventSource.addEventListener('connected', (event) => {
  console.log('Connected to SSE stream:', JSON.parse(event.data));
});

eventSource.addEventListener('tool_called', (event) => {
  console.log('Tool called:', JSON.parse(event.data));
});

// Make a regular HTTP request to call a tool
fetch('http://localhost:8000/mcp/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'kaltura.media.list',
    arguments: { page_size: 5 }
  })
})
.then(response => response.json())
.then(result => console.log('Tool result:', result));
```

## Error Handling

The SSE transport handles errors as follows:

1. Catches exceptions during request processing
2. Logs the error with context
3. Returns an appropriate HTTP error response to the client
4. For critical errors during server startup, re-raises the exception to be handled by the caller

This approach ensures that errors are properly logged and communicated to the client while still allowing the server to continue handling other requests.

## Implementation Notes

The current implementation has a limitation in the `_notify_clients()` method, which only logs the notification rather than actually sending it to clients. In a real implementation, this would need to be enhanced to actually send events to all connected clients. This could be done using a message queue or a similar mechanism to communicate between the request handlers and the SSE event generators.