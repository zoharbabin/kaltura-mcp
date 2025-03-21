# Base Transport Interface

This document provides the detailed implementation for the base transport interface in the Kaltura MCP server.

## File: `kaltura_mcp/transport/base.py`

```python
"""
Base transport interface for Kaltura MCP Server.
"""
import abc
import logging
from typing import Any, Dict, Optional

from mcp.server.lowlevel import Server

logger = logging.getLogger(__name__)


class McpTransport(abc.ABC):
    """Base interface for MCP transport mechanisms."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the transport with configuration.
        
        Args:
            config: Server configuration dictionary
        """
        self.config = config
        
    async def initialize(self) -> None:
        """Initialize the transport."""
        logger.info(f"Initializing {self.__class__.__name__}")
        
    @abc.abstractmethod
    async def run(self, server: Server) -> None:
        """
        Run the transport with the given server.
        
        Args:
            server: The MCP server instance
        """
        raise NotImplementedError("Transport must implement run method")
        
    async def shutdown(self) -> None:
        """Shutdown the transport."""
        logger.info(f"Shutting down {self.__class__.__name__}")
```

## Key Components

1. **Abstract Base Class**: `McpTransport` is an abstract base class that defines the interface for all transport implementations.

2. **Configuration**: The constructor takes a configuration dictionary that contains all the settings needed for the transport.

3. **Lifecycle Methods**:
   - `initialize()`: Prepares the transport for use
   - `run(server)`: Runs the transport with the given server
   - `shutdown()`: Cleans up resources when the transport is no longer needed

4. **Logging**: The transport uses the standard Python logging module to log important events.

## Usage

The base transport interface is used as follows:

1. Create a concrete transport implementation that inherits from `McpTransport`
2. Implement the required `run()` method
3. Optionally override the `initialize()` and `shutdown()` methods
4. Use the transport with the Kaltura MCP server

Example:

```python
class MyTransport(McpTransport):
    async def run(self, server):
        # Implementation goes here
        pass
```

## Error Handling

Transport implementations should handle errors appropriately:

1. Log errors using the standard Python logging module
2. Raise exceptions for critical errors that should stop the server
3. Handle non-critical errors gracefully to maintain server stability

## Thread Safety

Transport implementations should be thread-safe if they use multiple threads. The base interface itself is not thread-safe, so implementations must handle thread safety as needed.