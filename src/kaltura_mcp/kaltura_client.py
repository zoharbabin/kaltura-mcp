"""Kaltura API client management."""

import os
import time
import logging
from typing import Optional
from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.Plugins.Core import KalturaSessionType

logger = logging.getLogger(__name__)


class KalturaClientManager:
    """Manages Kaltura API client instances and sessions."""
    
    def __init__(self):
        self.service_url = os.getenv("KALTURA_SERVICE_URL", "https://www.kaltura.com")
        self.partner_id = int(os.getenv("KALTURA_PARTNER_ID", "0"))
        self.admin_secret = os.getenv("KALTURA_ADMIN_SECRET", "")
        self.user_id = os.getenv("KALTURA_USER_ID", "")
        self.session_expiry = int(os.getenv("KALTURA_SESSION_EXPIRY", "86400"))
        
        # Validate required credentials on initialization
        if not self.admin_secret:
            raise ValueError("KALTURA_ADMIN_SECRET environment variable is required")
        if not self.partner_id:
            raise ValueError("KALTURA_PARTNER_ID environment variable is required")
        
        self._client: Optional[KalturaClient] = None
        self._ks: Optional[str] = None
        self._session_start_time: Optional[float] = None
        self._session_buffer = 300  # Refresh session 5 minutes before expiry
    
    def _mask_credential(self, credential: str, show_chars: int = 4) -> str:
        """Mask sensitive credential for logging."""
        if not credential or len(credential) <= show_chars:
            return "***"
        return credential[:show_chars] + "***"
    
    def get_client(self) -> KalturaClient:
        """Get or create a Kaltura client with valid session."""
        if not self._client or not self._ks or self._is_session_expired():
            self._create_session()
        return self._client
    
    def _is_session_expired(self) -> bool:
        """Check if the current session is expired or close to expiry."""
        if not self._session_start_time:
            return True
        
        elapsed = time.time() - self._session_start_time
        return elapsed >= (self.session_expiry - self._session_buffer)
    
    def _create_session(self):
        """Create a new Kaltura session."""
        try:
            logger.info(f"Creating new Kaltura session for partner {self.partner_id} at {self.service_url}")
            
            config = KalturaConfiguration()
            config.serviceUrl = self.service_url
            # Add timeout settings for better error handling
            config.requestTimeout = 30
            
            self._client = KalturaClient(config)
            
            # Start a session (never log the actual secret)
            self._ks = self._client.session.start(
                self.admin_secret,
                self.user_id,
                KalturaSessionType.ADMIN,
                self.partner_id,
                self.session_expiry,
                "disableentitlement"
            )
            
            # Set the session for the client
            self._client.setKs(self._ks)
            self._session_start_time = time.time()
            
            logger.info(f"Kaltura session created successfully, expires in {self.session_expiry} seconds")
            
        except Exception as e:
            # Mask any credential information in error messages
            error_msg = str(e)
            if self.admin_secret and self.admin_secret in error_msg:
                error_msg = error_msg.replace(self.admin_secret, self._mask_credential(self.admin_secret))
            logger.error(f"Failed to create Kaltura session: {error_msg}")
            raise RuntimeError("Failed to create Kaltura session") from e
    
    def invalidate_session(self):
        """Invalidate the current session."""
        if self._client and self._ks:
            try:
                self._client.session.end()
                logger.info("Kaltura session ended successfully")
            except Exception as e:
                logger.warning(f"Failed to properly end Kaltura session: {e}")
        self._client = None
        self._ks = None
        self._session_start_time = None