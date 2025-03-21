# Kaltura MCP Transport Architecture

## Overview

This document outlines the architecture for supporting multiple transport mechanisms in the Kaltura MCP server. The Model Context Protocol (MCP) allows for different transport options to facilitate communication between clients and servers. This architecture enables the Kaltura MCP server to support three primary transport mechanisms:

1. **STDIO Transport**: For direct process-to-process communication
2. **HTTP Transport**: For web-based communication
3. **SSE Transport**: For Server-Sent Events based communication

## Architecture Goals

- Provide a unified interface for all transport mechanisms
- Maintain backward compatibility with existing clients
- Enable easy configuration of transport options
- Support seamless switching between transport mechanisms
- Implement proper error handling and logging across all transports
- Ensure consistent behavior regardless of transport mechanism

## Core Components

### Transport Interface

The core of the architecture is a unified transport interface that abstracts the communication layer from the MCP server logic.

```python
class McpTransport:
    """Base interface for MCP transport mechanisms."""
    
    async def initialize(self):
        """Initialize the transport."""
        pass
        
    async def run(self, server):
        """Run the transport with the given server."""
        raise NotImplementedError("Transport must implement run method")
        
    async def shutdown(self):
        """Shutdown the transport."""
        pass
```

### Transport Implementations

#### STDIO Transport

```python
class StdioTransport(McpTransport):
    """STDIO-based transport for MCP."""
    
    async def run(self, server):
        """Run the server using STDIO transport."""
        async with stdio_server() as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
```

#### HTTP Transport

```python
class HttpTransport(McpTransport):
    """HTTP-based transport for MCP."""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        
    async def run(self, server):
        """Run the server using HTTP transport."""
        # Create HTTP handler with server instance
        handler = self._create_handler(server)
        
        # Start HTTP server
        self.server = ThreadedHTTPServer((self.host, self.port), handler)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Keep the main thread running
        while True:
            await asyncio.sleep(1)
            
    async def shutdown(self):
        """Shutdown the HTTP server."""
        if self.server:
            self.server.shutdown()
```

#### SSE Transport

```python
class SseTransport(McpTransport):
    """Server-Sent Events based transport for MCP."""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = None
        
    async def run(self, server):
        """Run the server using SSE transport."""
        self.app = self._create_sse_app(server)
        
        # Use uvicorn to run the ASGI app
        config = uvicorn.Config(self.app, host=self.host, port=self.port)
        server = uvicorn.Server(config)
        await server.serve()
```

### Transport Factory

```python
class TransportFactory:
    """Factory for creating transport instances."""
    
    @staticmethod
    def create_transport(config):
        """Create a transport instance based on configuration."""
        transport_type = config.server.transport.lower()
        
        if transport_type == "stdio":
            return StdioTransport()
        elif transport_type == "http":
            return HttpTransport(config.server.host, config.server.port)
        elif transport_type == "sse":
            return SseTransport(config.server.host, config.server.port)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
```

## Server Integration

The Kaltura MCP server will be updated to use the transport interface:

```python
class KalturaMcpServer:
    """Main server class for Kaltura-MCP."""
    
    def __init__(self, config):
        """Initialize the server with configuration."""
        self.config = config
        self.app = Server("kaltura-mcp-server")
        self.kaltura_client = None
        self.tool_handlers = {}
        self.resource_handlers = {}
        self.transport = TransportFactory.create_transport(config)
        
    async def run(self):
        """Run the server."""
        # Register MCP handlers
        self._register_handlers()
        
        logger.info(f"Starting Kaltura MCP Server with {self.config.server.transport} transport")
        
        # Run the server using the configured transport
        await self.transport.run(self.app)
```

## Configuration

The existing configuration system will be extended to support all transport options:

```yaml
# Server configuration
server:
  transport: "stdio"  # Options: stdio, http, sse
  host: "0.0.0.0"     # Used for HTTP and SSE transports
  port: 8000          # Used for HTTP and SSE transports
  debug: false        # Enable debug mode
```

## Client Compatibility

To ensure backward compatibility, clients will need to be updated to support all transport options:

```python
class KalturaMcpClient:
    """Client for Kaltura MCP Server."""
    
    @staticmethod
    async def connect(transport_type="stdio", host=None, port=None):
        """Connect to a Kaltura MCP server."""
        if transport_type == "stdio":
            async with stdio_client() as streams:
                client = Client()
                await client.connect(streams[0], streams[1])
                return client
        elif transport_type == "http":
            return await http_client_connect(host, port)
        elif transport_type == "sse":
            return await sse_client_connect(host, port)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
```

## Error Handling and Logging

Each transport implementation will include proper error handling and logging:

```python
class BaseTransport(McpTransport):
    """Base class for all transport implementations."""
    
    async def run(self, server):
        """Run the server with error handling."""
        try:
            await self._run_impl(server)
        except Exception as e:
            logger.error(f"Transport error: {e}")
            raise
```

## Testing Strategy

A comprehensive testing strategy will be implemented to ensure all transport mechanisms work correctly:

1. **Unit Tests**: Test each transport implementation in isolation
2. **Integration Tests**: Test the server with each transport mechanism
3. **End-to-End Tests**: Test complete client-server communication with each transport

## Implementation Plan

1. Create the transport interface and base classes
2. Implement the STDIO transport (largely reusing existing code)
3. Implement the HTTP transport (based on the integration test implementation)
4. Implement the SSE transport (new implementation)
5. Update the server to use the transport interface
6. Update the configuration system
7. Create client examples for each transport
8. Implement comprehensive tests
9. Update documentation

## Conclusion

This architecture provides a flexible and extensible way to support multiple transport mechanisms in the Kaltura MCP server. By abstracting the transport layer, we can ensure consistent behavior regardless of the communication mechanism used.