#!/usr/bin/env python
"""
Script to inspect the mcp.client module in detail.
"""
import sys
import importlib
import inspect

def inspect_module(module_name):
    """Inspect a module and print its contents."""
    print(f"Inspecting module: {module_name}")
    try:
        module = importlib.import_module(module_name)
        print(f"Module location: {module.__file__}")
        
        # Print all classes in the module
        print("\nClasses in module:")
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                print(f"- {name}")
                # Print class methods
                print(f"  Methods:")
                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                    if not method_name.startswith('_'):
                        print(f"    - {method_name}")
        
        # Print all functions in the module
        print("\nFunctions in module:")
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module.__name__:
                print(f"- {name}")
        
    except ImportError as e:
        print(f"Error importing module: {e}")

if __name__ == "__main__":
    # Inspect the mcp.client module
    inspect_module("mcp.client")
    
    # Try to import the client directly from mcp
    print("\n" + "="*50 + "\n")
    print("Trying to import client from mcp:")
    try:
        from mcp import client
        print(f"Type of mcp.client: {type(client).__name__}")
        if inspect.isclass(client):
            print("mcp.client is a class")
            print(f"Methods:")
            for method_name, method in inspect.getmembers(client, inspect.isfunction):
                if not method_name.startswith('_'):
                    print(f"  - {method_name}")
        elif inspect.ismodule(client):
            print("mcp.client is a module")
            print(f"Module location: {client.__file__}")
            print(f"Contents:")
            for name, obj in inspect.getmembers(client):
                if not name.startswith('_'):
                    obj_type = type(obj).__name__
                    if inspect.isclass(obj):
                        obj_type = "class"
                    elif inspect.isfunction(obj):
                        obj_type = "function"
                    elif inspect.ismodule(obj):
                        obj_type = "module"
                    print(f"  - {name} ({obj_type})")
    except ImportError as e:
        print(f"Error importing mcp.client: {e}")
    
    # Try to import the Client class from various locations
    print("\n" + "="*50 + "\n")
    print("Trying to find Client class:")
    
    try:
        from mcp.client.session import Client
        print("Found Client in mcp.client.session")
    except ImportError:
        print("Client not found in mcp.client.session")
    
    try:
        from mcp.client.stdio import Client
        print("Found Client in mcp.client.stdio")
    except ImportError:
        print("Client not found in mcp.client.stdio")
    
    try:
        from mcp import Client
        print("Found Client in mcp")
    except ImportError:
        print("Client not found in mcp")