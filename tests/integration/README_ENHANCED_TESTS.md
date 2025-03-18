# Enhanced Integration Tests for Kaltura MCP

This directory contains enhanced integration tests that verify the full flow from client to MCP server to Kaltura API. These tests ensure that the MCP server is intelligently translating client requests into appropriate Kaltura API calls.

## Overview

The enhanced tests include:

1. **Enhanced Client** (`enhanced_client.py`): A wrapper around the Kaltura client that adds detailed logging of API calls.
2. **Enhanced Server** (`enhanced_server.py`): A wrapper around the MCP server that adds detailed logging of request translation.
3. **Full MCP Flow Tests** (`test_full_mcp_flow.py`): Tests that verify the full flow from client to MCP server to Kaltura API.
4. **Direct API Test** (`direct_api_test.py`): A script that directly tests the Kaltura API with enhanced logging.
5. **Test MCP Client** (`test_mcp_client.py`): A client script that connects to a running MCP server and makes various requests.
6. **Run Enhanced Server** (`run_enhanced_server.py`): A script that runs the enhanced MCP server for testing.

## Running the Tests

### Running Full Flow Tests

To run the full MCP flow tests:

```bash
./run_tests.py --full-flow -v --log-api-calls
```

This will:
1. Start a real MCP server process
2. Connect a client to the server
3. Make various requests through the client
4. Verify that the server intelligently translates these requests to Kaltura API calls
5. Log the entire flow from client to server to API

### Running the Enhanced Server Manually

To run the enhanced MCP server manually:

```bash
python tests/integration/run_enhanced_server.py
```

This will start an MCP server on http://127.0.0.1:8765 with enhanced logging.

### Running the Test Client Manually

To run the test client against a running MCP server:

```bash
python tests/integration/test_mcp_client.py [server_url]
```

If `server_url` is not provided, it defaults to http://127.0.0.1:8765.

### Testing Direct API Calls

To test direct API calls with enhanced logging:

```bash
python tests/integration/direct_api_test.py
```

## Understanding the Logs

The enhanced tests produce detailed logs that show the flow from client to MCP server to Kaltura API:

1. **Client Request**: The client makes a request to the MCP server.
2. **MCP Server Processing**: The MCP server logs how it processes the request.
3. **Kaltura API Call**: The enhanced client logs the actual API call made to Kaltura.
4. **Kaltura API Response**: The enhanced client logs the response from Kaltura.
5. **MCP Server Response**: The MCP server logs how it processes the response.
6. **Client Response**: The client receives the response.

This logging chain helps verify that the MCP server is intelligently translating client requests into appropriate Kaltura API calls.

## Example Log Flow

For a request to list media entries, you might see logs like:

```
Client -> MCP: call_tool "kaltura.media.list" with arguments: {}
MCP: Processing tool request for "kaltura.media.list"
MCP -> Kaltura: API REQUEST [media.list_1234567890]: media.list
Kaltura -> MCP: API RESPONSE [media.list_1234567890]: Success (took 0.14s)
MCP: Formatting response for client
MCP -> Client: Response with 30 media entries
```

This shows the complete flow from client to MCP server to Kaltura API and back.

## Configuration

The enhanced tests use the same configuration as the regular integration tests, but with additional logging. The configuration is loaded from:

1. Environment variables (preferred for sensitive data)
2. `tests/integration/config.json` (for non-sensitive settings)

Make sure your environment variables are set correctly:

```bash
export KALTURA_PARTNER_ID=your_partner_id
export KALTURA_ADMIN_SECRET=your_admin_secret
export KALTURA_USER_ID=your_user_id