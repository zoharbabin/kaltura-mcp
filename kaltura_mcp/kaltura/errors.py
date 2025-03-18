"""
Error handling for Kaltura API integration.
"""
from KalturaClient.exceptions import KalturaException, KalturaClientException
from enum import Enum, auto

# Define our own error codes since they're not available in mcp.types
class ErrorCode(Enum):
    """Error codes for MCP errors."""
    InvalidRequest = auto()
    InvalidParams = auto()
    MethodNotFound = auto()
    InternalError = auto()
    Unauthorized = auto()
    Forbidden = auto()
    NotFound = auto()

class McpError(Exception):
    """MCP error class."""
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)

def translate_kaltura_error(error):
    """Translate Kaltura errors to MCP errors."""
    if isinstance(error, KalturaClientException):
        return McpError(
            ErrorCode.InternalError,
            f"Kaltura client error: {error.message}"
        )
    
    if isinstance(error, KalturaException):
        # Map Kaltura error codes to MCP error codes
        if error.code in (
            "INVALID_KS",
            "INVALID_SESSION",
            "EXPIRED_SESSION",
        ):
            return McpError(
                ErrorCode.Unauthorized,
                f"Authentication error: {error.message}"
            )
        
        if error.code in (
            "INVALID_PARTNER_ID",
            "PARTNER_NOT_FOUND",
        ):
            return McpError(
                ErrorCode.Unauthorized,
                f"Partner authentication error: {error.message}"
            )
        
        if error.code in (
            "MISSING_PARAMETER",
            "INVALID_PARAMETER",
        ):
            return McpError(
                ErrorCode.InvalidParams,
                f"Parameter error: {error.message}"
            )
        
        if error.code in (
            "ENTRY_ID_NOT_FOUND",
            "CATEGORY_NOT_FOUND",
            "USER_NOT_FOUND",
        ):
            return McpError(
                ErrorCode.NotFound,
                f"Resource not found: {error.message}"
            )
        
        if error.code in (
            "PERMISSION_DENIED",
            "ACCESS_CONTROL_RESTRICTED",
        ):
            return McpError(
                ErrorCode.Forbidden,
                f"Permission denied: {error.message}"
            )
        
        # Default error mapping
        return McpError(
            ErrorCode.InternalError,
            f"Kaltura API error ({error.code}): {error.message}"
        )
    
    # Unknown error type
    return McpError(
        ErrorCode.InternalError,
        f"Unknown error: {str(error)}"
    )