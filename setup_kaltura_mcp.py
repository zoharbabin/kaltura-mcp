#!/usr/bin/env python3
"""
Kaltura MCP Setup Script

This script sets up the Kaltura MCP project by:
1. Checking prerequisites
2. Creating a virtual environment (optional)
3. Setting up configuration files
4. Installing dependencies
5. Running verification tests
6. Validating the environment
"""

import argparse
import importlib.util
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Union, Tuple


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("Error: Python 3.10 or higher is required.")
        sys.exit(1)
    else:
        print(f"Found Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Git
    try:
        git_process = subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, text=True)
        print(f"Found {git_process.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Git is not installed or not in PATH. It's recommended for development.")
    
    # Check pip
    try:
        import pip
        print(f"Found pip version {pip.__version__}")
    except ImportError:
        print("Warning: pip module not found, but continuing anyway.")
    
    # Check system dependencies for python-magic
    if sys.platform == "linux":
        try:
            subprocess.run(["ldconfig", "-p"], check=True, stdout=subprocess.PIPE)
            print("System libraries available.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: Unable to check system libraries. You may need to install libmagic.")
    elif sys.platform == "darwin":
        try:
            subprocess.run(["brew", "--version"], check=True, stdout=subprocess.PIPE)
            print("Homebrew is installed, can be used to install dependencies.")
            print("You may need to run: brew install libmagic")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: Homebrew not found. You may need to install libmagic manually.")
    elif sys.platform == "win32":
        print("On Windows, you may need to install the python-magic-bin package.")
    
    # Check network connectivity to Kaltura API
    try:
        import urllib.request
        import urllib.error
        try:
            with urllib.request.urlopen("https://www.kaltura.com/api_v3/service/system/action/ping", timeout=5) as response:
                if response.status == 200:
                    print("Successfully connected to Kaltura API.")
                else:
                    print(f"Warning: Could not connect to Kaltura API. Status code: {response.status}")
        except urllib.error.URLError as e:
            print(f"Warning: Could not connect to Kaltura API: {e}")
    except ImportError:
        print("Warning: Could not check Kaltura API connectivity due to missing urllib module.")
    
    print("Prerequisites check completed.")


def create_virtual_environment() -> Tuple[Optional[str], Optional[str]]:
    """Create a virtual environment if it doesn't exist."""
    print("Checking for virtual environment...")
    
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("Virtual environment created successfully.")
            
            # Determine the pip path based on platform
            if sys.platform == "win32":
                pip_path = str(venv_dir / "Scripts" / "pip")
                python_path = str(venv_dir / "Scripts" / "python")
            else:
                pip_path = str(venv_dir / "bin" / "pip")
                python_path = str(venv_dir / "bin" / "python")
            
            # Upgrade pip in the virtual environment
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
            print("Pip upgraded in virtual environment.")
            
            return pip_path, python_path
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return None, None
    else:
        print("Virtual environment already exists.")
        # Determine the pip path based on platform
        if sys.platform == "win32":
            pip_path = str(venv_dir / "Scripts" / "pip")
            python_path = str(venv_dir / "Scripts" / "python")
        else:
            pip_path = str(venv_dir / "bin" / "pip")
            python_path = str(venv_dir / "bin" / "python")
        return pip_path, python_path


