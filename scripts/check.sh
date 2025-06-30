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