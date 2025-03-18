"""
Mock implementations for testing the Kaltura-MCP Server.

This package provides mock implementations of external dependencies
to enable testing without requiring real external services.
"""

from .mock_kaltura_api import MockKalturaAPI, MockKalturaClientWrapper

__all__ = ["MockKalturaAPI", "MockKalturaClientWrapper"]
