#!/usr/bin/env python3
"""Kaltura MCP Server - Provides tools for managing Kaltura API operations."""

import os
import sys
import asyncio
from typing import Any, Dict, List, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .kaltura_client import KalturaClientManager
from .tools import (
    get_media_entry,
    list_categories,
    get_analytics,
    get_download_url,
    get_thumbnail_url,
    search_entries_intelligent,
    list_caption_assets,
    get_caption_content,
    list_attachment_assets,
    get_attachment_content,
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
                    "search_text": {"type": "string", "description": "Filter categories by name or description"},
                    "limit": {"type": "integer", "description": "Maximum number of categories to return (default: 20)"},
                },
            },
        ),
        types.Tool(
            name="get_analytics",
            description="Get comprehensive analytics using Kaltura Report API. Supports multiple report types including content performance, user engagement, geographic distribution, contributor stats, and more.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "Optional media entry ID for specific entry analytics. If omitted, returns aggregated analytics."},
                    "from_date": {"type": "string", "description": "Start date for analytics (YYYY-MM-DD format)"},
                    "to_date": {"type": "string", "description": "End date for analytics (YYYY-MM-DD format)"},
                    "report_type": {
                        "type": "string",
                        "enum": ["content", "user_engagement", "contributors", "geographic", "bandwidth", "storage", "system", "platforms", "operating_system", "browsers"],
                        "description": "Type of analytics report: 'content' (top performing content), 'user_engagement' (user behavior), 'contributors' (top uploaders), 'geographic' (location data), 'bandwidth' (usage stats), 'storage' (storage metrics), 'system' (system reports), 'platforms' (device types), 'operating_system' (OS breakdown), 'browsers' (browser stats). Default: 'content'"
                    },
                    "categories": {"type": "string", "description": "Optional category filter (use full category name including parent paths)"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return (default: 20, max: 100)"},
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["plays", "views", "engagement", "drop_off"]},
                        "description": "Metrics to retrieve: plays, views, engagement, drop_off. Used for reference/interpretation.",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="get_download_url",
            description="Get direct download URL for media files",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The media entry ID"},
                    "flavor_id": {"type": "string", "description": "Optional specific flavor ID for quality/format selection"},
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
                    "width": {"type": "integer", "description": "Thumbnail width in pixels (default: 120)"},
                    "height": {"type": "integer", "description": "Thumbnail height in pixels (default: 90)"},
                    "second": {"type": "integer", "description": "Video timestamp in seconds to capture (default: 5)"},
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
                        "description": "Search query. Use '*' to list all entries (essential for finding latest/newest content), use keywords to search for specific content, or exact phrases in quotes."
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["unified", "entry", "caption", "metadata", "cuepoint"],
                        "description": "Search scope: 'unified' (all fields), 'entry' (titles/descriptions), 'caption' (transcripts), 'metadata' (custom fields), 'cuepoint' (chapters). Default: 'unified'"
                    },
                    "match_type": {
                        "type": "string",
                        "enum": ["partial", "exact_match", "starts_with", "exists", "range"],
                        "description": "Match type: 'partial' (contains), 'exact_match' (exact phrase), 'starts_with' (prefix), 'exists' (has value), 'range' (numeric/date). Default: 'partial'"
                    },
                    "specific_field": {
                        "type": "string",
                        "description": "Specific field to search within the selected scope. Common fields: 'name', 'description', 'tags', 'created_at'. Leave blank to search all fields."
                    },
                    "boolean_operator": {
                        "type": "string",
                        "enum": ["and", "or", "not"],
                        "description": "Boolean operator for multi-term queries: 'and' (all terms), 'or' (any term), 'not' (exclude). Default: 'and'"
                    },
                    "include_highlights": {
                        "type": "boolean",
                        "description": "Include highlighted matching text snippets in results. Default: true"
                    },
                    "custom_metadata": {
                        "type": "object",
                        "properties": {
                            "profile_id": {"type": "integer", "description": "Custom metadata profile ID"},
                            "xpath": {"type": "string", "description": "XPath to specific metadata field"}
                        },
                        "description": "Custom metadata search parameters. Requires both profile_id and xpath. Used for searching custom metadata fields."
                    },
                    "date_range": {
                        "type": "object", 
                        "properties": {
                            "after": {"type": "string", "description": "Created after this date (YYYY-MM-DD format)"},
                            "before": {"type": "string", "description": "Created before this date (YYYY-MM-DD format)"}
                        },
                        "description": "Filter entries by creation date range. Use YYYY-MM-DD format."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20, max: 100)"
                    },
                    "sort_field": {
                        "type": "string",
                        "enum": ["created_at", "updated_at", "name", "views", "plays", "last_played_at", "rank", "start_date", "end_date"],
                        "description": "Field to sort by. Options: 'created_at' (creation date), 'updated_at' (last modified), 'name' (alphabetical), 'views' (view count), 'plays' (play count), 'last_played_at' (recent activity), 'rank' (relevance), 'start_date' (schedule start), 'end_date' (schedule end). Default: 'created_at'"
                    },
                    "sort_order": {
                        "type": "string",
                        "enum": ["desc", "asc"],
                        "description": "Sort direction. Use 'desc' for newest/highest first (default), 'asc' for oldest/lowest first. For finding latest content, use 'desc' with 'created_at'"
                    }
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
                    "attachment_asset_id": {"type": "string", "description": "The attachment asset ID"},
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