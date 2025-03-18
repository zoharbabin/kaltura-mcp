# Context Management

This page documents the context management strategies used in the Kaltura-MCP Server to optimize the data returned to Large Language Models (LLMs).

## Overview

LLMs have limited context windows, which means they can only process a certain amount of text at a time. When working with large datasets from the Kaltura API, it's important to optimize the data to fit within these context windows while maintaining relevance and usefulness.

The Kaltura-MCP Server implements three main context management strategies:

1. **Pagination Strategy**: Handles large result sets by paginating them into manageable chunks
2. **Selective Context Strategy**: Filters data to include only the fields that are relevant to the current context
3. **Summarization Strategy**: Summarizes long text fields to provide concise information

These strategies can be used individually or combined to provide optimal context for LLMs.

## Pagination Strategy

The pagination strategy is used to handle large result sets by dividing them into pages. This is particularly useful for list resources that may return hundreds or thousands of items.

### Implementation

```python
class PaginationStrategy:
    """Strategy for paginating large result sets."""
    
    def apply(self, data, params):
        """Apply the pagination strategy to the data."""
        page_size = params.get("page_size", 10)
        page_index = params.get("page_index", 1)
        
        # Extract total count and objects from data
        total_count = data.get("totalCount", 0)
        objects = data.get("objects", [])
        
        # Calculate pagination info
        start_index = (page_index - 1) * page_size
        end_index = min(start_index + page_size, total_count)
        next_page_available = end_index < total_count
        
        # Create paginated result
        result = {
            "objects": objects,
            "totalCount": total_count,
            "pageSize": page_size,
            "pageIndex": page_index,
            "nextPageAvailable": next_page_available
        }
        
        return json.dumps(result)
```

### Usage

The pagination strategy is typically used in list resource handlers:

```python
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

### Configuration

The pagination strategy can be configured in the `config.yaml` file:

```yaml
context:
  pagination:
    default_page_size: 10
    max_page_size: 100
```

## Selective Context Strategy

The selective context strategy is used to filter data to include only the fields that are relevant to the current context. This is useful for reducing the size of large objects with many fields.

### Implementation

```python
class SelectiveContextStrategy:
    """Strategy for selecting relevant fields from data."""
    
    def __init__(self, default_fields=None):
        """Initialize the strategy with default fields."""
        self.default_fields = default_fields or [
            "id", "name", "description", "createdAt", "updatedAt"
        ]
    
    def apply(self, data, fields=None):
        """Apply the selective context strategy to the data."""
        fields = fields or self.default_fields
        
        if isinstance(data, dict):
            # Filter dictionary fields
            return {k: self.apply(v, fields) for k, v in data.items() if k in fields}
        elif isinstance(data, list):
            # Apply to each item in the list
            return [self.apply(item, fields) for item in data]
        else:
            # Return primitive values as is
            return data
```

### Usage

The selective context strategy is typically used in resource handlers:

```python
class MediaEntryResourceHandler(BaseResourceHandler):
    """Handler for media entry resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.selective_strategy = SelectiveContextStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract entry ID and fields
        entry_id, fields = self._parse_uri(uri)
        
        # Get media entry from Kaltura API
        result = await self.kaltura_client.get_media(entry_id)
        
        # Apply selective context strategy
        return json.dumps(self.selective_strategy.apply(result, fields))
```

### Configuration

The selective context strategy can be configured in the `config.yaml` file:

```yaml
context:
  selective:
    default_fields: ["id", "name", "description", "createdAt", "updatedAt"]
```

## Summarization Strategy

The summarization strategy is used to summarize long text fields to provide concise information. This is useful for reducing the size of large text fields while maintaining their meaning.

### Implementation

```python
class SummarizationStrategy:
    """Strategy for summarizing long text fields."""
    
    def __init__(self, max_length=1000, ellipsis="..."):
        """Initialize the strategy with max length and ellipsis."""
        self.max_length = max_length
        self.ellipsis = ellipsis
    
    def apply(self, data, fields_to_summarize=None):
        """Apply the summarization strategy to the data."""
        fields_to_summarize = fields_to_summarize or ["description"]
        
        if isinstance(data, dict):
            # Summarize dictionary fields
            result = {}
            for k, v in data.items():
                if k in fields_to_summarize and isinstance(v, str) and len(v) > self.max_length:
                    # Summarize long text
                    result[k] = v[:self.max_length - len(self.ellipsis)] + self.ellipsis
                else:
                    # Apply recursively to nested data
                    result[k] = self.apply(v, fields_to_summarize)
            return result
        elif isinstance(data, list):
            # Apply to each item in the list
            return [self.apply(item, fields_to_summarize) for item in data]
        else:
            # Return primitive values as is
            return data
```

### Usage

The summarization strategy is typically used in resource handlers:

```python
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
        return json.dumps(self.summarization_strategy.apply(result))
```

### Configuration

The summarization strategy can be configured in the `config.yaml` file:

```yaml
context:
  summarization:
    max_length: 1000
    ellipsis: "..."
```

## Combining Strategies

The three context management strategies can be combined to provide optimal context for LLMs. For example, you might use pagination for list resources, selective context for all resources, and summarization for resources with long text fields.

### Example: Combined Strategy

```python
class MediaListResourceHandler(BaseResourceHandler):
    """Handler for media list resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.pagination_strategy = PaginationStrategy()
        self.selective_strategy = SelectiveContextStrategy()
        self.summarization_strategy = SummarizationStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract parameters
        params = self._parse_uri(uri)
        
        # Get media list from Kaltura API
        result = await self.kaltura_client.list_media(params)
        
        # Apply pagination strategy
        paginated = json.loads(self.pagination_strategy.apply(result, params))
        
        # Apply selective context strategy
        selected = self.selective_strategy.apply(paginated)
        
        # Apply summarization strategy
        summarized = self.summarization_strategy.apply(selected)
        
        return json.dumps(summarized)
