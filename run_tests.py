#!/usr/bin/env python
"""
Script to run tests for the Kaltura MCP project.

This script runs all tests except integration tests by default.
To run integration tests, use the --integration flag.
"""
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Run tests for the Kaltura MCP project")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-vv")
    
    if not args.integration and not args.all:
        # Skip integration tests by default
        cmd.extend(["--ignore=tests/integration"])
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())