"""
Pytest configuration and fixtures.
"""

import importlib.metadata
import sys
from unittest.mock import AsyncMock

import pytest

from kaltura_mcp.config import Config, KalturaConfig, ServerConfig


# Mock sse_starlette module to avoid import error
class MockEventSourceResponse:
    def __init__(self, *args, **kwargs):
        pass


class MockSseStarlette:
    EventSourceResponse = MockEventSourceResponse


sys.modules["sse_starlette"] = MockSseStarlette()


# Mock importlib.metadata to avoid version error
class MockImportlibMetadata:
    @staticmethod
    def version(name):
        return "1.0.0"


importlib.metadata.version = MockImportlibMetadata.version


@pytest.fixture
def server_config():
    """Create a test server configuration."""
    kaltura_config = KalturaConfig(
        partner_id=123,
        admin_secret="test_secret",
        user_id="test_user",
        service_url="https://example.com",
    )
    server_config = ServerConfig(log_level="INFO", transport="stdio", port=8000)
    return Config(kaltura=kaltura_config, server=server_config)


@pytest.fixture
def mock_kaltura_client():
    """Create a mock Kaltura client."""
    client = AsyncMock()
    client.execute_request = AsyncMock()
    return client
