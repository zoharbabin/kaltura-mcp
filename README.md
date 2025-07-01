# Kaltura MCP Server

A Model Context Protocol (MCP) server that provides secure, read-only tools for managing Kaltura API operations. This server enables AI assistants to search, discover, and analyze Kaltura media content safely.

## Features

- **Media Discovery**: Search and browse media entries with advanced filtering
- **Content Analysis**: Access captions, transcripts, and attachment content
- **Category Management**: Browse and explore content categories  
- **Analytics**: Retrieve viewing analytics and performance metrics
- **Secure Access**: Read-only operations with comprehensive input validation
- **Session Management**: Automatic session handling with configurable expiry

## Installation

1. Clone this repository:
```bash
git clone https://github.com/zoharbabin/kaltura-mcp.git
cd kaltura-mcp
```

2. Install dependencies:
```bash
pip install -e .
```

## Usage Modes

This server supports two deployment modes:

### 🔧 Local MCP Server (Stdio Mode)
**Best for:** Personal use, direct Claude Desktop integration, development

### 🌐 Remote MCP Server (HTTP/SSE Mode)  
**Best for:** Hosted services, multiple users, production deployments

---

## Local MCP Server Setup (Claude Desktop)

### Step 1: Install Package

```bash
pip install kaltura-mcp
```

### Step 2: Setup Environment Configuration

**🔒 Secure Method (Recommended)**: Use the interactive setup script:

```bash
# Navigate to your project directory
cd /path/to/kaltura-mcp

# Run the interactive setup
python setup_env.py
```

The script will guide you through:
1. Choosing between stdio (local) or remote mode
2. Securely entering your Kaltura credentials
3. Generating a `.env` file with proper permissions (600)
4. Providing the exact Claude Desktop configuration

**📋 Manual Method**: Copy and edit the example file:

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
# - For stdio mode: Only fill in KALTURA_* variables
# - For remote mode: Fill in JWT_SECRET_KEY, OAUTH_*, and SERVER_* variables
nano .env

# Set secure permissions
chmod 600 .env
```

### Step 3: Get Your Kaltura Credentials

You'll need these credentials from your Kaltura account:

- **Service URL**: Your Kaltura server URL (usually `https://cdnapisec.kaltura.com`)
- **Partner ID**: Your numeric partner ID (found in KMC → Settings → Integration Settings)
- **Admin Secret**: Your API admin secret key (found in KMC → Settings → Integration Settings)  
- **User ID**: Your Kaltura user ID (usually your email or `admin`)

### Step 4: Configure Claude Desktop

Open your Claude Desktop configuration file:

**macOS**: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**🔒 Secure Configuration (credentials in .env file)**:

```json
{
  "mcpServers": {
    "kaltura": {
      "command": "/full/path/to/kaltura-mcp"
    }
  }
}
```

**Important Notes**: 
- Replace `/full/path/to/kaltura-mcp` with the actual path to your kaltura-mcp command (find it with `which kaltura-mcp`)
- The `.env` file is automatically loaded from the project directory by the server
- The `setup_env.py` script will automatically detect and provide the correct command path

### Step 5: Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely for the changes to take effect.

### Step 6: Test the Integration

In Claude Desktop, try asking:
- "Search for recent Kaltura videos"
- "List my Kaltura categories"
- "Find videos about [topic] in my Kaltura account"

### Troubleshooting Local Setup

**Issue**: `kaltura-mcp` command not found
- **Solution**: Make sure you installed with `pip install kaltura-mcp` and the command is in your PATH

**Issue**: "Error: Missing required environment variables"
- **Solution**: 
  1. Check that `.env` file exists in your project directory
  2. Verify file permissions: `ls -la .env` (should show `-rw-------`)
  3. Ensure all required Kaltura credentials are set in `.env` file

**Issue**: "Invalid credentials" or "Authentication failed"
- **Solution**: 
  1. Verify your credentials in Kaltura KMC → Settings → Integration Settings
  2. Check `.env` file for typos or extra spaces
  3. Run `python setup_env.py` to recreate the configuration

