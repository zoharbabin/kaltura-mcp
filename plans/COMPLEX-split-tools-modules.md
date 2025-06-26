# Split tools.py into Modules - COMPLEX (6 hours)

**Complexity**: High  
**Impact**: Critical - Improves maintainability and code organization  
**Time Estimate**: 6 hours  
**Dependencies**: Tool registry pattern

## Problem
The current `tools.py` file is 1282 lines long, containing all tool implementations in a single file. This creates several issues:
- Difficult to navigate and maintain
- Hard to test individual components
- Tight coupling between unrelated functionality
- Multiple developers can't work on different tools simultaneously
- Violates single responsibility principle

## Solution
Split the monolithic `tools.py` file into focused, cohesive modules organized by functionality:
- `media.py` - Media entry operations
- `search.py` - Search and discovery tools
- `analytics.py` - Analytics and reporting
- `assets.py` - Caption and attachment handling
- `utils.py` - Shared utilities
- `base.py` - Base classes and interfaces

## Implementation Steps

### 1. Analyze Current tools.py Structure (30 minutes)
First, let's map out the current functions and their categories:

**Media Tools:**
- `get_media_entry()` - Get entry details
- `get_download_url()` - Get download URLs
- `get_thumbnail_url()` - Get thumbnail URLs

**Search Tools:**
- `search_entries()` - Basic search
- `esearch_entries()` - Advanced eSearch
- `search_entries_intelligent()` - Intelligent search wrapper

**Analytics Tools:**
- `get_analytics()` - Analytics data

**Category Tools:**
- `list_categories()` - List content categories

**Asset Tools:**
- `list_caption_assets()` - List captions
- `get_caption_content()` - Get caption text
- `list_attachment_assets()` - List attachments
- `get_attachment_content()` - Get attachment content

**Utility Functions:**
- `safe_serialize_kaltura_field()` - Serialize fields
- `handle_kaltura_error()` - Error handling
- `validate_entry_id()` - Input validation

### 2. Create Enhanced Utils Module (45 minutes)
**File: `src/kaltura_mcp/tools/utils.py`** (Complete refactor)
```python
"""Comprehensive utilities for Kaltura MCP tools."""

import re
import os
import json
import logging
import traceback
import hashlib
import requests
from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Functions
# ============================================================================

def validate_entry_id(entry_id: Any) -> bool:
    """
    Validate Kaltura entry ID format with comprehensive security checks.
    
    Args:
        entry_id: Entry ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not entry_id or not isinstance(entry_id, str):
        return False
    
    # Security: Check for path traversal attempts
    if '..' in entry_id or '/' in entry_id or '\\' in entry_id:
        return False
    
    # Security: Check for command injection attempts
    dangerous_chars = ['$', '`', ';', '&', '|', '<', '>', '"', "'", '(', ')']
    if any(char in entry_id for char in dangerous_chars):
        return False
    
    # Format validation: Should be number_alphanumeric
    if not re.match(r'^[0-9]+_[a-zA-Z0-9]+$', entry_id):
        return False
    
    # Length validation: Reasonable bounds
    if len(entry_id) < 3 or len(entry_id) > 50:
        return False
        
    return True


def validate_date_format(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD)."""
    if not date_str or not isinstance(date_str, str):
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """Validate URL format and safety."""
    if not url or not isinstance(url, str):
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme)
    except Exception:
        return False


def validate_dimensions(width: int, height: int, max_size: int = 4096) -> bool:
    """Validate image/video dimensions."""
    if not isinstance(width, int) or not isinstance(height, int):
        return False
    
    return 1 <= width <= max_size and 1 <= height <= max_size


def validate_limit_offset(limit: Optional[int], offset: Optional[int]) -> tuple:
    """Validate and normalize pagination parameters."""
    # Validate limit
    if limit is None:
        limit = 20
    elif not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer")
    elif limit > 100:
        limit = 100  # Cap at 100
    
    # Validate offset
    if offset is None:
        offset = 0
    elif not isinstance(offset, int) or offset < 0:
        raise ValueError("Offset must be a non-negative integer")
    
    return limit, offset


# ============================================================================
# Serialization and Formatting Functions
# ============================================================================

def safe_serialize_kaltura_field(field: Any) -> Any:
    """Safely serialize Kaltura enum/object fields to JSON-compatible values."""
    if field is None:
        return None
    if hasattr(field, 'value'):
        return field.value
    return str(field)


def format_timestamp(timestamp: Optional[int]) -> Optional[str]:
    """Format Unix timestamp to ISO format."""
    if timestamp is None:
        return None
    
    try:
        return datetime.fromtimestamp(timestamp).isoformat()
    except (ValueError, TypeError, OSError):
        logger.warning(f"Invalid timestamp: {timestamp}")
        return None


def format_duration(duration: Optional[int]) -> Optional[str]:
    """Format duration in seconds to human-readable format."""
    if duration is None or duration <= 0:
        return None
    
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def format_file_size(size_bytes: Optional[int]) -> Optional[str]:
    """Format file size in bytes to human-readable format."""
    if size_bytes is None or size_bytes <= 0:
        return None
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def clean_string(value: Any, max_length: Optional[int] = None) -> Optional[str]:
    """Clean and validate string input."""
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace
    value = value.strip()
    
    # Return None for empty strings
    if not value:
        return None
    
    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length-3] + "..."
    
    return value


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage."""
    if not filename:
        return "unknown"
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove path separators
    filename = filename.replace('..', '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


# ============================================================================
# Error Handling Functions
# ============================================================================

def handle_kaltura_error(e: Exception, operation: str, context: Dict[str, Any] = None) -> str:
    """Centralized error handling for Kaltura API operations."""
    error_context = context or {}
    error_type = type(e).__name__
    
    # Log the error for debugging
    logger.error(f"Kaltura API error in {operation}: {str(e)}", exc_info=True)
    
    # Create detailed error response
    error_response = {
        "error": f"Failed to {operation}: {str(e)}",
        "errorType": error_type,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        **error_context
    }
    
    # Add suggestion based on error type
    suggestion = get_error_suggestion(e, operation)
    if suggestion:
        error_response["suggestion"] = suggestion
    
    # Log detailed error for debugging (not exposed to user)
    if os.getenv("KALTURA_DEBUG") == "true":
        error_response["traceback"] = traceback.format_exc()
    
    return json.dumps(error_response, indent=2)


def get_error_suggestion(error: Exception, operation: str) -> Optional[str]:
    """Get helpful suggestion based on error type and operation."""
    error_str = str(error).lower()
    
    if "authentication" in error_str or "session" in error_str:
        return "Check your Kaltura credentials and ensure they are valid"
    
    elif "permission" in error_str or "access" in error_str:
        return "Verify that your Kaltura account has permissions for this operation"
    
    elif "not found" in error_str:
        if "get media entry" in operation:
            return "Verify the entry ID exists and is accessible to your account"
        return "Check that the requested resource exists and is accessible"
    
    elif "network" in error_str or "connection" in error_str:
        return "Check your network connection and Kaltura service URL"
    
    elif "timeout" in error_str:
        return "The request timed out. Try reducing the scope or check server status"
    
    elif "rate limit" in error_str:
        return "API rate limit exceeded. Please wait before making more requests"
    
    return None


def create_error_response(error: str, error_type: str = "APIError", 
                         operation: str = "unknown", **context) -> str:
    """Create standardized error response."""
    response = {
        "error": error,
        "errorType": error_type,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        **context
    }
    
    return json.dumps(response, indent=2)


# ============================================================================
# Data Processing Functions
# ============================================================================

def parse_kaltura_response(response: Any) -> Dict[str, Any]:
    """Parse and structure Kaltura API response."""
    if not response:
        return {}
    
    result = {}
    
    # Handle list responses
    if hasattr(response, 'objects') and hasattr(response, 'totalCount'):
        result = {
            'totalCount': response.totalCount,
            'objects': []
        }
        
        for obj in response.objects or []:
            result['objects'].append(parse_kaltura_object(obj))
    
    # Handle single object responses
    else:
        result = parse_kaltura_object(response)
    
    return result


def parse_kaltura_object(obj: Any) -> Dict[str, Any]:
    """Parse a single Kaltura object into a dictionary."""
    if not obj:
        return {}
    
    result = {}
    
    # Common fields to extract
    common_fields = [
        'id', 'name', 'description', 'mediaType', 'status', 'createdAt', 
        'updatedAt', 'duration', 'tags', 'categories', 'categoriesIds',
        'thumbnailUrl', 'downloadUrl', 'plays', 'views', 'width', 'height',
        'size', 'format', 'language', 'accuracy', 'filename', 'title'
    ]
    
    for field in common_fields:
        if hasattr(obj, field):
            try:
                value = getattr(obj, field)
                if value is not None:
                    result[field] = safe_serialize_kaltura_field(value)
            except (AttributeError, TypeError):
                continue
    
    # Special handling for timestamps
    for timestamp_field in ['createdAt', 'updatedAt', 'lastPlayedAt']:
        if timestamp_field in result and result[timestamp_field]:
            result[timestamp_field] = format_timestamp(result[timestamp_field])
    
    return result


def build_url_with_params(base_url: str, params: Dict[str, Any]) -> str:
    """Build URL with query parameters."""
    if not params:
        return base_url
    
    # Filter out None values
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    if not filtered_params:
        return base_url
    
    # Build parameter string
    param_strings = []
    for key, value in filtered_params.items():
        param_strings.append(f"{key}={value}")
    
    separator = "&" if "?" in base_url else "?"
    return base_url + separator + "&".join(param_strings)


# ============================================================================
# Content Download Functions
# ============================================================================

def download_content(url: str, timeout: int = 30, max_size: int = 10*1024*1024) -> tuple:
    """
    Safely download content from URL.
    
    Args:
        url: URL to download from
        timeout: Request timeout in seconds
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (success: bool, content: bytes or error: str)
    """
    if not validate_url(url):
        return False, "Invalid URL format"
    
    try:
        # Create session with timeout
        session = requests.Session()
        headers = {
            'User-Agent': 'Kaltura-MCP/1.0 (Python)'
        }
        
        # Make request with streaming to check size
        response = session.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Check content length
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > max_size:
            return False, f"Content too large: {content_length} bytes (max: {max_size})"
        
        # Download content in chunks
        content = b""
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > max_size:
                return False, f"Content exceeded maximum size: {max_size} bytes"
        
        return True, content
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to download content from {url}: {e}")
        return False, f"Download failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error downloading from {url}: {e}")
        return False, f"Unexpected error: {str(e)}"


