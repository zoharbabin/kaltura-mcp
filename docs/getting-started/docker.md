# Using Docker with Kaltura MCP

This guide explains how to use Docker with the Kaltura MCP server for development, testing, and deployment.

## Prerequisites

Before you begin, ensure you have the following:

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed (optional, but recommended)
- A Kaltura account with API access

## Quick Start

### Using Pre-built Multi-architecture Docker Image

The easiest way to get started is with our pre-built multi-architecture Docker image from GitHub Container Registry, which supports both x86_64/amd64 and ARM64/Apple Silicon architectures:

```bash
# Pull the latest image
docker pull ghcr.io/zoharbabin/kaltura-mcp:latest

# Create a configuration file
cp config.yaml.example config.yaml
# Edit config.yaml with your Kaltura API credentials

# Run the container with HTTP transport
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=http ghcr.io/zoharbabin/kaltura-mcp:latest
```

### Using Docker Compose

Alternatively, you can build the image locally using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp

# Create a configuration file
cp config.yaml.example config.yaml
# Edit config.yaml with your Kaltura API credentials

# Build and run the Docker container with HTTP transport
docker-compose up kaltura-mcp-http
```

## Transport Mechanisms

The Kaltura MCP server supports three transport mechanisms:

1. **STDIO Transport**: For direct process-to-process communication
2. **HTTP Transport**: For web-based communication
3. **SSE Transport**: For Server-Sent Events based communication

### Using STDIO Transport

The STDIO transport is useful for direct process-to-process communication:

```bash
# Using Docker run
docker run -i -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=stdio ghcr.io/zoharbabin/kaltura-mcp:latest

# Using Docker Compose
docker-compose up kaltura-mcp-stdio
```

### Using HTTP Transport

The HTTP transport is useful for web-based communication:

```bash
# Using Docker run
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=http ghcr.io/zoharbabin/kaltura-mcp:latest

# Using Docker Compose
docker-compose up kaltura-mcp-http
```

### Using SSE Transport

The SSE transport is useful for Server-Sent Events based communication:

```bash
# Using Docker run
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=sse ghcr.io/zoharbabin/kaltura-mcp:latest

# Using Docker Compose
docker-compose up kaltura-mcp-sse
```

## Docker Configuration

### Dockerfile

The Kaltura MCP project includes a Dockerfile that creates a lightweight image with all necessary dependencies:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy source code first
COPY . .

# Run setup script in non-interactive mode
RUN python setup_kaltura_mcp.py --non-interactive --skip-venv --dev-deps

# Expose ports for HTTP and SSE transports
EXPOSE 8000

# Set default transport to stdio
ENV KALTURA_MCP_TRANSPORT=stdio

# Run server with configurable transport
CMD ["sh", "-c", "kaltura-mcp"]
```

### Docker Compose

The `docker-compose.yml` file provides a convenient way to run the Docker container with different transport mechanisms:

```yaml
version: '3'

services:
  # Base service with shared configuration
  kaltura-mcp-base: &kaltura-mcp-base
    build: .
    volumes:
      - ./config.yaml:/app/config.yaml
    environment:
      - PYTHONUNBUFFERED=1

  # STDIO transport service
  kaltura-mcp-stdio:
    <<: *kaltura-mcp-base
    environment:
      - PYTHONUNBUFFERED=1
      - KALTURA_MCP_TRANSPORT=stdio
    stdin_open: true
    tty: true

  # HTTP transport service
  kaltura-mcp-http:
    <<: *kaltura-mcp-base
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - KALTURA_MCP_TRANSPORT=http
      - KALTURA_MCP_HOST=0.0.0.0
      - KALTURA_MCP_PORT=8000

  # SSE transport service
  kaltura-mcp-sse:
    <<: *kaltura-mcp-base
    ports:
      - "8001:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - KALTURA_MCP_TRANSPORT=sse
      - KALTURA_MCP_HOST=0.0.0.0
      - KALTURA_MCP_PORT=8000
```

This configuration:
- Defines a base service with shared configuration
- Creates separate services for each transport mechanism
- Maps appropriate ports for HTTP and SSE transports
- Sets environment variables for each transport mechanism
- Enables stdin and tty for the STDIO transport