**Issue**: Claude Desktop doesn't show the MCP server
- **Solution**: 
  1. Check the config file syntax with a JSON validator
  2. Verify the command path is correct (use `which kaltura-mcp`)
  3. Restart Claude Desktop completely
  4. Check Claude Desktop logs for error messages

**Issue**: ".env file not found" error
- **Solution**:
  1. Run `python setup_env.py` from your project directory
  2. Ensure the `.env` file exists in the same directory as the server code
  3. Check file permissions: `ls -la .env` (should show `-rw-------`)

**✅ Security Benefits:** 
- ✅ **Secure file permissions** (600 - owner only)
- ✅ **Git-ignored by default** (won't be committed)
- ✅ **Local to project directory** (easy to manage)
- ✅ **Standard .env pattern** (familiar to developers)
- ✅ **No credentials in config files** (improved security)

---

## Remote MCP Server Setup

### Configuration

For remote/hosted deployment, additional environment variables are required:

```bash
cp .env.example .env
# Configure remote server settings
```

**Required environment variables:**
- `JWT_SECRET_KEY`: Strong secret key for JWT token signing (⚠️ **CRITICAL FOR SECURITY**)
- `OAUTH_REDIRECT_URI`: OAuth callback URL (e.g., `https://your-domain.com/oauth/callback`)
- `SERVER_HOST`: Server bind address (default: `0.0.0.0`)
- `SERVER_PORT`: Server port (default: `8000`)

**Optional environment variables:**
- `SERVER_RELOAD`: Enable auto-reload in development (default: `false`)
- `OAUTH_CLIENT_ID`: Custom OAuth client ID
- `OAUTH_CLIENT_SECRET`: Custom OAuth client secret

### Running Remote Server

```bash
# Using the installed command
kaltura-mcp-remote

# Or using Python module
python -m kaltura_mcp.remote_server
```

The remote server provides:
- **HTTP/SSE transport** for MCP protocol
- **JWT-based authentication** for secure credential management
- **Web-based authorization** flow for user-friendly setup
- **Multi-tenant support** for hosting as a service

### Available Tools

1. **get_media_entry** - Get detailed information about a specific media entry
   - Parameters: entry_id (required)

2. **list_categories** - List and search content categories
   - Parameters: search_text, limit

3. **Analytics Tools** - Comprehensive analytics suite with purpose-driven functions:
   - **get_analytics** - General analytics data for reporting and analysis
   - **get_analytics_timeseries** - Time-series data optimized for charts
   - **get_video_retention** - Detailed viewer retention analysis throughout videos
   - **get_realtime_metrics** - Live analytics updated every ~30 seconds
   - **get_quality_metrics** - Quality of Experience (QoE) and streaming performance
   - **get_geographic_breakdown** - Location-based analytics at various granularities
   - **list_analytics_capabilities** - Discover all available analytics functions
   - See [Analytics Guide](docs/KALTURA_ANALYTICS_GUIDE.md) for detailed usage

4. **get_download_url** - Get direct download URL for media files
   - Parameters: entry_id (required), flavor_id

5. **get_thumbnail_url** - Get video thumbnail/preview image URL with custom dimensions
   - Parameters: entry_id (required), width, height, second

6. **search_entries** - Search and discover media entries with intelligent sorting and filtering
   - Parameters: query (required), search_type, match_type, specific_field, boolean_operator, include_highlights, custom_metadata, date_range, max_results, sort_field, sort_order

7. **list_caption_assets** - List available captions and subtitles for a media entry
   - Parameters: entry_id (required)

8. **get_caption_content** - Get caption/subtitle content and download URL
   - Parameters: caption_asset_id (required)

9. **list_attachment_assets** - List attachment assets for a media entry
   - Parameters: entry_id (required)

10. **get_attachment_content** - Get attachment content details and download content as base64
    - Parameters: attachment_asset_id (required)

### Prompts

The server provides intelligent prompts to guide users through complex workflows:

1. **analytics_wizard** - Interactive guide for creating comprehensive analytics reports
   ```
   Arguments:
   - analysis_goal: What to analyze (e.g., "video performance", "viewer engagement", "geographic reach")
   - time_period: Time range (e.g., "today", "yesterday", "last_week", "last_month")
   ```

2. **content_discovery** - Natural language search assistant for finding media
   ```
   Arguments:
   - search_intent: What you're looking for in natural language
   - include_details: Whether to fetch captions/attachments (yes/no)
   ```

3. **accessibility_audit** - Content accessibility compliance checker
   ```
   Arguments:
   - audit_scope: What to audit ("all", "recent", "category:name", or entry_id)
   ```

4. **retention_analysis** - Create comprehensive retention analysis report
   ```
   Arguments:
   - entry_id: Video to analyze (e.g., "1_3atosphg") [required]
   - time_period: Months of data to analyze (default: "12")
   - output_format: "interactive" (HTML) or "markdown" (default: "interactive")
   ```

### Resources

The server exposes frequently-used data as cached resources:

1. **kaltura://analytics/capabilities** - Complete analytics documentation
   - All 60+ report types with descriptions
   - Available metrics and dimensions
   - Best practices for different use cases
   - Cached for 30 minutes

2. **kaltura://categories/tree** - Category hierarchy with entry counts
   - Complete category tree structure
   - Entry counts per category
   - Parent-child relationships
   - Cached for 30 minutes

3. **kaltura://media/recent/{count}** - Recent media entries
   - Replace {count} with number of entries (e.g., kaltura://media/recent/20)
   - Maximum 100 entries
   - Includes basic metadata
   - Cached for 5 minutes

---

## Remote MCP Server (Advanced)

### User Authorization Flow

1. **Server Deployment**: Deploy the remote server to your hosting environment
2. **User Authorization**: Users visit `https://your-server.com/oauth/authorize` 
3. **Credential Entry**: Users securely enter their Kaltura credentials via web form
4. **Token Generation**: Server generates a JWT token with encrypted credentials
5. **Client Configuration**: Users add the server URL and token to their MCP client

### Step-by-Step Remote Setup

#### 1. Generate Secure JWT Secret

```bash
# Generate a strong secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2. Configure Environment

```bash
# Set in your .env file or environment
JWT_SECRET_KEY=your-generated-secret-key-here
OAUTH_REDIRECT_URI=https://your-domain.com/oauth/callback
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

#### 3. Deploy Server

**Option A: Direct Python**
```bash
kaltura-mcp-remote
```

**Option B: Docker**
```bash
docker-compose up -d
```

**Option C: Production with Gunicorn (Optional)**
```bash
# Install gunicorn separately if needed for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker kaltura_mcp.remote_server:app
```

#### 4. User Onboarding

Send users to: `https://your-server.com/oauth/authorize?response_type=code&client_id=kaltura-mcp&redirect_uri=https://your-server.com/oauth/callback&state=user123`

#### 5. Client Configuration

**For Claude Desktop (Remote Mode):**

The easiest way to use the remote server with Claude Desktop is via the proxy client:

```json
{
  "mcpServers": {
    "kaltura-remote": {
      "command": "kaltura-mcp-proxy",
      "env": {
        "KALTURA_REMOTE_SERVER_URL": "https://your-server.com/mcp/messages",
        "KALTURA_REMOTE_ACCESS_TOKEN": "your-jwt-token-from-authorization-flow"
      }
    }
  }
}
```

The proxy client (`kaltura-mcp-proxy`) acts as a local stdio MCP server that forwards requests to your remote server. This provides the best compatibility with Claude Desktop.

**For Custom MCP Clients:**
```javascript
// HTTP transport with authentication
const transport = new HTTPTransport({
  baseUrl: "https://your-server.com/mcp/messages",
  headers: {
    "Authorization": "Bearer user-jwt-token-here"
  }
});
```

### Analytics Documentation

The MCP server provides a comprehensive analytics suite with purpose-driven functions optimized for different use cases:

**Purpose-Built Analytics Functions:**
- **get_analytics**: Comprehensive reporting data in table format for detailed analysis
- **get_analytics_timeseries**: Time-series data optimized for charts and visualizations
- **get_video_retention**: Detailed viewer retention curves showing exactly where viewers drop off
- **get_realtime_metrics**: Live analytics updated every ~30 seconds for monitoring
- **get_quality_metrics**: Quality of Experience (QoE) metrics for streaming performance
- **get_geographic_breakdown**: Location-based analytics at country, region, or city level

**Analytics Capabilities:**
- 60+ report types covering content, users, geography, platforms, and more
- Raw data access for custom analysis and visualization
- Intelligent insights including drop-off points and engagement patterns
- Support for filtering by date ranges, categories, users, and dimensions

For comprehensive documentation, see:
- [Analytics Guide](docs/KALTURA_ANALYTICS_GUIDE.md) - Complete reference for all analytics functions
- [Analytics Examples](examples/analytics_examples.py) - Code examples and visualizations

### Security Considerations

#### Production Deployment
- **Use HTTPS**: Always deploy with TLS/SSL certificates
- **Secure JWT Secret**: Use a cryptographically strong secret key (32+ bytes)
- **Environment Security**: Never commit secrets to version control
- **Network Security**: Use firewalls and VPN access where appropriate
- **Regular Updates**: Keep dependencies updated for security patches

#### JWT Token Security
- **Token Expiration**: Tokens expire after 24 hours by default
- **Credential Encryption**: Kaltura credentials are encrypted within JWT payload
- **Scope Limitation**: Tokens are limited to read-only Kaltura operations
- **Revocation**: Restart server to invalidate all existing tokens

#### Infrastructure
```bash
# Example nginx configuration for production
server {
    listen 443 ssl;
    server_name your-kaltura-mcp.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Deployment

**docker-compose.yml for production:**
```yaml
version: '3.8'
services:
  kaltura-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OAUTH_REDIRECT_URI=https://your-domain.com/oauth/callback
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.kaltura-mcp.rule=Host(\`your-domain.com\`)"
      - "traefik.http.routers.kaltura-mcp.tls=true"
```

### Monitoring & Logging

The remote server provides built-in logging and can be monitored via:
- **Health Check**: `GET /` returns server status
- **Metrics**: Access logs via Docker volumes or server logs
- **Error Tracking**: Configure external error tracking services

### Important Security Notes

#### Local Mode Security (Recommended)
- ✅ **Direct Configuration** - Credentials configured directly in Claude Desktop
- ✅ **MCP Standard Compliance** - Client passes credentials to server via environment variables
- ✅ **Process Isolation** - MCP server runs in isolated process with limited scope
- ✅ **No network exposure** - Direct API communication with Kaltura
- ✅ **Local credential storage** - Credentials never leave your machine
- ✅ **Secure transmission** - Credentials passed securely to MCP server process

#### Remote Mode Security  
- ✅ **Credential encryption** - Kaltura credentials encrypted in JWT tokens
- ✅ **Token expiration** - Automatic 24-hour token expiry
- ✅ **TLS encryption** - HTTPS required for production
- ⚠️ **Server trust** - You must trust the remote server operator
- ⚠️ **Credential transmission** - Credentials are sent to remote server (encrypted)

#### Production Checklist
- [ ] Use HTTPS with valid certificates
- [ ] Generate strong JWT secret key (32+ bytes)
- [ ] Configure secure environment variables
- [ ] Set up proper logging and monitoring
- [ ] Implement rate limiting (nginx/cloudflare)
- [ ] Regular security updates
- [ ] Backup and disaster recovery plan

### Deployment Architectures

#### Personal Use (Recommended)
```
Claude Desktop ←→ Local MCP Server ←→ Kaltura API
```

#### Small Team
```
Claude Desktop ←→ Proxy Client ←→ Remote MCP Server ←→ Kaltura API
```

#### Enterprise
```
Multiple Clients ←→ Load Balancer ←→ Multiple MCP Servers ←→ Kaltura API
                                          ↓
                                    Redis/Database
```

## Documentation

- [Analytics Guide](docs/KALTURA_ANALYTICS_GUIDE.md) - Comprehensive guide to analytics features
- [Prompts and Resources](docs/PROMPTS_AND_RESOURCES.md) - Detailed documentation of MCP prompts and resources
- [API Documentation](https://developer.kaltura.com/) - Official Kaltura API documentation

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT