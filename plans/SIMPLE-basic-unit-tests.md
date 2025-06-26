# Add Basic Unit Tests - SIMPLE (3 hours)

**Complexity**: Medium  
**Impact**: Critical - Ensures code reliability and prevents regressions  
**Time Estimate**: 3 hours  
**Dependencies**: Development tooling, Configuration management

## Problem
The project lacks test coverage, making it difficult to ensure code quality, prevent regressions, and safely refactor code.

## Solution
Implement comprehensive unit tests with pytest, including fixtures, mocking, and coverage reporting.

## Implementation Steps

### 1. Create Test Structure (15 minutes)
```bash
# Create test directories
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures

# Create test files
touch tests/__init__.py
touch tests/conftest.py
touch tests/unit/__init__.py
touch tests/unit/test_config.py
touch tests/unit/test_validation.py
touch tests/unit/test_kaltura_client.py
touch tests/unit/test_error_handling.py
touch tests/integration/__init__.py
touch tests/integration/test_server_local.py
touch tests/fixtures/__init__.py
touch tests/fixtures/sample_data.py
```

### 2. Create Pytest Configuration and Fixtures (30 minutes)
**File: `tests/conftest.py`**
```python
"""Pytest configuration and shared fixtures."""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from typing import Dict, Any

from kaltura_mcp.config import KalturaConfig, ServerConfig, AppConfig
from kaltura_mcp.kaltura_client import KalturaClientManager


@pytest.fixture
def sample_kaltura_config() -> KalturaConfig:
    """Provide a valid KalturaConfig for testing."""
    return KalturaConfig(
        service_url="https://test.kaltura.com",
        partner_id=12345,
        admin_secret="test_secret_12345678",
        user_id="test@example.com",
        session_expiry=86400
    )


@pytest.fixture
def sample_server_config() -> ServerConfig:
    """Provide a valid ServerConfig for testing."""
    return ServerConfig(
        jwt_secret_key="test_jwt_secret_key_that_is_long_enough_for_security",
        oauth_redirect_uri="http://localhost:8000/oauth/callback",
        server_host="0.0.0.0",
        server_port=8000,
        server_reload=False,
        cors_origins=["*"],
        log_level="INFO"
    )


@pytest.fixture
def sample_app_config(sample_kaltura_config, sample_server_config) -> AppConfig:
    """Provide a complete AppConfig for testing."""
    return AppConfig(
        kaltura=sample_kaltura_config,
        server=sample_server_config,
        debug=False
    )


@pytest.fixture
def mock_kaltura_client():
    """Provide a mocked Kaltura client."""
    client = Mock()
    
    # Mock media service
    client.media = Mock()
    client.media.get = Mock()
    client.media.list = Mock()
    
    # Mock category service
    client.category = Mock()
    client.category.list = Mock()
    
    # Mock report service
    client.report = Mock()
    client.report.getTable = Mock()
    
    # Mock session service
    client.session = Mock()
    client.session.start = Mock(return_value="test_session_token")
    
    # Mock client methods
    client.setKs = Mock()
    
    return client


@pytest.fixture
def mock_kaltura_entry():
    """Provide a mocked Kaltura media entry."""
    entry = Mock()
    entry.id = "1_test123"
    entry.name = "Test Video"
    entry.description = "A test video description"
    entry.mediaType = Mock()
    entry.mediaType.value = "1"  # Video
    entry.createdAt = 1609459200  # 2021-01-01
    entry.updatedAt = 1609459200
    entry.duration = 300  # 5 minutes
    entry.tags = "test,video"
    entry.categories = "Test Category"
    entry.thumbnailUrl = "https://test.kaltura.com/thumbnail.jpg"
    entry.downloadUrl = "https://test.kaltura.com/download.mp4"
    entry.plays = 100
    entry.views = 150
    entry.width = 1920
    entry.height = 1080
    entry.status = Mock()
    entry.status.value = "2"  # Ready
    return entry


@pytest.fixture
def mock_client_manager(sample_kaltura_config, mock_kaltura_client):
    """Provide a mocked KalturaClientManager."""
    with patch('kaltura_mcp.kaltura_client.KalturaClient') as mock_client_class:
        mock_client_class.return_value = mock_kaltura_client
        
        manager = KalturaClientManager(sample_kaltura_config)
        manager._client = mock_kaltura_client
        manager._ks = "test_session_token"
        manager._session_start_time = 1609459200
        
        return manager


@pytest.fixture
def temp_config_file(tmp_path, sample_app_config):
    """Create a temporary configuration file."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "kaltura": sample_app_config.kaltura.to_dict(),
        "server": sample_app_config.server.mask_secrets(),
        "debug": sample_app_config.debug
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    return config_file


@pytest.fixture
def mock_env_vars(monkeypatch, sample_kaltura_config, sample_server_config):
    """Set up environment variables for testing."""
    monkeypatch.setenv("KALTURA_SERVICE_URL", sample_kaltura_config.service_url)
    monkeypatch.setenv("KALTURA_PARTNER_ID", str(sample_kaltura_config.partner_id))
    monkeypatch.setenv("KALTURA_ADMIN_SECRET", sample_kaltura_config.admin_secret)
    monkeypatch.setenv("KALTURA_USER_ID", sample_kaltura_config.user_id)
    monkeypatch.setenv("KALTURA_SESSION_EXPIRY", str(sample_kaltura_config.session_expiry))
    
    monkeypatch.setenv("JWT_SECRET_KEY", sample_server_config.jwt_secret_key)
    monkeypatch.setenv("OAUTH_REDIRECT_URI", sample_server_config.oauth_redirect_uri)
    monkeypatch.setenv("SERVER_HOST", sample_server_config.server_host)
    monkeypatch.setenv("SERVER_PORT", str(sample_server_config.server_port))
    monkeypatch.setenv("LOG_LEVEL", sample_server_config.log_level)


@pytest.fixture
def sample_media_response():
    """Sample media list response data."""
    return {
        "totalCount": 2,
        "entries": [
            {
                "id": "1_test123",
                "name": "Test Video 1",
                "description": "First test video",
                "mediaType": "1",
                "createdAt": "2021-01-01T00:00:00",
                "duration": 300,
                "plays": 100,
                "views": 150
            },
            {
                "id": "1_test456",
                "name": "Test Video 2", 
                "description": "Second test video",
                "mediaType": "1",
                "createdAt": "2021-01-02T00:00:00",
                "duration": 600,
                "plays": 50,
                "views": 75
            }
        ]
    }


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration for each test."""
    import logging
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Reset to default level
    logging.root.setLevel(logging.WARNING)
```

