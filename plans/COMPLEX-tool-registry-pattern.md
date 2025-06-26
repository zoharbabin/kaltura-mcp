# Tool Registry Pattern - COMPLEX (4 hours)

**Complexity**: Medium-High  
**Impact**: Very High - Eliminates code duplication and improves maintainability  
**Time Estimate**: 4 hours  
**Dependencies**: Configuration management, Basic unit tests

## Problem
- Tool definitions are duplicated between `server.py` and `remote_server.py`
- Long if-elif chains for tool dispatch in both servers
- Difficult to add new tools (requires changes in multiple places)
- No centralized tool management
- Hard to maintain consistency between different server modes

## Solution
Create a comprehensive tool registry system with:
- Base tool interface for consistency
- Automatic tool discovery and registration
- Centralized tool definitions
- Decorator-based registration
- Type-safe tool execution
- Shared tool logic between servers

## Implementation Steps

### 1. Create Base Tool Interface (45 minutes)
**File: `src/kaltura_mcp/tools/base.py`**
```python
"""Base interfaces and utilities for Kaltura MCP tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import json
import logging
from datetime import datetime

import mcp.types as types
from kaltura_mcp.kaltura_client import KalturaClientManager

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Exception raised during tool execution."""
    
    def __init__(self, message: str, error_type: str = "ToolError", context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}


class BaseTool(ABC):
    """Abstract base class for all Kaltura MCP tools."""
    
    def __init__(self):
        """Initialize the tool."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name as exposed to MCP clients."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool description."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for tool input validation."""
        pass
    
    @abstractmethod
    async def execute(self, manager: KalturaClientManager, **kwargs) -> str:
        """
        Execute the tool with provided arguments.
        
        Args:
            manager: Kaltura client manager instance
            **kwargs: Tool-specific arguments
            
        Returns:
            JSON string with tool results
            
        Raises:
            ToolExecutionError: If tool execution fails
        """
        pass
    
    def to_mcp_tool(self) -> types.Tool:
        """Convert tool to MCP Tool definition."""
        return types.Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )
    
    def validate_input(self, **kwargs) -> Dict[str, Any]:
        """
        Validate input parameters against schema.
        Override in subclasses for custom validation.
        
        Returns:
            Validated and potentially transformed parameters
        """
        # Basic validation against JSON schema would go here
        # For now, just return the kwargs as-is
        return kwargs
    
    def handle_error(self, error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle and format errors consistently.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            context: Additional context for debugging
            
        Returns:
            JSON error response
        """
        error_context = context or {}
        error_type = type(error).__name__
        
        # Log the error
        self.logger.error(f"Tool execution failed in {operation}: {str(error)}", exc_info=True)
        
        # Create error response
        error_response = {
            "error": f"Failed to {operation}: {str(error)}",
            "errorType": error_type,
            "operation": operation,
            "tool": self.name,
            **error_context
        }
        
        return json.dumps(error_response, indent=2)
    
    def format_success_response(self, data: Any) -> str:
        """
        Format successful response data.
        
        Args:
            data: Response data (dict, list, or other JSON-serializable)
            
        Returns:
            JSON string response
        """
        if isinstance(data, str):
            try:
                # If it's already JSON, validate it
                json.loads(data)
                return data
            except json.JSONDecodeError:
                # If not JSON, wrap it
                return json.dumps({"result": data}, indent=2)
        
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for special types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class MediaTool(BaseTool):
    """Base class for media-related tools."""
    
    def validate_entry_id(self, entry_id: str) -> str:
        """Validate Kaltura entry ID format."""
        from ..utils import validate_entry_id
        
        if not validate_entry_id(entry_id):
            raise ToolExecutionError(
                "Invalid entry ID format",
                error_type="ValidationError",
                context={"entry_id": entry_id}
            )
        return entry_id


class SearchTool(BaseTool):
    """Base class for search-related tools."""
    
    def validate_search_params(self, **kwargs) -> Dict[str, Any]:
        """Validate common search parameters."""
        validated = kwargs.copy()
        
        # Validate limit
        if 'limit' in validated:
            limit = validated['limit']
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                raise ToolExecutionError(
                    "Limit must be an integer between 1 and 100",
                    error_type="ValidationError",
                    context={"provided_limit": limit}
                )
        
        # Validate sort order
        if 'sort_order' in validated:
            sort_order = validated['sort_order']
            if sort_order not in ['asc', 'desc']:
                raise ToolExecutionError(
                    "Sort order must be 'asc' or 'desc'",
                    error_type="ValidationError",
                    context={"provided_sort_order": sort_order}
                )
        
        return validated


class AnalyticsTool(BaseTool):
    """Base class for analytics-related tools."""
    
    def validate_date_range(self, from_date: str, to_date: str) -> tuple:
        """Validate date range format and logic."""
        import re
        from datetime import datetime
        
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if not re.match(date_pattern, from_date):
            raise ToolExecutionError(
                "from_date must be in YYYY-MM-DD format",
                error_type="ValidationError",
                context={"from_date": from_date}
            )
        
        if not re.match(date_pattern, to_date):
            raise ToolExecutionError(
                "to_date must be in YYYY-MM-DD format",
                error_type="ValidationError",
                context={"to_date": to_date}
            )
        
        # Validate date range logic
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            
            if to_dt < from_dt:
                raise ToolExecutionError(
                    "to_date must be after from_date",
                    error_type="ValidationError",
                    context={"from_date": from_date, "to_date": to_date}
                )
            
            return from_dt, to_dt
            
        except ValueError as e:
            raise ToolExecutionError(
                f"Invalid date format: {str(e)}",
                error_type="ValidationError",
                context={"from_date": from_date, "to_date": to_date}
            )


class AssetTool(BaseTool):
    """Base class for asset-related tools (captions, attachments)."""
    
    def validate_asset_id(self, asset_id: str) -> str:
        """Validate asset ID format."""
        if not asset_id or not isinstance(asset_id, str):
            raise ToolExecutionError(
                "Asset ID is required and must be a string",
                error_type="ValidationError",
                context={"asset_id": asset_id}
            )
        
        # Basic format validation (can be enhanced based on Kaltura specs)
        if len(asset_id) < 3 or len(asset_id) > 50:
            raise ToolExecutionError(
                "Asset ID must be between 3 and 50 characters",
                error_type="ValidationError",
                context={"asset_id": asset_id}
            )
        
        return asset_id
```

