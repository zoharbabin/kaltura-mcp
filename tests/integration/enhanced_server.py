"""
Enhanced MCP server implementation for integration testing.

This module provides an enhanced version of the KalturaMcpServer that adds
detailed logging to show how client requests are translated into Kaltura API calls.
"""
import logging
import json
import time
import asyncio
from typing import Any, Dict, List, Optional

from kaltura_mcp.server import KalturaMcpServer
from tests.integration.enhanced_client import EnhancedKalturaClientWrapper
from mcp import types

# Configure logging
logger = logging.getLogger("mcp_server_flow")
logger.setLevel(logging.INFO)

class EnhancedKalturaMcpServer(KalturaMcpServer):
    """Enhanced MCP server with detailed logging of request translation."""
    
    async def initialize(self):
        """Initialize the server with enhanced client and logging."""
        logger.info("Initializing enhanced MCP server")
        
        # Create enhanced Kaltura client
        from tests.integration.enhanced_client import EnhancedKalturaClientWrapper
        self.kaltura_client = EnhancedKalturaClientWrapper(self.config)
        await self.kaltura_client.initialize()
        
        # Register tool handlers
        self._register_tool_handlers()
        
        # Register resource handlers
        self._register_resource_handlers()
        
        # Wrap handlers with logging
        self._wrap_handlers_with_logging()
        
        logger.info(f"Enhanced MCP server initialized with {len(self.tool_handlers)} tools and {len(self.resource_handlers)} resources")
    
    def _wrap_handlers_with_logging(self):
        """Wrap all handlers with logging to track request translation."""
        # Wrap tool handlers
        for name, handler in list(self.tool_handlers.items()):
            original_handle = handler.handle
            
            async def logged_handle(arguments, _original_handle=original_handle, _name=name):
                logger.info(f"MCP TOOL REQUEST: {_name} with arguments: {json.dumps(arguments, indent=2)}")
                start_time = time.time()
                try:
                    result = await _original_handle(arguments)
                    execution_time = time.time() - start_time
                    logger.info(f"MCP TOOL RESPONSE: {_name} completed in {execution_time:.2f}s")
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"MCP TOOL ERROR: {_name} failed after {execution_time:.2f}s: {e}")
                    raise
            
            handler.handle = logged_handle
        
        # Wrap resource handlers
        for name, handler in list(self.resource_handlers.items()):
            original_handle = handler.handle
            
            async def logged_handle(uri, _original_handle=original_handle, _name=name):
                logger.info(f"MCP RESOURCE REQUEST: {_name} for URI: {uri}")
                start_time = time.time()
                try:
                    result = await _original_handle(uri)
                    execution_time = time.time() - start_time
                    logger.info(f"MCP RESOURCE RESPONSE: {_name} completed in {execution_time:.2f}s")
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"MCP RESOURCE ERROR: {_name} failed after {execution_time:.2f}s: {e}")
                    raise
            
            handler.handle = logged_handle
    
    async def run(self):
        """Run the server with enhanced logging."""
        logger.info("Starting enhanced MCP server")
        
        # Register MCP handlers with logging
        
        # List tools handler
        async def list_tools_handler() -> list[types.Tool]:
            """List all available tools."""
            logger.info("MCP REQUEST: list_tools")
            tools = [handler.get_tool_definition() for handler in self.tool_handlers.values()]
            logger.info(f"MCP RESPONSE: list_tools returned {len(tools)} tools")
            return tools
        
        # Call tool handler
        async def call_tool_handler(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Call a tool with the given name and arguments."""
            logger.info(f"MCP REQUEST: call_tool {name} with arguments: {json.dumps(arguments, indent=2)}")
            start_time = time.time()
            
            if name not in self.tool_handlers:
                logger.error(f"MCP ERROR: Unknown tool: {name}")
                raise ValueError(f"Unknown tool: {name}")
            
            handler = self.tool_handlers[name]
            try:
                result = await handler.handle(arguments)
                execution_time = time.time() - start_time
                logger.info(f"MCP RESPONSE: call_tool {name} completed in {execution_time:.2f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"MCP ERROR: call_tool {name} failed after {execution_time:.2f}s: {e}")
                raise
        
        # List resources handler
        async def list_resources_handler() -> list[types.Resource]:
            """List all available resources."""
            logger.info("MCP REQUEST: list_resources")
            resources = [handler.get_resource_definition() for handler in self.resource_handlers.values()]
            logger.info(f"MCP RESPONSE: list_resources returned {len(resources)} resources")
            return resources
        
        # Read resource handler
        async def read_resource_handler(uri: str) -> str | bytes:
            """Read a resource with the given URI."""
            logger.info(f"MCP REQUEST: read_resource {uri}")
            start_time = time.time()
            
            # Find the appropriate handler based on URI pattern
            for handler in self.resource_handlers.values():
                if handler.matches_uri(uri):
                    try:
                        result = await handler.handle(uri)
                        execution_time = time.time() - start_time
                        logger.info(f"MCP RESPONSE: read_resource {uri} completed in {execution_time:.2f}s")
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        logger.error(f"MCP ERROR: read_resource {uri} failed after {execution_time:.2f}s: {e}")
                        raise
            
            logger.error(f"MCP ERROR: Unknown resource: {uri}")
            raise ValueError(f"Unknown resource: {uri}")
        
        # Register handlers with the app
        self.app.list_tools = list_tools_handler
        self.app.call_tool = call_tool_handler
        self.app.list_resources = list_resources_handler
        self.app.read_resource = read_resource_handler
        
        logger.info("Enhanced MCP server handlers registered")
        
        # Run the server using the configured transport
        if self.config.server.transport == "stdio":
            from mcp.server.stdio import stdio_server
            logger.info("Starting enhanced MCP server with stdio transport")
            async with stdio_server() as streams:
                await self.app.run(
                    streams[0], streams[1], self.app.create_initialization_options()
                )
        elif self.config.server.transport == "http":
            from mcp.server.http import http_server
            logger.info(f"Starting enhanced MCP server with HTTP transport on {self.config.server.host}:{self.config.server.port}")
            await http_server(
                self.app,
                host=self.config.server.host,
                port=self.config.server.port,
                debug=self.config.server.debug
            )
        else:
            logger.error(f"Unsupported transport: {self.config.server.transport}")
            raise ValueError(f"Unsupported transport: {self.config.server.transport}")