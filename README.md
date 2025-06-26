# Kaltura MCP Server

A Model Context Protocol (MCP) server that provides secure, read-only tools for managing Kaltura API operations. This server enables AI assistants to search, discover, and analyze Kaltura media content safely.

## Features

- **Media Discovery**: Search and browse media entries with advanced filtering
- **Content Analysis**: Access captions, transcripts, and attachment content
- **Category Management**: Browse and explore content categories  
- **Analytics**: Retrieve viewing analytics and performance metrics
- **Secure Access**: Read-only operations with comprehensive input validation
- **Session Management**: Automatic session handling with configurable expiry

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd kaltura-mcp
```

2. Install dependencies:
```bash
pip install -e .
```

3. Configure your Kaltura credentials:
```bash
cp .env.example .env
# Edit .env with your Kaltura API credentials
```

## Configuration

Set the following environment variables in your `.env` file:

- `KALTURA_SERVICE_URL`: Your Kaltura service URL (default: https://www.kaltura.com)
- `KALTURA_PARTNER_ID`: Your Kaltura partner ID
- `KALTURA_ADMIN_SECRET`: Your Kaltura admin secret
- `KALTURA_USER_ID`: Your Kaltura user ID
- `KALTURA_SESSION_EXPIRY`: Session expiry time in seconds (default: 86400)

## Usage

### Running the MCP Server

```bash
python -m kaltura_mcp.server
```

### Available Tools

1. **get_media_entry** - Get detailed information about a specific media entry
   - Parameters: entry_id (required)

2. **list_categories** - List and search content categories
   - Parameters: search_text, limit

3. **get_analytics** - Get viewing analytics and performance metrics for media entries
   - Parameters: from_date (required), to_date (required), entry_id, metrics

4. **get_download_url** - Get direct download URL for media files
   - Parameters: entry_id (required), flavor_id

5. **get_thumbnail_url** - Get video thumbnail/preview image URL with custom dimensions
   - Parameters: entry_id (required), width, height, second

6. **search_entries** - Search and discover media entries with intelligent sorting and filtering
   - Parameters: query (required), search_type, match_type, specific_field, boolean_operator, include_highlights, custom_metadata, date_range, max_results, sort_field, sort_order

7. **list_caption_assets** - List available captions and subtitles for a media entry
   - Parameters: entry_id (required)

8. **get_caption_content** - Get caption/subtitle content and download URL
   - Parameters: caption_asset_id (required)

9. **list_attachment_assets** - List attachment assets for a media entry
   - Parameters: entry_id (required)

10. **get_attachment_content** - Get attachment content details and download content as base64
    - Parameters: attachment_asset_id (required)

### Integration with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "kaltura": {
      "command": "python",
      "args": ["-m", "kaltura_mcp.server"],
      "cwd": "/path/to/kaltura-mcp",
      "env": {
        "KALTURA_SERVICE_URL": "https://www.kaltura.com",
        "KALTURA_PARTNER_ID": "your_partner_id",
        "KALTURA_ADMIN_SECRET": "your_admin_secret",
        "KALTURA_USER_ID": "your_user_id"
      }
    }
  }
}
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT