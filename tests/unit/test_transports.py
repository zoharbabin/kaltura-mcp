"""
Tests for the transport implementations.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.lowlevel import Server

from kaltura_mcp.transport.base import McpTransport
from kaltura_mcp.transport.http import HttpTransport, McpHttpHandler
from kaltura_mcp.transport.sse import SseTransport
from kaltura_mcp.transport.stdio import StdioTransport


# Define a test transport class outside the test classes to avoid collection warnings
# Use leading underscore to indicate it's a private implementation detail
class _TestTransportImpl(McpTransport):
    """Test transport implementation."""

    async def run(self, server):
        """Run the transport."""
        self.run_called = True
        self.run_args = (server,)


class TestBaseTransport:
    """Tests for the base transport interface."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return {
            "server": {
                "transport": "stdio",
                "host": "localhost",
                "port": 8000,
            }
        }

    @pytest.fixture
    def mock_server(self):
        """Create a mock server."""
        server = AsyncMock(spec=Server)
        server.create_initialization_options.return_value = {}
        return server

    @pytest.fixture
    def test_transport(self, config):
        """Create a test transport."""
        return _TestTransportImpl(config)

    @pytest.mark.asyncio
    async def test_initialize(self, test_transport):
        """Test the initialize method."""
        await test_transport.initialize()
        # No assertions needed, just checking that it doesn't raise an exception

    @pytest.mark.asyncio
    async def test_shutdown(self, test_transport):
        """Test the shutdown method."""
        await test_transport.shutdown()
        # No assertions needed, just checking that it doesn't raise an exception


class TestStdioTransport:
    """Tests for the STDIO transport."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return {
            "server": {
                "transport": "stdio",
                "host": "localhost",
                "port": 8000,
            }
        }

    @pytest.fixture
    def mock_server(self):
        """Create a mock server."""
        server = AsyncMock(spec=Server)
        server.create_initialization_options.return_value = {}
        return server

    @pytest.fixture
    def mock_streams(self):
        """Create mock streams."""
        return (AsyncMock(), AsyncMock())

    @pytest.mark.asyncio
    @patch("kaltura_mcp.transport.stdio.stdio_server")
    async def test_run(self, mock_stdio_server, config, mock_server, mock_streams):
        """Test the run method."""
        # Set up the mock stdio_server context manager
        mock_stdio_server.return_value.__aenter__.return_value = mock_streams

        # Create the transport and run it
        transport = StdioTransport(config)
        await transport.run(mock_server)

        # Check that stdio_server was called
        mock_stdio_server.assert_called_once()

        # Check that the server's run method was called with the streams
        mock_server.run.assert_called_once_with(
            mock_streams[0], mock_streams[1], mock_server.create_initialization_options.return_value
        )

    @pytest.mark.asyncio
    @patch("kaltura_mcp.transport.stdio.stdio_server")
    async def test_run_error(self, mock_stdio_server, config, mock_server):
        """Test error handling in the run method."""
        # Set up the mock stdio_server to raise an exception
        mock_stdio_server.return_value.__aenter__.side_effect = Exception("Test error")

        # Create the transport
        transport = StdioTransport(config)

        # Run the transport and check that it raises the exception
        with pytest.raises(Exception, match="Test error"):
            await transport.run(mock_server)


class TestHttpTransport:
    """Tests for the HTTP transport."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return {
            "server": {
                "transport": "http",
                "host": "localhost",
                "port": 8000,
            }
        }

    @pytest.fixture
    def mock_server(self):
        """Create a mock server."""
        server = AsyncMock(spec=Server)
        server.create_initialization_options.return_value = {}
        return server

    @pytest.mark.asyncio
    async def test_initialize(self, config):
        """Test the initialize method."""
        transport = HttpTransport(config)
        await transport.initialize()
        assert transport.host == "localhost"
        assert transport.port == 8000

    @pytest.mark.asyncio
    @patch("kaltura_mcp.transport.http.ThreadedHTTPServer")
    @patch("kaltura_mcp.transport.http.threading.Thread")
    @patch("kaltura_mcp.transport.http.asyncio.sleep")
    async def test_run(self, mock_sleep, mock_thread, mock_server_class, config, mock_server):
        """Test the run method."""
        # Set up the mocks
        mock_server_instance = MagicMock()
        mock_server_class.return_value = mock_server_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        # Make sleep raise an exception to break the infinite loop
        mock_sleep.side_effect = [None, Exception("Break loop")]

        # Create the transport
        transport = HttpTransport(config)

        # Run the transport and check that it raises the exception
        with pytest.raises(Exception, match="Break loop"):
            await transport.run(mock_server)

        # Check that the server was created with the correct host and port
        mock_server_class.assert_called_once()
        args, kwargs = mock_server_class.call_args
        assert args[0] == ("localhost", 8000)
        assert args[1] == McpHttpHandler

        # Check that the thread was created and started
        mock_thread.assert_called_once_with(target=mock_server_instance.serve_forever)
        assert mock_thread_instance.daemon is True
        mock_thread_instance.start.assert_called_once()

        # Check that McpHttpHandler.mcp_server was set
        assert McpHttpHandler.mcp_server == mock_server

    @pytest.mark.asyncio
    async def test_shutdown(self, config):
        """Test the shutdown method."""
        transport = HttpTransport(config)
        transport.server = MagicMock()
        await transport.shutdown()
        transport.server.shutdown.assert_called_once()
        transport.server.server_close.assert_called_once()


