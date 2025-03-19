# Using Kaltura MCP with Claude

This guide provides step-by-step instructions for setting up the Kaltura Model Context Protocol (MCP) server and integrating it with Claude or other MCP-compatible AI assistants.

## What is Claude?

Claude is an AI assistant developed by Anthropic that supports the Model Context Protocol (MCP), allowing it to interact with external tools and data sources. By integrating Claude with the Kaltura MCP server, you can enable Claude to manage your Kaltura media library through natural language conversations.

## What You'll Learn

In this guide, you'll learn how to:
- Install and configure the Kaltura MCP server
- Integrate the server with Claude Desktop
- Use Claude to manage your Kaltura media library

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10 or higher** installed on your system
- **Kaltura API credentials** (partner ID, admin secret, user ID)
- **Claude Desktop app** installed (or another MCP-compatible AI assistant)
- **Git** installed (for cloning the repository)

## Step 1: Install the Kaltura MCP Server

You have two options for installing the Kaltura MCP server: directly from source or using Docker.

### Option 1: Install from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/kaltura/kaltura-mcp-public.git
   cd kaltura-mcp-public
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

### Option 2: Using Docker

If you prefer using Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/kaltura/kaltura-mcp-public.git
   cd kaltura-mcp-public
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up
   ```

## Step 2: Configure the Kaltura MCP Server

After installation, you need to configure the server with your Kaltura API credentials.

1. Create a configuration file by copying the example:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit the `config.yaml` file with your Kaltura API credentials:
   ```yaml
   # Kaltura API credentials
   kaltura:
     partner_id: YOUR_PARTNER_ID  # Your Kaltura partner ID
     admin_secret: "YOUR_ADMIN_SECRET"  # Your Kaltura admin secret
     user_id: "YOUR_USER_ID"  # Your Kaltura user ID
     service_url: "https://www.kaltura.com/api_v3"  # Kaltura API endpoint
   ```

   > **Note**: Replace `YOUR_PARTNER_ID`, `YOUR_ADMIN_SECRET`, and `YOUR_USER_ID` with your actual Kaltura credentials.

3. Alternatively, you can use environment variables instead of editing the config file:
   ```bash
   export KALTURA_PARTNER_ID=YOUR_PARTNER_ID
   export KALTURA_ADMIN_SECRET=YOUR_ADMIN_SECRET
   export KALTURA_USER_ID=YOUR_USER_ID
   ```

## Step 3: Test the Kaltura MCP Server

Before integrating with Claude, it's a good idea to test that your server is working correctly.

### Using the MCP CLI

1. Install the MCP CLI tool:
   ```bash
   pip install mcp
   ```

2. Start the server with the MCP Inspector:
   ```bash
   mcp dev kaltura_mcp/server.py:main
   ```

3. Open http://localhost:5173 in your web browser to access the MCP Inspector.

4. Test the server using the MCP CLI:
   ```bash
   # List available tools
   mcp tools kaltura-mcp

   # List available resources
   mcp resources kaltura-mcp

   # Call a tool to list media entries
   mcp call kaltura-mcp kaltura.media.list '{"page_size": 5, "filter": {}}'

   # Read a resource to get a list of media entries
   mcp read kaltura-mcp kaltura://media/list?page_size=5
   ```

If these commands return data from your Kaltura account, your server is configured correctly.

## Step 4: Integrate with Claude Desktop

Now that your Kaltura MCP server is working, you can integrate it with Claude Desktop.

1. Install the Kaltura MCP server in Claude Desktop:

   ```bash
   # Navigate to the directory containing the mcp CLI tool
   cd /path/to/mcp/cli

   # Install the Kaltura MCP server
   mcp install /path/to/kaltura-mcp-public
   ```

   > **Note**: Replace `/path/to/kaltura-mcp-public` with the actual path to your cloned repository.

2. Configure the server with your Kaltura credentials by editing the config.yaml file in Claude Desktop's configuration directory:

   - On macOS: `~/Library/Application Support/Claude/mcp/kaltura-mcp/config.yaml`
   - On Windows: `%APPDATA%\Claude\mcp\kaltura-mcp\config.yaml`
   - On Linux: `~/.config/Claude/mcp/kaltura-mcp/config.yaml`

3. Alternatively, you can add the MCP server configuration directly to Claude's settings file:

   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - On Linux: `~/.config/Claude/claude_desktop_config.json`

   Add the following to the `mcpServers` object in the settings file:

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

   > **Note**: If the `mcpServers` object already exists, add the `kaltura` entry to it rather than creating a new object.

## Step 5: Using Kaltura MCP with Claude

Once the integration is set up, you can use Claude to manage your Kaltura media library through natural language conversations. Here are some examples of what you can ask Claude:

### Listing Media

```
Show me a list of my recent media entries in Kaltura.
```

### Getting Media Details

```
Tell me about the media entry with ID "0_abc123".
```

### Uploading Media

```
Upload this video file to my Kaltura account: /path/to/video.mp4
```

### Managing Categories

```
List all categories in my Kaltura account.
```

### Managing Users

```
Show me the users in my Kaltura account.
```

## Example Conversation

Here's an example conversation with Claude using the Kaltura MCP server:

**User**: Show me a list of my recent media entries in Kaltura.

**Claude**: I'll retrieve your recent media entries from Kaltura.

Here are your 5 most recent media entries:

1. **Title**: Marketing Video 2025
   **ID**: 0_abc123
   **Created**: March 15, 2025
   **Type**: Video
   **Duration**: 2:45

2. **Title**: Product Demo
   **ID**: 0_def456
   **Created**: March 14, 2025
   **Type**: Video
   **Duration**: 5:12

3. **Title**: Company Logo
   **ID**: 0_ghi789
   **Created**: March 12, 2025
   **Type**: Image
   **Duration**: N/A

4. **Title**: Quarterly Report
   **ID**: 0_jkl012
   **Created**: March 10, 2025
   **Type**: Document
   **Duration**: N/A

5. **Title**: Training Audio
   **ID**: 0_mno345
   **Created**: March 8, 2025
   **Type**: Audio
   **Duration**: 15:30

**User**: Tell me more about the Marketing Video 2025.

**Claude**: Here are the details for the Marketing Video 2025:

**Basic Information**:
- **Title**: Marketing Video 2025
- **ID**: 0_abc123
- **Created**: March 15, 2025 at 14:32:45
- **Last Updated**: March 16, 2025 at 09:15:22
- **Owner**: john.doe@example.com

**Media Properties**:
- **Type**: Video
- **Duration**: 2:45 (165 seconds)
- **File Size**: 128.5 MB
- **Format**: MP4
- **Resolution**: 1920x1080
- **Bitrate**: 6.2 Mbps

**Content Information**:
- **Description**: "Official marketing video for Q2 2025 product launch"
- **Tags**: marketing, product-launch, official, 2025
- **Categories**: Marketing Materials, Product Launches

**Publishing Status**:
- **Status**: Ready
- **Access Control**: Default
- **Views**: 45
- **Direct URL**: https://cdnapisec.kaltura.com/p/12345/sp/1234500/playManifest/entryId/0_abc123/format/url/protocol/https

## Troubleshooting

### Common Issues

1. **Connection Issues**: If Claude cannot connect to the Kaltura MCP server, check that:
   - The server is running
   - The configuration file is correctly set up
   - The environment variables are properly set

2. **Authentication Issues**: If you see authentication errors, verify:
   - Your Kaltura API credentials are correct
   - The partner ID, admin secret, and user ID match your Kaltura account

3. **Permission Issues**: If you encounter permission errors, ensure:
   - The user specified in the configuration has the necessary permissions in Kaltura
   - The actions you're trying to perform are allowed for that user

### Checking Logs

Check the log file specified in your configuration (default: `kaltura-mcp.log`) for more detailed error information.

## Next Steps

Now that you have successfully integrated Claude with your Kaltura media library, you might want to:

- Explore the [Claude Integration Architecture](claude-integration-architecture.md) to understand how the components work together
- Check out the [Claude Integration Quick Reference](claude-integration-quick-reference.md) for common commands and configurations
- Learn about [Claude Integration Best Practices](claude-integration-best-practices.md) for optimal usage

## Conclusion

By integrating Claude with the Kaltura MCP server, you've enabled a powerful natural language interface to your Kaltura media library. This allows you to manage your media assets, categories, and users through simple conversations with Claude, making media management more accessible and efficient.