"""Test resources functionality."""

import json
from unittest.mock import Mock

import pytest

from kaltura_mcp.resources import resources_manager


def test_list_resources():
    """Test listing resources."""
    resources = resources_manager.list_resources()
    templates = resources_manager.list_resource_templates()

    # Static resources
    resource_uris = [str(r.uri) for r in resources]
    assert "kaltura://analytics/capabilities" in resource_uris
    assert "kaltura://categories/tree" in resource_uris

    # Dynamic templates
    template_uris = [str(t.uriTemplate) for t in templates]
    assert "kaltura://media/recent/{count}" in template_uris


@pytest.mark.asyncio
async def test_analytics_capabilities():
    """Test analytics capabilities resource."""
    mock_manager = Mock()

    content = await resources_manager.read_resource(
        "kaltura://analytics/capabilities", mock_manager
    )

    data = json.loads(content)
    assert "report_types" in data
    assert "categories" in data
    assert "available_metrics" in data
    assert "available_dimensions" in data
    assert "time_intervals" in data
    assert "best_practices" in data

    # Check some specific report types exist
    assert "content" in data["report_types"]
    assert "user_engagement" in data["report_types"]
    assert "geographic" in data["report_types"]

    # Check categories are populated
    assert len(data["categories"]["content"]) > 0
    assert len(data["categories"]["users"]) > 0


@pytest.mark.asyncio
async def test_category_tree():
    """Test category tree resource."""
    mock_manager = Mock()
    mock_client = Mock()
    mock_manager.get_client.return_value = mock_client

    # Create mock categories with proper attributes
    class MockCategory:
        def __init__(self, id, name, fullName, entriesCount, parentId):
            self.id = id
            self.name = name
            self.fullName = fullName
            self.entriesCount = entriesCount
            self.parentId = parentId

    # Mock category list response
    mock_result = Mock()
    mock_result.objects = [
        MockCategory(
            id=1, name="Root Category", fullName="Root Category", entriesCount=10, parentId=0
        ),
        MockCategory(
            id=2,
            name="Child Category",
            fullName="Root Category>Child Category",
            entriesCount=5,
            parentId=1,
        ),
    ]
    mock_client.category.list.return_value = mock_result

    content = await resources_manager.read_resource("kaltura://categories/tree", mock_manager)

    data = json.loads(content)
    assert "tree" in data
    assert "total_categories" in data
    assert "total_entries" in data
    assert data["total_categories"] == 2
    assert data["total_entries"] == 15


@pytest.mark.asyncio
async def test_recent_media():
    """Test recent media resource."""
    mock_manager = Mock()
    mock_client = Mock()
    mock_manager.get_client.return_value = mock_client

    # Create mock media entries with proper attributes
    class MockMediaEntry:
        def __init__(self, id, name, description, createdAt, duration, plays, views):
            self.id = id
            self.name = name
            self.description = description
            self.createdAt = createdAt
            self.duration = duration
            self.plays = plays
            self.views = views

    # Mock media list response
    mock_result = Mock()
    mock_result.objects = [
        MockMediaEntry(
            id="1_abc123",
            name="Video 1",
            description="Description 1",
            createdAt=1234567890,
            duration=120,
            plays=100,
            views=150,
        ),
        MockMediaEntry(
            id="1_def456",
            name="Video 2",
            description="Description 2",
            createdAt=1234567891,
            duration=180,
            plays=50,
            views=75,
        ),
    ]
    mock_result.totalCount = 100
    mock_client.media.list.return_value = mock_result

    content = await resources_manager.read_resource("kaltura://media/recent/20", mock_manager)

    data = json.loads(content)
    assert "entries" in data
    assert "count" in data
    assert "total_available" in data
    assert len(data["entries"]) == 2
    assert data["total_available"] == 100


@pytest.mark.asyncio
async def test_resource_caching():
    """Test resource caching."""
    mock_manager = Mock()

    # Clear cache
    resources_manager.cache.clear()

    # First read
    content1 = await resources_manager.read_resource(
        "kaltura://analytics/capabilities", mock_manager
    )

    # Second read (should be cached)
    content2 = await resources_manager.read_resource(
        "kaltura://analytics/capabilities", mock_manager
    )

    assert content1 == content2
    assert len(resources_manager.cache) == 1


@pytest.mark.asyncio
async def test_unknown_resource():
    """Test unknown resource handling."""
    mock_manager = Mock()

    with pytest.raises(ValueError, match="Unknown resource"):
        await resources_manager.read_resource("kaltura://unknown/resource", mock_manager)


@pytest.mark.asyncio
async def test_recent_media_with_different_counts():
    """Test recent media with different count values."""
    mock_manager = Mock()
    mock_client = Mock()
    mock_manager.get_client.return_value = mock_client

    # Mock empty result
    mock_result = Mock()
    mock_result.objects = []
    mock_result.totalCount = 0
    mock_client.media.list.return_value = mock_result

    # Test with count 50
    await resources_manager.read_resource("kaltura://media/recent/50", mock_manager)

    # Verify the pager was set correctly
    # Call args are (filter, pager) as positional arguments
    call_args = mock_client.media.list.call_args[0]
    pager_call = call_args[1] if len(call_args) > 1 else None
    assert pager_call is not None
    assert pager_call.pageSize == 50

    # Test with count > 100 (should cap at 100)
    await resources_manager.read_resource("kaltura://media/recent/200", mock_manager)

    call_args = mock_client.media.list.call_args[0]
    pager_call = call_args[1] if len(call_args) > 1 else None
    assert pager_call is not None
    assert pager_call.pageSize == 100  # Should be capped


@pytest.mark.asyncio
async def test_resource_find_by_pattern():
    """Test finding resources by URI pattern."""
    # Test static resource
    resource = resources_manager._find_resource("kaltura://analytics/capabilities")
    assert resource is not None
    assert resource.name == "Analytics Capabilities"

    # Test dynamic resource
    resource = resources_manager._find_resource("kaltura://media/recent/25")
    assert resource is not None
    assert resource.name == "Recent Media"

    # Test non-matching
    resource = resources_manager._find_resource("kaltura://invalid/path")
    assert resource is None
