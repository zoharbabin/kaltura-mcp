# Configuration Management System - SIMPLE (2 hours)

**Complexity**: Medium  
**Impact**: High - Centralizes configuration and improves maintainability  
**Time Estimate**: 2 hours  
**Dependencies**: Development tooling setup

## Problem
Configuration is scattered across different files and lacks proper validation, type safety, and centralized management.

## Solution
Create a comprehensive configuration management system using dataclasses with validation, environment loading, and flexible configuration sources.

## Implementation Steps

### 1. Create Configuration Module (45 minutes)
**File: `src/kaltura_mcp/config.py`**
```python
"""Configuration management for Kaltura MCP server."""

import os
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class KalturaConfig:
    """Configuration for Kaltura API access."""
    
    service_url: str = field(default="https://cdnapisec.kaltura.com")
    partner_id: int = field(default=0)
    admin_secret: str = field(default="")
    user_id: str = field(default="")
    session_expiry: int = field(default=86400)  # 24 hours
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    @classmethod
    def from_env(cls) -> 'KalturaConfig':
        """Create configuration from environment variables."""
        return cls(
            service_url=os.getenv('KALTURA_SERVICE_URL', cls.service_url),
            partner_id=int(os.getenv('KALTURA_PARTNER_ID', '0')),
            admin_secret=os.getenv('KALTURA_ADMIN_SECRET', ''),
            user_id=os.getenv('KALTURA_USER_ID', ''),
            session_expiry=int(os.getenv('KALTURA_SESSION_EXPIRY', '86400'))
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KalturaConfig':
        """Create configuration from dictionary."""
        # Filter only known fields to avoid TypeError
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)
    
    @classmethod
    def from_file(cls, path: Union[str, Path]) -> 'KalturaConfig':
        """Load configuration from JSON file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def validate(self) -> None:
        """Validate configuration values."""
        errors = []
        
        # Service URL validation
        if not self.service_url:
            errors.append("service_url is required")
        elif not self.service_url.startswith(('http://', 'https://')):
            errors.append("service_url must start with http:// or https://")
        else:
            # Additional URL validation
            try:
                parsed = urlparse(self.service_url)
                if not parsed.netloc:
                    errors.append("service_url must be a valid URL")
            except Exception:
                errors.append("service_url must be a valid URL")
        
        # Partner ID validation
        if self.partner_id <= 0:
            errors.append("partner_id must be a positive integer")
        
        # Admin secret validation
        if not self.admin_secret:
            errors.append("admin_secret is required")
        elif len(self.admin_secret) < 8:
            errors.append("admin_secret must be at least 8 characters")
        
        # User ID validation
        if not self.user_id:
            errors.append("user_id is required")
        
        # Session expiry validation
        if self.session_expiry < 300:  # Minimum 5 minutes
            errors.append("session_expiry must be at least 300 seconds (5 minutes)")
        elif self.session_expiry > 604800:  # Maximum 7 days
            errors.append("session_expiry cannot exceed 604800 seconds (7 days)")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'service_url': self.service_url,
            'partner_id': self.partner_id,
            'admin_secret': self.admin_secret,
            'user_id': self.user_id,
            'session_expiry': self.session_expiry
        }
    
    def mask_secrets(self) -> Dict[str, Any]:
        """Return configuration with masked secrets for logging."""
        data = self.to_dict()
        if data['admin_secret']:
            # Show first 4 characters and mask the rest
            secret = data['admin_secret']
            data['admin_secret'] = secret[:4] + '*' * (len(secret) - 4)
        return data
    
    def save_to_file(self, path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"Configuration saved to {path}")


@dataclass
class ServerConfig:
    """Configuration for the MCP remote server."""
    
    jwt_secret_key: str = field(default="")
    oauth_redirect_uri: str = field(default="http://localhost:8000/oauth/callback")
    oauth_client_id: str = field(default="kaltura-mcp")
    oauth_client_secret: str = field(default="")
    server_host: str = field(default="0.0.0.0")
    server_port: int = field(default=8000)
    server_reload: bool = field(default=False)
    cors_origins: list = field(default_factory=lambda: ["*"])
    log_level: str = field(default="INFO")
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Create server configuration from environment variables."""
        cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
        if cors_origins == ['*']:
            cors_origins = ["*"]
        else:
            cors_origins = [origin.strip() for origin in cors_origins]
        
        return cls(
            jwt_secret_key=os.getenv('JWT_SECRET_KEY', ''),
            oauth_redirect_uri=os.getenv('OAUTH_REDIRECT_URI', cls.oauth_redirect_uri),
            oauth_client_id=os.getenv('OAUTH_CLIENT_ID', cls.oauth_client_id),
            oauth_client_secret=os.getenv('OAUTH_CLIENT_SECRET', ''),
            server_host=os.getenv('SERVER_HOST', cls.server_host),
            server_port=int(os.getenv('SERVER_PORT', '8000')),
            server_reload=os.getenv('SERVER_RELOAD', 'false').lower() == 'true',
            cors_origins=cors_origins,
            log_level=os.getenv('LOG_LEVEL', cls.log_level).upper()
        )
    
    def validate(self) -> None:
        """Validate server configuration."""
        errors = []
        
        # JWT secret validation
        if not self.jwt_secret_key:
            errors.append("jwt_secret_key is required for remote server")
        elif len(self.jwt_secret_key) < 32:
            errors.append("jwt_secret_key must be at least 32 characters for security")
        
        # Port validation
        if not (1 <= self.server_port <= 65535):
            errors.append("server_port must be between 1 and 65535")
        
        # Host validation
        if not self.server_host:
            errors.append("server_host cannot be empty")
        
        # OAuth redirect URI validation
        if self.oauth_redirect_uri and not self.oauth_redirect_uri.startswith(('http://', 'https://')):
            errors.append("oauth_redirect_uri must be a valid URL")
        
        # Log level validation
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            errors.append(f"log_level must be one of: {', '.join(valid_log_levels)}")
        
        if errors:
            raise ValueError(f"Server configuration validation failed: {'; '.join(errors)}")
    
    def mask_secrets(self) -> Dict[str, Any]:
        """Return configuration with masked secrets."""
        data = {
            'jwt_secret_key': self._mask_secret(self.jwt_secret_key),
            'oauth_redirect_uri': self.oauth_redirect_uri,
            'oauth_client_id': self.oauth_client_id,
            'oauth_client_secret': self._mask_secret(self.oauth_client_secret),
            'server_host': self.server_host,
            'server_port': self.server_port,
            'server_reload': self.server_reload,
            'cors_origins': self.cors_origins,
            'log_level': self.log_level
        }
        return data
    
    def _mask_secret(self, secret: str) -> str:
        """Mask a secret value for logging."""
        if not secret:
            return ""
        if len(secret) <= 8:
            return "*" * len(secret)
        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]


@dataclass
class AppConfig:
    """Combined application configuration."""
    
    kaltura: KalturaConfig = field(default_factory=KalturaConfig)
    server: Optional[ServerConfig] = field(default=None)
    debug: bool = field(default=False)
    
    @classmethod
    def from_env(cls, include_server: bool = False) -> 'AppConfig':
        """Create application configuration from environment variables."""
        kaltura_config = KalturaConfig.from_env()
        server_config = ServerConfig.from_env() if include_server else None
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        return cls(
            kaltura=kaltura_config,
            server=server_config,
            debug=debug
        )
    
    @classmethod
    def from_file(cls, path: Union[str, Path]) -> 'AppConfig':
        """Load configuration from JSON file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        
        kaltura_config = KalturaConfig.from_dict(data.get('kaltura', {}))
        server_data = data.get('server')
        server_config = ServerConfig(**server_data) if server_data else None
        debug = data.get('debug', False)
        
        return cls(
            kaltura=kaltura_config,
            server=server_config,
            debug=debug
        )
    
    def validate(self) -> None:
        """Validate all configurations."""
        self.kaltura.validate()
        if self.server:
            self.server.validate()
    
    def setup_logging(self) -> None:
        """Configure logging based on configuration."""
        log_level = logging.DEBUG if self.debug else logging.INFO
        if self.server:
            log_level = getattr(logging, self.server.log_level)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set specific loggers
        logging.getLogger('kaltura_mcp').setLevel(log_level)
        
        if self.debug:
            logging.getLogger('uvicorn').setLevel(logging.DEBUG)
        else:
            logging.getLogger('uvicorn.access').setLevel(logging.WARNING)


def load_config(config_path: Optional[Union[str, Path]] = None, 
                include_server: bool = False) -> AppConfig:
    """
    Load configuration from file or environment variables.
    
    Args:
        config_path: Path to configuration file (optional)
        include_server: Whether to include server configuration
    
    Returns:
        AppConfig instance
    """
    if config_path:
        config = AppConfig.from_file(config_path)
        logger.info(f"Configuration loaded from file: {config_path}")
    else:
        config = AppConfig.from_env(include_server=include_server)
        logger.info("Configuration loaded from environment variables")
    
    # Validate configuration
    config.validate()
    
    # Setup logging
    config.setup_logging()
    
    # Log masked configuration for debugging
    if config.debug:
        logger.debug(f"Kaltura config: {config.kaltura.mask_secrets()}")
        if config.server:
            logger.debug(f"Server config: {config.server.mask_secrets()}")
    
    return config
```

