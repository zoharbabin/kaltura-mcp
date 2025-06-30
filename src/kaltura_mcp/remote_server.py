#!/usr/bin/env python3
"""Kaltura Remote MCP Server - HTTP/SSE server with OAuth authentication."""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlencode

import jwt
import mcp.types as types
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mcp.server import Server

from .kaltura_client import KalturaClientManager
from .tools import (
    get_analytics,
    get_attachment_content,
    get_caption_content,
    get_download_url,
    get_media_entry,
    get_thumbnail_url,
    list_attachment_assets,
    list_caption_assets,
    list_categories,
    search_entries_intelligent,
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth and JWT configuration
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# FastAPI app
app = FastAPI(
    title="Kaltura Remote MCP Server",
    description="Remote Model Context Protocol server for Kaltura API with OAuth authentication",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# In-memory storage for demo (use Redis/database in production)
user_sessions: Dict[str, Dict[str, Any]] = {}
active_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids

# MCP Server instance
mcp_server = Server("kaltura-remote-mcp")


class KalturaOAuthManager:
    """Manages OAuth flow for Kaltura accounts."""

    def __init__(self):
        self.client_id = OAUTH_CLIENT_ID
        self.client_secret = OAUTH_CLIENT_SECRET
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/oauth/callback")
        self.auth_url = (
            "https://www.kaltura.com/api_v3/index.php"  # Kaltura doesn't use standard OAuth
        )

    async def get_authorization_url(self, state: str) -> str:
        """Generate authorization URL for Kaltura."""
        # Since Kaltura doesn't use standard OAuth, we'll create a custom flow
        # This redirects to our own authorization page where users enter their credentials
        params = {
            "state": state,
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        return f"/oauth/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        # In a real implementation, this would validate the code and return user credentials
        # For this demo, we'll decode the "code" which contains the user's Kaltura credentials
        try:
            # The code is base64 encoded JSON with Kaltura credentials
            import base64

            credentials_json = base64.b64decode(code).decode("utf-8")
            credentials = json.loads(credentials_json)

            # Validate credentials by attempting to create a session
            kaltura_manager = KalturaClientManager()
            await kaltura_manager.initialize(
                service_url=credentials.get("service_url", "https://www.kaltura.com"),
                partner_id=credentials["partner_id"],
                admin_secret=credentials["admin_secret"],
                user_id=credentials.get("user_id", "admin"),
            )

            return {
                "access_token": self.create_access_token(credentials),
                "token_type": "bearer",
                "expires_in": JWT_EXPIRATION_HOURS * 3600,
                "kaltura_credentials": credentials,
            }
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise HTTPException(status_code=400, detail="Invalid authorization code")

    def create_access_token(self, kaltura_credentials: Dict[str, Any]) -> str:
        """Create JWT access token with Kaltura credentials."""
        payload = {
            "sub": f"kaltura_{kaltura_credentials['partner_id']}_{kaltura_credentials.get('user_id', 'admin')}",
            "kaltura_credentials": kaltura_credentials,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
            "iss": "kaltura-mcp-server",
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


oauth_manager = KalturaOAuthManager()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = oauth_manager.verify_token(token)
    return payload


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Kaltura Remote MCP Server",
        "version": "0.1.0",
        "description": "Remote Model Context Protocol server for Kaltura API",
        "endpoints": {
            "oauth_authorize": "/oauth/authorize",
            "oauth_callback": "/oauth/callback",
            "mcp_messages": "/mcp/messages",
            "mcp_sse": "/mcp/sse/{connection_id}",
        },
    }


@app.get("/oauth/authorize")
async def oauth_authorize(
    response_type: str, client_id: str, redirect_uri: str, state: str, scope: Optional[str] = None
):
    """OAuth authorization endpoint - presents credential entry form."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kaltura MCP Authorization</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin: 15px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{ width: 100%; padding: 8px; box-sizing: border-box; }}
            button {{ background-color: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
            button:hover {{ background-color: #005a87; }}
            .help {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <h1>Authorize Kaltura MCP Access</h1>
        <p>Please enter your Kaltura API credentials to allow secure access to your Kaltura account.</p>

        <form id="authForm">
            <div class="form-group">
                <label for="service_url">Kaltura Service URL:</label>
                <input type="url" id="service_url" name="service_url" value="https://www.kaltura.com" required>
                <div class="help">Your Kaltura server URL (usually https://www.kaltura.com)</div>
            </div>

            <div class="form-group">
                <label for="partner_id">Partner ID:</label>
                <input type="number" id="partner_id" name="partner_id" required>
                <div class="help">Your Kaltura partner ID (numeric)</div>
            </div>

            <div class="form-group">
                <label for="admin_secret">Admin Secret:</label>
                <input type="password" id="admin_secret" name="admin_secret" required>
                <div class="help">Your Kaltura admin secret key</div>
            </div>

            <div class="form-group">
                <label for="user_id">User ID:</label>
                <input type="text" id="user_id" name="user_id" value="admin">
                <div class="help">Your Kaltura user ID (optional, defaults to 'admin')</div>
            </div>

            <button type="submit">Authorize Access</button>
        </form>

        <script>
            document.getElementById('authForm').addEventListener('submit', async function(e) {{
                e.preventDefault();

                const credentials = {{
                    service_url: document.getElementById('service_url').value,
                    partner_id: parseInt(document.getElementById('partner_id').value),
                    admin_secret: document.getElementById('admin_secret').value,
                    user_id: document.getElementById('user_id').value || 'admin'
                }};

                // Encode credentials as base64 JSON for the "code"
                const code = btoa(JSON.stringify(credentials));

                // Redirect to callback with the code
                const callbackUrl = new URL('{redirect_uri}');
                callbackUrl.searchParams.set('code', code);
                callbackUrl.searchParams.set('state', '{state}');

                window.location.href = callbackUrl.toString();
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    """OAuth callback endpoint."""
    try:
        token_data = await oauth_manager.exchange_code_for_token(code, state)

        # Store user session
        user_id = jwt.decode(
            token_data["access_token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )["sub"]
        user_sessions[user_id] = {
            "access_token": token_data["access_token"],
            "kaltura_credentials": token_data["kaltura_credentials"],
            "created_at": datetime.utcnow().isoformat(),
        }

        # Generate the MCP endpoint URL from the redirect URI
        mcp_url = oauth_manager.redirect_uri.replace("/oauth/callback", "/mcp/messages")

        # Return success page with token
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; }}
                .token {{ background-color: #f8f9fa; padding: 10px; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✅ Authorization Successful!</h1>
                <p>Your Kaltura account has been successfully connected to the MCP server.</p>

                <h3>Your Access Token:</h3>
                <div class="token">{token_data["access_token"]}</div>

                <h3>Usage Instructions:</h3>
                <p>For Claude Desktop, use the proxy client configuration:</p>
                <pre>
{{
  "mcpServers": {{
    "kaltura-remote": {{
      "command": "kaltura-mcp-proxy",
      "env": {{
        "KALTURA_REMOTE_SERVER_URL": "{mcp_url}",
        "KALTURA_REMOTE_ACCESS_TOKEN": "{token_data["access_token"]}"
      }}
    }}
  }}
}}
                </pre>
                <p><strong>Note:</strong> Save your token securely. It expires in 24 hours.</p>
                <p><strong>Server URL:</strong> {mcp_url}</p>
                <p><strong>Installation:</strong> Run <code>pip install kaltura-mcp</code> to get the proxy client.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/mcp/messages")
async def handle_mcp_message(request: Request, user: Dict[str, Any] = Depends(get_current_user)):
    """Handle MCP JSON-RPC messages via HTTP POST."""
    try:
        # Validate MCP headers according to specification
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(status_code=400, detail="Content-Type must be application/json")

        # Parse the JSON-RPC message
        message = await request.json()
        logger.info(
            f"Received MCP message from user {user['sub']}: {message.get('method', 'unknown')}"
        )

        # Initialize Kaltura client for this user
        kaltura_manager = KalturaClientManager()
        credentials = user["kaltura_credentials"]
        await kaltura_manager.initialize(
            service_url=credentials.get("service_url", "https://www.kaltura.com"),
            partner_id=credentials["partner_id"],
            admin_secret=credentials["admin_secret"],
            user_id=credentials.get("user_id", "admin"),
        )

        # Process MCP message
        response = await process_mcp_message(message, kaltura_manager)

        # Add CORS headers for browser compatibility
        return response

    except Exception as e:
        logger.error(f"Error handling MCP message: {e}")
        return {
            "jsonrpc": "2.0",
            "id": message.get("id") if "message" in locals() else None,
            "error": {"code": -32603, "message": "Internal error", "data": str(e)},
        }


@app.get("/mcp/sse/{connection_id}")
async def mcp_sse_endpoint(connection_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Server-Sent Events endpoint for MCP streaming."""
    user_id = user["sub"]

    async def event_stream():
        # Add connection to active connections
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(connection_id)

        try:
            # Send initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id})}\\n\\n"

            # Keep connection alive and listen for messages
            while True:
                # In a real implementation, you'd listen for messages from a queue/pubsub
                # For now, just send periodic keepalive
                await asyncio.sleep(30)
                yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': datetime.utcnow().isoformat()})}\\n\\n"

        except asyncio.CancelledError:
            pass
        finally:
            # Clean up connection
            if user_id in active_connections:
                active_connections[user_id].discard(connection_id)
                if not active_connections[user_id]:
                    del active_connections[user_id]

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


async def process_mcp_message(
    message: Dict[str, Any], kaltura_manager: KalturaClientManager
) -> Dict[str, Any]:
    """Process incoming MCP JSON-RPC message."""
    method = message.get("method")
    params = message.get("params", {})
    msg_id = message.get("id")

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "kaltura-remote-mcp", "version": "0.1.0"},
                },
            }

        elif method == "tools/list":
            tools = await get_available_tools()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": [tool.model_dump() for tool in tools]},
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            result = await call_tool(tool_name, arguments, kaltura_manager)
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": result}}

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    except Exception as e:
        logger.error(f"Error processing MCP message: {e}")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32603, "message": "Internal error", "data": str(e)},
        }


