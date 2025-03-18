"""
Tests for configuration management.
"""
import pytest
import os
from unittest.mock import patch, mock_open

from kaltura_mcp.config import load_config, _parse_config_data, _load_config_from_env, _validate_config

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

def test_load_config_from_env():
    """Test loading configuration from environment variables."""
    with patch.dict(os.environ, {
        "KALTURA_PARTNER_ID": "123",
        "KALTURA_ADMIN_SECRET": "test_secret",
        "KALTURA_USER_ID": "test_user",
        "KALTURA_SERVICE_URL": "https://example.com",
        "KALTURA_MCP_LOG_LEVEL": "DEBUG",
        "KALTURA_MCP_TRANSPORT": "stdio",
        "KALTURA_MCP_PORT": "8000"
    }):
        config = _load_config_from_env()
        
        assert config.kaltura.partner_id == 123
        assert config.kaltura.admin_secret == "test_secret"
        assert config.kaltura.user_id == "test_user"
        assert config.kaltura.service_url == "https://example.com"
        assert config.server.log_level == "DEBUG"
        assert config.server.transport == "stdio"
        assert config.server.port == 8000

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