def setup_config_files(interactive=False):
    """Set up configuration files from examples with optional interactive mode."""
    print("Setting up configuration files...")
    
    # Main config file
    if os.path.exists("config.yaml.example") and not os.path.exists("config.yaml"):
        print("Creating config.yaml from config.yaml.example")
        shutil.copy2("config.yaml.example", "config.yaml")
        
        if interactive:
            try:
                import yaml
                with open("config.yaml", "r") as f:
                    config = yaml.safe_load(f)
                
                print("\nPlease provide your Kaltura API credentials:")
                print("(You can find these in your Kaltura Management Console under Integration Settings)")
                config["kaltura"]["partner_id"] = int(input("Partner ID: "))
                config["kaltura"]["admin_secret"] = input("Admin Secret: ")
                config["kaltura"]["user_id"] = input("User ID [admin]: ") or "admin"
                
                with open("config.yaml", "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
                print("Configuration updated successfully.")
            except Exception as e:
                print(f"Error updating configuration: {e}")
                print("Please edit config.yaml manually with your actual configuration.")
        else:
            print("Please edit config.yaml with your actual configuration.")
    elif os.path.exists("config.yaml"):
        print("config.yaml already exists, skipping creation.")
    else:
        print("Warning: config.yaml.example not found. Cannot create configuration file.")
    
    # Integration test config file
    integration_test_dir = Path("tests/integration")
    if integration_test_dir.exists():
        example_path = integration_test_dir / "config.json.example"
        config_path = integration_test_dir / "config.json"
        
        if example_path.exists() and not config_path.exists():
            print("Creating tests/integration/config.json from config.json.example")
            shutil.copy2(example_path, config_path)
            
            if interactive:
                try:
                    import json
                    with open(config_path, "r") as f:
                        test_config = json.load(f)
                    
                    print("\nUsing the same Kaltura API credentials for integration tests? (y/n)")
                    if input().lower() == "y":
                        try:
                            import yaml
                            with open("config.yaml", "r") as f:
                                main_config = yaml.safe_load(f)
                            test_config["kaltura"]["partner_id"] = main_config["kaltura"]["partner_id"]
                            test_config["kaltura"]["admin_secret"] = main_config["kaltura"]["admin_secret"]
                            test_config["kaltura"]["user_id"] = main_config["kaltura"]["user_id"]
                        except Exception as e:
                            print(f"Error reading main config: {e}")
                            print("Please enter integration test credentials manually:")
                            test_config["kaltura"]["partner_id"] = int(input("Partner ID: "))
                            test_config["kaltura"]["admin_secret"] = input("Admin Secret: ")
                            test_config["kaltura"]["user_id"] = input("User ID [admin]: ") or "admin"
                    else:
                        print("Please enter integration test credentials:")
                        test_config["kaltura"]["partner_id"] = int(input("Partner ID: "))
                        test_config["kaltura"]["admin_secret"] = input("Admin Secret: ")
                        test_config["kaltura"]["user_id"] = input("User ID [admin]: ") or "admin"
                    
                    with open(config_path, "w") as f:
                        json.dump(test_config, f, indent=2)
                    print("Integration test configuration updated successfully.")
                except Exception as e:
                    print(f"Error updating integration test configuration: {e}")
                    print("Please edit tests/integration/config.json manually.")
            else:
                print("Please edit tests/integration/config.json with your test configuration.")
        elif config_path.exists():
            print("tests/integration/config.json already exists, skipping creation.")
        else:
            print("Warning: tests/integration/config.json.example not found. Cannot create test configuration file.")


def install_dependencies(pip_path=None, python_path=None, dev_dependencies=True):
    """Install dependencies."""
    print("Installing dependencies...")
    
    pip_cmd = pip_path if pip_path else f"{sys.executable} -m pip"
    
    try:
        # Install the package in development mode
        if pip_path:
            subprocess.run([pip_path, "install", "-e", "."], check=True)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print("Successfully installed package dependencies")
        
        # Install development dependencies
        if dev_dependencies:
            if pip_path:
                subprocess.run([pip_path, "install", "-e", ".[dev]"], check=True)
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], check=True)
            print("Successfully installed development dependencies")
        
        # Verify installation
        try:
            python_cmd = python_path if python_path else sys.executable
            subprocess.run([python_cmd, "-c", "import kaltura_mcp; print(f'Successfully imported kaltura_mcp')"], check=True)
            print("Installation verified successfully.")
        except subprocess.CalledProcessError:
            print("Warning: Could not verify installation.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    
    return True


def run_verification_tests(python_path=None, interactive=True):
    """Run verification tests."""
    print("Running verification tests...")
    
    python_cmd = python_path if python_path else sys.executable
    
    if os.path.exists("run_tests.py"):
        # Run unit tests and code quality checks
        print("Running unit tests and code quality checks...")
        try:
            subprocess.run([python_cmd, "run_tests.py", "--lint", "--type-check"], check=True)
            print("Unit tests and code quality checks passed.")
        except subprocess.CalledProcessError:
            print("Warning: Unit tests or code quality checks failed. Please check the output.")
        
        # Ask about running integration tests if in interactive mode
        if interactive:
            print("\nWould you like to run integration tests? (y/n)")
            print("Note: This requires valid Kaltura API credentials in tests/integration/config.json")
            if input().lower() == "y":
                try:
                    subprocess.run([python_cmd, "run_tests.py", "--integration"], check=True)
                    print("Integration tests passed.")
                except subprocess.CalledProcessError:
                    print("Warning: Integration tests failed. Please check the output.")
        else:
            print("Skipping integration tests in non-interactive mode.")
    else:
        print("Warning: run_tests.py not found. Cannot run verification tests.")


def validate_environment(python_path=None):
    """Validate that the environment is properly set up."""
    print("Validating environment...")
    
    # Check if config.yaml exists and has required fields
    try:
        import yaml
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            # Check for required configuration
            if not config.get("kaltura", {}).get("partner_id"):
                print("Warning: Kaltura partner_id not configured in config.yaml")
            if not config.get("kaltura", {}).get("admin_secret"):
                print("Warning: Kaltura admin_secret not configured in config.yaml")
            
            # Check server port availability
            port = config.get("server", {}).get("port", 8000)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("127.0.0.1", port))
                print(f"Port {port} is available for the server.")
            except socket.error:
                print(f"Warning: Port {port} is already in use. The server may not start properly.")
            finally:
                s.close()
        else:
            print("Warning: config.yaml not found. The server will not be able to start.")
            return False
        
        # Try to import the server module to validate installation
        python_cmd = python_path if python_path else sys.executable
        try:
            result = subprocess.run(
                [python_cmd, "-c", "import kaltura_mcp.server; print('Server module imported successfully')"],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not import server module: {e}")
            if e.stderr:
                print(e.stderr)
            return False
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        return False
    except Exception as e:
        print(f"Error validating environment: {e}")
        return False
    
    return True


def main():
    """Main function."""
    print("=== Kaltura MCP Setup ===")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Set up the Kaltura MCP environment")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive configuration")
    parser.add_argument("--non-interactive", action="store_true", help="Disable interactive prompts (for CI/CD)")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-validation", action="store_true", help="Skip environment validation")
    parser.add_argument("--dev-deps", action="store_true", help="Install development dependencies")
    args = parser.parse_args()
    
    # Determine interactive mode
    interactive = args.interactive and not args.non_interactive
    
    # Check prerequisites
    check_prerequisites()
    
    # Create virtual environment if not skipped
    pip_path, python_path = None, None
    if not args.skip_venv:
        pip_path, python_path = create_virtual_environment()
    
    # Set up configuration files
    setup_config_files(interactive=interactive)
    
    # Install dependencies
    install_success = install_dependencies(
        pip_path=pip_path, 
        python_path=python_path,
        dev_dependencies=args.dev_deps
    )
    
    if not install_success:
        print("Warning: Dependency installation had issues. Continuing with setup...")
    
    # Run verification tests if not skipped
    if not args.skip_tests:
        run_verification_tests(python_path=python_path, interactive=interactive)
    
    # Validate environment if not skipped
    if not args.skip_validation:
        validate_environment(python_path=python_path)
    
    print("\n=== Setup Complete ===")
    print("Please review any warnings or errors above.")
    print("For more information, see the documentation in the docs directory.")
    
    # Provide next steps
    print("\nNext Steps:")
    print("1. Ensure your Kaltura API credentials are configured in config.yaml")
    print("2. Start the server with: python -m kaltura_mcp.server")
    print("3. Try the examples in the examples directory")


if __name__ == "__main__":
    main()
