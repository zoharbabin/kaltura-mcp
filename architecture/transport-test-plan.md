# Transport Test Plan

This document outlines the test plan for the transport implementations in the Kaltura MCP server.

## Test Strategy

The test strategy for the transport implementations includes:

1. **Unit Tests**: Test each transport implementation in isolation
2. **Integration Tests**: Test the transport implementations with the server
3. **End-to-End Tests**: Test complete client-server communication with each transport

## Unit Tests

### Base Transport Tests

File: `tests/unit/transport/test_base.py`

```python
"""
Unit tests for the base transport interface.
"""
import pytest

from kaltura_mcp.transport.base import McpTransport


class TestBaseTransport:
    """Tests for the base transport interface."""
    
    def test_abstract_class(self):
        """Test that McpTransport is an abstract class."""
        with pytest.raises(TypeError):
            McpTransport({})
    
    def test_concrete_implementation(self):
        """Test that a concrete implementation can be created."""
        class ConcreteTransport(McpTransport):
            async def run(self, server):
                pass
        
        transport = ConcreteTransport({})
        assert isinstance(transport, McpTransport)
    
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test the initialize method."""
        class ConcreteTransport(McpTransport):
            async def run(self, server):
                pass
        
        transport = ConcreteTransport({})
        await transport.initialize()
        # No assertion needed, just checking that it doesn't raise an exception
    
    @pytest.mark.asyncio
    async def test_shutdown_method(self):
        """Test the shutdown method."""
        class ConcreteTransport(McpTransport):
            async def run(self, server):
                pass
        
        transport = ConcreteTransport({})
        await transport.shutdown()
        # No assertion needed, just checking that it doesn't raise an exception
```

### STDIO Transport Tests

File: `tests/unit/transport/test_stdio.py`

```python
"""
Unit tests for the STDIO transport.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kaltura_mcp.transport.stdio import StdioTransport


class TestStdioTransport:
    """Tests for the STDIO transport."""
    
    def test_initialization(self):
        """Test initialization of the STDIO transport."""
        config = {"server": {"transport": "stdio"}}
        transport = StdioTransport(config)
        assert transport.config == config
    
    @pytest.mark.asyncio
    async def test_run_method(self):
        """Test the run method."""
        config = {"server": {"transport": "stdio"}}
        transport = StdioTransport(config)
        
        # Mock the server
        server = AsyncMock()
        server.create_initialization_options.return_value = {"test": "options"}
        
        # Mock the stdio_server context manager
        mock_streams = (AsyncMock(), AsyncMock())
        mock_stdio_server = AsyncMock()
        mock_stdio_server.__aenter__.return_value = mock_streams
        
        with patch("kaltura_mcp.transport.stdio.stdio_server", return_value=mock_stdio_server):
            await transport.run(server)
        
        # Verify that the server's run method was called with the correct arguments
        server.run.assert_awaited_once_with(mock_streams[0], mock_streams[1], {"test": "options"})
    
    @pytest.mark.asyncio
    async def test_run_method_error(self):
        """Test the run method with an error."""
        config = {"server": {"transport": "stdio"}}
        transport = StdioTransport(config)
        
        # Mock the server
        server = AsyncMock()
        server.run.side_effect = Exception("Test error")
        
        # Mock the stdio_server context manager
        mock_streams = (AsyncMock(), AsyncMock())
        mock_stdio_server = AsyncMock()
        mock_stdio_server.__aenter__.return_value = mock_streams
        
        with patch("kaltura_mcp.transport.stdio.stdio_server", return_value=mock_stdio_server):
            with pytest.raises(Exception, match="Test error"):
                await transport.run(server)
```

### HTTP Transport Tests

File: `tests/unit/transport/test_http.py`

