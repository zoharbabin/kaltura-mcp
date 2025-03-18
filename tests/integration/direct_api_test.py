#!/usr/bin/env python
"""
Direct test script to demonstrate API calls with enhanced logging.
"""
import os
import sys
import logging
import asyncio
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import our enhanced client
from tests.integration.enhanced_client import EnhancedKalturaClientWrapper
from tests.integration.conftest import load_integration_config

# Configure root logger to show all logs
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)

# Make sure our API logger is set to INFO
api_logger = logging.getLogger("kaltura_api_calls")
api_logger.setLevel(logging.INFO)

# Add a console handler to ensure output goes to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
api_logger.addHandler(handler)
api_logger.propagate = True  # Make sure logs propagate to parent loggers

async def run_test():
    """Run a direct test of the Kaltura API with enhanced logging."""
    print("Starting direct API test with enhanced logging")
    print("-" * 80)
    
    try:
        # Load configuration
        config = load_integration_config()
        print(f"Loaded configuration with partner ID: {config.kaltura.partner_id}")
        
        # Create enhanced client
        client = EnhancedKalturaClientWrapper(config)
        await client.initialize()
        print(f"Client initialized with service URL: {client.get_service_url()}")
        
        # Make API calls
        print("\n1. Testing media.list API call:")
        media_list = await client.execute_request("media", "list")
        print(f"Retrieved {len(media_list.objects) if hasattr(media_list, 'objects') else 0} media entries")
        
        print("\n2. Testing category.list API call:")
        category_list = await client.execute_request("category", "list")
        print(f"Retrieved {len(category_list.objects) if hasattr(category_list, 'objects') else 0} categories")
        
        print("\n3. Testing user.list API call:")
        user_list = await client.execute_request("user", "list")
        print(f"Retrieved {len(user_list.objects) if hasattr(user_list, 'objects') else 0} users")
        
        print("\nAPI test completed successfully")
        
    except Exception as e:
        print(f"Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_test())
    sys.exit(exit_code)