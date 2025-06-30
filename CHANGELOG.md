# Changelog

All notable changes to the Kaltura MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Elegant modular tools architecture - split monolithic tools.py into 5 focused domain modules
- Comprehensive unit test suite with 58 tests covering all critical functionality
- Development tooling with Black formatting and Ruff linting
- Unified check script for development workflow
- Secure .env credential management system
- Support for both stdio (local) and remote (HTTP/SSE) deployment modes
- JWT-based authentication for remote mode
- Proxy client for Claude Desktop integration with remote servers
- Comprehensive tutorial with real-world use cases

### Changed
- Simplified .env configuration - removed redundant .env.stdio.example and .env.remote.example files
- Improved error handling with centralized error response formatting
- Enhanced security validation for entry IDs to prevent injection attacks

### Security
- Input validation for all entry IDs to prevent command injection
- Secure credential handling with environment variables
- Read-only API operations to prevent data modification
- JWT token authentication for remote mode

## [0.1.0] - 2024-12-01

### Added
- Initial release with 10 core Kaltura API tools
- Media discovery and search capabilities
- Content analysis with caption and attachment support
- Category management functionality
- Analytics retrieval with multiple report types
- Download URL generation for media files
- Thumbnail URL generation with custom dimensions
- Advanced search with eSearch API integration
- Docker support for easy deployment
- Comprehensive README documentation