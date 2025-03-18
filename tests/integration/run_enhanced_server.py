#!/usr/bin/env python
"""
Script to run the enhanced MCP server for testing.

This script starts an enhanced MCP server that provides detailed logging
of how client requests are translated into Kaltura API calls.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.integration.conftest import load_integration_config

# Import the enhanced server
from tests.integration.enhanced_server import EnhancedKalturaMcpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("run_enhanced_server")

# Configure specific loggers
for logger_name in ["mcp_server_flow", "kaltura_api_calls"]:
    log = logging.getLogger(logger_name)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.propagate = False


async def run_server():
    """Run the enhanced MCP server."""
    logger.info("Starting enhanced MCP server")

    try:
        # Load configuration
        config = load_integration_config()

        # Override transport to use HTTP for easier testing
        config.server.transport = "http"
        config.server.port = 8765
        config.server.debug = True

        logger.info(f"Loaded configuration with partner ID: {config.kaltura.partner_id}")
        logger.info(f"Server will run on http://{config.server.host}:{config.server.port}")

        # Create and initialize server
        server = EnhancedKalturaMcpServer(config)
        await server.initialize()

        # Run server
        await server.run()

    except Exception as e:
        logger.error(f"Error running server: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
