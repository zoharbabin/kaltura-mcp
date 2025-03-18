# Server API

This page documents the main server API for the Kaltura-MCP Server.

## Overview

The Kaltura-MCP Server is built on top of the fast-mcp framework and implements the Model Context Protocol (MCP). It provides a server that can be used by MCP clients to interact with the Kaltura API.

## Server Architecture

The server architecture consists of the following components:

1. **KalturaMcpServer**: The main server class that initializes and runs the MCP server
2. **KalturaClientWrapper**: A wrapper around the kaltura-client-py SDK that provides a simplified interface
3. **Tool Handlers**: Classes that implement the MCP tool interface for different Kaltura API operations
4. **Resource Handlers**: Classes that implement the MCP resource interface for different Kaltura API entities
5. **Context Management Strategies**: Classes that optimize data for LLM consumption

## KalturaMcpServer Class

The `KalturaMcpServer` class is the main entry point for the server. It initializes the server, registers tool and resource handlers, and handles MCP requests.

### Initialization

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
```

### Server Initialization

```python
async def initialize(self):
    """Initialize the server components."""
    # Initialize Kaltura client
    from kaltura_mcp.kaltura.client import KalturaClientWrapper
    self.kaltura_client = KalturaClientWrapper(self.config)
    await self.kaltura_client.initialize()
    
    # Register tool handlers
    self._register_tool_handlers()
    
    # Register resource handlers
    self._register_resource_handlers()
    
    logger.info("Kaltura MCP Server initialized")
```

### Tool Handler Registration

```python
def _register_tool_handlers(self):
    """Register all tool handlers."""
    # Import tool handlers
    from kaltura_mcp.tools.media import (
        MediaListToolHandler,
        MediaGetToolHandler,
        MediaUploadToolHandler,
        MediaUpdateToolHandler,
        MediaDeleteToolHandler
    )
    from kaltura_mcp.tools.category import (
        CategoryListToolHandler,
        CategoryGetToolHandler,
        CategoryAddToolHandler,
        CategoryUpdateToolHandler,
        CategoryDeleteToolHandler
    )
    from kaltura_mcp.tools.user import (
        UserListToolHandler,
        UserGetToolHandler,
        UserAddToolHandler,
        UserUpdateToolHandler,
        UserDeleteToolHandler
    )
    
    # Register media tools
    self.tool_handlers["kaltura.media.list"] = MediaListToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.media.get"] = MediaGetToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.media.upload"] = MediaUploadToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.media.update"] = MediaUpdateToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.media.delete"] = MediaDeleteToolHandler(self.kaltura_client)
    
    # Register category tools
    self.tool_handlers["kaltura.category.list"] = CategoryListToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.category.get"] = CategoryGetToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.category.add"] = CategoryAddToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.category.update"] = CategoryUpdateToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.category.delete"] = CategoryDeleteToolHandler(self.kaltura_client)
    
    # Register user tools
    self.tool_handlers["kaltura.user.list"] = UserListToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.user.get"] = UserGetToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.user.add"] = UserAddToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.user.update"] = UserUpdateToolHandler(self.kaltura_client)
    self.tool_handlers["kaltura.user.delete"] = UserDeleteToolHandler(self.kaltura_client)
    
    logger.info(f"Registered {len(self.tool_handlers)} tool handlers")
```

### Resource Handler Registration

```python
def _register_resource_handlers(self):
    """Register all resource handlers."""
    # Import resource handlers
    from kaltura_mcp.resources.media import MediaEntryResourceHandler, MediaListResourceHandler
    from kaltura_mcp.resources.category import CategoryResourceHandler, CategoryListResourceHandler
    from kaltura_mcp.resources.user import UserResourceHandler, UserListResourceHandler
    
    # Register media resources
    self.resource_handlers["media_entry"] = MediaEntryResourceHandler(self.kaltura_client)
    self.resource_handlers["media_list"] = MediaListResourceHandler(self.kaltura_client)
    
    # Register category resources
    self.resource_handlers["category"] = CategoryResourceHandler(self.kaltura_client)
    self.resource_handlers["category_list"] = CategoryListResourceHandler(self.kaltura_client)
    
    # Register user resources
    self.resource_handlers["user"] = UserResourceHandler(self.kaltura_client)
    self.resource_handlers["user_list"] = UserListResourceHandler(self.kaltura_client)
    
    logger.info(f"Registered {len(self.resource_handlers)} resource handlers")
