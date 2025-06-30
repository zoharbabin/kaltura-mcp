#!/usr/bin/env python3
"""Local MCP Proxy Client - Connects to remote Kaltura MCP server via stdio."""

import asyncio
import os
import sys
from typing import Any, Dict

import httpx
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server


class RemoteMCPProxy:
    """Proxy that connects local MCP client to remote Kaltura MCP server."""

    def __init__(self, server_url: str, access_token: str):
        self.server_url = server_url
        self.access_token = access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to remote MCP server."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.server_url, json=message, headers=self.headers, timeout=30.0
            )
            response.raise_for_status()
            return response.json()


# Create local MCP server that proxies to remote
server = Server("kaltura-mcp-proxy")

# Get configuration from environment
REMOTE_SERVER_URL = os.getenv("KALTURA_REMOTE_SERVER_URL")
REMOTE_ACCESS_TOKEN = os.getenv("KALTURA_REMOTE_ACCESS_TOKEN")

if not REMOTE_SERVER_URL or not REMOTE_ACCESS_TOKEN:
    print("Error: Missing required environment variables:", file=sys.stderr)
    print("KALTURA_REMOTE_SERVER_URL and KALTURA_REMOTE_ACCESS_TOKEN must be set", file=sys.stderr)
    sys.exit(1)

proxy = RemoteMCPProxy(REMOTE_SERVER_URL, REMOTE_ACCESS_TOKEN)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List tools from remote server."""
    message = {"jsonrpc": "2.0", "id": "list_tools", "method": "tools/list", "params": {}}

    response = await proxy.send_message(message)
    if "error" in response:
        return []

    tools_data = response.get("result", {}).get("tools", [])
    return [types.Tool(**tool) for tool in tools_data]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Call tool on remote server."""
    message = {
        "jsonrpc": "2.0",
        "id": f"call_tool_{name}",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }

    response = await proxy.send_message(message)
    if "error" in response:
        error_msg = response["error"].get("message", "Unknown error")
        return [types.TextContent(type="text", text=f"Error: {error_msg}")]

    content = response.get("result", {}).get("content", [])
    return [types.TextContent(**item) for item in content]


async def async_main():
    """Run the proxy MCP server."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Proxy error: {e}", file=sys.stderr)


def main():
    """Entry point for the CLI script."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
