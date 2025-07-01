"""Simple resources implementation for Kaltura MCP."""

import json
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

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
                static_resources.append(
                    types.Resource(
                        uri=r.uri_pattern,
                        name=r.name,
                        description=r.description,
                        mimeType=r.mime_type,
                    )
                )
        return static_resources

    def list_resource_templates(self) -> List[types.ResourceTemplate]:
        """List dynamic resource templates."""
        templates = []
        for r in self.resources:
            if "{" in r.uri_pattern:  # Dynamic resource
                templates.append(
                    types.ResourceTemplate(
                        uriTemplate=r.uri_pattern,
                        name=r.name,
                        description=r.description,
                        mimeType=r.mime_type,
                    )
                )
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
        "categories": {"content": [], "users": [], "geographic": [], "platform": [], "quality": []},
        "available_metrics": [
            "count_plays",
            "unique_viewers",
            "avg_view_time",
            "sum_time_viewed",
            "avg_completion_rate",
            "count_loads",
        ],
        "available_dimensions": [
            "device",
            "operating_system",
            "browser",
            "country",
            "region",
            "city",
            "domain",
            "entry_id",
            "user_id",
        ],
        "time_intervals": ["hours", "days", "weeks", "months"],
        "best_practices": {
            "performance_analysis": "Use 'content' report with time series",
            "engagement_tracking": "Combine 'user_engagement' with retention",
            "geographic_insights": "Start with country, drill to city",
        },
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
            "category": category,
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
            "children": [],
        }

        categories_by_id[category.id] = cat_data

        if category.parentId == 0:
            root_categories.append(cat_data)

    # Build tree
    for cat_id, cat_data in categories_by_id.items():
        parent_id = cat_data["parentId"]
        if parent_id and parent_id in categories_by_id:
            categories_by_id[parent_id]["children"].append(cat_data)

    return json.dumps(
        {
            "tree": root_categories,
            "total_categories": len(categories_by_id),
            "total_entries": sum(cat["entriesCount"] for cat in categories_by_id.values()),
        },
        indent=2,
    )


# Recent Media Resource
async def recent_media_handler(uri: str, manager: KalturaClientManager) -> str:
    """Return recent media entries."""
    # Extract count from URI
    match = re.match(r"kaltura://media/recent/(\d+)", uri)
    count = int(match.group(1)) if match else 20
    count = min(count, 100)  # Cap at 100

    client = manager.get_client()

    from KalturaClient.Plugins.Core import (
        KalturaFilterPager,
        KalturaMediaEntryFilter,
        KalturaMediaEntryOrderBy,
    )

    filter = KalturaMediaEntryFilter()
    filter.orderBy = KalturaMediaEntryOrderBy.CREATED_AT_DESC

    pager = KalturaFilterPager()
    pager.pageSize = count

    result = client.media.list(filter, pager)

    entries = []
    for entry in result.objects:
        entries.append(
            {
                "id": entry.id,
                "name": entry.name,
                "description": entry.description,
                "createdAt": entry.createdAt,
                "duration": entry.duration,
                "plays": entry.plays or 0,
                "views": entry.views or 0,
            }
        )

    return json.dumps(
        {"entries": entries, "count": len(entries), "total_available": result.totalCount}, indent=2
    )


# Register resources
resources_manager.register(
    ResourceDefinition(
        uri_pattern="kaltura://analytics/capabilities",
        name="Analytics Capabilities",
        description="All available analytics report types and options",
        mime_type="application/json",
        handler=analytics_capabilities_handler,
        cache_duration=1800,  # 30 minutes
    )
)

resources_manager.register(
    ResourceDefinition(
        uri_pattern="kaltura://categories/tree",
        name="Category Hierarchy",
        description="Complete category tree with entry counts",
        mime_type="application/json",
        handler=category_tree_handler,
        cache_duration=1800,  # 30 minutes
    )
)

resources_manager.register(
    ResourceDefinition(
        uri_pattern="kaltura://media/recent/{count}",
        name="Recent Media",
        description="Most recently added media entries",
        mime_type="application/json",
        handler=recent_media_handler,
        cache_duration=300,  # 5 minutes
    )
)
