"""Kaltura MCP tools - elegant modular organization."""

# Import utilities
from .analytics import (
    get_analytics,
    get_analytics_timeseries,
    get_geographic_breakdown,
    get_quality_metrics,
    get_realtime_metrics,
    get_video_retention,
    list_analytics_capabilities,
)
from .analytics_core import (
    get_analytics_enhanced,
    get_analytics_graph,
    get_geographic_analytics,
    get_qoe_analytics,
    get_realtime_analytics,
    get_video_timeline_analytics,
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
    # Analytics operations - purpose-based naming
    "get_analytics",
    "get_analytics_timeseries",
    "get_video_retention",
    "get_realtime_metrics",
    "get_quality_metrics",
    "get_geographic_breakdown",
    "list_analytics_capabilities",
    # Analytics operations - core/enhanced (kept for compatibility)
    "get_analytics_enhanced",
    "get_analytics_graph",
    "get_geographic_analytics",
    "get_qoe_analytics",
    "get_realtime_analytics",
    "get_video_timeline_analytics",
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
