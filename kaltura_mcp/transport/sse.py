"""
Server-Sent Events (SSE) transport implementation for Kaltura MCP Server.

Note: The SSE transport has known stability issues in test environments.
These issues are primarily related to connection handling and event streaming.
For production use, consider using HTTP transport instead until these issues are resolved.
"""

import asyncio
import json
import logging
import signal
from typing import Any, AsyncGenerator, Dict, Set

import uvicorn
from mcp.server.lowlevel import Server
from mcp.types import EmbeddedResource, ImageContent, Resource, TextContent, Tool
from pydantic.networks import AnyUrl
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


# Set up signal handlers to properly clean up the event loop
def handle_sigterm(*args: Any) -> None:
    """Handle SIGTERM signal."""
    logger.info("Received SIGTERM signal, shutting down")
    # Get the current event loop
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            # Stop the event loop
            loop.stop()
    except Exception as e:
        logger.error(f"Error stopping event loop: {e}")

    # Don't call sys.exit() in a library, as it will terminate the entire process
    # including any tests that might be running


# Only register signal handlers when running as a standalone server, not during tests
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)


class McpJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MCP objects."""

    def default(self, obj: Any) -> Dict[str, Any]:
        """Handle MCP objects."""
        if isinstance(obj, Tool):
            return {
                "name": obj.name,
                "description": obj.description,
                "input_schema": obj.inputSchema,  # Use camelCase as per mcp.types.Tool
            }
        elif isinstance(obj, Resource):
            return {
                "uri": str(obj.uri),  # Convert AnyUrl to string
                "name": obj.name,
                "description": obj.description,
                "mime_type": obj.mimeType,  # Use camelCase as per mcp.types.Resource
            }
        elif isinstance(obj, TextContent):
            return {"type": obj.type, "text": obj.text}
        elif isinstance(obj, ImageContent):
            return {"type": obj.type, "data": obj.data, "mimeType": obj.mimeType}
        elif isinstance(obj, EmbeddedResource):
            return {"type": obj.type, "resource": obj.resource}
        elif isinstance(obj, AnyUrl):
            return {"url": str(obj)}  # Convert AnyUrl to string and return as dict
        return super().default(obj)  # type: ignore


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
        self.app: Starlette = None  # type: ignore
        self.server_instance: uvicorn.Server = None  # type: ignore
        self.mcp_server: Server = None  # type: ignore
        self.active_connections: Set[int] = set()

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

            # Run the server with retries
            max_retries = 5
            retry_delay = 1.0

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_retries} to start SSE server on {self.host}:{self.port}")

                    # Configure the server with a reasonable timeout
                    config = uvicorn.Config(
                        self.app,
                        host=self.host,
                        port=self.port,
                        log_level="info",
                        timeout_keep_alive=30,  # Shorter keep-alive timeout to avoid hanging
                        limit_concurrency=100,  # Limit concurrent connections
                        timeout_graceful_shutdown=10,  # Faster graceful shutdown
                        reload=False,  # Disable auto-reload
                        workers=1,  # Use only one worker for testing
                    )

                    # Create a server instance with the configuration
                    self.server_instance = uvicorn.Server(config)

                    # Set up a task to monitor the server
                    async def monitor_server() -> None:
                        try:
                            # Wait a moment to ensure the server started successfully
                            await asyncio.sleep(2)
                            logger.info(f"SSE server successfully started on {self.host}:{self.port}")

                            # Keep monitoring the server
                            while True:
                                try:
                                    await asyncio.sleep(5)
                                    if not self.server_instance.started:
                                        logger.error("SSE server stopped unexpectedly")
                                        break
                                except asyncio.CancelledError:
                                    # Handle cancellation during sleep
                                    logger.info("Monitor task sleep cancelled")
                                    raise
                        except asyncio.CancelledError:
                            logger.info("Monitor task cancelled")
                            # Don't re-raise, just exit cleanly
                            return
                        except Exception as e:
                            logger.error(f"Error in monitor task: {e}")

                    # Start the monitor task
                    monitor_task = asyncio.create_task(monitor_server())

                    # Start the server
                    try:
                        await self.server_instance.serve()
                    except asyncio.CancelledError:
                        logger.info("SSE server task cancelled")
                        # Properly clean up the server
                        if hasattr(self.server_instance, "shutdown"):
                            try:
                                await asyncio.wait_for(self.server_instance.shutdown(), timeout=1.0)
                            except (asyncio.TimeoutError, Exception):
                                pass
                        raise
                    except Exception as serve_error:
                        logger.error(f"Error in SSE server.serve(): {serve_error}")
                        raise

                    # If we get here, the server has stopped
                    monitor_task.cancel()
                    try:
                        # Use wait_for with a timeout to avoid hanging
                        await asyncio.wait_for(asyncio.shield(monitor_task), timeout=1.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        # Either the task was cancelled or it timed out, both are fine
                        pass
                    break

                except OSError as e:
                    if attempt < max_retries:
                        logger.warning(f"Failed to start SSE server (attempt {attempt}/{max_retries}): {e}")
                        # Make sure any resources are cleaned up
                        if hasattr(self.server_instance, "shutdown"):
                            try:
                                await self.server_instance.shutdown()
                            except Exception:
                                pass
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to start SSE server after {max_retries} attempts: {e}")
                        raise
        except Exception as e:
            logger.error(f"Error running server with SSE transport: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the SSE server."""
        await super().shutdown()

        if self.server_instance:
            logger.info("Shutting down SSE server")
            try:
                # Use wait_for with a timeout to avoid hanging
                await asyncio.wait_for(self.server_instance.shutdown(), timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("SSE server shutdown timed out")
            except Exception as e:
                logger.error(f"Error shutting down SSE server: {e}")

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
            # Manually serialize with our custom encoder
            tools_json = json.loads(json.dumps({"tools": tools}, cls=McpJSONEncoder))
            return JSONResponse(tools_json)
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _handle_list_resources(self, request: Request) -> JSONResponse:
        """Handle list resources endpoint."""
        if not self.mcp_server:
            return JSONResponse({"error": "Server not initialized"}, status_code=500)

        try:
            resources = await self.mcp_server.list_resources()
            # Manually serialize with our custom encoder
            resources_json = json.loads(json.dumps({"resources": resources}, cls=McpJSONEncoder))
            return JSONResponse(resources_json)
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

            resource = await self.mcp_server.read_resource(uri)  # type: ignore
            # Manually serialize with our custom encoder
            resource_json = json.loads(json.dumps(resource, cls=McpJSONEncoder))
            return JSONResponse(resource_json)
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

            result = await self.mcp_server.call_tool(name, arguments)  # type: ignore

            # Notify all connected clients about the tool call
            await self._notify_clients({"event": "tool_called", "data": {"name": name, "arguments": arguments}})

            # Manually serialize with our custom encoder
            result_json = json.loads(json.dumps(result, cls=McpJSONEncoder))
            return JSONResponse(result_json)
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    async def _handle_sse_connection(self, request: Request) -> Response:
        """Handle SSE connection."""
        if not self.mcp_server:
            return Response("Server not initialized", status_code=500)

        connection_id = id(request)

        async def event_generator() -> AsyncGenerator[str, None]:
            """Generate SSE events."""
            # Add this connection to active connections
            self.active_connections.add(connection_id)

            try:
                # Send initial connection event
                yield f"event: connected\ndata: {json.dumps({'id': connection_id}, cls=McpJSONEncoder)}\n\n"

                # Keep the connection alive
                while True:
                    # Send a ping every 5 seconds to keep the connection alive
                    # but with a shorter timeout to avoid hanging tests
                    await asyncio.sleep(5)
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
        if not self.active_connections:
            logger.debug("No active connections to notify")
            return

        logger.info(f"Notifying {len(self.active_connections)} clients: {data}")

        # Create a shared event message
        event_data = json.dumps(data, cls=McpJSONEncoder)
        event_message = f"event: {data.get('event', 'message')}\ndata: {event_data}\n\n"

        # Store the message in a shared queue for each connection
        # Each connection's event generator will pick it up on the next iteration
        for connection_id in list(self.active_connections):
            try:
                # In a real implementation, we would use a proper message queue
                # or a shared state mechanism to deliver events to clients
                # For now, we'll just log that we would send the event
                logger.debug(f"Would send event to client {connection_id}: {event_message}")
            except Exception as e:
                logger.error(f"Error notifying client {connection_id}: {e}")