### 2. Create Tool Registry System (60 minutes)
**File: `src/kaltura_mcp/tool_registry.py`**
```python
"""Tool registry system for managing and executing MCP tools."""

import logging
from typing import Dict, List, Type, Optional, Any, Set
from collections import defaultdict
import importlib
import pkgutil

import mcp.types as types
from .tools.base import BaseTool, ToolExecutionError
from .kaltura_client import KalturaClientManager

logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Exception raised by tool registry operations."""
    pass


class ToolRegistry:
    """Registry for managing and executing MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        self._categories: Dict[str, Set[str]] = defaultdict(set)
        self._initialized = False
        
        logger.info("Tool registry initialized")
    
    def register(self, tool_class: Type[BaseTool], category: Optional[str] = None) -> None:
        """
        Register a tool class in the registry.
        
        Args:
            tool_class: The tool class to register
            category: Optional category for organization
            
        Raises:
            ToolRegistryError: If tool is already registered or invalid
        """
        # Create tool instance to get name
        try:
            tool_instance = tool_class()
        except Exception as e:
            raise ToolRegistryError(f"Failed to instantiate tool {tool_class.__name__}: {e}")
        
        tool_name = tool_instance.name
        
        # Check for duplicate registration
        if tool_name in self._tools:
            existing_class = self._tool_classes[tool_name]
            if existing_class != tool_class:
                raise ToolRegistryError(
                    f"Tool '{tool_name}' already registered with different class "
                    f"(existing: {existing_class.__name__}, new: {tool_class.__name__})"
                )
            logger.debug(f"Tool '{tool_name}' already registered, skipping")
            return
        
        # Validate tool
        self._validate_tool(tool_instance)
        
        # Register tool
        self._tools[tool_name] = tool_instance
        self._tool_classes[tool_name] = tool_class
        
        # Add to category
        if category:
            self._categories[category].add(tool_name)
        
        logger.info(f"Registered tool: {tool_name} ({tool_class.__name__})")
    
    def _validate_tool(self, tool: BaseTool) -> None:
        """Validate tool implementation."""
        errors = []
        
        # Check required attributes
        if not tool.name:
            errors.append("Tool name cannot be empty")
        
        if not tool.description:
            errors.append("Tool description cannot be empty")
        
        if not isinstance(tool.input_schema, dict):
            errors.append("Tool input_schema must be a dictionary")
        
        # Validate schema structure
        schema = tool.input_schema
        if 'type' not in schema:
            errors.append("Tool input_schema must have 'type' field")
        
        if schema.get('type') != 'object':
            errors.append("Tool input_schema type must be 'object'")
        
        if 'properties' not in schema:
            errors.append("Tool input_schema must have 'properties' field")
        
        if errors:
            raise ToolRegistryError(f"Tool validation failed: {'; '.join(errors)}")
    
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name not in self._tools:
            return False
        
        # Remove from tools
        del self._tools[tool_name]
        del self._tool_classes[tool_name]
        
        # Remove from categories
        for category_tools in self._categories.values():
            category_tools.discard(tool_name)
        
        logger.info(f"Unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[types.Tool]:
        """Get all registered tools as MCP Tool definitions."""
        return [tool.to_mcp_tool() for tool in self._tools.values()]
    
    def list_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tool names in a specific category."""
        return list(self._categories.get(category, set()))
    
    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self._categories.keys())
    
    async def execute(self, name: str, manager: KalturaClientManager, **kwargs) -> str:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name to execute
            manager: Kaltura client manager
            **kwargs: Tool arguments
            
        Returns:
            JSON string response
            
        Raises:
            ToolRegistryError: If tool not found
            ToolExecutionError: If tool execution fails
        """
        tool = self.get_tool(name)
        if not tool:
            available_tools = ', '.join(self.list_tool_names())
            raise ToolRegistryError(
                f"Unknown tool: {name}. Available tools: {available_tools}"
            )
        
        logger.info(f"Executing tool: {name}")
        logger.debug(f"Tool arguments: {kwargs}")
        
        try:
            # Validate input parameters
            validated_kwargs = tool.validate_input(**kwargs)
            
            # Execute tool
            result = await tool.execute(manager, **validated_kwargs)
            
            logger.info(f"Tool execution completed: {name}")
            return result
            
        except ToolExecutionError:
            # Re-raise tool execution errors as-is
            raise
        except Exception as e:
            # Wrap unexpected errors
            logger.error(f"Unexpected error in tool {name}: {e}", exc_info=True)
            raise ToolExecutionError(
                f"Unexpected error in tool execution: {str(e)}",
                error_type=type(e).__name__,
                context={"tool": name, "arguments": kwargs}
            )
    
    def auto_discover(self, package_name: str = "kaltura_mcp.tools") -> int:
        """
        Automatically discover and register tools from a package.
        
        Args:
            package_name: Package to search for tools
            
        Returns:
            Number of tools discovered and registered
        """
        if self._initialized:
            logger.debug("Tool registry already initialized, skipping auto-discovery")
            return len(self._tools)
        
        discovered_count = 0
        
        try:
            # Import the tools package
            tools_package = importlib.import_module(package_name)
            
            # Walk through all modules in the package
            for importer, modname, ispkg in pkgutil.iter_modules(
                tools_package.__path__, 
                tools_package.__name__ + "."
            ):
                if modname.endswith('.base'):
                    continue  # Skip base module
                
                try:
                    # Import the module
                    module = importlib.import_module(modname)
                    logger.debug(f"Scanning module: {modname}")
                    
                    # Look for BaseTool subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # Check if it's a tool class
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseTool) and 
                            attr != BaseTool and
                            not attr.__name__.startswith('_')):
                            
                            try:
                                # Determine category from module name
                                module_parts = modname.split('.')
                                category = module_parts[-1] if len(module_parts) > 1 else None
                                
                                self.register(attr, category)
                                discovered_count += 1
                                
                            except ToolRegistryError as e:
                                logger.warning(f"Failed to register tool {attr.__name__}: {e}")
                
                except ImportError as e:
                    logger.warning(f"Failed to import module {modname}: {e}")
                except Exception as e:
                    logger.error(f"Error processing module {modname}: {e}")
        
        except ImportError as e:
            logger.error(f"Failed to import tools package {package_name}: {e}")
        
        self._initialized = True
        logger.info(f"Auto-discovery completed: {discovered_count} tools registered")
        return discovered_count
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get information about the current registry state."""
        return {
            "total_tools": len(self._tools),
            "tools": list(self._tools.keys()),
            "categories": {cat: list(tools) for cat, tools in self._categories.items()},
            "initialized": self._initialized
        }


# Global registry instance
registry = ToolRegistry()


def register_tool(category: Optional[str] = None):
    """
    Decorator for registering tool classes.
    
    Args:
        category: Optional category for the tool
        
    Example:
        @register_tool("media")
        class GetMediaEntryTool(MediaTool):
            ...
    """
    def decorator(cls: Type[BaseTool]) -> Type[BaseTool]:
        registry.register(cls, category)
        return cls
    
    return decorator


def get_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return registry
```

