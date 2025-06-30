"""Minimal pytest fixtures for testing our business logic."""

import pytest


@pytest.fixture
def valid_config_data():
    """Valid configuration data for testing our validation."""
    return {
        "partner_id": 12345,
        "service_url": "https://test.kaltura.com",
        "admin_secret": "test_secret_12345678",
        "user_id": "test@example.com",
        "session_expiry": 86400,
    }
