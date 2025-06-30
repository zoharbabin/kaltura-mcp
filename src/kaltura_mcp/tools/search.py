"""Search and discovery operations - find and organize content."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from KalturaClient.Plugins.Core import (
    KalturaCategoryFilter,
    KalturaFilterPager,
    KalturaMediaEntryFilter,
)
from KalturaClient.Plugins.ElasticSearch import (
    KalturaESearchCaptionFieldName,
    KalturaESearchCaptionItem,
    KalturaESearchCuePointFieldName,
    KalturaESearchCuePointItem,
    KalturaESearchEntryFieldName,
    KalturaESearchEntryItem,
    KalturaESearchEntryMetadataItem,
    KalturaESearchEntryOperator,
    KalturaESearchEntryOrderByFieldName,
    KalturaESearchEntryOrderByItem,
    KalturaESearchEntryParams,
    KalturaESearchItemType,
    KalturaESearchOperatorType,
    KalturaESearchOrderBy,
    KalturaESearchRange,
    KalturaESearchSortOrder,
    KalturaESearchUnifiedItem,
)

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field

logger = logging.getLogger(__name__)


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
        categories.append(
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "tags": category.tags,
                "fullName": category.fullName,
                "depth": category.depth,
                "entriesCount": category.entriesCount,
                "createdAt": datetime.fromtimestamp(category.createdAt).isoformat()
                if category.createdAt
                else None,
            }
        )

    return json.dumps(
        {
            "totalCount": result.totalCount,
            "categories": categories,
        },
        indent=2,
    )


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
        entries.append(
            {
                "id": entry.id,
                "name": entry.name,
                "description": entry.description,
                "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                "createdAt": datetime.fromtimestamp(entry.createdAt).isoformat()
                if entry.createdAt
                else None,
                "duration": entry.duration,
                "tags": entry.tags,
                "thumbnailUrl": entry.thumbnailUrl,
                "plays": entry.plays,
                "views": entry.views,
            }
        )

    return json.dumps(
        {
            "query": query,
            "totalCount": result.totalCount,
            "entries": entries,
        },
        indent=2,
    )


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
                "mediaType": result.object.mediaType.value
                if hasattr(result.object.mediaType, "value")
                else result.object.mediaType,
                "createdAt": datetime.fromtimestamp(result.object.createdAt).isoformat()
                if result.object.createdAt
                else None,
                "duration": result.object.duration,
                "tags": result.object.tags,
                "thumbnailUrl": result.object.thumbnailUrl,
                "plays": result.object.plays,
                "views": result.object.views,
            }

            # Add highlights if available
            if hasattr(result, "highlight") and result.highlight:
                highlights = []
                for highlight in result.highlight:
                    highlight_data = {
                        "fieldName": highlight.fieldName,
                        "hits": [hit.value for hit in highlight.hits] if highlight.hits else [],
                    }
                    highlights.append(highlight_data)
                entry_data["highlights"] = highlights

            # Add items data (for captions, metadata, etc.)
            if hasattr(result, "itemsData") and result.itemsData:
                items_data = []
                for item_data in result.itemsData:
                    item_info = {"totalCount": item_data.totalCount, "items": []}

                    if hasattr(item_data, "items") and item_data.items:
                        for item in item_data.items:
                            item_detail = {}

                            # Handle different item types
                            if hasattr(item, "line"):  # Caption item
                                item_detail.update(
                                    {
                                        "line": item.line,
                                        "startsAt": item.startsAt,
                                        "endsAt": item.endsAt,
                                        "language": item.language,
                                        "captionAssetId": item.captionAssetId,
                                    }
                                )
                            elif hasattr(item, "valueText"):  # Metadata item
                                item_detail.update(
                                    {
                                        "xpath": item.xpath,
                                        "metadataProfileId": item.metadataProfileId,
                                        "metadataFieldId": item.metadataFieldId,
                                        "valueText": item.valueText,
                                    }
                                )

                            # Add highlights for this item
                            if hasattr(item, "highlight") and item.highlight:
                                item_highlights = []
                                for highlight in item.highlight:
                                    item_highlight = {
                                        "fieldName": highlight.fieldName,
                                        "hits": [hit.value for hit in highlight.hits]
                                        if highlight.hits
                                        else [],
                                    }
                                    item_highlights.append(item_highlight)
                                item_detail["highlights"] = item_highlights

                            item_info["items"].append(item_detail)

                    items_data.append(item_info)
                entry_data["itemsData"] = items_data

            entries.append(entry_data)

        return json.dumps(
            {
                "searchTerm": search_term,
                "searchType": search_type,
                "totalCount": search_results.totalCount,
                "entries": entries,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "error": f"eSearch failed: {str(e)}",
                "searchTerm": search_term,
                "searchType": search_type,
            },
            indent=2,
        )


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
        # For wildcard searches, we need to avoid field-specific restrictions
        # Use unified search with a common term that should match most entries
        search_type = "unified"  # Force unified search to avoid field restrictions
        match_type = "partial"  # Use partial matching
        # Use common terms that are likely to appear in most entries (video, audio, or metadata)
        # "e" is the most common letter in English and should match most content
        query = "e"
        specific_field = None  # Clear any specific field to avoid API restrictions

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
            sort_order=sort_order,
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
                    "highlightsEnabled": include_highlights,
                },
                "filters": {
                    "dateRange": date_range,
                    "customMetadata": custom_metadata if custom_metadata else None,
                },
                "results": {
                    "count": len(result_data["entries"]),
                    "totalMatches": result_data.get("totalCount", 0),
                    "maxRequested": max_results,
                },
                "searchCapabilities": {
                    "availableScopes": [
                        "unified (all content)",
                        "entry (metadata)",
                        "caption (transcripts)",
                        "metadata (custom fields)",
                        "cuepoint (temporal markers)",
                    ],
                    "availableMatchTypes": [
                        "partial (contains)",
                        "exact_match (exact phrase)",
                        "starts_with (prefix)",
                        "exists (field has value)",
                        "range (numeric/date)",
                    ],
                    "advancedFeatures": [
                        "highlighting",
                        "boolean operators",
                        "custom metadata search",
                        "date filtering",
                        "field-specific search",
                    ],
                },
            }
            result_data["searchContext"] = search_context

        return json.dumps(result_data, indent=2)

    except Exception as e:
        # If eSearch fails, provide detailed error information
        logger.error(f"eSearch failed: {e}")
        return handle_kaltura_error(
            e,
            "search entries",
            {
                "searchQuery": query,
                "searchType": search_type,
                "suggestion": "Try using simpler parameters or check your search syntax",
            },
        )


# Helper functions - copy exactly as-is
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
