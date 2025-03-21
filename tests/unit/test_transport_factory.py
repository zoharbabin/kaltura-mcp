"""
Tests for the transport factory.
"""

import pytest

from kaltura_mcp.transport import TransportFactory
from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.stdio import StdioTransport


def test_create_stdio_transport():
    """Test creating a STDIO transport."""
    config = {
        "server": {
            "transport": "stdio",
            "host": "localhost",
            "port": 8000,
        }
    }

    transport = TransportFactory.create_transport(config)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, StdioTransport)


def test_create_http_transport():
    """Test creating an HTTP transport."""
    config = {
        "server": {
            "transport": "http",
            "host": "localhost",
            "port": 8000,
        }
    }

    transport = TransportFactory.create_transport(config)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, HttpTransport)
    assert transport.host == "localhost"
    assert transport.port == 8000


def test_create_sse_transport():
    """Test creating an SSE transport."""
    config = {
        "server": {
            "transport": "sse",
            "host": "localhost",
            "port": 8000,
        }
    }

    transport = TransportFactory.create_transport(config)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, SseTransport)
    assert transport.host == "localhost"
    assert transport.port == 8000


def test_create_default_transport():
    """Test creating a transport with no transport type specified."""
    config = {
        "server": {
            "host": "localhost",
            "port": 8000,
        }
    }

    transport = TransportFactory.create_transport(config)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, StdioTransport)


def test_create_transport_with_empty_config():
    """Test creating a transport with an empty config."""
    config = {}

    transport = TransportFactory.create_transport(config)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, StdioTransport)


def test_create_transport_with_none_config():
    """Test creating a transport with None config."""
    transport = TransportFactory.create_transport(None)

    assert isinstance(transport, McpTransport)
    assert isinstance(transport, StdioTransport)


def test_create_unsupported_transport():
    """Test creating an unsupported transport."""
    config = {
        "server": {
            "transport": "unsupported",
            "host": "localhost",
            "port": 8000,
        }
    }

    with pytest.raises(ValueError) as excinfo:
        TransportFactory.create_transport(config)

    assert "Unsupported transport type: unsupported" in str(excinfo.value)