### 3. Create Utility Functions (30 minutes)
**File: `src/kaltura_mcp/tools/utils.py`** (Enhanced)
```python
"""Enhanced utilities for Kaltura MCP tools."""

import re
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_serialize_kaltura_field(field: Any) -> Any:
    """Safely serialize Kaltura enum/object fields to JSON-compatible values."""
    if field is None:
        return None
    if hasattr(field, 'value'):
        return field.value
    return str(field)


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
    dangerous_chars = ['$', '`', ';', '&', '|', '<', '>', '"', "'"]
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
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    # Additional validation: check if it's a real date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_timestamp(timestamp: Optional[int]) -> Optional[str]:
    """
    Format Unix timestamp to ISO format.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        ISO formatted datetime string or None
    """
    if timestamp is None:
        return None
    
    try:
        return datetime.fromtimestamp(timestamp).isoformat()
    except (ValueError, TypeError, OSError):
        logger.warning(f"Invalid timestamp: {timestamp}")
        return None


def clean_string(value: Any) -> Optional[str]:
    """
    Clean and validate string input.
    
    Args:
        value: Value to clean
        
    Returns:
        Cleaned string or None
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace
    value = value.strip()
    
    # Return None for empty strings
    if not value:
        return None
    
    return value


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
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


def parse_kaltura_response(response: Any) -> Dict[str, Any]:
    """
    Parse and structure Kaltura API response.
    
    Args:
        response: Raw Kaltura response object
        
    Returns:
        Structured dictionary
    """
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
    """
    Parse a single Kaltura object into a dictionary.
    
    Args:
        obj: Kaltura object
        
    Returns:
        Dictionary representation
    """
    if not obj:
        return {}
    
    result = {}
    
    # Get all attributes that don't start with underscore
    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue
        
        try:
            attr_value = getattr(obj, attr_name)
            
            # Skip methods
            if callable(attr_value):
                continue
            
            # Serialize the value
            result[attr_name] = safe_serialize_kaltura_field(attr_value)
            
        except (AttributeError, TypeError):
            # Skip attributes that can't be accessed
            continue
    
    return result


def build_error_response(error: Exception, operation: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build standardized error response.
    
    Args:
        error: Exception that occurred
        operation: Operation that failed
        context: Additional context
        
    Returns:
        Error response dictionary
    """
    error_context = context or {}
    
    return {
        "error": f"Failed to {operation}: {str(error)}",
        "errorType": type(error).__name__,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        **error_context
    }


