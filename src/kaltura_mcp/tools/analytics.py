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
        report_type: Type of report - see full list in report_type_map
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
            # Content Performance
            "content": KalturaReportType.TOP_CONTENT,  # 1
            "content_dropoff": KalturaReportType.CONTENT_DROPOFF,  # 2
            "content_interactions": KalturaReportType.CONTENT_INTERACTIONS,  # 3
            "engagement_timeline": KalturaReportType.USER_ENGAGEMENT_TIMELINE,  # 34 - Timeline engagement
            "content_contributions": KalturaReportType.CONTENT_CONTRIBUTIONS,  # 7
            # User Analytics
            "user_engagement": KalturaReportType.USER_ENGAGEMENT,  # 11
            "specific_user_engagement": KalturaReportType.SPECIFIC_USER_ENGAGEMENT,  # 12
            "user_top_content": KalturaReportType.USER_TOP_CONTENT,  # 13
            "user_content_dropoff": KalturaReportType.USER_CONTENT_DROPOFF,  # 14
            "user_content_interactions": KalturaReportType.USER_CONTENT_INTERACTIONS,  # 15
            "user_usage": KalturaReportType.USER_USAGE,  # 17
            "unique_users": KalturaReportType.UNIQUE_USERS_PLAY,  # 35
            # Geographic
            "geographic": KalturaReportType.MAP_OVERLAY,  # 4
            "geographic_country": KalturaReportType.MAP_OVERLAY_COUNTRY,  # 36
            "geographic_region": KalturaReportType.MAP_OVERLAY_REGION,  # 37
            "geographic_city": KalturaReportType.MAP_OVERLAY_CITY,  # 30
            # Platform & Technology
            "platforms": KalturaReportType.PLATFORMS,  # 21
            "operating_system": KalturaReportType.OPERATING_SYSTEM,  # 22
            "operating_system_families": KalturaReportType.OPERATING_SYSTEM_FAMILIES,  # 32
            "browsers": KalturaReportType.BROWSERS,  # 23
            "browsers_families": KalturaReportType.BROWSERS_FAMILIES,  # 33
            # Creators & Contributors
            "contributors": KalturaReportType.TOP_CONTRIBUTORS,  # 5
            "creators": KalturaReportType.TOP_CREATORS,  # 20
            "content_creator": KalturaReportType.TOP_CONTENT_CREATOR,  # 38
            "content_contributors": KalturaReportType.TOP_CONTENT_CONTRIBUTORS,  # 39
            # Distribution
            "bandwidth": KalturaReportType.TOP_SYNDICATION,  # 6
            "playback_context": KalturaReportType.TOP_PLAYBACK_CONTEXT,  # 25
            "sources": KalturaReportType.TOP_SOURCES,  # 41
            # Usage & Infrastructure
            "partner_usage": KalturaReportType.PARTNER_USAGE,  # 201
            "storage": KalturaReportType.PARTNER_USAGE,  # Partner usage for storage
            "system": KalturaReportType.PARTNER_USAGE,  # Partner usage for system
            "vpaas_usage": KalturaReportType.VPAAS_USAGE,  # 26
            "entry_usage": KalturaReportType.ENTRY_USAGE,  # 27
            "cdn_bandwidth": KalturaReportType.CDN_BANDWIDTH_USAGE,  # 64
            # Advanced Analytics
            "playback_rate": KalturaReportType.PLAYBACK_RATE,  # 46
            "player_interactions": KalturaReportType.PLAYER_RELATED_INTERACTIONS,  # 45
            "percentiles": KalturaReportType.PERCENTILES,  # 43
            "interactive_video": KalturaReportType.USER_INTERACTIVE_VIDEO,  # 49
            "interactive_nodes": KalturaReportType.INTERACTIVE_VIDEO_TOP_NODES,  # 50
        }

        kaltura_report_type = report_type_map.get(report_type, KalturaReportType.TOP_CONTENT)

        # Determine if we need EndUserReportInputFilter (for user engagement reports)
        end_user_reports = [
            "user_engagement",
            "specific_user_engagement",
            "user_top_content",
            "user_content_dropoff",
            "user_content_interactions",
            "user_usage",
            "engagement_timeline",
        ]
        if report_type in end_user_reports:
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
            # Content Performance
            "content": "Top Content",
            "content_dropoff": "Content Drop-off Analysis",
            "content_interactions": "Content Interactions",
            "engagement_timeline": "Engagement Timeline",
            "content_contributions": "Content Contributions",
            # User Analytics
            "user_engagement": "User Engagement",
            "specific_user_engagement": "Specific User Engagement",
            "user_top_content": "User Top Content",
            "user_content_dropoff": "User Content Drop-off",
            "user_content_interactions": "User Content Interactions",
            "user_usage": "User Usage Statistics",
            "unique_users": "Unique Users",
            # Geographic
            "geographic": "Geographic Distribution",
            "geographic_country": "Country Distribution",
            "geographic_region": "Regional Distribution",
            "geographic_city": "City Distribution",
            # Platform & Technology
            "platforms": "Platforms",
            "operating_system": "Operating Systems",
            "operating_system_families": "OS Families",
            "browsers": "Browsers",
            "browsers_families": "Browser Families",
            # Creators & Contributors
            "contributors": "Top Contributors",
            "creators": "Top Creators",
            "content_creator": "Top Content by Creator",
            "content_contributors": "Top Content Contributors",
            # Distribution
            "bandwidth": "Bandwidth Usage",
            "playback_context": "Playback Context",
            "sources": "Top Traffic Sources",
            # Usage & Infrastructure
            "partner_usage": "Partner Usage",
            "storage": "Storage Usage",
            "system": "System Reports",
            "vpaas_usage": "VPaaS Usage",
            "entry_usage": "Entry Usage",
            "cdn_bandwidth": "CDN Bandwidth Usage",
            # Advanced Analytics
            "playback_rate": "Playback Rate Analysis",
            "player_interactions": "Player Interactions",
            "percentiles": "Performance Percentiles",
            "interactive_video": "Interactive Video Analytics",
            "interactive_nodes": "Interactive Video Nodes",
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
