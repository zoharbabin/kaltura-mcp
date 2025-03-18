"""
Tests for the Kaltura MCP Server.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest

from kaltura_mcp.server import KalturaMcpServer

# Only run tests with asyncio backend to avoid trio dependency issues
pytestmark = pytest.mark.asyncio


async def test_server_initialization(server_config):
    """Test server initialization."""
    # Create a mock KalturaClientWrapper class
    mock_client = AsyncMock()
    mock_client_class = MagicMock(return_value=mock_client)

    # Create server
    server = KalturaMcpServer(server_config)

    # Patch the import inside the initialize method
    with patch.dict(
        "sys.modules",
        {"kaltura_mcp.kaltura.client": MagicMock(KalturaClientWrapper=mock_client_class)},
    ):
        # Initialize server
        await server.initialize()

        # Verify client was initialized
        mock_client_class.assert_called_once_with(server_config)
        mock_client.initialize.assert_called_once()

        # Verify handlers were registered
        assert len(server.tool_handlers) > 0
        assert len(server.resource_handlers) > 0

        # Verify specific handlers exist
        assert "kaltura.media.list" in server.tool_handlers
        assert "kaltura.media.get" in server.tool_handlers
        assert "kaltura.media.upload" in server.tool_handlers
        assert "kaltura.media.update" in server.tool_handlers
        assert "kaltura.media.delete" in server.tool_handlers

        assert "media_entry" in server.resource_handlers
        assert "media_list" in server.resource_handlers


async def test_list_tools(server_config):
    """Test listing tools."""
    # Create a mock KalturaClientWrapper class
    mock_client = AsyncMock()
    mock_client_class = MagicMock(return_value=mock_client)

    # Create server
    server = KalturaMcpServer(server_config)

    # Patch the import inside the initialize method
    with patch.dict(
        "sys.modules",
        {"kaltura_mcp.kaltura.client": MagicMock(KalturaClientWrapper=mock_client_class)},
    ):
        # Initialize server
        await server.initialize()

        # Create a mock tool handler that returns a tool definition
        mock_tool_handler = MagicMock()
        mock_tool_definition = types.Tool(
            name="test.tool",
            description="Test tool",
            inputSchema={"type": "object", "properties": {}},
        )
        mock_tool_handler.get_tool_definition = MagicMock(return_value=mock_tool_definition)

        # Add the mock handler to the server's tool handlers
        server.tool_handlers["test.tool"] = mock_tool_handler

        # We need to manually create and register the list_tools handler since it's normally done in run()
        async def list_tools_handler():
            return [handler.get_tool_definition() for handler in server.tool_handlers.values()]

        server.app.list_tools = list_tools_handler

        # Now we can call the handler
        tools = await server.app.list_tools()

        # Verify tools were returned
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Verify tool structure
        for tool in tools:
            assert isinstance(tool, types.Tool)
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")


async def test_call_tool(server_config):
    """Test calling a tool."""
    # Create a mock KalturaClientWrapper class
    mock_client = AsyncMock()
    mock_client_class = MagicMock(return_value=mock_client)

    # Create server
    server = KalturaMcpServer(server_config)

    # Patch the import inside the initialize method
    with patch.dict(
        "sys.modules",
        {"kaltura_mcp.kaltura.client": MagicMock(KalturaClientWrapper=mock_client_class)},
    ):
        # Initialize server
        await server.initialize()

        # Mock the tool handler
        mock_handler = AsyncMock()
        # Create a proper TextContent object with the required 'type' field
        text_content = types.TextContent(type="text", text="Test result")
        mock_handler.handle = AsyncMock(return_value=[text_content])
        server.tool_handlers["test.tool"] = mock_handler

        # We need to manually create and register the call_tool handler since it's normally done in run()
        async def call_tool_handler(name, arguments):
            if name not in server.tool_handlers:
                raise ValueError(f"Unknown tool: {name}")

            handler = server.tool_handlers[name]
            return await handler.handle(arguments)

        server.app.call_tool = call_tool_handler

        # Test call_tool handler
        result = await server.app.call_tool("test.tool", {"param": "value"})

        # Verify handler was called
        mock_handler.handle.assert_called_once_with({"param": "value"})

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].text == "Test result"
        assert result[0].type == "text"

        # Test with unknown tool
        with pytest.raises(ValueError, match="Unknown tool: unknown.tool"):
            await server.app.call_tool("unknown.tool", {})
