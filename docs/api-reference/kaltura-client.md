# Kaltura Client

This page documents the Kaltura client wrapper used in the Kaltura-MCP Server.

## Overview

The `KalturaClientWrapper` class is a wrapper around the kaltura-client-py SDK that provides a simplified interface for interacting with the Kaltura API. It handles authentication, session management, error handling, and provides methods for common Kaltura API operations.

## KalturaClientWrapper Class

```python
class KalturaClientWrapper:
    """Wrapper for the Kaltura client."""
    
    def __init__(self, config):
        """Initialize the wrapper with configuration."""
        self.config = config
        self.client = None
        self.session = None
        self.session_expiry = None
    
    async def initialize(self):
        """Initialize the Kaltura client."""
        # Create Kaltura client
        self.client = KalturaClient(KalturaConfiguration(
            serviceUrl=self.config["kaltura"]["service_url"]
        ))
        
        # Start session
        await self._start_session()
    
    async def _start_session(self):
        """Start a Kaltura session."""
        # Check if we need to start a new session
        if self.session is None or self._is_session_expired():
            # Start admin session
            self.session = await self._start_admin_session()
            
            # Set session in client
            self.client.setKs(self.session)
            
            # Set session expiry
            self.session_expiry = time.time() + self.config["kaltura"]["session_duration"] - 60
    
    async def _start_admin_session(self):
        """Start an admin session."""
        # Create session service
        session_service = KalturaSessionService(self.client)
        
        # Start session
        result = await session_service.start(
            self.config["kaltura"]["admin_secret"],
            self.config["kaltura"]["user_id"],
            KalturaSessionType.ADMIN,
            self.config["kaltura"]["partner_id"],
            self.config["kaltura"]["session_duration"],
            self.config["kaltura"]["session_privileges"]
        )
        
        return result
    
    def _is_session_expired(self):
        """Check if the session is expired."""
        return self.session_expiry is not None and time.time() > self.session_expiry
    
    async def _ensure_session(self):
        """Ensure that we have a valid session."""
        if self.session is None or self._is_session_expired():
            await self._start_session()
```

## Media Methods

The `KalturaClientWrapper` class provides methods for working with media entries:

### List Media

```python
async def list_media(self, params=None):
    """List media entries."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create media service
    media_service = KalturaMediaService(self.client)
    
    # Create filter
    filter = KalturaMediaEntryFilter()
    
    # Apply filter parameters
    if params and "filter" in params:
        for key, value in params["filter"].items():
            if hasattr(filter, key):
                setattr(filter, key, value)
    
    # Create pager
    pager = KalturaFilterPager()
    if params:
        if "page_size" in params:
            pager.pageSize = params["page_size"]
        if "page_index" in params:
            pager.pageIndex = params["page_index"]
    
    # List media entries
    result = await media_service.list(filter, pager)
    
    # Convert to dict
    return self._to_dict(result)
```

### Get Media

```python
async def get_media(self, entry_id):
    """Get a media entry."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create media service
    media_service = KalturaMediaService(self.client)
    
    # Get media entry
    result = await media_service.get(entry_id)
    
    # Convert to dict
    return self._to_dict(result)
```

### Upload Media

```python
async def upload_media(self, file_path, name=None, description=None, tags=None, media_type=KalturaMediaType.VIDEO):
    """Upload a media entry."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create media service
    media_service = KalturaMediaService(self.client)
    
    # Create upload token service
    upload_token_service = KalturaUploadTokenService(self.client)
    
    # Create media entry
    entry = KalturaMediaEntry()
    entry.mediaType = media_type
    if name:
        entry.name = name
    if description:
        entry.description = description
    if tags:
        entry.tags = tags
    
    # Add media entry
    entry = await media_service.add(entry)
    
    # Create upload token
    upload_token = KalturaUploadToken()
    upload_token = await upload_token_service.add(upload_token)
    
    # Upload file
    upload_token = await upload_token_service.upload(upload_token.id, file_path)
    
    # Add content to media entry
    resource = KalturaUploadedFileTokenResource()
    resource.token = upload_token.id
    entry = await media_service.addContent(entry.id, resource)
    
    # Convert to dict
    return self._to_dict(entry)
```

### Update Media

```python
async def update_media(self, entry_id, name=None, description=None, tags=None):
    """Update a media entry."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create media service
    media_service = KalturaMediaService(self.client)
    
    # Get current entry
    entry = await media_service.get(entry_id)
    
    # Update fields
    if name:
        entry.name = name
    if description:
        entry.description = description
    if tags:
        entry.tags = tags
    
    # Update entry
    result = await media_service.update(entry_id, entry)
    
    # Convert to dict
    return self._to_dict(result)
```

