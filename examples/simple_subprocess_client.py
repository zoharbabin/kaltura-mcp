#!/usr/bin/env python3
"""
Simple Kaltura MCP Client using subprocess

This script demonstrates how to interact with the Kaltura MCP server using subprocess.
It starts the server as a subprocess and communicates with it using stdin/stdout.

Prerequisites:
- Python 3.10 or higher
- Kaltura MCP server installed
"""
import json
import subprocess
import time


def main():
    """Run the simple subprocess client."""
    print("Starting Kaltura MCP Server...")

    # Start the Kaltura MCP server as a subprocess
    try:
        process = subprocess.Popen(
            ["kaltura-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )

        # Wait for the server to start
        time.sleep(2)

        # Check if the process is still running
        if process.poll() is not None:
            print("Error: Kaltura MCP Server failed to start")
            stderr_output = process.stderr.read()
            print(f"Error output: {stderr_output}")
            return

        print("Kaltura MCP Server started")

        # Send a request to list tools
        request = {"jsonrpc": "2.0", "id": 1, "method": "listTools", "params": {}}

        print("\nSending request to list tools...")
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        # Read the response
        response = process.stdout.readline()
        tools_response = json.loads(response)

        if "result" in tools_response:
            print("\n=== Available Tools ===")
            for tool in tools_response["result"]["tools"]:
                print(f"- {tool['name']}: {tool['description']}")
        else:
            print(f"Error: {tools_response.get('error', 'Unknown error')}")

        # Send a request to list resources
        request = {"jsonrpc": "2.0", "id": 2, "method": "listResources", "params": {}}

        print("\nSending request to list resources...")
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        # Read the response
        response = process.stdout.readline()
        resources_response = json.loads(response)

        if "result" in resources_response:
            print("\n=== Available Resources ===")
            for resource in resources_response["result"]["resources"]:
                print(f"- {resource['uri']}: {resource.get('description', 'No description')}")
        else:
            print(f"Error: {resources_response.get('error', 'Unknown error')}")

    except FileNotFoundError:
        print("Error: Kaltura MCP Server executable not found")
        print("Make sure the server is installed and in your PATH")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Terminate the process
        if "process" in locals() and process.poll() is None:
            print("\nTerminating Kaltura MCP Server...")
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
