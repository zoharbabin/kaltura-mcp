# Installing Kaltura-MCP Server

This guide provides step-by-step instructions for installing the Kaltura-MCP Server.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- Git
- pip or uv (recommended) package manager
- A Kaltura account with API access

## Using the Setup Script

The easiest way to install and configure the Kaltura-MCP Server is to use the provided setup script:

```bash
# Clone the repository
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp-public

# Run the setup script
python setup_kaltura_mcp.py
```

The setup script will:
1. Check prerequisites
2. Create a virtual environment (optional)
3. Set up configuration files
4. Install dependencies
5. Run verification tests
6. Validate the environment

### Setup Script Options

The setup script supports several command-line options:

```
usage: setup_kaltura_mcp.py [-h] [--interactive] [--non-interactive] [--skip-venv] [--skip-tests] [--skip-validation] [--dev-deps]

Set up the Kaltura MCP environment

options:
  -h, --help         show this help message and exit
  --interactive      Enable interactive configuration
  --non-interactive  Disable interactive prompts (for CI/CD)
  --skip-venv        Skip virtual environment creation
  --skip-tests       Skip running tests
  --skip-validation  Skip environment validation
  --dev-deps         Install development dependencies
```

For example, to set up the environment interactively:

```bash
python setup_kaltura_mcp.py --interactive
```

## Manual Installation Methods

If you prefer to install manually, there are several ways to install the Kaltura-MCP Server:

### Method 1: Install from Source

This is the recommended method for development or if you need the latest features.

```bash
# Clone the repository
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp-public

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

# Using the setup script
python setup_kaltura_mcp.py --dev-deps
```

## Docker Installation

For Docker-based installation, see the [Docker Guide](docker.md).

## Verifying the Installation

To verify that the installation was successful, you can run:

```bash
# Check if the package is installed
pip list | grep kaltura-mcp

# Try importing the package
python -c "import kaltura_mcp; print('Kaltura MCP Server installed successfully')"

# Using the setup script
python setup_kaltura_mcp.py --skip-venv --skip-tests
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

#### System Dependencies

On Linux, you may need to install libmagic:

```bash
# Debian/Ubuntu
sudo apt-get install libmagic1

# CentOS/RHEL
sudo yum install file-devel
```

On macOS, you can use Homebrew:

```bash
brew install libmagic
```

On Windows, you may need to install the python-magic-bin package:

```bash
pip install python-magic-bin
```

## Next Steps

After installing the Kaltura-MCP Server, you need to [configure](configuration.md) it before you can use it.