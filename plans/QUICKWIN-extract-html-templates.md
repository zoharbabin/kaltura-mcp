# Extract HTML Templates - QUICKWIN (15 minutes)

**Complexity**: Very Low  
**Impact**: High - Improves code maintainability  
**Time Estimate**: 15 minutes  
**Dependencies**: None

## Problem
HTML content is embedded directly in Python code in `remote_server.py`, making it hard to maintain, edit, and version.

## Solution
Move HTML content to separate template files and use file-based template loading.

## Implementation Steps

### 1. Create Templates Directory (2 minutes)
```bash
mkdir -p src/kaltura_mcp/templates
```

### 2. Create OAuth Form Template (5 minutes)
```bash
touch src/kaltura_mcp/templates/oauth_form.html
```

**File: `src/kaltura_mcp/templates/oauth_form.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Kaltura MCP Authorization</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
            max-width: 400px; 
            margin: 50px auto; 
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        .form-group { 
            margin-bottom: 15px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: 500;
            color: #555;
        }
        input { 
            width: 100%; 
            padding: 8px 12px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            font-size: 14px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #0066cc;
            box-shadow: 0 0 0 2px rgba(0,102,204,0.2);
        }
        button { 
            background: #0066cc; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 4px; 
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover { 
            background: #0052a3; 
        }
        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Kaltura MCP Authorization</h1>
        <p>Please enter your Kaltura credentials to generate an access token.</p>
        
        <form method="POST" action="/oauth/token">
            <div class="form-group">
                <label for="service_url">Service URL:</label>
                <input type="url" id="service_url" name="service_url" 
                       value="https://cdnapisec.kaltura.com" required>
                <div class="help-text">Usually https://cdnapisec.kaltura.com or your custom URL</div>
            </div>
            
            <div class="form-group">
                <label for="partner_id">Partner ID:</label>
                <input type="text" id="partner_id" name="partner_id" required>
                <div class="help-text">Found in KMC → Settings → Integration Settings</div>
            </div>
            
            <div class="form-group">
                <label for="admin_secret">Admin Secret:</label>
                <input type="password" id="admin_secret" name="admin_secret" required>
                <div class="help-text">Found in KMC → Settings → Integration Settings</div>
            </div>
            
            <div class="form-group">
                <label for="user_id">User ID:</label>
                <input type="text" id="user_id" name="user_id" required>
                <div class="help-text">Usually your email or 'admin'</div>
            </div>
            
            <button type="submit">Generate Access Token</button>
        </form>
    </div>
</body>
</html>
```

### 3. Create Success Template (3 minutes)
```bash
touch src/kaltura_mcp/templates/oauth_success.html
```

**File: `src/kaltura_mcp/templates/oauth_success.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Authorization Success - Kaltura MCP</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
            max-width: 600px; 
            margin: 50px auto; 
            padding: 20px;
            background: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #28a745;
            margin-bottom: 20px;
            text-align: center;
        }
        .success-icon {
            text-align: center;
            font-size: 48px;
            color: #28a745;
            margin-bottom: 20px;
        }
        .token-container {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #28a745;
            margin: 20px 0;
        }
        .token {
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            background: white;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .config-example {
            background: #f1f3f4;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .config-example pre {
            margin: 0;
            font-size: 12px;
            overflow-x: auto;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .copy-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 10px;
        }
        .copy-button:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Authorization Successful!</h1>
        
        <p>Your access token has been generated successfully. Use this token to configure your MCP client.</p>
        
        <div class="token-container">
            <strong>Access Token:</strong>
            <div class="token" id="token">{{ACCESS_TOKEN}}</div>
            <button class="copy-button" onclick="copyToken()">Copy Token</button>
        </div>
        
        <div class="warning">
            <strong>⚠️ Security Notice:</strong> Keep this token secure and do not share it. The token expires in 24 hours.
        </div>
        
        <h3>Claude Desktop Configuration</h3>
        <p>Add this configuration to your Claude Desktop config file:</p>
        
        <div class="config-example">
            <pre id="config">{
  "mcpServers": {
    "kaltura-remote": {
      "command": "kaltura-mcp-proxy",
      "env": {
        "KALTURA_REMOTE_SERVER_URL": "{{SERVER_URL}}/mcp/messages",
        "KALTURA_REMOTE_ACCESS_TOKEN": "{{ACCESS_TOKEN}}"
      }
    }
  }
}</pre>
            <button class="copy-button" onclick="copyConfig()">Copy Configuration</button>
        </div>
        
        <p><strong>Config file location:</strong></p>
        <ul>
            <li><strong>macOS:</strong> <code>~/Library/Application Support/Claude/claude_desktop_config.json</code></li>
            <li><strong>Windows:</strong> <code>%APPDATA%\Claude\claude_desktop_config.json</code></li>
        </ul>
        
        <p>After updating the configuration, restart Claude Desktop to apply the changes.</p>
    </div>
    
    <script>
        function copyToken() {
            const token = document.getElementById('token').textContent;
            navigator.clipboard.writeText(token).then(() => {
                alert('Token copied to clipboard!');
            });
        }
        
        function copyConfig() {
            const config = document.getElementById('config').textContent;
            navigator.clipboard.writeText(config).then(() => {
                alert('Configuration copied to clipboard!');
            });
        }
    </script>
</body>
</html>
```

### 4. Update remote_server.py (5 minutes)
**File: `src/kaltura_mcp/remote_server.py`**

Add imports at the top:
```python
from pathlib import Path
from fastapi.responses import HTMLResponse
```

Add after the FastAPI app creation:
```python
# Templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"

def load_template(template_name: str, **kwargs) -> str:
    """Load and render a template with variables."""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    
    content = template_path.read_text(encoding='utf-8')
    
    # Simple template variable replacement
    for key, value in kwargs.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    
    return content
```

Replace the `oauth_authorize` function:
```python
@app.get("/oauth/authorize")
async def oauth_authorize():
    """Display OAuth authorization form."""
    html_content = load_template("oauth_form.html")
    return HTMLResponse(content=html_content)
```

Replace the success response in `oauth_token` function:
```python
# In the oauth_token function, replace the HTML response with:
html_content = load_template(
    "oauth_success.html",
    ACCESS_TOKEN=token,
    SERVER_URL=request.url.replace(path="/oauth/callback")
)
return HTMLResponse(content=html_content)
```

## Testing
1. Start the remote server: `kaltura-mcp-remote`
2. Visit `http://localhost:8000/oauth/authorize`
3. Verify the form displays correctly
4. Test the authorization flow

## Benefits
- ✅ Cleaner Python code
- ✅ Easier to maintain HTML
- ✅ Better separation of concerns
- ✅ Easier to customize styling
- ✅ Version control for templates

## Files Modified
- `src/kaltura_mcp/remote_server.py`

## Files Created
- `src/kaltura_mcp/templates/oauth_form.html`
- `src/kaltura_mcp/templates/oauth_success.html`