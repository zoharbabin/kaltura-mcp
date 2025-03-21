"""
Integration tests for the transport factory and server integration.
"""

import pytest

from kaltura_mcp.config import load_config
from kaltura_mcp.server import KalturaMcpServer
from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.stdio import StdioTransport


class TestTransportFactoryIntegration:
    """Integration tests for the transport factory and server integration."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        try:
            # Try to load the default configuration
            config = load_config()
        except ValueError:
            # If validation fails, create a minimal valid configuration for testing
            from kaltura_mcp.config import Config, ContextConfig, KalturaConfig, LoggingConfig, ServerConfig

            config = Config(
                kaltura=KalturaConfig(
                    partner_id=12345,  # Test partner ID
                    admin_secret="test-secret",
                    user_id="test-user",
                    service_url="https://www.kaltura.com/api_v3",
                ),
                server=ServerConfig(host="localhost", port=8765, transport="stdio"),
                logging=LoggingConfig(level="INFO"),
                context=ContextConfig(default_strategy="pagination", max_entries=100, max_context_size=10000),
            )
            # Create raw data structure for direct manipulation
            config._raw_data = {
                "kaltura": {
                    "partner_id": 12345,
                    "admin_secret": "test-secret",
                    "user_id": "test-user",
                    "service_url": "https://www.kaltura.com/api_v3",
                },
                "server": {"host": "localhost", "port": 8765, "transport": "stdio"},
                "logging": {"level": "INFO"},
                "context": {"default_strategy": "pagination", "max_entries": 100, "max_context_size": 10000},
            }

        # Override with test-specific values
        config._raw_data["server"]["host"] = "localhost"
        config._raw_data["server"]["port"] = 8765  # Use a different port for tests
        return config

    @pytest.mark.asyncio
    async def test_stdio_transport_factory(self, config):
        """Test the STDIO transport factory integration."""
        # Set the transport type to STDIO
        config._raw_data["server"]["transport"] = "stdio"

        # Create the server
        server = KalturaMcpServer(config)

        # Check that the transport is a StdioTransport
        assert isinstance(server.transport, McpTransport)
        assert isinstance(server.transport, StdioTransport)

        # Check that the transport has the correct configuration
        assert server.transport.config["server"]["transport"] == "stdio"

    @pytest.mark.asyncio
    async def test_http_transport_factory(self, config):
        """Test the HTTP transport factory integration."""
        # Set the transport type to HTTP
        config._raw_data["server"]["transport"] = "http"

        # Create the server
        server = KalturaMcpServer(config)

        # Check that the transport is an HttpTransport
        assert isinstance(server.transport, McpTransport)
        assert isinstance(server.transport, HttpTransport)

        # Check that the transport has the correct configuration
        assert server.transport.config["server"]["transport"] == "http"
        assert server.transport.host == "localhost"
        assert server.transport.port == 8765

    @pytest.mark.asyncio
    async def test_sse_transport_factory(self, config):
        """Test the SSE transport factory integration."""
        # Set the transport type to SSE
        config._raw_data["server"]["transport"] = "sse"

        # Create the server
        server = KalturaMcpServer(config)

        # Check that the transport is an SseTransport
        assert isinstance(server.transport, McpTransport)
        assert isinstance(server.transport, SseTransport)

        # Check that the transport has the correct configuration
        assert server.transport.config["server"]["transport"] == "sse"
        assert server.transport.host == "localhost"
        assert server.transport.port == 8765

    @pytest.mark.asyncio
    async def test_empty_config_transport_factory(self, config):
        """Test the transport factory with an empty configuration."""
        # Create a server with an empty server configuration
        config._raw_data["server"] = {}
        server = KalturaMcpServer(config)

        # Check that the transport is a StdioTransport (default)
        assert isinstance(server.transport, McpTransport)
        assert isinstance(server.transport, StdioTransport)

    @pytest.mark.asyncio
    async def test_missing_config_transport_factory(self, config):
        """Test the transport factory with a missing server configuration."""
        # Create a server with a missing server configuration
        del config._raw_data["server"]
        server = KalturaMcpServer(config)

        # Check that the transport is a StdioTransport (default)
        assert isinstance(server.transport, McpTransport)
        assert isinstance(server.transport, StdioTransport)

    @pytest.mark.asyncio
    async def test_invalid_transport_type(self, config):
        """Test the transport factory with an invalid transport type."""
        # Set an invalid transport type
        config._raw_data["server"]["transport"] = "invalid"

        # Check that creating a server with an invalid transport type raises a ValueError
        with pytest.raises(ValueError, match="Unsupported transport type: invalid"):
            KalturaMcpServer(config)
