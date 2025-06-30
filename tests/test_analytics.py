"""Properly structured tests for analytics functionality."""

import json
from unittest.mock import Mock

import pytest

from kaltura_mcp.tools.analytics import get_analytics


class TestAnalytics:
    """Test suite with proper mocking for analytics functionality."""

    @pytest.fixture
    def mock_manager(self):
        """Mock Kaltura client manager."""
        manager = Mock()
        client = Mock()
        manager.get_client.return_value = client
        return manager

    @pytest.fixture
    def valid_dates(self):
        """Valid date range for testing."""
        return {"from_date": "2024-01-01", "to_date": "2024-01-31"}

    @pytest.fixture
    def mock_report_result(self):
        """Mock report result from Kaltura API."""
        result = Mock()
        result.header = "entry_id,entry_name,plays,views,engagement_rate"
        result.data = "1_abc123,Test Video,1000,1500,0.75\n1_def456,Another Video,500,800,0.65"
        return result

    # ========================================================================
    # DATE VALIDATION TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_invalid_date_format(self, mock_manager):
        """Test handling of invalid date formats."""
        result = await get_analytics(mock_manager, "2024/01/01", "2024-01-31")
        data = json.loads(result)
        assert "error" in data
        assert "Invalid date format" in data["error"]

    @pytest.mark.asyncio
    async def test_valid_date_formats(self, mock_manager, valid_dates, mock_report_result):
        """Test acceptance of valid date formats."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = mock_report_result

        result = await get_analytics(mock_manager, **valid_dates)
        data = json.loads(result)

        assert "error" not in data
        assert data["dateRange"]["from"] == valid_dates["from_date"]
        assert data["dateRange"]["to"] == valid_dates["to_date"]

    # ========================================================================
    # REPORT TYPE TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_engagement_timeline_report(self, mock_manager, valid_dates):
        """Test engagement timeline report specifically."""
        # Mock timeline-specific response
        timeline_result = Mock()
        timeline_result.header = "position,views,replays,completion_rate"
        timeline_result.data = "0,1000,0,1.0\n30,950,50,0.95\n60,900,100,0.90\n90,850,75,0.85"

        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = timeline_result

        result = await get_analytics(
            mock_manager, report_type="engagement_timeline", entry_id="1_abc123", **valid_dates
        )
        data = json.loads(result)

        assert data["reportTypeCode"] == "engagement_timeline"
        assert data["reportType"] == "Engagement Timeline"
        assert "position" in data["headers"]
        assert "replays" in data["headers"]
        assert len(data["data"]) == 4
        assert data["data"][1]["replays"] == "50"

    @pytest.mark.asyncio
    async def test_multiple_report_types(self, mock_manager, valid_dates, mock_report_result):
        """Test various report types work correctly."""
        report_types_to_test = [
            ("content", "Top Content"),
            ("content_dropoff", "Content Drop-off Analysis"),
            ("user_engagement", "User Engagement"),
            ("geographic_country", "Country Distribution"),
            ("platforms", "Platforms"),
            ("playback_rate", "Playback Rate Analysis"),
        ]

        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = mock_report_result

        for report_type_code, expected_name in report_types_to_test:
            result = await get_analytics(mock_manager, report_type=report_type_code, **valid_dates)
            data = json.loads(result)

            assert "error" not in data
            assert data["reportTypeCode"] == report_type_code
            assert data["reportType"] == expected_name

    # ========================================================================
    # ENTRY ID VALIDATION TEST
    # ========================================================================

    @pytest.mark.asyncio
    async def test_invalid_entry_id(self, mock_manager, valid_dates):
        """Test handling of invalid entry IDs."""
        result = await get_analytics(mock_manager, entry_id="invalid_id", **valid_dates)
        data = json.loads(result)
        assert "error" in data
        assert "Invalid entry ID format" in data["error"]

    # ========================================================================
    # DATA PARSING TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_csv_data_parsing(self, mock_manager, valid_dates):
        """Test parsing of CSV response data."""
        custom_result = Mock()
        custom_result.header = "metric1,metric2,metric3"
        custom_result.data = "100,200,300\n400,500,600\n700,800,900"

        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = custom_result

        result = await get_analytics(mock_manager, **valid_dates)
        data = json.loads(result)

        assert data["headers"] == ["metric1", "metric2", "metric3"]
        assert len(data["data"]) == 3
        assert data["data"][0]["metric1"] == "100"
        assert data["data"][1]["metric2"] == "500"
        assert data["data"][2]["metric3"] == "900"

    @pytest.mark.asyncio
    async def test_empty_data_handling(self, mock_manager, valid_dates):
        """Test handling of empty report data."""
        empty_result = Mock()
        empty_result.header = "entry_id,plays,views"
        empty_result.data = ""

        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = empty_result

        result = await get_analytics(mock_manager, **valid_dates)
        data = json.loads(result)

        assert data["headers"] == ["entry_id", "plays", "views"]
        assert data["data"] == []
        assert data["totalResults"] == 0

    # ========================================================================
    # PARAMETER TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_limit_parameter(self, mock_manager, valid_dates, mock_report_result):
        """Test limit parameter handling."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = mock_report_result

        # Check that getTable is called with correct pager settings
        await get_analytics(mock_manager, limit=50, **valid_dates)

        # Get the pager argument from the call
        call_args = mock_client.report.getTable.call_args
        pager = call_args.kwargs["pager"]
        assert pager.pageSize == 50

    @pytest.mark.asyncio
    async def test_category_filter(self, mock_manager, valid_dates, mock_report_result):
        """Test category filtering."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = mock_report_result

        category = "Training>Sales"
        await get_analytics(mock_manager, categories=category, **valid_dates)

        # Get the filter argument from the call
        call_args = mock_client.report.getTable.call_args
        report_filter = call_args.kwargs["reportInputFilter"]
        assert report_filter.categories == category

    # ========================================================================
    # ERROR HANDLING TEST
    # ========================================================================

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_manager, valid_dates):
        """Test handling of Kaltura API errors."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.side_effect = Exception("API Error: Invalid KS")

        result = await get_analytics(mock_manager, **valid_dates)
        data = json.loads(result)

        assert "error" in data
        assert "Failed to retrieve analytics" in data["error"]
        assert "API Error" in data["error"]
        assert "suggestion" in data

    # ========================================================================
    # INTEGRATION TEST
    # ========================================================================

    @pytest.mark.asyncio
    async def test_full_analytics_flow(self, mock_manager):
        """Test complete analytics flow with realistic data."""
        # Mock a comprehensive response
        comprehensive_result = Mock()
        comprehensive_result.header = (
            "entry_id,entry_name,plays,unique_viewers,avg_view_time,completion_rate"
        )
        comprehensive_result.data = "\n".join(
            [
                "1_video1,Product Demo,5000,3500,180,0.65",
                "1_video2,Tutorial Part 1,3000,2500,420,0.85",
                "1_video3,Tutorial Part 2,2500,2000,380,0.80",
                "1_video4,Webinar Recording,1500,1200,2400,0.45",
                "1_video5,Company Overview,8000,7000,90,0.95",
            ]
        )

        mock_client = mock_manager.get_client.return_value
        mock_client.report.getTable.return_value = comprehensive_result

        result = await get_analytics(
            mock_manager,
            from_date="2024-01-01",
            to_date="2024-01-31",
            report_type="content",
            limit=10,
        )
        data = json.loads(result)

        # Verify structure
        assert data["reportType"] == "Top Content"
        assert data["reportTypeCode"] == "content"
        assert len(data["headers"]) == 6
        assert len(data["data"]) == 5
        assert data["totalResults"] == 5

        # Verify data parsing
        assert data["data"][0]["entry_name"] == "Product Demo"
        assert data["data"][0]["plays"] == "5000"
        assert data["data"][4]["completion_rate"] == "0.95"
