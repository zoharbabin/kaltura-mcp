# Using the MCP Inspector with Kaltura MCP

The MCP Inspector is a web-based interface for interacting with MCP servers, including the Kaltura MCP server. This guide explains how to use the MCP Inspector to explore and test the Kaltura MCP server.

## Starting the MCP Inspector

To start the MCP Inspector with the Kaltura MCP server:

```bash
# Navigate to the Kaltura MCP directory
cd kaltura-mcp-public

# Activate your virtual environment (if using one)
source venv/bin/activate

# Start the MCP Inspector with the Kaltura MCP server
mcp dev kaltura_mcp/server.py:main
```

This will start the MCP Inspector on http://localhost:5173 and the Kaltura MCP server on port 3000.

## Using the MCP Inspector

Once the MCP Inspector is running, open http://localhost:5173 in your web browser. You'll see the MCP Inspector interface, which allows you to:

1. **Explore Available Tools**: View all the tools provided by the Kaltura MCP server, including their descriptions and input schemas.

2. **Execute Tools**: Call tools with custom parameters and see the results.

3. **Browse Resources**: View all the resources provided by the Kaltura MCP server.

4. **Access Resources**: Read resources with custom URIs and see the results.

## Available Tools

The Kaltura MCP server provides the following tools:

### Media Tools

- **kaltura.media.list**: List media entries with filtering and pagination
- **kaltura.media.get**: Get details of a specific media entry
- **kaltura.media.upload**: Upload a file to Kaltura
- **kaltura.media.update**: Update a media entry
- **kaltura.media.delete**: Delete a media entry

### Category Tools

- **kaltura.category.list**: List categories with filtering and pagination
- **kaltura.category.get**: Get details of a specific category
- **kaltura.category.add**: Add a new category
- **kaltura.category.update**: Update a category
- **kaltura.category.delete**: Delete a category

### User Tools

- **kaltura.user.list**: List users with filtering and pagination
- **kaltura.user.get**: Get details of a specific user
- **kaltura.user.add**: Add a new user
- **kaltura.user.update**: Update a user
- **kaltura.user.delete**: Delete a user

## Example: Listing Media Entries

1. In the MCP Inspector, click on the "Tools" tab.
2. Find and click on the "kaltura.media.list" tool.
3. In the "Arguments" section, enter:
   ```json
   {
     "page_size": 5,
     "filter": {}
   }
   ```
4. Click "Call Tool" to execute the tool.
5. The results will be displayed in the "Result" section.

## Example: Getting a Media Entry

1. In the MCP Inspector, click on the "Tools" tab.
2. Find and click on the "kaltura.media.get" tool.
3. In the "Arguments" section, enter:
   ```json
   {
     "entryId": "0_abc123"
   }
   ```
   (Replace "0_abc123" with an actual entry ID from your Kaltura account)
4. Click "Call Tool" to execute the tool.
5. The results will be displayed in the "Result" section.

## Example: Accessing a Resource

1. In the MCP Inspector, click on the "Resources" tab.
2. Find and click on the "kaltura://media/list" resource.
3. In the "URI Parameters" section, enter:
   ```
   kaltura://media/list?page_size=5
   ```
4. Click "Read Resource" to access the resource.
5. The results will be displayed in the "Result" section.

## Conclusion

The MCP Inspector provides a convenient way to explore and test the Kaltura MCP server. You can use it to understand the available tools and resources, test different parameters, and see the results in real-time.

This is particularly useful for developers who want to integrate the Kaltura MCP server with their applications or for administrators who want to test the server's functionality.