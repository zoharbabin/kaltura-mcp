# Configuring Kaltura-MCP Server

This guide explains how to configure the Kaltura-MCP Server for your environment.

## Configuration File

The Kaltura-MCP Server uses a YAML configuration file to store settings. By default, it looks for a file named `config.yaml` in the current working directory.

### Creating a Configuration File

You can create a configuration file by copying the example configuration:

```bash
cp config.yaml.example config.yaml
```

Then edit the `config.yaml` file with your preferred text editor to add your Kaltura API credentials and other settings.

### Configuration File Structure

The configuration file has the following structure:

```yaml
kaltura:
  partner_id: 123456
  admin_secret: "your-admin-secret"
  user_id: "your-user-id"
  service_url: "https://www.kaltura.com"
  session_duration: 86400  # 24 hours in seconds
  session_privileges: "disableentitlement"

server:
  log_level: "INFO"
  transport: "stdio"
  port: 8000
  host: "127.0.0.1"

context:
  default_strategy: "selective"
  pagination:
    default_page_size: 10
    max_page_size: 100
  summarization:
    max_length: 1000
    ellipsis: "..."
  selective:
    default_fields: ["id", "name", "description", "createdAt", "updatedAt"]
```

### Configuration Options

#### Kaltura Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `partner_id` | Your Kaltura partner ID | None | Yes |
| `admin_secret` | Your Kaltura admin secret | None | Yes |
| `user_id` | Your Kaltura user ID | None | Yes |
| `service_url` | The URL of the Kaltura API service | "https://www.kaltura.com" | No |
| `session_duration` | Duration of the Kaltura session in seconds | 86400 (24 hours) | No |
| `session_privileges` | Privileges for the Kaltura session | "disableentitlement" | No |

#### Server Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | "INFO" | No |
| `transport` | Transport method (stdio, websocket) | "stdio" | No |
| `port` | Port for the websocket transport | 8000 | No (only for websocket) |
| `host` | Host for the websocket transport | "127.0.0.1" | No (only for websocket) |

#### Context Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `default_strategy` | Default context management strategy (pagination, summarization, selective) | "selective" | No |
| `pagination.default_page_size` | Default page size for pagination | 10 | No |
| `pagination.max_page_size` | Maximum page size for pagination | 100 | No |
| `summarization.max_length` | Maximum length for summarized text | 1000 | No |
| `summarization.ellipsis` | String to use for truncated text | "..." | No |
| `selective.default_fields` | Default fields to include in selective context | ["id", "name", "description", "createdAt", "updatedAt"] | No |

## Environment Variables

You can also configure the Kaltura-MCP Server using environment variables. Environment variables take precedence over the configuration file.

### Available Environment Variables

| Environment Variable | Configuration Option | Example |
|----------------------|----------------------|---------|
| `KALTURA_PARTNER_ID` | kaltura.partner_id | `export KALTURA_PARTNER_ID=123456` |
| `KALTURA_ADMIN_SECRET` | kaltura.admin_secret | `export KALTURA_ADMIN_SECRET=your-admin-secret` |
| `KALTURA_USER_ID` | kaltura.user_id | `export KALTURA_USER_ID=your-user-id` |
| `KALTURA_SERVICE_URL` | kaltura.service_url | `export KALTURA_SERVICE_URL=https://www.kaltura.com` |
| `KALTURA_SESSION_DURATION` | kaltura.session_duration | `export KALTURA_SESSION_DURATION=86400` |
| `KALTURA_SESSION_PRIVILEGES` | kaltura.session_privileges | `export KALTURA_SESSION_PRIVILEGES=disableentitlement` |
| `KALTURA_MCP_LOG_LEVEL` | server.log_level | `export KALTURA_MCP_LOG_LEVEL=INFO` |
| `KALTURA_MCP_TRANSPORT` | server.transport | `export KALTURA_MCP_TRANSPORT=stdio` |
| `KALTURA_MCP_PORT` | server.port | `export KALTURA_MCP_PORT=8000` |
| `KALTURA_MCP_HOST` | server.host | `export KALTURA_MCP_HOST=127.0.0.1` |

## Configuration Loading Order

The configuration is loaded in the following order, with later sources overriding earlier ones:

1. Default values
2. Configuration file (`config.yaml`)
3. Environment variables

## Testing Your Configuration

You can test your configuration by running the server:

```bash
kaltura-mcp
```

If the configuration is valid, you should see output similar to:

```
INFO - kaltura_mcp.server - Kaltura MCP Server initialized
INFO - kaltura_mcp.server - Registered 15 tool handlers
INFO - kaltura_mcp.server - Registered 6 resource handlers
INFO - kaltura_mcp.server - Starting Kaltura MCP Server
```

## Next Steps

After configuring the Kaltura-MCP Server, you can proceed to the [Quick Start](quick-start.md) guide to learn how to use it.