### Delete Media

```python
async def delete_media(self, entry_id):
    """Delete a media entry."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create media service
    media_service = KalturaMediaService(self.client)
    
    # Delete entry
    await media_service.delete(entry_id)
    
    return {"success": True}
```

## Category Methods

The `KalturaClientWrapper` class provides methods for working with categories:

### List Categories

```python
async def list_categories(self, params=None):
    """List categories."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create category service
    category_service = KalturaCategoryService(self.client)
    
    # Create filter
    filter = KalturaCategoryFilter()
    
    # Apply filter parameters
    if params and "filter" in params:
        for key, value in params["filter"].items():
            if hasattr(filter, key):
                setattr(filter, key, value)
    
    # Create pager
    pager = KalturaFilterPager()
    if params:
        if "page_size" in params:
            pager.pageSize = params["page_size"]
        if "page_index" in params:
            pager.pageIndex = params["page_index"]
    
    # List categories
    result = await category_service.list(filter, pager)
    
    # Convert to dict
    return self._to_dict(result)
```

### Get Category

```python
async def get_category(self, category_id):
    """Get a category."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create category service
    category_service = KalturaCategoryService(self.client)
    
    # Get category
    result = await category_service.get(category_id)
    
    # Convert to dict
    return self._to_dict(result)
```

### Add Category

```python
async def add_category(self, name, description=None, parent_id=None, tags=None):
    """Add a category."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create category service
    category_service = KalturaCategoryService(self.client)
    
    # Create category
    category = KalturaCategory()
    category.name = name
    if description:
        category.description = description
    if parent_id:
        category.parentId = parent_id
    if tags:
        category.tags = tags
    
    # Add category
    result = await category_service.add(category)
    
    # Convert to dict
    return self._to_dict(result)
```

### Update Category

```python
async def update_category(self, category_id, name=None, description=None, tags=None):
    """Update a category."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create category service
    category_service = KalturaCategoryService(self.client)
    
    # Get current category
    category = await category_service.get(category_id)
    
    # Update fields
    if name:
        category.name = name
    if description:
        category.description = description
    if tags:
        category.tags = tags
    
    # Update category
    result = await category_service.update(category_id, category)
    
    # Convert to dict
    return self._to_dict(result)
```

### Delete Category

```python
async def delete_category(self, category_id, move_entries_to_parent=True):
    """Delete a category."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create category service
    category_service = KalturaCategoryService(self.client)
    
    # Delete category
    await category_service.delete(category_id, move_entries_to_parent)
    
    return {"success": True}
```

## User Methods

The `KalturaClientWrapper` class provides methods for working with users:

### List Users

```python
async def list_users(self, params=None):
    """List users."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create user service
    user_service = KalturaUserService(self.client)
    
    # Create filter
    filter = KalturaUserFilter()
    
    # Apply filter parameters
    if params and "filter" in params:
        for key, value in params["filter"].items():
            if hasattr(filter, key):
                setattr(filter, key, value)
    
    # Create pager
    pager = KalturaFilterPager()
    if params:
        if "page_size" in params:
            pager.pageSize = params["page_size"]
        if "page_index" in params:
            pager.pageIndex = params["page_index"]
    
    # List users
    result = await user_service.list(filter, pager)
    
    # Convert to dict
    return self._to_dict(result)
```

### Get User

```python
async def get_user(self, user_id):
    """Get a user."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create user service
    user_service = KalturaUserService(self.client)
    
    # Get user
    result = await user_service.get(user_id)
    
    # Convert to dict
    return self._to_dict(result)
```

### Add User

```python
async def add_user(self, user_id, email, first_name, last_name, screen_name=None, password=None, is_admin=False):
    """Add a user."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create user service
    user_service = KalturaUserService(self.client)
    
    # Create user
    user = KalturaUser()
    user.id = user_id
    user.email = email
    user.firstName = first_name
    user.lastName = last_name
    if screen_name:
        user.screenName = screen_name
    if is_admin:
        user.isAdmin = is_admin
    
    # Add user
    result = await user_service.add(user, password)
    
    # Convert to dict
    return self._to_dict(result)
```

### Update User

```python
async def update_user(self, user_id, email=None, first_name=None, last_name=None, screen_name=None, password=None, is_admin=None):
    """Update a user."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create user service
    user_service = KalturaUserService(self.client)
    
    # Get current user
    user = await user_service.get(user_id)
    
    # Update fields
    if email:
        user.email = email
    if first_name:
        user.firstName = first_name
    if last_name:
        user.lastName = last_name
    if screen_name:
        user.screenName = screen_name
    if is_admin is not None:
        user.isAdmin = is_admin
    
    # Update user
    result = await user_service.update(user_id, user)
    
    # If password is provided, update it separately
    if password:
        await user_service.setInitialPassword(user_id, password)
    
    # Convert to dict
    return self._to_dict(result)
```