## Building the Docker Image Manually

If you prefer to build and run the Docker image manually:

```bash
# Build the Docker image
docker build -t kaltura-mcp .

# Run the Docker container with HTTP transport
docker run -p 8000:8000 -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=http kaltura-mcp
```

### Building Multi-Architecture Docker Images

The project includes a script to build multi-architecture Docker images for all transport types:

```bash
# Build images locally (no push)
./build-transport-docker-images.sh

# Build and push images to a registry
./build-transport-docker-images.sh --push --registry your-registry --owner your-username

# For GitHub Container Registry, authenticate first
export CR_PAT=YOUR_GITHUB_TOKEN
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
./build-transport-docker-images.sh --push
```

The script supports the following options:

- `--push`: Push images to the registry
- `--registry`: Specify the registry (default: ghcr.io)
- `--owner`: Specify the owner/organization (default: zoharbabin)
- `--repo`: Specify the repository name (default: kaltura-mcp)
- `--platforms`: Specify the platforms to build for (default: linux/amd64,linux/arm64)

## Configuration

### Using a Configuration File

When using Docker, you need to configure the Kaltura MCP server by mounting a configuration file into the container. The configuration file should be in YAML or JSON format and contain your Kaltura API credentials and other settings.

For Docker, it's important to set the host to `0.0.0.0` in your configuration file to allow connections from outside the container:

```yaml
server:
  transport: "http"  # Transport type (stdio, http, sse)
  host: "0.0.0.0"    # Important: Use 0.0.0.0 to allow external connections
  port: 8000
```

### Using Environment Variables

Alternatively, you can configure the Kaltura MCP server using environment variables. This is particularly useful for sensitive information that you don't want to store in a configuration file:

```bash
# Run the container with environment variables
docker run -p 8000:8000 \
  -e KALTURA_PARTNER_ID=123456 \
  -e KALTURA_ADMIN_SECRET=your-admin-secret \
  -e KALTURA_USER_ID=your-user-id \
  -e KALTURA_SERVICE_URL=https://www.kaltura.com/api_v3 \
  -e KALTURA_MCP_TRANSPORT=http \
  -e KALTURA_MCP_HOST=0.0.0.0 \
  -e KALTURA_MCP_PORT=8000 \
  ghcr.io/zoharbabin/kaltura-mcp:latest
```

Available environment variables:

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `KALTURA_PARTNER_ID` | Your Kaltura partner ID | None (required) |
| `KALTURA_ADMIN_SECRET` | Your Kaltura admin secret | None (required) |
| `KALTURA_USER_ID` | Your Kaltura user ID | None (required) |
| `KALTURA_SERVICE_URL` | Kaltura API endpoint | `https://www.kaltura.com/api_v3` |
| `KALTURA_MCP_TRANSPORT` | Transport type | `stdio` |
| `KALTURA_MCP_HOST` | Server host | `0.0.0.0` |
| `KALTURA_MCP_PORT` | Server port | `8000` |
| `KALTURA_MCP_DEBUG` | Enable debug mode | `false` |
| `LOGGING_LEVEL` | Logging level | `INFO` |
| `CONTEXT_DEFAULT_STRATEGY` | Default context management strategy | `pagination` |
| `CONTEXT_MAX_ENTRIES` | Maximum number of entries | `100` |
| `CONTEXT_MAX_CONTEXT_SIZE` | Maximum context size in tokens | `10000` |

## Running Tests in Docker

To run tests inside the Docker container:

```bash
# Run all tests
docker run --rm kaltura-mcp python run_tests.py

# Run specific tests
docker run --rm kaltura-mcp python run_tests.py --lint --type-check

# Run transport-specific tests
docker run --rm kaltura-mcp python run_tests.py -k "test_transport"
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with the mounted configuration file, ensure that the file has the correct permissions:

```bash
chmod 644 config.yaml
```

### Port Already in Use

If port 8000 is already in use on your host, you can map a different port:

```bash
docker run -p 8001:8000 -v $(pwd)/config.yaml:/app/config.yaml -e KALTURA_MCP_TRANSPORT=http kaltura-mcp
```

Or update the `docker-compose.yml` file:

```yaml
ports:
  - "8001:8000"
