"""
Resource handlers for Kaltura MCP Server.
"""
from kaltura_mcp.resources.base import KalturaResourceHandler
from kaltura_mcp.resources.media import MediaEntryResourceHandler, MediaListResourceHandler

__all__ = ["KalturaResourceHandler", "MediaEntryResourceHandler", "MediaListResourceHandler"]