```

## Field Name Mapping

The Kaltura-MCP Server also implements field name mapping to handle inconsistent key naming in JSON responses (e.g., `createdAt` vs `created_at`). This ensures that both camelCase and snake_case formats are supported.

### Implementation

```python
class FieldNameMapper:
    """Utility for mapping between camelCase and snake_case field names."""
    
    @staticmethod
    def camel_to_snake(name):
        """Convert camelCase to snake_case."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    @staticmethod
    def snake_to_camel(name):
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @classmethod
    def map_keys(cls, data, to_snake=False):
        """Map keys in data to either snake_case or camelCase."""
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                new_key = cls.camel_to_snake(k) if to_snake else cls.snake_to_camel(k)
                result[new_key] = cls.map_keys(v, to_snake)
            return result
        elif isinstance(data, list):
            return [cls.map_keys(item, to_snake) for item in data]
        else:
            return data
```

### Usage

The field name mapper is typically used in resource handlers and context strategies:

```python
class SelectiveContextStrategy:
    """Strategy for selecting relevant fields from data."""
    
    def __init__(self, default_fields=None):
        """Initialize the strategy with default fields."""
        self.default_fields = default_fields or [
            "id", "name", "description", "createdAt", "updatedAt"
        ]
        self.field_mapper = FieldNameMapper()
    
    def apply(self, data, fields=None):
        """Apply the selective context strategy to the data."""
        fields = fields or self.default_fields
        
        # Map fields to both camelCase and snake_case
        camel_fields = fields
        snake_fields = [self.field_mapper.camel_to_snake(f) for f in fields]
        all_fields = set(camel_fields + snake_fields)
        
        if isinstance(data, dict):
            # Filter dictionary fields
            result = {k: self.apply(v, fields) for k, v in data.items() if k in all_fields}
            
            # Include both camelCase and snake_case versions of each field
            for k, v in data.items():
                if k in all_fields:
                    camel_key = self.field_mapper.snake_to_camel(k)
                    snake_key = self.field_mapper.camel_to_snake(k)
                    result[camel_key] = self.apply(v, fields)
                    result[snake_key] = self.apply(v, fields)
            
            return result
        elif isinstance(data, list):
            # Apply to each item in the list
            return [self.apply(item, fields) for item in data]
        else:
            # Return primitive values as is
            return data
```

## Custom Context Management Strategies

You can implement custom context management strategies by creating a new class with an `apply` method:

```python
class MyCustomStrategy:
    """Custom context management strategy."""
    
    def __init__(self, config=None):
        """Initialize the strategy with configuration."""
        self.config = config or {}
    
    def apply(self, data, params=None):
        """Apply the strategy to the data."""
        # Implement your custom logic here
        return data
```

Then use your custom strategy in resource handlers:

```python
class MediaEntryResourceHandler(BaseResourceHandler):
    """Handler for media entry resources."""
    
    def __init__(self, kaltura_client):
        """Initialize the resource handler."""
        super().__init__(kaltura_client)
        self.custom_strategy = MyCustomStrategy()
    
    async def handle(self, uri):
        """Handle the resource request."""
        # Parse URI and extract entry ID
        entry_id = self._parse_uri(uri)
        
        # Get media entry from Kaltura API
        result = await self.kaltura_client.get_media(entry_id)
        
        # Apply custom strategy
        return json.dumps(self.custom_strategy.apply(result))