```python
"""
Unit tests for the HTTP transport.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kaltura_mcp.transport.http import HttpTransport, McpHttpHandler, ThreadedHTTPServer


class TestHttpTransport:
    """Tests for the HTTP transport."""
    
    def test_initialization(self):
        """Test initialization of the HTTP transport."""
        config = {"server": {"transport": "http", "host": "localhost", "port": 8000}}
        transport = HttpTransport(config)
        assert transport.config == config
        assert transport.host == "localhost"
        assert transport.port == 8000
        assert transport.server is None
        assert transport.server_thread is None
    
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test the initialize method."""
        config = {"server": {"transport": "http", "host": "localhost", "port": 8000}}
        transport = HttpTransport(config)
        await transport.initialize()
        # No assertion needed, just checking that it doesn't raise an exception
    
    @pytest.mark.asyncio
    async def test_run_method(self):
        """Test the run method."""
        config = {"server": {"transport": "http", "host": "localhost", "port": 8000}}
        transport = HttpTransport(config)
        
        # Mock the server
        server = MagicMock()
        
        # Mock the ThreadedHTTPServer
        mock_server = MagicMock()
        mock_thread = MagicMock()
        
        with patch("kaltura_mcp.transport.http.ThreadedHTTPServer", return_value=mock_server):
            with patch("kaltura_mcp.transport.http.threading.Thread", return_value=mock_thread):
                # Mock asyncio.sleep to raise an exception after the first call
                with patch("kaltura_mcp.transport.http.asyncio.sleep", side_effect=[None, Exception("Stop")]):
                    with pytest.raises(Exception, match="Stop"):
                        await transport.run(server)
        
        # Verify that the server was started
        assert McpHttpHandler.mcp_server == server
        assert transport.server == mock_server
        assert transport.server_thread == mock_thread
        mock_thread.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_method(self):
        """Test the shutdown method."""
        config = {"server": {"transport": "http", "host": "localhost", "port": 8000}}
        transport = HttpTransport(config)
        transport.server = MagicMock()
        
        await transport.shutdown()
        
        # Verify that the server was shut down
        transport.server.shutdown.assert_called_once()
        transport.server.server_close.assert_called_once()


class TestMcpHttpHandler:
    """Tests for the McpHttpHandler."""
    
    def test_handle_root(self):
        """Test handling the root endpoint."""
        handler = MagicMock()
        McpHttpHandler._handle_root(handler)
        
        # Verify that the response was sent
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_once_with("Content-type", "text/plain")
        handler.end_headers.assert_called_once()
        handler.wfile.write.assert_called_once_with(b"Kaltura MCP Server")
    
    def test_handle_info(self):
        """Test handling the info endpoint."""
        handler = MagicMock()
        handler._send_json_response = MagicMock()
        
        McpHttpHandler._handle_info(handler)
        
        # Verify that the response was sent
        handler._send_json_response.assert_called_once()
        info = handler._send_json_response.call_args[0][0]
        assert info["name"] == "Kaltura MCP Server"
        assert info["transport"] == "http"
    
    def test_handle_list_tools_no_server(self):
        """Test handling the list tools endpoint with no server."""
        handler = MagicMock()
        McpHttpHandler.mcp_server = None
        
        McpHttpHandler._handle_list_tools(handler)
        
        # Verify that an error was sent
        handler.send_error.assert_called_once_with(500, "Server not initialized")
    
    def test_handle_list_tools_with_server(self):
        """Test handling the list tools endpoint with a server."""
        handler = MagicMock()
        handler._run_coroutine = MagicMock(return_value=[{"name": "test_tool"}])
        handler._send_json_response = MagicMock()
        
        McpHttpHandler.mcp_server = MagicMock()
        McpHttpHandler.mcp_server.list_tools = MagicMock()
        
        McpHttpHandler._handle_list_tools(handler)
        
        # Verify that the response was sent
        handler._run_coroutine.assert_called_once_with(McpHttpHandler.mcp_server.list_tools())
        handler._send_json_response.assert_called_once_with({"tools": [{"name": "test_tool"}]})
```

### SSE Transport Tests

File: `tests/unit/transport/test_sse.py`

