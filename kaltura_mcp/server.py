#!/usr/bin/env python3
"""
Kaltura MCP Server main module.
"""
import logging
from typing import Any, Dict, List, Union, Optional, Callable, Coroutine

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from kaltura_mcp.config import load_config

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

        # Run the server using stdio transport
        async with stdio_server() as streams:
            await self.app.run(streams[0], streams[1], self.app.create_initialization_options())


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