### 2. Update kaltura_client.py to Use Configuration (30 minutes)
**File: `src/kaltura_mcp/kaltura_client.py` (updated sections)**
```python
"""Kaltura API client management with configuration support."""

import os
import time
import logging
from typing import Optional

from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.Plugins.Core import KalturaSessionType

from .config import KalturaConfig

logger = logging.getLogger(__name__)


class KalturaClientManager:
    """Manages Kaltura API client instances and sessions with configuration support."""
    
    def __init__(self, config: Optional[KalturaConfig] = None):
        """
        Initialize the Kaltura client manager.
        
        Args:
            config: KalturaConfig instance. If None, loads from environment.
        """
        self.config = config or KalturaConfig.from_env()
        self._client: Optional[KalturaClient] = None
        self._ks: Optional[str] = None
        self._session_start_time: Optional[float] = None
        self._session_buffer = 300  # Refresh session 5 minutes before expiry
        
        logger.info(f"Initialized KalturaClientManager for partner {self.config.partner_id}")
    
    def has_required_config(self) -> bool:
        """Check if required configuration is available."""
        try:
            self.config.validate()
            return True
        except ValueError as e:
            logger.warning(f"Configuration validation failed: {e}")
            return False
    
    def get_client(self) -> KalturaClient:
        """Get or create a Kaltura client with valid session."""
        if not self._client or not self._ks or self._is_session_expired():
            self._create_session()
        return self._client
    
    def _is_session_expired(self) -> bool:
        """Check if the current session is expired or about to expire."""
        if not self._session_start_time:
            return True
        
        elapsed = time.time() - self._session_start_time
        return elapsed >= (self.config.session_expiry - self._session_buffer)
    
    def _create_session(self):
        """Create a new Kaltura session using configuration."""
        try:
            logger.info(f"Creating new Kaltura session for partner {self.config.partner_id}")
            
            # Create Kaltura configuration
            kaltura_config = KalturaConfiguration()
            kaltura_config.serviceUrl = self.config.service_url
            kaltura_config.partnerId = self.config.partner_id
            
            # Create client
            self._client = KalturaClient(kaltura_config)
            
            # Generate admin session
            self._ks = self._client.session.start(
                self.config.admin_secret,
                self.config.user_id,
                KalturaSessionType.ADMIN,
                self.config.partner_id,
                self.config.session_expiry
            )
            
            # Set the session on the client
            self._client.setKs(self._ks)
            self._session_start_time = time.time()
            
            logger.info("Kaltura session created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create Kaltura session: {e}")
            self._client = None
            self._ks = None
            self._session_start_time = None
            raise
    
    def invalidate_session(self):
        """Invalidate the current session."""
        logger.info("Invalidating Kaltura session")
        self._ks = None
        self._session_start_time = None
        if self._client:
            self._client.setKs(None)
    
    def get_session_info(self) -> dict:
        """Get information about the current session."""
        if not self._session_start_time:
            return {"status": "no_session"}
        
        elapsed = time.time() - self._session_start_time
        remaining = self.config.session_expiry - elapsed
        
        return {
            "status": "active" if not self._is_session_expired() else "expired",
            "partner_id": self.config.partner_id,
            "user_id": self.config.user_id,
            "elapsed_seconds": int(elapsed),
            "remaining_seconds": int(remaining),
            "expires_soon": remaining <= self._session_buffer
        }
```

