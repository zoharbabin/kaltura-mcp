"""
Media-related resource handlers for Kaltura MCP Server.
"""

import json
import logging
import re
from typing import Any, Dict, List, Pattern, Union

import mcp.types as types
from KalturaClient.Plugins.Core import KalturaFilterPager, KalturaMediaEntryFilter

from kaltura_mcp.resources.base import KalturaResourceHandler
from kaltura_mcp.tools.base import KalturaJSONEncoder

logger = logging.getLogger(__name__)


class MediaEntryResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://media/{entryId} resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        # Exclude "list" from the entry ID pattern
        return re.compile(r"^kaltura://media/(?!list$)(?P<entry_id>[^/]+)$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a media entry resource request."""
        # Extract entry ID from URI
        params = self.extract_uri_params(uri)
        entry_id = params.get("entry_id")

        if not entry_id:
            raise ValueError(f"Invalid media entry URI: {uri}")

        # Execute request
        try:
            entry = await self.kaltura_client.execute_request("media", "get", entryId=entry_id)

            # Format response
            response = {
                "id": entry.id,
                "name": entry.name,
                "description": entry.description,
                "createdAt": entry.createdAt,
                "updatedAt": entry.updatedAt,
                "status": entry.status.value if entry.status is not None else None,
                "mediaType": entry.mediaType.value,
                "duration": entry.duration,
                "thumbnailUrl": entry.thumbnailUrl,
                "downloadUrl": entry.downloadUrl,
                "plays": entry.plays,
                "views": entry.views,
                "width": entry.width,
                "height": entry.height,
                "tags": entry.tags,
            }

            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

        except Exception as e:
            logger.error(f"Error getting media entry: {e}")
            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(
                        {"error": f"Error getting media entry: {str(e)}"},
                        indent=2,
                        cls=KalturaJSONEncoder,
                    ),
                    uri=uri,  # type: ignore
                )
            ]

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura Media Entry",
            description="Get details of a specific media entry",
            mimeType="application/json",
            uri="kaltura://media/{entryId}",  # type: ignore
        )


class MediaListResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://media/list resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        return re.compile(r"^kaltura://media/list(?:\?(?P<query_string>.*))?$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a media list resource request."""
        # Extract query parameters from URI
        params = self.extract_uri_params(uri)
        query_string = params.get("query_string", "")

        # Parse query string
        import urllib.parse

        query_params = dict(urllib.parse.parse_qsl(query_string))

        # Set defaults
        page_size = int(query_params.get("page_size", "30"))
        page_index = int(query_params.get("page_index", "1"))

        # Create filter
        media_filter = KalturaMediaEntryFilter()
        media_filter.orderBy = "-createdAt"  # Sort by newest first

        # Apply filter parameters
        if "name_like" in query_params:
            media_filter.nameLike = query_params["name_like"]

        if "media_type" in query_params:
            media_filter.mediaTypeEqual = int(query_params["media_type"])

        if "status" in query_params:
            media_filter.statusEqual = int(query_params["status"])

        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index

        # Execute request
        try:
            result = await self.kaltura_client.execute_request("media", "list", filter=media_filter, pager=pager)

            # Format response
            entries = []
            for entry in result.objects:
                entries.append(
                    {
                        "id": entry.id,
                        "name": entry.name,
                        "description": entry.description,
                        "createdAt": entry.createdAt,
                        "updatedAt": entry.updatedAt,
                        "status": entry.status.value if entry.status is not None else None,
                        "mediaType": entry.mediaType.value if entry.mediaType is not None else None,
                        "duration": entry.duration,
                        "thumbnailUrl": entry.thumbnailUrl,
                    }
                )

            response = {
                "totalCount": result.totalCount,
                "entries": entries,
                "pageSize": page_size,
                "pageIndex": page_index,
            }

            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

        except Exception as e:
            logger.error(f"Error listing media entries: {e}")
            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps({"error": f"Error listing media entries: {str(e)}"}, indent=2),
                    uri=uri,  # type: ignore
                )
            ]

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura Media List",
            description="List media entries with optional filtering",
            mimeType="application/json",
            uri="kaltura://media/list",  # type: ignore
        )
