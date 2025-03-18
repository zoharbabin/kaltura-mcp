# Integration Tests for Kaltura-MCP Server

This directory contains integration tests for the Kaltura-MCP Server. These tests verify that the server components work correctly with the actual Kaltura API.

## Setup

To run the integration tests, you need to have a valid Kaltura API account and create a configuration file.

1. Copy the example configuration file:
   ```bash
   cp config.json.example config.json
   ```

2. Edit `config.json` and fill in your Kaltura API credentials:
   ```json
   {
     "partner_id": 12345,
     "admin_secret": "your_admin_secret_here",
     "user_id": "your_user_id_here",
     "service_url": "https://www.kaltura.com/api_v3"
   }
   ```

   - `partner_id`: Your Kaltura partner ID (an integer)
   - `admin_secret`: Your Kaltura admin secret
   - `user_id`: Your Kaltura user ID
   - `service_url`: The URL of the Kaltura API service (usually "https://www.kaltura.com/api_v3" for the SaaS version)

## Running the Tests

To run all integration tests:

```bash
pytest tests/integration
```

To run a specific test file:

```bash
pytest tests/integration/test_media_integration.py
```

To run a specific test:

```bash
pytest tests/integration/test_media_integration.py::TestMediaIntegration::test_media_list_tool
```

## Test Categories

The integration tests are organized into the following categories:

### Media Tests (`test_media_integration.py`)

Tests for media-related tools and resources:
- `test_media_list_tool`: Tests listing media entries
- `test_media_get_tool`: Tests retrieving a specific media entry
- `test_media_upload_update_delete_flow`: Tests the complete media lifecycle (upload, update, delete)
- `test_media_resource_access`: Tests accessing media resources

### Category Tests (`test_category_integration.py`)

Tests for category-related tools and resources:
- `test_category_list_tool`: Tests listing categories
- `test_category_get_tool`: Tests retrieving a specific category
- `test_category_add_update_delete_flow`: Tests the complete category lifecycle (add, update, delete)
- `test_category_resource_access`: Tests accessing category resources

### User Tests (`test_user_integration.py`)

Tests for user-related tools and resources:
- `test_user_list_tool`: Tests listing users
- `test_user_get_tool`: Tests retrieving a specific user
- `test_user_add_update_delete_flow`: Tests the complete user lifecycle (add, update, delete)
- `test_user_resource_access`: Tests accessing user resources

## Notes

- The integration tests require a valid Kaltura API account with appropriate permissions.
- Some tests may create, modify, or delete data in your Kaltura account. Make sure to use a test account or be aware of the potential changes.
- Tests are skipped if the `config.json` file is not found or is invalid.
- Tests that require existing data (like media entries, categories, or users) will be skipped if no data is found.