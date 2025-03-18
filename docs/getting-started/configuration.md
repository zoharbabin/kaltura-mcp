# Configuring Kaltura-MCP Server

This guide explains how to configure the Kaltura-MCP Server for your environment.

## Configuration File

The Kaltura-MCP Server supports both YAML and JSON configuration files. By default, it looks for a file named `config.yaml` in the current working directory, but you can specify a different file using the `KALTURA_MCP_CONFIG` environment variable.

### Creating a Configuration File

You can create a configuration file by copying the example configuration:

```bash
cp config.yaml.example config.yaml
```

Then edit the `config.yaml` file with your preferred text editor to add your Kaltura API credentials and other settings.

### Configuration File Formats

The configuration file can be in either YAML or JSON format. The system automatically detects the format based on the file extension (`.yaml`, `.yml`, or `.json`).

### Configuration File Structure

The configuration file has the following structure:

```yaml
# Kaltura API credentials
kaltura:
  partner_id: 123456  # Your Kaltura partner ID
  admin_secret: "your-admin-secret"  # Your Kaltura admin secret
  user_id: "your-user-id"  # Your Kaltura user ID
  service_url: "https://www.kaltura.com/api_v3"  # Kaltura API endpoint

# Server configuration
server:
  host: "127.0.0.1"  # Server host
  port: 8000  # Server port
  debug: false  # Enable debug mode
  log_level: "INFO"  # Logging level
  transport: "stdio"  # Transport method (stdio, websocket)

# Logging configuration
logging:
  level: "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  file: "kaltura-mcp.log"  # Log file path (optional)

# Context management configuration
context:
  default_strategy: "pagination"  # Default context management strategy (pagination, summarization, selective)
  max_entries: 100  # Maximum number of entries to return in a single response
  max_context_size: 10000  # Maximum context size in tokens
```

### Configuration Options

#### Kaltura Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `partner_id` | Your Kaltura partner ID | None | Yes |
| `admin_secret` | Your Kaltura admin secret | None | Yes |
| `user_id` | Your Kaltura user ID | "admin" | No |
| `service_url` | The URL of the Kaltura API service | "https://www.kaltura.com/api_v3" | No |

#### Server Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | "INFO" | No |
| `transport` | Transport method (stdio, websocket) | "stdio" | No |
| `port` | Port for the websocket transport | 8000 | No |
| `host` | Host for the websocket transport | "127.0.0.1" | No |
| `debug` | Enable debug mode | false | No |

#### Logging Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | "INFO" | No |
| `file` | Path to log file | None | No |

#### Context Section

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `default_strategy` | Default context management strategy (pagination, summarization, selective) | "pagination" | No |
| `max_entries` | Maximum number of entries to return in a single response | 100 | No |
| `max_context_size` | Maximum context size in tokens | 10000 | No |

## Environment Variables

You can also configure the Kaltura-MCP Server using environment variables. Environment variables take precedence over the configuration file.

### Available Environment Variables

| Environment Variable | Configuration Option | Example |
|----------------------|----------------------|---------|
| `KALTURA_MCP_CONFIG` | Path to config file | `export KALTURA_MCP_CONFIG=/path/to/config.yaml` |
| `KALTURA_PARTNER_ID` | kaltura.partner_id | `export KALTURA_PARTNER_ID=123456` |
| `KALTURA_ADMIN_SECRET` | kaltura.admin_secret | `export KALTURA_ADMIN_SECRET=your-admin-secret` |
| `KALTURA_USER_ID` | kaltura.user_id | `export KALTURA_USER_ID=your-user-id` |
| `KALTURA_SERVICE_URL` | kaltura.service_url | `export KALTURA_SERVICE_URL=https://www.kaltura.com/api_v3` |
| `KALTURA_MCP_LOG_LEVEL` | server.log_level | `export KALTURA_MCP_LOG_LEVEL=INFO` |
| `KALTURA_MCP_TRANSPORT` | server.transport | `export KALTURA_MCP_TRANSPORT=stdio` |
| `KALTURA_MCP_PORT` | server.port | `export KALTURA_MCP_PORT=8000` |
| `KALTURA_MCP_HOST` | server.host | `export KALTURA_MCP_HOST=127.0.0.1` |
| `KALTURA_MCP_DEBUG` | server.debug | `export KALTURA_MCP_DEBUG=true` |
| `KALTURA_MCP_LOG_FILE` | logging.file | `export KALTURA_MCP_LOG_FILE=kaltura-mcp.log` |
| `KALTURA_MCP_CONTEXT_STRATEGY` | context.default_strategy | `export KALTURA_MCP_CONTEXT_STRATEGY=pagination` |
| `KALTURA_MCP_MAX_ENTRIES` | context.max_entries | `export KALTURA_MCP_MAX_ENTRIES=100` |
| `KALTURA_MCP_MAX_CONTEXT_SIZE` | context.max_context_size | `export KALTURA_MCP_MAX_CONTEXT_SIZE=10000` |

## Configuration for Integration Tests

For integration tests, a separate configuration file is used. By default, the system looks for `tests/integration/config.json`, but you can specify a different file using the `KALTURA_MCP_TEST_CONFIG` environment variable.

You can create this file by copying the example:

```bash
cp tests/integration/config.json.example tests/integration/config.json
```

Then edit the file with your test environment credentials.

## Configuration Loading Order

The configuration is loaded in the following order, with later sources overriding earlier ones:

1. Default values
2. Configuration file (specified by `KALTURA_MCP_CONFIG` or default `config.yaml`)
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