def encode_content_base64(content: bytes) -> str:
    """Encode binary content as base64."""
    import base64
    return base64.b64encode(content).decode('utf-8')


# ============================================================================
# Caching Functions
# ============================================================================

def generate_cache_key(operation: str, **params) -> str:
    """Generate cache key for operation and parameters."""
    # Sort parameters for consistent keys
    sorted_params = sorted(params.items())
    params_str = json.dumps(sorted_params, sort_keys=True)
    
    # Create hash of operation + parameters
    key_data = f"{operation}:{params_str}"
    return hashlib.md5(key_data.encode()).hexdigest()


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check if expired
        if datetime.utcnow().timestamp() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        expiry = datetime.utcnow().timestamp() + ttl
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        current_time = datetime.utcnow().timestamp()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if current_time > expiry
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)


# Global cache instance
_global_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get global cache instance."""
    return _global_cache
```

### 3. Create Media Tools Module (90 minutes)
**File: `src/kaltura_mcp/tools/media.py`** (Complete implementation)
```python
"""Media entry related tools."""

import json
from typing import Dict, Any, Optional

from .base import MediaTool
from .utils import (
    validate_entry_id, safe_serialize_kaltura_field, format_timestamp,
    parse_kaltura_object, build_url_with_params, validate_dimensions
)
from ..tool_registry import register_tool


@register_tool("media")
class GetMediaEntryTool(MediaTool):
    """Tool for retrieving detailed media entry information."""
    
    @property
    def name(self) -> str:
        return "get_media_entry"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific media entry"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entry_id": {
                    "type": "string",
                    "description": "The Kaltura entry ID to retrieve",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$",
                    "minLength": 3,
                    "maxLength": 50
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str) -> str:
        """Execute the get media entry tool."""
        try:
            # Validate entry ID
            entry_id = self.validate_entry_id(entry_id)
            
            # Get Kaltura client
            client = manager.get_client()
            
            # Retrieve entry
            entry = client.media.get(entry_id)
            
            # Build comprehensive response
            response_data = {
                "id": entry.id,
                "name": entry.name,
                "description": entry.description,
                "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                "status": safe_serialize_kaltura_field(entry.status),
                "createdAt": format_timestamp(entry.createdAt),
                "updatedAt": format_timestamp(entry.updatedAt),
                "duration": entry.duration,
                "tags": entry.tags,
                "categories": entry.categories,
                "categoriesIds": entry.categoriesIds,
                "thumbnailUrl": entry.thumbnailUrl,
                "downloadUrl": entry.downloadUrl,
                "plays": entry.plays or 0,
                "views": entry.views or 0,
                "lastPlayedAt": format_timestamp(entry.lastPlayedAt),
                "width": entry.width,
                "height": entry.height,
                "dataUrl": entry.dataUrl,
                "flavorParamsIds": entry.flavorParamsIds,
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "get media entry", {"entry_id": entry_id})


@register_tool("media")
class GetDownloadUrlTool(MediaTool):
    """Tool for getting direct download URLs for media files."""
    
    @property
    def name(self) -> str:
        return "get_download_url"
    
    @property
    def description(self) -> str:
        return "Get a direct download URL for a media entry"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entry_id": {
                    "type": "string",
                    "description": "Media entry ID",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                },
                "flavor_id": {
                    "type": "string",
                    "description": "Optional specific flavor ID",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str, flavor_id: Optional[str] = None) -> str:
        """Execute the get download URL tool."""
        try:
            # Validate entry ID
            entry_id = self.validate_entry_id(entry_id)
            
            # Get Kaltura client
            client = manager.get_client()
            
            # Get the entry to verify it exists
            entry = client.media.get(entry_id)
            
            # Get flavor assets
            from KalturaClient.Plugins.Core import KalturaAssetFilter
            flavor_filter = KalturaAssetFilter()
            flavor_filter.entryIdEqual = entry_id
            flavors = client.flavorAsset.list(flavor_filter)
            
            target_flavor = None
            
            if flavor_id:
                # Find specific flavor
                for flavor in flavors.objects:
                    if flavor.id == flavor_id:
                        target_flavor = flavor
                        break
                
                if not target_flavor:
                    return self.format_success_response({
                        "error": f"Flavor ID {flavor_id} not found for entry {entry_id}",
                        "availableFlavors": [f.id for f in flavors.objects]
                    })
            else:
                # Get the source or highest quality flavor
                for flavor in flavors.objects:
                    if flavor.isOriginal:
                        target_flavor = flavor
                        break
                
                if not target_flavor and flavors.objects:
                    target_flavor = flavors.objects[0]
            
            if not target_flavor:
                return self.format_success_response({
                    "error": "No flavor assets found for this entry",
                    "entryId": entry_id
                })
            
            # Get download URL
            download_url = client.flavorAsset.getUrl(target_flavor.id)
            
            response_data = {
                "entryId": entry_id,
                "entryName": entry.name,
                "flavorId": target_flavor.id,
                "fileSize": target_flavor.size * 1024 if target_flavor.size else None,
                "bitrate": target_flavor.bitrate,
                "format": target_flavor.fileExt,
                "downloadUrl": download_url,
                "isOriginal": target_flavor.isOriginal,
                "containerFormat": safe_serialize_kaltura_field(target_flavor.containerFormat),
                "videoCodec": safe_serialize_kaltura_field(target_flavor.videoCodecId),
                "width": target_flavor.width,
                "height": target_flavor.height
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "get download URL", {
                "entry_id": entry_id,
                "flavor_id": flavor_id
            })


@register_tool("media")
class GetThumbnailUrlTool(MediaTool):
    """Tool for generating custom thumbnail URLs."""
    
    @property
    def name(self) -> str:
        return "get_thumbnail_url"
    
    @property
    def description(self) -> str:
        return "Get video thumbnail/preview image URL with custom dimensions"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entry_id": {
                    "type": "string",
                    "description": "Media entry ID",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                },
                "width": {
                    "type": "integer",
                    "description": "Thumbnail width in pixels",
                    "minimum": 1,
                    "maximum": 4096,
                    "default": 120
                },
                "height": {
                    "type": "integer", 
                    "description": "Thumbnail height in pixels",
                    "minimum": 1,
                    "maximum": 4096,
                    "default": 90
                },
                "second": {
                    "type": "integer",
                    "description": "Video second to capture (for videos)",
                    "minimum": 0,
                    "default": 5
                },
                "quality": {
                    "type": "integer",
                    "description": "JPEG quality (1-100)",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 75
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str, width: int = 120, 
                     height: int = 90, second: int = 5, quality: int = 75) -> str:
        """Execute the get thumbnail URL tool."""
        try:
            # Validate entry ID
            entry_id = self.validate_entry_id(entry_id)
            
            # Validate dimensions
            if not validate_dimensions(width, height):
                return self.format_success_response({
                    "error": "Invalid dimensions: width and height must be between 1 and 4096"
                })
            
            # Get Kaltura client
            client = manager.get_client()
            
            # Get entry to verify it exists and get info
            entry = client.media.get(entry_id)
            
            if not entry.thumbnailUrl:
                return self.format_success_response({
                    "error": "No thumbnail available for this entry",
                    "entryId": entry_id,
                    "entryName": entry.name
                })
            
            # Build thumbnail URL with parameters
            params = {
                "width": width,
                "height": height,
                "quality": quality
            }
            
            # Add video-specific parameters
            from KalturaClient.Plugins.Core import KalturaMediaType
            is_video = hasattr(entry, 'mediaType') and entry.mediaType == KalturaMediaType.VIDEO
            
            if is_video and second > 0:
                params["vid_sec"] = second
            
            # Construct final URL
            thumbnail_url = build_url_with_params(entry.thumbnailUrl, params)
            
            response_data = {
                "entryId": entry_id,
                "entryName": entry.name,
                "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                "thumbnailUrl": thumbnail_url,
                "parameters": {
                    "width": width,
                    "height": height,
                    "quality": quality,
                    "second": second if is_video else None
                },
                "originalThumbnailUrl": entry.thumbnailUrl
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "get thumbnail URL", {
                "entry_id": entry_id,
                "width": width,
                "height": height,
                "second": second,
                "quality": quality
            })


@register_tool("media")
class ListMediaEntriesTool(MediaTool):
    """Tool for listing media entries with filtering and pagination."""
    
    @property
    def name(self) -> str:
        return "list_media_entries"
    
    @property
    def description(self) -> str:
        return "List media entries with optional filtering by media type and search text"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "search_text": {
                    "type": "string",
                    "description": "Optional search text to filter entries"
                },
                "media_type": {
                    "type": "string",
                    "enum": ["video", "audio", "image"],
                    "description": "Optional media type filter"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entries to return",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of entries to skip",
                    "minimum": 0,
                    "default": 0
                }
            },
            "additionalProperties": False
        }
    
    async def execute(self, manager, search_text: Optional[str] = None,
                     media_type: Optional[str] = None, limit: int = 20, 
                     offset: int = 0) -> str:
        """Execute the list media entries tool."""
        try:
            # Get Kaltura client
            client = manager.get_client()
            
            # Create filter
            from KalturaClient.Plugins.Core import KalturaMediaEntryFilter, KalturaMediaType
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
            from KalturaClient.Plugins.Core import KalturaFilterPager
            pager = KalturaFilterPager()
            pager.pageSize = min(limit, 100)
            pager.pageIndex = offset // limit + 1
            
            # List entries
            result = client.media.list(filter, pager)
            
            entries = []
            for entry in result.objects:
                entries.append({
                    "id": entry.id,
                    "name": entry.name,
                    "description": entry.description,
                    "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                    "status": safe_serialize_kaltura_field(entry.status),
                    "createdAt": format_timestamp(entry.createdAt),
                    "duration": entry.duration,
                    "tags": entry.tags,
                    "thumbnailUrl": entry.thumbnailUrl,
                    "downloadUrl": entry.downloadUrl,
                    "plays": entry.plays or 0,
                    "views": entry.views or 0,
                })
            
            response_data = {
                "totalCount": result.totalCount,
                "entries": entries,
                "pagination": {
                    "page": offset // limit + 1,
                    "pageSize": limit,
                    "offset": offset,
                    "hasMore": len(entries) == limit
                },
                "filters": {
                    "search_text": search_text,
                    "media_type": media_type
                }
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "list media entries", {
                "search_text": search_text,
                "media_type": media_type,
                "limit": limit,
                "offset": offset
            })
```

### 4. Create Search Tools Module (90 minutes)
**File: `src/kaltura_mcp/tools/search.py`**
```python
"""Search and discovery tools."""

import json
from typing import Dict, Any, Optional, List

from .base import SearchTool
from .utils import (
    validate_limit_offset, parse_kaltura_response, 
    safe_serialize_kaltura_field, format_timestamp
)
from ..tool_registry import register_tool


@register_tool("search")
class SearchEntriesTool(SearchTool):
    """Intelligent search tool with advanced filtering capabilities."""
    
    @property
    def name(self) -> str:
        return "search_entries"
    
    @property
    def description(self) -> str:
        return ("Search and discover media entries with intelligent sorting and filtering. "
                "IMPORTANT: To find the latest/newest videos, use query='*' with "
                "sort_field='created_at' and sort_order='desc'.")
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string", 
                    "description": ("Search query. Use '*' to list all entries (essential for "
                                   "finding latest/newest content), use keywords to search for "
                                   "specific content, or exact phrases in quotes."),
                    "minLength": 1,
                    "maxLength": 500
                },
                "search_type": {
                    "type": "string",
                    "enum": ["unified", "entry", "caption", "metadata", "cuepoint"],
                    "description": "Type of search to perform",
                    "default": "unified"
                },
                "match_type": {
                    "type": "string",
                    "enum": ["partial", "exact_match", "starts_with", "exists", "range"],
                    "description": "How to match the search query",
                    "default": "partial"
                },
                "specific_field": {
                    "type": "string",
                    "description": "Search in a specific field (name, description, tags, etc.)"
                },
                "boolean_operator": {
                    "type": "string",
                    "enum": ["and", "or", "not"],
                    "description": "Boolean operator for multiple terms",
                    "default": "and"
                },
                "include_highlights": {
                    "type": "boolean",
                    "description": "Include search result highlights",
                    "default": True
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "sort_field": {
                    "type": "string",
                    "enum": ["created_at", "updated_at", "name", "views", "plays", "rank"],
                    "description": "Field to sort by",
                    "default": "created_at"
                },
                "sort_order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order",
                    "default": "desc"
                },
                "date_range": {
                    "type": "object",
                    "properties": {
                        "after": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
                        "before": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
                    },
                    "description": "Date range filter"
                },
                "custom_metadata": {
                    "type": "object",
                    "properties": {
                        "profile_id": {"type": "integer"},
                        "xpath": {"type": "string"}
                    },
                    "description": "Custom metadata search parameters"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, query: str, search_type: str = "unified",
                     match_type: str = "partial", specific_field: Optional[str] = None,
                     boolean_operator: str = "and", include_highlights: bool = True,
                     max_results: int = 20, sort_field: str = "created_at", 
                     sort_order: str = "desc", date_range: Optional[Dict[str, str]] = None,
                     custom_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Execute intelligent search."""
        try:
            # Validate parameters
            validated_params = self.validate_search_params(
                query=query, max_results=max_results, sort_order=sort_order
            )
            
            # Handle special case for listing all entries
            if query == "*":
                return await self._list_all_entries(manager, sort_field, sort_order, max_results)
            
            # Perform eSearch
            return await self._perform_esearch(
                manager=manager,
                query=query,
                search_type=search_type,
                match_type=match_type,
                specific_field=specific_field,
                boolean_operator=boolean_operator,
                include_highlights=include_highlights,
                max_results=max_results,
                sort_field=sort_field,
                sort_order=sort_order,
                date_range=date_range,
                custom_metadata=custom_metadata
            )
            
        except Exception as e:
            return self.handle_error(e, "search entries", {
                "query": query,
                "search_type": search_type,
                "max_results": max_results
            })
    
    async def _list_all_entries(self, manager, sort_field: str, sort_order: str, 
                               limit: int) -> str:
        """List all entries using basic media.list API."""
        try:
            client = manager.get_client()
            
            # Create filter and pager
            from KalturaClient.Plugins.Core import KalturaMediaEntryFilter, KalturaFilterPager
            filter = KalturaMediaEntryFilter()
            
            # Set sort order
            order_map = {
                "created_at": "+createdAt" if sort_order == "asc" else "-createdAt",
                "updated_at": "+updatedAt" if sort_order == "asc" else "-updatedAt", 
                "name": "+name" if sort_order == "asc" else "-name",
                "views": "+views" if sort_order == "asc" else "-views",
                "plays": "+plays" if sort_order == "asc" else "-plays"
            }
            filter.orderBy = order_map.get(sort_field, "-createdAt")
            
            pager = KalturaFilterPager()
            pager.pageSize = min(limit, 100)
            
            # Execute search
            result = client.media.list(filter, pager)
            
            # Format results
            entries = []
            for entry in result.objects:
                entries.append({
                    "id": entry.id,
                    "name": entry.name,
                    "description": entry.description,
                    "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                    "createdAt": format_timestamp(entry.createdAt),
                    "duration": entry.duration,
                    "tags": entry.tags,
                    "thumbnailUrl": entry.thumbnailUrl,
                    "plays": entry.plays or 0,
                    "views": entry.views or 0,
                })
            
            response_data = {
                "searchQuery": "*",
                "operationType": "list_all",
                "totalCount": result.totalCount,
                "entries": entries,
                "searchConfiguration": {
                    "sort_field": sort_field,
                    "sort_order": sort_order,
                    "max_results": limit
                }
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            raise Exception(f"Failed to list all entries: {str(e)}")
    
    async def _perform_esearch(self, manager, **params) -> str:
        """Perform advanced eSearch operation."""
        try:
            # Import eSearch classes
            from KalturaClient.Plugins.ElasticSearch import (
                KalturaESearchEntryParams, KalturaESearchEntryOperator,
                KalturaESearchEntryItem, KalturaESearchUnifiedItem,
                KalturaESearchItemType, KalturaESearchEntryFieldName,
                KalturaESearchOperatorType, KalturaESearchOrderBy,
                KalturaESearchEntryOrderByItem, KalturaESearchEntryOrderByFieldName,
                KalturaESearchSortOrder
            )
            from KalturaClient.Plugins.Core import KalturaFilterPager
            
            client = manager.get_client()
            
            # Create search items based on search type
            search_items = []
            
            if params["search_type"] == "unified":
                unified_item = KalturaESearchUnifiedItem()
                unified_item.searchTerm = params["query"]
                unified_item.itemType = self._get_item_type(params["match_type"])
                unified_item.addHighlight = params["include_highlights"]
                search_items.append(unified_item)
            
            elif params["search_type"] == "entry":
                entry_item = KalturaESearchEntryItem()
                entry_item.searchTerm = params["query"]
                entry_item.itemType = self._get_item_type(params["match_type"])
                entry_item.fieldName = self._get_entry_field_name(params["specific_field"] or "name")
                entry_item.addHighlight = params["include_highlights"]
                search_items.append(entry_item)
            
            # Add date range filtering if specified
            if params["date_range"]:
                date_item = self._create_date_range_item(params["date_range"])
                if date_item:
                    search_items.append(date_item)
            
            # Create search operator
            search_operator = KalturaESearchEntryOperator()
            search_operator.operator = self._get_operator_type(params["boolean_operator"])
            search_operator.searchItems = search_items
            
            # Create search parameters
            search_params = KalturaESearchEntryParams()
            search_params.searchOperator = search_operator
            
            # Add sorting
            order_by = KalturaESearchOrderBy()
            order_item = KalturaESearchEntryOrderByItem()
            order_item.sortField = self._get_sort_field(params["sort_field"])
            order_item.sortOrder = self._get_sort_order(params["sort_order"])
            order_by.orderItems = [order_item]
            search_params.orderBy = order_by
            
            # Add paging
            pager = KalturaFilterPager()
            pager.pageSize = min(params["max_results"], 100)
            
            # Execute search
            search_results = client.elasticSearch.eSearch.searchEntry(search_params, pager)
            
            # Process results
            entries = []
            for result in search_results.objects:
                entry_data = {
                    "id": result.object.id,
                    "name": result.object.name,
                    "description": result.object.description,
                    "mediaType": safe_serialize_kaltura_field(result.object.mediaType),
                    "createdAt": format_timestamp(result.object.createdAt),
                    "duration": result.object.duration,
                    "tags": result.object.tags,
                    "thumbnailUrl": result.object.thumbnailUrl,
                    "plays": result.object.plays or 0,
                    "views": result.object.views or 0,
                }
                
                # Add highlights if available
                if hasattr(result, 'highlight') and result.highlight and params["include_highlights"]:
                    highlights = []
                    for highlight in result.highlight:
                        highlight_data = {
                            "fieldName": highlight.fieldName,
                            "hits": [hit.value for hit in highlight.hits] if highlight.hits else []
                        }
                        highlights.append(highlight_data)
                    entry_data["highlights"] = highlights
                
                entries.append(entry_data)
            
            response_data = {
                "searchQuery": params["query"],
                "searchType": params["search_type"],
                "totalCount": search_results.totalCount,
                "entries": entries,
                "searchConfiguration": {
                    "match_type": params["match_type"],
                    "sort_field": params["sort_field"],
                    "sort_order": params["sort_order"],
                    "highlights_enabled": params["include_highlights"]
                }
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            raise Exception(f"eSearch failed: {str(e)}")
    
    def _get_item_type(self, item_type: str):
        """Convert string to KalturaESearchItemType."""
        from KalturaClient.Plugins.ElasticSearch import KalturaESearchItemType
        
        type_map = {
            "exact_match": KalturaESearchItemType.EXACT_MATCH,
            "partial": KalturaESearchItemType.PARTIAL,
            "starts_with": KalturaESearchItemType.STARTS_WITH,
            "exists": KalturaESearchItemType.EXISTS,
            "range": KalturaESearchItemType.RANGE,
        }
        return type_map.get(item_type, KalturaESearchItemType.PARTIAL)
    
    def _get_entry_field_name(self, field_name: str):
        """Convert string to KalturaESearchEntryFieldName."""
        from KalturaClient.Plugins.ElasticSearch import KalturaESearchEntryFieldName
        
        field_map = {
            "name": KalturaESearchEntryFieldName.NAME,
            "description": KalturaESearchEntryFieldName.DESCRIPTION,
            "tags": KalturaESearchEntryFieldName.TAGS,
            "created_at": KalturaESearchEntryFieldName.CREATED_AT,
            "updated_at": KalturaESearchEntryFieldName.UPDATED_AT,
            "user_id": KalturaESearchEntryFieldName.USER_ID,
        }
        return field_map.get(field_name, KalturaESearchEntryFieldName.NAME)
    
    def _get_operator_type(self, operator_type: str):
        """Convert string to KalturaESearchOperatorType."""
        from KalturaClient.Plugins.ElasticSearch import KalturaESearchOperatorType
        
        operator_map = {
            "and": KalturaESearchOperatorType.AND_OP,
            "or": KalturaESearchOperatorType.OR_OP,
            "not": KalturaESearchOperatorType.NOT_OP,
        }
        return operator_map.get(operator_type, KalturaESearchOperatorType.AND_OP)
    
    def _get_sort_field(self, field_name: str):
        """Convert string to KalturaESearchEntryOrderByFieldName."""
        from KalturaClient.Plugins.ElasticSearch import KalturaESearchEntryOrderByFieldName
        
        field_map = {
            "created_at": KalturaESearchEntryOrderByFieldName.CREATED_AT,
            "updated_at": KalturaESearchEntryOrderByFieldName.UPDATED_AT,
            "name": KalturaESearchEntryOrderByFieldName.NAME,
            "views": KalturaESearchEntryOrderByFieldName.VIEWS,
            "plays": KalturaESearchEntryOrderByFieldName.PLAYS,
            "rank": KalturaESearchEntryOrderByFieldName.RANK,
        }
        return field_map.get(field_name, KalturaESearchEntryOrderByFieldName.CREATED_AT)
    
    def _get_sort_order(self, sort_order: str):
        """Convert string to KalturaESearchSortOrder."""
        from KalturaClient.Plugins.ElasticSearch import KalturaESearchSortOrder
        
        order_map = {
            "asc": KalturaESearchSortOrder.ORDER_BY_ASC,
            "desc": KalturaESearchSortOrder.ORDER_BY_DESC,
        }
        return order_map.get(sort_order, KalturaESearchSortOrder.ORDER_BY_DESC)
    
    def _create_date_range_item(self, date_range: Dict[str, str]):
        """Create date range search item."""
        from KalturaClient.Plugins.ElasticSearch import (
            KalturaESearchEntryItem, KalturaESearchItemType,
            KalturaESearchEntryFieldName, KalturaESearchRange
        )
        from datetime import datetime
        
        try:
            if "after" in date_range and "before" in date_range:
                start_timestamp = int(datetime.strptime(date_range["after"], "%Y-%m-%d").timestamp())
                end_timestamp = int(datetime.strptime(date_range["before"], "%Y-%m-%d").timestamp())
                
                range_item = KalturaESearchRange()
                range_item.greaterThanOrEqual = start_timestamp
                range_item.lessThanOrEqual = end_timestamp
                
                date_item = KalturaESearchEntryItem()
                date_item.itemType = KalturaESearchItemType.RANGE
                date_item.fieldName = KalturaESearchEntryFieldName.CREATED_AT
                date_item.range = range_item
                
                return date_item
        except ValueError:
            pass  # Invalid date format, skip date filtering
        
        return None


@register_tool("search")
class ListCategoriesTool(SearchTool):
    """Tool for listing content categories."""
    
    @property
    def name(self) -> str:
        return "list_categories"
    
    @property
    def description(self) -> str:
        return "List and search content categories"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "search_text": {
                    "type": "string",
                    "description": "Optional search text to filter categories"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of categories to return",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                }
            },
            "additionalProperties": False
        }
    
    async def execute(self, manager, search_text: Optional[str] = None, 
                     limit: int = 20) -> str:
        """Execute the list categories tool."""
        try:
            # Get Kaltura client
            client = manager.get_client()
            
            # Create filter
            from KalturaClient.Plugins.Core import KalturaCategoryFilter, KalturaFilterPager
            filter = KalturaCategoryFilter()
            if search_text:
                filter.freeText = search_text
            
            # Create pager
            pager = KalturaFilterPager()
            pager.pageSize = min(limit, 100)
            
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
                    "createdAt": format_timestamp(category.createdAt),
                    "parentId": category.parentId,
                    "partnerId": category.partnerId
                })
            
            response_data = {
                "totalCount": result.totalCount,
                "categories": categories,
                "searchText": search_text,
                "limit": limit
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "list categories", {
                "search_text": search_text,
                "limit": limit
            })
