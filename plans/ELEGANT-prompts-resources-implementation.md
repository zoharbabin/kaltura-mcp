# Prompts and Resources Implementation Plan - ELEGANT

**Complexity**: Medium  
**Impact**: Very High - Transforms user experience and MCP compliance  
**Priority**: HIGH - Core MCP feature implementation  
**Time Estimate**: 4-5 hours  
**Dependencies**: None (can be done independently)

## Executive Summary

This plan implements MCP Prompts and Resources for the Kaltura MCP server, following the project's existing patterns of simplicity and elegance. The implementation focuses on high-value features while maintaining clean, maintainable code.

## Problem Statement

Current limitations:
- Complex tools with many parameters are difficult to discover and use
- No guided workflows for common multi-step operations  
- Frequently accessed data requires repeated API calls
- LLMs struggle to understand which tool combinations to use

## Solution Overview

### 1. **Prompts** - Guided Workflows (Simple Implementation)
- Analytics wizard for comprehensive reports
- Content discovery assistant
- Accessibility audit guide

### 2. **Resources** - Cached Data Access
- Analytics capabilities documentation
- Category hierarchy tree
- Recent media entries

## Implementation Plan

### Phase 1: Simple Infrastructure (1 hour)

#### 1.1 Prompts System
**File: `src/kaltura_mcp/prompts.py`**
```python
"""Simple prompts implementation for Kaltura MCP."""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json
from datetime import datetime, timedelta

import mcp.types as types
from .kaltura_client import KalturaClientManager


@dataclass
class PromptDefinition:
    """Simple prompt definition."""
    name: str
    description: str
    arguments: List[types.PromptArgument]
    handler: Callable


class PromptsManager:
    """Manages MCP prompts with simple patterns."""
    
    def __init__(self):
        self.prompts: Dict[str, PromptDefinition] = {}
    
    def register(self, prompt: PromptDefinition) -> None:
        """Register a prompt."""
        self.prompts[prompt.name] = prompt
    
    def list_prompts(self) -> List[types.Prompt]:
        """List all prompts for MCP."""
        return [
            types.Prompt(
                name=p.name,
                description=p.description,
                arguments=p.arguments
            )
            for p in self.prompts.values()
        ]
    
    async def get_prompt(self, name: str, manager: KalturaClientManager, 
                        arguments: Optional[Dict[str, Any]] = None) -> types.GetPromptResult:
        """Execute a prompt and return messages."""
        if name not in self.prompts:
            raise ValueError(f"Unknown prompt: {name}")
        
        prompt = self.prompts[name]
        messages = await prompt.handler(manager, arguments or {})
        return types.GetPromptResult(messages=messages)


# Global prompts manager
prompts_manager = PromptsManager()


# Analytics Wizard Prompt
async def analytics_wizard_handler(manager: KalturaClientManager, 
                                 arguments: Dict[str, Any]) -> List[types.PromptMessage]:
    """Generate analytics wizard workflow."""
    goal = arguments.get("analysis_goal", "performance").lower()
    time_period = arguments.get("time_period", "last_week")
    
    # Convert time period to dates
    today = datetime.now()
    date_map = {
        "today": (today, today),
        "yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "last_week": (today - timedelta(days=7), today),
        "last_month": (today - timedelta(days=30), today),
    }
    
    start, end = date_map.get(time_period, date_map["last_week"])
    from_date = start.strftime("%Y-%m-%d")
    to_date = end.strftime("%Y-%m-%d")
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"I need to analyze {goal} for {time_period}. Please help me understand the data."
            )
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you analyze your content. Let me gather the relevant data."
            )
        )
    ]
    
    # Add workflow based on goal
    if "performance" in goal or "video" in goal:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"First, use get_analytics with from_date='{from_date}', to_date='{to_date}', "
                     f"report_type='content' to see top performing videos. Then use get_analytics_timeseries "
                     f"to see trends over time."
            )
        ))
    elif "engagement" in goal:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Use get_analytics with from_date='{from_date}', to_date='{to_date}', "
                     f"report_type='user_engagement' to analyze how viewers interact with content."
            )
        ))
    elif "geographic" in goal:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Use get_geographic_breakdown with from_date='{from_date}', to_date='{to_date}' "
                     f"to see where your viewers are located."
            )
        ))
    else:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Analyze the data from {from_date} to {to_date} using appropriate analytics tools."
            )
        ))
    
    return messages


# Content Discovery Prompt
async def content_discovery_handler(manager: KalturaClientManager,
                                  arguments: Dict[str, Any]) -> List[types.PromptMessage]:
    """Generate content discovery workflow."""
    intent = arguments.get("search_intent", "")
    include_details = arguments.get("include_details", "no").lower() == "yes"
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"I'm looking for: {intent}"
            )
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you find the content. Let me search based on your requirements."
            )
        )
    ]
    
    # Determine search strategy
    if "caption" in intent.lower() or "transcript" in intent.lower():
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Use search_entries_intelligent with query='{intent}', search_type='caption', "
                     f"include_highlights=True to find content with matching captions."
            )
        ))
    elif "recent" in intent.lower() or "latest" in intent.lower():
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text="Use search_entries_intelligent with sort_field='created_at', sort_order='desc' "
                     "to find the most recent content."
            )
        ))
    else:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Use search_entries_intelligent with query='{intent}' to find matching content."
            )
        ))
    
    if include_details:
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text="For each result, also check for available captions using list_caption_assets."
            )
        ))
    
    return messages


# Accessibility Audit Prompt
async def accessibility_audit_handler(manager: KalturaClientManager,
                                    arguments: Dict[str, Any]) -> List[types.PromptMessage]:
    """Generate accessibility audit workflow."""
    scope = arguments.get("audit_scope", "recent")
    
    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"I need to audit {scope} for accessibility compliance."
            )
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you check content for accessibility. This includes captions and metadata."
            )
        )
    ]
    
    if scope == "all":
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text="First, use search_entries_intelligent with media_type='video' to find all videos. "
                     "Then for each video, use list_caption_assets to check caption availability."
            )
        ))
    elif scope == "recent":
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text="Use search_entries_intelligent with sort_field='created_at', sort_order='desc', "
                     "max_results=20 to get recent videos. Then check each for captions."
            )
        ))
    elif scope.startswith("category:"):
        category = scope.replace("category:", "")
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Search for videos in category '{category}' and check their caption availability."
            )
        ))
    else:
        # Assume it's an entry ID
        messages.append(types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Check entry {scope} for accessibility using get_media_entry and list_caption_assets."
            )
        ))
    
    return messages


# Register prompts
prompts_manager.register(PromptDefinition(
    name="analytics_wizard",
    description="Interactive guide for creating comprehensive analytics reports",
    arguments=[
        types.PromptArgument(
            name="analysis_goal",
            description="What to analyze: 'video performance', 'viewer engagement', 'geographic reach'",
            required=True
        ),
        types.PromptArgument(
            name="time_period",
            description="Time period: 'today', 'yesterday', 'last_week', 'last_month'",
            required=True
        )
    ],
    handler=analytics_wizard_handler
))

prompts_manager.register(PromptDefinition(
    name="content_discovery",
    description="Natural language search assistant for finding media",
    arguments=[
        types.PromptArgument(
            name="search_intent",
            description="What you're looking for in natural language",
            required=True
        ),
        types.PromptArgument(
            name="include_details",
            description="Include captions and attachments? (yes/no)",
            required=False
        )
    ],
    handler=content_discovery_handler
))

prompts_manager.register(PromptDefinition(
    name="accessibility_audit",
    description="Check content for accessibility compliance",
    arguments=[
        types.PromptArgument(
            name="audit_scope",
            description="Scope: 'all', 'recent', 'category:name', or entry_id",
            required=True
        )
    ],
    handler=accessibility_audit_handler
))
```