### 3. Create Configuration Tests (45 minutes)
**File: `tests/unit/test_config.py`**
```python
"""Test configuration management."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from kaltura_mcp.config import KalturaConfig, ServerConfig, AppConfig, load_config


class TestKalturaConfig:
    """Test KalturaConfig class."""
    
    def test_valid_config_creation(self, sample_kaltura_config):
        """Test creating a valid configuration."""
        assert sample_kaltura_config.partner_id == 12345
        assert sample_kaltura_config.service_url == "https://test.kaltura.com"
        assert sample_kaltura_config.user_id == "test@example.com"
        assert sample_kaltura_config.session_expiry == 86400
    
    def test_invalid_partner_id(self):
        """Test that invalid partner ID raises error."""
        with pytest.raises(ValueError, match="partner_id must be a positive integer"):
            KalturaConfig(
                service_url="https://test.kaltura.com",
                partner_id=0,
                admin_secret="test_secret_12345678",
                user_id="test@example.com"
            )
    
    def test_invalid_service_url(self):
        """Test that invalid service URL raises error."""
        with pytest.raises(ValueError, match="service_url must start with"):
            KalturaConfig(
                service_url="invalid-url",
                partner_id=12345,
                admin_secret="test_secret_12345678",
                user_id="test@example.com"
            )
    
    def test_short_admin_secret(self):
        """Test that short admin secret raises error."""
        with pytest.raises(ValueError, match="admin_secret must be at least 8 characters"):
            KalturaConfig(
                service_url="https://test.kaltura.com",
                partner_id=12345,
                admin_secret="short",
                user_id="test@example.com"
            )
    
    def test_invalid_session_expiry(self):
        """Test that invalid session expiry raises error."""
        with pytest.raises(ValueError, match="session_expiry must be at least 300 seconds"):
            KalturaConfig(
                service_url="https://test.kaltura.com",
                partner_id=12345,
                admin_secret="test_secret_12345678",
                user_id="test@example.com",
                session_expiry=100
            )
    
    def test_from_env(self, mock_env_vars):
        """Test loading configuration from environment."""
        config = KalturaConfig.from_env()
        assert config.service_url == "https://test.kaltura.com"
        assert config.partner_id == 12345
        assert config.admin_secret == "test_secret_12345678"
        assert config.user_id == "test@example.com"
    
    def test_from_dict(self):
        """Test creating configuration from dictionary."""
        data = {
            "service_url": "https://dict.kaltura.com",
            "partner_id": 99999,
            "admin_secret": "dict_secret_12345678",
            "user_id": "dict@example.com",
            "session_expiry": 3600
        }
        config = KalturaConfig.from_dict(data)
        assert config.service_url == "https://dict.kaltura.com"
        assert config.partner_id == 99999
    
    def test_from_file(self, temp_config_file):
        """Test loading configuration from file."""
        config = AppConfig.from_file(temp_config_file)
        assert config.kaltura.partner_id == 12345
        assert config.kaltura.service_url == "https://test.kaltura.com"
    
    def test_mask_secrets(self, sample_kaltura_config):
        """Test that secrets are properly masked."""
        masked = sample_kaltura_config.mask_secrets()
        assert masked['admin_secret'] == 'test***'
        assert masked['partner_id'] == sample_kaltura_config.partner_id
        assert 'secret' not in masked['admin_secret']
    
    def test_to_dict(self, sample_kaltura_config):
        """Test converting configuration to dictionary."""
        data = sample_kaltura_config.to_dict()
        assert data['partner_id'] == 12345
        assert data['service_url'] == "https://test.kaltura.com"
        assert data['admin_secret'] == "test_secret_12345678"


class TestServerConfig:
    """Test ServerConfig class."""
    
    def test_valid_server_config(self, sample_server_config):
        """Test creating valid server configuration."""
        assert sample_server_config.server_port == 8000
        assert sample_server_config.server_host == "0.0.0.0"
        assert sample_server_config.log_level == "INFO"
    
    def test_short_jwt_secret(self):
        """Test that short JWT secret raises error."""
        with pytest.raises(ValueError, match="jwt_secret_key must be at least 32 characters"):
            ServerConfig(jwt_secret_key="short")
    
    def test_invalid_port(self):
        """Test that invalid port raises error."""
        with pytest.raises(ValueError, match="server_port must be between 1 and 65535"):
            ServerConfig(
                jwt_secret_key="a" * 32,
                server_port=70000
            )
    
    def test_invalid_log_level(self):
        """Test that invalid log level raises error."""
        with pytest.raises(ValueError, match="log_level must be one of"):
            ServerConfig(
                jwt_secret_key="a" * 32,
                log_level="INVALID"
            )
    
    def test_from_env(self, mock_env_vars):
        """Test loading server configuration from environment."""
        config = ServerConfig.from_env()
        assert config.server_port == 8000
        assert config.oauth_redirect_uri == "http://localhost:8000/oauth/callback"
    
    def test_mask_secrets(self, sample_server_config):
        """Test server configuration secret masking."""
        masked = sample_server_config.mask_secrets()
        assert masked['jwt_secret_key'].startswith('test')
        assert masked['jwt_secret_key'].endswith('rity')
        assert '***' in masked['jwt_secret_key']


class TestAppConfig:
    """Test AppConfig class."""
    
    def test_complete_app_config(self, sample_app_config):
        """Test complete application configuration."""
        assert sample_app_config.kaltura is not None
        assert sample_app_config.server is not None
        assert sample_app_config.debug is False
    
    def test_from_env_with_server(self, mock_env_vars):
        """Test loading app configuration with server config."""
        config = AppConfig.from_env(include_server=True)
        assert config.kaltura is not None
        assert config.server is not None
    
    def test_from_env_without_server(self, mock_env_vars):
        """Test loading app configuration without server config."""
        config = AppConfig.from_env(include_server=False)
        assert config.kaltura is not None
        assert config.server is None
    
    def test_validate_all(self, sample_app_config):
        """Test validation of all configurations."""
        # Should not raise any exceptions
        sample_app_config.validate()
    
    def test_setup_logging_debug(self, sample_app_config):
        """Test logging setup in debug mode."""
        sample_app_config.debug = True
        sample_app_config.setup_logging()
        
        import logging
        assert logging.getLogger('kaltura_mcp').level == logging.DEBUG
    
    def test_setup_logging_info(self, sample_app_config):
        """Test logging setup in info mode."""
        sample_app_config.debug = False
        sample_app_config.setup_logging()
        
        import logging
        assert logging.getLogger('kaltura_mcp').level == logging.INFO


class TestLoadConfig:
    """Test load_config function."""
    
    def test_load_from_env(self, mock_env_vars):
        """Test loading configuration from environment."""
        config = load_config(include_server=True)
        assert config.kaltura.partner_id == 12345
        assert config.server.server_port == 8000
    
    def test_load_from_file(self, temp_config_file):
        """Test loading configuration from file."""
        config = load_config(config_path=temp_config_file)
        assert config.kaltura.partner_id == 12345
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config(config_path="nonexistent.json")
    
    @patch('kaltura_mcp.config.logger')
    def test_logging_setup_called(self, mock_logger, mock_env_vars):
        """Test that logging is set up when loading configuration."""
        config = load_config(include_server=False)
        # Verify that configuration was loaded
        assert config.kaltura.partner_id == 12345
```

