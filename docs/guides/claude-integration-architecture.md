# Claude Integration Architecture

This document provides an architectural overview of how the Kaltura MCP server integrates with Claude and the Kaltura API.

## Introduction

The Kaltura MCP server acts as a bridge between Claude (or other MCP-compatible AI assistants) and the Kaltura API. It implements the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/mcp), which provides a standardized way for AI models to interact with external systems.

This integration enables Claude to perform media management tasks in Kaltura through natural language conversations, including uploading media, retrieving metadata, searching for content, and managing categories and users.

## System Architecture

The following diagram illustrates the high-level architecture of the Claude-Kaltura integration:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Claude Desktop │◄────►│  Kaltura MCP    │◄────►│  Kaltura API    │
│     or Web      │      │     Server      │      │    Service      │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        ▲                        ▲                        ▲
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    User Input   │      │  Configuration  │      │  Kaltura Media  │
│  & Responses    │      │    Settings     │      │   & Metadata    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Component Descriptions

### 1. Claude Desktop or Web

Claude is an AI assistant developed by Anthropic that supports the Model Context Protocol. It serves as the user interface for the integration, allowing users to:

- Interact with the system using natural language
- Send requests to the Kaltura MCP server
- Receive and display responses in a user-friendly format

Claude interprets user requests, translates them into appropriate MCP tool calls or resource requests, and formats the responses for the user.

### 2. Kaltura MCP Server

The Kaltura MCP server is the core component of the integration. It:

- Implements the Model Context Protocol
- Provides standardized tools and resources for AI models to interact with Kaltura
- Translates Claude's requests into Kaltura API calls
- Processes and formats Kaltura API responses for Claude

The server exposes a set of tools (functions that can be called) and resources (data that can be accessed) that Claude can use to interact with Kaltura.

### 3. Kaltura API Service

The Kaltura API is the official interface to the Kaltura media management platform. It:

- Provides access to Kaltura's media management capabilities
- Handles authentication and authorization
- Processes CRUD operations for media, categories, users, etc.
- Returns data in JSON format

## Data Flow

### 1. User Request Flow

When a user asks Claude to perform a Kaltura-related task, the following data flow occurs:

```
User → Claude → MCP Server → Kaltura API → Media Data → MCP Server → Claude → User
```

1. The user sends a natural language request to Claude (e.g., "Show me my recent videos")
2. Claude interprets the request and calls the appropriate MCP tool or resource
3. The Kaltura MCP server receives the request and translates it into a Kaltura API call
4. The Kaltura API processes the request and returns the data
5. The Kaltura MCP server formats the response according to the MCP specification
6. Claude receives the response and presents it to the user in a readable format

### 2. Authentication Flow

Before any requests can be processed, the Kaltura MCP server must authenticate with the Kaltura API:

```
MCP Server → Kaltura Credentials → Kaltura API → Session Token → MCP Server
```

1. The Kaltura MCP server reads the credentials from its configuration
2. It sends an authentication request to the Kaltura API
3. The Kaltura API validates the credentials and returns a session token
4. The Kaltura MCP server stores the session token for subsequent requests

## Integration Points

### Claude to MCP Server Integration

Claude connects to the MCP server using the Model Context Protocol, which defines a standard way for AI models to interact with external systems. The key aspects of this integration are:

- **Communication Transport**: Claude and the MCP server communicate via stdio (standard input/output) or websocket transport
- **Request Types**: Claude can make several types of requests to the MCP server:
  - List available tools
  - Call a tool with parameters
  - List available resources
  - Read a resource
- **Response Handling**: Claude processes the responses from the MCP server and presents them to the user in a readable format

### MCP Server to Kaltura API Integration

The Kaltura MCP server connects to the Kaltura API using the Kaltura Python client. The key aspects of this integration are:

- **Authentication**: The server authenticates with the Kaltura API using the partner ID, admin secret, and user ID
- **Request Translation**: The server translates MCP requests into Kaltura API calls
- **Response Formatting**: The server formats Kaltura API responses according to the MCP specification
- **Error Handling**: The server handles errors from the Kaltura API and returns appropriate error responses to Claude

## Configuration Architecture

The integration requires configuration at two levels: Claude's configuration and the Kaltura MCP server's configuration.

