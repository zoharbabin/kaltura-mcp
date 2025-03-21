"""
Tests for the server integration with the transport interface.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kaltura_mcp.server import KalturaMcpServer
from kaltura_mcp.transport.base import McpTransport


class MockTransport(McpTransport):
    """Mock transport for testing."""

    def __init__(self, config):
        """Initialize the mock transport."""
        super().__init__(config)
        self.initialize_called = False
        self.run_called = False
        self.run_args = None

    async def initialize(self):
        """Initialize the mock transport."""
        await super().initialize()
        self.initialize_called = True

    async def run(self, server):
        """Run the mock transport."""
        self.run_called = True
        self.run_args = (server,)


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config._raw_data = {
        "server": {
            "transport": "stdio",
            "host": "localhost",
            "port": 8000,
        }
    }
    return config


@pytest.fixture
def mock_kaltura_client():
    """Create a mock Kaltura client."""
    client = AsyncMock()
    client.initialize = AsyncMock()
    return client


@pytest.mark.asyncio
@patch("kaltura_mcp.server.TransportFactory")
async def test_server_creates_transport(mock_factory, mock_config):
    """Test that the server creates a transport instance."""
    # Create a mock transport
    mock_transport = MockTransport(mock_config._raw_data)
    mock_factory.create_transport.return_value = mock_transport

    # Create the server
    server = KalturaMcpServer(mock_config)

    # Verify that the factory was called with the correct arguments
    mock_factory.create_transport.assert_called_once_with(mock_config._raw_data)

    # Verify that the transport was set on the server
    assert server.transport == mock_transport


@pytest.mark.asyncio
@patch("kaltura_mcp.server.TransportFactory")
@patch("kaltura_mcp.kaltura.client.KalturaClientWrapper")
async def test_server_initializes_transport(mock_client_class, mock_factory, mock_config):
    """Test that the server initializes the transport."""
    # Create a mock transport
    mock_transport = MockTransport(mock_config._raw_data)
    mock_factory.create_transport.return_value = mock_transport

    # Create a mock client
    mock_client = AsyncMock()
    mock_client_class.return_value = mock_client

    # Create and initialize the server
    server = KalturaMcpServer(mock_config)
    await server.initialize()

    # Verify that the transport was initialized
    assert mock_transport.initialize_called


@pytest.mark.asyncio
@patch("kaltura_mcp.server.TransportFactory")
@patch("kaltura_mcp.kaltura.client.KalturaClientWrapper")
async def test_server_runs_transport(mock_client_class, mock_factory, mock_config):
    """Test that the server runs the transport."""
    # Create a mock transport
    mock_transport = MockTransport(mock_config._raw_data)
    mock_factory.create_transport.return_value = mock_transport

    # Create a mock client
    mock_client = AsyncMock()
    mock_client_class.return_value = mock_client

    # Create and initialize the server
    server = KalturaMcpServer(mock_config)
    await server.initialize()

    # Run the server
    await server.run()

    # Verify that the transport was run with the correct arguments
    assert mock_transport.run_called
    assert mock_transport.run_args[0] == server.app
