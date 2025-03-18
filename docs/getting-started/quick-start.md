# Quick Start Guide

This guide will help you get started with the Kaltura MCP server quickly and easily.

## Prerequisites

Before you begin, make sure you have:

- Python 3.10 or higher installed
- Kaltura API credentials (partner ID, admin secret, user ID)
- Git (optional, for cloning the repository)

## Installation

### Option 1: Install from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/kaltura/kaltura-mcp-public.git
   cd kaltura-mcp-public
   ```

2. Run the setup script:
   ```bash
   ./setup_kaltura_mcp.py
   ```

   This script will:
   - Check prerequisites
   - Set up configuration files
   - Install dependencies
   - Run verification tests

3. Configure the server:
   ```bash
   # Edit the config.yaml file with your Kaltura API credentials
   nano config.yaml
   ```

### Option 2: Using Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/kaltura/kaltura-mcp-public.git
   cd kaltura-mcp-public
   ```

2. Create and configure the config.yaml file:
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your Kaltura credentials
   nano config.yaml
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up
   ```

## Running the Server

### Option 1: Direct Execution

```bash
# If installed in a virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
kaltura-mcp
```

### Option 2: Using the MCP CLI

```bash
# Start the server with the MCP Inspector
mcp dev kaltura_mcp/server.py:main

# Or run the server directly
mcp run kaltura_mcp/server.py:main
```

### Option 3: Using Docker

```bash
docker-compose up
```

## Verifying the Installation

### Using the MCP Inspector

1. Start the server with the MCP Inspector:
   ```bash
   mcp dev kaltura_mcp/server.py:main
   ```

2. Open http://localhost:5173 in your web browser.

3. Connect to the server using the "Connect" button.

4. Explore the available tools and resources.

### Using the MCP CLI

```bash
# List tools
mcp tools kaltura-mcp

# List resources
mcp resources kaltura-mcp

# Call a tool
mcp call kaltura-mcp kaltura.media.list '{"page_size": 5, "filter": {}}'

# Read a resource
mcp read kaltura-mcp kaltura://media/list?page_size=5
```

### Using a Python Client

Create a simple Python script to test the server:

```python
#!/usr/bin/env python3
import asyncio
import json
from mcp import ClientSession, StdioServerParameters

async def main():
    # Set up server parameters
    server_params = StdioServerParameters(
        command="kaltura-mcp",
        args=[],
        env=None
    )
    
    # Create a client using stdio transport
    async with await asyncio.create_subprocess_exec(
        server_params.command,
        *server_params.args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=server_params.env
    ) as process:
        # Create a client session
        session = ClientSession(process.stdout, process.stdin)
        
        # Initialize the session
        await session.initialize()
        
        # List available tools
        tools_result = await session.list_tools()
        print("Available tools:")
        for tool in tools_result.tools:
            print(f"- {tool.name}: {tool.description}")
        
        # Call the media.list tool
        result = await session.call_tool("kaltura.media.list", {
            "page_size": 5,
            "filter": {}
        })
        print("\nMedia entries:")
        print(json.dumps(json.loads(result.content[0].text), indent=2))
        
        # Close the session
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `test_client.py` and run it:

```bash
python test_client.py
```

## Next Steps

Now that you have the Kaltura MCP server up and running, you can:

1. **Explore the available tools and resources** using the MCP Inspector or MCP CLI.
2. **Integrate with Claude or other LLMs** that support the MCP protocol.
3. **Develop custom clients** using the MCP client library.
4. **Extend the server** with additional tools and resources.

For more information, see the following resources:

- [Using with Claude](../../examples/using_with_claude.md)
- [MCP CLI Guide](../../examples/mcp_cli_guide.md)
- [API Reference](../api-reference/README.md)
- [Example Applications](../../examples/README.md)