def validate_limit_offset(limit: Optional[int] = None, 
                         offset: Optional[int] = None) -> tuple:
    """
    Validate and normalize limit/offset parameters.
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Tuple of (validated_limit, validated_offset)
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Validate limit
    if limit is None:
        limit = 20  # Default
    
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer")
    
    if limit > 100:
        limit = 100  # Cap at 100
    
    # Validate offset
    if offset is None:
        offset = 0  # Default
    
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("Offset must be a non-negative integer")
    
    return limit, offset
```

### 4. Refactor Example Tool to Use New Pattern (45 minutes)
**File: `src/kaltura_mcp/tools/media.py`** (New implementation)
```python
"""Media entry related tools using the new registry pattern."""

import json
from typing import Dict, Any, Optional

from .base import MediaTool
from .utils import safe_serialize_kaltura_field, format_timestamp, parse_kaltura_object
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
            
            # Build response
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
                }
            },
            "required": ["entry_id"],
            "additionalProperties": False
        }
    
    async def execute(self, manager, entry_id: str, width: int = 120, 
                     height: int = 90, second: int = 5) -> str:
        """Execute the get thumbnail URL tool."""
        try:
            # Validate entry ID
            entry_id = self.validate_entry_id(entry_id)
            
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
            params = [f"width={width}", f"height={height}"]
            
            # Add video-specific parameters
            from KalturaClient.Plugins.Core import KalturaMediaType
            if hasattr(entry, 'mediaType') and entry.mediaType == KalturaMediaType.VIDEO:
                params.append(f"vid_sec={second}")
            
            # Construct final URL
            separator = "&" if "?" in entry.thumbnailUrl else "?"
            thumbnail_url = entry.thumbnailUrl + separator + "&".join(params)
            
            response_data = {
                "entryId": entry_id,
                "entryName": entry.name,
                "mediaType": safe_serialize_kaltura_field(entry.mediaType),
                "thumbnailUrl": thumbnail_url,
                "parameters": {
                    "width": width,
                    "height": height,
                    "second": second if hasattr(entry, 'mediaType') and entry.mediaType == KalturaMediaType.VIDEO else None
                }
            }
            
            return self.format_success_response(response_data)
            
        except Exception as e:
            return self.handle_error(e, "get thumbnail URL", {
                "entry_id": entry_id,
                "width": width,
                "height": height,
                "second": second
            })
```

### 5. Update Servers to Use Registry (60 minutes)
**File: `src/kaltura_mcp/server.py`** (Updated sections)
```python
"""Local MCP server using the tool registry pattern."""

import logging
import sys
import asyncio
import traceback
from typing import Any, Dict, List

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import load_config
from .kaltura_client import KalturaClientManager
from .tool_registry import get_registry, ToolRegistryError
from .tools.base import ToolExecutionError

logger = logging.getLogger(__name__)

# Initialize server and registry
server = Server("kaltura-mcp")
registry = get_registry()

# Global configuration and manager
config = None
kaltura_manager = None


def initialize_server():
    """Initialize server with configuration and tools."""
    global config, kaltura_manager
    
    try:
        # Load configuration from environment
        config = load_config(include_server=False)
        logger.info("Configuration loaded successfully")
        
        # Initialize Kaltura client manager
        kaltura_manager = KalturaClientManager(config.kaltura)
        
        # Validate configuration
        if not kaltura_manager.has_required_config():
            logger.error("Invalid Kaltura configuration")
            sys.exit(1)
        
        # Auto-discover and register tools
        tool_count = registry.auto_discover()
        logger.info(f"Initialized server with {tool_count} tools")
        
        # Log registered tools in debug mode
        if config.debug:
            registry_info = registry.get_registry_info()
            logger.debug(f"Registry info: {registry_info}")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        if config and config.debug:
            traceback.print_exc()
        sys.exit(1)


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List all available tools from the registry."""
    try:
        tools = registry.list_tools()
        logger.debug(f"Listed {len(tools)} tools")
        return tools
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        return []


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution requests using the registry."""
    try:
        logger.info(f"Executing tool: {name}")
        logger.debug(f"Tool arguments: {arguments}")
        
        # Execute tool through registry
        result = await registry.execute(name, kaltura_manager, **arguments)
        
        logger.info(f"Tool execution completed: {name}")
        return [types.TextContent(type="text", text=result)]
        
    except ToolRegistryError as e:
        logger.error(f"Tool registry error: {e}")
        error_response = {
            "error": str(e),
            "errorType": "ToolRegistryError",
            "availableTools": registry.list_tool_names()
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except ToolExecutionError as e:
        logger.error(f"Tool execution error: {e}")
        error_response = {
            "error": str(e),
            "errorType": e.error_type,
            "context": e.context
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
    except Exception as e:
        logger.error(f"Unexpected error executing tool {name}: {e}", exc_info=True)
        error_response = {
            "error": f"Unexpected error: {str(e)}",
            "errorType": type(e).__name__,
            "tool": name
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def async_main():
    """Run the Kaltura MCP server."""
    # Initialize server
    initialize_server()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        if config and config.debug:
            traceback.print_exc()


def main():
    """Entry point for the CLI script."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
