"""Shared utilities for all Kaltura MCP tools."""

import json
import logging
import os
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


def safe_serialize_kaltura_field(field):
    """Safely serialize Kaltura enum/object fields to JSON-compatible values."""
    if field is None:
        return None
    if hasattr(field, "value"):
        return field.value
    return str(field)


def handle_kaltura_error(e: Exception, operation: str, context: Dict[str, Any] = None) -> str:
    """Centralized error handling for Kaltura API operations."""
    import traceback

    error_context = context or {}
    error_type = type(e).__name__

    # Log the error for debugging
    logger.error(f"Kaltura API error in {operation}: {str(e)}", exc_info=True)

    # Create detailed error response
    error_response = {
        "error": f"Failed to {operation}: {str(e)}",
        "errorType": error_type,
        "operation": operation,
        **error_context,
    }

    # Log detailed error for debugging (not exposed to user)
    if os.getenv("KALTURA_DEBUG") == "true":
        logger.debug(f"Detailed traceback for {operation}: {traceback.format_exc()}")

    return json.dumps(error_response, indent=2)


def validate_entry_id(entry_id: str) -> bool:
    """Validate Kaltura entry ID format with proper security checks."""
    if not entry_id or not isinstance(entry_id, str):
        return False

    # Sanitize input - remove any potentially dangerous characters
    if not re.match(r"^[0-9]+_[a-zA-Z0-9]+$", entry_id):
        return False

    # Check length constraints (Kaltura IDs are typically 10-20 chars)
    if len(entry_id) < 3 or len(entry_id) > 50:
        return False

    return True
