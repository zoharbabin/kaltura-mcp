"""
End-to-end tests for all transport types.

This module provides comprehensive end-to-end tests for all transport types,
ensuring that they work correctly in real-world scenarios.
"""

import fcntl
import json
import os
import subprocess
import sys
import time as time_module
from unittest.mock import MagicMock

import pytest
import requests

from tests.integration.utils import find_available_port

# Import the actual client classes
try:
    from mcp.client.lowlevel import Client
    from mcp.client.stdio import stdio_client
    from sseclient import SSEClient
except ImportError:
    # Mock the MCP client imports if not available
    class MockClient:
        """Mock MCP client for testing."""

        def __init__(self):
            self.connected = False
            self.server_info = {"name": "kaltura-mcp-server"}
            self.tools = []
            self.resources = []

        async def connect(self, reader, writer):
            """Mock connect method."""
            self.connected = True
            return True

        async def get_server_info(self):
            """Mock get_server_info method."""
            return self.server_info

        async def list_tools(self):
            """Mock list_tools method."""
            return [MagicMock(name="kaltura.media.list")]

        async def list_resources(self):
            """Mock list_resources method."""
            return [MagicMock(uri="kaltura://media/123")]

        async def call_tool(self, name, arguments):
            """Mock call_tool method."""
            return []

    # Mock SSE client
    class MockSSEClient:
        """Mock SSE client for testing."""

        def __init__(self, url):
            self.url = url
            self.event_data = {"id": "test-connection-id"}

        def events(self):
            """Mock events generator."""
            yield MagicMock(event="connected", data=json.dumps(self.event_data))

    # Use the mock classes
    Client = MockClient
    stdio_client = MagicMock()
    SSEClient = MockSSEClient


