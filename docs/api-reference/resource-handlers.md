# Resource Handlers

This page documents all the resource handlers available in the Kaltura-MCP Server.

## Overview

Resource handlers are Python classes that implement the MCP resource interface. They are responsible for:

1. Defining the resource's URI pattern, description, and MIME type
2. Parsing resource URIs and extracting parameters
3. Fetching appropriate data from the Kaltura API
4. Transforming responses to MCP resource format
5. Applying context management strategies

## Base Resource Handler

All resource handlers inherit from the `BaseResourceHandler` class, which provides common functionality:

```python
class BaseResourceHandler:
    """Base class for all resource handlers."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler with a Kaltura client."""
        self.kaltura_client = kaltura_client
    
    def get_resource_definition(self):
        """Get the resource definition."""
        return {
            "uri": self.get_uri_pattern(),
            "description": self.get_description(),
            "mimeType": self.get_mime_type()
        }
    
    def get_uri_pattern(self):
        """Get the resource URI pattern."""
        raise NotImplementedError("Subclasses must implement get_uri_pattern")
    
    def get_description(self):
        """Get the resource description."""
        raise NotImplementedError("Subclasses must implement get_description")
    
    def get_mime_type(self):
        """Get the resource MIME type."""
        return "application/json"
    
    def matches_uri(self, uri):
        """Check if the URI matches this resource handler."""
        import re
        pattern = self.get_uri_pattern().replace("{", "(?P<").replace("}", ">[^/]+)")
        return re.match(f"^{pattern}$", uri) is not None
    
    async def handle(self, uri):
        """Handle the resource request."""
        raise NotImplementedError("Subclasses must implement handle")
```

## Media Resources

### Media Entry Resource

**URI Pattern**: `kaltura://media/{entry_id}`

**Description**: Get details of a specific media entry.

**MIME Type**: `application/json`

**Example URI**: `kaltura://media/0_abc123`

**Example Response**:
```json
{
  "id": "0_abc123",
  "name": "My Video",
  "description": "This is my video",
  "createdAt": "2023-01-01T12:00:00Z",
  "updatedAt": "2023-01-02T12:00:00Z",
  "userId": "user123",
  "mediaType": 1,
  "duration": 120,
  "msDuration": 120000,
  "status": 2,
  "tags": "tag1, tag2",
  "thumbnailUrl": "https://example.com/thumbnail.jpg",
  "downloadUrl": "https://example.com/download.mp4",
  "plays": 100,
  "views": 200
}
```

### Media List Resource

**URI Pattern**: `kaltura://media/list`

**Description**: List media entries with filtering and pagination.

**MIME Type**: `application/json`

**Query Parameters**:
- `page_size`: Number of entries per page (default: 10)
- `page_index`: Page index (1-based, default: 1)
- `name_like`: Filter entries by name (substring match)
- `tags`: Filter entries by tags (comma-separated)
- `created_after`: Filter entries created after this date (ISO format)
- `created_before`: Filter entries created before this date (ISO format)
- `status_in`: Filter entries by status (comma-separated)

**Example URI**: `kaltura://media/list?page_size=5&name_like=test&tags=tag1,tag2`

**Example Response**:
```json
{
  "objects": [
    {
      "id": "0_abc123",
      "name": "Test Video 1",
      "description": "This is test video 1",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z",
      "userId": "user123",
      "mediaType": 1,
      "duration": 120,
      "status": 2,
      "tags": "tag1, tag2"
    },
    {
      "id": "0_def456",
      "name": "Test Video 2",
      "description": "This is test video 2",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z",
      "userId": "user123",
      "mediaType": 1,
      "duration": 180,
      "status": 2,
      "tags": "tag1, tag2"
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}
```

## Category Resources

### Category Resource

**URI Pattern**: `kaltura://categories/{category_id}`

**Description**: Get details of a specific category.

**MIME Type**: `application/json`

**Example URI**: `kaltura://categories/123`

**Example Response**:
```json
{
  "id": 123,
  "name": "My Category",
  "description": "This is my category",
  "createdAt": "2023-01-01T12:00:00Z",
  "updatedAt": "2023-01-02T12:00:00Z",
  "partnerId": 12345,
  "parentId": 0,
  "depth": 1,
  "fullName": "My Category",
  "entriesCount": 10,
  "directEntriesCount": 5,
  "tags": "tag1, tag2"
}
```

### Category List Resource

**URI Pattern**: `kaltura://categories/list`

**Description**: List categories with filtering and pagination.

**MIME Type**: `application/json`

**Query Parameters**:
- `page_size`: Number of categories per page (default: 10)
- `page_index`: Page index (1-based, default: 1)
- `name_like`: Filter categories by name (substring match)
- `parent_id`: Filter categories by parent ID
- `full_name_starts_with`: Filter categories by full name prefix

**Example URI**: `kaltura://categories/list?page_size=5&name_like=test&parent_id=0`

