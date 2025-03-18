# Mock Kaltura API for Testing

This directory contains a mock implementation of the Kaltura API for testing the Kaltura-MCP Server without requiring a real Kaltura API connection.

## Overview

The mock Kaltura API provides in-memory implementations of the key Kaltura API services used by the Kaltura-MCP Server:

- Media entry management (list, get, add, update, delete, upload)
- Category management (list, get, add, update, delete)
- User management (list, get, add, update, delete)

It is designed to mimic the behavior of the real Kaltura API, including error handling and response formatting, while operating entirely in memory without external dependencies.

## Usage

### Using the Mock API in Tests

To use the mock API in your tests, you can patch the `KalturaClientWrapper` class with the `MockKalturaClientWrapper` class:

```python
from unittest.mock import patch
from tests.mocks.mock_kaltura_api import MockKalturaClientWrapper

@patch('kaltura_mcp.kaltura.client.KalturaClientWrapper', MockKalturaClientWrapper)
def test_something():
    # Your test code here
    pass
```

Alternatively, you can use the `mock_server` fixture provided in `tests/test_with_mock_api.py`:

```python
async def test_something(mock_server):
    # Your test code here using mock_server
    pass
```

### Mock Data

The mock API is initialized with sample data:

- 20 media entries with various properties
- 10 categories in a hierarchical structure
- 10 users with different attributes

You can access and modify this data directly through the `MockKalturaAPI` instance:

```python
from tests.mocks.mock_kaltura_api import MockKalturaAPI

api = MockKalturaAPI()

# Access media entries
media_entry = api.media_entries["0_sample1"]

# Access categories
category = api.categories[1]

# Access users
user = api.users["user1"]
```

### Creating New Objects

When creating new objects for the mock API, make sure to include all required attributes:

```python
# Create a media entry
from tests.mocks.mock_kaltura_api import KalturaMediaEntry
entry = KalturaMediaEntry(
    id="0_test_media",  # ID is required
    name="Test Media",
    description="Test Description",
    tags="test,media"
)

# Create a category
from tests.mocks.mock_kaltura_api import KalturaCategory
category = KalturaCategory(
    id=100,  # ID is required
    parentId=0,  # parentId is required
    name="Test Category",
    description="Test Description"
)

# Create a user
from tests.mocks.mock_kaltura_api import KalturaUser
user = KalturaUser(
    id="test_user",  # ID is required
    screenName="Test User",
    email="test@example.com"
)
```

### Customizing the Mock API

You can customize the mock API by extending the `MockKalturaAPI` class or by modifying the `_initialize_sample_data` method to create different test data:

```python
from tests.mocks.mock_kaltura_api import MockKalturaAPI

class CustomMockKalturaAPI(MockKalturaAPI):
    def _initialize_sample_data(self):
        # Your custom initialization code here
        pass
```

## Implementation Details

### `MockKalturaAPI` Class

This class provides the core implementation of the mock Kaltura API services:

- `list_media`: List media entries based on filter and pager
- `get_media_entry`: Get a media entry by ID
- `add_media_entry`: Add a new media entry
- `update_media_entry`: Update a media entry
- `delete_media_entry`: Delete a media entry
- `list_categories`: List categories based on filter and pager
- `get_category`: Get a category by ID
- `add_category`: Add a new category
- `update_category`: Update a category
- `delete_category`: Delete a category
- `list_users`: List users based on filter and pager
- `get_user`: Get a user by ID
- `add_user`: Add a new user
- `update_user`: Update a user
- `delete_user`: Delete a user

### `MockKalturaClientWrapper` Class

This class provides a wrapper around the `MockKalturaAPI` class that mimics the interface of the real `KalturaClientWrapper` class:

- `initialize`: Initialize the client
- `ensure_valid_ks`: Ensure a valid Kaltura session
- `execute_request`: Execute a Kaltura API request
- `list_media`: List media entries
- `get_media_entry`: Get a media entry by ID
- `add_media_entry`: Add a new media entry
- `update_media_entry`: Update a media entry
- `delete_media_entry`: Delete a media entry
- `upload_media`: Upload a media file
- `list_categories`: List categories
- `get_category`: Get a category by ID
- `add_category`: Add a new category
- `update_category`: Update a category
- `delete_category`: Delete a category
- `list_users`: List users
- `get_user`: Get a user by ID
- `add_user`: Add a new user
- `update_user`: Update a user
- `delete_user`: Delete a user

## Benefits of Using the Mock API

1. **Speed**: Tests run much faster without network calls to a real Kaltura API
2. **Reliability**: Tests are not affected by network issues or API rate limits
3. **Isolation**: Tests run in isolation without affecting real data
4. **Reproducibility**: Tests always run with the same initial data
5. **No Dependencies**: No need for a real Kaltura API account or credentials
6. **Controlled Testing**: You can test edge cases and error conditions easily

## Limitations

1. The mock API only implements the services and methods used by the Kaltura-MCP Server
2. Some advanced features of the Kaltura API may not be fully implemented
3. The mock API does not validate all input parameters as strictly as the real API
4. File uploads are simulated without actually processing file content