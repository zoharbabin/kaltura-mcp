"""
Kaltura client wrapper for the Kaltura MCP Server.
"""

import logging
import time
from typing import Any, Dict, Optional

from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.exceptions import KalturaClientException, KalturaException
from KalturaClient.Plugins.Core import KalturaSessionType

logger = logging.getLogger(__name__)


class KalturaClientWrapper:
    """Wrapper for the Kaltura client SDK."""

    def __init__(self, config: Any) -> None:
        """Initialize with configuration."""
        self.config = config
        self.client: Optional[KalturaClient] = None
        self.ks: Optional[str] = None
        self.ks_expiry = 0

    async def initialize(self) -> None:
        """Initialize the Kaltura client."""
        # Create client configuration
        client_config = KalturaConfiguration()
        client_config.serviceUrl = self.config.kaltura.service_url

        # Create client
        self.client = KalturaClient(client_config)

        # Generate initial KS
        await self.ensure_valid_ks()

        logger.info("Kaltura client initialized")

    async def ensure_valid_ks(self) -> str:
        """Ensure a valid Kaltura Session is available."""
        if self.ks and time.time() < self.ks_expiry:
            return self.ks

        # Generate new KS
        logger.info("Generating new Kaltura session")
        if self.client is not None:
            ks = self.client.generateSession(
                self.config.kaltura.admin_secret,
                self.config.kaltura.user_id,
                KalturaSessionType.ADMIN,
                self.config.kaltura.partner_id,
                86400,  # 24 hours
                "disableentitlement",
            )

            # Convert bytes to string if necessary
            if isinstance(ks, bytes):
                self.ks = ks.decode("utf-8")
            else:
                self.ks = ks

            # Set KS in client
            self.client.setKs(self.ks)

        # Set expiry time (slightly less than actual expiry to be safe)
        self.ks_expiry = int(time.time() + 86000)  # ~23.9 hours

        return self.ks or ""

    async def execute_request(self, service: str, action: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Execute a Kaltura API request."""
        # Ensure valid KS
        await self.ensure_valid_ks()

        # Initialize params if None
        if params is None:
            params = {}

        # Handle any additional keyword arguments
        params.update(kwargs)

        # Get service
        service_obj = getattr(self.client, service)
        if not service_obj:
            raise ValueError("Unknown service: " + service)

        # Get action
        action_func = getattr(service_obj, action)
        if not action_func:
            raise ValueError("Unknown action: " + action)

        # Execute request
        try:
            logger.debug("Executing Kaltura API request: " + service + "." + action)
            if params:
                return action_func(**params)
            else:
                return action_func()
        except (KalturaException, KalturaClientException) as e:
            # Translate Kaltura exceptions to MCP-friendly exceptions
            from kaltura_mcp.kaltura.errors import translate_kaltura_error

            logger.error(f"Kaltura API error: {e}")
            raise translate_kaltura_error(e) from e

    def get_service_url(self) -> str:
        """Get the Kaltura service URL."""
        return str(self.config.kaltura.service_url)

    def get_ks(self) -> str:
        """Get the current Kaltura Session ID."""
        return self.ks or ""

    async def list_media(self, page_size: int = 30, page: int = 1) -> Any:
        """List media entries."""
        await self.ensure_valid_ks()

        # Create a filter for listing media entries
        from KalturaClient.Plugins.Core import KalturaFilterPager, KalturaMediaEntryFilter

        # Create a proper filter object
        filter_params = KalturaMediaEntryFilter()
        filter_params.orderBy = "-createdAt"

        # Create a proper pager object
        pager_params = KalturaFilterPager()
        pager_params.pageSize = page_size
        pager_params.pageIndex = page

        result = await self.execute_request("media", "list", filter=filter_params, pager=pager_params)

        return result
