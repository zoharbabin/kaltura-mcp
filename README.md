# Kaltura Model Context Protocol (MCP) Server

The Kaltura MCP Server is an implementation of the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/mcp) that provides AI models with access to Kaltura's media management capabilities.

## Overview

This server enables AI models to:

- Upload media to Kaltura
- Retrieve media metadata
- Search for media
- Manage categories
- Manage users and permissions

By implementing the Model Context Protocol, this server allows AI models to interact with Kaltura's API in a standardized way, making it easier to integrate Kaltura's capabilities into AI workflows.

## Requirements

- **Python**: 3.10 or higher (3.10, 3.11, 3.12 are officially supported)
- **Operating Systems**: Linux, macOS, Windows
- **Dependencies**: See `pyproject.toml` for a complete list

## Repository Structure

The `kaltura-mcp-public` repository contains the complete, self-contained Kaltura MCP server implementation, including:

- All necessary code
- Comprehensive documentation
- Docker support
- Setup script
- Example clients
- Test scripts

## Installation

### Using Docker

#### Option 1: Using Pre-built Docker Image

The easiest way to get started is with our pre-built multi-architecture Docker image (supports both x86_64/amd64 and ARM64/Apple Silicon):

```bash
# Pull the latest image
docker pull ghcr.io/zoharbabin/kaltura-mcp:latest

# Create a config file
cp config.yaml.example config.yaml
# Edit config.yaml with your Kaltura API credentials

# Run the container
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml ghcr.io/zoharbabin/kaltura-mcp:latest
```

#### Option 2: Building Locally with Docker Compose

Alternatively, you can build the image locally:

```bash
# Clone the repository
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp

# Build and run with Docker Compose
docker-compose up
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp

# Create a virtual environment (Python 3.10 or higher required)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure the server
cp config.yaml.example config.yaml
# Edit config.yaml with your Kaltura API credentials

# Run the server
python -m kaltura_mcp.server
```

## Configuration

The Kaltura MCP Server supports a unified configuration system that works with both YAML and JSON formats. To get started:

1. Copy `config.yaml.example` to `config.yaml` and edit it with your Kaltura API credentials:

```yaml
kaltura:
  partner_id: YOUR_PARTNER_ID
  admin_secret: YOUR_ADMIN_SECRET
  user_id: YOUR_USER_ID
  service_url: https://www.kaltura.com/api_v3
```

2. You can also use environment variables for configuration:

```bash
export KALTURA_PARTNER_ID=YOUR_PARTNER_ID
export KALTURA_ADMIN_SECRET=YOUR_ADMIN_SECRET
export KALTURA_USER_ID=YOUR_USER_ID
```

For more detailed configuration options, see the [Configuration Guide](docs/getting-started/configuration.md).

## Usage

### With Claude

To use the Kaltura MCP Server with Claude, see the [Using with Claude](examples/using_with_claude.md) guide.

### With the MCP CLI

To use the Kaltura MCP Server with the MCP CLI, see the [Using with MCP CLI](examples/using_with_mcp_cli.md) guide.

### Programmatically

To use the Kaltura MCP Server programmatically, see the [examples](examples/) directory.

## Available Tools

The Kaltura MCP Server provides the following tools:

- `media_upload`: Upload media files to Kaltura
- `media_get`: Retrieve media metadata
- `media_update`: Update media metadata
- `media_delete`: Delete media
- `category_list`: List categories
- `category_get`: Retrieve category metadata
- `category_add`: Add a new category
- `category_update`: Update category metadata
- `category_delete`: Delete a category
- `user_list`: List users
- `user_get`: Retrieve user metadata
- `user_add`: Add a new user
- `user_update`: Update user metadata
- `user_delete`: Delete a user

## Available Resources

The Kaltura MCP Server provides the following resources:

- `media://{entry_id}`: Media entry metadata
- `category://{category_id}`: Category metadata
- `user://{user_id}`: User metadata

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.