```

**File: `src/kaltura_mcp/remote_server.py`** (Updated sections)
```python
"""Remote MCP server using the tool registry pattern."""

import json
import logging
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import load_config, ServerConfig
from .kaltura_client import KalturaClientManager
from .tool_registry import get_registry, ToolRegistryError
from .tools.base import ToolExecutionError

logger = logging.getLogger(__name__)

# Initialize registry
registry = get_registry()

# Global configuration
config = None


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    global config
    
    # Load configuration
    config = load_config(include_server=True)
    
    # Auto-discover tools
    tool_count = registry.auto_discover()
    logger.info(f"Initialized remote server with {tool_count} tools")
    
    # Create FastAPI app
    app = FastAPI(
        title="Kaltura MCP Remote Server",
        description="Remote MCP server for Kaltura API operations",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()


@app.get("/mcp/tools")
async def get_available_tools():
    """Get list of available tools."""
    try:
        tools = registry.list_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ],
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"Failed to get tools: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tools")


@app.post("/mcp/tools/{tool_name}")
async def execute_tool(tool_name: str, request: Request):
    """Execute a specific tool."""
    try:
        # Get request body
        body = await request.json()
        
        # Extract arguments (handle different MCP message formats)
        if "arguments" in body:
            arguments = body["arguments"]
        elif "params" in body:
            arguments = body["params"]
        else:
            arguments = body
        
        # Get JWT token and extract Kaltura config
        # (This would require JWT token validation - simplified here)
        # kaltura_config = extract_kaltura_config_from_jwt(request)
        # manager = KalturaClientManager(kaltura_config)
        
        # For demo, create a basic manager (in real implementation, 
        # this would come from JWT token)
        manager = KalturaClientManager()
        
        # Execute tool
        result = await registry.execute(tool_name, manager, **arguments)
        
        return {"result": json.loads(result)}
        
    except ToolRegistryError as e:
        logger.error(f"Tool registry error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except ToolExecutionError as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=400, detail={
            "error": str(e),
            "type": e.error_type,
            "context": e.context
        })
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# Include other routes (OAuth, etc.) from original implementation...


