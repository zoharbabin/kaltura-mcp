"""Asset operations - captions, attachments, and supplementary content."""

import json
from datetime import datetime

import requests

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field, validate_entry_id

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


async def list_caption_assets(
    manager: KalturaClientManager,
    entry_id: str,
) -> str:
    """List all caption assets for a media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    if not CAPTION_AVAILABLE:
        return json.dumps(
            {
                "error": "Caption functionality is not available. The Caption plugin is not installed.",
                "entryId": entry_id,
            },
            indent=2,
        )

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
                "id": getattr(caption, "id", None),
                "entryId": getattr(caption, "entryId", None),
                "language": safe_serialize_kaltura_field(getattr(caption, "language", None)),
                "languageCode": safe_serialize_kaltura_field(
                    getattr(caption, "languageCode", None)
                ),
                "label": getattr(caption, "label", None),
                "format": safe_serialize_kaltura_field(getattr(caption, "format", None)),
                "status": safe_serialize_kaltura_field(getattr(caption, "status", None)),
                "fileExt": getattr(caption, "fileExt", None),
                "size": getattr(caption, "size", None),
                "createdAt": datetime.fromtimestamp(caption.createdAt).isoformat()
                if caption.createdAt
                else None,
                "updatedAt": datetime.fromtimestamp(caption.updatedAt).isoformat()
                if caption.updatedAt
                else None,
                "accuracy": getattr(caption, "accuracy", None),
                "isDefault": safe_serialize_kaltura_field(getattr(caption, "isDefault", None)),
            }
            captions.append(caption_data)

        return json.dumps(
            {
                "entryId": entry_id,
                "totalCount": result.totalCount,
                "captionAssets": captions,
            },
            indent=2,
        )

    except Exception as e:
        return handle_kaltura_error(e, "list caption assets", {"entryId": entry_id})


async def get_caption_content(
    manager: KalturaClientManager,
    caption_asset_id: str,
) -> str:
    """Get the actual text content of a caption asset."""

    if not CAPTION_AVAILABLE:
        return json.dumps(
            {
                "error": "Caption functionality is not available. The Caption plugin is not installed.",
                "captionAssetId": caption_asset_id,
            },
            indent=2,
        )

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
        elif not content_url.startswith(("http://", "https://")):
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
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
            "language": caption_asset.language.value
            if hasattr(caption_asset.language, "value")
            else str(caption_asset.language),
            "label": caption_asset.label,
            "format": caption_asset.format.value
            if hasattr(caption_asset.format, "value")
            else str(caption_asset.format),
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
            result[
                "note"
            ] = "Caption asset details retrieved but text content could not be downloaded. Use contentUrl for manual download."

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to get caption content: {str(e)}",
                "captionAssetId": caption_asset_id,
            },
            indent=2,
        )


async def list_attachment_assets(
    manager: KalturaClientManager,
    entry_id: str,
) -> str:
    """List all attachment assets for a media entry."""
    if not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    if not ATTACHMENT_AVAILABLE:
        return json.dumps(
            {
                "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
                "entryId": entry_id,
            },
            indent=2,
        )

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
                "format": attachment.format.value
                if hasattr(attachment.format, "value")
                else str(attachment.format),
                "status": attachment.status.value
                if hasattr(attachment.status, "value")
                else str(attachment.status),
                "fileExt": attachment.fileExt,
                "size": attachment.size,
                "createdAt": datetime.fromtimestamp(attachment.createdAt).isoformat()
                if attachment.createdAt
                else None,
                "updatedAt": datetime.fromtimestamp(attachment.updatedAt).isoformat()
                if attachment.updatedAt
                else None,
                "description": attachment.description,
                "tags": attachment.tags,
            }
            attachments.append(attachment_data)

        return json.dumps(
            {
                "entryId": entry_id,
                "totalCount": result.totalCount,
                "attachmentAssets": attachments,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to list attachment assets: {str(e)}",
                "entryId": entry_id,
            },
            indent=2,
        )


async def get_attachment_content(
    manager: KalturaClientManager,
    attachment_asset_id: str,
) -> str:
    """Get download URL and details for an attachment asset."""

    if not ATTACHMENT_AVAILABLE:
        return json.dumps(
            {
                "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
                "attachmentAssetId": attachment_asset_id,
            },
            indent=2,
        )

    client = manager.get_client()

    try:
        # Get attachment asset details
        attachment_asset = client.attachment.attachmentAsset.get(attachment_asset_id)

        # Get the attachment download URL
        download_url = client.attachment.attachmentAsset.getUrl(attachment_asset_id)

        # Validate URL before making request
        if not download_url or not isinstance(download_url, str):
            return json.dumps(
                {
                    "error": "Invalid or missing attachment download URL",
                    "attachmentAssetId": attachment_asset_id,
                },
                indent=2,
            )
        elif not download_url.startswith(("http://", "https://")):
            return json.dumps(
                {
                    "error": "Attachment URL must use HTTP or HTTPS protocol",
                    "attachmentAssetId": attachment_asset_id,
                },
                indent=2,
            )

        # Download the actual attachment content
        attachment_content = None
        download_error = None

        try:
            # Create a session for downloading
            session = requests.Session()

            # Set headers
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            # Download the attachment content with timeout
            response = session.get(download_url, headers=headers, timeout=30)
            response.raise_for_status()

            # Encode content as base64
            import base64

            attachment_content = base64.b64encode(response.content).decode("utf-8")

        except requests.exceptions.RequestException as e:
            download_error = f"Failed to download attachment content: {str(e)}"
        except Exception as e:
            download_error = f"Error processing attachment content: {str(e)}"

        result = {
            "attachmentAssetId": attachment_asset_id,
            "entryId": attachment_asset.entryId,
            "filename": attachment_asset.filename,
            "title": attachment_asset.title,
            "format": attachment_asset.format.value
            if hasattr(attachment_asset.format, "value")
            else str(attachment_asset.format),
            "downloadUrl": download_url,
            "size": attachment_asset.size,
            "description": attachment_asset.description,
            "tags": attachment_asset.tags,
        }

        if download_error:
            result["downloadError"] = download_error
            result[
                "note"
            ] = "Failed to download content automatically. You can try the downloadUrl manually."
        else:
            result["content"] = attachment_content
            result["contentEncoding"] = "base64"
            result["note"] = "Content downloaded and encoded as base64"

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to get attachment content: {str(e)}",
                "attachmentAssetId": attachment_asset_id,
            },
            indent=2,
        )
