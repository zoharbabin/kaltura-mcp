"""
Utility functions for integration tests.
"""

import socket
from typing import Optional


def find_available_port(start_port: int = 8000, end_port: int = 9000) -> Optional[int]:
    """
    Find an available port in the given range.

    Args:
        start_port: The start of the port range to search
        end_port: The end of the port range to search

    Returns:
        An available port number, or None if no ports are available
    """
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # Set a short timeout to avoid hanging
                sock.settimeout(0.1)
                # Set SO_REUSEADDR to avoid "address already in use" errors
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Try to bind to the port
                sock.bind(("localhost", port))
                # If we get here, the port is available

                # Double-check by trying to connect to the port
                check_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                check_sock.settimeout(0.1)
                try:
                    # If this succeeds, the port is actually in use
                    check_sock.connect(("localhost", port))
                    check_sock.close()
                    continue  # Port is in use, try the next one
                except (socket.error, OSError):
                    # Connection failed, which means the port is truly available
                    check_sock.close()
                    return port
            except (socket.error, OSError):
                # Port is in use, try the next one
                continue

    # No ports available
    return None
