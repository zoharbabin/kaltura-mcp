#!/usr/bin/env python3
"""
Simple HTTP Client for Kaltura MCP Server

This script demonstrates how to connect to the Kaltura MCP server running in Docker
using simple HTTP requests.

Prerequisites:
- Python 3.10 or higher
- requests library installed
- Kaltura MCP server running in Docker on port 8000
"""
import json
import requests
import sys

def main():
    """Run the HTTP client."""
    print("Connecting to Kaltura MCP Server running in Docker...")
    
    # Base URL for the server running in Docker
    base_url = "http://localhost:8000"
    
    try:
        # Test connection to the server
        response = requests.get(base_url)
        if response.status_code == 200:
            print("Successfully connected to the server")
            print(f"Server response: {response.text}")
        else:
            print(f"Failed to connect to server: {response.status_code}")
            return
        
        # Try to access the MCP API endpoints
        print("\n=== Testing MCP API Endpoints ===")
        
        # Try to list tools
        print("\nTesting /tools endpoint...")
        try:
            response = requests.get(f"{base_url}/tools")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to list resources
        print("\nTesting /resources endpoint...")
        try:
            response = requests.get(f"{base_url}/resources")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to access media entries
        print("\nTesting /media endpoint...")
        try:
            response = requests.get(f"{base_url}/media")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to access categories
        print("\nTesting /categories endpoint...")
        try:
            response = requests.get(f"{base_url}/categories")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
        # Try to access users
        print("\nTesting /users endpoint...")
        try:
            response = requests.get(f"{base_url}/users")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
        
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server. Make sure the Docker container is running.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()