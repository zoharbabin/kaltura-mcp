# Elegant Modular Tools - FINAL PLAN (2 hours)

**Complexity**: Clean & Simple  
**Impact**: High - Perfect balance of organization, simplicity, and extensibility  
**Priority**: HIGH (enables better maintainability and future growth)  
**Time Estimate**: 2 hours  
**Dependencies**: None

## Problem Analysis

The current `tools.py` file (1414 lines, 18 functions) works perfectly but needs reorganization for:
- Better navigation and maintenance
- Clear domain separation
- Future extensibility  
- Team collaboration

**Current Function Breakdown by Domain:**
- **3 utility functions**: `safe_serialize_kaltura_field`, `handle_kaltura_error`, `validate_entry_id`
- **4 core media functions**: `list_media_entries`, `get_media_entry`, `get_download_url`, `get_thumbnail_url`
- **1 analytics function**: `get_analytics` (163 lines - substantial domain)
- **6 search functions**: `search_entries`, `esearch_entries`, `search_entries_intelligent`, `list_categories`, `_get_*` helpers
- **4 asset functions**: `list_caption_assets`, `get_caption_content`, `list_attachment_assets`, `get_attachment_content`

## Elegant Solution

Create **5 focused modules** with **zero breaking changes**:

- **`tools/utils.py`** - Shared utilities (3 functions, ~80 lines)
- **`tools/media.py`** - Core media operations (4 functions, ~400 lines)
- **`tools/analytics.py`** - Analytics and reporting (1 function, ~200 lines)
- **`tools/search.py`** - Search & discovery (6 functions + helpers, ~600 lines)  
- **`tools/assets.py`** - Assets & supplementary content (4 functions, ~300 lines)

## Design Principles

✅ **Zero Breaking Changes**: Same API, same imports, same tests pass  
✅ **Domain-Driven**: Each module owns a clear business domain  
✅ **Future-Ready**: Room for natural growth in each domain  
✅ **Clean Dependencies**: Minimal coupling, clear import patterns  
✅ **Copy-Paste Migration**: Move functions exactly as-is  
✅ **Maintainable**: Related functionality together, easy to find and modify  

## Implementation Steps

### 1. Create Shared Utilities Module (15 minutes)
**File: `src/kaltura_mcp/tools/utils.py`**
```python
"""Shared utilities for all Kaltura MCP tools."""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def safe_serialize_kaltura_field(field):
    """Safely serialize Kaltura enum/object fields to JSON-compatible values."""
    # Copy exactly from tools.py lines 66-72


def handle_kaltura_error(e: Exception, operation: str, context: Dict[str, Any] = None) -> str:
    """Centralized error handling for Kaltura API operations."""
    # Copy exactly from tools.py lines 75-97


def validate_entry_id(entry_id: str) -> bool:
    """Validate Kaltura entry ID format with proper security checks."""
    # Copy exactly from tools.py lines 100-113
```

### 2. Create Core Media Module (25 minutes)
**File: `src/kaltura_mcp/tools/media.py`**
```python
"""Core media entry operations - the heart of Kaltura management."""

from typing import Any, Dict, Optional

from KalturaClient.Plugins.Core import (
    KalturaAssetFilter,
    KalturaFilterPager,
    KalturaMediaEntry,
    KalturaMediaEntryFilter,
    KalturaMediaListResponse,
    KalturaMediaType,
)

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field, validate_entry_id


async def list_media_entries(
    manager: KalturaClientManager,
    search_text: Optional[str] = None,
    media_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """List media entries with optional filtering."""
    # Copy exactly from tools.py lines 116-176


async def get_media_entry(manager: KalturaClientManager, entry_id: str) -> str:
    """Get detailed information about a specific media entry."""
    # Copy exactly from tools.py lines 179-221


async def get_download_url(
    manager: KalturaClientManager, entry_id: str, flavor_id: Optional[str] = None
) -> str:
    """Get direct download URL for media files."""
    # Copy exactly from tools.py lines 502-563


async def get_thumbnail_url(
    manager: KalturaClientManager,
    entry_id: str,
    width: int = 120,
    height: int = 90,
    second: int = 5,
) -> str:
    """Get video thumbnail/preview image URL with custom dimensions."""
    # Copy exactly from tools.py lines 565-631
```

### 3. Create Analytics Module (20 minutes)
**File: `src/kaltura_mcp/tools/analytics.py`**
```python
"""Analytics and reporting operations - insights and performance data."""

from typing import List, Optional

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, validate_entry_id


async def get_analytics(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    entry_id: Optional[str] = None,
    report_type: str = "content",
    categories: Optional[str] = None,
    limit: int = 20,
    metrics: Optional[List[str]] = None,
) -> str:
    """Get comprehensive analytics using Kaltura Report API."""
    # Copy exactly from tools.py lines 269-430
```

