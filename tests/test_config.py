"""Test our configuration validation logic only."""

import os
from unittest.mock import patch

import pytest

from kaltura_mcp.kaltura_client import KalturaClientManager


def test_our_config_validation_rules():
    """Test OUR validation rules for Kaltura configuration."""

    # Test valid config loads successfully
    with patch.dict(
        os.environ,
        {
            "KALTURA_SERVICE_URL": "https://test.kaltura.com",
            "KALTURA_PARTNER_ID": "12345",
            "KALTURA_ADMIN_SECRET": "test_secret_12345678",
            "KALTURA_USER_ID": "test@example.com",
            "KALTURA_SESSION_EXPIRY": "86400",
        },
    ):
        manager = KalturaClientManager()
        manager._load_config()
        assert manager.service_url == "https://test.kaltura.com"
        assert manager.partner_id == 12345
        assert manager.admin_secret == "test_secret_12345678"
        assert manager.user_id == "test@example.com"
        assert manager.session_expiry == 86400


def test_our_required_config_validation():
    """Test OUR validation that prevents startup failures."""

    # Test missing admin secret validation
    with patch.dict(
        os.environ,
        {
            "KALTURA_SERVICE_URL": "https://test.kaltura.com",
            "KALTURA_PARTNER_ID": "12345",
            "KALTURA_ADMIN_SECRET": "",  # Empty secret should fail
            "KALTURA_USER_ID": "test@example.com",
        },
    ):
        manager = KalturaClientManager()
        with pytest.raises(
            ValueError, match="KALTURA_ADMIN_SECRET environment variable is required"
        ):
            manager._load_config()

    # Test missing partner ID validation
    with patch.dict(
        os.environ,
        {
            "KALTURA_SERVICE_URL": "https://test.kaltura.com",
            "KALTURA_PARTNER_ID": "0",  # Zero partner ID should fail
            "KALTURA_ADMIN_SECRET": "test_secret_12345678",
            "KALTURA_USER_ID": "test@example.com",
        },
    ):
        manager = KalturaClientManager()
        with pytest.raises(ValueError, match="KALTURA_PARTNER_ID environment variable is required"):
            manager._load_config()


def test_our_config_defaults():
    """Test OUR default value handling."""

    # Test defaults when environment variables are missing
    with patch.dict(
        os.environ,
        {"KALTURA_ADMIN_SECRET": "test_secret_12345678", "KALTURA_PARTNER_ID": "12345"},
        clear=True,
    ):
        manager = KalturaClientManager()
        manager._load_config()

        # Our defaults
        assert manager.service_url == "https://www.kaltura.com"  # Our default
        assert manager.user_id == ""  # Our default
        assert manager.session_expiry == 86400  # Our default


def test_our_config_loading_once():
    """Test OUR lazy loading logic."""

    with patch.dict(
        os.environ, {"KALTURA_ADMIN_SECRET": "test_secret_12345678", "KALTURA_PARTNER_ID": "12345"}
    ):
        manager = KalturaClientManager()

        # Should not be loaded initially
        assert not manager._config_loaded

        # Should load on first call
        manager._load_config()
        assert manager._config_loaded

        # Should not reload on second call
        original_secret = manager.admin_secret
        manager._load_config()
        assert manager.admin_secret == original_secret


def test_our_credential_masking_logic():
    """Test OUR credential masking implementation."""

    manager = KalturaClientManager()

    # Test our masking logic
    assert manager._mask_credential("test_secret_12345678") == "test***"
    assert manager._mask_credential("short") == "shor***"  # 5 chars - shows first 4
    assert manager._mask_credential("") == "***"  # Empty credential
    assert manager._mask_credential("abc") == "***"  # Too short (3 chars <= 4)


def test_our_has_required_config():
    """Test OUR configuration validation without exceptions."""

    # Valid config should return True
    with patch.dict(
        os.environ, {"KALTURA_ADMIN_SECRET": "test_secret_12345678", "KALTURA_PARTNER_ID": "12345"}
    ):
        manager = KalturaClientManager()
        assert manager.has_required_config() is True

    # Missing config should return False (not raise exception)
    with patch.dict(os.environ, {}, clear=True):
        manager = KalturaClientManager()
        assert manager.has_required_config() is False
