"""Test dimension parameter handling across different analytics functions."""

import json
from unittest.mock import Mock, patch

import pytest

from kaltura_mcp.tools.analytics import (
    get_analytics,
    get_analytics_timeseries,
)
from kaltura_mcp.tools.analytics_core import (
    get_analytics_enhanced,
    get_analytics_graph,
)


class TestDimensionHandling:
    """Test that dimension parameter is handled correctly for different API methods."""

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

    @pytest.mark.asyncio
    async def test_dimension_with_table_format(self, mock_manager, valid_dates):
        """Test that dimension parameter doesn't break getTable calls."""
        mock_client = mock_manager.get_client.return_value

        # Mock getTable response
        mock_result = Mock()
        mock_result.header = "entry_id,plays,device"
        mock_result.data = "1_abc,100,Desktop\n1_xyz,50,Mobile"
        mock_result.totalCount = 2
        mock_client.report.getTable.return_value = mock_result

        # Call with dimension parameter
        result = await get_analytics_enhanced(
            mock_manager,
            **valid_dates,
            report_type="content",
            dimension="device",
            response_format="json",
        )

        # Verify getTable was called WITHOUT dimension
        call_args = mock_client.report.getTable.call_args
        assert "dimension" not in call_args.kwargs
        assert "order" in call_args.kwargs  # order should be passed

        # Check response includes note about dimension limitation
        data = json.loads(result)
        assert "note" in data
        assert "Dimension 'device' was requested" in data["note"]
        assert "Use get_analytics_graph()" in data["note"]

    @pytest.mark.asyncio
    async def test_dimension_with_graph_format(self, mock_manager, valid_dates):
        """Test that dimension parameter works correctly with getGraphs."""
        mock_client = mock_manager.get_client.return_value

        # Mock getGraphs response
        mock_graphs = [
            type("Graph", (), {"id": "count_plays", "data": "20240101|100;20240102|150;"})()
        ]
        mock_client.report.getGraphs.return_value = mock_graphs
        mock_client.report.getTotal.return_value = None

        # Call with dimension parameter
        result = await get_analytics_graph(
            mock_manager, **valid_dates, report_type="content", dimension="device"
        )

        # Verify getGraphs was called WITH dimension
        call_args = mock_client.report.getGraphs.call_args
        assert call_args.kwargs["dimension"] == "device"

        # Check response
        data = json.loads(result)
        assert "graphs" in data
        assert "error" not in data

    @pytest.mark.asyncio
    async def test_dimension_with_csv_format(self, mock_manager, valid_dates):
        """Test that dimension parameter works with CSV export."""
        mock_client = mock_manager.get_client.return_value

        # Mock CSV export response
        mock_client.report.getUrlForReportAsCsv.return_value = "https://example.com/report.csv"

        # Call with dimension parameter
        result = await get_analytics_enhanced(
            mock_manager,
            **valid_dates,
            report_type="content",
            dimension="device",
            response_format="csv",
        )

        # Verify getUrlForReportAsCsv was called WITH dimension
        call_args = mock_client.report.getUrlForReportAsCsv.call_args
        assert call_args.kwargs["dimension"] == "device"
        assert call_args.kwargs["order"] is None  # order_by was None

        # Check response
        data = json.loads(result)
        assert data["format"] == "csv"
        assert "download_url" in data

    @pytest.mark.asyncio
    async def test_analytics_v2_dimension_passthrough(self, mock_manager, valid_dates):
        """Test that analytics_v2 functions pass dimension correctly."""
        with patch("kaltura_mcp.tools.analytics_core.get_analytics_enhanced") as mock_enhanced:
            mock_enhanced.return_value = json.dumps(
                {"data": [], "note": "Dimension 'device' was requested..."}
            )

            # Test get_analytics with dimension
            result = await get_analytics(
                mock_manager, **valid_dates, report_type="content", dimension="device"
            )

            # Verify dimension was passed through
            call_kwargs = mock_enhanced.call_args.kwargs
            assert call_kwargs["dimension"] == "device"

            # Check the note is in response
            data = json.loads(result)
            assert "note" in data

    @pytest.mark.asyncio
    async def test_timeseries_with_dimension(self, mock_manager, valid_dates):
        """Test that timeseries function uses graph format which supports dimension."""
        with patch("kaltura_mcp.tools.analytics_core.get_analytics_graph") as mock_graph:
            mock_graph.return_value = json.dumps({"graphs": [{"metric": "plays", "data": []}]})

            # Test get_analytics_timeseries with dimension
            await get_analytics_timeseries(
                mock_manager, **valid_dates, report_type="content", dimension="device"
            )

            # Verify it called graph function with dimension
            call_kwargs = mock_graph.call_args.kwargs
            assert call_kwargs["dimension"] == "device"

    @pytest.mark.asyncio
    async def test_order_parameter_handling(self, mock_manager, valid_dates):
        """Test that order parameter is passed correctly."""
        mock_client = mock_manager.get_client.return_value

        # Mock response
        mock_result = Mock()
        mock_result.header = "entry_id,plays"
        mock_result.data = "1_abc,100"
        mock_client.report.getTable.return_value = mock_result

        # Call with order_by parameter
        await get_analytics_enhanced(
            mock_manager,
            **valid_dates,
            report_type="content",
            order_by="+plays",  # Sort by plays ascending
        )

        # Verify order was passed to getTable
        call_args = mock_client.report.getTable.call_args
        assert call_args.kwargs["order"] == "+plays"

    @pytest.mark.asyncio
    async def test_error_message_clarity(self, mock_manager, valid_dates):
        """Test that error messages are clear when dimension issues occur."""
        mock_client = mock_manager.get_client.return_value

        # Simulate the original error
        mock_client.report.getTable.side_effect = TypeError(
            "getTable() got an unexpected keyword argument 'dimension'"
        )

        # This should now handle the error gracefully
        result = await get_analytics_enhanced(
            mock_manager, **valid_dates, report_type="content", dimension="device"
        )

        # Should return error response, not raise
        data = json.loads(result)
        assert "error" in data
        assert "Failed to retrieve analytics" in data["error"]