if __name__ == "__main__":
    import uvicorn
    
    server_config = config.server if config else ServerConfig.from_env()
    
    uvicorn.run(
        "kaltura_mcp.remote_server:app",
        host=server_config.server_host,
        port=server_config.server_port,
        reload=server_config.server_reload,
        log_level=server_config.log_level.lower()
    )


def main():
    """Entry point for remote server CLI."""
    import uvicorn
    
    server_config = ServerConfig.from_env()
    
    uvicorn.run(
        "kaltura_mcp.remote_server:app",
        host=server_config.server_host,
        port=server_config.server_port,
        reload=server_config.server_reload,
        log_level=server_config.log_level.lower()
    )
```

### 6. Update Tools Package Structure (30 minutes)
**File: `src/kaltura_mcp/tools/__init__.py`** (Updated)
```python
"""Kaltura MCP tools package with registry pattern."""

# Import all tool modules to trigger registration
from . import media
from . import search  # Will be created
from . import analytics  # Will be created
from . import assets  # Will be created

# Export registry and utilities
from ..tool_registry import get_registry, register_tool
from .utils import validate_entry_id, format_timestamp, safe_serialize_kaltura_field
from .base import BaseTool, MediaTool, SearchTool, AnalyticsTool, AssetTool

__all__ = [
    'get_registry',
    'register_tool', 
    'validate_entry_id',
    'format_timestamp',
    'safe_serialize_kaltura_field',
    'BaseTool',
    'MediaTool',
    'SearchTool', 
    'AnalyticsTool',
    'AssetTool'
]
```

## Testing the Tool Registry

### 1. Test Registry Functionality
```python
# Test script: test_registry.py
from kaltura_mcp.tool_registry import get_registry
from kaltura_mcp.config import KalturaConfig
from kaltura_mcp.kaltura_client import KalturaClientManager