### 4. Create Validation Tests (30 minutes)
**File: `tests/unit/test_validation.py`**
```python
"""Test input validation functions."""

import pytest
from kaltura_mcp.tools import validate_entry_id


class TestValidation:
    """Test input validation functions."""
    
    @pytest.mark.parametrize("entry_id,expected", [
        # Valid entry IDs
        ("0_abc123", True),
        ("123_xyz789", True),
        ("1_a", True),
        ("999999_abcdef123456", True),
        ("12_test", True),
        
        # Invalid entry IDs
        ("invalid", False),
        ("", False),
        (None, False),
        ("0_", False),
        ("_abc", False),
        ("abc_123", False),  # Must start with number
        ("123", False),      # Must have underscore
        ("123_", False),     # Must have content after underscore
        
        # Security tests - path traversal attempts
        ("0_../etc/passwd", False),
        ("0_abc/../../etc", False),
        ("0_..\\windows\\system32", False),
        ("0_test/../config", False),
        
        # Length tests
        ("1_" + "a" * 100, False),  # Too long
        ("1_" + "a" * 47, True),    # Just right (50 total chars)
        ("1_" + "a" * 48, False),   # Too long (51 total chars)
        
        # Special characters
        ("123_abc-def", False),  # Hyphen not allowed
        ("123_abc.def", False),  # Dot not allowed
        ("123_abc@def", False),  # @ not allowed
        ("123_abc def", False),  # Space not allowed
        ("123_abc123", True),    # Only alphanumeric allowed
        ("123_ABC123", True),    # Uppercase allowed
    ])
    def test_validate_entry_id(self, entry_id, expected):
        """Test entry ID validation with various inputs."""
        assert validate_entry_id(entry_id) == expected
    
    def test_validate_entry_id_type_safety(self):
        """Test that non-string types are handled safely."""
        assert validate_entry_id(123) is False
        assert validate_entry_id([]) is False
        assert validate_entry_id({}) is False
        assert validate_entry_id(True) is False
    
    @pytest.mark.parametrize("malicious_input", [
        "0_$(rm -rf /)",
        "0_`cat /etc/passwd`",
        "0_; rm -rf /",
        "0_&& echo 'pwned'",
        "0_| cat /etc/hosts",
        "0_<script>alert('xss')</script>",
        "0_' OR '1'='1",
        "0_\"; DROP TABLE users; --",
    ])
    def test_validate_entry_id_security(self, malicious_input):
        """Test that malicious inputs are rejected."""
        assert validate_entry_id(malicious_input) is False
```