### 3. Update Server Files to Use Configuration (30 minutes)
**File: `src/kaltura_mcp/server.py` (updated sections)**
```python
"""Local MCP server with configuration support."""

import logging
import sys
import asyncio
import traceback
from typing import Any, Dict, List

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import load_config
from .kaltura_client import KalturaClientManager
# ... other imports

logger = logging.getLogger(__name__)

# Global configuration and manager
config = None
kaltura_manager = None


def initialize_server():
    """Initialize server with configuration."""
    global config, kaltura_manager
    
    try:
        # Load configuration from environment
        config = load_config(include_server=False)
        logger.info("Configuration loaded successfully")
        
        # Initialize Kaltura client manager
        kaltura_manager = KalturaClientManager(config.kaltura)
        
        # Validate configuration
        if not kaltura_manager.has_required_config():
            logger.error("Invalid Kaltura configuration")
            sys.exit(1)
        
        logger.info("Server initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        if config and config.debug:
            traceback.print_exc()
        sys.exit(1)


async def async_main():
    """Run the Kaltura MCP server."""
    # Initialize server
    initialize_server()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        if config and config.debug:
            traceback.print_exc()


def main():
    """Entry point for the CLI script."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
```

### 4. Create Configuration Utilities (15 minutes)
**File: `src/kaltura_mcp/config_utils.py`**
```python
"""Configuration utilities and helpers."""

import os
import secrets
from pathlib import Path
from typing import Optional

from .config import KalturaConfig, ServerConfig, AppConfig


def generate_jwt_secret() -> str:
    """Generate a secure JWT secret key."""
    return secrets.token_urlsafe(32)


def create_sample_config(output_path: Optional[Path] = None) -> Path:
    """Create a sample configuration file."""
    sample_config = {
        "kaltura": {
            "service_url": "https://cdnapisec.kaltura.com",
            "partner_id": 12345,
            "admin_secret": "your-admin-secret-here",
            "user_id": "your-email@example.com",
            "session_expiry": 86400
        },
        "server": {
            "jwt_secret_key": generate_jwt_secret(),
            "oauth_redirect_uri": "http://localhost:8000/oauth/callback",
            "server_host": "0.0.0.0",
            "server_port": 8000,
            "server_reload": False,
            "cors_origins": ["*"],
            "log_level": "INFO"
        },
        "debug": False
    }
    
    if output_path is None:
        output_path = Path("config.sample.json")
    
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    return output_path


def validate_env_config() -> bool:
    """Validate that environment variables are properly set."""
    try:
        config = AppConfig.from_env(include_server=True)
        config.validate()
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


def check_config_completeness() -> dict:
    """Check which configuration values are missing."""
    required_kaltura = ['KALTURA_SERVICE_URL', 'KALTURA_PARTNER_ID', 
                       'KALTURA_ADMIN_SECRET', 'KALTURA_USER_ID']
    required_server = ['JWT_SECRET_KEY']
    
    missing_kaltura = [var for var in required_kaltura if not os.getenv(var)]
    missing_server = [var for var in required_server if not os.getenv(var)]
    
    return {
        'missing_kaltura': missing_kaltura,
        'missing_server': missing_server,
        'all_present': not missing_kaltura and not missing_server
    }


if __name__ == "__main__":
    # CLI utility for configuration management
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            if validate_env_config():
                print("✅ Configuration is valid")
                sys.exit(0)
            else:
                print("❌ Configuration is invalid")
                sys.exit(1)
        
        elif command == "check":
            status = check_config_completeness()
            if status['all_present']:
                print("✅ All required configuration present")
            else:
                if status['missing_kaltura']:
                    print(f"❌ Missing Kaltura config: {', '.join(status['missing_kaltura'])}")
                if status['missing_server']:
                    print(f"❌ Missing server config: {', '.join(status['missing_server'])}")
        
        elif command == "sample":
            output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
            created_path = create_sample_config(output_path)
            print(f"✅ Sample configuration created: {created_path}")
        
        elif command == "secret":
            print(f"Generated JWT secret: {generate_jwt_secret()}")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: validate, check, sample, secret")
            sys.exit(1)
    else:
        print("Usage: python -m kaltura_mcp.config_utils <command>")
        print("Commands:")
        print("  validate - Validate current environment configuration")
        print("  check    - Check which configuration values are missing")
        print("  sample   - Create a sample configuration file")
        print("  secret   - Generate a JWT secret key")
```