### 4. Create Search Module (35 minutes)
**File: `src/kaltura_mcp/tools/search.py`**
```python
"""Search and discovery operations - find and organize content."""

from typing import Any, Dict, List, Optional

from KalturaClient.Plugins.Core import KalturaCategoryFilter, KalturaFilterPager
from KalturaClient.Plugins.ElasticSearch import (
    KalturaESearchCaptionFieldName,
    KalturaESearchCaptionItem,
    KalturaESearchCuePointFieldName,
    KalturaESearchCuePointItem,
    KalturaESearchEntryFieldName,
    KalturaESearchEntryItem,
    KalturaESearchEntryMetadataItem,
    KalturaESearchEntryOperator,
    KalturaESearchEntryOrderByFieldName,
    KalturaESearchEntryOrderByItem,
    KalturaESearchEntryParams,
    KalturaESearchItemType,
    KalturaESearchOperatorType,
    KalturaESearchOrderBy,
    KalturaESearchRange,
    KalturaESearchSortOrder,
    KalturaESearchUnifiedItem,
)

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field, validate_entry_id


async def list_categories(
    manager: KalturaClientManager, search_text: Optional[str] = None, limit: int = 20
) -> str:
    """List and search content categories."""
    # Copy exactly from tools.py lines 223-267


async def search_entries(
    manager: KalturaClientManager,
    query: str,
    search_type: str = "basic",
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "createdAt",
    sort_order: str = "desc",
) -> str:
    """Search media entries using basic search."""
    # Copy exactly from tools.py lines 432-500


async def esearch_entries(
    manager: KalturaClientManager,
    search_params: Dict[str, Any],
    pager: Optional[Dict[str, int]] = None,
) -> str:
    """Advanced eSearch for media entries."""
    # Copy exactly from tools.py lines 633-852


async def search_entries_intelligent(
    manager: KalturaClientManager,
    query: str,
    search_type: str = "unified",
    match_type: str = "partial",
    specific_field: Optional[str] = None,
    boolean_operator: str = "and",
    include_highlights: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
    date_range: Optional[Dict[str, str]] = None,
    max_results: int = 20,
    sort_field: str = "created_at",
    sort_order: str = "desc",
) -> str:
    """Search and discover media entries with intelligent sorting and filtering."""
    # Copy exactly from tools.py lines 936-1081


# Helper functions - copy exactly as-is
def _get_item_type(item_type: str):
    # Copy exactly from tools.py lines 854-864

def _get_entry_field_name(field_name: str):
    # Copy exactly from tools.py lines 866-877

def _get_caption_field_name(field_name: str):
    # Copy exactly from tools.py lines 879-888

def _get_cuepoint_field_name(field_name: str):
    # Copy exactly from tools.py lines 890-899

def _get_operator_type(operator_type: str):
    # Copy exactly from tools.py lines 901-909

def _get_sort_field(field_name: str):
    # Copy exactly from tools.py lines 911-925

def _get_sort_order(sort_order: str):
    # Copy exactly from tools.py lines 927-934
```

### 5. Create Assets Module (20 minutes)
**File: `src/kaltura_mcp/tools/assets.py`**
```python
"""Asset operations - captions, attachments, and supplementary content."""

from typing import Any, Dict, Optional

from ..kaltura_client import KalturaClientManager
from .utils import handle_kaltura_error, safe_serialize_kaltura_field, validate_entry_id

# Try to import Caption plugin for caption assets
try:
    from KalturaClient.Plugins.Caption import (
        KalturaCaptionAssetFilter,
    )
    CAPTION_AVAILABLE = True
except ImportError:
    CAPTION_AVAILABLE = False

# Try to import Attachment plugin for attachment assets
try:
    from KalturaClient.Plugins.Attachment import (
        KalturaAttachmentAssetFilter,
    )
    ATTACHMENT_AVAILABLE = True
except ImportError:
    ATTACHMENT_AVAILABLE = False


async def list_caption_assets(manager: KalturaClientManager, entry_id: str) -> str:
    """List available captions and subtitles for a media entry."""
    # Copy exactly from tools.py lines 1083-1146


async def get_caption_content(manager: KalturaClientManager, caption_asset_id: str) -> str:
    """Get caption/subtitle content and download URL."""
    # Copy exactly from tools.py lines 1148-1240


async def list_attachment_assets(manager: KalturaClientManager, entry_id: str) -> str:
    """List attachment assets for a media entry."""
    # Copy exactly from tools.py lines 1242-1312


async def get_attachment_content(manager: KalturaClientManager, attachment_asset_id: str) -> str:
    """Get attachment content details and download URL."""
    # Copy exactly from tools.py lines 1314-1414
```

