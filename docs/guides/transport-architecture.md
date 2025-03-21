# Transport Architecture

This guide explains the transport architecture of the Kaltura MCP server, which enables communication between clients and the server using different transport mechanisms.

## Overview

The Kaltura MCP server supports multiple transport mechanisms to facilitate communication between clients and the server. The transport architecture is designed to be modular, extensible, and configurable, allowing the server to be used in a variety of environments and use cases.

The server currently supports three transport mechanisms:

1. **STDIO Transport**: For direct process-to-process communication
2. **HTTP Transport**: For web-based communication
3. **SSE Transport**: For Server-Sent Events based communication

## Transport Interface

All transport implementations share a common interface defined in the `McpTransport` abstract base class. This interface provides a unified way to initialize, run, and shut down transport mechanisms.

```python
class McpTransport(abc.ABC):
    """Base interface for MCP transport mechanisms."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the transport with configuration."""
        self.config = config
        
    async def initialize(self) -> None:
        """Initialize the transport."""
        logger.info(f"Initializing {self.__class__.__name__}")
        
    @abc.abstractmethod
    async def run(self, server: Server) -> None:
        """Run the transport with the given server."""
        raise NotImplementedError("Transport must implement run method")
        
    async def shutdown(self) -> None:
        """Shutdown the transport."""
        logger.info(f"Shutting down {self.__class__.__name__}")
```

## Transport Implementations

### STDIO Transport

The STDIO transport uses standard input and output streams for communication between the client and server. This is the simplest transport mechanism and is particularly useful for direct process-to-process communication, such as when the MCP server is embedded in another process.

```python
class StdioTransport(McpTransport):
    """STDIO-based transport for MCP."""
    
    async def run(self, server: Server) -> None:
        """Run the server using STDIO transport."""
        async with stdio_server() as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
```

### HTTP Transport

The HTTP transport uses a standard HTTP server to expose MCP functionality as a RESTful API. This transport is particularly useful for web-based clients and for integrating the MCP server with web applications.

```python
class HttpTransport(McpTransport):
    """HTTP-based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the HTTP transport."""
        super().__init__(config)
        self.host = config["server"]["host"]
        self.port = config["server"]["port"]
        
    async def run(self, server: Server) -> None:
        """Run the server using HTTP transport."""
        # Create HTTP handler with server instance
        handler = self._create_handler(server)
        
        # Start HTTP server
        self.server = ThreadedHTTPServer((self.host, self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Keep the main thread running
        while True:
            await asyncio.sleep(1)
```

### SSE Transport

The SSE transport uses Server-Sent Events to enable real-time communication from the server to clients. This transport is particularly useful for applications that need to display live updates or notifications.

```python
class SseTransport(McpTransport):
    """Server-Sent Events based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the SSE transport."""
        super().__init__(config)
        self.host = config["server"]["host"]
        self.port = config["server"]["port"]
        
    async def run(self, server: Server) -> None:
        """Run the server using SSE transport."""
        self.app = self._create_sse_app(server)
        
        # Use uvicorn to run the ASGI app
        config = uvicorn.Config(self.app, host=self.host, port=self.port)
        server = uvicorn.Server(config)
        await server.serve()
```

## Transport Factory

The transport factory is responsible for creating the appropriate transport instance based on the server configuration. This allows the server to be configured to use different transport mechanisms without changing the server code.

```python
class TransportFactory:
    """Factory for creating transport instances."""
    
    @staticmethod
    def create_transport(config: Dict[str, Any]) -> McpTransport:
        """Create a transport instance based on configuration."""
        transport_type = config["server"].get("transport", "stdio").lower()
        
        if transport_type == "stdio":
            return StdioTransport(config)
        elif transport_type == "http":
            return HttpTransport(config)
        elif transport_type == "sse":
            return SseTransport(config)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
```

## Server Integration

The Kaltura MCP server integrates with the transport architecture by creating a transport instance during initialization and using it to run the server. This allows the server to be used with different transport mechanisms without changing the server code.

