"""
STDIO transport implementation for Kaltura MCP Server.
"""

import asyncio
import logging
from typing import Any, Dict

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


class StdioTransport(McpTransport):
    """STDIO-based transport for MCP."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the STDIO transport.

        Args:
            config: Server configuration dictionary
        """
        super().__init__(config)

    async def run(self, server: Server) -> None:
        """
        Run the server using STDIO transport.

        Args:
            server: The MCP server instance
        """
        logger.info("Starting server with STDIO transport")

        try:
            # Set up error handling and retry logic
            max_retries = 3
            retry_delay = 1.0

            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_retries} to start STDIO transport")

                    async with stdio_server() as streams:
                        # Set up a task to monitor the server
                        async def monitor_server() -> None:
                            # Wait a moment to ensure the server started successfully
                            await asyncio.sleep(1)
                            logger.info("STDIO transport successfully started")

                        # Start the monitor task
                        monitor_task = asyncio.create_task(monitor_server())

                        # Run the server
                        await server.run(streams[0], streams[1], server.create_initialization_options())

                        # If we get here, the server has stopped
                        monitor_task.cancel()
                        break

                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(f"Failed to start STDIO transport (attempt {attempt}/{max_retries}): {e}")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to start STDIO transport after {max_retries} attempts: {e}")
                        raise
        except Exception as e:
            logger.error(f"Error running server with STDIO transport: {e}")
            raise
