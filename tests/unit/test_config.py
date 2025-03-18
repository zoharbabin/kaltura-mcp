"""
Tests for configuration management.
"""
import pytest
import os
from unittest.mock import patch, mock_open

from kaltura_mcp.config import load_config, _parse_config_data, _apply_env_overrides, _validate_config

def test_parse_config_data():
    """Test parsing configuration from dictionary."""
    config_data = {
        "kaltura": {
            "partner_id": 123,
            "admin_secret": "test_secret",
            "user_id": "test_user",
            "service_url": "https://example.com"
        },
        "server": {
            "log_level": "DEBUG",
            "transport": "stdio",
            "port": 8000
        }
    }
    
    config = _parse_config_data(config_data)
    
    assert config.kaltura.partner_id == 123
    assert config.kaltura.admin_secret == "test_secret"
    assert config.kaltura.user_id == "test_user"
    assert config.kaltura.service_url == "https://example.com"
    assert config.server.log_level == "DEBUG"
    assert config.server.transport == "stdio"
    assert config.server.port == 8000

def test_apply_env_overrides():
    """Test applying environment variable overrides to configuration."""
    from kaltura_mcp.config import Config, KalturaConfig, ServerConfig, LoggingConfig, ContextConfig
    
    # Create a base config
    config = Config(
        kaltura=KalturaConfig(
            partner_id=100,
            admin_secret="original_secret",
            user_id="original_user",
            service_url="https://original.com"
        ),
        server=ServerConfig(
            log_level="INFO",
            transport="websocket",
            port=9000,
            host="localhost",
            debug=False
        ),
        logging=LoggingConfig(
            level="INFO",
            file=None
        ),
        context=ContextConfig(
            default_strategy="selective",
            max_entries=50,
            max_context_size=5000
        )
    )
    
    # Apply environment variable overrides
    with patch.dict(os.environ, {
        "KALTURA_PARTNER_ID": "123",
        "KALTURA_ADMIN_SECRET": "test_secret",
        "KALTURA_USER_ID": "test_user",
        "KALTURA_SERVICE_URL": "https://example.com",
        "KALTURA_MCP_LOG_LEVEL": "DEBUG",
        "KALTURA_MCP_TRANSPORT": "stdio",
        "KALTURA_MCP_PORT": "8000",
        "KALTURA_MCP_HOST": "0.0.0.0",
        "KALTURA_MCP_DEBUG": "true",
        "KALTURA_MCP_LOG_FILE": "test.log",
        "KALTURA_MCP_CONTEXT_STRATEGY": "pagination",
        "KALTURA_MCP_MAX_ENTRIES": "100",
        "KALTURA_MCP_MAX_CONTEXT_SIZE": "10000"
    }):
        config = _apply_env_overrides(config)
        
        # Check that environment variables override the original values
        assert config.kaltura.partner_id == 123
        assert config.kaltura.admin_secret == "test_secret"
        assert config.kaltura.user_id == "test_user"
        assert config.kaltura.service_url == "https://example.com"
        assert config.server.log_level == "DEBUG"
        assert config.logging.level == "DEBUG"
        assert config.server.transport == "stdio"
        assert config.server.port == 8000
        assert config.server.host == "0.0.0.0"
        assert config.server.debug is True
        assert config.logging.file == "test.log"
        assert config.context.default_strategy == "pagination"
        assert config.context.max_entries == 100
        assert config.context.max_context_size == 10000

def test_validate_config_valid():
    """Test validating a valid configuration."""
    from kaltura_mcp.config import Config, KalturaConfig, ServerConfig
    
    config = Config(
        kaltura=KalturaConfig(
            partner_id=123,
            admin_secret="test_secret",
            user_id="test_user",
            service_url="https://example.com"
        ),
        server=ServerConfig()
    )
    
    # Should not raise an exception
    _validate_config(config)

def test_validate_config_invalid_partner_id():
    """Test validating a configuration with invalid partner_id."""
    from kaltura_mcp.config import Config, KalturaConfig, ServerConfig
    
    config = Config(
        kaltura=KalturaConfig(
            partner_id=0,
            admin_secret="test_secret",
            user_id="test_user",
            service_url="https://example.com"
        ),
        server=ServerConfig()
    )
    
    with pytest.raises(ValueError, match="Invalid partner_id"):
        _validate_config(config)

def test_validate_config_missing_admin_secret():
    """Test validating a configuration with missing admin_secret."""
    from kaltura_mcp.config import Config, KalturaConfig, ServerConfig
    
    config = Config(
        kaltura=KalturaConfig(
            partner_id=123,
            admin_secret="",
            user_id="test_user",
            service_url="https://example.com"
        ),
        server=ServerConfig()
    )
    
    with pytest.raises(ValueError, match="Missing admin_secret"):
        _validate_config(config)