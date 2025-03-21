"""
Transport factory for Kaltura MCP Server.
"""

import logging
import os
from typing import Any, Dict, Optional

from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.stdio import StdioTransport

logger = logging.getLogger(__name__)


class TransportFactory:
    """Factory for creating transport instances."""

    @staticmethod
    def create_transport(config: Optional[Dict[str, Any]] = None) -> McpTransport:
        """
        Create a transport instance based on configuration.

        Args:
            config: Server configuration dictionary

        Returns:
            A transport instance

        Raises:
            ValueError: If the transport type is not supported
        """
        # Check for transport type in environment variable first
        env_transport = os.environ.get("KALTURA_MCP_TRANSPORT")

        # Handle empty or missing config
        if config is None or not config or "server" not in config:
            if env_transport:
                logger.info(f"Using transport from environment variable: {env_transport}")
                return TransportFactory._create_transport_by_type(env_transport, {"server": {"transport": env_transport}})
            else:
                logger.info("No server configuration found, using default STDIO transport")
                return StdioTransport({"server": {"transport": "stdio"}})

        # Use environment variable if set, otherwise use config
        if env_transport:
            transport_type = env_transport.lower()
            logger.info(f"Using transport from environment variable: {transport_type}")

            # Update the config with the transport type from environment
            config_copy = config.copy()
            if "server" in config_copy:
                server_config = config_copy["server"].copy()
                server_config["transport"] = transport_type
                config_copy["server"] = server_config
            else:
                config_copy["server"] = {"transport": transport_type}

            return TransportFactory._create_transport_by_type(transport_type, config_copy)
        else:
            transport_type = config["server"].get("transport", "stdio").lower()
            logger.info(f"Creating transport of type: {transport_type}")
            return TransportFactory._create_transport_by_type(transport_type, config)

    @staticmethod
    def _create_transport_by_type(transport_type: str, config: Dict[str, Any]) -> McpTransport:
        """Create a transport instance based on the transport type."""
        logger.info(f"Creating transport of type: {transport_type}")

        if transport_type == "stdio":
            return StdioTransport(config)
        elif transport_type == "http":
            return HttpTransport(config)
        elif transport_type == "sse":
            return SseTransport(config)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
