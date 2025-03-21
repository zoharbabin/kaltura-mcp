# Transport Factory Implementation

This document provides the detailed implementation for the transport factory in the Kaltura MCP server.

## File: `kaltura_mcp/transport/__init__.py`

```python
"""
Transport factory for Kaltura MCP Server.
"""
import logging
from typing import Any, Dict

from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.stdio import StdioTransport

logger = logging.getLogger(__name__)


class TransportFactory:
    """Factory for creating transport instances."""
    
    @staticmethod
    def create_transport(config: Dict[str, Any]) -> McpTransport:
        """
        Create a transport instance based on configuration.
        
        Args:
            config: Server configuration dictionary
        
        Returns:
            A transport instance
            
        Raises:
            ValueError: If the transport type is not supported
        """
        transport_type = config["server"]["transport"].lower()
        
        logger.info(f"Creating transport of type: {transport_type}")
        
        if transport_type == "stdio":
            return StdioTransport(config)
        elif transport_type == "http":
            return HttpTransport(config)
        elif transport_type == "sse":
            return SseTransport(config)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
```

## Key Components

1. **TransportFactory Class**: Provides a static method for creating transport instances based on configuration.

2. **Create Transport Method**: Takes a configuration dictionary and returns an appropriate transport instance based on the configured transport type.

3. **Supported Transports**:
   - `stdio`: Standard input/output transport
   - `http`: HTTP transport
   - `sse`: Server-Sent Events transport

## How the Transport Factory Works

The transport factory uses the factory pattern to create transport instances:

1. The factory reads the transport type from the configuration
2. Based on the transport type, it creates an instance of the appropriate transport class
3. It returns the transport instance to the caller

This approach provides several benefits:
- Encapsulates the creation logic in one place
- Makes it easy to add new transport types in the future
- Provides a consistent interface for creating transports

## Usage Example

```python
# Load configuration
config = load_config()

# Create transport using factory
transport = TransportFactory.create_transport(config._raw_data)

# Initialize and run transport
await transport.initialize()
await transport.run(server)
```

## Error Handling

The transport factory handles errors as follows:

1. Validates the transport type
2. Raises a `ValueError` if the transport type is not supported
3. Logs the transport type being created

This approach ensures that only supported transport types are used and provides clear error messages when an unsupported transport type is specified.

## Adding New Transport Types

To add a new transport type:

1. Create a new transport class that implements the `McpTransport` interface
2. Import the new transport class in the factory module
3. Add a new condition to the `create_transport` method to create an instance of the new transport class

For example, to add a WebSocket transport:

```python
from kaltura_mcp.transport.websocket import WebSocketTransport

# In the create_transport method
if transport_type == "websocket":
    return WebSocketTransport(config)
```

## Configuration

The transport factory expects the configuration to have the following structure:

```yaml
server:
  transport: "stdio"  # Options: stdio, http, sse
  host: "0.0.0.0"     # Used for HTTP and SSE transports
  port: 8000          # Used for HTTP and SSE transports
  # Other server configuration options...
```

The `transport` field specifies which transport type to use. The `host` and `port` fields are used by the HTTP and SSE transports to determine where to listen for connections.