#### 1.2 Resources System
**File: `src/kaltura_mcp/resources.py`**
```python
"""Simple resources implementation for Kaltura MCP."""

from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
import json
import time
import re

import mcp.types as types
from .kaltura_client import KalturaClientManager
from .tools.analytics_core import REPORT_TYPE_MAP, REPORT_TYPE_NAMES


@dataclass
class ResourceDefinition:
    """Simple resource definition."""
    uri_pattern: str
    name: str
    description: str
    mime_type: str
    handler: Callable
    cache_duration: int = 300  # 5 minutes default


class ResourcesManager:
    """Manages MCP resources with simple caching."""
    
    def __init__(self):
        self.resources: List[ResourceDefinition] = []
        self.cache: Dict[str, Tuple[str, float]] = {}
    
    def register(self, resource: ResourceDefinition) -> None:
        """Register a resource."""
        self.resources.append(resource)
    
    def list_resources(self) -> List[types.Resource]:
        """List static resources."""
        static_resources = []
        for r in self.resources:
            if "{" not in r.uri_pattern:  # Static resource
                static_resources.append(types.Resource(
                    uri=r.uri_pattern,
                    name=r.name,
                    description=r.description,
                    mimeType=r.mime_type
                ))
        return static_resources
    
    def list_resource_templates(self) -> List[types.ResourceTemplate]:
        """List dynamic resource templates."""
        templates = []
        for r in self.resources:
            if "{" in r.uri_pattern:  # Dynamic resource
                templates.append(types.ResourceTemplate(
                    uriTemplate=r.uri_pattern,
                    name=r.name,
                    description=r.description,
                    mimeType=r.mime_type
                ))
        return templates
    
    async def read_resource(self, uri: str, manager: KalturaClientManager) -> str:
        """Read resource with caching."""
        # Check cache
        if uri in self.cache:
            content, cached_at = self.cache[uri]
            resource = self._find_resource(uri)
            if resource and (time.time() - cached_at) < resource.cache_duration:
                return content
        
        # Find matching resource
        resource = self._find_resource(uri)
        if not resource:
            raise ValueError(f"Unknown resource: {uri}")
        
        # Read fresh content
        content = await resource.handler(uri, manager)
        
        # Update cache
        self.cache[uri] = (content, time.time())
        
        return content
    
    def _find_resource(self, uri: str) -> Optional[ResourceDefinition]:
        """Find resource matching URI."""
        for resource in self.resources:
            # Convert pattern to regex
            pattern = resource.uri_pattern
            pattern = pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
            pattern = f"^{pattern}$"
            
            if re.match(pattern, uri):
                return resource
        return None


# Global resources manager
resources_manager = ResourcesManager()


# Analytics Capabilities Resource
async def analytics_capabilities_handler(uri: str, manager: KalturaClientManager) -> str:
    """Return analytics capabilities documentation."""
    capabilities = {
        "report_types": {},
        "categories": {
            "content": [],
            "users": [],
            "geographic": [],
            "platform": [],
            "quality": []
        },
        "available_metrics": [
            "count_plays", "unique_viewers", "avg_view_time",
            "sum_time_viewed", "avg_completion_rate", "count_loads"
        ],
        "available_dimensions": [
            "device", "operating_system", "browser", "country",
            "region", "city", "domain", "entry_id", "user_id"
        ],
        "time_intervals": ["hours", "days", "weeks", "months"],
        "best_practices": {
            "performance_analysis": "Use 'content' report with time series",
            "engagement_tracking": "Combine 'user_engagement' with retention",
            "geographic_insights": "Start with country, drill to city"
        }
    }
    
    # Build report type information
    for key, code in REPORT_TYPE_MAP.items():
        category = "content"
        if "user" in key or "engagement" in key:
            category = "users"
        elif "geo" in key or "map" in key:
            category = "geographic"
        elif "platform" in key or "browser" in key:
            category = "platform"
        elif "qoe" in key or "quality" in key:
            category = "quality"
        
        capabilities["report_types"][key] = {
            "key": key,
            "code": code,
            "name": REPORT_TYPE_NAMES.get(key, key.replace("_", " ").title()),
            "category": category
        }
        
        if category in capabilities["categories"]:
            capabilities["categories"][category].append(key)
    
    return json.dumps(capabilities, indent=2)


# Category Tree Resource
async def category_tree_handler(uri: str, manager: KalturaClientManager) -> str:
    """Return category hierarchy."""
    client = manager.get_client()
    
    from KalturaClient.Plugins.Core import KalturaCategoryFilter, KalturaFilterPager
    
    filter = KalturaCategoryFilter()
    pager = KalturaFilterPager()
    pager.pageSize = 500
    
    result = client.category.list(filter, pager)
    
    # Build hierarchy
    categories_by_id = {}
    root_categories = []
    
    for category in result.objects:
        cat_data = {
            "id": category.id,
            "name": category.name,
            "fullName": category.fullName,
            "entriesCount": category.entriesCount,
            "parentId": category.parentId,
            "children": []
        }
        
        categories_by_id[category.id] = cat_data
        
        if category.parentId == 0:
            root_categories.append(cat_data)
    
    # Build tree
    for cat_id, cat_data in categories_by_id.items():
        parent_id = cat_data["parentId"]
        if parent_id and parent_id in categories_by_id:
            categories_by_id[parent_id]["children"].append(cat_data)
    
    return json.dumps({
        "tree": root_categories,
        "total_categories": len(categories_by_id),
        "total_entries": sum(cat["entriesCount"] for cat in categories_by_id.values())
    }, indent=2)


# Recent Media Resource
async def recent_media_handler(uri: str, manager: KalturaClientManager) -> str:
    """Return recent media entries."""
    # Extract count from URI
    match = re.match(r"kaltura://media/recent/(\d+)", uri)
    count = int(match.group(1)) if match else 20
    count = min(count, 100)  # Cap at 100
    
    client = manager.get_client()
    
    from KalturaClient.Plugins.Core import (
        KalturaMediaEntryFilter,
        KalturaFilterPager,
        KalturaMediaEntryOrderBy
    )
    
    filter = KalturaMediaEntryFilter()
    filter.orderBy = KalturaMediaEntryOrderBy.CREATED_AT_DESC
    
    pager = KalturaFilterPager()
    pager.pageSize = count
    
    result = client.media.list(filter, pager)
    
    entries = []
    for entry in result.objects:
        entries.append({
            "id": entry.id,
            "name": entry.name,
            "description": entry.description,
            "createdAt": entry.createdAt,
            "duration": entry.duration,
            "plays": entry.plays or 0,
            "views": entry.views or 0
        })
    
    return json.dumps({
        "entries": entries,
        "count": len(entries),
        "total_available": result.totalCount
    }, indent=2)


# Register resources
resources_manager.register(ResourceDefinition(
    uri_pattern="kaltura://analytics/capabilities",
    name="Analytics Capabilities",
    description="All available analytics report types and options",
    mime_type="application/json",
    handler=analytics_capabilities_handler,
    cache_duration=1800  # 30 minutes
))

resources_manager.register(ResourceDefinition(
    uri_pattern="kaltura://categories/tree",
    name="Category Hierarchy",
    description="Complete category tree with entry counts",
    mime_type="application/json",
    handler=category_tree_handler,
    cache_duration=1800  # 30 minutes
))

resources_manager.register(ResourceDefinition(
    uri_pattern="kaltura://media/recent/{count}",
    name="Recent Media",
    description="Most recently added media entries",
    mime_type="application/json",
    handler=recent_media_handler,
    cache_duration=300  # 5 minutes
))
```

