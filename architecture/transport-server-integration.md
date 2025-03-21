# Server Integration Implementation

This document provides the detailed implementation for integrating the transport system with the Kaltura MCP server.

## File: `kaltura_mcp/server.py` (Updated)

```python
#!/usr/bin/env python3
"""
Kaltura MCP Server main module.
"""
import logging
from typing import Any, Dict, List, Union

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server

from kaltura_mcp.config import load_config
from kaltura_mcp.transport import TransportFactory

logger = logging.getLogger(__name__)


class KalturaMcpServer:
    """Main server class for Kaltura-MCP."""

    def __init__(self, config: Any) -> None:
        """Initialize the server with configuration."""
        self.config = config
        self.app: Server = Server("kaltura-mcp-server")
        self.kaltura_client: Any = None
        self.tool_handlers: Dict[str, Any] = {}
        self.resource_handlers: Dict[str, Any] = {}
        self.transport = TransportFactory.create_transport(config._raw_data)

    async def initialize(self) -> None:
        """Initialize the server components."""
        # Initialize Kaltura client
        from kaltura_mcp.kaltura.client import KalturaClientWrapper

        self.kaltura_client = KalturaClientWrapper(self.config)
        await self.kaltura_client.initialize()

        # Register tool handlers
        self._register_tool_handlers()

        # Register resource handlers
        self._register_resource_handlers()
        
        # Initialize transport
        await self.transport.initialize()

        logger.info("Kaltura MCP Server initialized")

    def _register_tool_handlers(self) -> None:
        """Register all tool handlers."""
        # Import tool handlers
        from kaltura_mcp.tools.category import (
            CategoryAddToolHandler,
            CategoryDeleteToolHandler,
            CategoryGetToolHandler,
            CategoryListToolHandler,
            CategoryUpdateToolHandler,
        )
        from kaltura_mcp.tools.enhanced_media import EnhancedMediaUploadToolHandler
        from kaltura_mcp.tools.media import (
            MediaDeleteToolHandler,
            MediaGetToolHandler,
            MediaListToolHandler,
            MediaUpdateToolHandler,
        )
        from kaltura_mcp.tools.user import (
            UserAddToolHandler,
            UserDeleteToolHandler,
            UserGetToolHandler,
            UserListToolHandler,
            UserUpdateToolHandler,
        )

        # Register media tools
        self.tool_handlers["kaltura.media.list"] = MediaListToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.media.get"] = MediaGetToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.media.upload"] = EnhancedMediaUploadToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.media.update"] = MediaUpdateToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.media.delete"] = MediaDeleteToolHandler(self.kaltura_client)

        # Register category tools
        self.tool_handlers["kaltura.category.list"] = CategoryListToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.category.get"] = CategoryGetToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.category.add"] = CategoryAddToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.category.update"] = CategoryUpdateToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.category.delete"] = CategoryDeleteToolHandler(self.kaltura_client)

        # Register user tools
        self.tool_handlers["kaltura.user.list"] = UserListToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.user.get"] = UserGetToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.user.add"] = UserAddToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.user.update"] = UserUpdateToolHandler(self.kaltura_client)
        self.tool_handlers["kaltura.user.delete"] = UserDeleteToolHandler(self.kaltura_client)

        logger.info(f"Registered {len(self.tool_handlers)} tool handlers")

    def _register_resource_handlers(self) -> None:
        """Register all resource handlers."""
        # Import resource handlers
        from kaltura_mcp.resources.category import (
            CategoryListResourceHandler,
            CategoryResourceHandler,
        )
        from kaltura_mcp.resources.media import MediaEntryResourceHandler, MediaListResourceHandler
        from kaltura_mcp.resources.user import UserListResourceHandler, UserResourceHandler

        # Register media resources
        self.resource_handlers["media_entry"] = MediaEntryResourceHandler(self.kaltura_client)
        self.resource_handlers["media_list"] = MediaListResourceHandler(self.kaltura_client)

        # Register category resources
        self.resource_handlers["category"] = CategoryResourceHandler(self.kaltura_client)
        self.resource_handlers["category_list"] = CategoryListResourceHandler(self.kaltura_client)

        # Register user resources
        self.resource_handlers["user"] = UserResourceHandler(self.kaltura_client)
        self.resource_handlers["user_list"] = UserListResourceHandler(self.kaltura_client)

        logger.info(f"Registered {len(self.resource_handlers)} resource handlers")

    async def run(self) -> None:
        """Run the server."""
        # Register MCP handlers

        # Register handlers directly

        # List tools handler
        async def list_tools_handler() -> List[types.Tool]:
            """List all available tools."""
            return [handler.get_tool_definition() for handler in self.tool_handlers.values()]

        # Call tool handler
        async def call_tool_handler(
            name: str, arguments: Dict[str, Any]
        ) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
            """Call a tool with the given name and arguments."""
            if name not in self.tool_handlers:
                raise ValueError(f"Unknown tool: {name}")

            handler = self.tool_handlers[name]
            return await handler.handle(arguments)  # type: ignore

        # List resources handler
        async def list_resources_handler() -> List[types.Resource]:
            """List all available resources."""
            return [handler.get_resource_definition() for handler in self.resource_handlers.values()]

        # Read resource handler
        async def read_resource_handler(uri: str) -> Union[str, bytes]:
            """Read a resource with the given URI."""
            # Find the appropriate handler based on URI pattern
            for handler in self.resource_handlers.values():
                if handler.matches_uri(uri):
                    return await handler.handle(uri)  # type: ignore

            raise ValueError(f"Unknown resource: {uri}")

        # Register handlers with the app
        self.app.list_tools = list_tools_handler  # type: ignore
        self.app.call_tool = call_tool_handler  # type: ignore
        self.app.list_resources = list_resources_handler  # type: ignore
        self.app.read_resource = read_resource_handler  # type: ignore

        logger.info("Starting Kaltura MCP Server")

        # Run the server using the configured transport
        await self.transport.run(self.app)


def main() -> None:
    """Main entry point for the server."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Load configuration
    config = load_config()

    # Create and run server
    server = KalturaMcpServer(config)

    async def run_server() -> None:
        await server.initialize()
        await server.run()

    anyio.run(run_server)


if __name__ == "__main__":
    main()
```

