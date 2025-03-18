"""
Tests for the unified configuration system.
"""

import os
import tempfile

from kaltura_mcp.config import (
    load_config,
)


class TestUnifiedConfig:
    """Test the unified configuration system."""

    def test_load_yaml_config(self):
        """Test loading configuration from a YAML file."""
        # Save original environment variables
        original_env = {}
        env_vars_to_clear = [
            "KALTURA_PARTNER_ID",
            "KALTURA_ADMIN_SECRET",
            "KALTURA_USER_ID",
            "KALTURA_SERVICE_URL",
            "KALTURA_MCP_LOG_LEVEL",
            "KALTURA_MCP_TRANSPORT",
            "KALTURA_MCP_PORT",
            "KALTURA_MCP_HOST",
            "KALTURA_MCP_DEBUG",
            "KALTURA_MCP_LOG_FILE",
            "KALTURA_MCP_CONTEXT_STRATEGY",
            "KALTURA_MCP_MAX_ENTRIES",
            "KALTURA_MCP_MAX_CONTEXT_SIZE",
        ]

        for var in env_vars_to_clear:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]

        try:
            with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp:
                temp.write(
                    """
                    kaltura:
                      partner_id: 12345
                      admin_secret: "test-secret"
                      user_id: "test-user"
                      service_url: "https://test.kaltura.com/api_v3"
                    server:
                      log_level: "DEBUG"
                      transport: "stdio"
                      port: 9000
                      host: "0.0.0.0"
                      debug: true
                    logging:
                      level: "DEBUG"
                      file: "test.log"
                    context:
                      default_strategy: "summarization"
                      max_entries: 50
                      max_context_size: 5000
                    """
                )
                temp.flush()

                config = load_config(temp.name)

                # Check Kaltura config
                assert config.kaltura.partner_id == 12345
                assert config.kaltura.admin_secret == "test-secret"
                assert config.kaltura.user_id == "test-user"
                assert config.kaltura.service_url == "https://test.kaltura.com/api_v3"
        finally:
            # Restore original environment variables
            for var, value in original_env.items():
                os.environ[var] = value

        # Check server config
        assert config.server.log_level == "DEBUG"
        assert config.server.transport == "stdio"
        assert config.server.port == 9000
        assert config.server.host == "0.0.0.0"
        assert config.server.debug is True

        # Check logging config
        assert config.logging.level == "DEBUG"
        assert config.logging.file == "test.log"

        # Check context config
        assert config.context.default_strategy == "summarization"
        assert config.context.max_entries == 50
        assert config.context.max_context_size == 5000

    def test_load_json_config(self):
        """Test loading configuration from a JSON file."""
        # Save original environment variables
        original_env = {}
        env_vars_to_clear = [
            "KALTURA_PARTNER_ID",
            "KALTURA_ADMIN_SECRET",
            "KALTURA_USER_ID",
            "KALTURA_SERVICE_URL",
            "KALTURA_MCP_LOG_LEVEL",
            "KALTURA_MCP_TRANSPORT",
            "KALTURA_MCP_PORT",
            "KALTURA_MCP_HOST",
            "KALTURA_MCP_DEBUG",
            "KALTURA_MCP_LOG_FILE",
            "KALTURA_MCP_CONTEXT_STRATEGY",
            "KALTURA_MCP_MAX_ENTRIES",
            "KALTURA_MCP_MAX_CONTEXT_SIZE",
        ]

        for var in env_vars_to_clear:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]

        try:
            with tempfile.NamedTemporaryFile(suffix=".json", mode="w+") as temp:
                temp.write(
                    """
                    {
                        "kaltura": {
                            "partner_id": 67890,
                            "admin_secret": "json-secret",
                            "user_id": "json-user",
                            "service_url": "https://json.kaltura.com/api_v3"
                        },
                        "server": {
                            "log_level": "WARNING",
                            "transport": "websocket",
                            "port": 8080,
                            "host": "localhost",
                            "debug": false
                        },
                        "logging": {
                            "level": "WARNING",
                            "file": "json.log"
                        },
                        "context": {
                            "default_strategy": "selective",
                            "max_entries": 200,
                            "max_context_size": 20000
                        }
                    }
                    """
                )
                temp.flush()

                config = load_config(temp.name)

                # Check Kaltura config
                assert config.kaltura.partner_id == 67890
                assert config.kaltura.admin_secret == "json-secret"
                assert config.kaltura.user_id == "json-user"
                assert config.kaltura.service_url == "https://json.kaltura.com/api_v3"
        finally:
            # Restore original environment variables
            for var, value in original_env.items():
                os.environ[var] = value

        # Check server config
        assert config.server.log_level == "WARNING"
        assert config.server.transport == "websocket"
        assert config.server.port == 8080
        assert config.server.host == "localhost"
        assert config.server.debug is False

        # Check logging config
        assert config.logging.level == "WARNING"
        assert config.logging.file == "json.log"

        # Check context config
        assert config.context.default_strategy == "selective"
        assert config.context.max_entries == 200
        assert config.context.max_context_size == 20000

    def test_env_var_override(self):
        """Test that environment variables override config file values."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp:
            temp.write(
                """
            kaltura:
              partner_id: 12345
              admin_secret: "test-secret"
              user_id: "test-user"
              service_url: "https://test.kaltura.com/api_v3"
            """
            )
            temp.flush()

            # Set environment variables
            os.environ["KALTURA_PARTNER_ID"] = "99999"
            os.environ["KALTURA_ADMIN_SECRET"] = "env-secret"
            os.environ["KALTURA_MCP_LOG_LEVEL"] = "ERROR"

            try:
                config = load_config(temp.name)

                # Check that env vars override file values
                assert config.kaltura.partner_id == 99999
                assert config.kaltura.admin_secret == "env-secret"
                assert config.server.log_level == "ERROR"

                # Check that file values are used when no env var
                assert config.kaltura.user_id == "test-user"
                assert config.kaltura.service_url == "https://test.kaltura.com/api_v3"
            finally:
                # Clean up environment variables
                del os.environ["KALTURA_PARTNER_ID"]
                del os.environ["KALTURA_ADMIN_SECRET"]
                del os.environ["KALTURA_MCP_LOG_LEVEL"]

    def test_custom_value_access(self):
        """Test accessing custom configuration values."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp:
            temp.write(
                """
            kaltura:
              partner_id: 12345
              admin_secret: "test-secret"
              user_id: "test-user"
              service_url: "https://test.kaltura.com/api_v3"
            custom:
              feature_flags:
                enable_advanced_upload: true
                max_file_size: 1073741824
              api_rate_limits:
                default: 100
                upload: 10
            """
            )
            temp.flush()

            config = load_config(temp.name)

            # Access custom values using get_custom_value
            assert config.get_custom_value("custom.feature_flags.enable_advanced_upload") is True
            assert config.get_custom_value("custom.feature_flags.max_file_size") == 1073741824
            assert config.get_custom_value("custom.api_rate_limits.default") == 100
            assert config.get_custom_value("custom.api_rate_limits.upload") == 10

            # Test default value for non-existent path
            assert config.get_custom_value("custom.non_existent", "default") == "default"
            assert config.get_custom_value("completely.invalid.path") is None
