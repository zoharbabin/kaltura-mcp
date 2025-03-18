#!/usr/bin/env python3
"""
MCP CLI Wrapper for Kaltura MCP Server

This script demonstrates how to use the MCP CLI tool to interact with the Kaltura MCP server.
It wraps the mcp CLI commands in a Python script for easier use.

Prerequisites:
- Python 3.10 or higher
- MCP CLI tool installed (`pip install mcp[cli]`)
- Kaltura MCP server installed
"""
import json
import subprocess
import time


def run_command(command, capture_output=True):
    """Run a command and return the output."""
    try:
        result = subprocess.run(command, capture_output=capture_output, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None


def main():
    """Run the MCP CLI wrapper."""
    print("Starting Kaltura MCP Server...")

    # Start the Kaltura MCP server in the background
    server_process = subprocess.Popen(["kaltura-mcp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for the server to start
    time.sleep(2)

    try:
        # Check if the MCP CLI tool is installed
        print("Checking for MCP CLI tool...")
        mcp_help = run_command(["mcp", "--help"])
        if mcp_help:
            print("MCP CLI tool found")
        else:
            print("MCP CLI tool not found. Please install it with 'pip install mcp[cli]'")
            return

        # List tools
        print("\nListing tools...")
        tools_output = run_command(["mcp", "tools", "list"])
        if tools_output:
            print("\n=== Available Tools ===")
            print(tools_output)

        # List resources
        print("\nListing resources...")
        resources_output = run_command(["mcp", "resources", "list"])
        if resources_output:
            print("\n=== Available Resources ===")
            print(resources_output)

        # Call the media.list tool
        print("\nCalling kaltura.media.list tool...")
        media_list_args = json.dumps({"page_size": 5, "filter": {}})
        media_list_output = run_command(["mcp", "tools", "call", "kaltura.media.list", media_list_args])
        if media_list_output:
            print("\n=== Media List Result ===")
            print(media_list_output)

        # Read the media list resource
        print("\nReading kaltura://media/list resource...")
        media_resource_output = run_command(["mcp", "resources", "read", "kaltura://media/list?page_size=5"])
        if media_resource_output:
            print("\n=== Media List Resource ===")
            print(media_resource_output)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Terminate the server process
        print("\nTerminating Kaltura MCP Server...")
        server_process.terminate()
        server_process.wait(timeout=5)


if __name__ == "__main__":
    main()
