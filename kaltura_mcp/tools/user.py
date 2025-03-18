"""
User-related tool handlers for Kaltura MCP Server.
"""
import json
import logging
from typing import Dict, Any, List, Union

import mcp.types as types
from KalturaClient.Plugins.Core import (
    KalturaUserFilter,
    KalturaFilterPager,
    KalturaUser,
    KalturaUserOrderBy
)

from kaltura_mcp.tools.base import KalturaToolHandler, KalturaJSONEncoder

logger = logging.getLogger(__name__)

class UserGetToolHandler(KalturaToolHandler):
    """Handler for the kaltura.user.get tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a user get request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["id"])
        
        user_id = arguments["id"]
        
        # Execute request
        try:
            user = await self.kaltura_client.execute_request(
                "user", "get",
                userId=user_id
            )
            
            # Format response
            response = {
                "id": user.id,
                "partnerId": user.partnerId,
                "screenName": user.screenName,
                "fullName": user.fullName,
                "email": user.email,
                "status": user.status.value if hasattr(user.status, 'value') else 2,
                "createdAt": user.createdAt,
                "updatedAt": user.updatedAt,
                "lastLoginTime": user.lastLoginTime,
                "roleIds": user.roleIds,
                "isAdmin": user.isAdmin,
                "type": user.type.value if hasattr(user.type, 'value') else 0,
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error getting user: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.user.get",
            description="Get details of a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user to retrieve"
                    }
                },
                "required": ["user_id"]
            }
        )


class UserAddToolHandler(KalturaToolHandler):
    """Handler for the kaltura.user.add tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a user add request."""
        # Validate required parameters
        # Check if we have full_name or first_name + last_name
        if "full_name" not in arguments and ("first_name" in arguments and "last_name" in arguments):
            arguments["full_name"] = f"{arguments['first_name']} {arguments['last_name']}"
        
        # Check if we have user_id instead of id
        if "user_id" in arguments and "id" not in arguments:
            arguments["id"] = arguments["user_id"]
            
        self._validate_required_params(arguments, ["id", "email", "full_name"])
        
        user_id = arguments["id"]
        email = arguments["email"]
        full_name = arguments["full_name"]
        screen_name = arguments.get("screenName", full_name)
        
        try:
            # Create a new user
            user = KalturaUser()
            user.id = user_id
            user.email = email
            user.fullName = full_name
            user.screenName = screen_name
            
            # Add optional parameters if provided
            if "role_ids" in arguments:
                user.roleIds = arguments["role_ids"]
            
            if "is_admin" in arguments:
                user.isAdmin = arguments["is_admin"]
            
            # Add the user
            result = await self.kaltura_client.execute_request(
                "user", "add",
                user=user
            )
            
            # Format response
            response = {
                "id": result.id,
                "partnerId": result.partnerId,
                "screenName": result.screenName,
                "fullName": result.fullName,
                "email": result.email,
                "status": result.status.value if hasattr(result.status, 'value') else 2,
                "createdAt": result.createdAt,
                "updatedAt": result.updatedAt,
                "message": "User added successfully"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error adding user: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.user.add",
            description="Add a new user to Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "User ID (unique identifier)"
                    },
                    "email": {
                        "type": "string",
                        "description": "User's email address"
                    },
                    "full_name": {
                        "type": "string",
                        "description": "User's full name"
                    },
                    "screenName": {
                        "type": "string",
                        "description": "User's screen name (defaults to full name if not provided)"
                    },
                    "role_ids": {
                        "type": "string",
                        "description": "Comma-separated list of role IDs"
                    },
                    "is_admin": {
                        "type": "boolean",
                        "description": "Whether the user is an admin"
                    }
                },
                "required": ["id", "email", "full_name"]
            }
        )


class UserUpdateToolHandler(KalturaToolHandler):
    """Handler for the kaltura.user.update tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a user update request."""
        # Validate required parameters
        # Check if we have user_id or id
        if "user_id" not in arguments and "id" in arguments:
            arguments["user_id"] = arguments["id"]
        
        self._validate_required_params(arguments, ["id"])
        
        user_id = arguments["id"]
        
        try:
            # First get the current user
            current_user = await self.kaltura_client.execute_request(
                "user", "get",
                userId=user_id
            )
            
            # Create a new user object with the current values
            user = KalturaUser()
            user.email = arguments.get("email", current_user.email)
            user.fullName = arguments.get("full_name", current_user.fullName)
            
            # Handle screenName properly
            if "screenName" in arguments:
                user.screenName = arguments["screenName"]
            
            # Add optional parameters if provided
            if "role_ids" in arguments:
                user.roleIds = arguments["role_ids"]
            
            if "is_admin" in arguments:
                user.isAdmin = arguments["is_admin"]
            
            # Update the user - don't pass screen_name separately
            updated_user = await self.kaltura_client.execute_request(
                "user", "update",
                userId=user_id,
                user=user
            )
            
            # Format response
            response = {
                "id": updated_user.id,
                "partnerId": updated_user.partnerId,
                "screenName": updated_user.screenName,
                "full_name": updated_user.fullName,
                "email": updated_user.email,
                "status": updated_user.status.value if hasattr(updated_user.status, 'value') else 2,
                "createdAt": updated_user.createdAt,
                "updatedAt": updated_user.updatedAt,
                "first_name": arguments.get("first_name", ""),
                "last_name": arguments.get("last_name", ""),
                "message": "User updated successfully"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error updating user: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.user.update",
            description="Update a user in Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user to update"
                    },
                    "email": {
                        "type": "string",
                        "description": "New email address for the user"
                    },
                    "full_name": {
                        "type": "string",
                        "description": "New full name for the user"
                    },
                    "screenName": {
                        "type": "string",
                        "description": "New screen name for the user"
                    },
                    "role_ids": {
                        "type": "string",
                        "description": "New comma-separated list of role IDs"
                    },
                    "is_admin": {
                        "type": "boolean",
                        "description": "Whether the user is an admin"
                    }
                },
                "required": ["user_id"]
            }
        )


class UserDeleteToolHandler(KalturaToolHandler):
    """Handler for the kaltura.user.delete tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a user delete request."""
        # Validate required parameters
        # Check if we have user_id or id
        if "user_id" not in arguments and "id" in arguments:
            arguments["user_id"] = arguments["id"]
        
        self._validate_required_params(arguments, ["id"])
        
        user_id = arguments["id"]
        
        try:
            # First get the current user to verify it exists
            current_user = await self.kaltura_client.execute_request(
                "user", "get",
                userId=user_id
            )
            
            # Delete the user
            result = await self.kaltura_client.execute_request(
                "user", "delete",
                userId=user_id
            )
            
            # Format response
            response = {
                "id": user_id,
                "fullName": current_user.fullName,
                "message": "User deleted successfully",
                "success": True
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error deleting user: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.user.delete",
            description="Delete a user from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user to delete"
                    }
                },
                "required": ["user_id"]
            }
        )


class UserListToolHandler(KalturaToolHandler):
    """Handler for the kaltura.user.list tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a user list request."""
        # Validate parameters
        page_size = arguments.get("page_size", 30)
        page = arguments.get("page", 1)
        page_index = arguments.get("page_index", page)
        
        # Create filter
        filter_params = arguments.get("filter", {})
        user_filter = KalturaUserFilter()
        
        # Apply filter parameters
        for key, value in filter_params.items():
            if hasattr(user_filter, key):
                setattr(user_filter, key, value)
        
        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index
        
        # Execute request
        try:
            result = await self.kaltura_client.execute_request(
                "user", "list",
                filter=user_filter, pager=pager
            )
            
            # Format response
            users = []
            for user in result.objects:
                users.append({
                    "id": user.id,
                    "partnerId": user.partnerId,
                    "screenName": user.screenName,
                    "fullName": user.fullName,
                    "email": user.email,
                    "status": user.status.value if hasattr(user.status, 'value') else 2,
                    "createdAt": user.createdAt,
                    "updatedAt": user.updatedAt,
                    "lastLoginTime": user.lastLoginTime,
                    "roleIds": user.roleIds,
                    "isAdmin": user.isAdmin,
                    "type": user.type.value if hasattr(user.type, 'value') else 0,
                })
            
            response = {
                "totalCount": result.totalCount,
                "users": users,
                "pageSize": page_size,
                "pageIndex": page_index,
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error listing users: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.user.list",
            description="List users from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "Filter parameters for users",
                        "properties": {
                            "idOrScreenNameStartsWith": {
                                "type": "string",
                                "description": "Free text search on ID or screen name"
                            },
                            "idEqual": {
                                "type": "string",
                                "description": "Filter by user ID"
                            },
                            "statusEqual": {
                                "type": "integer",
                                "description": "Filter by status"
                            },
                            "createdAtGreaterThanOrEqual": {
                                "type": "integer",
                                "description": "Filter by creation date (unix timestamp)"
                            }
                        }
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "default": 30
                    },
                    "page_index": {
                        "type": "integer",
                        "description": "Page number (1-based)",
                        "default": 1
                    }
                }
            }
        )