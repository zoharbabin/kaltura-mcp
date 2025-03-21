# HTTP Transport Implementation

This document provides the detailed implementation for the HTTP transport in the Kaltura MCP server.

## File: `kaltura_mcp/transport/http.py`

```python
"""
HTTP transport implementation for Kaltura MCP Server.
"""
import asyncio
import http.server
import json
import logging
import socketserver
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from urllib.parse import parse_qs, urlparse

import mcp.types as types
from mcp.server.lowlevel import Server

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


class McpHttpHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for MCP server requests."""
    
    # This will be set by the transport
    mcp_server: Optional[Server] = None
    
    def log_message(self, format: str, *args: Any) -> None:
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format%args}")
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query = parse_qs(parsed_url.query)
            
            # Handle different endpoints
            if path == "/":
                self._handle_root()
            elif path == "/mcp/info":
                self._handle_info()
            elif path == "/mcp/tools":
                self._handle_list_tools()
            elif path == "/mcp/resources":
                self._handle_list_resources()
            elif path.startswith("/mcp/resources/read"):
                self._handle_read_resource(query)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self) -> None:
        """Handle POST requests."""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Read request body
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            request_data = json.loads(body)
            
            # Handle different endpoints
            if path == "/mcp/tools/call":
                self._handle_call_tool(request_data)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, str(e))
    
    def _handle_root(self) -> None:
        """Handle root endpoint."""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Kaltura MCP Server")
    
    def _handle_info(self) -> None:
        """Handle info endpoint."""
        info = {
            "name": "Kaltura MCP Server",
            "version": "1.0.0",
            "transport": "http",
        }
        self._send_json_response(info)
    
    def _handle_list_tools(self) -> None:
        """Handle list tools endpoint."""
        if not self.mcp_server:
            self.send_error(500, "Server not initialized")
            return
            
        try:
            # Run the coroutine in a new event loop
            tools = self._run_coroutine(self.mcp_server.list_tools())
            self._send_json_response({"tools": tools})
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            self.send_error(500, str(e))
    
    def _handle_list_resources(self) -> None:
        """Handle list resources endpoint."""
        if not self.mcp_server:
            self.send_error(500, "Server not initialized")
            return
            
        try:
            # Run the coroutine in a new event loop
            resources = self._run_coroutine(self.mcp_server.list_resources())
            self._send_json_response({"resources": resources})
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            self.send_error(500, str(e))
    
    def _handle_read_resource(self, query: Dict[str, List[str]]) -> None:
        """Handle read resource endpoint."""
        if not self.mcp_server:
            self.send_error(500, "Server not initialized")
            return
            
        try:
            # Get URI from query parameters
            if "uri" not in query:
                self.send_error(400, "Missing uri parameter")
                return
                
            uri = query["uri"][0]
            
            # Run the coroutine in a new event loop
            resource = self._run_coroutine(self.mcp_server.read_resource(uri))
            self._send_json_response(resource)
        except Exception as e:
            logger.error(f"Error reading resource: {e}")
            self.send_error(500, str(e))
    
    def _handle_call_tool(self, request_data: Dict[str, Any]) -> None:
        """Handle call tool endpoint."""
        if not self.mcp_server:
            self.send_error(500, "Server not initialized")
            return
            
        try:
            # Get tool name and arguments from request
            if "name" not in request_data:
                self.send_error(400, "Missing name parameter")
                return
                
            name = request_data["name"]
            arguments = request_data.get("arguments", {})
            
            # Run the coroutine in a new event loop
            result = self._run_coroutine(self.mcp_server.call_tool(name, arguments))
            self._send_json_response(result)
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            self.send_error(500, str(e))
    
    def _send_json_response(self, data: Any) -> None:
        """Send a JSON response."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _run_coroutine(self, coroutine: Any) -> Any:
        """Run a coroutine in a new event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server."""
    daemon_threads = True


class HttpTransport(McpTransport):
    """HTTP-based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the HTTP transport.
        
        Args:
            config: Server configuration dictionary
        """
        super().__init__(config)
        self.host = config["server"]["host"]
        self.port = config["server"]["port"]
        self.server = None
        self.server_thread = None
    
    async def initialize(self) -> None:
        """Initialize the HTTP transport."""
        await super().initialize()
        logger.info(f"HTTP transport will listen on {self.host}:{self.port}")
    
    async def run(self, server: Server) -> None:
        """
        Run the server using HTTP transport.
        
        Args:
            server: The MCP server instance
        """
        logger.info(f"Starting server with HTTP transport on {self.host}:{self.port}")
        
        try:
            # Set the server instance in the handler class
            McpHttpHandler.mcp_server = server
            
            # Create and start the HTTP server
            self.server = ThreadedHTTPServer((self.host, self.port), McpHttpHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info(f"HTTP server started on {self.host}:{self.port}")
            
            # Keep the main thread running
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error running server with HTTP transport: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the HTTP server."""
        await super().shutdown()
        
        if self.server:
            logger.info("Shutting down HTTP server")
            self.server.shutdown()
            self.server.server_close()
```

