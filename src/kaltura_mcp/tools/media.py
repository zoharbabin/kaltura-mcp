"""Core media entry operations - the heart of Kaltura management."""

import json
from datetime import datetime
from typing import Optional

from KalturaClient.Plugins.Core import (
    KalturaAssetFilter,
    KalturaFilterPager,
    KalturaMediaEntry,
    KalturaMediaEntryFilter,
    KalturaMediaListResponse,
    KalturaMediaType,
)

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field, validate_entry_id


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
                "downloadUrl": entry.downloadUrl,
                "plays": entry.plays,
                "views": entry.views,
            }
        )

    return json.dumps(
        {
            "totalCount": result.totalCount,
            "entries": entries,
            "page": offset // limit + 1,
            "pageSize": limit,
        },
        indent=2,
    )


async def get_media_entry(manager: KalturaClientManager, entry_id: str) -> str:
    """Get detailed information about a specific media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    try:
        client = manager.get_client()
        entry: KalturaMediaEntry = client.media.get(entry_id)
    except Exception as e:
        return handle_kaltura_error(e, "get media entry", {"entry_id": entry_id})

    return json.dumps(
        {
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "mediaType": safe_serialize_kaltura_field(entry.mediaType),
            "createdAt": datetime.fromtimestamp(entry.createdAt).isoformat()
            if entry.createdAt
            else None,
            "updatedAt": datetime.fromtimestamp(entry.updatedAt).isoformat()
            if entry.updatedAt
            else None,
            "duration": entry.duration,
            "tags": entry.tags,
            "categories": entry.categories,
            "categoriesIds": entry.categoriesIds,
            "thumbnailUrl": entry.thumbnailUrl,
            "downloadUrl": entry.downloadUrl,
            "plays": entry.plays,
            "views": entry.views,
            "lastPlayedAt": datetime.fromtimestamp(entry.lastPlayedAt).isoformat()
            if entry.lastPlayedAt
            else None,
            "width": entry.width,
            "height": entry.height,
            "dataUrl": entry.dataUrl,
            "flavorParamsIds": entry.flavorParamsIds,
            "status": safe_serialize_kaltura_field(entry.status),
        },
        indent=2,
    )


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

    return json.dumps(
        {
            "entryId": entry_id,
            "entryName": entry.name,
            "flavorId": target_flavor.id,
            "fileSize": target_flavor.size * 1024
            if target_flavor.size
            else None,  # Convert KB to bytes
            "bitrate": target_flavor.bitrate,
            "format": target_flavor.fileExt,
            "downloadUrl": download_url,
        },
        indent=2,
    )


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
        return json.dumps(
            {"error": "Invalid dimensions: width and height must be between 1 and 4096"}, indent=2
        )

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
        return json.dumps(
            {
                "error": "No thumbnail available for this entry",
                "entryId": entry_id,
            }
        )

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

    return json.dumps(
        {
            "entryId": entry_id,
            "entryName": entry.name,
            "mediaType": safe_serialize_kaltura_field(entry.mediaType),
            "thumbnailUrl": thumbnail_url,
            "width": width,
            "height": height,
            "second": second if entry.mediaType == KalturaMediaType.VIDEO else None,
        },
        indent=2,
    )