```

### Container Not Starting

If the container fails to start, check the logs:

```bash
docker logs $(docker ps -q -f name=kaltura-mcp)
```

Or with Docker Compose:

```bash
docker-compose logs kaltura-mcp-http
```

### Transport-Specific Issues

#### STDIO Transport

If you're having issues with the STDIO transport:

- Ensure you're running the container with the `-i` flag to enable interactive mode
- Check that your client is correctly connected to the container's stdin/stdout

#### HTTP Transport

If you're having issues with the HTTP transport:

- Ensure the port is correctly mapped (`-p 8000:8000`)
- Check that the host is set to `0.0.0.0` to allow external connections
- Verify that no other service is using the same port

#### SSE Transport

If you're having issues with the SSE transport:

- Ensure the port is correctly mapped (`-p 8000:8000`)
- Check that the host is set to `0.0.0.0` to allow external connections
- Verify that your client supports Server-Sent Events

## Multi-architecture Docker Images

The Kaltura MCP Docker images are built for multiple architectures:

- **linux/amd64**: For Intel/AMD processors (standard x86_64 architecture)
- **linux/arm64**: For ARM-based processors (including Apple Silicon M1/M2/M3)

This means you can run the Docker image on various platforms without compatibility issues. When you pull the image from GitHub Container Registry, Docker automatically selects the appropriate architecture for your system.

### Using a Specific Architecture

If you need to use a specific architecture, you can specify it when pulling the image:

```bash
# For AMD64 (Intel/AMD)
docker pull --platform linux/amd64 ghcr.io/zoharbabin/kaltura-mcp:latest

# For ARM64 (Apple Silicon)
docker pull --platform linux/arm64 ghcr.io/zoharbabin/kaltura-mcp:latest
```

### Image Tags

The Docker images use the following tagging scheme:

- `latest`: The most recent build from the main branch
- `vX.Y.Z`: Specific version releases (e.g., `v1.0.0`)
- `<commit-sha>`: Images tagged with the Git commit SHA for precise version control

## Best Practices

1. **Use the pre-built images**: Use the pre-built multi-architecture images from GitHub Container Registry when possible
2. **Mount configuration files**: Mount configuration files from the host to avoid rebuilding the image
3. **Use environment variables**: Use environment variables for sensitive information
4. **Choose the right transport**: Select the appropriate transport mechanism for your use case
5. **Test the Docker image**: Always test the Docker image before deploying
6. **Keep the Docker image small**: The Dockerfile is optimized to create a small image

## Interacting with the Server

Once the Kaltura MCP server is running in Docker, you can interact with it in several ways:

### Using the MCP CLI

The MCP CLI is a command-line tool for interacting with MCP servers:

```bash
# Install the MCP CLI
pip install mcp-cli

# Connect to the MCP server (HTTP transport)
mcp-cli connect http://localhost:8000

# List available tools
mcp-cli tools list

# Call a tool
mcp-cli tools call media_get --args '{"entry_id": "0_abc123"}'

# Access a resource
mcp-cli resources read media://0_abc123
```

### Using Python Clients

You can use the example Python clients provided in the `examples/` directory:

```bash
# Transport client examples
python examples/transport_client_examples.py http localhost 8000
python examples/transport_client_examples.py sse localhost 8001
```

### Using HTTP Requests

You can interact with the server using HTTP requests (for HTTP and SSE transports):

```bash
# Get server information
curl http://localhost:8000/mcp/info

# List available tools
curl http://localhost:8000/mcp/tools

# Call a tool
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "media_get", "arguments": {"entry_id": "0_abc123"}}'

# Access a resource
curl http://localhost:8000/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "media://0_abc123"}'
```

### Using with Claude

To use the Kaltura MCP server with Claude, see the [Using with Claude](../examples/using_with_claude.md) guide.

## Next Steps

After setting up the Kaltura MCP server with Docker, you can proceed to the [Quick Start](quick-start.md) guide to learn how to use it.