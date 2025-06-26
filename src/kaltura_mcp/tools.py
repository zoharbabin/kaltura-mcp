"""Kaltura API tools implementation."""

import os
import json
import re
import requests
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

from KalturaClient.Plugins.Core import (
    KalturaMediaEntry,
    KalturaMediaListResponse,
    KalturaFilterPager,
    KalturaMediaEntryFilter,
    KalturaCategory,
    KalturaCategoryFilter,
    KalturaAssetFilter,
)

# Try to import Caption plugin for caption assets
try:
    from KalturaClient.Plugins.Caption import (
        KalturaCaptionAssetFilter,
    )
    CAPTION_AVAILABLE = True
except ImportError:
    CAPTION_AVAILABLE = False

# Try to import Attachment plugin for attachment assets
try:
    from KalturaClient.Plugins.Attachment import (
        KalturaAttachmentAssetFilter,
    )
    ATTACHMENT_AVAILABLE = True
except ImportError:
    ATTACHMENT_AVAILABLE = False

# ElasticSearch plugin for eSearch functionality (always available)
from KalturaClient.Plugins.ElasticSearch import (
    KalturaESearchEntryParams,
    KalturaESearchEntryOperator,
    KalturaESearchEntryItem,
    KalturaESearchUnifiedItem,
    KalturaESearchCaptionItem,
    KalturaESearchCuePointItem,
    KalturaESearchEntryMetadataItem,
    KalturaESearchItemType,
    KalturaESearchEntryFieldName,
    KalturaESearchCaptionFieldName,
    KalturaESearchCuePointFieldName,
    KalturaESearchOperatorType,
    KalturaESearchRange,
    KalturaESearchOrderBy,
    KalturaESearchEntryOrderByItem,
    KalturaESearchEntryOrderByFieldName,
    KalturaESearchSortOrder,
)
# Analytics plugin not available in current KalturaClient version

from .kaltura_client import KalturaClientManager


def safe_serialize_kaltura_field(field):
    """Safely serialize Kaltura enum/object fields to JSON-compatible values."""
    if field is None:
        return None
    if hasattr(field, 'value'):
        return field.value
    return str(field)


def handle_kaltura_error(e: Exception, operation: str, context: Dict[str, Any] = None) -> str:
    """Centralized error handling for Kaltura API operations."""
    import traceback
    
    error_context = context or {}
    error_type = type(e).__name__
    
    # Log the error for debugging
    logger.error(f"Kaltura API error in {operation}: {str(e)}", exc_info=True)
    
    # Create detailed error response
    error_response = {
        "error": f"Failed to {operation}: {str(e)}",
        "errorType": error_type,
        "operation": operation,
        **error_context
    }
    
    # Log detailed error for debugging (not exposed to user)
    if os.getenv("KALTURA_DEBUG") == "true":
        logger.debug(f"Detailed traceback for {operation}: {traceback.format_exc()}")
    
    return json.dumps(error_response, indent=2)


def validate_entry_id(entry_id: str) -> bool:
    """Validate Kaltura entry ID format with proper security checks."""
    if not entry_id or not isinstance(entry_id, str):
        return False
    
    # Sanitize input - remove any potentially dangerous characters
    if not re.match(r'^[0-9]+_[a-zA-Z0-9]+$', entry_id):
        return False
    
    # Check length constraints (Kaltura IDs are typically 10-20 chars)
    if len(entry_id) < 3 or len(entry_id) > 50:
        return False
        
    return True


