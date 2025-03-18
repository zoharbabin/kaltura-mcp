"""
Enhanced Kaltura client wrapper for integration tests with detailed logging.
"""
import time
import logging
import json
from typing import Any, Dict, Optional

from KalturaClient import KalturaClient, KalturaConfiguration
from KalturaClient.exceptions import KalturaException, KalturaClientException
from KalturaClient.Plugins.Core import KalturaSessionType

from kaltura_mcp.kaltura.client import KalturaClientWrapper

# Set up a dedicated logger for API calls
api_logger = logging.getLogger("kaltura_api_calls")

class EnhancedKalturaClientWrapper(KalturaClientWrapper):
    """Enhanced wrapper for the Kaltura client SDK with detailed logging."""
    
    async def execute_request(self, service: str, action: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Execute a Kaltura API request with detailed logging."""
        # Ensure valid KS
        await self.ensure_valid_ks()
        
        # Initialize params if None
        if params is None:
            params = {}
            
        # Handle any additional keyword arguments
        params.update(kwargs)
        
        # Get service
        service_obj = getattr(self.client, service)
        if not service_obj:
            raise ValueError("Unknown service: " + service)
        
        # Get action
        action_func = getattr(service_obj, action)
        if not action_func:
            raise ValueError("Unknown action: " + action)
        
        # Log the request details
        request_id = f"{service}.{action}_{int(time.time() * 1000)}"
        
        # Format parameters for logging, handling complex objects
        log_params = {}
        for key, value in params.items():
            if hasattr(value, '__dict__'):
                # For Kaltura objects, get their properties
                obj_dict = {}
                for attr in dir(value):
                    if not attr.startswith('_') and not callable(getattr(value, attr)):
                        obj_dict[attr] = str(getattr(value, attr))
                log_params[key] = obj_dict
            else:
                log_params[key] = str(value)
        
        api_logger.info(f"API REQUEST [{request_id}]: {service}.{action}")
        api_logger.info(f"API PARAMS [{request_id}]: {json.dumps(log_params, indent=2)}")
        
        # Execute request
        start_time = time.time()
        try:
            result = None
            if params:
                result = action_func(**params)
            else:
                result = action_func()
            
            # Log the response
            execution_time = time.time() - start_time
            api_logger.info(f"API RESPONSE [{request_id}]: Success (took {execution_time:.2f}s)")
            
            # Log response details if possible
            try:
                if hasattr(result, '__dict__'):
                    result_dict = {}
                    for attr in dir(result):
                        if not attr.startswith('_') and not callable(getattr(result, attr)):
                            result_dict[attr] = str(getattr(result, attr))
                    api_logger.info(f"API RESULT [{request_id}]: {json.dumps(result_dict, indent=2)}")
                elif hasattr(result, 'objects'):
                    # For list responses
                    api_logger.info(f"API RESULT [{request_id}]: List with {len(result.objects)} items")
                    if result.objects and len(result.objects) > 0:
                        # Log first item as example
                        first_item = result.objects[0]
                        first_item_dict = {}
                        for attr in dir(first_item):
                            if not attr.startswith('_') and not callable(getattr(first_item, attr)):
                                first_item_dict[attr] = str(getattr(first_item, attr))
                        api_logger.info(f"API RESULT FIRST ITEM [{request_id}]: {json.dumps(first_item_dict, indent=2)}")
            except (TypeError, ValueError, AttributeError) as e:
                api_logger.info(f"API RESULT [{request_id}]: Could not serialize result: {e}")
            
            return result
            
        except (KalturaException, KalturaClientException) as e:
            # Log the error
            execution_time = time.time() - start_time
            api_logger.error(f"API ERROR [{request_id}]: {e} (took {execution_time:.2f}s)")
            
            # Translate Kaltura exceptions to MCP-friendly exceptions
            from kaltura_mcp.kaltura.errors import translate_kaltura_error
            raise translate_kaltura_error(e)