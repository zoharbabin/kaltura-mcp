# Contributing to Kaltura MCP

Thank you for your interest in contributing to Kaltura MCP! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

1. **Fork the repository**
2. **Create a branch**:
   ```
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Install development dependencies**:
   ```
   pip install -e ".[dev]"
   ```
5. **Auto-fix common issues**:
   ```
   # Fix formatting, sort imports, and fix linting issues automatically
   python run_tests.py --fix-all
   ```
6. **Run tests and quality checks**:
   ```
   # Run all CI checks (tests, linting, type checking, coverage)
   python run_tests.py --ci
   ```
7. **Fix remaining issues manually**:
   If there are still issues after running the auto-fixes, you'll need to address them manually:
   
   - **Type checking errors**:
     - Add missing type annotations to functions and variables
     - Install missing type stubs (e.g., `pip install types-PyYAML`)
   
   - **Linting errors**:
     - F541: Remove unnecessary f-prefix from strings without placeholders
     - E501: Break long lines into shorter ones
     - B011: Replace `assert False, "message"` with `raise AssertionError("message")`
     - F841: Remove unused local variables
   
   - **Test configuration issues**:
     - Ensure pytest-cov is installed for coverage reporting
     - Check for proper test configuration in pytest.ini

8. **Commit your changes**:
   ```
   git commit -m "Add feature: your feature description"
   ```
9. **Push to your fork**:
   ```
   git push origin feature/your-feature-name
   ```
10. **Create a Pull Request**

## Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatter that enforces a consistent style
- **isort**: Sorts imports alphabetically and automatically separates them into sections
- **Ruff**: Fast Python linter that checks for errors and enforces style
- **mypy**: Static type checker that helps catch type-related errors
- **pytest**: Testing framework for running unit and integration tests
- **pytest-cov**: Plugin for pytest that measures code coverage

You can run these tools individually:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code with auto-fix
ruff check --fix .

# Type check
mypy kaltura_mcp

# Run tests with coverage
pytest --cov=kaltura_mcp
```

Or use the run_tests.py script with appropriate flags:

```bash
# Format code
python run_tests.py --format

# Sort imports
python run_tests.py --sort-imports

# Lint code with auto-fix
python run_tests.py --lint-fix

# Run all auto-fixes
python run_tests.py --fix-all

# Run all CI checks
python run_tests.py --ci
```

## Common Issues and Manual Fixes

While many issues can be fixed automatically with the tools above, some require manual intervention. **These manual fixes are critical for passing CI checks.**

### 1. Line Length Issues (E501)

If you encounter line length issues that aren't fixed automatically:

- Break long strings into multiple lines using string concatenation:
  ```python
  # Before
  long_string = "This is a very long string that exceeds the line length limit of 130 characters and needs to be broken up."
  
  # After
  long_string = (
      "This is a very long string that exceeds the line length limit "
      "of 130 characters and needs to be broken up."
  )
  ```

- For long function calls, break parameters onto separate lines:
  ```python
  # Before
  result = some_function(param1, param2, param3, param4, param5, param6, param7, param8, param9, param10)
  
  # After
  result = some_function(
      param1,
      param2,
      param3,
      param4,
      param5,
      param6,
      param7,
      param8,
      param9,
      param10
  )
  ```

### 2. Assertion Issues (B011) - CRITICAL

Replace `assert False` statements with proper exceptions. This is critical because assertions can be disabled with Python's -O flag:

```python
# Before
assert False, "This operation is not supported"

# After
raise AssertionError("This operation is not supported")
```

This change ensures that the error will always be raised, even when Python is run with optimizations.

### 3. Exception Chaining (B904) - CRITICAL

Properly chain exceptions when re-raising. This is critical for maintaining the exception context:

```python
# Before
try:
    some_operation()
except Exception as e:
    raise ValueError(f"Operation failed: {e}")

# After
try:
    some_operation()
except Exception as e:
    raise ValueError(f"Operation failed: {e}") from e
```

This change preserves the original exception context, making debugging much easier by showing the complete exception chain.

### 4. Unused Variables (F841)

Remove unused variable assignments:

```python
# Before
try:
    result = some_operation()
except Exception as e:
    # result is never used
    pass

# After
try:
    some_operation()  # No assignment if not needed
except Exception:  # No 'as e' if e is not used
    pass
```

### 5. Import Ordering (E402)

Move all imports to the top of the file:

```python
# Before
import sys

def some_function():
    pass

import os  # This should be at the top

# After
import os
import sys

def some_function():
    pass
```

## Importance of Running CI Checks Locally

Before submitting a pull request, it's crucial to run the same checks that will be run in the CI pipeline. This helps catch issues early and ensures your contribution will pass the CI checks.

The workflow for fixing code quality issues should be:

1. **Run auto-fixes first**:
   ```bash
   python run_tests.py --fix-all
   ```

2. **Run CI checks to identify remaining issues**:
   ```bash
   python run_tests.py --ci
   ```

3. **Fix remaining issues manually** using the guidance in the "Common Issues and Manual Fixes" section above.

4. **Run CI checks again** to verify all issues are fixed:
   ```bash
   python run_tests.py --ci
   ```

5. **Commit only when all checks pass** to ensure your PR will be accepted.

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update documentation as needed
3. Include tests for new features
4. Ensure all tests pass
5. Your PR will be reviewed by maintainers

## Coding Standards

- Follow PEP 8 style guide for Python code
- Write clear, descriptive commit messages
- Include docstrings for all functions, classes, and modules
- Write tests for new features

## Reporting Bugs

Please report bugs by opening an issue in the GitHub repository. Include:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, etc.)

## Feature Requests

Feature requests are welcome! Please open an issue and:

- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this feature would be useful

## Questions?

If you have any questions, feel free to open an issue or contact the maintainers.

Thank you for contributing to Kaltura MCP!