async def list_media_entries(
    manager: KalturaClientManager,
    search_text: Optional[str] = None,
    media_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """List media entries with optional filtering."""
    client = manager.get_client()
    
    # Create filter
    filter = KalturaMediaEntryFilter()
    if search_text:
        filter.freeText = search_text
    
    if media_type:
        media_type_map = {
            "video": KalturaMediaType.VIDEO,
            "audio": KalturaMediaType.AUDIO,
            "image": KalturaMediaType.IMAGE,
        }
        if media_type in media_type_map:
            filter.mediaTypeEqual = media_type_map[media_type]
    
    # Create pager
    pager = KalturaFilterPager()
    pager.pageSize = limit
    pager.pageIndex = offset // limit + 1
    
    # List entries
    result: KalturaMediaListResponse = client.media.list(filter, pager)
    
    entries = []
    for entry in result.objects:
        entries.append({
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "mediaType": safe_serialize_kaltura_field(entry.mediaType),
            "createdAt": datetime.fromtimestamp(entry.createdAt).isoformat() if entry.createdAt else None,
            "duration": entry.duration,
            "tags": entry.tags,
            "thumbnailUrl": entry.thumbnailUrl,
            "downloadUrl": entry.downloadUrl,
            "plays": entry.plays,
            "views": entry.views,
        })
    
    return json.dumps({
        "totalCount": result.totalCount,
        "entries": entries,
        "page": offset // limit + 1,
        "pageSize": limit,
    }, indent=2)


async def get_media_entry(manager: KalturaClientManager, entry_id: str) -> str:
    """Get detailed information about a specific media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    try:
        client = manager.get_client()
        entry: KalturaMediaEntry = client.media.get(entry_id)
    except Exception as e:
        return handle_kaltura_error(e, "get media entry", {"entry_id": entry_id})
    
    return json.dumps({
        "id": entry.id,
        "name": entry.name,
        "description": entry.description,
        "mediaType": safe_serialize_kaltura_field(entry.mediaType),
        "createdAt": datetime.fromtimestamp(entry.createdAt).isoformat() if entry.createdAt else None,
        "updatedAt": datetime.fromtimestamp(entry.updatedAt).isoformat() if entry.updatedAt else None,
        "duration": entry.duration,
        "tags": entry.tags,
        "categories": entry.categories,
        "categoriesIds": entry.categoriesIds,
        "thumbnailUrl": entry.thumbnailUrl,
        "downloadUrl": entry.downloadUrl,
        "plays": entry.plays,
        "views": entry.views,
        "lastPlayedAt": datetime.fromtimestamp(entry.lastPlayedAt).isoformat() if entry.lastPlayedAt else None,
        "width": entry.width,
        "height": entry.height,
        "dataUrl": entry.dataUrl,
        "flavorParamsIds": entry.flavorParamsIds,
        "status": safe_serialize_kaltura_field(entry.status),
    }, indent=2)



async def list_categories(
    manager: KalturaClientManager,
    search_text: Optional[str] = None,
    limit: int = 20,
) -> str:
    """List available categories."""
    client = manager.get_client()
    
    # Create filter
    filter = KalturaCategoryFilter()
    if search_text:
        filter.freeText = search_text
    
    # Create pager
    pager = KalturaFilterPager()
    pager.pageSize = limit
    
    # List categories
    result = client.category.list(filter, pager)
    
    categories = []
    for category in result.objects:
        categories.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "tags": category.tags,
            "fullName": category.fullName,
            "depth": category.depth,
            "entriesCount": category.entriesCount,
            "createdAt": datetime.fromtimestamp(category.createdAt).isoformat() if category.createdAt else None,
        })
    
    return json.dumps({
        "totalCount": result.totalCount,
        "categories": categories,
    }, indent=2)




async def get_analytics(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    entry_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
) -> str:
    """Get analytics data for media entries."""
    # Validate date format
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, from_date) or not re.match(date_pattern, to_date):
        return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"}, indent=2)
    
    if entry_id and not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    # Analytics functionality requires additional setup
    return json.dumps({
        "error": "Analytics functionality requires additional plugin configuration. Please contact your Kaltura administrator to enable analytics.",
        "suggestion": "Use the Kaltura Management Console to view detailed analytics",
        "fromDate": from_date,
        "toDate": to_date,
        "entryId": entry_id,
        "requestedMetrics": metrics or ["plays", "views"],
    }, indent=2)


async def search_entries(
    manager: KalturaClientManager,
    query: str,
    search_in: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    limit: int = 20,
) -> str:
    """Advanced search for media entries using full-text search."""
    client = manager.get_client()
    
    # Create filter
    filter = KalturaMediaEntryFilter()
    
    # Set search fields
    if not search_in or "all" in search_in:
        filter.freeText = query
    else:
        if "name" in search_in:
            filter.nameMultiLikeOr = query
        if "tags" in search_in:
            filter.tagsMultiLikeOr = query
        if "description" in search_in:
            filter.descriptionLike = query
    
    # Set order
    if order_by:
        order_map = {
            "recent": "-createdAt",
            "views": "-views",
            "plays": "-plays",
            "name": "+name",
        }
        filter.orderBy = order_map.get(order_by, "-createdAt")
    
    # Create pager
    pager = KalturaFilterPager()
    pager.pageSize = limit
    
    # Search entries
    result = client.media.list(filter, pager)
    
    entries = []
    for entry in result.objects:
        entries.append({
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "mediaType": safe_serialize_kaltura_field(entry.mediaType),
            "createdAt": datetime.fromtimestamp(entry.createdAt).isoformat() if entry.createdAt else None,
            "duration": entry.duration,
            "tags": entry.tags,
            "thumbnailUrl": entry.thumbnailUrl,
            "plays": entry.plays,
            "views": entry.views,
        })
    
    return json.dumps({
        "query": query,
        "totalCount": result.totalCount,
        "entries": entries,
    }, indent=2)


async def get_download_url(
    manager: KalturaClientManager,
    entry_id: str,
    flavor_id: Optional[str] = None,
) -> str:
    """Get a direct download URL for a media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    try:
        client = manager.get_client()
        
        # Get the entry to verify it exists
        entry = client.media.get(entry_id)
    except Exception as e:
        return handle_kaltura_error(e, "get download URL", {"entry_id": entry_id})
    
    # Get flavor assets
    flavor_filter = KalturaAssetFilter()
    flavor_filter.entryIdEqual = entry_id
    flavors = client.flavorAsset.list(flavor_filter)
    
    if flavor_id:
        # Find specific flavor
        target_flavor = None
        for flavor in flavors.objects:
            if flavor.id == flavor_id:
                target_flavor = flavor
                break
        if not target_flavor:
            return json.dumps({"error": f"Flavor ID {flavor_id} not found for entry {entry_id}"})
    else:
        # Get the source or highest quality flavor
        target_flavor = None
        for flavor in flavors.objects:
            if flavor.isOriginal:
                target_flavor = flavor
                break
        if not target_flavor and flavors.objects:
            target_flavor = flavors.objects[0]
    
    if not target_flavor:
        return json.dumps({"error": "No flavor assets found for this entry"})
    
    # Get download URL
    download_url = client.flavorAsset.getUrl(target_flavor.id)
    
    return json.dumps({
        "entryId": entry_id,
        "entryName": entry.name,
        "flavorId": target_flavor.id,
        "fileSize": target_flavor.size * 1024 if target_flavor.size else None,  # Convert KB to bytes
        "bitrate": target_flavor.bitrate,
        "format": target_flavor.fileExt,
        "downloadUrl": download_url,
    }, indent=2)




async def get_thumbnail_url(
    manager: KalturaClientManager,
    entry_id: str,
    width: int = 120,
    height: int = 90,
    second: int = 5,
) -> str:
    """Get thumbnail URL for a media entry with custom dimensions."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    # Validate numeric parameters
    if width <= 0 or width > 4096 or height <= 0 or height > 4096:
        return json.dumps({"error": "Invalid dimensions: width and height must be between 1 and 4096"}, indent=2)
    
    if second < 0:
        return json.dumps({"error": "Invalid second parameter: must be non-negative"}, indent=2)
    
    try:
        client = manager.get_client()
    except Exception as e:
        return handle_kaltura_error(e, "get thumbnail URL", {"entry_id": entry_id})
    
    # Get the entry to verify it exists
    entry = client.media.get(entry_id)
    
    # Build thumbnail URL with parameters
    base_url = entry.thumbnailUrl
    if not base_url:
        return json.dumps({
            "error": "No thumbnail available for this entry",
            "entryId": entry_id,
        })
    
    # Add parameters for custom thumbnail
    params = []
    if width:
        params.append(f"width={width}")
    if height:
        params.append(f"height={height}")
    if second and entry.mediaType == KalturaMediaType.VIDEO:
        params.append(f"vid_sec={second}")
    
    # Construct URL
    if params:
        separator = "&" if "?" in base_url else "?"
        thumbnail_url = base_url + separator + "&".join(params)
    else:
        thumbnail_url = base_url
    
    return json.dumps({
        "entryId": entry_id,
        "entryName": entry.name,
        "mediaType": safe_serialize_kaltura_field(entry.mediaType),
        "thumbnailUrl": thumbnail_url,
        "width": width,
        "height": height,
        "second": second if entry.mediaType == KalturaMediaType.VIDEO else None,
    }, indent=2)


async def esearch_entries(
    manager: KalturaClientManager,
    search_term: str,
    search_type: str = "unified",
    item_type: str = "partial",
    field_name: Optional[str] = None,
    add_highlight: bool = True,
    operator_type: str = "and",
    metadata_profile_id: Optional[int] = None,
    metadata_xpath: Optional[str] = None,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
    limit: int = 20,
    sort_field: str = "created_at",
    sort_order: str = "desc",
) -> str:
    """Enhanced search using Kaltura eSearch API with advanced capabilities."""
    
    client = manager.get_client()
    
    try:
        # Use the ElasticSearch service through the client
        
        # Create search items based on search type
        search_items = []
        
        if search_type == "unified":
            # Unified search across all entry data
            unified_item = KalturaESearchUnifiedItem()
            unified_item.searchTerm = search_term
            unified_item.itemType = _get_item_type(item_type)
            unified_item.addHighlight = add_highlight
            search_items.append(unified_item)
            
        elif search_type == "entry":
            # Search in specific entry fields
            entry_item = KalturaESearchEntryItem()
            entry_item.searchTerm = search_term
            entry_item.itemType = _get_item_type(item_type)
            entry_item.fieldName = _get_entry_field_name(field_name or "name")
            entry_item.addHighlight = add_highlight
            search_items.append(entry_item)
            
        elif search_type == "caption":
            # Search in captions
            caption_item = KalturaESearchCaptionItem()
            caption_item.searchTerm = search_term
            caption_item.itemType = _get_item_type(item_type)
            caption_item.fieldName = _get_caption_field_name(field_name or "content")
            caption_item.addHighlight = add_highlight
            search_items.append(caption_item)
            
        elif search_type == "metadata":
            # Search in custom metadata
            metadata_item = KalturaESearchEntryMetadataItem()
            metadata_item.searchTerm = search_term
            metadata_item.itemType = _get_item_type(item_type)
            metadata_item.addHighlight = add_highlight
            
            if metadata_profile_id:
                metadata_item.metadataProfileId = metadata_profile_id
            if metadata_xpath:
                metadata_item.xpath = metadata_xpath
                
            search_items.append(metadata_item)
            
        elif search_type == "cuepoint":
            # Search in cue points
            cuepoint_item = KalturaESearchCuePointItem()
            cuepoint_item.searchTerm = search_term
            cuepoint_item.itemType = _get_item_type(item_type)
            cuepoint_item.fieldName = _get_cuepoint_field_name(field_name or "text")
            cuepoint_item.addHighlight = add_highlight
            search_items.append(cuepoint_item)
        
        # Add date range filtering if specified
        if date_range_start and date_range_end:
            try:
                start_timestamp = int(datetime.strptime(date_range_start, "%Y-%m-%d").timestamp())
                end_timestamp = int(datetime.strptime(date_range_end, "%Y-%m-%d").timestamp())
                
                range_item = KalturaESearchRange()
                range_item.greaterThanOrEqual = start_timestamp
                range_item.lessThanOrEqual = end_timestamp
                
                date_item = KalturaESearchEntryItem()
                date_item.itemType = KalturaESearchItemType.RANGE
                date_item.fieldName = KalturaESearchEntryFieldName.CREATED_AT
                date_item.range = range_item
                
                search_items.append(date_item)
            except ValueError:
                return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"})
        
        # Create search operator
        search_operator = KalturaESearchEntryOperator()
        search_operator.operator = _get_operator_type(operator_type)
        search_operator.searchItems = search_items
        
        # Create search parameters
        search_params = KalturaESearchEntryParams()
        search_params.searchOperator = search_operator
        
        # Add sorting
        order_by = KalturaESearchOrderBy()
        order_item = KalturaESearchEntryOrderByItem()
        order_item.sortField = _get_sort_field(sort_field)
        order_item.sortOrder = _get_sort_order(sort_order)
        order_by.orderItems = [order_item]
        search_params.orderBy = order_by
        
        # Add paging
        pager = KalturaFilterPager()
        pager.pageSize = limit
        
        # Execute search using the client's elasticsearch service
        search_results = client.elasticSearch.eSearch.searchEntry(search_params, pager)
        
        # Process results
        entries = []
        for result in search_results.objects:
            entry_data = {
                "id": result.object.id,
                "name": result.object.name,
                "description": result.object.description,
                "mediaType": result.object.mediaType.value if hasattr(result.object.mediaType, 'value') else result.object.mediaType,
                "createdAt": datetime.fromtimestamp(result.object.createdAt).isoformat() if result.object.createdAt else None,
                "duration": result.object.duration,
                "tags": result.object.tags,
                "thumbnailUrl": result.object.thumbnailUrl,
                "plays": result.object.plays,
                "views": result.object.views,
            }
            
            # Add highlights if available
            if hasattr(result, 'highlight') and result.highlight:
                highlights = []
                for highlight in result.highlight:
                    highlight_data = {
                        "fieldName": highlight.fieldName,
                        "hits": [hit.value for hit in highlight.hits] if highlight.hits else []
                    }
                    highlights.append(highlight_data)
                entry_data["highlights"] = highlights
            
            # Add items data (for captions, metadata, etc.)
            if hasattr(result, 'itemsData') and result.itemsData:
                items_data = []
                for item_data in result.itemsData:
                    item_info = {
                        "totalCount": item_data.totalCount,
                        "items": []
                    }
                    
                    if hasattr(item_data, 'items') and item_data.items:
                        for item in item_data.items:
                            item_detail = {}
                            
                            # Handle different item types
                            if hasattr(item, 'line'):  # Caption item
                                item_detail.update({
                                    "line": item.line,
                                    "startsAt": item.startsAt,
                                    "endsAt": item.endsAt,
                                    "language": item.language,
                                    "captionAssetId": item.captionAssetId,
                                })
                            elif hasattr(item, 'valueText'):  # Metadata item
                                item_detail.update({
                                    "xpath": item.xpath,
                                    "metadataProfileId": item.metadataProfileId,
                                    "metadataFieldId": item.metadataFieldId,
                                    "valueText": item.valueText,
                                })
                            
                            # Add highlights for this item
                            if hasattr(item, 'highlight') and item.highlight:
                                item_highlights = []
                                for highlight in item.highlight:
                                    item_highlight = {
                                        "fieldName": highlight.fieldName,
                                        "hits": [hit.value for hit in highlight.hits] if highlight.hits else []
                                    }
                                    item_highlights.append(item_highlight)
                                item_detail["highlights"] = item_highlights
                            
                            item_info["items"].append(item_detail)
                    
                    items_data.append(item_info)
                entry_data["itemsData"] = items_data
            
            entries.append(entry_data)
        
        return json.dumps({
            "searchTerm": search_term,
            "searchType": search_type,
            "totalCount": search_results.totalCount,
            "entries": entries,
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"eSearch failed: {str(e)}",
            "searchTerm": search_term,
            "searchType": search_type,
        }, indent=2)


def _get_item_type(item_type: str):
    """Convert string to KalturaESearchItemType."""
    type_map = {
        "exact_match": KalturaESearchItemType.EXACT_MATCH,
        "partial": KalturaESearchItemType.PARTIAL,
        "starts_with": KalturaESearchItemType.STARTS_WITH,
        "exists": KalturaESearchItemType.EXISTS,
        "range": KalturaESearchItemType.RANGE,
    }
    return type_map.get(item_type, KalturaESearchItemType.PARTIAL)


def _get_entry_field_name(field_name: str):
    """Convert string to KalturaESearchEntryFieldName."""
    field_map = {
        "name": KalturaESearchEntryFieldName.NAME,
        "description": KalturaESearchEntryFieldName.DESCRIPTION,
        "tags": KalturaESearchEntryFieldName.TAGS,
        "created_at": KalturaESearchEntryFieldName.CREATED_AT,
        "updated_at": KalturaESearchEntryFieldName.UPDATED_AT,
        "user_id": KalturaESearchEntryFieldName.USER_ID,
    }
    return field_map.get(field_name, KalturaESearchEntryFieldName.NAME)


def _get_caption_field_name(field_name: str):
    """Convert string to KalturaESearchCaptionFieldName."""
    field_map = {
        "content": KalturaESearchCaptionFieldName.CONTENT,
        "starts_at": KalturaESearchCaptionFieldName.STARTS_AT,
        "ends_at": KalturaESearchCaptionFieldName.ENDS_AT,
        "language": KalturaESearchCaptionFieldName.LANGUAGE,
    }
    return field_map.get(field_name, KalturaESearchCaptionFieldName.CONTENT)


def _get_cuepoint_field_name(field_name: str):
    """Convert string to KalturaESearchCuePointFieldName."""
    field_map = {
        "text": KalturaESearchCuePointFieldName.TEXT,
        "tags": KalturaESearchCuePointFieldName.TAGS,
        "starts_at": KalturaESearchCuePointFieldName.STARTS_AT,
        "ends_at": KalturaESearchCuePointFieldName.ENDS_AT,
    }
    return field_map.get(field_name, KalturaESearchCuePointFieldName.TEXT)


def _get_operator_type(operator_type: str):
    """Convert string to KalturaESearchOperatorType."""
    operator_map = {
        "and": KalturaESearchOperatorType.AND_OP,
        "or": KalturaESearchOperatorType.OR_OP,
        "not": KalturaESearchOperatorType.NOT_OP,
    }
    return operator_map.get(operator_type, KalturaESearchOperatorType.AND_OP)


def _get_sort_field(field_name: str):
    """Convert string to KalturaESearchEntryOrderByFieldName."""
    field_map = {
        "created_at": KalturaESearchEntryOrderByFieldName.CREATED_AT,
        "updated_at": KalturaESearchEntryOrderByFieldName.UPDATED_AT,
        "name": KalturaESearchEntryOrderByFieldName.NAME,
        "views": KalturaESearchEntryOrderByFieldName.VIEWS,
        "plays": KalturaESearchEntryOrderByFieldName.PLAYS,
        "last_played_at": KalturaESearchEntryOrderByFieldName.LAST_PLAYED_AT,
        "rank": KalturaESearchEntryOrderByFieldName.RANK,
        "start_date": KalturaESearchEntryOrderByFieldName.START_DATE,
        "end_date": KalturaESearchEntryOrderByFieldName.END_DATE,
    }
    return field_map.get(field_name, KalturaESearchEntryOrderByFieldName.CREATED_AT)


def _get_sort_order(sort_order: str):
    """Convert string to KalturaESearchSortOrder."""
    order_map = {
        "asc": KalturaESearchSortOrder.ORDER_BY_ASC,
        "desc": KalturaESearchSortOrder.ORDER_BY_DESC,
    }
    return order_map.get(sort_order, KalturaESearchSortOrder.ORDER_BY_DESC)


async def search_entries_intelligent(
    manager: KalturaClientManager,
    query: str,
    search_type: str = "unified",
    match_type: str = "partial", 
    specific_field: Optional[str] = None,
    boolean_operator: str = "and",
    include_highlights: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
    date_range: Optional[Dict[str, str]] = None,
    max_results: int = 20,
    sort_field: str = "created_at",
    sort_order: str = "desc",
) -> str:
    """
    Advanced search function that exposes the full power of Kaltura's eSearch API.
    
    This is the PRIMARY tool for finding and listing media entries. Use this for:
    - General searches with keywords
    - Listing all entries (query="*")
    - Filtering by date ranges, content types, fields
    - Searching in transcripts, metadata, or specific fields
    - Complex boolean queries with multiple criteria
    
    This function provides access to all eSearch capabilities while maintaining
    clear parameter naming and comprehensive documentation for LLM usage.
    """
    
    # Validate and cap max_results
    max_results = min(max_results, 100)
    
    # Handle special case for listing all entries
    if query == "*":
        # For "list all" queries, use "exists" match on the entry ID field
        # This efficiently returns all entries without text matching
        if search_type == "unified":
            search_type = "entry"
        if not specific_field:
            specific_field = "id"
        match_type = "exists"
        query = ""  # Empty query for exists matching
    
    # Extract date range if provided
    date_after = None
    date_before = None
    if date_range:
        date_after = date_range.get("after")
        date_before = date_range.get("before")
    
    # Extract custom metadata parameters
    metadata_profile_id = None
    metadata_xpath = None
    if custom_metadata:
        metadata_profile_id = custom_metadata.get("profile_id")
        metadata_xpath = custom_metadata.get("xpath")
    
    # Call the underlying eSearch function with all parameters
    try:
        result = await esearch_entries(
            manager=manager,
            search_term=query,
            search_type=search_type,
            item_type=match_type,
            field_name=specific_field,
            add_highlight=include_highlights,
            operator_type=boolean_operator,
            metadata_profile_id=metadata_profile_id,
            metadata_xpath=metadata_xpath,
            date_range_start=date_after,
            date_range_end=date_before,
            limit=max_results,
            sort_field=sort_field,
            sort_order=sort_order
        )
        
        # Parse the result to add comprehensive search context
        import json
        result_data = json.loads(result)
        
        # Add detailed search context information
        if "entries" in result_data:
            # Determine operation type
            original_query = query if query else "*"
            operation_type = "list_all" if original_query == "*" else "search"
            
            search_context = {
                "searchQuery": original_query,
                "operationType": operation_type,
                "searchConfiguration": {
                    "scope": search_type,
                    "matchType": match_type,
                    "specificField": specific_field,
                    "booleanOperator": boolean_operator,
                    "highlightsEnabled": include_highlights
                },
                "filters": {
                    "dateRange": date_range,
                    "customMetadata": custom_metadata if custom_metadata else None
                },
                "results": {
                    "count": len(result_data["entries"]),
                    "totalMatches": result_data.get("totalCount", 0),
                    "maxRequested": max_results
                },
                "searchCapabilities": {
                    "availableScopes": ["unified (all content)", "entry (metadata)", "caption (transcripts)", "metadata (custom fields)", "cuepoint (temporal markers)"],
                    "availableMatchTypes": ["partial (contains)", "exact_match (exact phrase)", "starts_with (prefix)", "exists (field has value)", "range (numeric/date)"],
                    "advancedFeatures": ["highlighting", "boolean operators", "custom metadata search", "date filtering", "field-specific search"]
                }
            }
            result_data["searchContext"] = search_context
        
        return json.dumps(result_data, indent=2)
        
    except Exception as e:
        # If eSearch fails, provide detailed error information
        logger.error(f"eSearch failed: {e}")
        return handle_kaltura_error(e, "search entries", {
            "searchQuery": query,
            "searchType": search_type,
            "suggestion": "Try using simpler parameters or check your search syntax"
        })


async def list_caption_assets(
    manager: KalturaClientManager,
    entry_id: str,
) -> str:
    """List all caption assets for a media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    if not CAPTION_AVAILABLE:
        return json.dumps({
            "error": "Caption functionality is not available. The Caption plugin is not installed.",
            "entryId": entry_id,
        }, indent=2)
    
    client = manager.get_client()
    
    try:
        # Create filter for caption assets
        filter = KalturaCaptionAssetFilter()
        filter.entryIdEqual = entry_id
        
        # List caption assets
        result = client.caption.captionAsset.list(filter)
        
        captions = []
        for caption in result.objects:
            caption_data = {
                "id": getattr(caption, 'id', None),
                "entryId": getattr(caption, 'entryId', None),
                "language": safe_serialize_kaltura_field(getattr(caption, 'language', None)),
                "languageCode": safe_serialize_kaltura_field(getattr(caption, 'languageCode', None)),
                "label": getattr(caption, 'label', None),
                "format": safe_serialize_kaltura_field(getattr(caption, 'format', None)),
                "status": safe_serialize_kaltura_field(getattr(caption, 'status', None)),
                "fileExt": getattr(caption, 'fileExt', None),
                "size": getattr(caption, 'size', None),
                "createdAt": datetime.fromtimestamp(caption.createdAt).isoformat() if caption.createdAt else None,
                "updatedAt": datetime.fromtimestamp(caption.updatedAt).isoformat() if caption.updatedAt else None,
                "accuracy": getattr(caption, 'accuracy', None),
                "isDefault": safe_serialize_kaltura_field(getattr(caption, 'isDefault', None)),
            }
            captions.append(caption_data)
        
        return json.dumps({
            "entryId": entry_id,
            "totalCount": result.totalCount,
            "captionAssets": captions,
        }, indent=2)
        
    except Exception as e:
        return handle_kaltura_error(e, "list caption assets", {"entryId": entry_id})


async def get_caption_content(
    manager: KalturaClientManager,
    caption_asset_id: str,
) -> str:
    """Get the actual text content of a caption asset."""
    
    if not CAPTION_AVAILABLE:
        return json.dumps({
            "error": "Caption functionality is not available. The Caption plugin is not installed.",
            "captionAssetId": caption_asset_id,
        }, indent=2)
    
    client = manager.get_client()
    
    try:
        # Get caption asset details
        caption_asset = client.caption.captionAsset.get(caption_asset_id)
        
        # Get the caption content URL
        content_url = client.caption.captionAsset.getUrl(caption_asset_id)
        
        # Validate URL before making request
        if not content_url or not isinstance(content_url, str):
            download_error = "Invalid or missing caption URL"
            caption_text = None
        elif not content_url.startswith(('http://', 'https://')):
            download_error = "Caption URL must use HTTP or HTTPS protocol"
            caption_text = None
        else:
            # Download the actual caption content
            caption_text = None
            download_error = None
            
            try:
                # Create a session for downloading
                session = requests.Session()
                
                # Set headers similar to reference implementation
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # Download the caption content with timeout
                response = session.get(content_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Get the text content
                caption_text = response.text
                
            except requests.exceptions.RequestException as e:
                download_error = f"Failed to download caption content: {str(e)}"
            except Exception as e:
                download_error = f"Error processing caption content: {str(e)}"
        
        result = {
            "captionAssetId": caption_asset_id,
            "entryId": caption_asset.entryId,
            "language": caption_asset.language.value if hasattr(caption_asset.language, 'value') else str(caption_asset.language),
            "label": caption_asset.label,
            "format": caption_asset.format.value if hasattr(caption_asset.format, 'value') else str(caption_asset.format),
            "contentUrl": content_url,
            "size": caption_asset.size,
            "accuracy": caption_asset.accuracy,
        }
        
        if caption_text is not None:
            result["captionText"] = caption_text
            result["textLength"] = len(caption_text)
            result["note"] = "Caption text content has been successfully downloaded and included."
        else:
            result["downloadError"] = download_error
            result["note"] = "Caption asset details retrieved but text content could not be downloaded. Use contentUrl for manual download."
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get caption content: {str(e)}",
            "captionAssetId": caption_asset_id,
        }, indent=2)


