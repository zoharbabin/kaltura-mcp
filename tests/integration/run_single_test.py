#!/usr/bin/env python
"""
Script to run a single integration test with enhanced logging.
"""
import logging
import sys

import pytest

# Configure root logger to show all logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# Make sure our API logger is set to INFO
api_logger = logging.getLogger("kaltura_api_calls")
api_logger.setLevel(logging.INFO)

# Add a console handler to ensure output goes to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
api_logger.addHandler(handler)
api_logger.propagate = True  # Make sure logs propagate to parent loggers

if __name__ == "__main__":
    # Run a single test that makes API calls
    test_path = "tests/integration/test_media_integration.py::TestMediaIntegration::test_media_list_tool"

    print("Running test with enhanced logging:")
    print(f"Test: {test_path}")
    print("-" * 80)

    # Run the test with pytest
    exit_code = pytest.main(["-v", test_path])

    print("-" * 80)
    print(f"Test completed with exit code: {exit_code}")
    sys.exit(exit_code)
