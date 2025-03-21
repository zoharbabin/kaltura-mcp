"""
Base classes for Kaltura resource handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Pattern

import mcp.types as types


class KalturaResourceHandler(ABC):
    """Base class for Kaltura resource handlers."""

    def __init__(self, kaltura_client: Any) -> None:
        """Initialize with a Kaltura client."""
        self.kaltura_client = kaltura_client
        self._uri_pattern = self._compile_uri_pattern()

    @abstractmethod
    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a resource request for the given URI."""
        pass

    @abstractmethod
    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        pass

    @abstractmethod
    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        pass

    def matches_uri(self, uri: str) -> bool:
        """Check if this handler matches the given URI."""
        return bool(self._uri_pattern.match(uri))

    def extract_uri_params(self, uri: str) -> Dict[str, Any]:
        """Extract parameters from the URI."""
        match = self._uri_pattern.match(uri)
        if not match:
            return {}
        return match.groupdict()
