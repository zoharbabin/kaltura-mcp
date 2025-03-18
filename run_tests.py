#!/usr/bin/env python
"""
Script to run tests and quality checks for the Kaltura MCP project.

This script can run:
- Unit tests and integration tests with pytest
- Linting with ruff (with auto-fix option)
- Type checking with mypy
- Code coverage with pytest-cov
- Code formatting with black
- Import sorting with isort

By default, it runs unit tests and linting. Use flags to run additional checks.
"""
import argparse
import importlib.util
import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_tests")


def check_dependencies():
    """Check if required dependencies are installed."""
    dependencies = {
        "pytest": "pytest",
        "pytest_asyncio": "pytest-asyncio",
        "pytest_cov": "pytest-cov",
        "ruff": "ruff",
        "mypy": "mypy",
        "black": "black",
        "isort": "isort",
    }

    missing = []
    for module, package in dependencies.items():
        if importlib.util.find_spec(module) is None:
            missing.append(package)

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error('Please install development dependencies with: pip install -e ".[dev]"')
        return False

    return True


def run_command(cmd, description):
    """Run a command and log its output."""
    logger.info(f"Running {description}: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        logger.error(f"{description} failed with exit code {result.returncode}")
    return result.returncode


def main():
    # Check if dependencies are installed
    if not check_dependencies():
        return 1

    parser = argparse.ArgumentParser(description="Run tests and quality checks for the Kaltura MCP project")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--full-flow", action="store_true", help="Run full MCP flow tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--log-api-calls", action="store_true", help="Log Kaltura API calls")
    parser.add_argument("--lint", action="store_true", help="Run linting with ruff")
    parser.add_argument("--lint-fix", action="store_true", help="Run linting with auto-fix")
    parser.add_argument("--type-check", action="store_true", help="Run type checking with mypy")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--format", action="store_true", help="Format code with black")
    parser.add_argument("--sort-imports", action="store_true", help="Sort imports with isort")
    parser.add_argument("--fix-all", action="store_true", help="Run all auto-fixes (format, sort imports, lint-fix)")
    parser.add_argument("--ci", action="store_true", help="Run all checks as in CI workflow")
    args = parser.parse_args()

    # If CI flag is set, run all checks
    if args.ci:
        args.lint = True
        args.type_check = True
        args.coverage = True
        args.all = True

    # If fix-all flag is set, run all auto-fixes
    if args.fix_all:
        args.format = True
        args.sort_imports = True
        args.lint_fix = True

    # Set environment variables for logging if requested
    if args.log_api_calls:
        os.environ["KALTURA_MCP_LOG_LEVEL"] = "DEBUG"
        os.environ["KALTURA_MCP_LOG_API_CALLS"] = "1"

    exit_code = 0

    # Format code if requested
    if args.format:
        format_cmd = ["black", "."]
        format_result = run_command(format_cmd, "code formatter")
        exit_code = exit_code or format_result

    # Sort imports if requested
    if args.sort_imports:
        isort_cmd = ["isort", "."]
        isort_result = run_command(isort_cmd, "import sorter")
        exit_code = exit_code or isort_result

    # Run linting if requested
    if args.lint_fix:
        lint_fix_cmd = ["ruff", "check", "--fix", "."]
        lint_fix_result = run_command(lint_fix_cmd, "linter with auto-fix")
        exit_code = exit_code or lint_fix_result
    elif args.lint:
        lint_cmd = ["ruff", "check", "."]
        lint_result = run_command(lint_cmd, "linter")
        exit_code = exit_code or lint_result

    # Run type checking if requested
    if args.type_check:
        mypy_cmd = ["mypy", "kaltura_mcp"]
        mypy_result = run_command(mypy_cmd, "type checker")
        exit_code = exit_code or mypy_result

    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        pytest_cmd.append("-vv")

    if args.coverage:
        pytest_cmd.extend(["--cov=kaltura_mcp"])

    if args.full_flow:
        # Run only the full flow tests
        pytest_cmd.extend(["tests/integration/test_full_mcp_flow.py"])
    elif not args.integration and not args.all:
        # Skip integration tests by default
        pytest_cmd.extend(["--ignore=tests/integration"])

    # Run tests
    test_result = run_command(pytest_cmd, "tests")
    exit_code = exit_code or test_result

    if exit_code == 0:
        logger.info("All checks passed!")
    else:
        logger.error("Some checks failed. Please fix the issues before committing.")
        logger.info("Try running with --fix-all to automatically fix many common issues.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