```

### MCP Handler Registration

```python
async def run(self):
    """Run the server."""
    # Register MCP handlers
    
    # List tools handler
    async def list_tools_handler() -> list[types.Tool]:
        """List all available tools."""
        return [handler.get_tool_definition() for handler in self.tool_handlers.values()]
    
    # Call tool handler
    async def call_tool_handler(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Call a tool with the given name and arguments."""
        if name not in self.tool_handlers:
            raise ValueError(f"Unknown tool: {name}")
        
        handler = self.tool_handlers[name]
        return await handler.handle(arguments)
    
    # List resources handler
    async def list_resources_handler() -> list[types.Resource]:
        """List all available resources."""
        return [handler.get_resource_definition() for handler in self.resource_handlers.values()]
    
    # Read resource handler
    async def read_resource_handler(uri: str) -> str | bytes:
        """Read a resource with the given URI."""
        # Find the appropriate handler based on URI pattern
        for handler in self.resource_handlers.values():
            if handler.matches_uri(uri):
                return await handler.handle(uri)
        
        raise ValueError(f"Unknown resource: {uri}")
    
    # Register handlers with the app
    self.app.list_tools = list_tools_handler
    self.app.call_tool = call_tool_handler
    self.app.list_resources = list_resources_handler
    self.app.read_resource = read_resource_handler
    
    logger.info("Starting Kaltura MCP Server")
    
    # Run the server using stdio transport
    async with stdio_server() as streams:
        await self.app.run(
            streams[0], streams[1], self.app.create_initialization_options()
        )
```

## MCP Protocol Handlers

The Kaltura-MCP Server implements the following MCP protocol handlers:

### List Tools Handler

The list tools handler returns a list of all available tools:

```python
async def list_tools_handler() -> list[types.Tool]:
    """List all available tools."""
    return [handler.get_tool_definition() for handler in self.tool_handlers.values()]
```

Example response:

```json
[
  {
    "name": "kaltura.media.list",
    "description": "List media entries with filtering and pagination",
    "inputSchema": {
      "type": "object",
      "properties": {
        "page_size": {
          "type": "integer",
          "description": "Number of entries per page",
          "default": 10
        },
        "page_index": {
          "type": "integer",
          "description": "Page index (1-based)",
          "default": 1
        },
        "filter": {
          "type": "object",
          "description": "Filter criteria",
          "properties": {
            "nameLike": {
              "type": "string",
              "description": "Filter entries by name (substring match)"
            }
          }
        }
      }
    }
  },
  // More tools...
]
```

### Call Tool Handler

The call tool handler calls a tool with the given name and arguments:

```python
async def call_tool_handler(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Call a tool with the given name and arguments."""
    if name not in self.tool_handlers:
        raise ValueError(f"Unknown tool: {name}")
    
    handler = self.tool_handlers[name]
    return await handler.handle(arguments)
```

Example request:

```json
{
  "name": "kaltura.media.list",
  "arguments": {
    "page_size": 5,
    "filter": {
      "nameLike": "test"
    }
  }
}
```

Example response:

```json
[
  {
    "type": "text",
    "text": "{\"objects\":[{\"id\":\"0_abc123\",\"name\":\"Test Video 1\"},{\"id\":\"0_def456\",\"name\":\"Test Video 2\"}],\"totalCount\":2,\"pageSize\":5,\"pageIndex\":1,\"nextPageAvailable\":false}"
  }
]
```

### List Resources Handler

The list resources handler returns a list of all available resources:

```python
async def list_resources_handler() -> list[types.Resource]:
    """List all available resources."""
    return [handler.get_resource_definition() for handler in self.resource_handlers.values()]
```

Example response:

```json
[
  {
    "uri": "kaltura://media/{entry_id}",
    "description": "Get details of a specific media entry",
    "mimeType": "application/json"
  },
  {
    "uri": "kaltura://media/list",
    "description": "List media entries with filtering and pagination",
    "mimeType": "application/json"
  },
  // More resources...
]
```

### Read Resource Handler

The read resource handler reads a resource with the given URI:

```python
async def read_resource_handler(uri: str) -> str | bytes:
    """Read a resource with the given URI."""
    # Find the appropriate handler based on URI pattern
    for handler in self.resource_handlers.values():
        if handler.matches_uri(uri):
            return await handler.handle(uri)
    
    raise ValueError(f"Unknown resource: {uri}")
```

Example request:

```
kaltura://media/list?page_size=5&name_like=test
```

Example response:

```json
{
  "objects": [
    {
      "id": "0_abc123",
      "name": "Test Video 1",
      "description": "This is test video 1",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z"
    },
    {
      "id": "0_def456",
      "name": "Test Video 2",
      "description": "This is test video 2",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z"
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}
```

## Error Handling

The Kaltura-MCP Server implements error handling to translate Kaltura API errors to MCP errors:

```python
try:
    # Call Kaltura API
    result = await self.kaltura_client.some_method()
    return result
except KalturaException as e:
    # Translate Kaltura error to MCP error
    if e.code == "INVALID_KS":
        raise McpError(ErrorCode.Unauthorized, "Invalid Kaltura session")
    elif e.code == "RESOURCE_NOT_FOUND":
        raise McpError(ErrorCode.NotFound, f"Resource not found: {e.message}")
    else:
        raise McpError(ErrorCode.InternalError, f"Kaltura API error: {e.message}")
```

## Server Configuration

The server configuration is loaded from a YAML file and environment variables:

```python
def load_config():
    """Load configuration from file and environment variables."""
    # Default configuration
    config = {
        "kaltura": {
            "partner_id": None,
            "admin_secret": None,
            "user_id": None,
            "service_url": "https://www.kaltura.com",
            "session_duration": 86400,
            "session_privileges": "disableentitlement"
        },
        "server": {
            "log_level": "INFO",
            "transport": "stdio",
            "port": 8000,
            "host": "127.0.0.1"
        },
        "context": {
            "default_strategy": "selective",
            "pagination": {
                "default_page_size": 10,
                "max_page_size": 100
            },
            "summarization": {
                "max_length": 1000,
                "ellipsis": "..."
            },
            "selective": {
                "default_fields": ["id", "name", "description", "createdAt", "updatedAt"]
            }
        }
    }
    
    # Load configuration from file
    config_file = os.environ.get("KALTURA_MCP_CONFIG", "config.yaml")
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            file_config = yaml.safe_load(f)
            if file_config:
                config = deep_merge(config, file_config)
    
    # Override with environment variables
    if os.environ.get("KALTURA_PARTNER_ID"):
        config["kaltura"]["partner_id"] = int(os.environ.get("KALTURA_PARTNER_ID"))
    if os.environ.get("KALTURA_ADMIN_SECRET"):
        config["kaltura"]["admin_secret"] = os.environ.get("KALTURA_ADMIN_SECRET")
    if os.environ.get("KALTURA_USER_ID"):
        config["kaltura"]["user_id"] = os.environ.get("KALTURA_USER_ID")
    if os.environ.get("KALTURA_SERVICE_URL"):
        config["kaltura"]["service_url"] = os.environ.get("KALTURA_SERVICE_URL")
    if os.environ.get("KALTURA_SESSION_DURATION"):
        config["kaltura"]["session_duration"] = int(os.environ.get("KALTURA_SESSION_DURATION"))
    if os.environ.get("KALTURA_SESSION_PRIVILEGES"):
        config["kaltura"]["session_privileges"] = os.environ.get("KALTURA_SESSION_PRIVILEGES")
    if os.environ.get("KALTURA_MCP_LOG_LEVEL"):
        config["server"]["log_level"] = os.environ.get("KALTURA_MCP_LOG_LEVEL")
    if os.environ.get("KALTURA_MCP_TRANSPORT"):
        config["server"]["transport"] = os.environ.get("KALTURA_MCP_TRANSPORT")
    if os.environ.get("KALTURA_MCP_PORT"):
        config["server"]["port"] = int(os.environ.get("KALTURA_MCP_PORT"))
    if os.environ.get("KALTURA_MCP_HOST"):
        config["server"]["host"] = os.environ.get("KALTURA_MCP_HOST")
    
    return config
```

## Running the Server

The server can be run using the `main` function:

```python
def main():
    """Main entry point for the server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load configuration
    config = load_config()
    
    # Create and run server
    server = KalturaMcpServer(config)
    
    async def run_server():
        await server.initialize()
        await server.run()
    
    anyio.run(run_server)
```

## Extending the Server

The server can be extended by adding new tool and resource handlers:

### Adding a New Tool Handler

```python
from kaltura_mcp.tools.base import BaseToolHandler

class MyCustomToolHandler(BaseToolHandler):
    """Custom tool handler."""
    
    def get_name(self):
        """Get the tool name."""
        return "kaltura.custom.tool"
    
    def get_description(self):
        """Get the tool description."""
        return "My custom tool"
    
    def get_input_schema(self):
        """Get the tool input schema."""
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1"
                },
                "param2": {
                    "type": "integer",
                    "description": "Parameter 2"
                }
            }
        }
    
    async def handle(self, arguments):
        """Handle the tool call."""
        # Implement your custom logic here
        return [
            {
                "type": "text",
                "text": "Custom tool result"
            }
        ]
```

Then register your custom tool handler in the server:

```python
# In server.py
self.tool_handlers["kaltura.custom.tool"] = MyCustomToolHandler(self.kaltura_client)
```

### Adding a New Resource Handler

```python
from kaltura_mcp.resources.base import BaseResourceHandler

class MyCustomResourceHandler(BaseResourceHandler):
    """Custom resource handler."""
    
    def get_uri_pattern(self):
        """Get the resource URI pattern."""
        return "kaltura://custom/{id}"
    
    def get_description(self):
        """Get the resource description."""
        return "My custom resource"
    
    def get_mime_type(self):
        """Get the resource MIME type."""
        return "application/json"
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract ID
        import re
        match = re.match(r"^kaltura://custom/(?P<id>[^/]+)$", uri)
        if not match:
            raise ValueError(f"Invalid URI: {uri}")
        
        id = match.group("id")
        
        # Implement your custom logic here
        result = {"id": id, "name": "Custom Resource"}
        
        return json.dumps(result)
```

Then register your custom resource handler in the server:

```python
# In server.py
self.resource_handlers["custom"] = MyCustomResourceHandler(self.kaltura_client)