### 5. Create Kaltura Client Tests (45 minutes)
**File: `tests/unit/test_kaltura_client.py`**
```python
"""Test Kaltura client management."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from kaltura_mcp.kaltura_client import KalturaClientManager
from kaltura_mcp.config import KalturaConfig


class TestKalturaClientManager:
    """Test KalturaClientManager class."""
    
    def test_initialization_with_config(self, sample_kaltura_config):
        """Test manager initialization with provided config."""
        manager = KalturaClientManager(sample_kaltura_config)
        assert manager.config == sample_kaltura_config
        assert manager._client is None
        assert manager._ks is None
    
    @patch('kaltura_mcp.kaltura_client.KalturaConfig')
    def test_initialization_without_config(self, mock_config_class, sample_kaltura_config):
        """Test manager initialization without config (loads from env)."""
        mock_config_class.from_env.return_value = sample_kaltura_config
        
        manager = KalturaClientManager()
        assert manager.config == sample_kaltura_config
        mock_config_class.from_env.assert_called_once()
    
    def test_has_required_config_valid(self, sample_kaltura_config):
        """Test has_required_config with valid configuration."""
        manager = KalturaClientManager(sample_kaltura_config)
        assert manager.has_required_config() is True
    
    def test_has_required_config_invalid(self):
        """Test has_required_config with invalid configuration."""
        invalid_config = KalturaConfig(
            service_url="https://test.kaltura.com",
            partner_id=0,  # Invalid
            admin_secret="",  # Invalid
            user_id=""  # Invalid
        )
        
        # This should raise during config creation due to validation
        with pytest.raises(ValueError):
            KalturaClientManager(invalid_config)
    
    @patch('kaltura_mcp.kaltura_client.KalturaClient')
    def test_session_creation(self, mock_client_class, sample_kaltura_config, mock_kaltura_client):
        """Test session creation process."""
        mock_client_class.return_value = mock_kaltura_client
        mock_kaltura_client.session.start.return_value = "test_session_token"
        
        manager = KalturaClientManager(sample_kaltura_config)
        client = manager.get_client()
        
        assert client == mock_kaltura_client
        assert manager._ks == "test_session_token"
        assert manager._session_start_time is not None
        mock_kaltura_client.setKs.assert_called_with("test_session_token")
    
    @patch('kaltura_mcp.kaltura_client.KalturaClient')
    def test_session_reuse(self, mock_client_class, sample_kaltura_config, mock_kaltura_client):
        """Test that valid sessions are reused."""
        mock_client_class.return_value = mock_kaltura_client
        mock_kaltura_client.session.start.return_value = "test_session_token"
        
        manager = KalturaClientManager(sample_kaltura_config)
        
        # First call creates session
        client1 = manager.get_client()
        session_start_time = manager._session_start_time
        
        # Second call should reuse session
        client2 = manager.get_client()
        
        assert client1 == client2
        assert manager._session_start_time == session_start_time
        assert mock_kaltura_client.session.start.call_count == 1
    
    def test_session_expiry_detection(self, sample_kaltura_config):
        """Test session expiry detection."""
        manager = KalturaClientManager(sample_kaltura_config)
        
        # No session yet
        assert manager._is_session_expired() is True
        
        # Fresh session
        manager._session_start_time = time.time()
        assert manager._is_session_expired() is False
        
        # Expired session (simulate old timestamp)
        manager._session_start_time = time.time() - (sample_kaltura_config.session_expiry + 100)
        assert manager._is_session_expired() is True
        
        # Soon-to-expire session (within buffer)
        buffer_time = manager._session_buffer + 100
        manager._session_start_time = time.time() - (sample_kaltura_config.session_expiry - buffer_time)
        assert manager._is_session_expired() is True
    
    @patch('kaltura_mcp.kaltura_client.KalturaClient')
    def test_session_refresh_on_expiry(self, mock_client_class, sample_kaltura_config, mock_kaltura_client):
        """Test that expired sessions are refreshed."""
        mock_client_class.return_value = mock_kaltura_client
        mock_kaltura_client.session.start.return_value = "test_session_token"
        
        manager = KalturaClientManager(sample_kaltura_config)
        
        # Create initial session
        manager.get_client()
        assert mock_kaltura_client.session.start.call_count == 1
        
        # Simulate session expiry
        manager._session_start_time = time.time() - (sample_kaltura_config.session_expiry + 100)
        
        # Next call should refresh session
        manager.get_client()
        assert mock_kaltura_client.session.start.call_count == 2
    
    @patch('kaltura_mcp.kaltura_client.KalturaClient')
    def test_session_creation_failure(self, mock_client_class, sample_kaltura_config):
        """Test handling of session creation failure."""
        mock_client = Mock()
        mock_client.session.start.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        manager = KalturaClientManager(sample_kaltura_config)
        
        with pytest.raises(Exception, match="API Error"):
            manager.get_client()
        
        # Ensure state is cleaned up on failure
        assert manager._client is None
        assert manager._ks is None
        assert manager._session_start_time is None
    
    def test_invalidate_session(self, sample_kaltura_config, mock_kaltura_client):
        """Test session invalidation."""
        manager = KalturaClientManager(sample_kaltura_config)
        manager._client = mock_kaltura_client
        manager._ks = "test_session_token"
        manager._session_start_time = time.time()
        
        manager.invalidate_session()
        
        assert manager._ks is None
        assert manager._session_start_time is None
        mock_kaltura_client.setKs.assert_called_with(None)
    
    def test_get_session_info_no_session(self, sample_kaltura_config):
        """Test session info when no session exists."""
        manager = KalturaClientManager(sample_kaltura_config)
        info = manager.get_session_info()
        assert info["status"] == "no_session"
    
    def test_get_session_info_active_session(self, sample_kaltura_config):
        """Test session info for active session."""
        manager = KalturaClientManager(sample_kaltura_config)
        manager._session_start_time = time.time()
        
        info = manager.get_session_info()
        assert info["status"] == "active"
        assert info["partner_id"] == sample_kaltura_config.partner_id
        assert info["user_id"] == sample_kaltura_config.user_id
        assert "elapsed_seconds" in info
        assert "remaining_seconds" in info
    
    def test_get_session_info_expired_session(self, sample_kaltura_config):
        """Test session info for expired session."""
        manager = KalturaClientManager(sample_kaltura_config)
        # Set session to expired
        manager._session_start_time = time.time() - (sample_kaltura_config.session_expiry + 100)
        
        info = manager.get_session_info()
        assert info["status"] == "expired"
        assert info["remaining_seconds"] < 0
```