**Example Response**:
```json
{
  "objects": [
    {
      "id": 123,
      "name": "Test Category 1",
      "description": "This is test category 1",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z",
      "partnerId": 12345,
      "parentId": 0,
      "depth": 1,
      "fullName": "Test Category 1",
      "entriesCount": 10,
      "directEntriesCount": 5,
      "tags": "tag1, tag2"
    },
    {
      "id": 456,
      "name": "Test Category 2",
      "description": "This is test category 2",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z",
      "partnerId": 12345,
      "parentId": 0,
      "depth": 1,
      "fullName": "Test Category 2",
      "entriesCount": 5,
      "directEntriesCount": 3,
      "tags": "tag1, tag2"
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}
```

## User Resources

### User Resource

**URI Pattern**: `kaltura://users/{user_id}`

**Description**: Get details of a specific user.

**MIME Type**: `application/json`

**Example URI**: `kaltura://users/user123`

**Example Response**:
```json
{
  "id": "user123",
  "screenName": "John Doe",
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "createdAt": "2023-01-01T12:00:00Z",
  "updatedAt": "2023-01-02T12:00:00Z",
  "partnerId": 12345,
  "status": 1,
  "isAdmin": false
}
```

### User List Resource

**URI Pattern**: `kaltura://users/list`

**Description**: List users with filtering and pagination.

**MIME Type**: `application/json`

**Query Parameters**:
- `page_size`: Number of users per page (default: 10)
- `page_index`: Page index (1-based, default: 1)
- `id_equal`: Filter users by ID (exact match)
- `id_in`: Filter users by ID (comma-separated list)
- `status_equal`: Filter users by status
- `status_in`: Filter users by status (comma-separated list)
- `email_like`: Filter users by email (substring match)

**Example URI**: `kaltura://users/list?page_size=5&email_like=example.com&status_equal=1`

**Example Response**:
```json
{
  "objects": [
    {
      "id": "user123",
      "screenName": "John Doe",
      "fullName": "John Doe",
      "email": "john.doe@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "createdAt": "2023-01-01T12:00:00Z",
      "updatedAt": "2023-01-02T12:00:00Z",
      "partnerId": 12345,
      "status": 1,
      "isAdmin": false
    },
    {
      "id": "user456",
      "screenName": "Jane Smith",
      "fullName": "Jane Smith",
      "email": "jane.smith@example.com",
      "firstName": "Jane",
      "lastName": "Smith",
      "createdAt": "2023-01-03T12:00:00Z",
      "updatedAt": "2023-01-04T12:00:00Z",
      "partnerId": 12345,
      "status": 1,
      "isAdmin": false
    }
  ],
  "totalCount": 2,
  "pageSize": 5,
  "pageIndex": 1,
  "nextPageAvailable": false
}
```

## Context Management in Resources

Resource handlers use context management strategies to optimize the data returned to LLMs:

### Pagination Strategy

The pagination strategy is used for list resources to handle large result sets:

```python
from kaltura_mcp.context.pagination import PaginationStrategy

class MediaListResourceHandler(BaseResourceHandler):
    """Handler for media list resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.pagination_strategy = PaginationStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract parameters
        params = self._parse_uri(uri)
        
        # Get media list from Kaltura API
        result = await self.kaltura_client.list_media(params)
        
        # Apply pagination strategy
        return self.pagination_strategy.apply(result, params)
```

### Selective Context Strategy

The selective context strategy is used to filter data to include only relevant fields:

```python
from kaltura_mcp.context.selective import SelectiveContextStrategy

class MediaEntryResourceHandler(BaseResourceHandler):
    """Handler for media entry resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.selective_strategy = SelectiveContextStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract entry ID
        entry_id = self._parse_uri(uri)
        
        # Get media entry from Kaltura API
        result = await self.kaltura_client.get_media(entry_id)
        
        # Apply selective context strategy
        return self.selective_strategy.apply(result)
```

### Summarization Strategy

The summarization strategy is used to summarize long text fields:

```python
from kaltura_mcp.context.summarization import SummarizationStrategy

class MediaEntryResourceHandler(BaseResourceHandler):
    """Handler for media entry resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.summarization_strategy = SummarizationStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract entry ID
        entry_id = self._parse_uri(uri)
        
        # Get media entry from Kaltura API
        result = await self.kaltura_client.get_media(entry_id)
        
        # Apply summarization strategy
        return self.summarization_strategy.apply(result)
```

## Implementing Custom Resource Handlers

You can implement custom resource handlers by extending the `BaseResourceHandler` class:

```python
from kaltura_mcp.resources.base import BaseResourceHandler

class MyCustomResourceHandler(BaseResourceHandler):
    """Custom resource handler."""
    
    def get_uri_pattern(self):
        """Get the resource URI pattern."""
        return "kaltura://custom/{id}"
    
    def get_description(self):
        """Get the resource description."""
        return "My custom resource"
    
    def get_mime_type(self):
        """Get the resource MIME type."""
        return "application/json"
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract ID
        import re
        match = re.match(r"^kaltura://custom/(?P<id>[^/]+)$", uri)
        if not match:
            raise ValueError(f"Invalid URI: {uri}")
        
        id = match.group("id")
        
        # Implement your custom logic here
        result = {"id": id, "name": "Custom Resource"}
        
        return json.dumps(result)
```

Then register your custom resource handler in the server:

```python
# In server.py
self.resource_handlers["custom"] = MyCustomResourceHandler(self.kaltura_client)