```

### 5. Create Analytics Tools Module (60 minutes)
**File: `src/kaltura_mcp/tools/analytics.py`**
```python
"""Analytics and reporting tools."""

import json
from typing import Dict, Any, Optional, List

from .base import AnalyticsTool
from .utils import validate_entry_id, validate_date_format
from ..tool_registry import register_tool


@register_tool("analytics")
class GetAnalyticsTool(AnalyticsTool):
    """Tool for retrieving analytics data using Kaltura Report API."""
    
    @property
    def name(self) -> str:
        return "get_analytics"
    
    @property
    def description(self) -> str:
        return ("Get comprehensive analytics using Kaltura Report API. Supports multiple "
                "report types including content performance, user engagement, geographic "
                "distribution, contributor stats, and more.")
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "from_date": {
                    "type": "string",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "Start date for analytics (YYYY-MM-DD format)"
                },
                "to_date": {
                    "type": "string", 
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                    "description": "End date for analytics (YYYY-MM-DD format)"
                },
                "entry_id": {
                    "type": "string",
                    "description": "Optional specific entry ID for entry-specific analytics",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["content", "user_engagement", "contributors", "geographic", 
                            "bandwidth", "storage", "system", "platforms", "operating_system", "browsers"],
                    "description": "Type of analytics report",
                    "default": "content"
                },
                "categories": {
                    "type": "string",
                    "description": "Optional category filter (use full category name including parent paths)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["plays", "views", "engagement", "drop_off"]},
                    "description": "Metrics to retrieve (for reference/interpretation)"
                }
            },
            "required": ["from_date", "to_date"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, from_date: str, to_date: str,
                     entry_id: Optional[str] = None, report_type: str = "content",
                     categories: Optional[str] = None, limit: int = 20,
                     metrics: Optional[List[str]] = None) -> str:
        """Execute the analytics tool."""
        try:
            # Validate date range
            from_dt, to_dt = self.validate_date_range(from_date, to_date)
            
            # Validate entry ID if provided
            if entry_id:
                entry_id = validate_entry_id(entry_id)
                if not entry_id:
                    return self.format_success_response({
                        "error": "Invalid entry ID format"
                    })
            
            # Get Kaltura client
            client = manager.get_client()
            
            try:
                # Import required classes for Report API
                from KalturaClient.Plugins.Core import (
                    KalturaReportType, 
                    KalturaReportInputFilter, 
                    KalturaEndUserReportInputFilter,
                    KalturaFilterPager
                )
                
                # Convert dates to timestamps
                start_time = int(from_dt.timestamp())
                end_time = int(to_dt.timestamp())
                
                # Map report type strings to enum values
                report_type_map = {
                    "content": KalturaReportType.TOP_CONTENT,
                    "user_engagement": KalturaReportType.USER_ENGAGEMENT,
                    "contributors": KalturaReportType.TOP_CONTRIBUTORS,
                    "geographic": KalturaReportType.MAP_OVERLAY,
                    "bandwidth": KalturaReportType.TOP_SYNDICATION,
                    "storage": KalturaReportType.PARTNER_USAGE,
                    "system": KalturaReportType.PARTNER_USAGE,
                    "platforms": KalturaReportType.PLATFORMS,
                    "operating_system": KalturaReportType.OPERATING_SYSTEM,
                    "browsers": KalturaReportType.BROWSERS,
                }
                
                kaltura_report_type = report_type_map.get(report_type, KalturaReportType.TOP_CONTENT)
                
                # Determine filter type
                if report_type == "user_engagement":
                    report_filter = KalturaEndUserReportInputFilter()
                else:
                    report_filter = KalturaReportInputFilter()
                
                # Set filter properties
                report_filter.fromDate = start_time
                report_filter.toDate = end_time
                
                # Add category filter if specified
                if categories:
                    report_filter.categories = categories
                
                # Create pager
                pager = KalturaFilterPager()
                pager.pageSize = min(limit, 100)
                pager.pageIndex = 1
                
                # Set object IDs for entry-specific reports
                object_ids = entry_id if entry_id else None
                
                # Call the report API
                report_result = client.report.getTable(
                    reportType=kaltura_report_type,
                    reportInputFilter=report_filter,
                    pager=pager,
                    objectIds=object_ids
                )
                
                # Process results
                analytics_data = self._process_report_result(
                    report_result, report_type, from_date, to_date, 
                    entry_id, categories, metrics
                )
                
                return self.format_success_response(analytics_data)
                
            except ImportError as e:
                return self.format_success_response({
                    "error": "Analytics report functionality is not available. Missing required Kaltura Report plugin.",
                    "detail": str(e),
                    "suggestion": "Ensure the Kaltura Python client includes the Report plugin",
                    "fromDate": from_date,
                    "toDate": to_date,
                    "entryId": entry_id,
                })
            
        except Exception as e:
            return self.handle_error(e, "retrieve analytics", {
                "from_date": from_date,
                "to_date": to_date,
                "entry_id": entry_id,
                "report_type": report_type,
                "categories": categories,
                "limit": limit,
                "metrics": metrics or ["plays", "views", "engagement", "drop_off"]
            })
    
    def _process_report_result(self, report_result, report_type: str, from_date: str,
                              to_date: str, entry_id: Optional[str], categories: Optional[str],
                              metrics: Optional[List[str]]) -> Dict[str, Any]:
        """Process raw report result into structured data."""
        # Get report type name for display
        report_type_names = {
            "content": "Top Content",
            "user_engagement": "User Engagement", 
            "contributors": "Top Contributors",
            "geographic": "Geographic Distribution",
            "bandwidth": "Bandwidth Usage",
            "storage": "Storage Usage",
            "system": "System Reports",
            "platforms": "Platforms",
            "operating_system": "Operating Systems",
            "browsers": "Browsers",
        }
        
        # Parse the results
        analytics_data = {
            "reportType": report_type_names.get(report_type, "Analytics Report"),
            "reportTypeCode": report_type,
            "dateRange": {
                "from": from_date,
                "to": to_date
            },
            "entryId": entry_id,
            "categories": categories,
            "requestedMetrics": metrics or ["plays", "views", "engagement", "drop_off"],
            "headers": report_result.header.split(',') if report_result.header else [],
            "data": []
        }
        
        # Process data rows
        if report_result.data:
            for row in report_result.data.split('\n'):
                if row.strip():
                    row_data = row.split(',')
                    if len(row_data) >= len(analytics_data["headers"]):
                        # Create a dictionary mapping headers to values
                        row_dict = {}
                        for i, header in enumerate(analytics_data["headers"]):
                            if i < len(row_data):
                                value = row_data[i].strip()
                                # Try to convert numeric values
                                try:
                                    if '.' in value:
                                        value = float(value)
                                    elif value.isdigit():
                                        value = int(value)
                                except ValueError:
                                    pass  # Keep as string
                                
                                row_dict[header.strip()] = value
                        analytics_data["data"].append(row_dict)
        
        analytics_data["totalResults"] = len(analytics_data["data"])
        
        # Add summary statistics
        if analytics_data["data"]:
            analytics_data["summary"] = self._calculate_summary_stats(
                analytics_data["data"], analytics_data["headers"]
            )
        
        return analytics_data
    
    def _calculate_summary_stats(self, data: List[Dict], headers: List[str]) -> Dict[str, Any]:
        """Calculate summary statistics from analytics data."""
        summary = {}
        
        # Look for numeric columns to summarize
        numeric_cols = []
        for header in headers:
            header = header.strip().lower()
            if any(keyword in header for keyword in ['plays', 'views', 'count', 'duration', 'time']):
                numeric_cols.append(header)
        
        for col in numeric_cols:
            values = []
            for row in data:
                if col in row and isinstance(row[col], (int, float)):
                    values.append(row[col])
            
            if values:
                summary[col] = {
                    "total": sum(values),
                    "average": sum(values) / len(values),
                    "max": max(values),
                    "min": min(values)
                }
        
        return summary