## Testing the Configuration System

### 1. Create Test Configuration (10 minutes)
```bash
# Create sample configuration
python -m kaltura_mcp.config_utils sample config.sample.json

# Check current environment
python -m kaltura_mcp.config_utils check

# Generate JWT secret
python -m kaltura_mcp.config_utils secret
```

### 2. Test Environment Loading
```python
# Test script
from kaltura_mcp.config import load_config

# Test environment loading
config = load_config(include_server=True)
print("Configuration loaded successfully!")
print(f"Partner ID: {config.kaltura.partner_id}")
print(f"Server port: {config.server.server_port if config.server else 'Not configured'}")
```

### 3. Test Validation
```python
from kaltura_mcp.config import KalturaConfig

# Test validation
try:
    config = KalturaConfig(
        service_url="invalid-url",
        partner_id=0,
        admin_secret="short",
        user_id="",
        session_expiry=100
    )
except ValueError as e:
    print(f"Validation works: {e}")
```

## Benefits
- ✅ Centralized configuration management
- ✅ Type-safe configuration with validation
- ✅ Support for multiple configuration sources
- ✅ Proper secret masking for logging
- ✅ Environment variable support
- ✅ File-based configuration support
- ✅ Comprehensive validation
- ✅ Development utilities

## Files Created
- `src/kaltura_mcp/config.py`
- `src/kaltura_mcp/config_utils.py`

## Files Modified
- `src/kaltura_mcp/kaltura_client.py`
- `src/kaltura_mcp/server.py`

## Next Steps
1. Update `remote_server.py` to use the new configuration system
2. Add configuration tests
3. Update documentation with configuration examples
4. Consider adding configuration file encryption for production