```python
"""
Unit tests for the SSE transport.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kaltura_mcp.transport.sse import SseTransport


class TestSseTransport:
    """Tests for the SSE transport."""
    
    def test_initialization(self):
        """Test initialization of the SSE transport."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        transport = SseTransport(config)
        assert transport.config == config
        assert transport.host == "localhost"
        assert transport.port == 8000
        assert transport.app is None
        assert transport.server_instance is None
        assert transport.mcp_server is None
        assert transport.active_connections == set()
    
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test the initialize method."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        transport = SseTransport(config)
        await transport.initialize()
        # No assertion needed, just checking that it doesn't raise an exception
    
    @pytest.mark.asyncio
    async def test_run_method(self):
        """Test the run method."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        transport = SseTransport(config)
        
        # Mock the server
        server = MagicMock()
        
        # Mock the app creation
        mock_app = MagicMock()
        transport._create_app = MagicMock(return_value=mock_app)
        
        # Mock uvicorn
        mock_config = MagicMock()
        mock_server_instance = AsyncMock()
        
        with patch("kaltura_mcp.transport.sse.uvicorn.Config", return_value=mock_config):
            with patch("kaltura_mcp.transport.sse.uvicorn.Server", return_value=mock_server_instance):
                await transport.run(server)
        
        # Verify that the server was started
        assert transport.mcp_server == server
        assert transport.app == mock_app
        assert transport.server_instance == mock_server_instance
        mock_server_instance.serve.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_method(self):
        """Test the shutdown method."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        transport = SseTransport(config)
        transport.server_instance = AsyncMock()
        
        await transport.shutdown()
        
        # Verify that the server was shut down
        transport.server_instance.shutdown.assert_awaited_once()
    
    def test_create_app(self):
        """Test creating the ASGI app."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        transport = SseTransport(config)
        
        with patch("kaltura_mcp.transport.sse.Starlette") as mock_starlette:
            transport._create_app()
        
        # Verify that Starlette was called with routes
        mock_starlette.assert_called_once()
        routes = mock_starlette.call_args[1]["routes"]
        assert len(routes) == 7  # 7 routes defined
```

### Transport Factory Tests

File: `tests/unit/transport/test_factory.py`

```python
"""
Unit tests for the transport factory.
"""
import pytest
from unittest.mock import patch

from kaltura_mcp.transport import TransportFactory
from kaltura_mcp.transport.stdio import StdioTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport


class TestTransportFactory:
    """Tests for the transport factory."""
    
    def test_create_stdio_transport(self):
        """Test creating a STDIO transport."""
        config = {"server": {"transport": "stdio"}}
        
        transport = TransportFactory.create_transport(config)
        
        assert isinstance(transport, StdioTransport)
        assert transport.config == config
    
    def test_create_http_transport(self):
        """Test creating an HTTP transport."""
        config = {"server": {"transport": "http", "host": "localhost", "port": 8000}}
        
        transport = TransportFactory.create_transport(config)
        
        assert isinstance(transport, HttpTransport)
        assert transport.config == config
        assert transport.host == "localhost"
        assert transport.port == 8000
    
    def test_create_sse_transport(self):
        """Test creating an SSE transport."""
        config = {"server": {"transport": "sse", "host": "localhost", "port": 8000}}
        
        transport = TransportFactory.create_transport(config)
        
        assert isinstance(transport, SseTransport)
        assert transport.config == config
        assert transport.host == "localhost"
        assert transport.port == 8000
    
    def test_create_unsupported_transport(self):
        """Test creating an unsupported transport."""
        config = {"server": {"transport": "unsupported"}}
        
        with pytest.raises(ValueError, match="Unsupported transport type: unsupported"):
            TransportFactory.create_transport(config)
```

## Integration Tests

### Server Integration Tests

File: `tests/integration/test_server_with_transports.py`

```python
"""
Integration tests for the server with different transports.
"""
import asyncio
import json
import os
import pytest
import requests
import subprocess
import time
from unittest.mock import AsyncMock, MagicMock, patch

from kaltura_mcp.config import load_config
from kaltura_mcp.server import KalturaMcpServer
from kaltura_mcp.transport import TransportFactory
from kaltura_mcp.transport.stdio import StdioTransport
from kaltura_mcp.transport.http import HttpTransport
from kaltura_mcp.transport.sse import SseTransport


class TestServerWithTransports:
    """Integration tests for the server with different transports."""
    
    @pytest.mark.asyncio
    async def test_server_with_stdio_transport(self, integration_config):
        """Test the server with STDIO transport."""
        # Override the transport type
        integration_config._raw_data["server"]["transport"] = "stdio"
        
        # Create a mock transport
        mock_transport = AsyncMock(spec=StdioTransport)
        
        # Create the server
        server = KalturaMcpServer(integration_config)
        server.transport = mock_transport
        
        # Initialize and run the server
        await server.initialize()
        await server.run()
        
        # Verify that the transport was used correctly
        mock_transport.initialize.assert_awaited_once()
        mock_transport.run.assert_awaited_once_with(server.app)
    
    @pytest.mark.asyncio
    async def test_server_with_http_transport(self, integration_config):
        """Test the server with HTTP transport."""
        # Override the transport type
        integration_config._raw_data["server"]["transport"] = "http"
        integration_config._raw_data["server"]["host"] = "localhost"
        integration_config._raw_data["server"]["port"] = 8000
        
        # Create a mock transport
        mock_transport = AsyncMock(spec=HttpTransport)
        
        # Create the server
        server = KalturaMcpServer(integration_config)
        server.transport = mock_transport
        
        # Initialize and run the server
        await server.initialize()
        await server.run()
        
        # Verify that the transport was used correctly
        mock_transport.initialize.assert_awaited_once()
        mock_transport.run.assert_awaited_once_with(server.app)
    
    @pytest.mark.asyncio
    async def test_server_with_sse_transport(self, integration_config):
        """Test the server with SSE transport."""
        # Override the transport type
        integration_config._raw_data["server"]["transport"] = "sse"
        integration_config._raw_data["server"]["host"] = "localhost"
        integration_config._raw_data["server"]["port"] = 8000
        
        # Create a mock transport
        mock_transport = AsyncMock(spec=SseTransport)
        
        # Create the server
        server = KalturaMcpServer(integration_config)
        server.transport = mock_transport
        
        # Initialize and run the server
        await server.initialize()
        await server.run()
        
        # Verify that the transport was used correctly
        mock_transport.initialize.assert_awaited_once()
        mock_transport.run.assert_awaited_once_with(server.app)
```