```

### 6. Create Assets Tools Module (75 minutes)
**File: `src/kaltura_mcp/tools/assets.py`**
```python
"""Caption and attachment asset tools."""

import json
from typing import Dict, Any, Optional

from .base import AssetTool
from .utils import (
    validate_entry_id, safe_serialize_kaltura_field, format_timestamp,
    download_content, encode_content_base64, sanitize_filename
)
from ..tool_registry import register_tool


@register_tool("assets")
class ListCaptionAssetsTool(AssetTool):
    """Tool for listing caption assets for a media entry."""
    
    @property
    def name(self) -> str:
        return "list_caption_assets"
    
    @property
    def description(self) -> str:
        return "List available captions and subtitles for a media entry"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entry_id": {
                    "type": "string",
                    "description": "Media entry ID",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str) -> str:
        """Execute the list caption assets tool."""
        try:
            # Validate entry ID
            entry_id = validate_entry_id(entry_id)
            if not entry_id:
                return self.format_success_response({
                    "error": "Invalid entry ID format"
                })
            
            # Check if caption functionality is available
            try:
                from KalturaClient.Plugins.Caption import KalturaCaptionAssetFilter
                caption_available = True
            except ImportError:
                caption_available = False
            
            if not caption_available:
                return self.format_success_response({
                    "error": "Caption functionality is not available. The Caption plugin is not installed.",
                    "entryId": entry_id,
                })
            
            # Get Kaltura client
            client = manager.get_client()
            
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
                    "createdAt": format_timestamp(getattr(caption, 'createdAt', None)),
                    "updatedAt": format_timestamp(getattr(caption, 'updatedAt', None)),
                    "accuracy": getattr(caption, 'accuracy', None),
                    "isDefault": safe_serialize_kaltura_field(getattr(caption, 'isDefault', None)),
                }
                captions.append(caption_data)
            
            response_data = {
                "entryId": entry_id,
                "totalCount": result.totalCount,
                "captionAssets": captions,
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "list caption assets", {"entryId": entry_id})