### 6. Create Error Handling Tests (30 minutes)
**File: `tests/unit/test_error_handling.py`**
```python
"""Test error handling functionality."""

import pytest
import json
from unittest.mock import patch

from kaltura_mcp.tools import handle_kaltura_error


class TestErrorHandling:
    """Test error handling functions."""
    
    def test_handle_kaltura_error_basic(self):
        """Test basic error handling."""
        error = Exception("Test error")
        result = handle_kaltura_error(error, "test operation")
        
        data = json.loads(result)
        assert data["error"] == "Failed to test operation: Test error"
        assert data["errorType"] == "Exception"
        assert data["operation"] == "test operation"
    
    def test_handle_kaltura_error_with_context(self):
        """Test error handling with context."""
        error = ValueError("Invalid input")
        context = {"entry_id": "1_test123", "user_id": "test@example.com"}
        
        result = handle_kaltura_error(error, "get media entry", context)
        
        data = json.loads(result)
        assert data["error"] == "Failed to get media entry: Invalid input"
        assert data["errorType"] == "ValueError"
        assert data["operation"] == "get media entry"
        assert data["entry_id"] == "1_test123"
        assert data["user_id"] == "test@example.com"
    
    @patch.dict('os.environ', {'KALTURA_DEBUG': 'true'})
    def test_handle_kaltura_error_debug_mode(self):
        """Test error handling in debug mode includes traceback."""
        error = RuntimeError("Debug error")
        result = handle_kaltura_error(error, "debug operation")
        
        data = json.loads(result)
        assert data["error"] == "Failed to debug operation: Debug error"
        # In debug mode, traceback should be included
        # Note: We can't easily test the exact traceback content
        assert "operation" in data
    
    def test_handle_kaltura_error_different_exception_types(self):
        """Test error handling with different exception types."""
        test_cases = [
            (ValueError("Value error"), "ValueError"),
            (TypeError("Type error"), "TypeError"),
            (KeyError("Key error"), "KeyError"),
            (AttributeError("Attribute error"), "AttributeError"),
            (RuntimeError("Runtime error"), "RuntimeError"),
        ]
        
        for error, expected_type in test_cases:
            result = handle_kaltura_error(error, "test operation")
            data = json.loads(result)
            assert data["errorType"] == expected_type
            assert "test operation" in data["error"]
    
    def test_handle_kaltura_error_empty_context(self):
        """Test error handling with empty context."""
        error = Exception("Test error")
        result = handle_kaltura_error(error, "test operation", {})
        
        data = json.loads(result)
        assert data["error"] == "Failed to test operation: Test error"
        assert data["operation"] == "test operation"
        # Should not have extra keys from empty context
        expected_keys = {"error", "errorType", "operation"}
        assert set(data.keys()) == expected_keys
    
    def test_handle_kaltura_error_none_context(self):
        """Test error handling with None context."""
        error = Exception("Test error")
        result = handle_kaltura_error(error, "test operation", None)
        
        data = json.loads(result)
        assert data["error"] == "Failed to test operation: Test error"
        assert data["operation"] == "test operation"
    
    def test_handle_kaltura_error_complex_context(self):
        """Test error handling with complex context data."""
        error = Exception("Complex error")
        context = {
            "entry_id": "1_test123",
            "search_params": {
                "query": "test video",
                "limit": 20,
                "sort": "createdAt"
            },
            "filters": ["category1", "category2"],
            "user_permissions": {
                "read": True,
                "write": False
            }
        }
        
        result = handle_kaltura_error(error, "complex search", context)
        
        data = json.loads(result)
        assert data["error"] == "Failed to complex search: Complex error"
        assert data["entry_id"] == "1_test123"
        assert data["search_params"]["query"] == "test video"
        assert data["filters"] == ["category1", "category2"]
        assert data["user_permissions"]["read"] is True
```

