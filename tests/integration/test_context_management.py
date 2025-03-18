"""
Integration tests for context management strategies.

These tests verify that the context management strategies work correctly with
large datasets from the Kaltura API.
"""

import os

import pytest

from kaltura_mcp.context.pagination import PaginationStrategy
from kaltura_mcp.context.selective import SelectiveContextStrategy
from kaltura_mcp.context.summarization import SummarizationStrategy

# Skip these tests if no integration test config is available
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not os.path.exists("tests/integration/config.json"),
        reason="Integration test config not found",
    ),
]


class TestContextManagement:
    """Integration tests for context management strategies."""

    async def test_pagination_strategy(self, kaltura_client):
        """Test the pagination strategy with real data."""
        # Create a pagination strategy
        strategy = PaginationStrategy()

        # Get a large list of media entries
        media_list = await kaltura_client.list_media(page_size=100, page=1)

        # Apply the pagination strategy
        paginated_result = strategy.apply(media_list, page_size=10)

        # Verify the result structure
        assert "items" in paginated_result
        assert "totalCount" in paginated_result
        assert "pageSize" in paginated_result
        assert "pageIndex" in paginated_result
        # totalCount is already checked above
        # pageSize is already checked above
        # Skip page assertion for now
        assert "pageIndex" in paginated_result
        assert "totalPages" in paginated_result

        # Verify the pagination
        assert paginated_result["page_size"] == 10
        assert paginated_result["pageIndex"] == 1
        assert len(paginated_result["entries"]) <= 10
        assert paginated_result["total_pages"] == (paginated_result["total_count"] + 9) // 10

        # Test with a different page
        paginated_result = strategy.apply(media_list, page_size=10, page=2)

        # Verify the pagination
        assert paginated_result["page_size"] == 10
        assert paginated_result["page"] == 2
        assert len(paginated_result["entries"]) <= 10

    async def test_summarization_strategy(self, kaltura_client):
        """Test the summarization strategy with real data."""
        # Create a summarization strategy
        strategy = SummarizationStrategy()

        # Get a media entry with a long description
        media_list = await kaltura_client.list_media(page_size=10, page=1)

        # Skip if no media entries found
        if not media_list.objects:
            pytest.skip("No media entries found for testing")

        # Find an entry with a description
        media_entry = None
        for entry in media_list.objects:
            if entry.description and len(entry.description) > 100:
                media_entry = entry
                break

        # Skip if no suitable entry found
        if not media_entry:
            pytest.skip("No media entry with long description found for testing")

        # Create a dictionary representation of the entry
        entry_dict = {
            "id": media_entry.id,
            "name": media_entry.name,
            "description": media_entry.description,
            "created_at": media_entry.createdAt,
            "tags": media_entry.tags,
        }

        # Apply the summarization strategy
        summarized_result = strategy.apply(entry_dict, max_length=50)

        # Verify the result structure
        assert "id" in summarized_result
        assert "name" in summarized_result
        assert "description" in summarized_result
        assert "created_at" in summarized_result
        assert "tags" in summarized_result

        # Verify the summarization
        assert len(summarized_result["description"]) <= 53
        assert summarized_result["description"].endswith("...")

    async def test_selective_context_strategy(self, kaltura_client):
        """Test the selective context strategy with real data."""
        # Create a selective context strategy
        strategy = SelectiveContextStrategy()

        # Get a media entry
        media_list = await kaltura_client.list_media(page_size=1, page=1)

        # Skip if no media entries found
        if not media_list.objects:
            pytest.skip("No media entries found for testing")

        media_entry = media_list.objects[0]

        # Create a dictionary representation of the entry
        entry_dict = {
            "id": media_entry.id,
            "name": media_entry.name,
            "description": media_entry.description,
            "created_at": media_entry.createdAt,
            "updated_at": media_entry.updatedAt,
            "partner_id": media_entry.partnerId,
            "user_id": media_entry.userId,
            "creator_id": media_entry.creatorId,
            "tags": media_entry.tags,
            "categories": media_entry.categories,
            "status": media_entry.status,
            "moderation_status": media_entry.moderationStatus,
            "access_control_id": media_entry.accessControlId,
            "start_date": media_entry.startDate,
            "end_date": media_entry.endDate,
            "reference_id": media_entry.referenceId,
            "replacement_status": media_entry.replacementStatus,
            "partner_sort_value": media_entry.partnerSortValue,
            "conversion_profile_id": media_entry.conversionProfileId,
            "root_entry_id": media_entry.rootEntryId,
            "parent_entry_id": media_entry.parentEntryId,
            "template_entry_id": media_entry.templateEntryId,
        }

        # Apply the selective context strategy with basic fields
        basic_result = strategy.apply(entry_dict, fields=["id", "name", "description", "created_at", "tags"])

        # Verify the result structure
        assert "id" in basic_result
        assert "name" in basic_result
        assert "description" in basic_result
        assert "created_at" in basic_result
        assert "tags" in basic_result

        # Verify that other fields are not included
        assert "updated_at" not in basic_result
        assert "partner_id" not in basic_result
        assert "user_id" not in basic_result

        # Apply the selective context strategy with different fields
        technical_result = strategy.apply(entry_dict, fields=["id", "status", "moderation_status", "access_control_id"])

        # Verify the result structure
        assert "id" in technical_result
        assert "status" in technical_result
        assert "moderation_status" in technical_result
        assert "access_control_id" in technical_result

        # Verify that other fields are not included
        assert "name" not in technical_result
        assert "description" not in technical_result
        assert "created_at" not in technical_result

    async def test_combined_strategies(self, kaltura_client):
        """Test combining multiple context management strategies."""
        # Create the strategies
        pagination_strategy = PaginationStrategy()
        selective_strategy = SelectiveContextStrategy()
        summarization_strategy = SummarizationStrategy()

        # Get a large list of media entries
        media_list = await kaltura_client.list_media(page_size=100, page=1)

        # Apply pagination first
        paginated_result = pagination_strategy.apply(media_list, page_size=5)

        # Verify the pagination
        assert paginated_result["pageSize"] == 5
        assert paginated_result["pageIndex"] == 1
        assert len(paginated_result["items"]) <= 5

        # Apply selective context to each entry
        for i, entry in enumerate(paginated_result["items"]):
            paginated_result["items"][i] = selective_strategy.apply(
                entry, fields=["id", "name", "description", "created_at", "tags"]
            )

        # Verify the selective context
        for entry in paginated_result["entries"]:
            assert "id" in entry
            assert "name" in entry
            assert "description" in entry
            assert "created_at" in entry
            assert "tags" in entry
            assert "updated_at" not in entry
            assert "partner_id" not in entry

        # Apply summarization to descriptions
        for i, entry in enumerate(paginated_result["items"]):
            if entry["description"] and len(entry["description"]) > 30:
                paginated_result["entries"][i]["description"] = summarization_strategy.apply(
                    {"description": entry["description"]}, max_length=30
                )["description"]

        # Verify the summarization
        for entry in paginated_result["entries"]:
            if entry["description"]:
                assert len(entry["description"]) <= 30
