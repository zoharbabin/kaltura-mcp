# Add Development Tooling - QUICKWIN (30 minutes)

**Complexity**: Low  
**Impact**: High - Ensures code quality and consistency  
**Time Estimate**: 30 minutes  
**Dependencies**: None

## Problem
The project lacks consistent code formatting, linting, and development standards, making it harder to maintain code quality.

## Solution
Add comprehensive development tooling with Black (formatting), Ruff (linting), mypy (type checking), and development configuration.

## Implementation Steps

### 1. Create .editorconfig (3 minutes)
**File: `.editorconfig`**
```ini
# EditorConfig helps developers define and maintain consistent
# coding styles between different editors and IDEs
# editorconfig.org

root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[*.{js,json}]
indent_size = 2

[Makefile]
indent_style = tab

[*.py]
max_line_length = 100
```

### 2. Update pyproject.toml with Tool Configuration (10 minutes)
**Add to `pyproject.toml`:**

```toml
[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "Q",   # flake8-quotes
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
    "UP007", # Use X | Y for type annotations (not supported in 3.9)
]

[tool.ruff.lint.isort]
known-third-party = ["mcp", "fastapi", "pydantic", "KalturaClient", "uvicorn", "authlib"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.lint.flake8-quotes]
inline-quotes = "double"
multiline-quotes = "double"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true
disallow_any_generics = false
disallow_untyped_defs = false
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_unused_ignores = true

# Ignore missing imports for third-party libraries
[[tool.mypy.overrides]]
module = [
    "KalturaClient.*",
    "mcp.*",
    "dotenv.*",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=kaltura_mcp",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

### 3. Update Development Dependencies (5 minutes)
**Update the `[project.optional-dependencies]` section in `pyproject.toml`:**

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.0.0,<8.0.0",
    "pytest-asyncio>=0.21.0,<1.0.0",
    "pytest-cov>=4.0.0,<5.0.0",
    "pytest-mock>=3.11.0,<4.0.0",
    
    # Code quality
    "black>=23.12.0,<24.0.0",
    "ruff>=0.1.0,<1.0.0",
    "mypy>=1.8.0,<2.0.0",
    
    # Type stubs
    "types-requests>=2.31.0",
    "types-python-dateutil>=2.8.0",
    
    # Documentation
    "mkdocs>=1.5.0,<2.0.0",
    "mkdocs-material>=9.4.0,<10.0.0",
]
```

### 4. Create Development Scripts (7 minutes)
**File: `scripts/lint.sh`**
```bash
#!/bin/bash
# Comprehensive linting and formatting script

set -e

echo "🧹 Running code formatting and linting..."

# Format code with Black
echo "📝 Formatting code with Black..."
black src/ tests/ --diff --color

# Lint with Ruff
echo "🔍 Linting with Ruff..."
ruff check src/ tests/ --fix

# Type check with mypy
echo "🔬 Type checking with mypy..."
mypy src/ --pretty

# Check imports
echo "📦 Checking import sorting..."
ruff check src/ tests/ --select I --fix

echo "✅ All checks passed!"
```

**File: `scripts/test.sh`**
```bash
#!/bin/bash
# Test runner script

set -e

echo "🧪 Running tests with coverage..."

# Run tests with coverage
pytest tests/ -v \
    --cov=kaltura_mcp \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=80

echo "📊 Coverage report generated in htmlcov/"
echo "✅ Tests completed!"
```

**File: `scripts/setup-dev.sh`**
```bash
#!/bin/bash
# Development environment setup script

echo "🚀 Setting up Kaltura MCP development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📦 Installing package and dependencies..."
pip install -e ".[dev]"

# Make scripts executable
chmod +x scripts/*.sh

echo "🧪 Running initial checks..."
./scripts/lint.sh

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run tests: ./scripts/test.sh"
echo "  3. Format code: ./scripts/lint.sh"
echo "  4. Start coding! 🚀"
```

### 5. Make Scripts Executable (2 minutes)
```bash
chmod +x scripts/*.sh
```

### 6. Create VSCode Settings (3 minutes)
**File: `.vscode/settings.json`**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.lintOnSave": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.associations": {
        "*.py": "python"
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "[python]": {
        "editor.rulers": [100],
        "editor.tabSize": 4,
        "editor.insertSpaces": true
    },
    "[json]": {
        "editor.tabSize": 2
    },
    "[yaml]": {
        "editor.tabSize": 2
    }
}
```

**File: `.vscode/extensions.json`**
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "editorconfig.editorconfig",
        "ms-vscode.vscode-json"
    ]
}
```

## Testing the Setup

### 1. Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### 2. Run Initial Setup
```bash
./scripts/setup-dev.sh
```

### 3. Test the Tools
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/

# Run all checks
./scripts/lint.sh
```

## IDE Integration

### VSCode
- Install recommended extensions
- Settings will automatically apply
- Formatting on save enabled
- Linting integrated

### PyCharm
- Configure Black as external tool
- Enable Ruff linting plugin
- Configure mypy type checker

## Benefits
- ✅ Consistent code formatting
- ✅ Automated linting and error detection
- ✅ Type checking for better code quality
- ✅ IDE integration for immediate feedback
- ✅ Automated setup for new developers
- ✅ Pre-configured testing environment

## Files Created
- `.editorconfig`
- `scripts/lint.sh`
- `scripts/test.sh`
- `scripts/setup-dev.sh`
- `.vscode/settings.json`
- `.vscode/extensions.json`

## Files Modified
- `pyproject.toml` (added tool configurations)

## Next Steps
After implementing this:
1. Run `./scripts/setup-dev.sh` to set up the environment
2. All developers should use these tools before committing
3. Consider adding pre-commit hooks (separate improvement)
4. Integrate with CI/CD pipeline (separate improvement)