"""
Category-related resource handlers for Kaltura MCP Server.
"""

import json
import logging
import re
from typing import Any, Dict, List, Pattern, Union

import mcp.types as types
from KalturaClient.Plugins.Core import KalturaCategoryFilter, KalturaFilterPager

from kaltura_mcp.resources.base import KalturaResourceHandler
from kaltura_mcp.tools.base import KalturaJSONEncoder

logger = logging.getLogger(__name__)


class CategoryResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://category/{categoryId} resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        return re.compile(r"^kaltura://category/(?P<category_id>\d+)$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a category resource request."""
        # Extract category ID from URI
        params = self.extract_uri_params(uri)
        category_id = params.get("category_id")

        if not category_id:
            raise ValueError(f"Invalid category URI: {uri}")

        # Execute request
        try:
            category = await self.kaltura_client.execute_request("category", "get", id=int(category_id))

            # Format response
            response = {
                "id": category.id,
                "name": category.name,
                "fullName": category.fullName,
                "description": category.description,
                "tags": category.tags,
                "status": category.status.value if category.status else None,
                "createdAt": category.createdAt,
                "updatedAt": category.updatedAt,
                "parentId": category.parentId,
                "depth": category.depth,
                "entriesCount": category.entriesCount,
                "fullIds": category.fullIds,
                "privacyContext": category.privacyContext,
                "privacy": category.privacy,
                "membersCount": category.membersCount,
                "pendingMembersCount": category.pendingMembersCount,
                "owner": category.owner,
            }

            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

        except Exception as e:
            logger.error(f"Error getting category: {e}")
            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(
                        {"error": f"Error getting category: {str(e)}"},
                        indent=2,
                        cls=KalturaJSONEncoder,
                    ),
                    uri=uri,  # type: ignore
                )
            ]

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura Category",
            description="Get details of a specific category",
            mimeType="application/json",
            uri="kaltura://category/{categoryId}",  # type: ignore
        )


class CategoryListResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://category/list resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        return re.compile(r"^kaltura://category/list(?:\?(?P<query_string>.*))?$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a category list resource request."""
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
        category_filter = KalturaCategoryFilter()

        # Apply filter parameters
        if "name_like" in query_params:
            category_filter.nameLike = query_params["name_like"]

        if "parent_id" in query_params:
            category_filter.parentIdEqual = int(query_params["parent_id"])

        if "status" in query_params:
            category_filter.statusEqual = int(query_params["status"])

        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index

        # Execute request
        try:
            result = await self.kaltura_client.execute_request("category", "list", filter=category_filter, pager=pager)

            # Format response
            categories = []
            for category in result.objects:
                categories.append(
                    {
                        "id": category.id,
                        "name": category.name,
                        "fullName": category.fullName,
                        "description": category.description,
                        "tags": category.tags,
                        "status": category.status.value if category.status else None,
                        "createdAt": category.createdAt,
                        "updatedAt": category.updatedAt,
                        "parentId": category.parentId,
                        "depth": category.depth,
                        "entriesCount": category.entriesCount,
                        "fullIds": category.fullIds,
                    }
                )

            response = {
                "totalCount": result.totalCount,
                "categories": categories,
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
            logger.error(f"Error listing categories: {e}")
            raise ValueError(f"Error listing categories: {str(e)}") from e

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura Category List",
            description="List categories with optional filtering",
            mimeType="application/json",
            uri="kaltura://category/list",  # type: ignore
        )
