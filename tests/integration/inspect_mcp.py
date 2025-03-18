#!/usr/bin/env python
"""
Script to inspect the MCP package structure.
"""
import sys
import importlib
import pkgutil
import inspect

def inspect_package(package_name):
    """Inspect a package and print its structure."""
    print(f"Inspecting package: {package_name}")
    try:
        package = importlib.import_module(package_name)
        print(f"Package location: {package.__file__}")
        
        # Print all modules in the package
        print("\nModules in package:")
        for _, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
            print(f"- {name} ({'package' if ispkg else 'module'})")
        
        # Print all attributes in the package
        print("\nAttributes in package:")
        for name in dir(package):
            if not name.startswith('_'):  # Skip private attributes
                attr = getattr(package, name)
                attr_type = type(attr).__name__
                if inspect.ismodule(attr):
                    attr_type = "module"
                elif inspect.isclass(attr):
                    attr_type = "class"
                elif inspect.isfunction(attr):
                    attr_type = "function"
                print(f"- {name} ({attr_type})")
        
    except ImportError as e:
        print(f"Error importing package: {e}")

if __name__ == "__main__":
    # Inspect the mcp package
    inspect_package("mcp")
    
    # Inspect the mcp.client package
    print("\n" + "="*50 + "\n")
    inspect_package("mcp.client")