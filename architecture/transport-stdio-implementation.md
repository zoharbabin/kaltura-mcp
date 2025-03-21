# STDIO Transport Implementation

This document provides the detailed implementation for the STDIO transport in the Kaltura MCP server.

## File: `kaltura_mcp/transport/stdio.py`

```python
"""
STDIO transport implementation for Kaltura MCP Server.
"""
import logging
from typing import Any, Dict

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from kaltura_mcp.transport.base import McpTransport

logger = logging.getLogger(__name__)


class StdioTransport(McpTransport):
    """STDIO-based transport for MCP."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the STDIO transport.
        
        Args:
            config: Server configuration dictionary
        """
        super().__init__(config)
        
    async def run(self, server: Server) -> None:
        """
        Run the server using STDIO transport.
        
        Args:
            server: The MCP server instance
        """
        logger.info("Starting server with STDIO transport")
        
        try:
            async with stdio_server() as streams:
                await server.run(streams[0], streams[1], server.create_initialization_options())
        except Exception as e:
            logger.error(f"Error running server with STDIO transport: {e}")
            raise
```

## Key Components

1. **StdioTransport Class**: Implements the `McpTransport` interface for STDIO communication.

2. **Run Method**: Uses the `stdio_server` context manager from the MCP SDK to create input and output streams, then runs the server with these streams.

3. **Error Handling**: Catches and logs any exceptions that occur during server execution, then re-raises them to be handled by the caller.

## How STDIO Transport Works

The STDIO transport uses standard input and output streams for communication between the client and server:

1. The server reads JSON-RPC requests from standard input
2. The server processes the requests using the MCP protocol
3. The server writes JSON-RPC responses to standard output

This transport is particularly useful for:
- Direct process-to-process communication
- Integration with command-line tools
- Embedding the MCP server in another process

## Advantages of STDIO Transport

1. **Simplicity**: Simple to implement and use
2. **Reliability**: Direct process-to-process communication without network overhead
3. **Security**: No network exposure, reducing attack surface
4. **Integration**: Easy integration with command-line tools and scripts

## Limitations of STDIO Transport

1. **Single Client**: Only one client can connect at a time
2. **Process Coupling**: Client and server must be in the same process hierarchy
3. **No Authentication**: No built-in authentication mechanism
4. **Limited Scalability**: Not suitable for high-volume or distributed scenarios

## Usage Example

```python
# Server side
server = KalturaMcpServer(config)
await server.initialize()
await server.run()  # Uses STDIO transport if configured

# Client side
async with stdio_client() as streams:
    client = Client()
    await client.connect(streams[0], streams[1])
    # Use client...
```

## Error Handling

The STDIO transport handles errors as follows:

1. Catches exceptions during server execution
2. Logs the error with context
3. Re-raises the exception to be handled by the caller

This approach ensures that errors are properly logged while still allowing the caller to handle them appropriately.