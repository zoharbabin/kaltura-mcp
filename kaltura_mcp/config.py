"""
Configuration management for Kaltura MCP Server.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import yaml


@dataclass
class KalturaConfig:
    """Kaltura API configuration."""

    partner_id: int
    admin_secret: str
    user_id: str
    service_url: str


@dataclass
class ServerConfig:
    """Server configuration."""

    log_level: str = "INFO"
    transport: str = "stdio"
    port: int = 8000
    host: str = "127.0.0.1"
    debug: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    file: Optional[str] = None


@dataclass
class ContextConfig:
    """Context management configuration."""

    default_strategy: str = "pagination"
    max_entries: int = 100
    max_context_size: int = 10000


@dataclass
class Config:
    """Main configuration class."""

    kaltura: KalturaConfig
    server: ServerConfig
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    context: ContextConfig = field(default_factory=ContextConfig)

    # Store the raw config data for access to custom fields
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    def get_custom_value(self, path: str, default: Any = None) -> Any:
        """Get a custom configuration value by dot-notation path."""
        parts = path.split(".")
        current = self._raw_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables and config file.

    Args:
        config_path: Optional path to the config file. If not provided,
                    will check KALTURA_MCP_CONFIG env var or default to config.yaml

    Returns:
        Config object with all configuration settings
    """
    # Determine config file path
    if config_path is None:
        config_path = os.environ.get("KALTURA_MCP_CONFIG", "config.yaml")

    config_data: Dict[str, Any] = {}

    # Load from config file if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                config_data = yaml.safe_load(f) or {}
            elif config_path.endswith(".json"):
                config_data = json.load(f)
            else:
                # Default to YAML for unknown extensions
                config_data = yaml.safe_load(f) or {}

    # Create config from file data
    config = _parse_config_data(config_data)

    # Apply environment variable overrides
    config = _apply_env_overrides(config)

    # Validate config
    _validate_config(config)

    return config


def _apply_env_overrides(config: Config) -> Config:
    """Apply environment variable overrides to the configuration."""
    # Override Kaltura config
    if "KALTURA_PARTNER_ID" in os.environ:
        config.kaltura.partner_id = int(os.environ["KALTURA_PARTNER_ID"])

    if "KALTURA_ADMIN_SECRET" in os.environ:
        config.kaltura.admin_secret = os.environ["KALTURA_ADMIN_SECRET"]

    if "KALTURA_USER_ID" in os.environ:
        config.kaltura.user_id = os.environ["KALTURA_USER_ID"]

    if "KALTURA_SERVICE_URL" in os.environ:
        config.kaltura.service_url = os.environ["KALTURA_SERVICE_URL"]

    # Override server config
    if "KALTURA_MCP_LOG_LEVEL" in os.environ:
        config.server.log_level = os.environ["KALTURA_MCP_LOG_LEVEL"]
        config.logging.level = os.environ["KALTURA_MCP_LOG_LEVEL"]

    if "KALTURA_MCP_TRANSPORT" in os.environ:
        config.server.transport = os.environ["KALTURA_MCP_TRANSPORT"]

    if "KALTURA_MCP_PORT" in os.environ:
        config.server.port = int(os.environ["KALTURA_MCP_PORT"])

    if "KALTURA_MCP_HOST" in os.environ:
        config.server.host = os.environ["KALTURA_MCP_HOST"]

    if "KALTURA_MCP_DEBUG" in os.environ:
        config.server.debug = os.environ["KALTURA_MCP_DEBUG"].lower() in ("true", "1", "yes")

    # Override logging config
    if "KALTURA_MCP_LOG_FILE" in os.environ:
        config.logging.file = os.environ["KALTURA_MCP_LOG_FILE"]

    # Override context config
    if "KALTURA_MCP_CONTEXT_STRATEGY" in os.environ:
        config.context.default_strategy = os.environ["KALTURA_MCP_CONTEXT_STRATEGY"]

    if "KALTURA_MCP_MAX_ENTRIES" in os.environ:
        config.context.max_entries = int(os.environ["KALTURA_MCP_MAX_ENTRIES"])

    if "KALTURA_MCP_MAX_CONTEXT_SIZE" in os.environ:
        config.context.max_context_size = int(os.environ["KALTURA_MCP_MAX_CONTEXT_SIZE"])

    return config


def _parse_config_data(data: dict) -> Config:
    """Parse configuration data from dictionary."""
    # Extract Kaltura config
    kaltura_config = KalturaConfig(
        partner_id=data.get("kaltura", {}).get("partner_id", 0),
        admin_secret=data.get("kaltura", {}).get("admin_secret", ""),
        user_id=data.get("kaltura", {}).get("user_id", "admin"),
        service_url=data.get("kaltura", {}).get("service_url", "https://www.kaltura.com/api_v3"),
    )

    # Extract server config
    server_data = data.get("server", {})
    server_config = ServerConfig(
        log_level=server_data.get("log_level", "INFO"),
        transport=server_data.get("transport", "stdio"),
        port=server_data.get("port", 8000),
        host=server_data.get("host", "127.0.0.1"),
        debug=server_data.get("debug", False),
    )

    # Extract logging config
    logging_data = data.get("logging", {})
    logging_config = LoggingConfig(
        level=logging_data.get("level", "INFO"),
        file=logging_data.get("file"),
    )

    # Extract context config
    context_data = data.get("context", {})
    context_config = ContextConfig(
        default_strategy=context_data.get("default_strategy", "pagination"),
        max_entries=context_data.get("max_entries", 100),
        max_context_size=context_data.get("max_context_size", 10000),
    )

    # Create the config object
    config = Config(
        kaltura=kaltura_config,
        server=server_config,
        logging=logging_config,
        context=context_config,
    )

    # Store the raw data for custom field access
    config._raw_data = data

    return config


def _validate_config(config: Config) -> None:
    """Validate configuration."""
    if config.kaltura.partner_id <= 0:
        raise ValueError("Invalid partner_id")

    if not config.kaltura.admin_secret:
        raise ValueError("Missing admin_secret")

    if not config.kaltura.service_url:
        raise ValueError("Missing service_url")
