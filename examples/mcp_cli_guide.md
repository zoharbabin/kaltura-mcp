# Using the MCP CLI with Kaltura MCP Server

This guide explains how to use the MCP CLI tool to interact with the Kaltura MCP server.

## Prerequisites

- MCP CLI tool installed (`pip install mcp`)
- Kaltura MCP server installed and configured

## Basic Commands

### Starting the Server with the MCP Inspector

The MCP Inspector provides a web interface for interacting with the MCP server. To start the server with the MCP Inspector:

```bash
# Navigate to your Kaltura MCP directory
cd /path/to/kaltura-mcp-public

# Start the server with the MCP Inspector
mcp dev kaltura_mcp/server.py:main
```

This will start the MCP Inspector on http://localhost:5173 and the proxy server on port 3000.

### Running the Server Directly

To run the server directly without the MCP Inspector:

```bash
# Navigate to your Kaltura MCP directory
cd /path/to/kaltura-mcp-public

# Run the server
mcp run kaltura_mcp/server.py:main
```

### Using the kaltura-mcp Command

If you've installed the Kaltura MCP server using pip or the setup script, you can also use the `kaltura-mcp` command:

```bash
# Run the server
kaltura-mcp
```

## Testing the Server

### Using the MCP CLI to Test the Server

You can use the MCP CLI to test the server by running commands against it:

```bash
# List tools
mcp tools kaltura-mcp

# List resources
mcp resources kaltura-mcp

# Call a tool
mcp call kaltura-mcp kaltura.media.list '{"page_size": 5, "filter": {}}'

# Read a resource
mcp read kaltura-mcp kaltura://media/list?page_size=5
```

### Using the MCP Inspector

The MCP Inspector provides a web interface for interacting with the MCP server. To use it:

1. Start the server with the MCP Inspector:
   ```bash
   mcp dev kaltura_mcp/server.py:main
   ```

2. Open http://localhost:5173 in your web browser.

3. Connect to the server using the "Connect" button.

4. Use the interface to explore the available tools and resources, and to call tools and read resources.

## Example: Listing Media Entries

Here's an example of how to list media entries using the MCP CLI:

```bash
# Call the media.list tool
mcp call kaltura-mcp kaltura.media.list '{"page_size": 5, "filter": {}}'
```

This will return a JSON response with the first 5 media entries in your Kaltura account.

## Example: Getting a Media Entry

Here's an example of how to get a specific media entry using the MCP CLI:

```bash
# Call the media.get tool
mcp call kaltura-mcp kaltura.media.get '{"entryId": "0_abc123"}'
```

Replace `0_abc123` with the actual ID of the media entry you want to retrieve.

## Example: Uploading a Media Entry

Here's an example of how to upload a media entry using the MCP CLI:

```bash
# Call the media.upload tool
mcp call kaltura-mcp kaltura.media.upload '{"file_path": "/path/to/file.mp4", "title": "My Video"}'
```

Replace `/path/to/file.mp4` with the actual path to the file you want to upload.

## Conclusion

The MCP CLI provides a powerful way to interact with the Kaltura MCP server from the command line. You can use it to test the server, call tools, and read resources.

For more information on the MCP CLI, see the [MCP CLI documentation](https://github.com/modelcontextprotocol/mcp).