### Phase 2: Server Integration (1 hour)

#### 2.1 Update Server
**File: `src/kaltura_mcp/server.py` (additions)**
```python
# Add to imports at the top
from .prompts import prompts_manager
from .resources import resources_manager

# After existing server initialization, add these handlers:

# Prompt handlers
@server.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    """List all available prompts."""
    return prompts_manager.list_prompts()

@server.get_prompt()
async def get_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> types.GetPromptResult:
    """Get a specific prompt."""
    return await prompts_manager.get_prompt(name, kaltura_manager, arguments)

# Resource handlers
@server.list_resources()
async def list_resources() -> List[types.Resource]:
    """List all available resources."""
    return resources_manager.list_resources()

@server.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    """List all resource templates."""
    return resources_manager.list_resource_templates()

@server.read_resource()
async def read_resource(uri: str) -> List[types.ResourceContent]:
    """Read a resource."""
    content = await resources_manager.read_resource(uri, kaltura_manager)
    return [types.ResourceContent(
        uri=uri,
        mimeType="application/json",
        text=content
    )]
```

### Phase 3: Testing (1 hour)

#### 3.1 Test Prompts
**File: `tests/test_prompts.py`**
```python
"""Test prompts functionality."""

import pytest
from unittest.mock import Mock
import mcp.types as types

from kaltura_mcp.prompts import prompts_manager


def test_list_prompts():
    """Test listing prompts."""
    prompts = prompts_manager.list_prompts()
    
    assert len(prompts) == 3
    assert any(p.name == "analytics_wizard" for p in prompts)
    assert any(p.name == "content_discovery" for p in prompts)
    assert any(p.name == "accessibility_audit" for p in prompts)


@pytest.mark.asyncio
async def test_analytics_wizard():
    """Test analytics wizard prompt."""
    mock_manager = Mock()
    
    result = await prompts_manager.get_prompt(
        "analytics_wizard",
        mock_manager,
        {
            "analysis_goal": "video performance",
            "time_period": "last_week"
        }
    )
    
    assert len(result.messages) > 0
    assert result.messages[0].role == "user"
    assert "analyze" in result.messages[0].content.text.lower()


@pytest.mark.asyncio
async def test_unknown_prompt():
    """Test unknown prompt handling."""
    mock_manager = Mock()
    
    with pytest.raises(ValueError, match="Unknown prompt"):
        await prompts_manager.get_prompt("unknown", mock_manager, {})
```