## Key Changes

The main changes to the server implementation are:

1. **Import Transport Factory**: Import the `TransportFactory` class from the `kaltura_mcp.transport` module.

2. **Create Transport Instance**: In the `__init__` method, create a transport instance using the `TransportFactory`.

3. **Initialize Transport**: In the `initialize` method, call the transport's `initialize` method.

4. **Use Transport**: In the `run` method, use the transport's `run` method instead of directly using the STDIO transport.

## How the Integration Works

The server integration works as follows:

1. The server creates a transport instance based on the configuration
2. The server initializes the transport during its own initialization
3. The server registers its handlers with the MCP app
4. The server runs the transport, passing the MCP app to it
5. The transport handles the communication between clients and the MCP app

This approach provides several benefits:
- The server doesn't need to know the details of the transport mechanism
- Different transports can be used without changing the server code
- The server can focus on its core functionality

## Configuration

The server uses the configuration to determine which transport to use. The configuration is loaded from a file and/or environment variables, and passed to the `TransportFactory` to create the appropriate transport instance.

Example configuration:

```yaml
server:
  transport: "stdio"  # Options: stdio, http, sse
  host: "0.0.0.0"     # Used for HTTP and SSE transports
  port: 8000          # Used for HTTP and SSE transports
  debug: false        # Enable debug mode
```

## Error Handling

The server handles errors as follows:

1. If an error occurs during transport initialization, it is logged and propagated
2. If an error occurs during transport execution, it is logged and propagated
3. The transport is responsible for handling communication-specific errors

This approach ensures that errors are properly logged and handled at the appropriate level.

## Lifecycle Management

The server manages the lifecycle of the transport as follows:

1. The server creates the transport instance during its own initialization
2. The server initializes the transport during its own initialization
3. The server runs the transport during its own run method
4. The transport is responsible for its own shutdown

This approach ensures that the transport is properly initialized and shut down along with the server.

## Testing

The server integration can be tested as follows:

1. Unit tests to verify that the server creates and uses the transport correctly
2. Integration tests to verify that the server works with different transports
3. End-to-end tests to verify that clients can communicate with the server using different transports

Example test:

```python
async def test_server_with_transport():
    """Test server with a specific transport."""
    # Create a mock transport
    mock_transport = MockTransport()
    
    # Create a server with the mock transport
    server = KalturaMcpServer(config)
    server.transport = mock_transport
    
    # Initialize and run the server
    await server.initialize()
    await server.run()
    
    # Verify that the transport was used correctly
    assert mock_transport.initialize_called
    assert mock_transport.run_called
    assert mock_transport.run_args[0] == server.app