# Get registry
registry = get_registry()

# Auto-discover tools
tool_count = registry.auto_discover()
print(f"Discovered {tool_count} tools")

# List tools
tools = registry.list_tool_names()
print(f"Available tools: {tools}")

# Get registry info
info = registry.get_registry_info()
print(f"Registry info: {info}")

# Test tool execution (with mock config)
config = KalturaConfig(
    service_url="https://test.kaltura.com",
    partner_id=12345,
    admin_secret="test_secret_12345678",
    user_id="test@example.com"
)
manager = KalturaClientManager(config)

# This would require valid credentials to actually work
# result = await registry.execute("get_media_entry", manager, entry_id="1_test123")
```

### 2. Create Tests for Registry
```python
# tests/unit/test_tool_registry.py
import pytest
from kaltura_mcp.tool_registry import ToolRegistry, register_tool
from kaltura_mcp.tools.base import BaseTool


class MockTool(BaseTool):
    @property
    def name(self):
        return "mock_tool"
    
    @property 
    def description(self):
        return "A mock tool for testing"
    
    @property
    def input_schema(self):
        return {"type": "object", "properties": {}}
    
    async def execute(self, manager, **kwargs):
        return '{"result": "mock"}'


def test_tool_registration():
    registry = ToolRegistry()
    registry.register(MockTool, "test")
    
    assert "mock_tool" in registry.list_tool_names()
    assert len(registry.get_tools_by_category("test")) == 1


def test_auto_discovery():
    registry = ToolRegistry()
    count = registry.auto_discover("kaltura_mcp.tools")
    assert count > 0
```

## Benefits
- ✅ Eliminates code duplication between servers
- ✅ Centralized tool management
- ✅ Type-safe tool execution
- ✅ Automatic tool discovery
- ✅ Consistent error handling
- ✅ Easy to add new tools
- ✅ Category-based organization
- ✅ Comprehensive validation
- ✅ Better testing support
- ✅ Improved maintainability

## Files Created
- `src/kaltura_mcp/tools/base.py`
- `src/kaltura_mcp/tool_registry.py`
- `src/kaltura_mcp/tools/media.py` (refactored)

## Files Modified
- `src/kaltura_mcp/tools/utils.py` (enhanced)
- `src/kaltura_mcp/tools/__init__.py`
- `src/kaltura_mcp/server.py`
- `src/kaltura_mcp/remote_server.py`

## Next Steps
1. Refactor remaining tools to use the new pattern
2. Add comprehensive tests for the registry
3. Create tools for search, analytics, and assets modules
4. Add tool dependency management
5. Implement tool versioning system