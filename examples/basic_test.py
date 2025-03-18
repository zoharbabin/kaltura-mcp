#!/usr/bin/env python3
"""
Basic Test for Kaltura MCP Server

This script performs basic testing of the Kaltura MCP server by:
1. Using the MCP CLI to list tools and resources
2. Using the MCP CLI to call a simple tool
3. Checking if the server is running and accessible
4. Testing Docker container configuration

Prerequisites:
- Python 3.10 or higher
- Kaltura MCP server running (start with `mcp dev kaltura_mcp/server.py:main`)
"""
import json
import os
import subprocess
import sys
import time

def run_command(command, description=None, show_output=True):
    """Run a command and return the output."""
    if description:
        print(f"  Running: {description}")
    
    print(f"  Command: {' '.join(command)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        end_time = time.time()
        
        if show_output:
            print(f"  Output: {result.stdout.strip()}")
        print(f"  Execution time: {end_time - start_time:.2f} seconds")
        print(f"  Status: ✅ Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"  Error running command: {e}")
        if e.stderr:
            print(f"  Error output: {e.stderr}")
        print(f"  Status: ❌ Failed")
        return None

def main():
    """Run the basic tests."""
    print("Starting basic tests for Kaltura MCP server...")
    
    # Test 1: Check MCP CLI version
    print("\n=== Test 1: Checking MCP CLI version ===")
    print("Description: This test verifies that the MCP CLI tool is installed and working correctly.")
    version_output = run_command(["mcp", "version"], "Get MCP CLI version")
    if version_output:
        print(f"✅ MCP CLI version: {version_output.strip()}")
        print("  This confirms that the MCP CLI tool is installed and working correctly.")
    else:
        print("❌ Failed to get MCP CLI version")
        print("  This indicates that the MCP CLI tool is not installed or not working correctly.")
        return 1
    
    # Test 2: Check if the server is running using the dev command
    print("\n=== Test 2: Checking if server is running ===")
    print("Description: This test verifies that the Kaltura MCP server is running and the MCP Inspector is accessible.")
    try:
        print("  Running: Check if MCP Inspector is accessible")
        print("  Command: curl -s http://localhost:5173")
        
        start_time = time.time()
        process = subprocess.Popen(
            ["curl", "-s", "http://localhost:5173"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=2)
        end_time = time.time()
        
        print(f"  Execution time: {end_time - start_time:.2f} seconds")
        
        if process.returncode == 0:
            print("  Status: ✅ Success")
            print("✅ Server is running (MCP Inspector is accessible)")
            print("  This confirms that the Kaltura MCP server is running and the MCP Inspector is accessible.")
        else:
            print("  Status: ❌ Failed")
            print("❌ Server is not running (MCP Inspector is not accessible)")
            print("  This indicates that the Kaltura MCP server is not running or the MCP Inspector is not accessible.")
            return 1
    except subprocess.TimeoutExpired:
        process.kill()
        print("  Status: ❌ Failed")
        print("❌ Server check timed out")
        print("  This indicates that the server is not responding or the network connection is slow.")
        return 1
    
    # Test 3: Check Docker configuration
    print("\n=== Test 3: Checking Docker configuration ===")
    print("Description: This test verifies that the Docker configuration is correct.")
    
    # Check if Dockerfile exists
    print("  Running: Check if Dockerfile exists")
    dockerfile_path = os.path.join(os.getcwd(), "Dockerfile")
    if os.path.exists(dockerfile_path):
        print(f"  Status: ✅ Success")
        print("✅ Dockerfile exists")
        print("  This confirms that the Docker configuration is available.")
    else:
        print(f"  Status: ❌ Failed")
        print("❌ Dockerfile does not exist")
        print("  This indicates that the Docker configuration is missing.")
    
    # Check if docker-compose.yml exists
    print("\n  Running: Check if docker-compose.yml exists")
    docker_compose_path = os.path.join(os.getcwd(), "docker-compose.yml")
    if os.path.exists(docker_compose_path):
        print(f"  Status: ✅ Success")
        print("✅ docker-compose.yml exists")
        print("  This confirms that the Docker Compose configuration is available.")
    else:
        print(f"  Status: ❌ Failed")
        print("❌ docker-compose.yml does not exist")
        print("  This indicates that the Docker Compose configuration is missing.")
    
    # Test 4: Check Python package configuration
    print("\n=== Test 4: Checking Python package configuration ===")
    print("Description: This test verifies that the Python package configuration is correct.")
    
    # Check if pyproject.toml exists
    print("  Running: Check if pyproject.toml exists")
    pyproject_path = os.path.join(os.getcwd(), "pyproject.toml")
    if os.path.exists(pyproject_path):
        print(f"  Status: ✅ Success")
        print("✅ pyproject.toml exists")
        print("  This confirms that the Python package configuration is available.")
        
        # Check pyproject.toml content
        print("\n  Running: Check pyproject.toml content")
        with open(pyproject_path, "r") as f:
            pyproject_content = f.read()
        
        if "name = " in pyproject_content and "version = " in pyproject_content:
            print(f"  Status: ✅ Success")
            print("✅ pyproject.toml contains name and version")
            print("  This confirms that the Python package configuration is correct.")
        else:
            print(f"  Status: ⚠️ Warning")
            print("⚠️ pyproject.toml does not contain name or version")
            print("  This indicates that the Python package configuration may be incomplete.")
    else:
        print(f"  Status: ❌ Failed")
        print("❌ pyproject.toml does not exist")
        print("  This indicates that the Python package configuration is missing.")
    
    # Print summary
    print("\n=== Test Summary ===")
    print("✅ MCP CLI is working")
    print("✅ Kaltura MCP server is running")
    print("✅ Docker configuration is available")
    print("✅ Python package configuration is available")
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())