@register_tool("assets")
class GetCaptionContentTool(AssetTool):
    """Tool for retrieving caption content and text."""
    
    @property
    def name(self) -> str:
        return "get_caption_content"
    
    @property
    def description(self) -> str:
        return "Get caption/subtitle content and download URL"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "caption_asset_id": {
                    "type": "string",
                    "description": "Caption asset ID to retrieve content for"
                },
                "download_content": {
                    "type": "boolean",
                    "description": "Whether to download and include the caption text",
                    "default": True
                }
            },
            "required": ["caption_asset_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, caption_asset_id: str, 
                     download_content: bool = True) -> str:
        """Execute the get caption content tool."""
        try:
            # Validate asset ID
            caption_asset_id = self.validate_asset_id(caption_asset_id)
            
            # Check if caption functionality is available
            try:
                from KalturaClient.Plugins.Caption import KalturaCaptionAssetFilter
                caption_available = True
            except ImportError:
                caption_available = False
            
            if not caption_available:
                return self.format_success_response({
                    "error": "Caption functionality is not available. The Caption plugin is not installed.",
                    "captionAssetId": caption_asset_id,
                })
            
            # Get Kaltura client
            client = manager.get_client()
            
            # Get caption asset details
            caption_asset = client.caption.captionAsset.get(caption_asset_id)
            
            # Get the caption content URL
            content_url = client.caption.captionAsset.getUrl(caption_asset_id)
            
            result = {
                "captionAssetId": caption_asset_id,
                "entryId": caption_asset.entryId,
                "language": safe_serialize_kaltura_field(caption_asset.language),
                "label": caption_asset.label,
                "format": safe_serialize_kaltura_field(caption_asset.format),
                "contentUrl": content_url,
                "size": caption_asset.size,
                "accuracy": caption_asset.accuracy,
                "filename": sanitize_filename(f"{caption_asset.label or 'caption'}.{caption_asset.fileExt or 'srt'}")
            }
            
            # Download content if requested
            if download_content and content_url:
                success, content_or_error = download_content(content_url)
                
                if success:
                    try:
                        caption_text = content_or_error.decode('utf-8')
                        result["captionText"] = caption_text
                        result["textLength"] = len(caption_text)
                        result["downloadStatus"] = "success"
                        result["note"] = "Caption text content has been successfully downloaded and included."
                    except UnicodeDecodeError:
                        # Try other encodings
                        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                            try:
                                caption_text = content_or_error.decode(encoding)
                                result["captionText"] = caption_text
                                result["textLength"] = len(caption_text)
                                result["downloadStatus"] = "success"
                                result["encoding"] = encoding
                                result["note"] = f"Caption text decoded using {encoding} encoding."
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            result["downloadError"] = "Failed to decode caption text with known encodings"
                            result["downloadStatus"] = "encoding_error"
                else:
                    result["downloadError"] = content_or_error
                    result["downloadStatus"] = "failed"
            else:
                result["downloadStatus"] = "skipped"
                result["note"] = "Caption content download was skipped or no URL available."
            
            return self.format_success_response(result)
            
        except Exception as e:
            return self.handle_error(e, "get caption content", {
                "caption_asset_id": caption_asset_id,
                "download_content": download_content
            })


@register_tool("assets")
class ListAttachmentAssetsTool(AssetTool):
    """Tool for listing attachment assets for a media entry."""
    
    @property
    def name(self) -> str:
        return "list_attachment_assets"
    
    @property
    def description(self) -> str:
        return "List attachment assets for a media entry"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entry_id": {
                    "type": "string",
                    "description": "Media entry ID",
                    "pattern": r"^[0-9]+_[a-zA-Z0-9]+$"
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str) -> str:
        """Execute the list attachment assets tool."""
        try:
            # Validate entry ID
            entry_id = validate_entry_id(entry_id)
            if not entry_id:
                return self.format_success_response({
                    "error": "Invalid entry ID format"
                })
            
            # Check if attachment functionality is available
            try:
                from KalturaClient.Plugins.Attachment import KalturaAttachmentAssetFilter
                attachment_available = True
            except ImportError:
                attachment_available = False
            
            if not attachment_available:
                return self.format_success_response({
                    "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
                    "entryId": entry_id,
                })
            
            # Get Kaltura client
            client = manager.get_client()
            
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
                    "format": safe_serialize_kaltura_field(attachment.format),
                    "status": safe_serialize_kaltura_field(attachment.status),
                    "fileExt": attachment.fileExt,
                    "size": attachment.size,
                    "createdAt": format_timestamp(attachment.createdAt),
                    "updatedAt": format_timestamp(attachment.updatedAt),
                    "description": attachment.description,
                    "tags": attachment.tags,
                }
                attachments.append(attachment_data)
            
            response_data = {
                "entryId": entry_id,
                "totalCount": result.totalCount,
                "attachmentAssets": attachments,
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "list attachment assets", {"entryId": entry_id})


