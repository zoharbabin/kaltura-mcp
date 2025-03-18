"""
Enhanced media-related tool handlers for Kaltura MCP Server.

This module provides an enhanced implementation of the media upload tool
that supports chunked uploading, automatic file type detection, and
handling of various file formats including media, documents, and data files.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Union

import mcp.types as types
from KalturaClient.Plugins.Core import (
    KalturaDataEntry,
    KalturaMediaEntry,
    KalturaUploadedFileTokenResource,
)
from KalturaClient.Plugins.Document import (
    KalturaDocumentEntry,
)

from kaltura_mcp.tools.base import KalturaJSONEncoder, KalturaToolHandler
from kaltura_mcp.utils.chunked_uploader import ChunkedUploader, TokenNotFinalizedError
from kaltura_mcp.utils.mime_utils import (
    get_document_type,
    get_media_type,
    guess_kaltura_entry_type,
    guess_mime_type,
)

logger = logging.getLogger(__name__)


class EnhancedMediaUploadToolHandler(KalturaToolHandler):
    """
    Enhanced handler for the kaltura.media.upload tool.

    This handler provides a robust implementation for uploading files to Kaltura
    with support for various file types and advanced features:

    Features:
    - Chunked uploading with adaptive chunk sizing for efficient handling of large files
    - MIME type detection for accurate file type handling (using python-magic if available)
    - Support for media (video, audio, image), document (PDF, Office, etc.), and data entry types
    - Proper error handling and retries for network issues
    - Category assignment for uploaded entries
    - Configurable chunk size and adaptive chunking parameters

    This implementation replaces the original MediaUploadToolHandler with a more
    robust and feature-rich solution based on the kaltura_uploader library.
    """

    async def handle(
        self, arguments: Dict[str, Any]
    ) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """
        Handle a media upload request.

        This method processes the upload request by:
        1. Validating the input parameters
        2. Detecting the file type
        3. Uploading the file in chunks
        4. Creating the appropriate entry type
        5. Optionally assigning a category
        6. Returning the entry details

        Args:
            arguments: Dictionary of arguments for the upload
                Required:
                - file_path: Path to the file to upload
                - name: Name of the entry
                Optional:
                - description: Description of the entry
                - tags: Comma-separated list of tags
                - access_control_id: Access control ID
                - conversion_profile_id: Conversion profile ID
                - category_id: Category ID to assign
                - chunk_size_kb: Initial chunk size in KB
                - adaptive_chunking: Whether to use adaptive chunking
                - verbose: Enable verbose logging

        Returns:
            List containing a TextContent object with the JSON response
        """
        # Validate required parameters
        self._validate_required_params(arguments, ["file_path", "name"])

        file_path = arguments["file_path"]
        name = arguments["name"]
        description = arguments.get("description", "")
        tags = arguments.get("tags", "")

        # Optional parameters
        access_control_id = arguments.get("access_control_id", 0)
        conversion_profile_id = arguments.get("conversion_profile_id", 0)
        category_id = arguments.get("category_id", 0)

        # Chunked upload parameters
        chunk_size_kb = arguments.get("chunk_size_kb", 2048)
        adaptive_chunking = arguments.get("adaptive_chunking", True)
        verbose = arguments.get("verbose", False)

        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File '{file_path}' does not exist.")
            if not os.path.isfile(file_path):
                raise ValueError(f"Path '{file_path}' is not a valid file.")

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError(f"File '{file_path}' is empty. Aborting upload.")

            # Determine entry type based on file content
            entry_type = guess_kaltura_entry_type(file_path)
            mime_type = guess_mime_type(file_path)

            logger.info(f"Uploading file '{file_path}' ({file_size} bytes) as {entry_type} entry")
            logger.info(f"Detected MIME type: {mime_type}")

            # Create chunked uploader
            uploader = ChunkedUploader(
                self.kaltura_client,
                chunk_size_kb=chunk_size_kb,
                adaptive_chunking=adaptive_chunking,
                verbose=verbose,
            )

            # Upload the file and get token ID
            try:
                upload_token_id = await uploader.upload_file(file_path)
                logger.info(f"File uploaded successfully with token ID: {upload_token_id}")
            except TokenNotFinalizedError as e:
                logger.error(f"Upload token could not be finalized: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": f"Upload failed: {str(e)}",
                                "details": "The upload token could not be finalized. The file may be partially uploaded.",
                            },
                            indent=2,
                        ),
                    )
                ]
            except Exception as e:
                logger.error(f"Error during file upload: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": f"Upload failed: {str(e)}",
                                "details": "An error occurred during the file upload process.",
                            },
                            indent=2,
                        ),
                    )
                ]

            # Create the appropriate entry type based on the file
            try:
                if entry_type == "media":
                    entry = await self._create_media_entry(
                        upload_token_id,
                        file_path,
                        name,
                        description,
                        tags,
                        access_control_id,
                        conversion_profile_id,
                    )
                    logger.info(f"Created media entry object: {type(entry)}")
                    if isinstance(entry, str):
                        entry_id = entry
                        logger.warning(f"Entry is a string, not an object: '{entry}'")
                        if not entry_id:
                            logger.error("Entry ID is empty string")
                            raise ValueError("Entry ID cannot be empty")
                    elif hasattr(entry, "id"):
                        entry_id = entry.id
                        logger.info(f"Created media entry with ID: {entry_id}")
                        if not entry_id:
                            logger.error("Entry ID is empty even though entry has id attribute")
                            raise ValueError("Entry ID cannot be empty")
                    else:
                        logger.error(f"Entry has no ID attribute: {entry}")
                        raise ValueError(f"Entry has no ID attribute: {entry}")
                elif entry_type == "document":
                    entry = await self._create_document_entry(
                        upload_token_id,
                        file_path,
                        name,
                        description,
                        tags,
                        mime_type,
                        access_control_id,
                        conversion_profile_id,
                    )
                    logger.info(f"Created document entry object: {type(entry)}")
                    if isinstance(entry, str):
                        entry_id = entry
                        logger.warning(f"Entry is a string, not an object: '{entry}'")
                        if not entry_id:
                            logger.error("Entry ID is empty string")
                            raise ValueError("Entry ID cannot be empty")
                    elif hasattr(entry, "id"):
                        entry_id = entry.id
                        logger.info(f"Created document entry with ID: {entry_id}")
                        if not entry_id:
                            logger.error("Entry ID is empty even though entry has id attribute")
                            raise ValueError("Entry ID cannot be empty")
                    else:
                        logger.error(f"Entry has no ID attribute: {entry}")
                        raise ValueError(f"Entry has no ID attribute: {entry}")
                else:
                    # Default to data entry
                    # For data entries, we need to be more careful
                    try:
                        entry = await self._create_data_entry(
                            upload_token_id, file_path, name, description, tags, access_control_id
                        )
                        logger.info(f"Created data entry object: {type(entry)}")

                        # Verify we have a valid entry with ID
                        if isinstance(entry, str):
                            entry_id = entry
                            logger.warning(f"Entry is a string, not an object: '{entry}'")
                            if not entry_id:
                                logger.error("Entry ID is empty string")
                                raise ValueError("Entry ID cannot be empty")
                        elif hasattr(entry, "id"):
                            entry_id = entry.id
                            logger.info(f"Created data entry with ID: {entry_id}")
                            if not entry_id:
                                logger.error("Entry ID is empty even though entry has id attribute")
                                raise ValueError("Entry ID cannot be empty")
                        else:
                            logger.error(f"Entry has no ID attribute: {entry}")
                            raise ValueError(f"Entry has no ID attribute: {entry}")

                        # For data entries, verify the entry exists by trying to get it
                        # This helps ensure the entry is fully created before proceeding
                        max_retries = 3
                        retry_delay = 2

                        for retry in range(max_retries):
                            try:
                                logger.info(f"Verifying data entry exists (attempt {retry+1}/{max_retries})")
                                verification = await self.kaltura_client.execute_request("data", "get", entryId=entry_id)
                                if verification and hasattr(verification, "id"):
                                    logger.info(f"Data entry verified with ID: {verification.id}")
                                    break
                                else:
                                    raise ValueError("Data entry verification returned invalid result")
                            except Exception as e:
                                logger.warning(f"Data entry verification attempt {retry+1} failed: {e}")
                                if retry < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                                    retry_delay *= 2  # Exponential backoff
                                else:
                                    logger.error(f"Data entry verification failed after {max_retries} attempts")
                                    # Continue anyway, the entry might still be valid
                    except Exception as e:
                        logger.error(f"Error in data entry creation or verification: {e}")
                        raise
            except Exception as e:
                logger.error(f"Error creating entry: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": f"Entry creation failed: {str(e)}",
                                "details": "The file was uploaded but creating the entry failed.",
                                "upload_token_id": upload_token_id,
                            },
                            indent=2,
                        ),
                    )
                ]

            # Optionally assign category
            if category_id > 0:
                try:
                    await self._assign_category(entry_id, category_id)
                    logger.info(f"Assigned entry {entry_id} to category {category_id}")
                except Exception as e:
                    logger.warning(f"Failed to assign category: {e}")
                    # Continue even if category assignment fails

            # Get the entry details
            try:
                # Always fetch the entry details to ensure we have the latest data
                logger.info(f"Fetching entry details for ID: {entry_id}")
                entry_details = await self._get_entry_details(entry_id, entry_type)

                # Format response
                response = {
                    "id": entry_id,
                    "name": name,
                    "description": description,
                    "entryType": entry_type,
                    "mimeType": mime_type,
                    "uploadedFileSize": file_size,
                    "status": (entry_details.status.value if hasattr(entry_details, "status") else None),
                    "createdAt": (entry_details.createdAt if hasattr(entry_details, "createdAt") else None),
                    "message": f"{entry_type.capitalize()} entry created successfully",
                }

                # Add media-specific fields
                if entry_type == "media" and hasattr(entry_details, "mediaType"):
                    response["mediaType"] = entry_details.mediaType.value
                    response["duration"] = entry_details.duration if hasattr(entry_details, "duration") else None
                    response["thumbnailUrl"] = entry_details.thumbnailUrl if hasattr(entry_details, "thumbnailUrl") else None

                return [types.TextContent(type="text", text=json.dumps(response, indent=2, cls=KalturaJSONEncoder))]
            except Exception as e:
                logger.error(f"Error getting entry details: {e}")
                # Return a basic success response even if getting details fails
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "id": entry_id,
                                "name": name,
                                "entryType": entry_type,
                                "message": f"{entry_type.capitalize()} entry created successfully",
                                "warning": "Could not retrieve full entry details",
                            },
                            indent=2,
                        ),
                    )
                ]

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": f"File not found: {str(e)}",
                            "details": "The specified file does not exist.",
                        },
                        indent=2,
                    ),
                )
            ]
        except ValueError as e:
            logger.error(f"Invalid input: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": f"Invalid input: {str(e)}",
                            "details": "The provided parameters are invalid.",
                        },
                        indent=2,
                    ),
                )
            ]
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": f"Error uploading file: {str(e)}",
                            "details": "An unexpected error occurred during the upload process.",
                        },
                        indent=2,
                    ),
                )
            ]

    async def _create_media_entry(
        self,
        upload_token_id: str,
        file_path: str,
        name: str,
        description: str,
        tags: str,
        access_control_id: int = 0,
        conversion_profile_id: int = 0,
    ):
        """
        Create a KalturaMediaEntry using the uploaded file.

        Args:
            upload_token_id: The ID of the upload token
            file_path: Path to the file (for media type detection)
            name: Name of the entry
            description: Description of the entry
            tags: Comma-separated list of tags
            access_control_id: Optional access control ID
            conversion_profile_id: Optional conversion profile ID

        Returns:
            Entry ID
        """
        # Determine media type
        media_type = get_media_type(file_path)

        # Create media entry
        entry = KalturaMediaEntry()
        entry.name = name
        entry.description = description
        entry.mediaType = media_type
        entry.tags = tags

        if access_control_id > 0:
            entry.accessControlId = access_control_id
        if conversion_profile_id > 0:
            entry.conversionProfileId = conversion_profile_id

        # Add the entry
        try:
            media_entry = await self.kaltura_client.execute_request("media", "add", entry=entry)

            if not hasattr(media_entry, "id") or not media_entry.id:
                logger.error("Media entry created without valid ID")
                raise ValueError("Media entry created without valid ID")

            logger.info(f"Created media entry with ID: {media_entry.id}")

            # Attach the uploaded file to the media entry
            resource = KalturaUploadedFileTokenResource()
            resource.token = upload_token_id

            final_entry = await self.kaltura_client.execute_request(
                "media", "addContent", entryId=media_entry.id, resource=resource
            )

            if not hasattr(final_entry, "id") or not final_entry.id:
                logger.error("Final media entry has no valid ID")
                # If final_entry has no ID, return the original media_entry which should have an ID
                return media_entry

            return final_entry
        except Exception as e:
            logger.error(f"Error in _create_media_entry: {e}")
            raise

    async def _create_document_entry(
        self,
        upload_token_id: str,
        file_path: str,
        name: str,
        description: str,
        tags: str,
        mime_type: str,
        access_control_id: int = 0,
        conversion_profile_id: int = 0,
    ):
        """
        Create a KalturaDocumentEntry using the uploaded file.

        Args:
            upload_token_id: The ID of the upload token
            file_path: Path to the file
            name: Name of the entry
            description: Description of the entry
            tags: Comma-separated list of tags
            mime_type: MIME type of the file
            access_control_id: Optional access control ID
            conversion_profile_id: Optional conversion profile ID

        Returns:
            Entry ID
        """
        # Determine document type
        document_type = get_document_type(mime_type)

        # Create document entry
        entry = KalturaDocumentEntry()
        entry.name = name
        entry.description = description
        entry.documentType = document_type
        entry.tags = tags

        if access_control_id > 0:
            entry.accessControlId = access_control_id
        if conversion_profile_id > 0:
            entry.conversionProfileId = conversion_profile_id

        # Add the entry
        try:
            document_entry = await self.kaltura_client.execute_request("document", "add", document=entry)

            if not hasattr(document_entry, "id") or not document_entry.id:
                logger.error("Document entry created without valid ID")
                raise ValueError("Document entry created without valid ID")

            logger.info(f"Created document entry with ID: {document_entry.id}")

            # Attach the uploaded file to the document entry
            resource = KalturaUploadedFileTokenResource()
            resource.token = upload_token_id

            final_entry = await self.kaltura_client.execute_request(
                "document", "addContent", entryId=document_entry.id, resource=resource
            )

            if not hasattr(final_entry, "id") or not final_entry.id:
                logger.error("Final document entry has no valid ID")
                # If final_entry has no ID, return the original document_entry which should have an ID
                return document_entry

            return final_entry
        except Exception as e:
            logger.error(f"Error in _create_document_entry: {e}")
            raise

    async def _create_data_entry(
        self,
        upload_token_id: str,
        file_path: str,
        name: str,
        description: str,
        tags: str,
        access_control_id: int = 0,
    ):
        """
        Create a KalturaDataEntry using the uploaded file.

        Args:
            upload_token_id: The ID of the upload token
            file_path: Path to the file
            name: Name of the entry
            description: Description of the entry
            tags: Comma-separated list of tags
            access_control_id: Optional access control ID

        Returns:
            Entry ID
        """
        # Create data entry
        entry = KalturaDataEntry()
        entry.name = name
        entry.description = description
        entry.tags = tags

        if access_control_id > 0:
            entry.accessControlId = access_control_id

        # Add the entry
        try:
            data_entry = await self.kaltura_client.execute_request("data", "add", dataEntry=entry)

            if not hasattr(data_entry, "id") or not data_entry.id:
                logger.error("Data entry created without valid ID")
                raise ValueError("Data entry created without valid ID")

            logger.info(f"Created data entry with ID: {data_entry.id}")

            # Attach the uploaded file to the data entry
            resource = KalturaUploadedFileTokenResource()
            resource.token = upload_token_id

            final_entry = await self.kaltura_client.execute_request(
                "data", "addContent", entryId=data_entry.id, resource=resource
            )

            if not hasattr(final_entry, "id") or not final_entry.id:
                logger.error("Final data entry has no valid ID")
                # If final_entry has no ID, return the original data_entry which should have an ID
                return data_entry

            return final_entry
        except Exception as e:
            logger.error(f"Error in _create_data_entry: {e}")
            raise

    async def _assign_category(self, entry_id: str, category_id: int) -> None:
        """
        Assign a Kaltura entry to a category.

        Args:
            entry_id: The ID of the entry
            category_id: The ID of the category
        """
        try:
            await self.kaltura_client.execute_request(
                "categoryEntry",
                "add",
                categoryEntry={"entryId": entry_id, "categoryId": category_id},
            )
            logger.info(f"Assigned entry {entry_id} to category {category_id}")
        except Exception as e:
            logger.warning(f"Failed to assign entry {entry_id} to category {category_id}: {e}")

    async def _get_entry_details(self, entry_id: str, entry_type: str):
        """
        Get the details of an entry.

        Args:
            entry_id: The ID of the entry
            entry_type: The type of the entry ("media", "document", or "data")

        Returns:
            Entry object
        """
        # If entry_id is already an object with an id attribute, use that id
        if hasattr(entry_id, "id"):
            logger.info(f"Entry ID is an object with id: {entry_id.id}")
            entry_id = entry_id.id

        logger.info(f"Getting details for {entry_type} entry with ID: {entry_id}")

        if entry_type == "media":
            return await self.kaltura_client.execute_request("media", "get", entryId=entry_id)
        elif entry_type == "document":
            return await self.kaltura_client.execute_request("document", "get", entryId=entry_id)
        else:
            return await self.kaltura_client.execute_request("data", "get", entryId=entry_id)

    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        return types.Tool(
            name="kaltura.media.upload",
            description="Upload a file to Kaltura with advanced features like chunked uploading and automatic file type detection",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to upload"},
                    "name": {"type": "string", "description": "Name of the entry"},
                    "description": {"type": "string", "description": "Description of the entry"},
                    "tags": {"type": "string", "description": "Comma-separated list of tags"},
                    "access_control_id": {
                        "type": "integer",
                        "description": "Access control ID to apply to the entry",
                    },
                    "conversion_profile_id": {
                        "type": "integer",
                        "description": "Conversion profile ID to apply to the entry",
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Category ID to assign the entry to",
                    },
                    "chunk_size_kb": {
                        "type": "integer",
                        "description": "Initial chunk size in KB (default=2048)",
                    },
                    "adaptive_chunking": {
                        "type": "boolean",
                        "description": "Enable adaptive chunking based on upload speed (default=true)",
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Enable verbose logging (default=false)",
                    },
                },
                "required": ["file_path", "name"],
            },
        )