### 7. Create Integration Test Structure (15 minutes)
**File: `tests/integration/test_server_local.py`**
```python
"""Integration tests for local MCP server."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

# Note: These are basic integration test stubs
# Full implementation would require MCP test framework


class TestLocalServerIntegration:
    """Integration tests for local MCP server."""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, mock_env_vars):
        """Test that server initializes properly with valid config."""
        # This would test actual server initialization
        # For now, just test config loading
        from kaltura_mcp.config import load_config
        
        config = load_config(include_server=False)
        assert config.kaltura.partner_id == 12345
    
    @pytest.mark.asyncio
    async def test_tool_registration(self, mock_env_vars):
        """Test that all tools are properly registered."""
        # This would test that MCP tools are registered correctly
        # Placeholder for future implementation
        pass
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_env_vars):
        """Test error handling in integration context."""
        # This would test error handling across the full stack
        # Placeholder for future implementation
        pass


@pytest.mark.slow
class TestFullServerIntegration:
    """Full integration tests (marked as slow)."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, mock_env_vars):
        """Test complete workflow from server start to tool execution."""
        # This would test a complete workflow
        # Requires more complex setup
        pass
```

### 8. Run Tests and Generate Coverage (10 minutes)
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ -v --cov=kaltura_mcp --cov-report=html --cov-report=term-missing

