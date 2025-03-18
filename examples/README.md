# Kaltura MCP Server Examples

This directory contains example applications and guides for using the Kaltura MCP server.

## Example Applications

### Python Clients

- [simple_demo_client.py](simple_demo_client.py) - Simple Python client using the MCP client library
- [demo_client.py](demo_client.py) - More comprehensive Python client example
- [kaltura_mcp_client.py](kaltura_mcp_client.py) - Client specifically for the Kaltura MCP server
- [simple_subprocess_client.py](simple_subprocess_client.py) - Client using subprocess to communicate with the server
- [working_mcp_client.py](working_mcp_client.py) - Working client example with error handling
- [direct_stdio_client.py](direct_stdio_client.py) - Client using direct stdio communication
- [http_client.py](http_client.py) - Client using HTTP transport
- [programmatic_client.py](programmatic_client.py) - Programmatic client example
- [simple_client.py](simple_client.py) - Minimal client implementation

### Test Scripts

- [basic_test.py](basic_test.py) - Basic test script for verifying server configuration
- [simple_functional_test.py](simple_functional_test.py) - Simple functional test script
- [complete_test.py](complete_test.py) - Comprehensive end-to-end test script
- [performance_test.py](performance_test.py) - Performance testing script for context management strategies

### Utility Scripts

- [mcp_cli_wrapper.py](mcp_cli_wrapper.py) - Wrapper script for the MCP CLI

## Usage Guides

- [using_with_claude.md](using_with_claude.md) - Guide for using the server with Claude
- [using_with_mcp_cli.md](using_with_mcp_cli.md) - Guide for using the server with the MCP CLI
- [mcp_cli_guide.md](mcp_cli_guide.md) - Comprehensive guide for using the MCP CLI with the server
- [using_mcp_inspector.md](using_mcp_inspector.md) - Guide for using the MCP Inspector with the server

## Getting Started

To run the example applications, you need to have the Kaltura MCP server installed and configured. See the [Quick Start Guide](../docs/getting-started/quick-start.md) for instructions.

### Running the Simple Demo Client

```bash
# Make sure the server is running
kaltura-mcp

# In another terminal, run the client
python simple_demo_client.py
```

### Using with Claude

See [using_with_claude.md](using_with_claude.md) for instructions on using the server with Claude.

### Using with MCP CLI

See [mcp_cli_guide.md](mcp_cli_guide.md) for instructions on using the server with the MCP CLI.

## Creating Your Own Client

You can use these examples as a starting point for creating your own client. The key steps are:

1. Connect to the server using the MCP client library or direct JSON-RPC communication
2. Initialize the session
3. List available tools and resources
4. Call tools and read resources as needed
5. Close the session when done

See the [API Reference](../docs/api-reference/README.md) for more information on the available tools and resources.