# Installing Kaltura-MCP Server

This guide provides step-by-step instructions for installing the Kaltura-MCP Server.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- Git
- pip or uv (recommended) package manager
- A Kaltura account with API access

## Installation Methods

There are several ways to install the Kaltura-MCP Server:

### Method 1: Install from Source

This is the recommended method for development or if you need the latest features.

```bash
# Clone the repository
git clone https://github.com/your-organization/kaltura-mcp.git
cd kaltura-mcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

### Method 2: Install from PyPI (Coming Soon)

For production use, you can install the package from PyPI:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install kaltura-mcp
```

### Method 3: Using uv (Recommended)

uv is a faster, more secure alternative to pip. To install with uv:

```bash
# Install uv if you don't have it
pip install uv

# Create a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
uv pip install -e .
```

## Installing Development Dependencies

If you plan to contribute to the project or run tests, you should install the development dependencies:

```bash
# Using pip
pip install -e ".[dev]"

# Using uv
uv pip install -e ".[dev]"
```

## Verifying the Installation

To verify that the installation was successful, you can run:

```bash
# Check if the package is installed
pip list | grep kaltura-mcp

# Try importing the package
python -c "import kaltura_mcp; print(kaltura_mcp.__version__)"
```

## Troubleshooting

### Common Issues

#### Missing Dependencies

If you encounter errors about missing dependencies, try installing them manually:

```bash
pip install anyio mcp kaltura-client-py
```

#### Trio Backend Issues

If you encounter issues with the anyio trio backend, install trio explicitly:

```bash
pip install "anyio[trio]"
```

#### Permission Issues

If you encounter permission issues during installation, try using the `--user` flag with pip:

```bash
pip install --user -e .
```

Or run the installation with elevated privileges (not recommended):

```bash
# On Linux/macOS
sudo pip install -e .

# On Windows (run Command Prompt as Administrator)
pip install -e .
```

## Next Steps

After installing the Kaltura-MCP Server, you need to [configure](configuration.md) it before you can use it.