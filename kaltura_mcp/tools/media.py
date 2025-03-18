"""
Media-related tool handlers for Kaltura MCP Server.
"""
import json
import logging
import os
from typing import Dict, Any, List, Union

import mcp.types as types
from KalturaClient.Plugins.Core import (
    KalturaMediaEntryFilter,
    KalturaFilterPager,
    KalturaMediaEntry,
    KalturaMediaType,
    KalturaUploadToken,
    KalturaUploadedFileTokenResource
)

from kaltura_mcp.tools.base import KalturaToolHandler, KalturaJSONEncoder

logger = logging.getLogger(__name__)

class MediaGetToolHandler(KalturaToolHandler):
    """Handler for the kaltura.media.get tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a media get request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["entry_id"])
        entry_id = arguments["entry_id"]
        
        # Execute request
        try:
            entry = await self.kaltura_client.execute_request(
                "media", "get",
                entryId=entry_id
            )
            
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
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting media entry: {e}")
            
            # For data entries, we need to try the data.get endpoint
            if "ENTRY_ID_NOT_FOUND" in str(e):
                try:
                    # Try to get it as a data entry instead
                    logger.info(f"Entry {entry_id} not found as media, trying as data entry")
                    data_entry = await self.kaltura_client.execute_request(
                        "data", "get",
                        entryId=entry_id
                    )
                    
                    # Format response for data entry
                    response = {
                        "id": data_entry.id,
                        "name": data_entry.name,
                        "description": data_entry.description,
                        "createdAt": data_entry.createdAt,
                        "updatedAt": data_entry.updatedAt,
                        "status": data_entry.status.value if hasattr(data_entry, "status") else None,
                        "dataContent": data_entry.dataContent if hasattr(data_entry, "dataContent") else None,
                        "tags": data_entry.tags,
                        "entryType": "data"
                    }
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                        )
                    ]
                except Exception as data_error:
                    logger.error(f"Error getting data entry: {data_error}")
                    # If both media.get and data.get fail, raise the original exception
                    raise Exception(f"Media entry not found: {entry_id}") from data_error
            
            # For other errors, return an error response
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error getting media entry: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.media.get",
            description="Get details of a specific media entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "ID of the media entry to retrieve"
                    }
                },
                "required": ["entry_id"]
            }
        )


class MediaDeleteToolHandler(KalturaToolHandler):
    """Handler for the kaltura.media.delete tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a media delete request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["entry_id"])
        
        entry_id = arguments["entry_id"]
        
        try:
            # First get the current entry to verify it exists
            current_entry = await self.kaltura_client.execute_request(
                "media", "get",
                entryId=entry_id
            )
            
            # Delete the entry
            result = await self.kaltura_client.execute_request(
                "media", "delete",
                entryId=entry_id
            )
            
            # Format response
            response = {
                "id": entry_id,
                "name": current_entry.name,
                "message": "Media entry deleted successfully",
                "success": True
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error deleting media entry: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error deleting media entry: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.media.delete",
            description="Delete a media entry from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "ID of the media entry to delete"
                    }
                },
                "required": ["entry_id"]
            }
        )


class MediaUpdateToolHandler(KalturaToolHandler):
    """Handler for the kaltura.media.update tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a media update request."""
        # Validate required parameters
        self._validate_required_params(arguments, ["entry_id"])
        
        entry_id = arguments["entry_id"]
        
        try:
            # First get the current entry
            current_entry = await self.kaltura_client.execute_request(
                "media", "get",
                entryId=entry_id
            )
            
            # Create a new entry object with the current values
            entry = KalturaMediaEntry()
            entry.name = arguments.get("name", current_entry.name)
            entry.description = arguments.get("description", current_entry.description)
            entry.tags = arguments.get("tags", current_entry.tags)
            
            # Update the entry - only pass entryId and mediaEntry
            # The Kaltura API doesn't accept name and description as separate parameters
            updated_entry = await self.kaltura_client.execute_request(
                "media", "update",
                entryId=entry_id,
                mediaEntry=entry
            )
            
            # Format response
            response = {
                "id": updated_entry.id,
                "name": updated_entry.name,
                "description": updated_entry.description,
                "createdAt": updated_entry.createdAt,
                "updatedAt": updated_entry.updatedAt,
                "status": updated_entry.status.value,
                "mediaType": updated_entry.mediaType.value,
                "duration": updated_entry.duration,
                "thumbnailUrl": updated_entry.thumbnailUrl,
                "tags": updated_entry.tags,
                "message": "Media entry updated successfully"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(response, indent=2, cls=KalturaJSONEncoder)
                )
            ]
            
        except Exception as e:
            logger.error(f"Error updating media entry: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error updating media entry: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.media.update",
            description="Update a media entry in Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "ID of the media entry to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the media entry"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the media entry"
                    },
                    "tags": {
                        "type": "string",
                        "description": "New comma-separated list of tags"
                    }
                },
                "required": ["entry_id"]
            }
        )


class MediaListToolHandler(KalturaToolHandler):
    """Handler for the kaltura.media.list tool."""
    
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a media list request."""
        # Validate parameters
        page_size = arguments.get("page_size", 30)
        page = arguments.get("page", 1)
        page_index = arguments.get("page_index", page)
        
        # Create filter
        filter_params = arguments.get("filter", {})
        media_filter = KalturaMediaEntryFilter()
        
        # Apply filter parameters
        for key, value in filter_params.items():
            if hasattr(media_filter, key):
                setattr(media_filter, key, value)
        
        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = page_size
        pager.pageIndex = page_index
        
        # Execute request
        try:
            result = await self.kaltura_client.execute_request(
                "media", "list",
                filter=media_filter, pager=pager
            )
            
            # Format response
            entries = []
            for entry in result.objects:
                entries.append({
                    "id": entry.id,
                    "name": entry.name,
                    "description": entry.description,
                    "createdAt": entry.createdAt,
                    "updatedAt": entry.updatedAt,
                    "status": entry.status.value,
                    "mediaType": entry.mediaType.value,
                    "duration": entry.duration,
                    "thumbnailUrl": entry.thumbnailUrl,
                })
            
            response = {
                "totalCount": result.totalCount,
                "entries": entries,
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
            logger.error(f"Error listing media entries: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Error listing media entries: {str(e)}"}, indent=2)
                )
            ]
    
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.media.list",
            description="List media entries from Kaltura",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "description": "Filter parameters for media entries",
                        "properties": {
                            "nameLike": {
                                "type": "string",
                                "description": "Free text search on name"
                            },
                            "mediaTypeEqual": {
                                "type": "integer",
                                "description": "Filter by media type (1=video, 2=image, 5=audio)"
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