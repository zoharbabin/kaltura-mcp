"""
Base classes for Kaltura tool handlers.
"""
import json
import mcp.types as types
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class KalturaJSONEncoder(json.JSONEncoder):
    '''JSON encoder that can handle Kaltura objects.'''
    
    def default(self, obj):
        '''Handle Kaltura objects by converting them to their value.'''
        # Handle Kaltura enum types that have a 'value' attribute
        if hasattr(obj, 'value'):
            return obj.value
        
        # Handle other Kaltura objects by converting to dict
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        
        # Let the base class handle it
        return super().default(obj)


class KalturaJSONEncoder(json.JSONEncoder):
    '''JSON encoder that can handle Kaltura objects.'''
    
    def default(self, obj):
        '''Handle Kaltura objects by converting them to their value.'''
        # Handle Kaltura enum types that have a 'value' attribute
        if hasattr(obj, 'value'):
            return obj.value
        
        # Handle other Kaltura objects by converting to dict
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        
        # Let the base class handle it
        return super().default(obj)

class KalturaJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Kaltura objects."""
    
    def default(self, obj):
        """Handle special Kaltura types."""
        # Handle objects with a value attribute
        if hasattr(obj, 'value'):
            return obj.value
        
        # Handle NotImplementedType
        if str(type(obj)) == "<class 'NotImplementedType'>":
            return None
            
        # Let the base class handle everything else
        return super().default(obj)

class KalturaToolHandler(ABC):
    """Base class for Kaltura tool handlers."""
    
    def __init__(self, kaltura_client):
        """Initialize with a Kaltura client."""
        self.kaltura_client = kaltura_client
    
    @abstractmethod
    async def handle(self, arguments: Dict[str, Any]) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        """Handle a tool request with the given arguments."""
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Return the tool definition."""
        pass
    
    def _validate_required_params(self, arguments: Dict[str, Any], required_params: List[str]) -> None:
        """Validate that required parameters are present."""
        for param in required_params:
            if param not in arguments:
                raise ValueError(f"Missing required parameter: {param}")