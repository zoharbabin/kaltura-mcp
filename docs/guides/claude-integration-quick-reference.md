# Claude Integration Quick Reference

This quick reference guide provides essential commands and configurations for setting up and using the Kaltura MCP server with Claude.

## Installation Commands

### Clone Repository
```bash
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp-public
```

### Python Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### Docker Installation
```bash
docker-compose up
```

## Configuration

### Create Configuration File
```bash
cp config.yaml.example config.yaml
```

### Minimal Configuration Example
```yaml
kaltura:
  partner_id: YOUR_PARTNER_ID
  admin_secret: "YOUR_ADMIN_SECRET"
  user_id: "YOUR_USER_ID"
  service_url: "https://www.kaltura.com/api_v3"
```

### Environment Variables
```bash
export KALTURA_PARTNER_ID=YOUR_PARTNER_ID
export KALTURA_ADMIN_SECRET=YOUR_ADMIN_SECRET
export KALTURA_USER_ID=YOUR_USER_ID
```

## Running the Server

### Direct Execution
```bash
kaltura-mcp
```

### Using MCP CLI
```bash
# With MCP Inspector (web interface)
mcp dev kaltura_mcp/server.py:main

# Without MCP Inspector
mcp run kaltura_mcp/server.py:main
```

### Using Docker
```bash
docker-compose up
```

## Testing the Server

### MCP CLI Commands
```bash
# List tools
mcp tools kaltura-mcp

# List resources
mcp resources kaltura-mcp

# Call a tool (list media)
mcp call kaltura-mcp kaltura.media.list '{"page_size": 5, "filter": {}}'

# Read a resource
mcp read kaltura-mcp kaltura://media/list?page_size=5
```

## Claude Desktop Integration

### Install MCP Server in Claude Desktop
```bash
mcp install /path/to/kaltura-mcp-public
```

### Claude Desktop Configuration Paths
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Claude Desktop Configuration Example
```json
{
  "mcpServers": {
    "kaltura": {
      "command": "kaltura-mcp",
      "args": [],
      "env": {
        "KALTURA_PARTNER_ID": "YOUR_PARTNER_ID",
        "KALTURA_ADMIN_SECRET": "YOUR_ADMIN_SECRET",
        "KALTURA_USER_ID": "YOUR_USER_ID"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

## Available Tools

| Tool Name | Description | Example Usage |
|-----------|-------------|--------------|
| `kaltura.media.list` | List media entries | "Show me my recent videos" |
| `kaltura.media.get` | Get media details | "Tell me about video 0_abc123" |
| `kaltura.media.upload` | Upload media | "Upload this file: /path/to/video.mp4" |
| `kaltura.media.update` | Update media | "Update the title of video 0_abc123 to 'New Title'" |
| `kaltura.media.delete` | Delete media | "Delete video 0_abc123" |
| `kaltura.category.list` | List categories | "Show me all categories" |
| `kaltura.category.get` | Get category details | "Tell me about category 12345" |
| `kaltura.category.add` | Add category | "Create a new category called 'Webinars'" |
| `kaltura.category.update` | Update category | "Rename category 12345 to 'Training Videos'" |
| `kaltura.category.delete` | Delete category | "Delete category 12345" |
| `kaltura.user.list` | List users | "Show me all users" |
| `kaltura.user.get` | Get user details | "Tell me about user john.doe" |
| `kaltura.user.add` | Add user | "Add user jane.doe with email jane.doe@example.com" |
| `kaltura.user.update` | Update user | "Update user john.doe's email to new.email@example.com" |
| `kaltura.user.delete` | Delete user | "Delete user john.doe" |

## Available Resources

| Resource URI | Description |
|--------------|-------------|
| `kaltura://media/{entryId}` | Media entry metadata |
| `kaltura://media/list?page_size={size}` | List of media entries |
| `kaltura://category/{categoryId}` | Category metadata |
| `kaltura://category/list?page_size={size}` | List of categories |
| `kaltura://user/{userId}` | User metadata |
| `kaltura://user/list?page_size={size}` | List of users |

## Example Claude Prompts

Here are some example prompts you can use with Claude once the integration is set up:

```
Show me a list of my recent media entries in Kaltura.

Tell me about the media entry with ID "0_abc123".

Upload this video file to my Kaltura account: /path/to/video.mp4

List all categories in my Kaltura account.

Show me the users in my Kaltura account.

Search for videos with "marketing" in the title.

Create a new category called "Product Demos" under the "Marketing" parent category.

Add tags "2025" and "quarterly-update" to video 0_abc123.

Update the description of video 0_def456 to "Updated product demonstration for Q2 2025".

Delete the media entry with ID "0_xyz789".
```

## Troubleshooting

### Check Server Status
```bash
# If running directly
ps aux | grep kaltura-mcp

# If running with Docker
docker ps | grep kaltura-mcp
```

### View Logs
```bash
# Check the log file specified in config.yaml
cat kaltura-mcp.log

# For Docker
docker logs kaltura-mcp
```

### Common Issues

1. **Authentication Errors**
   - Verify Kaltura API credentials
   - Check for typos in partner ID, admin secret, or user ID
   - Ensure the user has appropriate permissions in Kaltura

2. **Connection Issues**
   - Ensure the server is running
   - Check network connectivity to Kaltura API
   - Verify firewall settings allow outbound connections to the Kaltura API

3. **Permission Errors**
   - Verify user has appropriate permissions in Kaltura
   - Check access control settings for media entries
   - Ensure the user can perform the requested operation

4. **File Upload Issues**
   - Check file path is correct and accessible
   - Verify file format is supported by Kaltura
   - Ensure file size is within Kaltura's limits

5. **Claude Integration Issues**
   - Restart Claude Desktop
   - Check Claude Desktop configuration
   - Verify the MCP server is properly installed in Claude Desktop

## Next Steps

After setting up the basic integration, consider:

1. Exploring the [Claude Integration Architecture](claude-integration-architecture.md) to understand how the components work together
2. Learning about [Claude Integration Best Practices](claude-integration-best-practices.md) for optimal usage
3. Customizing the integration for your specific use cases

For more detailed information, refer to the [Claude Integration Setup Guide](claude-integration-setup.md).