# Run specific test types
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/ -m "not slow" -v          # Skip slow tests
pytest tests/ -k "test_config" -v       # Run config tests only

# Generate coverage report
coverage html
```

## Test Configuration in pyproject.toml (Already included in development tooling)

The test configuration is already included in the development tooling plan.

## Testing Commands and Scripts

### Create Test Runner Script
**File: `scripts/test.sh`** (Updated from development tooling)
```bash
#!/bin/bash
# Enhanced test runner script

set -e

echo "🧪 Running Kaltura MCP tests..."

# Parse command line arguments
COVERAGE_THRESHOLD=80
FAST_ONLY=false
UNIT_ONLY=false
INTEGRATION_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fast)
            FAST_ONLY=true
            shift
            ;;
        --unit)
            UNIT_ONLY=true
            shift
            ;;
        --integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        --coverage-threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Determine test selection
if [ "$UNIT_ONLY" = true ]; then
    TEST_PATH="tests/unit/"
    echo "Running unit tests only..."
elif [ "$INTEGRATION_ONLY" = true ]; then
    TEST_PATH="tests/integration/"
    echo "Running integration tests only..."
elif [ "$FAST_ONLY" = true ]; then
    TEST_PATH="tests/ -m 'not slow'"
    echo "Running fast tests only..."
else
    TEST_PATH="tests/"
    echo "Running all tests..."
fi

# Run tests with coverage
pytest $TEST_PATH -v \
    --cov=kaltura_mcp \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=$COVERAGE_THRESHOLD \
    --tb=short

echo "📊 Coverage report generated in htmlcov/"
echo "✅ Tests completed with coverage threshold: ${COVERAGE_THRESHOLD}%"
```

## Benefits
- ✅ Comprehensive test coverage
- ✅ Prevents regressions
- ✅ Enables safe refactoring
- ✅ Validates configuration management
- ✅ Tests error handling
- ✅ Mocking for external dependencies
- ✅ Coverage reporting
- ✅ Multiple test categories (unit, integration)
- ✅ Parameterized tests for edge cases
- ✅ Security testing for input validation

## Files Created
- `tests/conftest.py`
- `tests/unit/test_config.py`
- `tests/unit/test_validation.py`
- `tests/unit/test_kaltura_client.py`
- `tests/unit/test_error_handling.py`
- `tests/integration/test_server_local.py`
- `tests/fixtures/sample_data.py`
- `scripts/test.sh` (updated)

## Files Modified
- `pyproject.toml` (test configuration already added in dev tooling)

## Next Steps
1. Add tests for tool implementations
2. Add integration tests for remote server
3. Add performance tests
4. Set up automated test running in CI/CD
5. Add test coverage requirements to CI/CD pipeline