## End-to-End Tests

### STDIO Transport End-to-End Tests

File: `tests/integration/test_stdio_transport_e2e.py`

```python
"""
End-to-end tests for the STDIO transport.
"""
import asyncio
import json
import os
import pytest
import subprocess
import time
from unittest.mock import AsyncMock, MagicMock, patch

from mcp.client.lowlevel import Client
from mcp.client.stdio import stdio_client


class TestStdioTransportE2E:
    """End-to-end tests for the STDIO transport."""
    
    @pytest.mark.asyncio
    async def test_stdio_transport_e2e(self, integration_config):
        """Test the STDIO transport end-to-end."""
        # Create a temporary config file with STDIO transport
        config_path = "tests/integration/temp_config.yaml"
        with open(config_path, "w") as f:
            f.write(f"""
kaltura:
  partner_id: {integration_config.kaltura.partner_id}
  admin_secret: {integration_config.kaltura.admin_secret}
  user_id: {integration_config.kaltura.user_id}
  service_url: {integration_config.kaltura.service_url}
server:
  transport: stdio
  host: localhost
  port: 8000
            """)
        
        try:
            # Start the server as a subprocess
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "kaltura_mcp.server",
                "--config", config_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Wait for the server to start
            await asyncio.sleep(2)
            
            # Connect to the server using STDIO
            async with stdio_client() as streams:
                client = Client()
                await client.connect(streams[0], streams[1])
                
                # List available tools
                tools = await client.list_tools()
                assert len(tools) > 0
                
                # List available resources
                resources = await client.list_resources()
                assert len(resources) > 0
                
                # Call a tool
                result = await client.call_tool("kaltura.media.list", {"page_size": 5})
                assert len(result) > 0
        finally:
            # Clean up
            if process:
                process.terminate()
                await process.wait()
            
            if os.path.exists(config_path):
                os.remove(config_path)
```

### HTTP Transport End-to-End Tests

File: `tests/integration/test_http_transport_e2e.py`

```python
"""
End-to-end tests for the HTTP transport.
"""
import asyncio
import json
import os
import pytest
import requests
import subprocess
import time
from unittest.mock import AsyncMock, MagicMock, patch


class TestHttpTransportE2E:
    """End-to-end tests for the HTTP transport."""
    
    @pytest.mark.asyncio
    async def test_http_transport_e2e(self, integration_config):
        """Test the HTTP transport end-to-end."""
        # Create a temporary config file with HTTP transport
        config_path = "tests/integration/temp_config.yaml"
        with open(config_path, "w") as f:
            f.write(f"""
kaltura:
  partner_id: {integration_config.kaltura.partner_id}
  admin_secret: {integration_config.kaltura.admin_secret}
  user_id: {integration_config.kaltura.user_id}
  service_url: {integration_config.kaltura.service_url}
server:
  transport: http
  host: localhost
  port: 8000
            """)
        
        try:
            # Start the server as a subprocess
            process = subprocess.Popen(
                ["python", "-m", "kaltura_mcp.server", "--config", config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Wait for the server to start
            time.sleep(2)
            
            # Test connection to the server
            response = requests.get("http://localhost:8000")
            assert response.status_code == 200
            
            # List available tools
            response = requests.get("http://localhost:8000/mcp/tools")
            assert response.status_code == 200
            tools = response.json()["tools"]
            assert len(tools) > 0
            
            # List available resources
            response = requests.get("http://localhost:8000/mcp/resources")
            assert response.status_code == 200
            resources = response.json()["resources"]
            assert len(resources) > 0
            
            # Call a tool
            response = requests.post(
                "http://localhost:8000/mcp/tools/call",
                json={"name": "kaltura.media.list", "arguments": {"page_size": 5}},
            )
            assert response.status_code == 200
            result = response.json()
            assert len(result) > 0
        finally:
            # Clean up
            if process:
                process.terminate()
                process.wait()
            
            if os.path.exists(config_path):
                os.remove(config_path)
```

