#!/usr/bin/env python3
"""Interactive script to help setup .env file for Kaltura MCP Server."""

import os
import stat
import getpass
import secrets
from pathlib import Path


def main():
    print("🔐 Kaltura MCP Server - Environment Setup")
    print("=========================================")
    print()
    
    print("Which mode do you want to configure?")
    print("1. Stdio Mode (Local) - Direct Claude Desktop integration")
    print("2. Remote Mode (HTTP/SSE) - Hosted server with OAuth")
    print()
    
    while True:
        choice = input("Choose mode (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == '1':
        setup_stdio_mode()
    else:
        setup_remote_mode()


def setup_stdio_mode():
    """Setup .env file for stdio (local) mode."""
    print("\n📱 Stdio Mode Setup")
    print("==================")
    print("This mode runs locally and connects directly to Claude Desktop.")
    print()
    
    env_file = Path('.env')
    
    if env_file.exists():
        response = input(f".env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("Please enter your Kaltura credentials:")
    print("(Find these in Kaltura KMC → Settings → Integration Settings)")
    print()
    
    # Get credentials
    service_url = input("Service URL [https://cdnapisec.kaltura.com]: ").strip()
    if not service_url:
        service_url = "https://cdnapisec.kaltura.com"
    
    partner_id = input("Partner ID: ").strip()
    admin_secret = getpass.getpass("Admin Secret (hidden): ").strip()
    user_id = input("User ID (usually your email): ").strip()
    session_expiry = input("Session expiry in seconds [86400]: ").strip()
    if not session_expiry:
        session_expiry = "86400"
    
    # Validate input
    if not all([partner_id, admin_secret, user_id]):
        print("❌ All fields are required!")
        return
    
    if not partner_id.isdigit():
        print("❌ Partner ID must be a number!")
        return
    
    # Create .env content
    env_content = f"""# Kaltura MCP Server Configuration - Stdio Mode (Local)
# This file contains sensitive credentials - keep it secure!

KALTURA_SERVICE_URL={service_url}
KALTURA_PARTNER_ID={partner_id}
KALTURA_ADMIN_SECRET={admin_secret}
KALTURA_USER_ID={user_id}
KALTURA_SESSION_EXPIRY={session_expiry}
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Set secure permissions (600 - owner read/write only)
    env_file.chmod(0o600)
    
    print()
    print("✅ Environment file created successfully!")
    print(f"📁 Location: {env_file.absolute()}")
    print(f"🔒 Permissions: {oct(env_file.stat().st_mode)[-3:]}")
    print()
    # Find the kaltura-mcp command path
    import shutil
    kaltura_mcp_path = shutil.which('kaltura-mcp')
    if not kaltura_mcp_path:
        kaltura_mcp_path = "kaltura-mcp"  # fallback
    
    print("📋 Claude Desktop Configuration:")
    print("Copy this configuration to your Claude Desktop config file:")
    print()
    print('   {')
    print('     "mcpServers": {')
    print('       "kaltura": {')
    print(f'         "command": "{kaltura_mcp_path}"')
    print('       }')
    print('     }')
    print('   }')
    print()
    print("📍 Config file locations:")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print()
    print("🔄 Next steps:")
    print("1. Update your Claude Desktop configuration (see above)")
    print("2. Restart Claude Desktop")
    print("3. Test with: 'Search for recent Kaltura videos'")


def setup_remote_mode():
    """Setup .env file for remote (HTTP/SSE) mode."""
    print("\n🌐 Remote Mode Setup")
    print("===================")
    print("This mode runs as a hosted server with OAuth authentication.")
    print()
    
    env_file = Path('.env')
    
    if env_file.exists():
        response = input(f".env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("Please enter your remote server configuration:")
    print()
    
    # Generate JWT secret
    print("🔑 Generating secure JWT secret key...")
    jwt_secret = secrets.token_urlsafe(32)
    print(f"   Generated: {jwt_secret}")
    print()
    
    # Get server configuration
    redirect_uri = input("OAuth Redirect URI (e.g., https://your-domain.com/oauth/callback): ").strip()
    server_host = input("Server Host [0.0.0.0]: ").strip()
    if not server_host:
        server_host = "0.0.0.0"
    
    server_port = input("Server Port [8000]: ").strip()
    if not server_port:
        server_port = "8000"
    
    server_reload = input("Enable auto-reload for development? (y/N): ").strip().lower()
    server_reload = "true" if server_reload == 'y' else "false"
    
    # Optional OAuth configuration
    print()
    print("Optional OAuth configuration (leave blank for defaults):")
    oauth_client_id = input("OAuth Client ID [kaltura-mcp]: ").strip()
    if not oauth_client_id:
        oauth_client_id = "kaltura-mcp"
    
    oauth_client_secret = input("OAuth Client Secret (leave blank to generate): ").strip()
    if not oauth_client_secret:
        oauth_client_secret = secrets.token_urlsafe(24)
        print(f"   Generated: {oauth_client_secret}")
    
    # Validate input
    if not redirect_uri:
        print("❌ OAuth Redirect URI is required!")
        return
    
    if not server_port.isdigit():
        print("❌ Server port must be a number!")
        return
    
    # Create .env content
    env_content = f"""# Kaltura MCP Server Configuration - Remote Mode (HTTP/SSE)
# This file contains sensitive credentials - keep it secure!

# Required: Remote server configuration
JWT_SECRET_KEY={jwt_secret}
OAUTH_REDIRECT_URI={redirect_uri}

# Server configuration
SERVER_HOST={server_host}
SERVER_PORT={server_port}
SERVER_RELOAD={server_reload}

# OAuth configuration
OAUTH_CLIENT_ID={oauth_client_id}
OAUTH_CLIENT_SECRET={oauth_client_secret}

# Note: Kaltura credentials are provided by users via OAuth flow
# The following are only needed for testing/development:
# KALTURA_SERVICE_URL=https://cdnapisec.kaltura.com
# KALTURA_PARTNER_ID=your_partner_id_here
# KALTURA_ADMIN_SECRET=your_admin_secret_here
# KALTURA_USER_ID=your_email@domain.com
"""
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Set secure permissions (600 - owner read/write only)
    env_file.chmod(0o600)
    
    print()
    print("✅ Environment file created successfully!")
    print(f"📁 Location: {env_file.absolute()}")
    print(f"🔒 Permissions: {oct(env_file.stat().st_mode)[-3:]}")
    print()
    print("🚀 Starting the server:")
    print("   kaltura-mcp-remote")
    print()
    print("🔗 User authorization URL:")
    print(f"   {redirect_uri.replace('/oauth/callback', '/oauth/authorize')}?response_type=code&client_id={oauth_client_id}&redirect_uri={redirect_uri}&state=user123")
    print()
    print("📋 Claude Desktop Configuration (using proxy):")
    print("After users complete OAuth flow, they can use:")
    print()
    print('   {')
    print('     "mcpServers": {')
    print('       "kaltura-remote": {')
    print('         "command": "kaltura-mcp-proxy",')
    print('         "env": {')
    print(f'           "KALTURA_REMOTE_SERVER_URL": "{redirect_uri.replace("/oauth/callback", "/mcp/messages")}",')
    print('           "KALTURA_REMOTE_ACCESS_TOKEN": "user-jwt-token-from-authorization-flow"')
    print('         }')
    print('       }')
    print('     }')
    print('   }')
    print()
    print("🔄 Next steps:")
    print("1. Start the server: kaltura-mcp-remote")
    print("2. Deploy to your hosting environment")
    print("3. Set up HTTPS with proper certificates")
    print("4. Send users to the authorization URL")


if __name__ == "__main__":
    main()