#### 3.2 Test Resources
**File: `tests/test_resources.py`**
```python
"""Test resources functionality."""

import pytest
import json
from unittest.mock import Mock, MagicMock

from kaltura_mcp.resources import resources_manager


def test_list_resources():
    """Test listing resources."""
    resources = resources_manager.list_resources()
    templates = resources_manager.list_resource_templates()
    
    # Static resources
    assert any(r.uri == "kaltura://analytics/capabilities" for r in resources)
    assert any(r.uri == "kaltura://categories/tree" for r in resources)
    
    # Dynamic templates
    assert any(t.uriTemplate == "kaltura://media/recent/{count}" for t in templates)


@pytest.mark.asyncio
async def test_analytics_capabilities():
    """Test analytics capabilities resource."""
    mock_manager = Mock()
    
    content = await resources_manager.read_resource(
        "kaltura://analytics/capabilities",
        mock_manager
    )
    
    data = json.loads(content)
    assert "report_types" in data
    assert "categories" in data
    assert "available_metrics" in data


@pytest.mark.asyncio
async def test_resource_caching():
    """Test resource caching."""
    mock_manager = Mock()
    
    # Clear cache
    resources_manager.cache.clear()
    
    # First read
    content1 = await resources_manager.read_resource(
        "kaltura://analytics/capabilities",
        mock_manager
    )
    
    # Second read (should be cached)
    content2 = await resources_manager.read_resource(
        "kaltura://analytics/capabilities",
        mock_manager
    )
    
    assert content1 == content2
    assert len(resources_manager.cache) == 1
```

