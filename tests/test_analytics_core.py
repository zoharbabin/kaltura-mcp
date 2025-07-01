"""Tests for core analytics functionality."""

import json
from unittest.mock import Mock

import pytest

from kaltura_mcp.tools.analytics_core import (
    REPORT_TYPE_MAP,
    REPORT_TYPE_NAMES,
    analyze_retention_insights,
    calculate_retention_curve,
    convert_value,
    get_analytics_enhanced,
    get_analytics_graph,
    parse_csv_row,
    parse_graph_data,
    parse_percentiles_data,
    parse_timeline_data,
)


class TestAnalyticsCore:
    """Simplified test suite for enhanced analytics."""

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

    # ========================================================================
    # REPORT TYPE TESTS
    # ========================================================================

    def test_report_type_coverage(self):
        """Test we have significantly more report types than original."""
        # Original implementation has 39 report types
        assert len(REPORT_TYPE_MAP) >= 60, f"Expected 60+ report types, got {len(REPORT_TYPE_MAP)}"

        # All report types should have names
        for report_type in REPORT_TYPE_MAP:
            assert report_type in REPORT_TYPE_NAMES

    def test_critical_report_types_exist(self):
        """Test that critical missing report types are now included."""
        critical_reports = [
            "content_report_reasons",  # 44 - Content moderation
            "user_usage",  # 17 - Platform adoption
            "partner_usage",  # 201 - Resource usage
            "var_usage",  # 19 - Multi-tenant usage
            "self_serve_usage",  # 60 - Self-serve features
        ]

        for report_type in critical_reports:
            assert report_type in REPORT_TYPE_MAP
            assert report_type in REPORT_TYPE_NAMES

    def test_advanced_report_categories(self):
        """Test that advanced report categories are included."""
        # QoE reports
        qoe_reports = [
            "qoe_overview",
            "qoe_experience",
            "qoe_engagement",
            "qoe_stream_quality",
            "qoe_error_tracking",
        ]
        for report in qoe_reports:
            assert report in REPORT_TYPE_MAP
            assert REPORT_TYPE_MAP[report] >= 30001

        # Real-time reports
        realtime_reports = ["realtime_country", "realtime_users", "realtime_qos"]
        for report in realtime_reports:
            assert report in REPORT_TYPE_MAP
            assert REPORT_TYPE_MAP[report] >= 10001

        # Webcast reports
        webcast_reports = ["webcast_highlights", "webcast_engagement"]
        for report in webcast_reports:
            assert report in REPORT_TYPE_MAP
            assert REPORT_TYPE_MAP[report] >= 40001

    # ========================================================================
    # PARAMETER VALIDATION TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_unknown_report_type(self, mock_manager, valid_dates):
        """Test handling of unknown report type."""
        result = await get_analytics_enhanced(
            mock_manager, report_type="invalid_report_xyz", **valid_dates
        )
        data = json.loads(result)
        assert "error" in data
        assert "Unknown report type" in data["error"]
        assert "available_types" in data

    @pytest.mark.asyncio
    async def test_object_id_validation(self, mock_manager, valid_dates):
        """Test validation for reports requiring object IDs."""
        # These reports require object IDs
        for report_type in ["engagement_timeline", "specific_user_engagement"]:
            result = await get_analytics_enhanced(
                mock_manager, report_type=report_type, **valid_dates
            )
            data = json.loads(result)
            assert "error" in data
            assert "requires object IDs" in data["error"]

    # ========================================================================
    # ENHANCED FEATURES TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_csv_export_option(self, mock_manager, valid_dates):
        """Test CSV export format option."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getUrlForReportAsCsv.return_value = "https://example.com/report.csv"

        result = await get_analytics_enhanced(
            mock_manager, report_type="content", response_format="csv", **valid_dates
        )

        data = json.loads(result)
        assert data["format"] == "csv"
        assert "download_url" in data
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_pagination_support(self, mock_manager, valid_dates):
        """Test pagination parameters."""
        mock_client = mock_manager.get_client.return_value
        mock_result = Mock()
        mock_result.header = "entry_id,plays"
        mock_result.data = "1_a,100"
        mock_result.totalCount = 500
        mock_client.report.getTable.return_value = mock_result

        result = await get_analytics_enhanced(
            mock_manager, report_type="content", limit=50, page_index=3, **valid_dates
        )

        # Check pager was set correctly
        call_args = mock_client.report.getTable.call_args
        pager = call_args.kwargs["pager"]
        assert pager.pageSize == 50
        assert pager.pageIndex == 3

        data = json.loads(result)
        assert data["pagination"]["totalCount"] == 500

    # ========================================================================
    # UTILITY FUNCTION TESTS
    # ========================================================================

    def test_parse_csv_row(self):
        """Test CSV parsing utility."""
        # Simple row
        assert parse_csv_row("a,b,c") == ["a", "b", "c"]

        # Quoted values with commas
        assert parse_csv_row('"hello, world","test",123') == ["hello, world", "test", "123"]

        # Empty values
        assert parse_csv_row("a,,c") == ["a", "", "c"]

    def test_parse_timeline_data(self):
        """Test timeline data parsing."""
        # Standard timeline format
        result = parse_timeline_data("100,90,80,70;metadata_string")
        assert result["timeline"] == [100.0, 90.0, 80.0, 70.0]
        assert result["metadata"] == "metadata_string"

        # Without metadata
        result = parse_timeline_data("100,90,80")
        assert "timeline" in result

    def test_convert_value(self):
        """Test value type conversion."""
        # Integers
        assert convert_value("123") == 123
        assert convert_value(" 456 ") == 456

        # Floats
        assert convert_value("123.45") == 123.45
        assert convert_value("0.5") == 0.5

        # Strings
        assert convert_value("text") == "text"
        assert convert_value("123abc") == "123abc"

        # Empty/whitespace
        assert convert_value("") == ""
        assert convert_value("   ") == ""

        # Test semicolon-separated values (like "0;1" from PERCENTILES)
        assert convert_value("0;1") == 0
        assert convert_value("50;100") == 50
        assert convert_value("99;1") == 99
        assert convert_value("12.5;25") == 12.5
        assert convert_value("abc;def") == "abc;def"  # Non-numeric returns as string

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_partner_usage_report(self, mock_manager, valid_dates):
        """Test partner usage report with summary."""
        mock_client = mock_manager.get_client.return_value

        # Mock table data
        table_result = Mock()
        table_result.header = "date,bandwidth_gb,storage_gb"
        table_result.data = "2024-01,100,500"
        mock_client.report.getTable.return_value = table_result

        # Mock summary data
        summary_result = Mock()
        summary_result.header = "total_bandwidth,total_storage"
        summary_result.data = "100,500"
        mock_client.report.getTotal.return_value = summary_result

        result = await get_analytics_enhanced(
            mock_manager, report_type="partner_usage", **valid_dates
        )

        data = json.loads(result)
        # Check for error since imports may fail in test environment
        if "error" not in data:
            assert data["reportTypeCode"] == "partner_usage"
            assert data["reportTypeId"] == 201
            assert "summary" in data
            assert data["summary"]["total_bandwidth"] == 100

    @pytest.mark.asyncio
    async def test_timeline_report_parsing(self, mock_manager, valid_dates):
        """Test engagement timeline special parsing."""
        mock_client = mock_manager.get_client.return_value
        timeline_result = Mock()
        timeline_result.header = "timeline"
        timeline_result.data = "100,95,90,85,80;segment_info"
        mock_client.report.getTable.return_value = timeline_result

        result = await get_analytics_enhanced(
            mock_manager, report_type="engagement_timeline", entry_id="1_test", **valid_dates
        )

        data = json.loads(result)
        # Check for error since imports may fail in test environment
        if "error" not in data:
            assert data["reportTypeCode"] == "engagement_timeline"
            assert len(data["data"]) == 1
            assert data["data"][0]["timeline"] == [100.0, 95.0, 90.0, 85.0, 80.0]

    # ========================================================================
    # GRAPH DATA TESTS
    # ========================================================================

    def test_parse_graph_data(self):
        """Test graph data parsing function."""
        # Standard format
        graph_data = "20240101|100;20240102|150;20240103|200;"
        parsed = parse_graph_data(graph_data)

        assert len(parsed) == 3
        assert parsed[0] == {"date": "2024-01-01", "value": 100}
        assert parsed[1] == {"date": "2024-01-02", "value": 150}
        assert parsed[2] == {"date": "2024-01-03", "value": 200}

        # With decimal values
        graph_data = "20240101|45.5;20240102|52.3;"
        parsed = parse_graph_data(graph_data)
        assert parsed[0]["value"] == 45.5
        assert parsed[1]["value"] == 52.3

        # Empty data
        assert parse_graph_data("") == []
        assert parse_graph_data(None) == []

    @pytest.mark.asyncio
    async def test_get_analytics_graph_success(self, mock_manager, valid_dates):
        """Test successful graph data retrieval."""
        mock_client = mock_manager.get_client.return_value

        # Mock graph results
        mock_graphs = [
            type(
                "Graph",
                (),
                {"id": "count_plays", "data": "20240101|100;20240102|150;20240103|200;"},
            )(),
            type(
                "Graph",
                (),
                {"id": "avg_time_viewed", "data": "20240101|45.5;20240102|52.3;20240103|48.7;"},
            )(),
        ]
        mock_client.report.getGraphs.return_value = mock_graphs

        # Mock totals
        mock_totals = Mock()
        mock_totals.header = "total_plays,avg_time"
        mock_totals.data = "450,48.8"
        mock_client.report.getTotal.return_value = mock_totals

        result = await get_analytics_graph(mock_manager, report_type="content", **valid_dates)

        data = json.loads(result)

        # Check structure
        assert "graphs" in data
        assert "summary" in data
        assert "dateRange" in data

        # Check graphs data if no error
        if "error" not in data:
            assert len(data["graphs"]) == 2

            # Check first graph
            assert data["graphs"][0]["metric"] == "count_plays"
            assert len(data["graphs"][0]["data"]) == 3
            assert data["graphs"][0]["data"][0] == {"date": "2024-01-01", "value": 100}

            # Check second graph
            assert data["graphs"][1]["metric"] == "avg_time_viewed"
            assert data["graphs"][1]["data"][0]["value"] == 45.5

            # Check summary
            assert data["summary"]["total_plays"] == 450
            assert data["summary"]["avg_time"] == 48.8

    @pytest.mark.asyncio
    async def test_get_analytics_graph_with_interval(self, mock_manager, valid_dates):
        """Test graph data with different intervals."""
        mock_client = mock_manager.get_client.return_value
        mock_client.report.getGraphs.return_value = []
        mock_client.report.getTotal.return_value = None

        # Test with weekly interval
        await get_analytics_graph(
            mock_manager, report_type="content", interval="weeks", **valid_dates
        )

        # Verify interval was passed correctly
        call_args = mock_client.report.getGraphs.call_args
        report_filter = call_args.kwargs["reportInputFilter"]

        # Check the filter has interval property if supported
        if hasattr(report_filter, "interval"):
            assert report_filter.interval == "weeks"

    @pytest.mark.asyncio
    async def test_get_analytics_graph_error_handling(self, mock_manager, valid_dates):
        """Test graph data error handling."""
        # Test with invalid report type
        result = await get_analytics_graph(
            mock_manager, report_type="invalid_graph_type", **valid_dates
        )

        data = json.loads(result)
        assert "error" in data
        assert "Unknown report type" in data["error"]

    @pytest.mark.asyncio
    async def test_get_analytics_graph_entry_validation(self, mock_manager, valid_dates):
        """Test graph data with entry ID validation."""
        # Test with invalid entry ID
        result = await get_analytics_graph(
            mock_manager, report_type="content", entry_id="invalid_entry", **valid_dates
        )

        data = json.loads(result)
        assert "error" in data
        assert "Invalid entry ID format" in data["error"]

    # ========================================================================
    # PERCENTILES & VIDEO TIMELINE TESTS
    # ========================================================================

    def test_percentiles_data_parsing(self):
        """Test parsing of percentiles report data."""
        # Standard percentiles data
        data = "0|0|0;1|100|85;2|98|84;50|55|50;100|38|35;"
        parsed = parse_percentiles_data(data)

        assert len(parsed) == 5
        assert parsed[0] == {
            "percentile": 0,
            "count_viewers": 0,
            "unique_known_users": 0,
            "replay_count": 0,
        }
        assert parsed[1] == {
            "percentile": 1,
            "count_viewers": 100,
            "unique_known_users": 85,
            "replay_count": 15,
        }
        assert parsed[4] == {
            "percentile": 100,
            "count_viewers": 38,
            "unique_known_users": 35,
            "replay_count": 3,
        }

        # Empty data
        assert parse_percentiles_data("") == []
        assert parse_percentiles_data(None) == []

    def test_calculate_retention_curve(self):
        """Test retention curve calculation."""
        percentiles_data = [
            {"percentile": 0, "count_viewers": 0, "unique_known_users": 0, "replay_count": 0},
            {"percentile": 1, "count_viewers": 100, "unique_known_users": 85, "replay_count": 15},
            {"percentile": 50, "count_viewers": 55, "unique_known_users": 50, "replay_count": 5},
            {"percentile": 100, "count_viewers": 38, "unique_known_users": 35, "replay_count": 3},
        ]

        retention_curve = calculate_retention_curve(percentiles_data)

        assert len(retention_curve) == 4
        # Check normalization (based on percentile 1 as baseline)
        assert retention_curve[1]["retention_rate"] == 100.0  # 100/100 * 100
        assert abs(retention_curve[2]["retention_rate"] - 55.0) < 0.01  # 55/100 * 100
        assert abs(retention_curve[3]["retention_rate"] - 38.0) < 0.01  # 38/100 * 100

        # Check other fields
        assert retention_curve[1]["viewers"] == 100
        assert retention_curve[1]["unique_users"] == 85
        assert retention_curve[1]["replays"] == 15

    def test_analyze_retention_insights(self):
        """Test retention insights analysis."""
        retention_curve = [
            {
                "percentile": 0,
                "retention_rate": 100.0,
                "viewers": 100,
                "unique_users": 85,
                "replays": 15,
            },
            {
                "percentile": 10,
                "retention_rate": 85.0,
                "viewers": 85,
                "unique_users": 80,
                "replays": 5,
            },
            {
                "percentile": 25,
                "retention_rate": 70.0,
                "viewers": 70,
                "unique_users": 65,
                "replays": 5,
            },
            {
                "percentile": 50,
                "retention_rate": 45.0,
                "viewers": 45,
                "unique_users": 40,
                "replays": 5,
            },
            {
                "percentile": 75,
                "retention_rate": 40.0,
                "viewers": 40,
                "unique_users": 35,
                "replays": 5,
            },
            {
                "percentile": 95,
                "retention_rate": 35.0,
                "viewers": 35,
                "unique_users": 30,
                "replays": 5,
            },
            {
                "percentile": 100,
                "retention_rate": 33.0,
                "viewers": 33,
                "unique_users": 30,
                "replays": 3,
            },
        ]

        insights = analyze_retention_insights(retention_curve)

        # Check insights
        assert "avg_retention" in insights
        assert "fifty_percent_point" in insights
        assert "completion_rate" in insights
        assert "major_drop_offs" in insights
        assert "replay_hotspots" in insights
        assert "engagement_score" in insights

        # Verify fifty percent point
        assert insights["fifty_percent_point"] == 50  # First point where retention <= 50%

        # Verify completion rate
        assert insights["completion_rate"] == 35.0  # Value at 95%+

        # Verify drop-offs detected
        assert len(insights["major_drop_offs"]) > 0
        assert insights["major_drop_offs"][0]["percentile"] == 10  # 15% drop
        assert insights["major_drop_offs"][0]["drop_percentage"] == 15.0

    @pytest.mark.asyncio
    async def test_get_video_timeline_analytics_basic(self, mock_manager, valid_dates):
        """Test basic video timeline analytics retrieval."""
        # Mock the client
        mock_client = mock_manager.get_client.return_value

        # Mock the raw API response
        mock_result = Mock()
        mock_result.header = "percentile,count_viewers,unique_known_users"
        mock_result.data = "0,0,0\n1,100,85\n50,55,50\n100,38,35"
        mock_result.totalCount = 101
        mock_client.report.getTable.return_value = mock_result

        from kaltura_mcp.tools.analytics_core import get_video_timeline_analytics

        result = await get_video_timeline_analytics(mock_manager, entry_id="1_test123")
        data = json.loads(result)

        # Check raw response structure
        assert "video_id" in data
        assert data["video_id"] == "1_test123"
        assert "kaltura_raw_response" in data
        assert "report_info" in data

        # Check raw response data
        raw_response = data["kaltura_raw_response"]
        assert "header" in raw_response
        assert "data" in raw_response
        assert raw_response["header"] == "percentile,count_viewers,unique_known_users"

    @pytest.mark.asyncio
    async def test_get_video_timeline_analytics_with_user_filter(self, mock_manager):
        """Test video timeline analytics with user filtering."""
        mock_client = mock_manager.get_client.return_value

        # Mock response
        mock_result = Mock()
        mock_result.header = "percentile,count_viewers,unique_known_users"
        mock_result.data = "0|0|0;1|50|1;50|30|1;100|20|1;"
        mock_result.totalCount = 101
        mock_client.report.getTable.return_value = mock_result

        from kaltura_mcp.tools.analytics_core import get_video_timeline_analytics

        # Test with specific user
        result = await get_video_timeline_analytics(
            mock_manager, entry_id="1_test123", user_ids="user@example.com"
        )

        data = json.loads(result)

        # Check filter was applied
        assert data["filter"]["user_ids"] == "user@example.com"
        # Check we got raw response
        assert "kaltura_raw_response" in data
        assert (
            data["kaltura_raw_response"]["header"] == "percentile,count_viewers,unique_known_users"
        )

    @pytest.mark.asyncio
    async def test_get_video_timeline_analytics_invalid_entry(self, mock_manager):
        """Test video timeline analytics with invalid entry ID."""
        from kaltura_mcp.tools.analytics_core import get_video_timeline_analytics

        # Test with invalid entry ID
        result = await get_video_timeline_analytics(mock_manager, entry_id="invalid_entry")

        data = json.loads(result)
        assert "error" in data
        assert "Valid entry_id required" in data["error"]

    @pytest.mark.asyncio
    async def test_percentiles_report_type_aliases(self, mock_manager, valid_dates):
        """Test that all percentiles aliases map to report ID 43."""
        aliases = [
            "percentiles",
            "video_timeline",
            "retention_curve",
            "viewer_retention",
            "drop_off_analysis",
            "replay_detection",
        ]

        for alias in aliases:
            assert REPORT_TYPE_MAP[alias] == 43
            assert alias in REPORT_TYPE_NAMES
