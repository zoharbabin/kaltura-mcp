#!/usr/bin/env python
"""
Script to run tests for the Kaltura MCP project.

This script runs all tests except integration tests by default.
To run integration tests, use the --integration flag.
To run full MCP flow tests, use the --full-flow flag.
"""
import argparse
import subprocess
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("run_tests")

def main():
    parser = argparse.ArgumentParser(description="Run tests for the Kaltura MCP project")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--full-flow", action="store_true", help="Run full MCP flow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--log-api-calls", action="store_true", help="Log Kaltura API calls")
    args = parser.parse_args()

    # Set environment variables for logging if requested
    if args.log_api_calls:
        os.environ["KALTURA_MCP_LOG_LEVEL"] = "DEBUG"
        os.environ["KALTURA_MCP_LOG_API_CALLS"] = "1"
    
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-vv")
    
    if args.full_flow:
        # Run only the full flow tests
        cmd.extend(["tests/integration/test_full_mcp_flow.py"])
    elif not args.integration and not args.all:
        # Skip integration tests by default
        cmd.extend(["--ignore=tests/integration"])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())