# Using Kaltura MCP with Claude

This guide explains how to use the Kaltura MCP server with Claude or other LLMs that support the Model Context Protocol (MCP).

## Prerequisites

- Claude Desktop installed (or another MCP-compatible LLM)
- Kaltura MCP server installed and configured

## Installation in Claude Desktop

1. Install the Kaltura MCP server in Claude Desktop:

```bash
# Navigate to the directory containing the mcp CLI tool
cd /path/to/mcp/cli

# Install the Kaltura MCP server
mcp install /path/to/kaltura-mcp-public
```

2. Configure the server with your Kaltura credentials:

```bash
# Edit the config.yaml file in Claude Desktop's configuration directory
# On macOS: ~/Library/Application Support/Claude/mcp/kaltura-mcp/config.yaml
# On Windows: %APPDATA%\Claude\mcp\kaltura-mcp\config.yaml
# On Linux: ~/.config/Claude/mcp/kaltura-mcp/config.yaml
```

## Using with Claude

Once installed, you can use the Kaltura MCP server with Claude by asking questions about your Kaltura media library. Here are some examples:

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

Would you like to see more details about any of these entries?

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

Would you like me to perform any actions with this media entry?

## Conclusion

The Kaltura MCP server provides a powerful way to interact with your Kaltura media library using natural language through Claude or other MCP-compatible LLMs. You can manage media entries, categories, users, and more, all through a conversational interface.