### Claude Configuration

Claude's configuration specifies how to connect to the Kaltura MCP server:

```
┌─────────────────────────────────────────┐
│           Claude Configuration          │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │       mcpServers Object         │    │
│  │                                 │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │     kaltura Server      │    │    │
│  │  │                         │    │    │
│  │  │  - command              │    │    │
│  │  │  - args                 │    │    │
│  │  │  - env (credentials)    │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

The `mcpServers` object in Claude's configuration specifies:
- The command to run the Kaltura MCP server
- Any command-line arguments
- Environment variables (including Kaltura credentials)

### Kaltura MCP Server Configuration

The Kaltura MCP server's configuration specifies how to connect to the Kaltura API and how to handle requests:

```
┌─────────────────────────────────────────┐
│          Kaltura MCP Configuration      │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        kaltura Section          │    │
│  │  - partner_id                   │    │
│  │  - admin_secret                 │    │
│  │  - user_id                      │    │
│  │  - service_url                  │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        server Section           │    │
│  │  - host                         │    │
│  │  - port                         │    │
│  │  - debug                        │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        logging Section          │    │
│  │  - level                        │    │
│  │  - file                         │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        context Section          │    │
│  │  - default_strategy             │    │
│  │  - max_entries                  │    │
│  │  - max_context_size             │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

The configuration includes:
- **kaltura section**: Kaltura API credentials and endpoint
- **server section**: Server host, port, and debug settings
- **logging section**: Logging level and file path
- **context section**: Context management strategy and limits

## Available Tools and Resources

### Tools

The Kaltura MCP Server exposes the following tools to Claude:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `kaltura.media.list` | List media entries | `page_size`, `filter` |
| `kaltura.media.get` | Get media entry details | `entryId` |
| `kaltura.media.upload` | Upload media file | `file_path`, `title`, `description` |
| `kaltura.media.update` | Update media metadata | `entryId`, `metadata` |
| `kaltura.media.delete` | Delete media entry | `entryId` |
| `kaltura.category.list` | List categories | `page_size`, `filter` |
| `kaltura.category.get` | Get category details | `categoryId` |
| `kaltura.category.add` | Add new category | `name`, `parentId` |
| `kaltura.category.update` | Update category | `categoryId`, `metadata` |
| `kaltura.category.delete` | Delete category | `categoryId` |
| `kaltura.user.list` | List users | `page_size`, `filter` |
| `kaltura.user.get` | Get user details | `userId` |
| `kaltura.user.add` | Add new user | `userId`, `email`, `firstName`, `lastName` |
| `kaltura.user.update` | Update user | `userId`, `metadata` |
| `kaltura.user.delete` | Delete user | `userId` |

### Resources

The Kaltura MCP Server exposes the following resources to Claude:

| Resource URI | Description |
|--------------|-------------|
| `kaltura://media/{entryId}` | Media entry metadata |
| `kaltura://media/list?page_size={size}` | List of media entries |
| `kaltura://category/{categoryId}` | Category metadata |
| `kaltura://category/list?page_size={size}` | List of categories |
| `kaltura://user/{userId}` | User metadata |
| `kaltura://user/list?page_size={size}` | List of users |

## Security Considerations

When implementing the Claude-Kaltura integration, consider the following security aspects:

### 1. Authentication and Authorization

- The Kaltura MCP server uses the Kaltura admin secret for authentication, which provides full access to the Kaltura account
- Store credentials securely, preferably using environment variables
- Consider using a dedicated Kaltura user with limited permissions for the integration

### 2. Access Control

- The MCP server inherits the access control settings from the Kaltura account
- Ensure that the user specified in the configuration has appropriate permissions
- Configure media entries with proper access control profiles

### 3. Data Privacy

- Media metadata is shared with Claude during conversations
- Claude may store conversation history according to its privacy policy
- Consider data privacy regulations when sharing sensitive media information

## Conclusion

The architecture described in this document enables Claude to interact with Kaltura through the Model Context Protocol. By implementing this architecture, organizations can provide a natural language interface to their Kaltura media library, making media management more accessible and efficient.

For implementation details, refer to the [Claude Integration Setup Guide](claude-integration-setup.md) and [Claude Integration Best Practices](claude-integration-best-practices.md).