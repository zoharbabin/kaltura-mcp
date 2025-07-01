"""Test prompts functionality."""

from unittest.mock import Mock

import pytest

from kaltura_mcp.prompts import prompts_manager


def test_list_prompts():
    """Test listing prompts."""
    prompts = prompts_manager.list_prompts()

    assert len(prompts) == 4
    assert any(p.name == "analytics_wizard" for p in prompts)
    assert any(p.name == "content_discovery" for p in prompts)
    assert any(p.name == "accessibility_audit" for p in prompts)
    assert any(p.name == "retention_analysis" for p in prompts)


@pytest.mark.asyncio
async def test_analytics_wizard():
    """Test analytics wizard prompt."""
    mock_manager = Mock()

    result = await prompts_manager.get_prompt(
        "analytics_wizard",
        mock_manager,
        {"analysis_goal": "video performance", "time_period": "last_week"},
    )

    assert len(result.messages) > 0
    assert result.messages[0].role == "user"
    assert "analyze" in result.messages[0].content.text.lower()


@pytest.mark.asyncio
async def test_content_discovery():
    """Test content discovery prompt."""
    mock_manager = Mock()

    result = await prompts_manager.get_prompt(
        "content_discovery",
        mock_manager,
        {"search_intent": "training videos with captions", "include_details": "yes"},
    )

    assert len(result.messages) > 0
    assert result.messages[0].role == "user"
    assert "looking for" in result.messages[0].content.text.lower()
    # Should have additional message for details
    assert any("caption" in msg.content.text.lower() for msg in result.messages)


@pytest.mark.asyncio
async def test_accessibility_audit():
    """Test accessibility audit prompt."""
    mock_manager = Mock()

    result = await prompts_manager.get_prompt(
        "accessibility_audit", mock_manager, {"audit_scope": "recent"}
    )

    assert len(result.messages) > 0
    assert result.messages[0].role == "user"
    assert "audit" in result.messages[0].content.text.lower()
    assert "accessibility" in result.messages[1].content.text.lower()


@pytest.mark.asyncio
async def test_unknown_prompt():
    """Test unknown prompt handling."""
    mock_manager = Mock()

    with pytest.raises(ValueError, match="Unknown prompt"):
        await prompts_manager.get_prompt("unknown", mock_manager, {})


@pytest.mark.asyncio
async def test_analytics_wizard_time_periods():
    """Test different time periods in analytics wizard."""
    mock_manager = Mock()

    for time_period in ["today", "yesterday", "last_week", "last_month"]:
        result = await prompts_manager.get_prompt(
            "analytics_wizard",
            mock_manager,
            {"analysis_goal": "performance", "time_period": time_period},
        )

        assert len(result.messages) > 0
        # Check that dates are mentioned in the workflow
        assert any("from_date" in msg.content.text for msg in result.messages[2:])


@pytest.mark.asyncio
async def test_content_discovery_search_types():
    """Test different search types in content discovery."""
    mock_manager = Mock()

    # Test caption search
    result = await prompts_manager.get_prompt(
        "content_discovery",
        mock_manager,
        {"search_intent": "videos with transcript mentioning python"},
    )
    assert any("search_type='caption'" in msg.content.text for msg in result.messages)

    # Test recent content
    result = await prompts_manager.get_prompt(
        "content_discovery", mock_manager, {"search_intent": "latest uploaded videos"}
    )
    assert any("sort_field='created_at'" in msg.content.text for msg in result.messages)


@pytest.mark.asyncio
async def test_accessibility_audit_scopes():
    """Test different audit scopes."""
    mock_manager = Mock()

    # Test category scope
    result = await prompts_manager.get_prompt(
        "accessibility_audit", mock_manager, {"audit_scope": "category:Training"}
    )
    assert any("category 'Training'" in msg.content.text for msg in result.messages)

    # Test specific entry ID
    result = await prompts_manager.get_prompt(
        "accessibility_audit", mock_manager, {"audit_scope": "1_abc123"}
    )
    assert any("entry 1_abc123" in msg.content.text for msg in result.messages)


@pytest.mark.asyncio
async def test_retention_analysis():
    """Test retention analysis prompt."""
    mock_manager = Mock()

    # Test with all parameters
    result = await prompts_manager.get_prompt(
        "retention_analysis",
        mock_manager,
        {"entry_id": "1_3atosphg", "time_period": "6", "output_format": "interactive"},
    )

    assert len(result.messages) >= 5
    assert result.messages[0].role == "user"
    assert "1_3atosphg" in result.messages[0].content.text
    assert "6 months" in result.messages[0].content.text

    # Check workflow includes retention analysis
    workflow_text = " ".join(msg.content.text for msg in result.messages)
    assert "get_video_retention" in workflow_text
    assert "time_formatted" in workflow_text  # Check for time conversion emphasis
    assert "X-axis" in workflow_text and "time" in workflow_text  # Check X-axis clarity
    assert "list_caption_assets" in workflow_text
    assert "interactive" in workflow_text.lower()  # Check for interactive content
    assert "HTML" in workflow_text or "html" in workflow_text  # Check for HTML output
    assert "hover" in workflow_text  # Check for hover functionality
    assert "engagement" in workflow_text.lower()  # Check for engagement focus
    assert "visual" in workflow_text.lower()  # Check for visual emphasis

    # Test with minimal parameters
    result = await prompts_manager.get_prompt(
        "retention_analysis", mock_manager, {"entry_id": "1_test123"}
    )

    assert len(result.messages) >= 5
    assert "12 months" in result.messages[0].content.text  # Default time period
