"""
Category-related tool handlers for Kaltura MCP Server.
"""
import json
import logging
from typing import Dict, Any, List, Union

import mcp.types as types
from KalturaClient.Plugins.Core import (
    KalturaCategoryFilter,
    KalturaFilterPager,
    KalturaCategory,
    KalturaCategoryOrderBy
)

from kaltura_mcp.tools.base import KalturaToolHandler, KalturaJSONEncoder

logger = logging.getLogger(__name__)

class CategoryGetToolHandler(KalturaToolHandler):
    """Handler for the kaltura.category.get tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a category get request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["id"])
        
        category_id = arguments["id"]
        
        # Execute request
        try:
            category = await self.kaltura_client.execute_request(
                "category", "get",
                id=category_id
            )
            
            # Format response
            response = {
                "id": category.id,
                "name": category.name,
                "fullName": category.fullName,
                "description": category.description,
                "tags": category.tags,
                "status": category.status.value if hasattr(category.status, 'value') else 2,
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
                "owner": category.owner
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting category: {e}")
            # Always raise the exception for category not found errors
            if "CATEGORY_NOT_FOUND" in str(e) or "not found" in str(e).lower():
                raise ValueError(f"Category not found: {category_id}")
            # For other errors, return an error response
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error getting category: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.category.get",
            description="Get details of a specific category",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the category to retrieve"
                    }
                },
                "required": ["id"]
            }
        )


class CategoryAddToolHandler(KalturaToolHandler):
    """Handler for the kaltura.category.add tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a category add request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["name"])
        
        name = arguments["name"]
        description = arguments.get("description", "")
        tags = arguments.get("tags", "")
        parent_id = arguments.get("parent_id", 0)
        
        try:
            # Create a new category
            category = KalturaCategory()
            category.name = name
            category.description = description
            category.tags = tags
            category.parentId = parent_id
            
            # Add the category
            result = await self.kaltura_client.execute_request(
                "category", "add",
                category=category
            )
            
            # Format response
            response = {
                "id": result.id,
                "name": result.name,
                "fullName": result.fullName,
                "description": result.description,
                "tags": result.tags,
                "status": result.status.value if hasattr(result.status, 'value') else 2,
                "createdAt": result.createdAt,
                "updatedAt": result.updatedAt,
                "parentId": result.parentId,
                "message": "Category added successfully"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error adding category: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.category.add",
            description="Add a new category to Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the category"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the category"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Comma-separated list of tags"
                    },
                    "parent_id": {
                        "type": "integer",
                        "description": "ID of the parent category (0 for root category)"
                    }
                },
                "required": ["name"]
            }
        )


class CategoryUpdateToolHandler(KalturaToolHandler):
    """Handler for the kaltura.category.update tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a category update request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["id"])
        
        category_id = arguments["id"]
        
        try:
            # First get the current category
            current_category = await self.kaltura_client.execute_request(
                "category", "get",
                id=category_id
            )
            
            # Create a new category object with the current values
            category = KalturaCategory()
            category.name = arguments.get("name", current_category.name)
            category.description = arguments.get("description", current_category.description)
            category.tags = arguments.get("tags", current_category.tags)
            
            # Update the category - pass name and description directly as well
            updated_category = await self.kaltura_client.execute_request(
                "category", "update",
                id=category_id,
                category=category
            )
            
            # Format response
            response = {
                "id": updated_category.id,
                "name": updated_category.name,
                "fullName": updated_category.fullName,
                "description": updated_category.description,
                "tags": updated_category.tags,
                "status": updated_category.status.value if hasattr(updated_category.status, 'value') else 2,
                "createdAt": updated_category.createdAt,
                "updatedAt": updated_category.updatedAt,
                "parentId": updated_category.parentId,
                "message": "Category updated successfully"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error updating category: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.category.update",
            description="Update a category in Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the category to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the category"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the category"
                    },
                    "tags": {
                        "type": "string",
                        "description": "New comma-separated list of tags"
                    }
                },
                "required": ["id"]
            }
        )


class CategoryDeleteToolHandler(KalturaToolHandler):
    """Handler for the kaltura.category.delete tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a category delete request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["id"])
        
        category_id = arguments["id"]
        move_entries_to_parent = arguments.get("move_entries_to_parent", True)
        
        try:
            # First get the current category to verify it exists
            current_category = await self.kaltura_client.execute_request(
                "category", "get",
                id=category_id
            )
            
            # Delete the category
            result = await self.kaltura_client.execute_request(
                "category", "delete",
                id=category_id,
                moveEntriesToParentCategory=move_entries_to_parent
            )
            
            # Format response
            response = {
                "id": category_id,
                "name": current_category.name,
                "message": "Category deleted successfully",
                "success": True
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error deleting category: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.category.delete",
            description="Delete a category from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the category to delete"
                    },
                    "move_entries_to_parent": {
                        "type": "boolean",
                        "description": "Whether to move entries to parent category",
                        "default": True
                    }
                },
                "required": ["id"]
            }
        )


class CategoryListToolHandler(KalturaToolHandler):
    """Handler for the kaltura.category.list tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a category list request."""
        # Validate parameters
        page_size = arguments.get("page_size", 30)
        page = arguments.get("page", 1)
        page_index = arguments.get("page_index", page)
        
        # Create filter
        filter_params = arguments.get("filter", {})
        category_filter = KalturaCategoryFilter()
        
        # Apply filter parameters
        for key, value in filter_params.items():
            if hasattr(category_filter, key):
                setattr(category_filter, key, value)
        
        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index
        
        # Execute request
        try:
            result = await self.kaltura_client.execute_request(
                "category", "list",
                filter=category_filter, 
                pager=pager
            )
            
            # Format response
            categories = []
            for category in result.objects:
                categories.append({
                    "id": category.id,
                    "name": category.name,
                    "fullName": category.fullName,
                    "description": category.description,
                    "tags": category.tags,
                    "status": category.status.value if hasattr(category.status, 'value') else 2,
                    "createdAt": category.createdAt,
                    "updatedAt": category.updatedAt,
                    "parentId": category.parentId,
                    "depth": category.depth,
                    "entriesCount": category.entriesCount,
                    "fullIds": category.fullIds,
                })
            
            response = {
                "totalCount": result.totalCount,
                "categories": categories,
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
            logger.error(f"Error listing categories: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error listing categories: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.category.list",
            description="List categories from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "Filter parameters for categories",
                        "properties": {
                            "nameLike": {
                                "type": "string",
                                "description": "Free text search on name"
                            },
                            "parentIdEqual": {
                                "type": "integer",
                                "description": "Filter by parent category ID"
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