#!/usr/bin/env python3
"""
Enhanced server runner for integration tests.

This script runs the Kaltura MCP server with HTTP transport for testing.
"""
import anyio
import logging
import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaltura_mcp.config import load_config, Config
from kaltura_mcp.server import KalturaMcpServer
import asyncio
import socket
import threading
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class McpHttpHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for MCP server requests."""
    
    def __init__(self, *args, **kwargs):
        self.mcp_server = kwargs.pop('mcp_server', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Handle different endpoints
            if path == '/tools':
                self._handle_list_tools()
            elif path == '/resources':
                self._handle_list_resources()
            elif path.startswith('/resources/'):
                uri = path[len('/resources/'):]
                self._handle_read_resource(uri)
            else:
                # Default response for root path
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Kaltura MCP Server')
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            arguments = json.loads(body)
            
            # Handle different endpoints
            if path.startswith('/tools/'):
                tool_name = path[len('/tools/'):]
                self._handle_call_tool(tool_name, arguments)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, str(e))
    
    def _handle_list_tools(self):
        """Handle list tools request."""
        try:
            # Get the list_tools method
            list_tools_method = self.mcp_server.app.list_tools
            
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the coroutine
            tools = loop.run_until_complete(list_tools_method())
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(tools).encode())
        except Exception as e:
            logger.error(f"Error in _handle_list_tools: {e}")
            self.send_error(500, str(e))
    
    def _handle_list_resources(self):
        """Handle list resources request."""
        try:
            # Get the list_resources method
            list_resources_method = self.mcp_server.app.list_resources
            
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the coroutine
            resources = loop.run_until_complete(list_resources_method())
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resources).encode())
        except Exception as e:
            logger.error(f"Error in _handle_list_resources: {e}")
            self.send_error(500, str(e))
    
    def _handle_read_resource(self, uri):
        """Handle read resource request."""
        try:
            # Get the read_resource method
            read_resource_method = self.mcp_server.app.read_resource
            
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the coroutine
            resource = loop.run_until_complete(read_resource_method(uri))
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resource).encode())
        except Exception as e:
            logger.error(f"Error in _handle_read_resource: {e}")
            self.send_error(500, str(e))
    
    def _handle_call_tool(self, tool_name, arguments):
        """Handle call tool request."""
        try:
            # Get the call_tool method
            call_tool_method = self.mcp_server.app.call_tool
            
            # Create a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the coroutine with the correct arguments
            # The signature is likely call_tool({"name": tool_name, "arguments": arguments})
            result = loop.run_until_complete(call_tool_method(tool_name, arguments))
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error in _handle_call_tool: {e}")
            self.send_error(500, str(e))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server."""
    pass

async def run_http_server(config_path):
    """Run the server with HTTP transport."""
    # Load configuration
    if config_path:
        os.environ["KALTURA_MCP_CONFIG"] = config_path
    
    config = load_config()
    
    # Create and initialize server
    server = KalturaMcpServer(config)
    await server.initialize()
    
    # Get server config
    server_config = config.server
    host = server_config.host
    port = server_config.port
    
    logger.info(f"Starting HTTP server on {host}:{port}")
    
    # Create HTTP handler with server instance
    def handler(*args, **kwargs):
        kwargs['mcp_server'] = server
        return McpHttpHandler(*args, **kwargs)
    
    # Start HTTP server in a separate thread
    httpd = ThreadedHTTPServer((host, port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep the main thread running
    while True:
        await asyncio.sleep(1)

def main():
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get config path from command line
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the server
    anyio.run(run_http_server, config_path)

if __name__ == "__main__":
    main()