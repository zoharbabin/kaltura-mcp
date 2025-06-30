"""Analytics and reporting operations - insights and performance data."""

import json
import re
from typing import List, Optional

from ..kaltura_client import KalturaClientManager
from .utils import validate_entry_id


async def get_analytics(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    entry_id: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    report_type: str = "content",
    categories: Optional[str] = None,
    limit: int = 20,
) -> str:
    """Get analytics data using Kaltura Report API with support for multiple report types.

    Args:
        manager: Kaltura client manager
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        entry_id: Optional specific entry ID
        metrics: Requested metrics (for reference)
        report_type: Type of report - content, user_engagement, contributors, geographic, bandwidth, etc.
        categories: Category filter (full category name)
        limit: Maximum results to return
    """
    # Validate date format
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, from_date) or not re.match(date_pattern, to_date):
        return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"}, indent=2)

    if entry_id and not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    client = manager.get_client()

    try:
        # Import required classes for Report API
        # Convert dates to timestamps
        from datetime import datetime

        from KalturaClient.Plugins.Core import (
            KalturaEndUserReportInputFilter,
            KalturaFilterPager,
            KalturaReportInputFilter,
            KalturaReportType,
        )

        start_time = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        end_time = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

        # Map report type strings to enum values
        report_type_map = {
            "content": KalturaReportType.TOP_CONTENT,  # 1
            "user_engagement": KalturaReportType.USER_ENGAGEMENT,  # 11
            "contributors": KalturaReportType.TOP_CONTRIBUTORS,  # 5
            "geographic": KalturaReportType.MAP_OVERLAY,  # 4
            "bandwidth": KalturaReportType.TOP_SYNDICATION,  # 6
            "storage": KalturaReportType.PARTNER_USAGE,  # Partner usage for storage reports
            "system": KalturaReportType.PARTNER_USAGE,  # Partner usage for system reports
            "platforms": KalturaReportType.PLATFORMS,  # 13
            "operating_system": KalturaReportType.OPERATING_SYSTEM,  # 14
            "browsers": KalturaReportType.BROWSERS,  # 15
        }

        kaltura_report_type = report_type_map.get(report_type, KalturaReportType.TOP_CONTENT)

        # Determine if we need EndUserReportInputFilter (for user engagement reports)
        if report_type == "user_engagement":
            report_filter = KalturaEndUserReportInputFilter()
        else:
            report_filter = KalturaReportInputFilter()

        # Set common filter properties
        report_filter.fromDate = start_time
        report_filter.toDate = end_time

        # Add category filter if specified
        if categories:
            report_filter.categories = categories

        # Create pager (required for report API)
        pager = KalturaFilterPager()
        pager.pageSize = min(limit, 100)  # Cap at 100
        pager.pageIndex = 1

        # Set object IDs for entry-specific reports
        object_ids = entry_id if entry_id else None

        # Call the report API
        report_result = client.report.getTable(
            reportType=kaltura_report_type,
            reportInputFilter=report_filter,
            pager=pager,
            objectIds=object_ids,
        )

        # Get report type name for display
        report_type_names = {
            "content": "Top Content",
            "user_engagement": "User Engagement",
            "contributors": "Top Contributors",
            "geographic": "Geographic Distribution",
            "bandwidth": "Bandwidth Usage",
            "storage": "Storage Usage",
            "system": "System Reports",
            "platforms": "Platforms",
            "operating_system": "Operating Systems",
            "browsers": "Browsers",
        }

        # Parse the results
        analytics_data = {
            "reportType": report_type_names.get(report_type, "Analytics Report"),
            "reportTypeCode": report_type,
            "dateRange": {"from": from_date, "to": to_date},
            "entryId": entry_id,
            "categories": categories,
            "requestedMetrics": metrics or ["plays", "views", "engagement", "drop_off"],
            "headers": report_result.header.split(",") if report_result.header else [],
            "data": [],
        }

        # Process data rows
        if report_result.data:
            for row in report_result.data.split("\n"):
                if row.strip():
                    row_data = row.split(",")
                    if len(row_data) >= len(analytics_data["headers"]):
                        # Create a dictionary mapping headers to values
                        row_dict = {}
                        for i, header in enumerate(analytics_data["headers"]):
                            if i < len(row_data):
                                row_dict[header.strip()] = row_data[i].strip()
                        analytics_data["data"].append(row_dict)

        analytics_data["totalResults"] = len(analytics_data["data"])

        return json.dumps(analytics_data, indent=2)

    except ImportError as e:
        return json.dumps(
            {
                "error": "Analytics report functionality is not available. Missing required Kaltura Report plugin.",
                "detail": str(e),
                "suggestion": "Ensure the Kaltura Python client includes the Report plugin",
                "fromDate": from_date,
                "toDate": to_date,
                "entryId": entry_id,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve analytics: {str(e)}",
                "fromDate": from_date,
                "toDate": to_date,
                "entryId": entry_id,
                "requestedMetrics": metrics or ["plays", "views", "engagement", "drop_off"],
                "suggestion": "Check if your Kaltura account has analytics enabled and proper permissions",
            },
            indent=2,
        )
