"""
MIME type utilities for Kaltura MCP Server.

This module provides utilities for MIME type detection and mapping to Kaltura entry types.
It uses python-magic for content-based MIME type detection if available, otherwise falls
back to extension-based detection using the mimetypes module.
"""
import os
import logging
import mimetypes
from typing import Optional
from KalturaClient.Plugins.Core import KalturaMediaType
from KalturaClient.Plugins.Document import KalturaDocumentType

# Initialize mimetypes
mimetypes.init()

# Try to import python-magic for better MIME type detection
try:
    import magic  # python-magic (C-based libmagic bindings)
    HAS_PYTHON_MAGIC = True
except ImportError:
    HAS_PYTHON_MAGIC = False
    logging.warning(
        "python-magic is not installed. Falling back to extension-based MIME guess (less reliable)."
    )

logger = logging.getLogger(__name__)

def guess_mime_type(file_path: str) -> str:
    """
    Determine the MIME type of a file.
    
    Uses python-magic if available, otherwise falls back to mimetypes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist: {file_path}")
        return "application/octet-stream"
        
    if not os.path.isfile(file_path):
        logger.warning(f"Path is not a file: {file_path}")
        return "application/octet-stream"
        
    if HAS_PYTHON_MAGIC:
        try:
            # Use python-magic to detect MIME type from file content
            mime_type = magic.from_file(file_path, mime=True)
        except Exception as e:
            logger.warning(f"python-magic failed to detect MIME type: {e}. Falling back to mimetypes.")
            mime_type, _ = mimetypes.guess_type(file_path, strict=False)
    else:
        # Fallback to extension-based detection
        mime_type, _ = mimetypes.guess_type(file_path, strict=False)
    
    # Handle the case where MIME detection fails entirely
    if not mime_type:
        logger.debug(f"Unable to detect MIME type for {file_path}; defaulting to application/octet-stream.")
        return "application/octet-stream"
    
    return mime_type.lower()

def guess_kaltura_entry_type(file_path: str) -> str:
    """
    Determine the Kaltura entry type (media, document, or data) using MIME detection.
    
    This function maps file types to the appropriate Kaltura entry type:
    - Media: image/*, audio/*, video/*
    - Document: PDF, SWF, MS Office documents
    - Data: All other file types
    
    Args:
        file_path: Path to the file
        
    Returns:
        String indicating the entry type: "media", "document", or "data"
    """
    mime_type = guess_mime_type(file_path)
    logger.debug(f"Detected MIME type: '{mime_type}' for file '{file_path}'")

    # Check major type
    if mime_type.startswith(("image/", "audio/", "video/")):
        return "media"
    elif (
        mime_type == "application/pdf"
        or mime_type == "application/x-shockwave-flash"
        or mime_type.startswith("application/msword")
        or "application/vnd.openxmlformats-officedocument" in mime_type
    ):
        # This covers PDF, SWF, MS Word, OOXML files
        return "document"
    else:
        # Fallback to a "data" entry for all other MIME types
        return "data"

def get_media_type(file_path: str) -> KalturaMediaType:
    """
    Determine the KalturaMediaType based on file MIME type.
    
    This function maps file types to the appropriate KalturaMediaType:
    - VIDEO: video/*, .mp4, .mov, .avi, etc.
    - AUDIO: audio/*, .mp3, .wav, etc.
    - IMAGE: image/*, .jpg, .png, etc.
    
    Args:
        file_path: Path to the file
        
    Returns:
        KalturaMediaType enum value
    """
    mime_type = guess_mime_type(file_path)
    
    if mime_type.startswith("video/"):
        return KalturaMediaType.VIDEO
    elif mime_type.startswith("audio/"):
        return KalturaMediaType.AUDIO
    elif mime_type.startswith("image/"):
        return KalturaMediaType.IMAGE
    
    # Fallback to extension-based detection if MIME type is not conclusive
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Video extensions
    if ext in ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv']:
        return KalturaMediaType.VIDEO
    
    # Audio extensions
    elif ext in ['.mp3', '.wav', '.aac', '.m4a', '.flac']:
        return KalturaMediaType.AUDIO
    
    # Image extensions
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return KalturaMediaType.IMAGE
    
    # Default to video for unknown types
    logger.debug(f"Could not determine media type for {file_path}, defaulting to VIDEO")
    return KalturaMediaType.VIDEO

def get_document_type(mime_type: str) -> int:
    """
    Map MIME type to KalturaDocumentType enumeration value.
    
    This function maps MIME types to the appropriate KalturaDocumentType:
    - PDF: application/pdf
    - SWF: application/x-shockwave-flash
    - DOCUMENT: All other document types
    
    Args:
        mime_type: MIME type string
        
    Returns:
        KalturaDocumentType enum value
    """
    MIME_TO_DOCUMENT_TYPE = {
        'application/pdf': KalturaDocumentType.PDF,  # 13
        'application/x-shockwave-flash': KalturaDocumentType.SWF,  # 12
    }
    return MIME_TO_DOCUMENT_TYPE.get(mime_type.lower(), KalturaDocumentType.DOCUMENT)  # 11