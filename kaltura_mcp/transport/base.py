"""
Base transport interface for Kaltura MCP Server.
"""

import abc
import logging
from typing import Any, Dict

from mcp.server.lowlevel import Server

logger = logging.getLogger(__name__)


class McpTransport(abc.ABC):
    """Base interface for MCP transport mechanisms."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the transport with configuration.

        Args:
            config: Server configuration dictionary
        """
        self.config = config

    async def initialize(self) -> None:
        """Initialize the transport."""
        logger.info(f"Initializing {self.__class__.__name__}")

    @abc.abstractmethod
    async def run(self, server: Server) -> None:
        """
        Run the transport with the given server.

        Args:
            server: The MCP server instance
        """
        raise NotImplementedError("Transport must implement run method")

    async def shutdown(self) -> None:
        """Shutdown the transport."""
        logger.info(f"Shutting down {self.__class__.__name__}")
