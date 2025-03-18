"""
Pytest configuration and fixtures for integration tests.
"""
import pytest
import pytest_asyncio
import os
import json
import yaml
import logging
import sys

from kaltura_mcp.server import KalturaMcpServer
from kaltura_mcp.config import Config, KalturaConfig, ServerConfig, LoggingConfig, ContextConfig
from tests.integration.enhanced_client import EnhancedKalturaClientWrapper

# Configure logging for API calls
api_logger = logging.getLogger("kaltura_api_calls")
api_logger.setLevel(logging.INFO)

# Create console handler with a higher log level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
api_logger.addHandler(console_handler)
api_logger.propagate = False  # Prevent duplicate logging

def load_integration_config():
    """
    Load integration test configuration with priority for environment variables.
    This ensures sensitive data like secrets come from environment variables
    rather than config files.
    """
    # Determine config file path
    config_path = os.environ.get("KALTURA_MCP_TEST_CONFIG", "tests/integration/config.json")
    
    # Default config structure
    config_data = {
        "kaltura": {
            "partner_id": 0,
            "admin_secret": "",
            "user_id": "admin",
            "service_url": "https://www.kaltura.com/api_v3"
        },
        "server": {
            "log_level": "INFO",
            "transport": "stdio",
            "port": 8000,
            "host": "127.0.0.1",
            "debug": False
        },
        "logging": {
            "level": "INFO",
            "file": "kaltura-mcp-test.log"
        },
        "context": {
            "default_strategy": "pagination",
            "max_entries": 100,
            "max_context_size": 10000
        }
    }
    
    # Load from config file if it exists (for non-sensitive settings)
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                file_data = yaml.safe_load(f) or {}
            elif config_path.endswith('.json'):
                file_data = json.load(f)
            else:
                # Default to YAML for unknown extensions
                file_data = yaml.safe_load(f) or {}
            
            # Update config with file data (except sensitive fields that will come from env vars)
            if "server" in file_data:
                config_data["server"].update(file_data["server"])
            if "logging" in file_data:
                config_data["logging"].update(file_data["logging"])
            if "context" in file_data:
                config_data["context"].update(file_data["context"])
            
            # For kaltura section, only update non-sensitive fields from file
            if "kaltura" in file_data:
                if "service_url" in file_data["kaltura"]:
                    config_data["kaltura"]["service_url"] = file_data["kaltura"]["service_url"]
                if "user_id" in file_data["kaltura"]:
                    config_data["kaltura"]["user_id"] = file_data["kaltura"]["user_id"]
    
    # Create config objects
    kaltura_config = KalturaConfig(
        # Always prioritize environment variables for sensitive data
        partner_id=int(os.environ.get("KALTURA_PARTNER_ID", config_data["kaltura"]["partner_id"])),
        admin_secret=os.environ.get("KALTURA_ADMIN_SECRET", config_data["kaltura"]["admin_secret"]),
        user_id=os.environ.get("KALTURA_USER_ID", config_data["kaltura"]["user_id"]),
        service_url=os.environ.get("KALTURA_SERVICE_URL", config_data["kaltura"]["service_url"]),
    )
    
    server_data = config_data["server"]
    server_config = ServerConfig(
        log_level=os.environ.get("KALTURA_MCP_LOG_LEVEL", server_data["log_level"]),
        transport=os.environ.get("KALTURA_MCP_TRANSPORT", server_data["transport"]),
        port=int(os.environ.get("KALTURA_MCP_PORT", server_data["port"])),
        host=os.environ.get("KALTURA_MCP_HOST", server_data["host"]),
        debug=os.environ.get("KALTURA_MCP_DEBUG", "").lower() in ("true", "1", "yes") if "KALTURA_MCP_DEBUG" in os.environ else server_data["debug"],
    )
    
    logging_data = config_data["logging"]
    logging_config = LoggingConfig(
        level=os.environ.get("KALTURA_MCP_LOG_LEVEL", logging_data["level"]),
        file=os.environ.get("KALTURA_MCP_LOG_FILE", logging_data["file"]),
    )
    
    context_data = config_data["context"]
    context_config = ContextConfig(
        default_strategy=os.environ.get("KALTURA_MCP_CONTEXT_STRATEGY", context_data["default_strategy"]),
        max_entries=int(os.environ.get("KALTURA_MCP_MAX_ENTRIES", context_data["max_entries"])),
        max_context_size=int(os.environ.get("KALTURA_MCP_MAX_CONTEXT_SIZE", context_data["max_context_size"])),
    )
    
    # Create the config object
    config = Config(
        kaltura=kaltura_config,
        server=server_config,
        logging=logging_config,
        context=context_config,
    )
    
    # Store the raw data for custom field access
    config._raw_data = config_data
    
    # Validate required fields are present from environment variables
    if kaltura_config.partner_id <= 0:
        raise ValueError("KALTURA_PARTNER_ID environment variable must be set and > 0")
    
    if not kaltura_config.admin_secret:
        raise ValueError("KALTURA_ADMIN_SECRET environment variable must be set")
    
    return config

@pytest_asyncio.fixture(scope="class")
async def integration_config():
    """Load integration test configuration."""
    try:
        return load_integration_config()
    except Exception as e:
        pytest.skip(f"Invalid integration test config: {e}")

@pytest_asyncio.fixture(scope="class")
async def kaltura_client(integration_config):
    """Create a real Kaltura client for integration testing with enhanced logging."""
    api_logger.info("Creating enhanced Kaltura client for integration testing")
    client = EnhancedKalturaClientWrapper(integration_config)
    await client.initialize()
    api_logger.info(f"Kaltura client initialized with service URL: {client.get_service_url()}")
    api_logger.info(f"Using partner ID: {integration_config.kaltura.partner_id}")
    yield client
    # No cleanup needed as the session will expire
    api_logger.info("Kaltura client session completed")

@pytest_asyncio.fixture(scope="class")
async def server(integration_config):
    """Create a server instance with real Kaltura client."""
    api_logger.info("Creating KalturaMcpServer for integration testing")
    
    # Create server with custom client
    server = KalturaMcpServer(integration_config)
    
    # Replace the default client with our enhanced client
    enhanced_client = EnhancedKalturaClientWrapper(integration_config)
    await enhanced_client.initialize()
    server.kaltura_client = enhanced_client
    
    # Initialize server with our enhanced client
    api_logger.info("Initializing server components")
    await server.initialize()
    api_logger.info(f"Server initialized with {len(server.tool_handlers)} tools and {len(server.resource_handlers)} resources")
    
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