async def get_available_tools() -> List[types.Tool]:
    """Get list of available MCP tools."""
    return [
        types.Tool(
            name="get_media_entry",
            description="Get detailed information about a specific media entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "The Kaltura media entry ID"},
                },
                "required": ["entry_id"],
            },
        ),
        types.Tool(
            name="list_categories",
            description="List and search content categories",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "Filter categories by name or description",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of categories to return (default: 20)",
                    },
                },
            },
        ),
        types.Tool(
            name="get_analytics",
            description="Get viewing analytics and performance metrics for media entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "string",
                        "description": "Optional media entry ID for specific entry analytics",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date for analytics (YYYY-MM-DD format)",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date for analytics (YYYY-MM-DD format)",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["plays", "views", "engagement", "drop_off"],
                        },
                        "description": "Metrics to retrieve: plays, views, engagement, drop_off",
                    },
                },
                "required": ["from_date", "to_date"],
            },
        ),
        types.Tool(
            name="search_entries",
            description="Search and discover media entries with intelligent sorting and filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "search_type": {
                        "type": "string",
                        "enum": ["unified", "entry", "caption", "metadata", "cuepoint"],
                        "description": "Search scope",
                    },
                    "max_results": {"type": "integer", "description": "Maximum number of results"},
                    "sort_field": {"type": "string", "description": "Field to sort by"},
                    "sort_order": {
                        "type": "string",
                        "enum": ["desc", "asc"],
                        "description": "Sort direction",
                    },
                },
                "required": ["query"],
            },
        ),
        # Add other tools...
    ]


