"""
User-related resource handlers for Kaltura MCP Server.
"""

import json
import logging
import re
import urllib.parse
from typing import List, Pattern

import mcp.types as types
from KalturaClient.Plugins.Core import KalturaFilterPager, KalturaUserFilter

from kaltura_mcp.resources.base import KalturaResourceHandler
from kaltura_mcp.tools.base import KalturaJSONEncoder

logger = logging.getLogger(__name__)


class UserResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://user/{userId} resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        return re.compile(r"^kaltura://user/(?P<user_id>(?!list$)[^/]+)$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a user resource request."""
        # Extract user ID from URI
        params = self.extract_uri_params(uri)
        user_id = params.get("user_id")

        if not user_id:
            raise ValueError(f"Invalid user URI: {uri}")

        # Execute request
        try:
            user = await self.kaltura_client.execute_request("user", "get", userId=user_id)

            # Format response
            response = {
                "id": user.id,
                "partnerId": user.partnerId,
                "screenName": user.screenName,
                "fullName": user.fullName,
                "email": user.email,
                "status": user.status.value if user.status is not None else None,
                "createdAt": user.createdAt,
                "updatedAt": user.updatedAt,
                "lastLoginTime": user.lastLoginTime,
                "roleIds": user.roleIds,
                "isAdmin": user.isAdmin,
                "type": user.type.value if user.type else None,
            }

            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps({"error": f"Error getting user: {str(e)}"}, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura User",
            description="Get details of a specific user",
            mimeType="application/json",
            uri="kaltura://user/{userId}",  # type: ignore
        )


class UserListResourceHandler(KalturaResourceHandler):
    """Handler for the kaltura://user/list resource."""

    def _compile_uri_pattern(self) -> Pattern:
        """Compile the URI pattern for matching."""
        return re.compile(r"^kaltura://user/list(?:\?(?P<query_string>.*))?$")

    async def handle(self, uri: str) -> List[types.ResourceContents]:
        """Handle a user list resource request."""
        # Extract query parameters from URI
        params = self.extract_uri_params(uri)
        query_string = params.get("query_string", "")

        # Parse query string
        query_params = dict(urllib.parse.parse_qsl(query_string))

        # Set defaults
        page_size = int(query_params.get("page_size", "30"))
        page_index = int(query_params.get("page_index", "1"))

        # Create filter
        user_filter = KalturaUserFilter()

        # Apply filter parameters
        if "id_or_name_starts_with" in query_params:
            user_filter.idOrScreenNameStartsWith = query_params["id_or_name_starts_with"]

        if "id_equal" in query_params:
            user_filter.idEqual = query_params["id_equal"]

        if "status" in query_params:
            user_filter.statusEqual = int(query_params["status"])

        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index

        # Execute request
        try:
            result = await self.kaltura_client.execute_request("user", "list", filter=user_filter, pager=pager)

            # Format response
            users = []
            for user in result.objects:
                users.append(
                    {
                        "id": user.id,
                        "partnerId": user.partnerId,
                        "screenName": user.screenName,
                        "fullName": user.fullName,
                        "email": user.email,
                        "status": user.status.value if user.status is not None else None,
                        "createdAt": user.createdAt,
                        "updatedAt": user.updatedAt,
                        "lastLoginTime": user.lastLoginTime,
                        "roleIds": user.roleIds,
                        "isAdmin": user.isAdmin,
                        "type": user.type.value if user.type else None,
                    }
                )

            response = {
                "totalCount": result.totalCount,
                "users": users,
                "page_size": page_size,
                "page_index": page_index,
            }

            return [
                types.ResourceContents(
                    mimeType="application/json",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder),
                    uri=uri,  # type: ignore
                )
            ]

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise ValueError(f"Error listing users: {str(e)}") from e

    def get_resource_definition(self) -> types.Resource:
        """Return the resource definition."""
        return types.Resource(
            name="Kaltura User List",
            description="List users with optional filtering",
            mimeType="application/json",
            uri="kaltura://user/list",  # type: ignore
        )