```python
class KalturaMcpServer:
    """Main server class for Kaltura-MCP."""

    def __init__(self, config: Any) -> None:
        """Initialize the server with configuration."""
        self.config = config
        self.app: Server = Server("kaltura-mcp-server")
        self.transport = TransportFactory.create_transport(config._raw_data)

    async def initialize(self) -> None:
        """Initialize the server components."""
        # Initialize other components...
        
        # Initialize transport
        await self.transport.initialize()

    async def run(self) -> None:
        """Run the server."""
        # Register handlers...
        
        # Run the server using the configured transport
        await self.transport.run(self.app)
```

## Configuration

The transport mechanism is configured using the `transport` option in the `server` section of the configuration file:

```yaml
# Server configuration
server:
  transport: "stdio"  # Options: stdio, http, sse
  host: "0.0.0.0"     # Used for HTTP and SSE transports
  port: 8000          # Used for HTTP and SSE transports
  debug: false        # Enable debug mode
```

You can also set the transport using the `KALTURA_MCP_TRANSPORT` environment variable:

```bash
export KALTURA_MCP_TRANSPORT=http
```

## Client Examples

### STDIO Client

```python
async def stdio_client_example():
    """Example of using the STDIO transport."""
    async with stdio_client() as streams:
        client = Client()
        await client.connect(streams[0], streams[1])
        
        # Use client...
```

### HTTP Client

```python
def http_client_example(host="localhost", port=8000):
    """Example of using the HTTP transport."""
    base_url = f"http://{host}:{port}"
    
    # Get server info
    response = requests.get(f"{base_url}/mcp/info")
    info = response.json()
    
    # List tools
    response = requests.get(f"{base_url}/mcp/tools")
    tools = response.json()["tools"]
    
    # Call a tool
    response = requests.post(
        f"{base_url}/mcp/tools/call",
        json={"name": "kaltura.media.list", "arguments": {"page_size": 5}}
    )
    result = response.json()
```

### SSE Client

```python
def sse_client_example(host="localhost", port=8000):
    """Example of using the SSE transport."""
    base_url = f"http://{host}:{port}"
    
    # Connect to SSE stream
    client = SSEClient(f"{base_url}/mcp/sse")
    
    # Listen for events
    for event in client.events():
        print(f"Received event: {event.event}")
        print(f"Event data: {event.data}")
    
    # Call a tool using HTTP
    response = requests.post(
        f"{base_url}/mcp/tools/call",
        json={"name": "kaltura.media.list", "arguments": {"page_size": 5}}
    )
    result = response.json()
```

## Choosing a Transport

The choice of transport mechanism depends on your use case:

- **STDIO Transport**: Use this for direct process-to-process communication, such as when the MCP server is embedded in another process or when using the server from a command-line tool.

- **HTTP Transport**: Use this for web-based clients, such as web applications or REST API clients. This transport is also useful for integrating the MCP server with other web services.

- **SSE Transport**: Use this for applications that need real-time updates or notifications from the server. This transport is particularly useful for monitoring and dashboard applications.

## Adding a New Transport

To add a new transport mechanism:

1. Create a new class that inherits from `McpTransport`
2. Implement the required `run()` method
3. Add the new transport to the `TransportFactory`
4. Update the configuration documentation

For example, to add a WebSocket transport:

```python
class WebSocketTransport(McpTransport):
    """WebSocket-based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the WebSocket transport."""
        super().__init__(config)
        self.host = config["server"]["host"]
        self.port = config["server"]["port"]
        
    async def run(self, server: Server) -> None:
        """Run the server using WebSocket transport."""
        # Implementation goes here
```

Then add it to the `TransportFactory`:

```python
@staticmethod
def create_transport(config: Dict[str, Any]) -> McpTransport:
    """Create a transport instance based on configuration."""
    transport_type = config["server"].get("transport", "stdio").lower()
    
    if transport_type == "stdio":
        return StdioTransport(config)
    elif transport_type == "http":
        return HttpTransport(config)
    elif transport_type == "sse":
        return SseTransport(config)
    elif transport_type == "websocket":
        return WebSocketTransport(config)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")
```

## Testing Transport Implementations

The Kaltura MCP server includes comprehensive tests for all transport implementations:

### Unit Tests

Unit tests verify that each transport implementation works correctly in isolation:

