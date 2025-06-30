# Add Development Tooling - QUICKWIN (15 minutes)

**Complexity**: Low  
**Impact**: High - Ensures code quality and consistency  
**Time Estimate**: 15 minutes  
**Dependencies**: None

## Problem
The project lacks consistent code formatting, linting, and development standards, making it harder to maintain code quality.

## Solution
Add essential development tooling with Black (formatting) and Ruff (linting) - keeping it simple and effective.

## Implementation Steps

### 1. Create Simple .editorconfig (2 minutes)
**File: `.editorconfig`**
```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.py]
max_line_length = 100
```

### 2. Update pyproject.toml with Tool Configuration (5 minutes)
**Add to existing `pyproject.toml`:**

```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "W", "F", "I"]  # pycodestyle + pyflakes + isort
ignore = ["E501"]  # line too long (handled by black)

# Update existing dev dependencies (keep existing, add if missing):
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0,<8.0.0",
    "pytest-asyncio>=0.21.0,<1.0.0", 
    "black>=23.0.0,<24.0.0",
    "ruff>=0.1.0,<1.0.0",
]
```

### 3. Create Single Check Script (8 minutes)
**File: `scripts/check.sh`**
```bash
#!/bin/bash
# Simple code quality check

set -e

echo "🔧 Formatting code..."
black src/ tests/

echo "🔍 Linting code..."
ruff check src/ tests/ --fix

echo "🧪 Running tests..."
pytest tests/ -v

echo "✅ All checks passed!"
```

**Make script executable:**
```bash
mkdir -p scripts
chmod +x scripts/check.sh
```

## Testing the Setup

### 1. Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### 2. Test the Tools
```bash
# Run all checks
./scripts/check.sh

# Or run individually:
black src/ tests/
ruff check src/ tests/ --fix
pytest tests/ -v
```

## Benefits
- ✅ **Simple and maintainable** - minimal configuration overhead
- ✅ **Consistent code formatting** - Black handles all formatting decisions
- ✅ **Essential linting** - Ruff catches common errors and enforces imports
- ✅ **Single command** - `./scripts/check.sh` does everything
- ✅ **No IDE lock-in** - works with any editor that supports .editorconfig
- ✅ **Quick adoption** - developers can start using immediately

## Files Created
- `.editorconfig`
- `scripts/check.sh`

## Files Modified
- `pyproject.toml` (added tool configurations)

## What We're NOT Adding (Intentionally)
- ❌ **mypy** - Adds complexity without immediate value
- ❌ **Coverage requirements** - Tests pass or fail, that's enough  
- ❌ **Multiple scripts** - One script is simpler
- ❌ **IDE-specific configs** - .editorconfig works everywhere
- ❌ **Complex pytest config** - Basic pytest works fine

## Next Steps
After implementing this:
1. Run `pip install -e ".[dev]"` to install dev dependencies
2. Run `./scripts/check.sh` before committing changes
3. All future code will be consistently formatted and linted