#!/usr/bin/env python3
"""Kaltura MCP Server - Provides tools for managing Kaltura API operations."""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from .prompts import prompts_manager
from .resources import resources_manager
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
    """List all available Kaltura API tools.

    Tools are organized by function:
    - MEDIA: get_media_entry, search_entries, get_download_url, get_thumbnail_url
    - ANALYTICS: get_analytics, get_analytics_timeseries, get_video_retention, get_realtime_metrics,
                 get_quality_metrics, get_geographic_breakdown, list_analytics_capabilities
    - CAPTIONS: list_caption_assets, get_caption_content
    - ATTACHMENTS: list_attachment_assets, get_attachment_content
    - ORGANIZATION: list_categories

    Each tool description includes:
    - USE WHEN: Specific scenarios for using this tool
    - RETURNS: What data you'll get back
    - EXAMPLES: Concrete usage examples
    """
    return [
        types.Tool(
            name="get_media_entry",
            description="Get complete metadata for a single video/media file. USE WHEN: You have a specific entry_id and need full details (title, description, duration, tags, thumbnail, status). RETURNS: Complete media metadata including URLs, dimensions, creation date. EXAMPLE: After search finds entry_id='1_abc123', use this to get full video details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "The media entry ID (format: '1_abc123' or '0_xyz789')",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="list_categories",
            description="Browse content organization hierarchy. USE WHEN: Exploring content structure, finding category IDs for filtering, understanding content taxonomy. Categories organize videos into folders/topics. RETURNS: Tree structure with category names, IDs, parent-child relationships. EXAMPLE: Find all videos in 'Training' category by first getting category ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "Optional text to filter categories (e.g., 'training', 'marketing')",
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
            description="Get detailed analytics in TABLE format for reporting. USE WHEN: Creating reports, comparing metrics, ranking content, analyzing performance, exporting data. RETURNS: Structured data with headers/rows. EXAMPLES: 'Show top 10 videos by views', 'Compare user engagement by category', 'Export monthly performance report'. Use list_analytics_capabilities to see all 60+ report types. For charts/graphs, use get_analytics_timeseries instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (e.g., '2024-01-01')",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., '2024-01-31')",
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of analytics report (default: 'content'). Common options: 'content' (video performance), 'user_engagement' (viewer behavior), 'geographic' (location data), 'platforms' (device/OS breakdown). Run list_analytics_capabilities for all 60+ types.",
                    },
                    "entry_id": {
                        "type": "string",
                        "description": "Optional: Filter analytics for specific video (e.g., '1_abc123'). Leave empty for all content.",
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
                        "description": "Start date in YYYY-MM-DD format (e.g., '2024-01-01')",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., '2024-01-31')",
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
                        "description": "Optional: Track single video's performance over time (e.g., '1_abc123'). Leave empty for platform-wide trends.",
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["hours", "days", "weeks", "months"],
                        "description": "Time grouping for data points (default: 'days'). Use 'hours' for <7 day ranges, 'days' for monthly, 'weeks' for quarterly, 'months' for yearly views. Affects data granularity.",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="get_video_retention",
            description="Analyze WHERE viewers stop watching in a video. USE WHEN: Optimizing video content, finding boring sections, identifying engaging moments, improving completion rates. RETURNS: 101 data points (0-100%) showing viewer count at each percent of video. EXAMPLES: 'Where do viewers drop off in video 1_abc123?', 'What parts get replayed?', 'Compare retention for anonymous vs logged-in users'. Shows exact percentages where audience is lost.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video to analyze (required, format: '1_abc123'). Get from search_entries or get_media_entry.",
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
                        "description": "Optional viewer segment: 'anonymous' (not logged in), 'registered' (logged in), 'user@email.com' (specific user), 'cohort:students' (named group). Compare different audience behaviors.",
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
            description="Get LIVE analytics updating every 30 seconds. USE WHEN: Monitoring live events/streams, building real-time dashboards, tracking immediate campaign impact, detecting issues as they happen. RETURNS: Current active viewers, plays per minute, bandwidth usage. EXAMPLES: 'How many people watching right now?', 'Monitor live event performance', 'Track viral video in real-time'. Different from historical analytics - this is NOW.",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["viewers", "geographic", "quality"],
                        "description": "What to monitor (default: 'viewers'): 'viewers' = active viewer count, 'geographic' = viewer locations, 'quality' = streaming performance/buffering.",
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
            description="Analyze streaming QUALITY and viewer experience. USE WHEN: Troubleshooting playback issues, monitoring streaming performance, optimizing delivery, investigating viewer complaints. RETURNS: Buffer rates, bitrate averages, error rates, startup times, quality scores. EXAMPLES: 'Why are users complaining about buffering?', 'Check streaming quality by device type', 'Find videos with poor performance'. Helps ensure smooth playback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (e.g., '2024-01-01')",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., '2024-01-31')",
                    },
                    "metric_type": {
                        "type": "string",
                        "enum": ["overview", "experience", "engagement", "stream", "errors"],
                        "description": "Quality aspect to analyze (default: 'overview'): 'overview' = general quality, 'experience' = user QoE scores, 'engagement' = quality impact on viewing, 'stream' = technical metrics, 'errors' = playback failures.",
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
            description="Analyze viewer LOCATIONS and regional performance. USE WHEN: Understanding global reach, planning regional strategies, checking market penetration, optimizing CDN, compliance checks. RETURNS: Views/viewers by country/region/city with percentages. EXAMPLES: 'Which countries watch our content?', 'Show US state breakdown', 'Find top 10 cities for viewership'. Includes map-ready data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (e.g., '2024-01-01')",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (e.g., '2024-01-31')",
                    },
                    "granularity": {
                        "type": "string",
                        "enum": ["world", "country", "region", "city"],
                        "description": "Location detail level (default: 'country'): 'world' = continents, 'country' = nations, 'region' = states/provinces, 'city' = cities. Higher detail requires region_filter.",
                    },
                    "region_filter": {
                        "type": "string",
                        "description": "Zoom into specific area: For region view use country code (e.g., 'US' for US states), for city view use 'US-CA' for California cities. Required for region/city granularity.",
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
            description="Discover ALL analytics capabilities of this system. USE WHEN: User asks 'what analytics can you do?', exploring available reports, understanding metrics options, learning about analytics features. RETURNS: Complete list of 7 analytics functions with descriptions, 60+ report types, available dimensions, time intervals. EXAMPLE: Always run this when user first asks about analytics. No parameters needed - just call it!",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_download_url",
            description="Get direct DOWNLOAD link for video files. USE WHEN: User needs to download/save video locally, export for editing, backup content, share downloadable link. RETURNS: Time-limited secure URL for downloading. EXAMPLE: 'Download video 1_abc123', 'Get mp4 file for editing'. Different from streaming - this is for saving files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video to download (format: '1_abc123')",
                    },
                    "flavor_id": {
                        "type": "string",
                        "description": "Optional: Choose specific quality/format. Leave empty for default. Use list_media_entries to see available flavors.",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_thumbnail_url",
            description="Get video THUMBNAIL/POSTER image. USE WHEN: Displaying video previews, creating galleries, showing video cards, generating custom thumbnails. RETURNS: Image URL with your specified size. EXAMPLES: 'Get thumbnail for video 1_abc123', 'Create 400x300 preview image', 'Get frame from 30 seconds in'. Can capture any frame from video.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video to get thumbnail from (format: '1_abc123')",
                    },
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
            description="SEARCH for videos or LIST all content. USE WHEN: Finding videos by keyword, listing newest content, discovering what's available, filtering by date/category. POWERFUL SEARCH across titles, descriptions, tags, captions. EXAMPLES: 'Find videos about python', 'Show newest 10 videos' (use query='*' sort_field='created_at'), 'Search in transcripts for keyword', 'List videos from last week'. This is your primary discovery tool!",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms or '*' for all. EXAMPLES: '*' = list all videos, 'marketing' = find marketing content, '\"exact phrase\"' = exact match, 'python programming' = videos containing both words. ALWAYS use '*' when listing newest/all videos.",
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
            description="Find all CAPTIONS/SUBTITLES for a video. USE WHEN: Checking if video has captions, finding available languages, preparing for accessibility, getting transcript. RETURNS: List of caption files with languages, formats (SRT/VTT), IDs. EXAMPLE: 'Does video 1_abc123 have captions?', 'List subtitle languages available'. First step before getting caption content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video to check for captions (format: '1_abc123')",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_caption_content",
            description="Get actual CAPTION TEXT or download captions file. USE WHEN: Reading video transcript, downloading subtitles, analyzing spoken content, creating accessible content. RETURNS: Full caption text and download URL. EXAMPLE: 'Get English subtitles for video', 'Read transcript to find mentions of topic'. Use after list_caption_assets to get specific caption ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "caption_asset_id": {
                        "type": "string",
                        "description": "Caption ID from list_caption_assets (format: '1_xyz789')",
                    },
                },
                "required": ["caption_asset_id"],
            },
        ),
        types.Tool(
            name="list_attachment_assets",
            description="Find FILES ATTACHED to videos. USE WHEN: Looking for supplementary materials, PDFs, slides, documents linked to video. RETURNS: List of attached files with names, types, sizes, IDs. EXAMPLES: 'What documents are attached to training video?', 'Find PDF slides for presentation'. Attachments are additional files uploaded with videos.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Video to check for attachments (format: '1_abc123')",
                    },
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="get_attachment_content",
            description="Download or read ATTACHED FILES from videos. USE WHEN: Accessing supplementary materials, downloading PDFs, getting presentation slides, reading attached documents. RETURNS: File content (if text) or download URL. EXAMPLE: 'Download the PDF slides', 'Read the attached notes'. Use after list_attachment_assets to get specific attachment ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "attachment_asset_id": {
                        "type": "string",
                        "description": "Attachment ID from list_attachment_assets (format: '1_xyz789')",
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


@server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List all available prompts."""
    return prompts_manager.list_prompts()


@server.get_prompt()
async def get_prompt(
    name: str, arguments: Optional[Dict[str, Any]] = None
) -> types.GetPromptResult:
    """Get a specific prompt."""
    return await prompts_manager.get_prompt(name, kaltura_manager, arguments)


@server.list_resources()
async def list_resources() -> List[types.Resource]:
    """List all available resources."""
    return resources_manager.list_resources()


@server.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    """List all resource templates."""
    return resources_manager.list_resource_templates()


@server.read_resource()
async def read_resource(uri: str) -> List[types.ResourceContents]:
    """Read a resource."""
    content = await resources_manager.read_resource(uri, kaltura_manager)
    return [types.ResourceContents(uri=uri, mimeType="application/json", text=content)]


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