```bash
# Run all transport unit tests
python -m pytest tests/unit/test_transports.py

# Run tests for a specific transport
python -m pytest tests/unit/test_transports.py::TestStdioTransport
python -m pytest tests/unit/test_transports.py::TestHttpTransport
python -m pytest tests/unit/test_transports.py::TestSseTransport

# Run transport factory tests
python -m pytest tests/unit/test_transport_factory.py
```

### Integration Tests

Integration tests verify that the transports work correctly with the server:

```bash
# Run all transport integration tests
python -m pytest tests/integration/test_transport_integration.py

# Run advanced transport integration tests
python -m pytest tests/integration/test_advanced_transport_integration.py

# Run end-to-end transport tests
python -m pytest tests/integration/test_transport_end_to_end.py
```

### CI Tests

The project includes a comprehensive CI testing script that runs linting, type checking, and all tests:

```bash
# Run all CI checks
python run_tests.py --ci

# Run specific checks
python run_tests.py --lint      # Run linting only
python run_tests.py --type-check # Run type checking only
python run_tests.py --tests     # Run tests only

# Fix common linting issues automatically
python run_tests.py --fix-all
```

#### Type Checking

Type checking is an important part of the CI process. All transport implementations must pass mypy type checking:

```bash
# Run type checking
python run_tests.py --type-check
```

Key type checking considerations for transport implementations:

1. All functions must have return type annotations
2. All function parameters must have type annotations
3. When extending `json.JSONEncoder`, ensure the `default` method parameter is named `o` to match the parent class
4. Return dictionaries for all custom object types, not raw strings
5. Use `# type: ignore` comments only when absolutely necessary and with a comment explaining why

### Docker Tests

You can also run tests inside Docker containers:

```bash
# Run all tests in Docker
docker run --rm kaltura-mcp python run_tests.py

# Run transport-specific tests in Docker
docker run --rm kaltura-mcp python -m pytest tests/unit/test_transports.py
```

## CI/CD Integration

The Kaltura MCP project includes GitHub Actions workflows for testing all transport implementations:

- `transport-tests.yml`: Tests all transport implementations on multiple Python versions (3.10, 3.11, 3.12)
- Runs linting, type checking, and tests for each transport type
- Builds and tests Docker images for each transport type
- Builds multi-architecture Docker images (amd64, arm64) for deployment
- Pushes images to GitHub Container Registry with appropriate tags

### Docker Images

The CI/CD workflow builds and pushes the following Docker images:

- Base image: `ghcr.io/<owner>/kaltura-mcp:latest`, `ghcr.io/<owner>/kaltura-mcp:<version>`, `ghcr.io/<owner>/kaltura-mcp:<commit-sha>`
- STDIO transport: `ghcr.io/<owner>/kaltura-mcp:stdio`, `ghcr.io/<owner>/kaltura-mcp:<version>-stdio`, `ghcr.io/<owner>/kaltura-mcp:<commit-sha>-stdio`
- HTTP transport: `ghcr.io/<owner>/kaltura-mcp:http`, `ghcr.io/<owner>/kaltura-mcp:<version>-http`, `ghcr.io/<owner>/kaltura-mcp:<commit-sha>-http`
- SSE transport: `ghcr.io/<owner>/kaltura-mcp:sse`, `ghcr.io/<owner>/kaltura-mcp:<version>-sse`, `ghcr.io/<owner>/kaltura-mcp:<commit-sha>-sse`

These images are built for both amd64 and arm64 architectures, ensuring compatibility with different platforms.

### CI Workflow

The CI workflow is triggered on:
- Push to the main branch that affects transport files
- Pull requests to the main branch that affect transport files
- Manual trigger using the workflow_dispatch event

This ensures that all transport implementations are thoroughly tested before deployment.

## Conclusion

The transport architecture of the Kaltura MCP server provides a flexible and extensible way to support multiple communication mechanisms. By abstracting the transport layer, the server can be used in a variety of environments and use cases without changing the core server code.

The comprehensive testing suite ensures that all transport implementations work correctly and reliably, making it easy to add new transport mechanisms or modify existing ones without breaking compatibility.