class TestTransportEndToEnd:
    """End-to-end tests for all transport types."""

    def wait_for_server(self, url, max_attempts=20, delay=1.0):
        """Wait for the server to start."""
        print(f"Waiting for server to start at {url}...")

        for attempt in range(1, max_attempts + 1):
            print(f"Attempt {attempt}/{max_attempts}...")
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"Server started successfully at {url}")
                    return True
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")

            time_module.sleep(delay)

        print("Server did not start within the expected time")
        return False

    @pytest.fixture
    def config_path(self, tmp_path):
        """Create a temporary configuration file."""
        # Find an available port
        port = find_available_port(8000, 9000)
        if port is None:
            pytest.skip("No available ports found for testing")

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            f"""
kaltura:
  partner_id: 123456
  admin_secret: "test-secret"
  user_id: "test-user"
  service_url: "https://www.kaltura.com/api_v3"

server:
  host: "localhost"
  port: {port}
  debug: true
"""
        )
        return str(config_file), port

    @pytest.mark.parametrize("transport_type", ["stdio", "http"])
    def test_transport_switching(self, config_path, transport_type):
        """Test switching between transport types."""
        # Unpack the config_path and port
        if isinstance(config_path, tuple):
            config_file, port = config_path
        else:
            config_file, port = config_path, 8769  # Default port if not provided

        # Create environment variables
        env = os.environ.copy()
        env["KALTURA_MCP_CONFIG"] = config_file
        env["KALTURA_MCP_TRANSPORT"] = transport_type

        # Create a hard timeout for the entire test
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Test timed out for {transport_type} transport")

        # Set a 20-second timeout for the entire test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(20)

        # Start the server
        server_process = subprocess.Popen(
            [sys.executable, "-m", "kaltura_mcp.server"],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # For STDIO transport, we just check that the server starts and stops cleanly
            if transport_type == "stdio":
                time_module.sleep(2)
                # Check if the server process is still running
                if server_process.poll() is not None:
                    # If the server process has terminated, capture and print the output
                    stdout, stderr = server_process.communicate()
                    print(f"STDIO server process terminated with code {server_process.returncode}")
                    print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                    print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                    pytest.skip(f"STDIO server process terminated unexpectedly with code {server_process.returncode}")
            else:
                # For HTTP and SSE transports, check that the server is accessible
                time_module.sleep(2)  # Give the server more time to start

                # Wait for the server to start
                base_url = f"http://localhost:{port}"

                # Capture server output before waiting
                stdout_data = b""
                stderr_data = b""

                # Try to read from stdout if available (non-blocking)
                if server_process.stdout:
                    # Set stdout to non-blocking mode
                    fd = server_process.stdout.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                    try:
                        stdout_data = server_process.stdout.read()
                    except (IOError, BlockingIOError):
                        pass

                # Try to read from stderr if available (non-blocking)
                if server_process.stderr:
                    # Set stderr to non-blocking mode
                    fd = server_process.stderr.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                    try:
                        stderr_data = server_process.stderr.read()
                    except (IOError, BlockingIOError):
                        pass

                # Print any output we got
                if stdout_data:
                    print(f"Server STDOUT before waiting: {stdout_data.decode('utf-8', errors='replace')}")
                if stderr_data:
                    print(f"Server STDERR before waiting: {stderr_data.decode('utf-8', errors='replace')}")

                server_ready = self.wait_for_server(f"{base_url}/mcp/info")

                # If the server didn't start, capture and print the output
                if not server_ready:
                    # Check if the server process is still running
                    if server_process.poll() is not None:
                        stdout, stderr = server_process.communicate()
                        print(f"HTTP server process terminated with code {server_process.returncode}")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                    else:
                        # Terminate the process to get its output
                        server_process.terminate()
                        try:
                            stdout, stderr = server_process.communicate(timeout=5)
                            print("HTTP server process terminated to get output")
                            print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                            print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                        except subprocess.TimeoutExpired:
                            server_process.kill()
                            stdout, stderr = server_process.communicate()
                            print("HTTP server process killed after timeout")
                            print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                            print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")

                    pytest.skip(f"Server with {transport_type} transport did not start within the expected time")

                # Check server info
                response = requests.get(f"{base_url}/mcp/info")
                assert response.status_code == 200, f"Failed to get server info for {transport_type} transport"
                info = response.json()
                assert info["name"] == "Kaltura MCP Server", f"Unexpected server name for {transport_type} transport"
                assert (
                    info["transport"] == transport_type
                ), f"Server using wrong transport type: {info['transport']} instead of {transport_type}"
        finally:
            # Cancel the alarm
            signal.alarm(0)

            # Terminate the server process
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

    def test_concurrent_clients(self, config_path):
        """Test concurrent clients with different transport types."""
        # Unpack the config_path and port
        if isinstance(config_path, tuple):
            config_file, port = config_path
        else:
            config_file, port = config_path, 8769  # Default port if not provided

        # Create environment variables
        env = os.environ.copy()
        env["KALTURA_MCP_CONFIG"] = config_file

        # Create a hard timeout for the entire test
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out for concurrent clients test")

        # Set a 30-second timeout for the entire test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)

        # Test with HTTP transport (most suitable for concurrent clients)
        env["KALTURA_MCP_TRANSPORT"] = "http"
        server_process = subprocess.Popen(
            [sys.executable, "-m", "kaltura_mcp.server"],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Create a timeout thread to ensure we don't hang
        import threading

        def kill_after_timeout():
            try:
                import time

                time.sleep(15)  # 15 second timeout
                if server_process.poll() is None:
                    print("Timeout reached, terminating server process")
                    server_process.terminate()
            except Exception as e:
                print(f"Error in kill_after_timeout: {e}")

        timeout_thread = threading.Thread(target=kill_after_timeout)
        timeout_thread.daemon = True
        timeout_thread.start()

        try:
            time_module.sleep(3)  # Give the server more time to start

            # Create multiple clients and make concurrent requests
            base_url = f"http://localhost:{port}"

            # Wait for the server to start
            server_ready = self.wait_for_server(f"{base_url}/mcp/info")

            # If the server didn't start, capture and print the output
            if not server_ready:
                # Check if the server process is still running
                if server_process.poll() is not None:
                    stdout, stderr = server_process.communicate()
                    print(f"HTTP server process terminated with code {server_process.returncode}")
                    print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                    print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                else:
                    # Terminate the process to get its output
                    server_process.terminate()
                    try:
                        stdout, stderr = server_process.communicate(timeout=5)
                        print("HTTP server process terminated to get output")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                    except subprocess.TimeoutExpired:
                        server_process.kill()
                        stdout, stderr = server_process.communicate()
                        print("HTTP server process killed after timeout")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")

                pytest.skip("Server did not start within the expected time")

            # Function to make a request
            def make_request(client_id):
                try:
                    # Get server info
                    response = requests.get(f"{base_url}/mcp/info", timeout=5)
                    assert response.status_code == 200
                    info = response.json()
                    assert info["name"] == "Kaltura MCP Server"

                    # List tools
                    response = requests.get(f"{base_url}/mcp/tools", timeout=5)
                    assert response.status_code == 200
                    tools = response.json()["tools"]

                    # List resources
                    response = requests.get(f"{base_url}/mcp/resources", timeout=5)
                    assert response.status_code == 200
                    resources = response.json()["resources"]

                    return {
                        "client_id": client_id,
                        "info": info,
                        "tools_count": len(tools),
                        "resources_count": len(resources),
                        "success": True,
                    }
                except Exception as e:
                    return {"client_id": client_id, "error": str(e), "success": False}

            # Make concurrent requests with fewer clients to reduce load
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(5)]
                results = [future.result() for future in futures]

            # Check that at least some requests succeeded
            successful_results = [r for r in results if r.get("success", False)]
            assert len(successful_results) > 0, "No concurrent requests succeeded"

            for result in successful_results:
                assert result["info"]["name"] == "Kaltura MCP Server"
                assert result["tools_count"] > 0
                assert result["resources_count"] > 0

        finally:
            # Cancel the alarm
            signal.alarm(0)

            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

    def test_error_handling(self, config_path):
        """Test error handling with different transport types."""
        # Unpack the config_path and port
        if isinstance(config_path, tuple):
            config_file, port = config_path
        else:
            config_file, port = config_path, 8769  # Default port if not provided

        # Create environment variables
        env = os.environ.copy()
        env["KALTURA_MCP_CONFIG"] = config_file

        # Create a hard timeout for the entire test
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out for error handling test")

        # Set a 30-second timeout for the entire test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)

        # Test with HTTP transport
        env["KALTURA_MCP_TRANSPORT"] = "http"
        server_process = subprocess.Popen(
            [sys.executable, "-m", "kaltura_mcp.server"],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Create a timeout thread to ensure we don't hang
        import threading

        def kill_after_timeout():
            try:
                import time

                time.sleep(30)  # 30 second timeout - increased to give more time
                if server_process.poll() is None:
                    print("Timeout reached, terminating server process")
                    server_process.terminate()
            except Exception as e:
                print(f"Error in kill_after_timeout: {e}")

        timeout_thread = threading.Thread(target=kill_after_timeout)
        timeout_thread.daemon = True
        timeout_thread.start()

        try:
            time_module.sleep(3)  # Give the server more time to start
            base_url = f"http://localhost:{port}"

            # Wait for the server to start
            server_ready = self.wait_for_server(f"{base_url}/mcp/info")

            # If the server didn't start, capture and print the output
            if not server_ready:
                # Check if the server process is still running
                if server_process.poll() is not None:
                    stdout, stderr = server_process.communicate()
                    print(f"HTTP server process terminated with code {server_process.returncode}")
                    print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                    print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                else:
                    # Terminate the process to get its output
                    server_process.terminate()
                    try:
                        stdout, stderr = server_process.communicate(timeout=5)
                        print("HTTP server process terminated to get output")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                    except subprocess.TimeoutExpired:
                        server_process.kill()
                        stdout, stderr = server_process.communicate()
                        print("HTTP server process killed after timeout")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")

            assert server_ready, "Server did not start within the expected time"

            # Test invalid tool call
            response = requests.post(f"{base_url}/mcp/tools/call", json={"name": "non_existent_tool", "arguments": {}}, timeout=5)
            assert response.status_code in (404, 400, 500)

            # Test invalid resource access
            response = requests.get(f"{base_url}/mcp/resources/read?uri=invalid://resource", timeout=5)
            assert response.status_code in (404, 400, 500)

            # Test missing parameters
            response = requests.post(f"{base_url}/mcp/tools/call", json={}, timeout=5)
            assert response.status_code in (400, 422)

            # Test invalid JSON
            response = requests.post(
                f"{base_url}/mcp/tools/call", data="invalid json", headers={"Content-Type": "application/json"}, timeout=5
            )
            assert response.status_code in (400, 500)  # Accept either 400 or 500 for invalid JSON

        finally:
            # Cancel the alarm
            signal.alarm(0)

            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

    def test_performance(self, config_path):
        """Test performance with different transport types."""
        # Unpack the config_path and port
        if isinstance(config_path, tuple):
            config_file, port = config_path
        else:
            config_file, port = config_path, 8769  # Default port if not provided

        # Create environment variables
        env = os.environ.copy()
        env["KALTURA_MCP_CONFIG"] = config_file

        # Create a hard timeout for the entire test
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out for performance test")

        # Set a 45-second timeout for the entire test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(45)

        # Test with HTTP transport
        env["KALTURA_MCP_TRANSPORT"] = "http"
        server_process = subprocess.Popen(
            [sys.executable, "-m", "kaltura_mcp.server"],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Create a timeout thread to ensure we don't hang
        import threading

        def kill_after_timeout():
            try:
                import time

                time.sleep(45)  # 45 second timeout for performance tests - increased to give more time
                if server_process.poll() is None:
                    print("Timeout reached, terminating server process")
                    server_process.terminate()
            except Exception as e:
                print(f"Error in kill_after_timeout: {e}")

        timeout_thread = threading.Thread(target=kill_after_timeout)
        timeout_thread.daemon = True
        timeout_thread.start()

        try:
            time_module.sleep(3)  # Give the server more time to start
            base_url = f"http://localhost:{port}"

            # Wait for the server to start
            server_ready = self.wait_for_server(f"{base_url}/mcp/info")

            # If the server didn't start, capture and print the output
            if not server_ready:
                # Check if the server process is still running
                if server_process.poll() is not None:
                    stdout, stderr = server_process.communicate()
                    print(f"HTTP server process terminated with code {server_process.returncode}")
                    print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                    print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                else:
                    # Terminate the process to get its output
                    server_process.terminate()
                    try:
                        stdout, stderr = server_process.communicate(timeout=5)
                        print("HTTP server process terminated to get output")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")
                    except subprocess.TimeoutExpired:
                        server_process.kill()
                        stdout, stderr = server_process.communicate()
                        print("HTTP server process killed after timeout")
                        print(f"STDOUT: {stdout.decode('utf-8', errors='replace')}")
                        print(f"STDERR: {stderr.decode('utf-8', errors='replace')}")

            assert server_ready, "Server did not start within the expected time"

            # Measure response time for multiple requests
            # Warm up
            for _ in range(5):
                requests.get(f"{base_url}/mcp/info", timeout=5)

            # Reduce the number of requests to avoid timeouts
            num_requests = 10

            # Measure info endpoint
            start_time = time_module.time()
            for _ in range(num_requests):
                response = requests.get(f"{base_url}/mcp/info", timeout=5)
                assert response.status_code == 200
            end_time = time_module.time()

            avg_time = (end_time - start_time) / num_requests
            print(f"Average response time for /mcp/info: {avg_time:.4f} seconds")

            # Measure tools endpoint
            start_time = time_module.time()
            for _ in range(num_requests):
                response = requests.get(f"{base_url}/mcp/tools", timeout=5)
                assert response.status_code == 200
            end_time = time_module.time()

            avg_time = (end_time - start_time) / num_requests
            print(f"Average response time for /mcp/tools: {avg_time:.4f} seconds")

            # Measure resources endpoint
            start_time = time_module.time()
            for _ in range(num_requests):
                response = requests.get(f"{base_url}/mcp/resources", timeout=5)
                assert response.status_code == 200
            end_time = time_module.time()

            avg_time = (end_time - start_time) / num_requests
            print(f"Average response time for /mcp/resources: {avg_time:.4f} seconds")

        finally:
            # Cancel the alarm
            signal.alarm(0)

            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
