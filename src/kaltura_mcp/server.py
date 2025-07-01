#!/usr/bin/env python3
"""Kaltura MCP Server - Provides tools for managing Kaltura API operations."""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Load .env file from the MCP server directory
try:
    from dotenv import load_dotenv

    server_dir = Path(__file__).parent.parent.parent
    env_file = server_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from: {env_file}", file=sys.stderr)
    else:
        # Try loading from current working directory as fallback
        load_dotenv()
except ImportError:
    # dotenv not available, rely on system environment variables
    pass

from .kaltura_client import KalturaClientManager
from .tools import (
    get_analytics,
    get_analytics_timeseries,
    get_attachment_content,
    get_caption_content,
    get_download_url,
    get_geographic_breakdown,
    get_media_entry,
    get_quality_metrics,
    get_realtime_metrics,
    get_thumbnail_url,
    get_video_retention,
    get_video_timeline_analytics,
    list_analytics_capabilities,
    list_attachment_assets,
    list_caption_assets,
    list_categories,
    search_entries_intelligent,
)

server = Server("kaltura-mcp")
kaltura_manager = KalturaClientManager()


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available Kaltura API tools."""
    return [
        types.Tool(
            name="get_media_entry",
            description="Get detailed information about a specific media entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The Kaltura media entry ID"},
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="list_categories",
            description="List and search content categories",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "Filter categories by name or description",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of categories to return (default: 20)",
                    },
                },
            },
        ),
        types.Tool(
            name="get_analytics",
            description="Get comprehensive analytics data for detailed reporting and analysis. Use this for performance metrics, rankings, comparisons, and exporting tabular data. Supports 60+ report types.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Report type (default: 'content'). Options: content, user_engagement, geographic, platforms, bandwidth, etc. See list_analytics_capabilities for full list.",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Optional media entry ID for content-specific reports",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Optional user ID for user-specific reports",
                    },
                    "categories": {
                        "type": "string",
                        "description": "Optional category filter",
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Optional dimension for grouping (e.g., 'device', 'country')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results per page (default: 50)",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="get_analytics_timeseries",
            description="Get time-series analytics data optimized for charts and visualizations. Use this when creating graphs, dashboards, or tracking trends over time.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Report type (default: 'content')",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Metrics to include (e.g., ['plays', 'views'])",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Optional specific entry ID",
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["hours", "days", "weeks", "months"],
                        "description": "Time interval (default: 'days')",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="get_video_retention",
            description="Analyze viewer retention throughout a video with 101-point granularity. Shows where viewers drop off, replay segments, and completion rates. Essential for content optimization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video entry ID (required)",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date (optional, defaults to 30 days ago)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (optional, defaults to today)",
                    },
                    "user_filter": {
                        "type": "string",
                        "description": "Filter by: 'anonymous', 'registered', email, or 'cohort:name'",
                    },
                    "compare_segments": {
                        "type": "boolean",
                        "description": "Compare filtered segment vs all viewers",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_realtime_metrics",
            description="Get real-time analytics updated every ~30 seconds. Perfect for live monitoring, dashboards, and immediate feedback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["viewers", "geographic", "quality"],
                        "description": "Type of real-time data (default: 'viewers')",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Optional entry ID for content-specific metrics",
                    },
                },
            },
        ),
        types.Tool(
            name="get_quality_metrics",
            description="Get Quality of Experience (QoE) metrics for streaming performance. Analyzes buffering, bitrate, errors, and user experience quality.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "metric_type": {
                        "type": "string",
                        "enum": ["overview", "experience", "engagement", "stream", "errors"],
                        "description": "Type of quality metric (default: 'overview')",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Optional entry ID for content-specific analysis",
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Optional dimension (e.g., 'device', 'geography')",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="get_geographic_breakdown",
            description="Get analytics broken down by geographic location. Analyze global reach, market penetration, and regional content performance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "granularity": {
                        "type": "string",
                        "enum": ["world", "country", "region", "city"],
                        "description": "Geographic detail level (default: 'country')",
                    },
                    "region_filter": {
                        "type": "string",
                        "description": "Filter for specific region (e.g., 'US' for states)",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Metrics to include",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="list_analytics_capabilities",
            description="List all available analytics functions and their use cases. Helper to discover analytics capabilities.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_video_timeline_analytics",
            description="[DEPRECATED - Use get_video_retention instead] Legacy function for video timeline analytics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Single video entry ID (required)",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)",
                    },
                    "user_ids": {
                        "type": "string",
                        "description": "User filter",
                    },
                    "compare_cohorts": {
                        "type": "boolean",
                        "description": "Compare cohorts",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_download_url",
            description="Get direct download URL for media files",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The media entry ID"},
                    "flavor_id": {
                        "type": "string",
                        "description": "Optional specific flavor ID for quality/format selection",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_thumbnail_url",
            description="Get video thumbnail/preview image URL with custom dimensions",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The media entry ID"},
                    "width": {
                        "type": "integer",
                        "description": "Thumbnail width in pixels (default: 120)",
                    },
                    "height": {
                        "type": "integer",
                        "description": "Thumbnail height in pixels (default: 90)",
                    },
                    "second": {
                        "type": "integer",
                        "description": "Video timestamp in seconds to capture (default: 5)",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="search_entries",
            description="Search and discover media entries with intelligent sorting and filtering. Supports content search across titles, descriptions, captions, and metadata. IMPORTANT: To find the latest/newest videos, use query='*' with sort_field='created_at' and sort_order='desc'. This will list all entries sorted by creation date.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query. Use '*' to list all entries (essential for finding latest/newest content), use keywords to search for specific content, or exact phrases in quotes.",
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["unified", "entry", "caption", "metadata", "cuepoint"],
                        "description": "Search scope: 'unified' (all fields), 'entry' (titles/descriptions), 'caption' (transcripts), 'metadata' (custom fields), 'cuepoint' (chapters). Default: 'unified'",
                    },
                    "match_type": {
                        "type": "string",
                        "enum": ["partial", "exact_match", "starts_with", "exists", "range"],
                        "description": "Match type: 'partial' (contains), 'exact_match' (exact phrase), 'starts_with' (prefix), 'exists' (has value), 'range' (numeric/date). Default: 'partial'",
                    },
                    "specific_field": {
                        "type": "string",
                        "description": "Specific field to search within the selected scope. Common fields: 'name', 'description', 'tags', 'created_at'. Leave blank to search all fields.",
                    },
                    "boolean_operator": {
                        "type": "string",
                        "enum": ["and", "or", "not"],
                        "description": "Boolean operator for multi-term queries: 'and' (all terms), 'or' (any term), 'not' (exclude). Default: 'and'",
                    },
                    "include_highlights": {
                        "type": "boolean",
                        "description": "Include highlighted matching text snippets in results. Default: true",
                    },
                    "custom_metadata": {
                        "type": "object",
                        "properties": {
                            "profile_id": {
                                "type": "integer",
                                "description": "Custom metadata profile ID",
                            },
                            "xpath": {
                                "type": "string",
                                "description": "XPath to specific metadata field",
                            },
                        },
                        "description": "Custom metadata search parameters. Requires both profile_id and xpath. Used for searching custom metadata fields.",
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "after": {
                                "type": "string",
                                "description": "Created after this date (YYYY-MM-DD format)",
                            },
                            "before": {
                                "type": "string",
                                "description": "Created before this date (YYYY-MM-DD format)",
                            },
                        },
                        "description": "Filter entries by creation date range. Use YYYY-MM-DD format.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20, max: 100)",
                    },
                    "sort_field": {
                        "type": "string",
                        "enum": [
                            "created_at",
                            "updated_at",
                            "name",
                            "views",
                            "plays",
                            "last_played_at",
                            "rank",
                            "start_date",
                            "end_date",
                        ],
                        "description": "Field to sort by. Options: 'created_at' (creation date), 'updated_at' (last modified), 'name' (alphabetical), 'views' (view count), 'plays' (play count), 'last_played_at' (recent activity), 'rank' (relevance), 'start_date' (schedule start), 'end_date' (schedule end). Default: 'created_at'",
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["desc", "asc"],
                        "description": "Sort direction. Use 'desc' for newest/highest first (default), 'asc' for oldest/lowest first. For finding latest content, use 'desc' with 'created_at'",
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_caption_assets",
            description="List available captions and subtitles for a media entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The media entry ID"},
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_caption_content",
            description="Get caption/subtitle content and download URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "caption_asset_id": {"type": "string", "description": "The caption asset ID"},
                },
                "required": ["caption_asset_id"],
            },
        ),
        types.Tool(
            name="list_attachment_assets",
            description="List attachment assets for a media entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The media entry ID"},
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_attachment_content",
            description="Get attachment content details and download URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "attachment_asset_id": {
                        "type": "string",
                        "description": "The attachment asset ID",
                    },
                },
                "required": ["attachment_asset_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute a Kaltura API tool."""
    try:
        if name == "get_media_entry":
            result = await get_media_entry(kaltura_manager, **arguments)
        elif name == "list_categories":
            result = await list_categories(kaltura_manager, **arguments)
        elif name == "get_analytics":
            result = await get_analytics(kaltura_manager, **arguments)
        elif name == "get_analytics_timeseries":
            result = await get_analytics_timeseries(kaltura_manager, **arguments)
        elif name == "get_video_retention":
            result = await get_video_retention(kaltura_manager, **arguments)
        elif name == "get_realtime_metrics":
            result = await get_realtime_metrics(kaltura_manager, **arguments)
        elif name == "get_quality_metrics":
            result = await get_quality_metrics(kaltura_manager, **arguments)
        elif name == "get_geographic_breakdown":
            result = await get_geographic_breakdown(kaltura_manager, **arguments)
        elif name == "list_analytics_capabilities":
            result = await list_analytics_capabilities(kaltura_manager, **arguments)
        elif name == "get_video_timeline_analytics":
            result = await get_video_timeline_analytics(kaltura_manager, **arguments)
        elif name == "get_download_url":
            result = await get_download_url(kaltura_manager, **arguments)
        elif name == "get_thumbnail_url":
            result = await get_thumbnail_url(kaltura_manager, **arguments)
        elif name == "search_entries":
            result = await search_entries_intelligent(kaltura_manager, **arguments)
        elif name == "list_caption_assets":
            result = await list_caption_assets(kaltura_manager, **arguments)
        elif name == "get_caption_content":
            result = await get_caption_content(kaltura_manager, **arguments)
        elif name == "list_attachment_assets":
            result = await list_attachment_assets(kaltura_manager, **arguments)
        elif name == "get_attachment_content":
            result = await get_attachment_content(kaltura_manager, **arguments)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def async_main():
    """Run the Kaltura MCP server."""
    try:
        async with stdio_server() as (read_stream, write_stream):
            # Run the server with initialization options
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)


def main():
    """Entry point for the CLI script."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
