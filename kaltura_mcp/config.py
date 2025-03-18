"""
Configuration management for Kaltura MCP Server.
"""
import os
import yaml
from dataclasses import dataclass
from typing import Optional

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
    
@dataclass
class Config:
    """Main configuration class."""
    kaltura: KalturaConfig
    server: ServerConfig

def load_config() -> Config:
    """Load configuration from environment variables and config file."""
    # Try to load from config file
    config_file = os.environ.get("KALTURA_MCP_CONFIG", "config.yaml")
    config = None
    
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)
            config = _parse_config_data(config_data)
    
    # If no config file, try environment variables
    if config is None:
        config = _load_config_from_env()
    
    # Validate config
    _validate_config(config)
    
    return config

def _parse_config_data(data: dict) -> Config:
    """Parse configuration data from dictionary."""
    kaltura_config = KalturaConfig(
        partner_id=data.get("kaltura", {}).get("partner_id"),
        admin_secret=data.get("kaltura", {}).get("admin_secret"),
        user_id=data.get("kaltura", {}).get("user_id", "admin"),
        service_url=data.get("kaltura", {}).get("service_url", "https://www.kaltura.com"),
    )
    
    server_config = ServerConfig(
        log_level=data.get("server", {}).get("log_level", "INFO"),
        transport=data.get("server", {}).get("transport", "stdio"),
        port=data.get("server", {}).get("port", 8000),
    )
    
    return Config(kaltura=kaltura_config, server=server_config)

def _load_config_from_env() -> Config:
    """Load configuration from environment variables."""
    kaltura_config = KalturaConfig(
        partner_id=int(os.environ.get("KALTURA_PARTNER_ID", 0)),
        admin_secret=os.environ.get("KALTURA_ADMIN_SECRET", ""),
        user_id=os.environ.get("KALTURA_USER_ID", "admin"),
        service_url=os.environ.get("KALTURA_SERVICE_URL", "https://www.kaltura.com"),
    )
    
    server_config = ServerConfig(
        log_level=os.environ.get("KALTURA_MCP_LOG_LEVEL", "INFO"),
        transport=os.environ.get("KALTURA_MCP_TRANSPORT", "stdio"),
        port=int(os.environ.get("KALTURA_MCP_PORT", 8000)),
    )
    
    return Config(kaltura=kaltura_config, server=server_config)

def _validate_config(config: Config) -> None:
    """Validate configuration."""
    if config.kaltura.partner_id <= 0:
        raise ValueError("Invalid partner_id")
    
    if not config.kaltura.admin_secret:
        raise ValueError("Missing admin_secret")
    
    if not config.kaltura.service_url:
        raise ValueError("Missing service_url")