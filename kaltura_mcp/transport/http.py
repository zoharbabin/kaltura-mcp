"""
HTTP transport implementation for Kaltura MCP Server.
"""

import asyncio
import http.server
import json
import logging
import socketserver
import threading
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from mcp.server.lowlevel import Server
from mcp.types import EmbeddedResource, ImageContent, Resource, TextContent, Tool
from pydantic.networks import AnyUrl

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


class McpJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MCP objects."""

    def default(self, o: Any) -> Any:
        """
        Handle MCP objects.
        
        Args:
            o: The object to serialize
            
        Returns:
            A JSON serializable representation of the object
        """
        # Handle different MCP object types
        if isinstance(o, Tool):
            return {
                "name": o.name,
                "description": o.description,
                "input_schema": o.inputSchema,  # Use camelCase as per mcp.types.Tool
            }
        if isinstance(o, Resource):
            return {
                "uri": str(o.uri),  # Convert AnyUrl to string
                "name": o.name,
                "description": o.description,
                "mime_type": o.mimeType,  # Use camelCase as per mcp.types.Resource
            }
        if isinstance(o, TextContent):
            return {"type": o.type, "text": o.text}
        if isinstance(o, ImageContent):
            return {"type": o.type, "data": o.data, "mimeType": o.mimeType}
        if isinstance(o, EmbeddedResource):
            return {"type": o.type, "resource": o.resource}
        if isinstance(o, AnyUrl):
            return {"url": str(o)}  # Convert AnyUrl to string and return as dict
        # Fall back to default serialization
        return super().default(o)


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
            resource = self._run_coroutine(self.mcp_server.read_resource(uri))  # type: ignore
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
            result = self._run_coroutine(self.mcp_server.call_tool(name, arguments))  # type: ignore
            self._send_json_response(result)
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            self.send_error(500, str(e))

    def _send_json_response(self, data: Any) -> None:
        """Send a JSON response."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, cls=McpJSONEncoder).encode())

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
        self.server: ThreadedHTTPServer = None  # type: ignore
        self.server_thread: threading.Thread = None  # type: ignore

        # Enable debug mode for tests
        self.debug = config["server"].get("debug", False)
        if self.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("HTTP transport debug mode enabled")

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

            # Create and start the HTTP server with retries
            max_retries = 5
            retry_delay = 1.0

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_retries} to start HTTP server on {self.host}:{self.port}")

                    # Log more details about the host and port
                    logger.info(f"Using host: '{self.host}', port: {self.port}, type: {type(self.port)}")

                    # Set socket options to allow reuse of the address
                    ThreadedHTTPServer.allow_reuse_address = True  # Set at class level before instantiation
                    self.server = ThreadedHTTPServer((self.host, self.port), McpHttpHandler)

                    # Log server creation success
                    logger.info("HTTP server object created successfully")

                    self.server_thread = threading.Thread(target=self.server.serve_forever)
                    self.server_thread.daemon = True
                    self.server_thread.start()

                    # Wait a moment to ensure the server started successfully
                    logger.info("Waiting for server thread to start...")
                    await asyncio.sleep(1)

                    if self.server_thread.is_alive():
                        logger.info(f"HTTP server successfully started on {self.host}:{self.port}")
                        break
                    else:
                        logger.error("Server thread is not alive after starting")
                except OSError as e:
                    if attempt < max_retries:
                        logger.warning(f"Failed to start HTTP server (attempt {attempt}/{max_retries}): {e}")
                        # Try to close any partially created server
                        if self.server:
                            try:
                                logger.info("Closing partially created server")
                                self.server.server_close()
                            except Exception as close_error:
                                logger.error(f"Error closing server: {close_error}")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to start HTTP server after {max_retries} attempts: {e}")
                        raise

            # Keep the main thread running
            while True:
                await asyncio.sleep(1)

                # Check if the server thread is still alive
                if not self.server_thread.is_alive():
                    logger.error("HTTP server thread died unexpectedly")
                    break
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