### SSE Transport End-to-End Tests

File: `tests/integration/test_sse_transport_e2e.py`

```python
"""
End-to-end tests for the SSE transport.
"""
import asyncio
import json
import os
import pytest
import requests
import subprocess
import time
from unittest.mock import AsyncMock, MagicMock, patch

import sseclient


class TestSseTransportE2E:
    """End-to-end tests for the SSE transport."""
    
    @pytest.mark.asyncio
    async def test_sse_transport_e2e(self, integration_config):
        """Test the SSE transport end-to-end."""
        # Create a temporary config file with SSE transport
        config_path = "tests/integration/temp_config.yaml"
        with open(config_path, "w") as f:
            f.write(f"""
kaltura:
  partner_id: {integration_config.kaltura.partner_id}
  admin_secret: {integration_config.kaltura.admin_secret}
  user_id: {integration_config.kaltura.user_id}
  service_url: {integration_config.kaltura.service_url}
server:
  transport: sse
  host: localhost
  port: 8000
            """)
        
        try:
            # Start the server as a subprocess
            process = subprocess.Popen(
                ["python", "-m", "kaltura_mcp.server", "--config", config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Wait for the server to start
            time.sleep(2)
            
            # Test connection to the server
            response = requests.get("http://localhost:8000")
            assert response.status_code == 200
            
            # List available tools
            response = requests.get("http://localhost:8000/mcp/tools")
            assert response.status_code == 200
            tools = response.json()["tools"]
            assert len(tools) > 0
            
            # List available resources
            response = requests.get("http://localhost:8000/mcp/resources")
            assert response.status_code == 200
            resources = response.json()["resources"]
            assert len(resources) > 0
            
            # Call a tool
            response = requests.post(
                "http://localhost:8000/mcp/tools/call",
                json={"name": "kaltura.media.list", "arguments": {"page_size": 5}},
            )
            assert response.status_code == 200
            result = response.json()
            assert len(result) > 0
            
            # Establish SSE connection
            response = requests.get("http://localhost:8000/mcp/sse", stream=True)
            assert response.status_code == 200
            
            # Create SSE client
            client = sseclient.SSEClient(response)
            
            # Get the first event (should be "connected")
            event = next(client.events())
            assert event.event == "connected"
        finally:
            # Clean up
            if process:
                process.terminate()
                process.wait()
            
            if os.path.exists(config_path):
                os.remove(config_path)
```

## Test Execution

The tests can be run using pytest:

```bash
# Run all tests
pytest tests/unit/transport tests/integration

# Run only unit tests
pytest tests/unit/transport

# Run only integration tests
pytest tests/integration

# Run only end-to-end tests
pytest tests/integration/test_*_transport_e2e.py
```

## Test Coverage

To ensure comprehensive test coverage, the tests should cover:

1. **Functionality**: All transport features and behaviors
2. **Error Handling**: How transports handle errors
3. **Edge Cases**: Unusual or extreme conditions
4. **Performance**: Response times and resource usage
5. **Security**: Authentication and authorization

## Continuous Integration

The tests should be integrated into the project's CI/CD pipeline to ensure that changes to the transport implementations don't break existing functionality.

Example GitHub Actions workflow:

```yaml
name: Transport Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run unit tests
      run: |
        pytest tests/unit/transport
    - name: Run integration tests
      run: |
        pytest tests/integration
```

## Test Documentation

Each test file should include:

1. A module docstring explaining the purpose of the tests
2. Class docstrings explaining the test class
3. Method docstrings explaining each test case
4. Comments explaining complex test logic

This documentation helps other developers understand the tests and makes it easier to maintain them.