async def call_tool(
    tool_name: str, arguments: Dict[str, Any], kaltura_manager: KalturaClientManager
) -> List[types.TextContent]:
    """Execute a tool call."""
    try:
        if tool_name == "get_media_entry":
            result = await get_media_entry(kaltura_manager, **arguments)
        elif tool_name == "list_categories":
            result = await list_categories(kaltura_manager, **arguments)
        elif tool_name == "get_analytics":
            result = await get_analytics(kaltura_manager, **arguments)
        elif tool_name == "get_download_url":
            result = await get_download_url(kaltura_manager, **arguments)
        elif tool_name == "get_thumbnail_url":
            result = await get_thumbnail_url(kaltura_manager, **arguments)
        elif tool_name == "search_entries":
            result = await search_entries_intelligent(kaltura_manager, **arguments)
        elif tool_name == "list_caption_assets":
            result = await list_caption_assets(kaltura_manager, **arguments)
        elif tool_name == "get_caption_content":
            result = await get_caption_content(kaltura_manager, **arguments)
        elif tool_name == "list_attachment_assets":
            result = await list_attachment_assets(kaltura_manager, **arguments)
        elif tool_name == "get_attachment_content":
            result = await get_attachment_content(kaltura_manager, **arguments)
        else:
            result = f"Unknown tool: {tool_name}"

        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return [types.TextContent(type="text", text=f"Error executing {tool_name}: {str(e)}")]


def main():
    """Main entry point for the remote MCP server."""
    import uvicorn

    # Validate required environment variables
    required_vars = ["JWT_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and configure the remote server settings.")
        exit(1)

    # Get server configuration from environment
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "false").lower() == "true"

    logger.info(f"Starting Kaltura Remote MCP Server on {host}:{port}")
    logger.info(f"Authorization URL: http://{host}:{port}/oauth/authorize")

    # Run the FastAPI server
    uvicorn.run(
        "kaltura_mcp.remote_server:app", host=host, port=port, reload=reload, log_level="info"
    )


if __name__ == "__main__":
    main()
