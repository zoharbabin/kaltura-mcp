# Contributing to Kaltura MCP Server

Thank you for your interest in contributing to the Kaltura MCP Server! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct (see CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Issues

1. **Check existing issues** - Before creating a new issue, please check if it already exists
2. **Use issue templates** - When available, use the appropriate issue template
3. **Provide details** - Include:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs

### Suggesting Features

1. **Check the roadmap** - Review existing plans in the `/plans` directory
2. **Create a feature request** - Open an issue with:
   - Clear use case description
   - Benefits to users
   - Potential implementation approach

### Submitting Code

1. **Fork the repository** - Create your own fork to work on
2. **Create a feature branch** - Use descriptive branch names like `feature/add-playlist-support`
3. **Follow code style** - Run `./scripts/check.sh` before committing
4. **Write tests** - Add tests for new functionality
5. **Update documentation** - Keep README and docstrings up to date
6. **Commit messages** - Use conventional commit format:
   ```
   feat: Add playlist management tools
   fix: Correct analytics date parsing
   docs: Update README with new examples
   test: Add tests for caption retrieval
   refactor: Split search functions into modules
   ```

### Pull Request Process

1. **Ensure all tests pass** - Run `./scripts/check.sh`
2. **Update CHANGELOG.md** - Add your changes to the Unreleased section
3. **Create pull request** - Include:
   - Clear description of changes
   - Link to related issues
   - Screenshots for UI changes
   - Test results
4. **Address review feedback** - Be responsive to maintainer comments

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/zoharbabin/kaltura-mcp.git
   cd kaltura-mcp
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Set up pre-commit checks:
   ```bash
   # Run before each commit
   ./scripts/check.sh
   ```

## Code Style Guidelines

- **Python version**: Support Python 3.10+
- **Formatting**: Use Black with 100-char line length
- **Linting**: Follow Ruff rules (pycodestyle + pyflakes + isort)
- **Type hints**: Use type annotations where beneficial
- **Docstrings**: Add docstrings to all public functions and classes
- **Security**: Never commit credentials or sensitive data

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use pytest for all tests
- Follow existing test patterns in `/tests`
- Test both success and error cases

## Documentation Guidelines

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update TUTORIAL.md with new use cases
- Keep plans in `/plans` directory updated

## Questions?

If you have questions, feel free to:
- Open a discussion issue
- Contact the maintainers
- Review existing documentation

Thank you for contributing to make Kaltura MCP Server better!