@register_tool("assets")
class GetAttachmentContentTool(AssetTool):
    """Tool for retrieving attachment content and details."""
    
    @property
    def name(self) -> str:
        return "get_attachment_content"
    
    @property
    def description(self) -> str:
        return "Get attachment content details and download content as base64"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "attachment_asset_id": {
                    "type": "string",
                    "description": "Attachment asset ID to retrieve content for"
                },
                "download_content": {
                    "type": "boolean",
                    "description": "Whether to download and include the attachment content",
                    "default": False
                },
                "max_size_mb": {
                    "type": "integer",
                    "description": "Maximum file size to download in MB",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10
                }
            },
            "required": ["attachment_asset_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, attachment_asset_id: str, 
                     download_content: bool = False, max_size_mb: int = 10) -> str:
        """Execute the get attachment content tool."""
        try:
            # Validate asset ID
            attachment_asset_id = self.validate_asset_id(attachment_asset_id)
            
            # Check if attachment functionality is available
            try:
                from KalturaClient.Plugins.Attachment import KalturaAttachmentAssetFilter
                attachment_available = True
            except ImportError:
                attachment_available = False
            
            if not attachment_available:
                return self.format_success_response({
                    "error": "Attachment functionality is not available. The Attachment plugin is not installed.",
                    "attachmentAssetId": attachment_asset_id,
                })
            
            # Get Kaltura client
            client = manager.get_client()
            
            # Get attachment asset details
            attachment_asset = client.attachment.attachmentAsset.get(attachment_asset_id)
            
            # Get the attachment download URL
            download_url = client.attachment.attachmentAsset.getUrl(attachment_asset_id)
            
            result = {
                "attachmentAssetId": attachment_asset_id,
                "entryId": attachment_asset.entryId,
                "filename": sanitize_filename(attachment_asset.filename or "attachment"),
                "title": attachment_asset.title,
                "format": safe_serialize_kaltura_field(attachment_asset.format),
                "downloadUrl": download_url,
                "size": attachment_asset.size,
                "description": attachment_asset.description,
                "tags": attachment_asset.tags,
            }
            
            # Download content if requested
            if download_content and download_url:
                max_size_bytes = max_size_mb * 1024 * 1024
                success, content_or_error = download_content(
                    download_url, 
                    max_size=max_size_bytes
                )
                
                if success:
                    # Encode as base64
                    base64_content = encode_content_base64(content_or_error)
                    result["content"] = base64_content
                    result["contentEncoding"] = "base64"
                    result["actualSize"] = len(content_or_error)
                    result["downloadStatus"] = "success"
                    result["note"] = "Content downloaded and encoded as base64"
                else:
                    result["downloadError"] = content_or_error
                    result["downloadStatus"] = "failed"
                    result["note"] = "Failed to download content automatically. You can try the downloadUrl manually."
            else:
                result["downloadStatus"] = "skipped"
                result["note"] = "Content download was not requested."
            
            return self.format_success_response(result)
            
        except Exception as e:
            return self.handle_error(e, "get attachment content", {
                "attachment_asset_id": attachment_asset_id,
                "download_content": download_content,
                "max_size_mb": max_size_mb
            })
