"""
Pytest configuration and fixtures for integration tests.
"""
import pytest
import pytest_asyncio
import os
import json

from kaltura_mcp.server import KalturaMcpServer
from kaltura_mcp.config import Config, KalturaConfig, ServerConfig
from kaltura_mcp.kaltura.client import KalturaClientWrapper

@pytest_asyncio.fixture
async def integration_config():
    """Load integration test configuration."""
    try:
        with open("tests/integration/config.json", "r") as f:
            config_data = json.load(f)
            
        kaltura_config = KalturaConfig(
            partner_id=config_data["partner_id"],
            admin_secret=config_data["admin_secret"],
            user_id=config_data["user_id"],
            service_url=config_data["service_url"]
        )
        server_config = ServerConfig(
            log_level="INFO",
            transport="stdio",
            port=8000
        )
        return Config(kaltura=kaltura_config, server=server_config)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        pytest.skip(f"Invalid integration test config: {e}")

@pytest_asyncio.fixture
async def kaltura_client(integration_config):
    """Create a real Kaltura client for integration testing."""
    client = KalturaClientWrapper(integration_config)
    await client.initialize()
    yield client
    # No cleanup needed as the session will expire

@pytest_asyncio.fixture
async def server(integration_config):
    """Create a server instance with real Kaltura client."""
    server = KalturaMcpServer(integration_config)
    await server.initialize()
    
    # Register handlers manually since we're not calling run()
    async def list_tools_handler():
        return [handler.get_tool_definition() for handler in server.tool_handlers.values()]
    
    async def call_tool_handler(name, arguments):
        if name not in server.tool_handlers:
            raise ValueError(f"Unknown tool: {name}")
        
        handler = server.tool_handlers[name]
        return await handler.handle(arguments)
    
    async def list_resources_handler():
        return [handler.get_resource_definition() for handler in server.resource_handlers.values()]
    
    async def read_resource_handler(uri):
        for handler in server.resource_handlers.values():
            if handler.matches_uri(uri):
                return await handler.handle(uri)
        
        raise ValueError(f"Unknown resource: {uri}")
    
    server.app.list_tools = list_tools_handler
    server.app.call_tool = call_tool_handler
    server.app.list_resources = list_resources_handler
    server.app.read_resource = read_resource_handler
    
    return server