async def list_attachment_assets(
    manager: KalturaClientManager,
    entry_id: str,
) -> str:
    """List all attachment assets for a media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)
    
    if not ATTACHMENT_AVAILABLE:
        return json.dumps({
            "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
            "entryId": entry_id,
        }, indent=2)
    
    client = manager.get_client()
    
    try:
        # Create filter for attachment assets
        filter = KalturaAttachmentAssetFilter()
        filter.entryIdEqual = entry_id
        
        # List attachment assets
        result = client.attachment.attachmentAsset.list(filter)
        
        attachments = []
        for attachment in result.objects:
            attachment_data = {
                "id": attachment.id,
                "entryId": attachment.entryId,
                "filename": attachment.filename,
                "title": attachment.title,
                "format": attachment.format.value if hasattr(attachment.format, 'value') else str(attachment.format),
                "status": attachment.status.value if hasattr(attachment.status, 'value') else str(attachment.status),
                "fileExt": attachment.fileExt,
                "size": attachment.size,
                "createdAt": datetime.fromtimestamp(attachment.createdAt).isoformat() if attachment.createdAt else None,
                "updatedAt": datetime.fromtimestamp(attachment.updatedAt).isoformat() if attachment.updatedAt else None,
                "description": attachment.description,
                "tags": attachment.tags,
            }
            attachments.append(attachment_data)
        
        return json.dumps({
            "entryId": entry_id,
            "totalCount": result.totalCount,
            "attachmentAssets": attachments,
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to list attachment assets: {str(e)}",
            "entryId": entry_id,
        }, indent=2)


async def get_attachment_content(
    manager: KalturaClientManager,
    attachment_asset_id: str,
) -> str:
    """Get download URL and details for an attachment asset."""
    
    if not ATTACHMENT_AVAILABLE:
        return json.dumps({
            "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
            "attachmentAssetId": attachment_asset_id,
        }, indent=2)
    
    client = manager.get_client()
    
    try:
        # Get attachment asset details
        attachment_asset = client.attachment.attachmentAsset.get(attachment_asset_id)
        
        # Get the attachment download URL
        download_url = client.attachment.attachmentAsset.getUrl(attachment_asset_id)
        
        # Validate URL before making request
        if not download_url or not isinstance(download_url, str):
            return json.dumps({
                "error": "Invalid or missing attachment download URL",
                "attachmentAssetId": attachment_asset_id,
            }, indent=2)
        elif not download_url.startswith(('http://', 'https://')):
            return json.dumps({
                "error": "Attachment URL must use HTTP or HTTPS protocol",
                "attachmentAssetId": attachment_asset_id,
            }, indent=2)
        
        # Download the actual attachment content
        attachment_content = None
        download_error = None
        
        try:
            # Create a session for downloading
            session = requests.Session()
            
            # Set headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Download the attachment content with timeout
            response = session.get(download_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Encode content as base64
            import base64
            attachment_content = base64.b64encode(response.content).decode('utf-8')
            
        except requests.exceptions.RequestException as e:
            download_error = f"Failed to download attachment content: {str(e)}"
        except Exception as e:
            download_error = f"Error processing attachment content: {str(e)}"
        
        result = {
            "attachmentAssetId": attachment_asset_id,
            "entryId": attachment_asset.entryId,
            "filename": attachment_asset.filename,
            "title": attachment_asset.title,
            "format": attachment_asset.format.value if hasattr(attachment_asset.format, 'value') else str(attachment_asset.format),
            "downloadUrl": download_url,
            "size": attachment_asset.size,
            "description": attachment_asset.description,
            "tags": attachment_asset.tags,
        }
        
        if download_error:
            result["downloadError"] = download_error
            result["note"] = "Failed to download content automatically. You can try the downloadUrl manually."
        else:
            result["content"] = attachment_content
            result["contentEncoding"] = "base64"
            result["note"] = "Content downloaded and encoded as base64"
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get attachment content: {str(e)}",
            "attachmentAssetId": attachment_asset_id,
        }, indent=2)