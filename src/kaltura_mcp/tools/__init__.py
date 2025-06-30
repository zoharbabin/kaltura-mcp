"""Kaltura MCP tools - elegant modular organization."""

# Import utilities
from .analytics import (
    get_analytics,
)
from .analytics_enhanced import (
    get_analytics_enhanced,
    get_geographic_analytics,
    get_qoe_analytics,
    get_realtime_analytics,
)
from .assets import (
    get_attachment_content,
    get_caption_content,
    list_attachment_assets,
    list_caption_assets,
)

# Import by domain for clear organization
from .media import (
    get_download_url,
    get_media_entry,
    get_thumbnail_url,
    list_media_entries,
)
from .search import (
    esearch_entries,
    list_categories,
    search_entries,
    search_entries_intelligent,
)
from .utils import (
    handle_kaltura_error,
    safe_serialize_kaltura_field,
    validate_entry_id,
)

# Export everything exactly as before - ZERO breaking changes
__all__ = [
    # Utilities
    "handle_kaltura_error",
    "safe_serialize_kaltura_field",
    "validate_entry_id",
    # Media operations
    "get_download_url",
    "get_media_entry",
    "get_thumbnail_url",
    "list_media_entries",
    # Analytics operations
    "get_analytics",
    "get_analytics_enhanced",
    "get_geographic_analytics",
    "get_qoe_analytics",
    "get_realtime_analytics",
    # Search operations
    "esearch_entries",
    "list_categories",
    "search_entries",
    "search_entries_intelligent",
    # Asset operations
    "get_attachment_content",
    "get_caption_content",
    "list_attachment_assets",
    "list_caption_assets",
]