```

### 7. Update Package Initialization and Delete Old File (30 minutes)
**File: `src/kaltura_mcp/tools/__init__.py`** (Updated)
```python
"""Kaltura MCP tools package with modular architecture."""

# Import all tool modules to trigger registration
from . import media
from . import search
from . import analytics
from . import assets

# Export registry and utilities
from ..tool_registry import get_registry, register_tool
from .utils import (
    validate_entry_id, format_timestamp, safe_serialize_kaltura_field,
    handle_kaltura_error, validate_date_format, validate_dimensions
)
from .base import (
    BaseTool, MediaTool, SearchTool, AnalyticsTool, AssetTool,
    ToolExecutionError
)

__all__ = [
    # Registry
    'get_registry',
    'register_tool',
    
    # Utilities
    'validate_entry_id',
    'format_timestamp',
    'safe_serialize_kaltura_field',
    'handle_kaltura_error',
    'validate_date_format',
    'validate_dimensions',
    
    # Base classes
    'BaseTool',
    'MediaTool',
    'SearchTool',
    'AnalyticsTool',
    'AssetTool',
    'ToolExecutionError'
]

# Get registry info for debugging
def get_tools_info():
    """Get information about registered tools."""
    registry = get_registry()
    return {
        "total_tools": len(registry.list_tool_names()),
        "tools_by_category": {
            "media": registry.get_tools_by_category("media"),
            "search": registry.get_tools_by_category("search"),
            "analytics": registry.get_tools_by_category("analytics"),
            "assets": registry.get_tools_by_category("assets")
        }
    }
```

**Delete the old monolithic file:**
```bash
# Backup first (optional)
mv src/kaltura_mcp/tools.py src/kaltura_mcp/tools.py.backup

# Or just delete it
rm src/kaltura_mcp/tools.py
```

### 8. Create Tests for New Modules (30 minutes)
**File: `tests/unit/test_tools_modules.py`**
```python
"""Test the modular tools structure."""

import pytest
from kaltura_mcp.tool_registry import get_registry
from kaltura_mcp.tools import get_tools_info


class TestToolsModular:
    """Test modular tools organization."""
    
    def test_tools_are_registered(self):
        """Test that tools from all modules are registered."""
        registry = get_registry()
        registry.auto_discover()
        
        tool_names = registry.list_tool_names()
        
        # Check that we have tools from each category
        assert "get_media_entry" in tool_names  # Media
        assert "search_entries" in tool_names   # Search
        assert "get_analytics" in tool_names    # Analytics
        assert "list_caption_assets" in tool_names  # Assets
    
    def test_tools_by_category(self):
        """Test tools are properly categorized."""
        registry = get_registry()
        registry.auto_discover()
        
        media_tools = registry.get_tools_by_category("media")
        search_tools = registry.get_tools_by_category("search")
        analytics_tools = registry.get_tools_by_category("analytics")
        assets_tools = registry.get_tools_by_category("assets")
        
        assert len(media_tools) > 0
        assert len(search_tools) > 0
        assert len(analytics_tools) > 0
        assert len(assets_tools) > 0
    
    def test_get_tools_info(self):
        """Test tools info function."""
        info = get_tools_info()
        
        assert "total_tools" in info
        assert "tools_by_category" in info
        assert info["total_tools"] > 0
    
    def test_no_duplicate_tool_names(self):
        """Test that there are no duplicate tool names."""
        registry = get_registry()
        registry.auto_discover()
        
        tool_names = registry.list_tool_names()
        assert len(tool_names) == len(set(tool_names))
```

## Testing the Split

### 1. Test Registry Discovery
```bash
python -c "
from kaltura_mcp.tool_registry import get_registry
registry = get_registry()
count = registry.auto_discover()
print(f'Discovered {count} tools')
print('Tools:', registry.list_tool_names())
print('Categories:', registry.get_categories())
"
```

### 2. Test Import Structure
```bash
python -c "
from kaltura_mcp.tools import get_tools_info
info = get_tools_info()
print('Tools info:', info)
"
```

### 3. Run Comprehensive Tests
```bash
pytest tests/unit/test_tools_modules.py -v
pytest tests/unit/test_tool_registry.py -v
```

## Benefits
- ✅ Improved code organization (5 focused modules vs 1 monolithic file)
- ✅ Better maintainability (easier to find and modify specific functionality)
- ✅ Enhanced testability (can test individual modules)
- ✅ Better collaboration (multiple developers can work on different modules)
- ✅ Clearer separation of concerns
- ✅ Easier to extend (adding new tools is more straightforward)
- ✅ Reduced cognitive load (smaller, focused files)
- ✅ Better error isolation (issues in one module don't affect others)

## Files Created
- `src/kaltura_mcp/tools/base.py` (enhanced)
- `src/kaltura_mcp/tools/utils.py` (comprehensive refactor)
- `src/kaltura_mcp/tools/media.py`
- `src/kaltura_mcp/tools/search.py`
- `src/kaltura_mcp/tools/analytics.py`
- `src/kaltura_mcp/tools/assets.py`
- `tests/unit/test_tools_modules.py`

## Files Modified
- `src/kaltura_mcp/tools/__init__.py`

## Files Deleted
- `src/kaltura_mcp/tools.py` (replaced by modular structure)

## Next Steps
1. Add comprehensive tests for each module
2. Add tool-specific validation and error handling
3. Implement caching for frequently accessed data
4. Add tool performance monitoring
5. Consider adding tool versioning for backwards compatibility