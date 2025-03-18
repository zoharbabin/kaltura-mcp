# Tool Handlers

This page documents all the tool handlers available in the Kaltura-MCP Server.

## Overview

Tool handlers are Python classes that implement the MCP tool interface. They are responsible for:

1. Defining the tool's name, description, and input schema
2. Validating input parameters
3. Transforming inputs to Kaltura API format
4. Calling the appropriate Kaltura API services
5. Transforming responses to MCP format

## Base Tool Handler

All tool handlers inherit from the `BaseToolHandler` class, which provides common functionality:

```python
class BaseToolHandler:
    """Base class for all tool handlers."""
    
    def __init__(self, kaltura_client):
        """Initialize the tool handler with a Kaltura client."""
        self.kaltura_client = kaltura_client
    
    def get_tool_definition(self):
        """Get the tool definition."""
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "inputSchema": self.get_input_schema()
        }
    
    def get_name(self):
        """Get the tool name."""
        raise NotImplementedError("Subclasses must implement get_name")
    
    def get_description(self):
        """Get the tool description."""
        raise NotImplementedError("Subclasses must implement get_description")
    
    def get_input_schema(self):
        """Get the tool input schema."""
        raise NotImplementedError("Subclasses must implement get_input_schema")
    
    async def handle(self, arguments):
        """Handle the tool call."""
        raise NotImplementedError("Subclasses must implement handle")
```

## Media Tools

### Media List Tool

**Name**: `kaltura.media.list`

**Description**: List media entries with filtering and pagination.

**Input Schema**:
```json
{
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
        },
        "tags": {
          "type": "string",
          "description": "Filter entries by tags (comma-separated)"
        },
        "createdAtGreaterThanOrEqual": {
          "type": "string",
          "description": "Filter entries created after this date (ISO format)"
        },
        "createdAtLessThanOrEqual": {
          "type": "string",
          "description": "Filter entries created before this date (ISO format)"
        },
        "statusIn": {
          "type": "string",
          "description": "Filter entries by status (comma-separated)"
        }
      }
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.media.list", {
    "page_size": 10,
    "page_index": 1,
    "filter": {
        "nameLike": "test",
        "tags": "tag1,tag2",
        "createdAtGreaterThanOrEqual": "2023-01-01T00:00:00Z"
    }
})
```

### Media Get Tool

**Name**: `kaltura.media.get`

**Description**: Get details of a specific media entry.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["entry_id"],
  "properties": {
    "entry_id": {
      "type": "string",
      "description": "ID of the media entry"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.media.get", {
    "entry_id": "0_abc123"
})
```

### Media Upload Tool

**Name**: `kaltura.media.upload`

**Description**: Upload a new media entry.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["file_path"],
  "properties": {
    "file_path": {
      "type": "string",
      "description": "Path to the media file"
    },
    "name": {
      "type": "string",
      "description": "Name of the media entry"
    },
    "description": {
      "type": "string",
      "description": "Description of the media entry"
    },
    "tags": {
      "type": "string",
      "description": "Tags for the media entry (comma-separated)"
    },
    "media_type": {
      "type": "integer",
      "description": "Media type (1=video, 2=image, 5=audio)",
      "default": 1
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.media.upload", {
    "file_path": "/path/to/video.mp4",
    "name": "My Video",
    "description": "This is my video",
    "tags": "tag1,tag2",
    "media_type": 1
})
```

### Media Update Tool

**Name**: `kaltura.media.update`

**Description**: Update a media entry.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["entry_id"],
  "properties": {
    "entry_id": {
      "type": "string",
      "description": "ID of the media entry"
    },
    "name": {
      "type": "string",
      "description": "New name for the media entry"
    },
    "description": {
      "type": "string",
      "description": "New description for the media entry"
    },
    "tags": {
      "type": "string",
      "description": "New tags for the media entry (comma-separated)"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.media.update", {
    "entry_id": "0_abc123",
    "name": "Updated Video",
    "description": "This is an updated video",
    "tags": "updated,tags"
})
```

### Media Delete Tool

**Name**: `kaltura.media.delete`

**Description**: Delete a media entry.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["entry_id"],
  "properties": {
    "entry_id": {
      "type": "string",
      "description": "ID of the media entry"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.media.delete", {
    "entry_id": "0_abc123"
})
```

## Category Tools

### Category List Tool

**Name**: `kaltura.category.list`

**Description**: List categories with filtering and pagination.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "page_size": {
      "type": "integer",
      "description": "Number of categories per page",
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
          "description": "Filter categories by name (substring match)"
        },
        "parentIdEqual": {
          "type": "integer",
          "description": "Filter categories by parent ID"
        },
        "fullNameStartsWith": {
          "type": "string",
          "description": "Filter categories by full name prefix"
        }
      }
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.category.list", {
    "page_size": 10,
    "page_index": 1,
    "filter": {
        "nameLike": "test",
        "parentIdEqual": 0
    }
})
```

### Category Get Tool

**Name**: `kaltura.category.get`

**Description**: Get details of a specific category.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["category_id"],
  "properties": {
    "category_id": {
      "type": "integer",
      "description": "ID of the category"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.category.get", {
    "category_id": 123
})
```

### Category Add Tool

**Name**: `kaltura.category.add`

