#!/usr/bin/env python3
"""
Kaltura MCP Setup Script

This script sets up the Kaltura MCP project by:
1. Checking prerequisites
2. Setting up configuration files
3. Installing dependencies
4. Running verification tests
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("Checking prerequisites...")
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("Error: Python 3.10 or higher is required.")
        sys.exit(1)

    # Check pip - use a different approach that doesn't fail during package installation
    try:
        import pip

        print(f"Found pip version {pip.__version__}")
    except ImportError:
        print("Warning: pip module not found, but continuing anyway.")

    print("All prerequisites are installed.")


def setup_config_files():
    """Set up configuration files from examples."""
    print("Setting up configuration files...")

    # Main config file
    if os.path.exists("config.yaml.example") and not os.path.exists("config.yaml"):
        print("Creating config.yaml from config.yaml.example")
        shutil.copy2("config.yaml.example", "config.yaml")
        print("Please edit config.yaml with your actual configuration.")

    # Integration test config file
    integration_test_dir = Path("tests/integration")
    if integration_test_dir.exists():
        example_path = integration_test_dir / "config.json.example"
        config_path = integration_test_dir / "config.json"

        if example_path.exists() and not config_path.exists():
            print("Creating tests/integration/config.json from config.json.example")
            shutil.copy2(example_path, config_path)
            print("Please edit tests/integration/config.json with your test configuration.")


def install_dependencies():
    """Install dependencies."""
    print("Installing dependencies...")

    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print("Successfully installed dependencies")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")


def run_verification_tests():
    """Run verification tests."""
    print("Running verification tests...")

    if os.path.exists("run_tests.py"):
        print("Running tests...")
        try:
            subprocess.run([sys.executable, "run_tests.py"], check=True)
            print("Tests passed.")
        except subprocess.CalledProcessError:
            print("Warning: tests failed. Please check the output.")


def main():
    """Main function."""
    print("=== Kaltura MCP Setup ===")

    check_prerequisites()
    setup_config_files()
    install_dependencies()
    run_verification_tests()

    print("\n=== Setup Complete ===")
    print("Please review any warnings or errors above.")
    print("For more information, see the documentation in the docs directory.")


if __name__ == "__main__":
    main()
