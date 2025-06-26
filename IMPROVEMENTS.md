# Kaltura MCP Server - Improvement Recommendations

## High Priority Improvements

### 1. Code Refactoring

#### Split tools.py
The `tools.py` file (1282 lines) should be split into focused modules:

```
src/kaltura_mcp/tools/
├── __init__.py          # Export all tools
├── media.py             # Media entry operations
├── search.py            # Search and discovery tools
├── analytics.py         # Analytics and reporting
├── assets.py            # Caption and attachment handling
└── utils.py             # Common utilities (validation, error handling)
```

#### Create Tool Registry
Replace if-elif chains with a registry pattern:

```python
# src/kaltura_mcp/tool_registry.py
from typing import Dict, Callable, Any
import types

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, types.Tool] = {}
    
    def register(self, name: str, handler: Callable, definition: types.Tool):
        self._tools[name] = handler
        self._definitions[name] = definition
    
    async def execute(self, name: str, manager: Any, **kwargs):
        if handler := self._tools.get(name):
            return await handler(manager, **kwargs)
        raise ValueError(f"Unknown tool: {name}")
    
    def get_definitions(self) -> List[types.Tool]:
        return list(self._definitions.values())

# Usage
registry = ToolRegistry()
registry.register("get_media_entry", get_media_entry, media_entry_tool_def)
```

#### Extract HTML Templates
Move HTML content to template files:

```
src/kaltura_mcp/templates/
├── oauth_form.html
└── oauth_success.html
```

### 2. Add Test Coverage

#### Unit Tests Structure
```
tests/
├── unit/
│   ├── test_media_tools.py
│   ├── test_search_tools.py
│   ├── test_analytics_tools.py
│   ├── test_kaltura_client.py
│   └── test_validation.py
├── integration/
│   ├── test_server_local.py
│   ├── test_server_remote.py
│   └── test_proxy_client.py
└── conftest.py          # Pytest fixtures
```

#### Example Test
```python
# tests/unit/test_validation.py
import pytest
from kaltura_mcp.tools.utils import validate_entry_id

class TestValidation:
    def test_validate_entry_id_valid(self):
        assert validate_entry_id("0_abc123") is True
        assert validate_entry_id("123_xyz789") is True
    
    def test_validate_entry_id_invalid(self):
        assert validate_entry_id("invalid") is False
        assert validate_entry_id("") is False
        assert validate_entry_id(None) is False
        assert validate_entry_id("0_../etc/passwd") is False
```

### 3. Configuration Management

Create a proper configuration system:

```python
# src/kaltura_mcp/config.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class KalturaConfig:
    service_url: str
    partner_id: str
    admin_secret: str
    user_id: str
    session_expiry: int = 86400
    
    @classmethod
    def from_env(cls) -> 'KalturaConfig':
        return cls(
            service_url=os.environ['KALTURA_SERVICE_URL'],
            partner_id=os.environ['KALTURA_PARTNER_ID'],
            admin_secret=os.environ['KALTURA_ADMIN_SECRET'],
            user_id=os.environ['KALTURA_USER_ID'],
            session_expiry=int(os.environ.get('KALTURA_SESSION_EXPIRY', 86400))
        )
    
    def validate(self):
        if not all([self.service_url, self.partner_id, self.admin_secret, self.user_id]):
            raise ValueError("Missing required configuration")
```

### 4. Add Type Safety

Use Pydantic models for request/response validation:

```python
# src/kaltura_mcp/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class MediaEntryRequest(BaseModel):
    entry_id: str = Field(..., regex=r'^[0-9]+_[a-zA-Z0-9]+$')
    
    @validator('entry_id')
    def validate_entry_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Invalid entry ID length')
        return v

class MediaEntryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    media_type: str
    created_at: Optional[datetime]
    duration: Optional[int]
    plays: int = 0
    views: int = 0
```

### 5. Development Tooling

#### Add pre-commit configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.292
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### Add GitHub Actions CI/CD
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=kaltura_mcp --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 6. Documentation Improvements

#### Add API Documentation
```python
# src/kaltura_mcp/tools/media.py
async def get_media_entry(
    manager: KalturaClientManager,
    entry_id: str
) -> str:
    """
    Retrieve detailed information about a media entry.
    
    Args:
        manager: Kaltura client manager instance
        entry_id: The Kaltura entry ID (format: 0_xxxxxx)
    
    Returns:
        JSON string containing entry details
        
    Raises:
        ValueError: If entry_id format is invalid
        KalturaException: If API call fails
        
    Example:
        >>> result = await get_media_entry(manager, "0_abc123")
        >>> data = json.loads(result)
        >>> print(data['name'])
    """
```

#### Add Architecture Decision Records
```markdown
# docs/adr/001-split-deployment-modes.md
# ADR-001: Split Deployment Modes

## Status
Accepted

## Context
We need to support both local Claude Desktop usage and remote multi-tenant deployments.

## Decision
Implement three separate deployment modes:
1. Local stdio server for Claude Desktop
2. Remote HTTP/SSE server for hosted deployments
3. Proxy client to bridge local Claude to remote server

## Consequences
- More complex codebase with three entry points
- Better security isolation between modes
- Easier to optimize each mode independently
```

### 7. Performance Optimizations

#### Add Connection Pooling
```python
# src/kaltura_mcp/http_client.py
import httpx
from typing import Optional

class HTTPClientPool:
    _instance: Optional[httpx.AsyncClient] = None
    
    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._instance is None:
            cls._instance = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        return cls._instance
    
    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.aclose()
            cls._instance = None
```

#### Add Caching Layer
```python
# src/kaltura_mcp/cache.py
from functools import lru_cache
from typing import Optional
import hashlib
import json

class SimpleCache:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache = {}
    
    def key_for(self, func_name: str, **kwargs) -> str:
        data = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(f"{func_name}:{data}".encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def get(self, key: str) -> Optional[str]:
        # Implementation with TTL support
        pass
```

## Implementation Priority

1. **Immediate** (Breaking issues):
   - Fix the ADMIN_CONSOLE error ✅ (Already fixed)
   - Add basic error handling tests

2. **Short-term** (Code quality):
   - Split tools.py into modules
   - Add tool registry pattern
   - Extract HTML templates
   - Add basic unit tests

3. **Medium-term** (Maintainability):
   - Add comprehensive test coverage
   - Implement configuration management
   - Add type safety with Pydantic
   - Set up CI/CD pipeline

4. **Long-term** (Scale & Performance):
   - Add caching layer
   - Implement connection pooling
   - Add performance monitoring
   - Create deployment automation

## Conclusion

The Kaltura MCP Server is well-architected with good security practices and comprehensive documentation. The main areas for improvement are:

1. **Code organization** - Split large files and reduce duplication
2. **Testing** - Add comprehensive test coverage
3. **Type safety** - Use proper type hints and validation
4. **Development tooling** - Add linting, formatting, and CI/CD

These improvements will make the codebase more maintainable, easier to extend, and more reliable for production use.