**Description**: Add a new category.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["name"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Name of the category"
    },
    "description": {
      "type": "string",
      "description": "Description of the category"
    },
    "parent_id": {
      "type": "integer",
      "description": "ID of the parent category",
      "default": 0
    },
    "tags": {
      "type": "string",
      "description": "Tags for the category (comma-separated)"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.category.add", {
    "name": "My Category",
    "description": "This is my category",
    "parent_id": 0,
    "tags": "tag1,tag2"
})
```

### Category Update Tool

**Name**: `kaltura.category.update`

**Description**: Update a category.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["category_id"],
  "properties": {
    "category_id": {
      "type": "integer",
      "description": "ID of the category"
    },
    "name": {
      "type": "string",
      "description": "New name for the category"
    },
    "description": {
      "type": "string",
      "description": "New description for the category"
    },
    "tags": {
      "type": "string",
      "description": "New tags for the category (comma-separated)"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.category.update", {
    "category_id": 123,
    "name": "Updated Category",
    "description": "This is an updated category",
    "tags": "updated,tags"
})
```

### Category Delete Tool

**Name**: `kaltura.category.delete`

**Description**: Delete a category.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["category_id"],
  "properties": {
    "category_id": {
      "type": "integer",
      "description": "ID of the category"
    },
    "move_entries_to_parent": {
      "type": "boolean",
      "description": "Whether to move entries to the parent category",
      "default": true
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.category.delete", {
    "category_id": 123,
    "move_entries_to_parent": true
})
```

## User Tools

### User List Tool

**Name**: `kaltura.user.list`

**Description**: List users with filtering and pagination.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "page_size": {
      "type": "integer",
      "description": "Number of users per page",
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
        "idEqual": {
          "type": "string",
          "description": "Filter users by ID (exact match)"
        },
        "idIn": {
          "type": "string",
          "description": "Filter users by ID (comma-separated list)"
        },
        "statusEqual": {
          "type": "integer",
          "description": "Filter users by status"
        },
        "statusIn": {
          "type": "string",
          "description": "Filter users by status (comma-separated list)"
        },
        "emailLike": {
          "type": "string",
          "description": "Filter users by email (substring match)"
        }
      }
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.user.list", {
    "page_size": 10,
    "page_index": 1,
    "filter": {
        "emailLike": "example.com",
        "statusEqual": 1
    }
})
```

### User Get Tool

**Name**: `kaltura.user.get`

**Description**: Get details of a specific user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "ID of the user"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.user.get", {
    "user_id": "user123"
})
```

### User Add Tool

**Name**: `kaltura.user.add`

**Description**: Add a new user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "email", "first_name", "last_name"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "ID for the new user"
    },
    "email": {
      "type": "string",
      "description": "Email address of the user"
    },
    "first_name": {
      "type": "string",
      "description": "First name of the user"
    },
    "last_name": {
      "type": "string",
      "description": "Last name of the user"
    },
    "screen_name": {
      "type": "string",
      "description": "Screen name of the user"
    },
    "password": {
      "type": "string",
      "description": "Password for the user"
    },
    "is_admin": {
      "type": "boolean",
      "description": "Whether the user is an admin",
      "default": false
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.user.add", {
    "user_id": "user123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "screen_name": "johndoe",
    "password": "password123",
    "is_admin": false
})
```

### User Update Tool

**Name**: `kaltura.user.update`

**Description**: Update a user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "ID of the user"
    },
    "email": {
      "type": "string",
      "description": "New email address for the user"
    },
    "first_name": {
      "type": "string",
      "description": "New first name for the user"
    },
    "last_name": {
      "type": "string",
      "description": "New last name for the user"
    },
    "screen_name": {
      "type": "string",
      "description": "New screen name for the user"
    },
    "password": {
      "type": "string",
      "description": "New password for the user"
    },
    "is_admin": {
      "type": "boolean",
      "description": "Whether the user is an admin"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.user.update", {
    "user_id": "user123",
    "email": "newemail@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "screen_name": "janesmith"
})
```

### User Delete Tool

**Name**: `kaltura.user.delete`

**Description**: Delete a user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "ID of the user"
    }
  }
}
```

**Example**:
```python
result = await client.call_tool("kaltura.user.delete", {
    "user_id": "user123"
})
```

## Implementing Custom Tool Handlers

You can implement custom tool handlers by extending the `BaseToolHandler` class:

```python
from kaltura_mcp.tools.base import BaseToolHandler

class MyCustomToolHandler(BaseToolHandler):
    """Custom tool handler."""
    
    def get_name(self):
        """Get the tool name."""
        return "kaltura.custom.tool"
    
    def get_description(self):
        """Get the tool description."""
        return "My custom tool"
    
    def get_input_schema(self):
        """Get the tool input schema."""
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1"
                },
                "param2": {
                    "type": "integer",
                    "description": "Parameter 2"
                }
            }
        }
    
    async def handle(self, arguments):
        """Handle the tool call."""
        # Implement your custom logic here
        return [
            {
                "type": "text",
                "text": "Custom tool result"
            }
        ]
```

Then register your custom tool handler in the server:

```python
# In server.py
self.tool_handlers["kaltura.custom.tool"] = MyCustomToolHandler(self.kaltura_client)