### Phase 4: Documentation (30 minutes)

#### 4.1 Update README
Add to the README.md after the tools section:

```markdown
### Prompts

The server provides intelligent prompts to guide users through complex workflows:

1. **analytics_wizard** - Interactive guide for comprehensive analytics
   ```
   Arguments:
   - analysis_goal: What to analyze (e.g., "video performance")
   - time_period: Time range (e.g., "last_week")
   ```

2. **content_discovery** - Natural language search assistant
   ```
   Arguments:
   - search_intent: What you're looking for
   - include_details: Whether to fetch captions/attachments
   ```

3. **accessibility_audit** - Content accessibility checker
   ```
   Arguments:
   - audit_scope: What to audit ("all", "recent", or entry_id)
   ```

### Resources

The server exposes frequently-used data as cached resources:

1. **kaltura://analytics/capabilities** - Complete analytics documentation
2. **kaltura://categories/tree** - Category hierarchy with entry counts
3. **kaltura://media/recent/{count}** - Recent media entries (e.g., /20)
```

## Benefits

### For Users
1. **Guided Workflows** - Complex operations become simple conversations
2. **Faster Access** - Cached resources reduce API calls
3. **Natural Language** - Prompts understand intent, not just parameters

### For Developers
1. **Simple Code** - ~400 lines total, easy to understand and maintain
2. **Easy Extension** - Add new prompts/resources in minutes
3. **Follows Patterns** - Consistent with existing codebase style

### For MCP Compliance
1. **Full Compliance** - Implements prompts and resources per spec
2. **Proper Types** - Uses official MCP types throughout
3. **Clean Integration** - Minimal changes to existing server.py

## Extension Guide

### Adding a New Prompt
```python
# Define handler
async def my_prompt_handler(manager: KalturaClientManager, 
                          arguments: Dict[str, Any]) -> List[types.PromptMessage]:
    return [
        types.PromptMessage(
            role="user",
            content=types.TextContent(type="text", text="Your prompt logic here")
        )
    ]

# Register it
prompts_manager.register(PromptDefinition(
    name="my_prompt",
    description="What this prompt does",
    arguments=[
        types.PromptArgument(name="arg1", description="Description", required=True)
    ],
    handler=my_prompt_handler
))
```

### Adding a New Resource
```python
# Define handler
async def my_resource_handler(uri: str, manager: KalturaClientManager) -> str:
    # Fetch and return data as JSON
    return json.dumps({"data": "value"})

# Register it
resources_manager.register(ResourceDefinition(
    uri_pattern="kaltura://my/resource",
    name="My Resource",
    description="What this provides",
    mime_type="application/json",
    handler=my_resource_handler
))
```

## Implementation Timeline

1. **Hour 1** - Implement prompts.py and resources.py
2. **Hour 2** - Update server.py with handlers
3. **Hour 3** - Add tests
4. **Hour 4** - Update documentation and test with Claude Desktop

This simplified implementation provides all the value with minimal complexity, following the project's elegant patterns.