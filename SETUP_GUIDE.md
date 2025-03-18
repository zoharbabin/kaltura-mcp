# Kaltura MCP Server Setup Guide

This guide provides comprehensive instructions for setting up the Kaltura MCP server from a clean start, including which folders to keep, which to delete, and how to configure and run the server.

## Repository Cleanup

### Folders to Keep

Keep only the `kaltura-mcp-public` folder, which contains the complete, self-contained Kaltura MCP server implementation. This folder includes:

- All necessary code
- Comprehensive documentation
- Docker support
- Setup script
- Example clients
- Test scripts

### Folders to Delete

You can safely delete the following folders as they are no longer needed:

- `fast-mcp/` - This is specified as a dependency in pyproject.toml and will be installed via pip
- `kaltura-client-py/` - This is also specified as a dependency and will be installed via pip
- `kaltura-mcp/` - This was the original implementation that has been cleaned up and moved to kaltura-mcp-public
- `kaltura_uploader/` - Any necessary functionality has been incorporated or specified as a dependency
- `memory-bank/` - This was just for development process, not needed for the public release
- `tools/` - These are development tools, not needed for the public release

## Setting Up a Working Environment

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)
- Docker (optional, for containerized deployment)

### Step 1: Create a New Repository

```bash
# Create a new directory for the project
mkdir kaltura-mcp
cd kaltura-mcp

# Initialize a new Git repository
git init

# Copy the contents of kaltura-mcp-public into the new repository
cp -r /path/to/kaltura-mcp-public/* .

# Commit the initial files
git add .
git commit -m "Initial commit"
```

### Step 2: Create and Activate a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Upgrade pip and Install Requirements

```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install the package in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# If you encounter issues with trio tests, install trio explicitly
pip install "anyio[trio]"
```

### Step 4: Configure Kaltura Account Details

```bash
# Create a configuration file from the example
cp config.yaml.example config.yaml

# Edit the configuration file with your Kaltura account details
# Replace the placeholders with your actual values
nano config.yaml
```

Your `config.yaml` file should look like this:

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

### Step 5: Configure Integration Tests (Optional)

If you want to run integration tests, you need to create a configuration file for them:

```bash
# Create the integration tests directory if it doesn't exist
mkdir -p tests/integration

# Create a configuration file for integration tests
cat > tests/integration/config.json << EOL
{
  "partner_id": 123456,
  "admin_secret": "your-admin-secret",
  "user_id": "your-user-id",
  "service_url": "https://www.kaltura.com/api_v3"
}
EOL
```

### Step 6: Run the MCP Server

#### Option 1: Using the kaltura-mcp Command

```bash
# Run the server
kaltura-mcp
```

#### Option 2: Using the MCP CLI

```bash
# Start the server with the MCP Inspector
mcp dev kaltura_mcp/server.py:main

# Or run the server directly
mcp run kaltura_mcp/server.py:main
```

#### Option 3: Using Docker

```bash
# Build and run with Docker Compose
docker-compose up
```

### Step 7: Run Tests

#### Running Basic Tests

```bash
# Run all tests except integration tests
./run_tests.py

# Run tests with verbose output
./run_tests.py --verbose
```

#### Running Integration Tests

```bash
# Run all tests including integration tests
./run_tests.py --all

# Run only integration tests
./run_tests.py --integration
```

#### Running End-to-End Tests

```bash
# Run the basic test script
python examples/basic_test.py

# Run the complete test script
python examples/complete_test.py
```

### Step 8: Verify the Installation

#### Using the MCP Inspector

1. Start the server with the MCP Inspector:
   ```bash
   mcp dev kaltura_mcp/server.py:main
   ```

2. Open http://localhost:5173 in your web browser.

3. Connect to the server using the "Connect" button.

4. Explore the available tools and resources.

#### Using the MCP CLI

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

#### Using a Python Client

```bash
# Run the simple demo client
python examples/simple_demo_client.py
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Error: `ModuleNotFoundError: No module named 'xxx'`
   - Solution: Install the missing dependency with `pip install xxx`

2. **Configuration Issues**
   - Error: `Failed to connect to Kaltura API`
   - Solution: Check your Kaltura API credentials in `config.yaml`

3. **Port Already in Use**
   - Error: `Address already in use`
   - Solution: Change the port in `config.yaml` or stop the process using the port

4. **Permission Issues**
   - Error: `Permission denied`
   - Solution: Make sure you have the necessary permissions to run the server

### Getting Help

If you encounter any issues that are not covered in this guide, please:

1. Check the [documentation](docs/index.md) for more information
2. Look for similar issues in the [GitHub repository](https://github.com/kaltura/kaltura-mcp-public/issues)
3. Open a new issue if you can't find a solution

## Next Steps

Now that you have a working environment, you can:

1. **Explore the available tools and resources** using the MCP Inspector or MCP CLI
2. **Integrate with Claude or other LLMs** that support the MCP protocol
3. **Develop custom clients** using the MCP client library
4. **Extend the server** with additional tools and resources

For more information, see the [documentation](docs/index.md).