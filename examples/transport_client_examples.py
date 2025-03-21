#!/usr/bin/env python3
"""
Examples of using different transport mechanisms with the Kaltura MCP client.
"""
import asyncio
import sys

import requests

# Try to import the MCP client classes
try:
    from mcp.client.lowlevel import Client
    from mcp.client.stdio import stdio_client
    from sseclient import SSEClient
except ImportError:
    # If the imports fail, create mock classes for testing
    class Client:
        """Mock client for testing."""

        async def connect(self, reader, writer):
            """Mock connect method."""
            return True

        async def get_server_info(self):
            """Mock get_server_info method."""
            return {"name": "Mock MCP Server"}

        async def list_tools(self):
            """Mock list_tools method."""
            return []

        async def list_resources(self):
            """Mock list_resources method."""
            return []

        async def call_tool(self, name, arguments):
            """Mock call_tool method."""
            return []

    # Mock stdio_client context manager
    class StdioClientContextManager:
        """Mock stdio_client context manager."""

        def __init__(self, server=None):
            """Initialize with optional server."""
            self.server = server

        async def __aenter__(self):
            """Mock __aenter__ method."""
            return (None, None)  # reader, writer

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            """Mock __aexit__ method."""
            return False

    stdio_client = StdioClientContextManager

    # Mock SSEClient
    class SSEClient:
        """Mock SSE client."""

        def __init__(self, url):
            """Initialize with URL."""
            self.url = url

        def events(self):
            """Mock events method."""
            return []


async def stdio_client_example() -> None:
    """Example of using the STDIO transport."""
    print("=== STDIO Transport Example ===")

    try:
        # Create a server instance for stdio_client
        server = None  # This is a placeholder, the actual server is created by the transport

        async with stdio_client(server) as streams:
            try:
                client = Client()
                print("Connecting to server...")
                await client.connect(streams[0], streams[1])

                # Get server info
                print("Fetching server info...")
                info = await client.get_server_info()
                print(f"Server info: {info}")

                # List tools
                print("Fetching available tools...")
                tools = await client.list_tools()
                print(f"Available tools: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")

                # List resources
                print("Fetching available resources...")
                resources = await client.list_resources()
                print(f"Available resources: {len(resources)}")
                for resource in resources:
                    print(f"  - {resource.uri}: {resource.name}")

                # Call a tool
                if any(tool.name == "kaltura.media.list" for tool in tools):
                    print("\nCalling kaltura.media.list tool...")
                    result = await client.call_tool("kaltura.media.list", {"page_size": 5})
                    print(f"Result: {result}")
            except Exception as e:
                print(f"Error in STDIO client: {e}")
                raise
    except Exception as e:
        print(f"Error setting up STDIO transport: {e}")
        sys.exit(1)


def http_client_example(host: str = "localhost", port: int = 8000) -> None:
    """
    Example of using the HTTP transport.

    Args:
        host: The server host
        port: The server port
    """
    print("=== HTTP Transport Example ===")

    base_url = f"http://{host}:{port}"
    timeout = 5  # Set a reasonable timeout for all requests

    try:
        # Get server info with retry
        print("Fetching server info...")
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(f"{base_url}/mcp/info", timeout=timeout)
                response.raise_for_status()  # Raise an exception for HTTP errors
                info = response.json()
                print(f"Server info: {info}")
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"Attempt {attempt}/{max_retries} failed: {e}")
                    import time

                    time.sleep(retry_delay)
                else:
                    print(f"Failed to connect to server after {max_retries} attempts")
                    raise

        # List tools
        print("Fetching available tools...")
        response = requests.get(f"{base_url}/mcp/tools", timeout=timeout)
        response.raise_for_status()
        tools = response.json()["tools"]
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # List resources
        print("Fetching available resources...")
        response = requests.get(f"{base_url}/mcp/resources", timeout=timeout)
        response.raise_for_status()
        resources = response.json()["resources"]
        print(f"Available resources: {len(resources)}")
        for resource in resources:
            print(f"  - {resource['uri']}: {resource['name']}")

        # Call a tool
        if any(tool["name"] == "kaltura.media.list" for tool in tools):
            print("\nCalling kaltura.media.list tool...")
            response = requests.post(
                f"{base_url}/mcp/tools/call", json={"name": "kaltura.media.list", "arguments": {"page_size": 5}}, timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            print(f"Result: {result}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with server: {e}")
        sys.exit(1)


def sse_client_example(host: str = "localhost", port: int = 8000) -> None:
    """
    Example of using the SSE transport.

    Args:
        host: The server host
        port: The server port
    """
    print("=== SSE Transport Example ===")

    base_url = f"http://{host}:{port}"
    timeout = 5  # Set a reasonable timeout for all requests

    try:
        # Get server info with retry
        print("Fetching server info...")
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(f"{base_url}/mcp/info", timeout=timeout)
                response.raise_for_status()  # Raise an exception for HTTP errors
                info = response.json()
                print(f"Server info: {info}")
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"Attempt {attempt}/{max_retries} failed: {e}")
                    import time

                    time.sleep(retry_delay)
                else:
                    print(f"Failed to connect to server after {max_retries} attempts")
                    raise

        # List tools
        print("Fetching available tools...")
        response = requests.get(f"{base_url}/mcp/tools", timeout=timeout)
        response.raise_for_status()
        tools = response.json()["tools"]
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # List resources
        print("Fetching available resources...")
        response = requests.get(f"{base_url}/mcp/resources", timeout=timeout)
        response.raise_for_status()
        resources = response.json()["resources"]
        print(f"Available resources: {len(resources)}")
        for resource in resources:
            print(f"  - {resource['uri']}: {resource['name']}")

        # Connect to SSE stream
        print("\nConnecting to SSE stream...")
        try:
            client = SSEClient(f"{base_url}/mcp/sse")

            # Start a separate thread to listen for events
            def listen_for_events():
                try:
                    for event in client.events():
                        print(f"Received event: {event.event}")
                        print(f"Event data: {event.data}")
                except Exception as e:
                    print(f"Error in SSE event stream: {e}")

            import threading

            event_thread = threading.Thread(target=listen_for_events)
            event_thread.daemon = True
            event_thread.start()

            # Call a tool
            if any(tool["name"] == "kaltura.media.list" for tool in tools):
                print("\nCalling kaltura.media.list tool...")
                response = requests.post(
                    f"{base_url}/mcp/tools/call",
                    json={"name": "kaltura.media.list", "arguments": {"page_size": 5}},
                    timeout=timeout,
                )
                response.raise_for_status()
                result = response.json()
                print(f"Result: {result}")

            # Wait for a few events (limited to avoid hanging in tests)
            print("\nWaiting for events (limited to 5 seconds)...")
            try:
                import time

                # Only wait for 5 seconds to avoid hanging in tests
                time.sleep(5)
                print("\nFinished waiting for events")
            except KeyboardInterrupt:
                print("\nExiting...")
        except Exception as e:
            print(f"Error connecting to SSE stream: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with server: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python transport_client_examples.py <transport_type> [host] [port]")
        print("  transport_type: stdio, http, or sse")
        print("  host: Server host (default: localhost)")
        print("  port: Server port (default: 8000)")
        sys.exit(1)

    transport_type = sys.argv[1].lower()
    host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    if transport_type == "stdio":
        asyncio.run(stdio_client_example())
    elif transport_type == "http":
        http_client_example(host, port)
    elif transport_type == "sse":
        sse_client_example(host, port)
    else:
        print(f"Unsupported transport type: {transport_type}")
        print("Supported types: stdio, http, sse")
        sys.exit(1)


if __name__ == "__main__":
    main()