## Key Components

1. **HttpTransport Class**: Implements the `McpTransport` interface for HTTP communication.

2. **McpHttpHandler Class**: Handles HTTP requests and routes them to the appropriate MCP server methods.

3. **ThreadedHTTPServer Class**: Provides a threaded HTTP server implementation for handling multiple concurrent requests.

4. **Endpoint Handlers**:
   - `_handle_root()`: Handles requests to the root endpoint
   - `_handle_info()`: Provides server information
   - `_handle_list_tools()`: Lists available tools
   - `_handle_list_resources()`: Lists available resources
   - `_handle_read_resource()`: Reads a specific resource
   - `_handle_call_tool()`: Calls a specific tool

5. **Coroutine Runner**: The `_run_coroutine()` method runs asynchronous MCP server methods in a new event loop, allowing them to be called from synchronous HTTP handler methods.

## HTTP API Endpoints

The HTTP transport exposes the following endpoints:

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Root endpoint, returns a simple message | None |
| `/mcp/info` | GET | Returns server information | None |
| `/mcp/tools` | GET | Lists available tools | None |
| `/mcp/resources` | GET | Lists available resources | None |
| `/mcp/resources/read` | GET | Reads a specific resource | `uri` (query parameter) |
| `/mcp/tools/call` | POST | Calls a specific tool | `name`, `arguments` (JSON body) |

## How HTTP Transport Works

The HTTP transport uses a standard HTTP server to expose MCP functionality:

1. The server listens for HTTP requests on the configured host and port
2. When a request is received, it is routed to the appropriate handler based on the URL path
3. The handler converts the HTTP request to an MCP request, calls the appropriate MCP server method, and converts the result back to an HTTP response
4. The response is sent back to the client

This transport is particularly useful for:
- Web-based clients
- Integration with web applications
- Remote access to the MCP server

## Advantages of HTTP Transport

1. **Accessibility**: Can be accessed from any HTTP client
2. **Scalability**: Can handle multiple concurrent connections
3. **Compatibility**: Works with standard web technologies
4. **Flexibility**: Can be extended with additional endpoints and features

## Limitations of HTTP Transport

1. **Overhead**: HTTP adds some overhead compared to direct STDIO communication
2. **Security**: Requires additional security measures for production use
3. **Complexity**: More complex to implement and maintain than STDIO transport

## Usage Example

```python
# Server side (configured to use HTTP transport)
server = KalturaMcpServer(config)
await server.initialize()
await server.run()

# Client side (using requests library)
import requests

# List tools
response = requests.get("http://localhost:8000/mcp/tools")
tools = response.json()["tools"]

# Call a tool
response = requests.post(
    "http://localhost:8000/mcp/tools/call",
    json={"name": "kaltura.media.list", "arguments": {"page_size": 5}}
)
result = response.json()
```

## Error Handling

The HTTP transport handles errors as follows:

1. Catches exceptions during request processing
2. Logs the error with context
3. Returns an appropriate HTTP error response to the client
4. For critical errors during server startup, re-raises the exception to be handled by the caller

This approach ensures that errors are properly logged and communicated to the client while still allowing the server to continue handling other requests.

## Thread Safety

The HTTP transport uses a threaded HTTP server to handle multiple concurrent requests. Each request is handled in a separate thread, so the handler methods must be thread-safe. The `_run_coroutine()` method creates a new event loop for each request to ensure thread safety when calling asynchronous MCP server methods.