### Delete User

```python
async def delete_user(self, user_id):
    """Delete a user."""
    # Ensure we have a valid session
    await self._ensure_session()
    
    # Create user service
    user_service = KalturaUserService(self.client)
    
    # Delete user
    await user_service.delete(user_id)
    
    return {"success": True}
```

## Utility Methods

The `KalturaClientWrapper` class provides utility methods for working with Kaltura objects:

### Convert to Dictionary

```python
def _to_dict(self, obj):
    """Convert a Kaltura object to a dictionary."""
    if isinstance(obj, KalturaObjectBase):
        result = {}
        for attr, value in vars(obj).items():
            if not attr.startswith("_") and value is not None:
                result[attr] = self._to_dict(value)
        return result
    elif isinstance(obj, list):
        return [self._to_dict(item) for item in obj]
    else:
        return obj
```

## Error Handling

The `KalturaClientWrapper` class handles Kaltura API errors and translates them to MCP errors:

```python
try:
    # Call Kaltura API
    result = await media_service.list(filter, pager)
    return self._to_dict(result)
except KalturaException as e:
    # Translate Kaltura error to MCP error
    if e.code == "INVALID_KS":
        raise McpError(ErrorCode.Unauthorized, "Invalid Kaltura session")
    elif e.code == "RESOURCE_NOT_FOUND":
        raise McpError(ErrorCode.NotFound, f"Resource not found: {e.message}")
    else:
        raise McpError(ErrorCode.InternalError, f"Kaltura API error: {e.message}")
```

## Using the Kaltura Client Wrapper

The `KalturaClientWrapper` class is used by tool and resource handlers to interact with the Kaltura API:

```python
class MediaListToolHandler(BaseToolHandler):
    """Handler for the media.list tool."""
    
    def __init__(self, kaltura_client):
        """Initialize the tool handler."""
        super().__init__(kaltura_client)
    
    def get_name(self):
        """Get the tool name."""
        return "kaltura.media.list"
    
    def get_description(self):
        """Get the tool description."""
        return "List media entries with filtering and pagination"
    
    def get_input_schema(self):
        """Get the tool input schema."""
        return {
            "type": "object",
            "properties": {
                "page_size": {
                    "type": "integer",
                    "description": "Number of entries per page",
                    "default": 10
                },
                "page_index": {
                    "type": "integer",
                    "description": "Page index (1-based)",
                    "default": 1
                },
                "filter": {
                    "type": "object",
                    "description": "Filter criteria",
                    "properties": {
                        "nameLike": {
                            "type": "string",
                            "description": "Filter entries by name (substring match)"
                        }
                    }
                }
            }
        }
    
    async def handle(self, arguments):
        """Handle the tool call."""
        # Call Kaltura client
        result = await self.kaltura_client.list_media(arguments)
        
        # Return result as text content
        return [
            {
                "type": "text",
                "text": json.dumps(result)
            }
        ]
```

## Extending the Kaltura Client Wrapper

You can extend the `KalturaClientWrapper` class to add support for additional Kaltura API services:

```python
class ExtendedKalturaClientWrapper(KalturaClientWrapper):
    """Extended Kaltura client wrapper with additional methods."""
    
    async def list_playlists(self, params=None):
        """List playlists."""
        # Ensure we have a valid session
        await self._ensure_session()
        
        # Create playlist service
        playlist_service = KalturaPlaylistService(self.client)
        
        # Create filter
        filter = KalturaPlaylistFilter()
        
        # Apply filter parameters
        if params and "filter" in params:
            for key, value in params["filter"].items():
                if hasattr(filter, key):
                    setattr(filter, key, value)
        
        # Create pager
        pager = KalturaFilterPager()
        if params:
            if "page_size" in params:
                pager.pageSize = params["page_size"]
            if "page_index" in params:
                pager.pageIndex = params["page_index"]
        
        # List playlists
        result = await playlist_service.list(filter, pager)
        
        # Convert to dict
        return self._to_dict(result)
```

Then use your extended client wrapper in the server:

```python
# In server.py
from kaltura_mcp.kaltura.client import ExtendedKalturaClientWrapper

self.kaltura_client = ExtendedKalturaClientWrapper(self.config)
await self.kaltura_client.initialize()