### 6. Update Package Init - Zero Breaking Changes (10 minutes)
**File: `src/kaltura_mcp/tools/__init__.py`**
```python
"""Kaltura MCP tools - elegant modular organization."""

# Import utilities
from .utils import (
    handle_kaltura_error,
    safe_serialize_kaltura_field,
    validate_entry_id,
)

# Import by domain for clear organization
from .media import (
    get_download_url,
    get_media_entry,
    get_thumbnail_url,
    list_media_entries,
)

from .analytics import (
    get_analytics,
)

from .search import (
    esearch_entries,
    list_categories,
    search_entries,
    search_entries_intelligent,
)

from .assets import (
    get_attachment_content,
    get_caption_content,
    list_attachment_assets,
    list_caption_assets,
)

# Export everything exactly as before - ZERO breaking changes
__all__ = [
    # Utilities
    "handle_kaltura_error",
    "safe_serialize_kaltura_field",
    "validate_entry_id",
    # Media operations
    "get_download_url",
    "get_media_entry",
    "get_thumbnail_url",
    "list_media_entries",
    # Analytics operations
    "get_analytics",
    # Search operations
    "esearch_entries",
    "list_categories", 
    "search_entries",
    "search_entries_intelligent",
    # Asset operations
    "get_attachment_content",
    "get_caption_content",
    "list_attachment_assets",
    "list_caption_assets",
]
```

### 7. Test and Migrate (15 minutes)
```bash
# Create tools directory
mkdir -p src/kaltura_mcp/tools

# Create __init__.py to make it a package
touch src/kaltura_mcp/tools/__init__.py

# Backup original
cp src/kaltura_mcp/tools.py src/kaltura_mcp/tools.py.backup

# After creating all modules, remove original
rm src/kaltura_mcp/tools.py

# Test everything works exactly as before
./scripts/check.sh

# Verify imports work
python -c "from kaltura_mcp.tools import get_media_entry, get_analytics, search_entries_intelligent, list_caption_assets, handle_kaltura_error; print('✅ All imports work correctly')"

# If tests pass, clean up backup
rm src/kaltura_mcp/tools.py.backup
```

## Verification Checklist

### ✅ **Zero Breaking Changes**
- [ ] Same imports: `from kaltura_mcp.tools import get_media_entry` works
- [ ] Same API: All function signatures unchanged
- [ ] Same tests: All 58 tests pass without modification
- [ ] Same server.py: No changes needed to server imports

### ✅ **Code Quality**
- [ ] All functions copied exactly with same logic
- [ ] All imports preserved and working
- [ ] All error handling preserved
- [ ] All security validation preserved

### ✅ **Organization Benefits**
- [ ] Clear domain separation (media, analytics, search, assets)
- [ ] Related functionality grouped together
- [ ] Easy to find specific tools
- [ ] Ready for future extensions

## Future Extension Patterns

### Adding New Tools by Domain

**New Media Tool:**
```python
# Add to tools/media.py
async def upload_media(manager, file_path: str, title: str) -> str:
    """Upload new media entry."""
    # Implementation here
    
# Add to tools/__init__.py imports and __all__
# Add to server.py call_tool function
```

**New Analytics Tool:**
```python
# Add to tools/analytics.py  
async def get_user_engagement(manager, entry_id: str) -> str:
    """Get detailed user engagement analytics."""
    # Implementation here
```

### Domain Growth Potential
- **media.py**: Upload, transcode, playlist management, flavor management
- **analytics.py**: Real-time analytics, custom reports, export tools, dashboards  
- **search.py**: AI search, recommendations, semantic search, advanced filters
- **assets.py**: Auto-captions, metadata management, thumbnail generation

## Benefits

### **Immediate**
- 📁 **Perfect organization**: Clear domain separation
- 📖 **Easy navigation**: Know exactly where each tool lives
- 🔧 **Better maintenance**: Related functionality together
- 👥 **Team collaboration**: Teams can own specific domains

### **Long-term**
- 🎯 **Clear extension patterns**: New tools have obvious homes
- 🔒 **Domain isolation**: Changes in one area don't affect others
- 📊 **Scalable testing**: Test domains independently
- 📚 **Self-documenting**: Each module documents a business domain
- 🚀 **Growth-ready**: Each domain can grow independently

## Files Created
- `src/kaltura_mcp/tools/utils.py` (~80 lines) - Shared utilities
- `src/kaltura_mcp/tools/media.py` (~400 lines) - Core media operations
- `src/kaltura_mcp/tools/analytics.py` (~200 lines) - Analytics & reporting
- `src/kaltura_mcp/tools/search.py` (~600 lines) - Search & discovery
- `src/kaltura_mcp/tools/assets.py` (~300 lines) - Assets & supplementary content
- `src/kaltura_mcp/tools/__init__.py` (~80 lines) - Clean exports

## Files Removed
- `src/kaltura_mcp/tools.py` (1414 lines → replaced by 5 focused modules)

## Safety & Compliance Assurance

### **Functional Safety**
✅ **Exact code copying**: No logic changes, same behavior  
✅ **Preserved imports**: All dependencies maintained  
✅ **Same error handling**: Security and validation preserved  
✅ **Test compatibility**: All 58 tests continue to pass  

### **Security Compliance**
✅ **Validation preserved**: `validate_entry_id` security checks maintained  
✅ **Error handling preserved**: No sensitive data exposure  
✅ **Import patterns preserved**: No new attack vectors  

### **Maintainability**
✅ **Simple copy-paste**: Easy to verify correctness  
✅ **Clear separation**: Easy to understand and modify  
✅ **Future-ready**: Clear patterns for growth  

This plan creates **perfect organization with zero risk**: **same functionality, better structure, ready for growth**.