class TestSseTransport:
    """Tests for the SSE transport."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return {
            "server": {
                "transport": "sse",
                "host": "localhost",
                "port": 8000,
            }
        }

    @pytest.fixture
    def mock_server(self):
        """Create a mock server."""
        server = AsyncMock(spec=Server)
        server.create_initialization_options.return_value = {}
        return server

    @pytest.mark.asyncio
    async def test_initialize(self, config):
        """Test the initialize method."""
        transport = SseTransport(config)
        await transport.initialize()
        assert transport.host == "localhost"
        assert transport.port == 8000

    @pytest.mark.asyncio
    @patch("kaltura_mcp.transport.sse.uvicorn")
    async def test_run(self, mock_uvicorn, config, mock_server):
        """Test the run method."""
        # Set up the mocks
        mock_config = MagicMock()
        mock_uvicorn.Config.return_value = mock_config
        mock_server_instance = AsyncMock()
        mock_uvicorn.Server.return_value = mock_server_instance

        # Create the transport
        transport = SseTransport(config)

        # Run the transport
        await transport.run(mock_server)

        # Check that the app was created
        assert transport.app is not None
        assert transport.mcp_server == mock_server

        # Check that uvicorn was configured correctly
        mock_uvicorn.Config.assert_called_once_with(
            transport.app,
            host="localhost",
            port=8000,
            log_level="info",
            timeout_keep_alive=30,  # Shorter keep-alive timeout to avoid hanging
            limit_concurrency=100,  # Limit concurrent connections
            timeout_graceful_shutdown=10,  # Faster graceful shutdown
            reload=False,  # Disable auto-reload
            workers=1,  # Use only one worker for testing
        )
        mock_uvicorn.Server.assert_called_once_with(mock_config)
        mock_server_instance.serve.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown(self, config):
        """Test the shutdown method."""
        transport = SseTransport(config)
        transport.server_instance = AsyncMock()
        await transport.shutdown()
        transport.server_instance.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_app(self, config):
        """Test the _create_app method."""
        transport = SseTransport(config)
        app = transport._create_app()
        assert app is not None
        # Check that the app has the expected routes
        route_paths = [route.path for route in app.routes]
        assert "/" in route_paths
        assert "/mcp/info" in route_paths
        assert "/mcp/tools" in route_paths
        assert "/mcp/resources" in route_paths
        assert "/mcp/resources/read" in route_paths
        assert "/mcp/tools/call" in route_paths
        assert "/mcp/sse" in route_paths

    @pytest.mark.asyncio
    async def test_handle_root(self, config):
        """Test the _handle_root method."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_root(request)
        assert response.body == b"Kaltura MCP Server"
        assert response.media_type == "text/plain"

    @pytest.mark.asyncio
    async def test_handle_info(self, config):
        """Test the _handle_info method."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_info(request)
        data = json.loads(response.body.decode())
        assert data["name"] == "Kaltura MCP Server"
        assert data["version"] == "1.0.0"
        assert data["transport"] == "sse"

    @pytest.mark.asyncio
    async def test_handle_list_tools_no_server(self, config):
        """Test the _handle_list_tools method with no server."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_list_tools(request)
        assert response.status_code == 500
        data = json.loads(response.body.decode())
        assert data["error"] == "Server not initialized"

    @pytest.mark.asyncio
    async def test_handle_list_tools(self, config, mock_server):
        """Test the _handle_list_tools method."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        mock_server.list_tools = AsyncMock(return_value=[{"name": "test_tool"}])
        request = MagicMock()
        response = await transport._handle_list_tools(request)
        assert response.status_code == 200
        data = json.loads(response.body.decode())
        assert data["tools"] == [{"name": "test_tool"}]

    @pytest.mark.asyncio
    async def test_handle_list_resources_no_server(self, config):
        """Test the _handle_list_resources method with no server."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_list_resources(request)
        assert response.status_code == 500
        data = json.loads(response.body.decode())
        assert data["error"] == "Server not initialized"

    @pytest.mark.asyncio
    async def test_handle_list_resources(self, config, mock_server):
        """Test the _handle_list_resources method."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        mock_server.list_resources = AsyncMock(return_value=[{"uri": "test_resource"}])
        request = MagicMock()
        response = await transport._handle_list_resources(request)
        assert response.status_code == 200
        data = json.loads(response.body.decode())
        assert data["resources"] == [{"uri": "test_resource"}]

    @pytest.mark.asyncio
    async def test_handle_read_resource_no_server(self, config):
        """Test the _handle_read_resource method with no server."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_read_resource(request)
        assert response.status_code == 500
        data = json.loads(response.body.decode())
        assert data["error"] == "Server not initialized"

    @pytest.mark.asyncio
    async def test_handle_read_resource_no_uri(self, config, mock_server):
        """Test the _handle_read_resource method with no URI."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        request = MagicMock()
        request.query_params = {}
        response = await transport._handle_read_resource(request)
        assert response.status_code == 400
        data = json.loads(response.body.decode())
        assert data["error"] == "Missing uri parameter"

    @pytest.mark.asyncio
    async def test_handle_read_resource(self, config, mock_server):
        """Test the _handle_read_resource method."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        mock_server.read_resource = AsyncMock(return_value={"content": "test_content"})
        request = MagicMock()
        request.query_params = {"uri": "test_uri"}
        response = await transport._handle_read_resource(request)
        assert response.status_code == 200
        data = json.loads(response.body.decode())
        assert data == {"content": "test_content"}
        mock_server.read_resource.assert_called_once_with("test_uri")

    @pytest.mark.asyncio
    async def test_handle_call_tool_no_server(self, config):
        """Test the _handle_call_tool method with no server."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_call_tool(request)
        assert response.status_code == 500
        data = json.loads(response.body.decode())
        assert data["error"] == "Server not initialized"

    @pytest.mark.asyncio
    async def test_handle_call_tool_no_name(self, config, mock_server):
        """Test the _handle_call_tool method with no name."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        request = MagicMock()
        request.json = AsyncMock(return_value={})
        response = await transport._handle_call_tool(request)
        assert response.status_code == 400
        data = json.loads(response.body.decode())
        assert data["error"] == "Missing name parameter"

    @pytest.mark.asyncio
    async def test_handle_call_tool(self, config, mock_server):
        """Test the _handle_call_tool method."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        mock_server.call_tool = AsyncMock(return_value={"result": "test_result"})
        request = MagicMock()
        request.json = AsyncMock(return_value={"name": "test_tool", "arguments": {"arg": "value"}})
        response = await transport._handle_call_tool(request)
        assert response.status_code == 200
        data = json.loads(response.body.decode())
        assert data == {"result": "test_result"}
        mock_server.call_tool.assert_called_once_with("test_tool", {"arg": "value"})

    @pytest.mark.asyncio
    async def test_handle_sse_connection_no_server(self, config):
        """Test the _handle_sse_connection method with no server."""
        transport = SseTransport(config)
        request = MagicMock()
        response = await transport._handle_sse_connection(request)
        assert response.status_code == 500
        assert response.body == b"Server not initialized"

    @pytest.mark.asyncio
    @patch("kaltura_mcp.transport.sse.Response")
    async def test_handle_sse_connection(self, mock_response, config, mock_server):
        """Test the _handle_sse_connection method."""
        transport = SseTransport(config)
        transport.mcp_server = mock_server
        request = MagicMock()

        # Mock the Response class
        mock_response_instance = MagicMock()
        mock_response.return_value = mock_response_instance
        mock_response_instance.media_type = "text/event-stream"
        mock_response_instance.headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }

        await transport._handle_sse_connection(request)

        # Check that Response was called with the correct arguments
        mock_response.assert_called_once()
        args, kwargs = mock_response.call_args
        assert kwargs["media_type"] == "text/event-stream"
        assert kwargs["headers"] == {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }

    @pytest.mark.asyncio
    async def test_notify_clients(self, config):
        """Test the _notify_clients method."""
        transport = SseTransport(config)
        transport.active_connections = {1, 2, 3}
        await transport._notify_clients({"event": "test_event"})
        # No assertions needed, just checking that it doesn't raise an exception
