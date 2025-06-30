"""Enhanced Analytics - Complete implementation with all report types and advanced features."""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Union

from ..kaltura_client import KalturaClientManager
from .utils import validate_entry_id

# Complete mapping of all Kaltura report types
REPORT_TYPE_MAP = {
    # Content Performance Reports (1-10, 34, 44)
    "content": 1,  # TOP_CONTENT
    "content_dropoff": 2,  # CONTENT_DROPOFF
    "content_interactions": 3,  # CONTENT_INTERACTIONS
    "engagement_timeline": 34,  # USER_ENGAGEMENT_TIMELINE
    "content_contributions": 7,  # CONTENT_CONTRIBUTIONS
    "content_report_reasons": 44,  # CONTENT_REPORT_REASONS
    "content_spread": 10,  # CONTENT_SPREAD
    # User Analytics Reports (11-18, 35, 40)
    "user_engagement": 11,  # USER_ENGAGEMENT
    "specific_user_engagement": 12,  # SPECIFIC_USER_ENGAGEMENT
    "user_top_content": 13,  # USER_TOP_CONTENT
    "user_content_dropoff": 14,  # USER_CONTENT_DROPOFF
    "user_content_interactions": 15,  # USER_CONTENT_INTERACTIONS
    "user_usage": 17,  # USER_USAGE
    "unique_users": 35,  # UNIQUE_USERS_PLAY
    "user_highlights": 40,  # USER_HIGHLIGHTS
    "specific_user_usage": 18,  # SPECIFIC_USER_USAGE
    # Geographic & Demographic Reports (4, 30, 36-37)
    "geographic": 4,  # MAP_OVERLAY
    "geographic_country": 36,  # MAP_OVERLAY_COUNTRY
    "geographic_region": 37,  # MAP_OVERLAY_REGION
    "geographic_city": 30,  # MAP_OVERLAY_CITY
    # Platform & Technology Reports (21-23, 32-33)
    "platforms": 21,  # PLATFORMS
    "operating_system": 22,  # OPERATING_SYSTEM
    "browsers": 23,  # BROWSERS
    "operating_system_families": 32,  # OPERATING_SYSTEM_FAMILIES
    "browsers_families": 33,  # BROWSERS_FAMILIES
    # Creator & Contributor Reports (5, 20, 38-39)
    "contributors": 5,  # TOP_CONTRIBUTORS
    "creators": 20,  # TOP_CREATORS
    "content_creator": 38,  # TOP_CONTENT_CREATOR
    "content_contributors": 39,  # TOP_CONTENT_CONTRIBUTORS
    # Distribution & Syndication Reports (6, 25, 41-42)
    "syndication": 6,  # TOP_SYNDICATION
    "playback_context": 25,  # TOP_PLAYBACK_CONTEXT
    "sources": 41,  # TOP_SOURCES
    "syndication_usage": 42,  # TOP_SYNDICATION_DISTRIBUTION
    # Usage & Infrastructure Reports (19, 26-27, 60, 64, 201)
    "partner_usage": 201,  # PARTNER_USAGE
    "var_usage": 19,  # VAR_USAGE
    "vpaas_usage": 26,  # VPAAS_USAGE
    "entry_usage": 27,  # ENTRY_USAGE
    "self_serve_usage": 60,  # SELF_SERVE_USAGE
    "cdn_bandwidth": 64,  # CDN_BANDWIDTH_USAGE
    # Interactive & Advanced Reports (43, 45-50)
    "percentiles": 43,  # PERCENTILES
    "player_interactions": 45,  # PLAYER_RELATED_INTERACTIONS
    "playback_rate": 46,  # PLAYBACK_RATE
    "interactive_video": 49,  # USER_INTERACTIVE_VIDEO
    "interactive_nodes": 50,  # INTERACTIVE_VIDEO_TOP_NODES
    # Live & Real-time Reports (48, 10001-10006)
    "live_stats": 48,  # LIVE_STATS
    "realtime_country": 10001,  # MAP_OVERLAY_COUNTRY_REALTIME
    "realtime_users": 10005,  # USERS_OVERVIEW_REALTIME
    "realtime_qos": 10006,  # QOS_OVERVIEW_REALTIME
    # Quality of Experience Reports (30001-30050)
    "qoe_overview": 30001,  # QOE_OVERVIEW
    "qoe_experience": 30002,  # QOE_EXPERIENCE
    "qoe_engagement": 30014,  # QOE_ENGAGEMENT
    "qoe_stream_quality": 30026,  # QOE_STREAM_QUALITY
    "qoe_error_tracking": 30038,  # QOE_ERROR_TRACKING
    # Business Intelligence & Webcast Reports (40001-40013)
    "webcast_highlights": 40001,  # HIGHLIGHTS_WEBCAST
    "webcast_engagement": 40011,  # ENGAGEMENT_TIMELINE_WEBCAST
    # Additional Reports
    "discovery": 51,  # DISCOVERY
    "discovery_realtime": 52,  # DISCOVERY_REALTIME
    "realtime": 53,  # REALTIME
    "peak_usage": 54,  # PEAK_USAGE
    "flavor_params_usage": 55,  # FLAVOR_PARAMS_USAGE
    "content_spread_country": 56,  # CONTENT_SPREAD_COUNTRY
    "top_contributors_country": 57,  # TOP_CONTRIBUTORS_COUNTRY
    "contribution_source": 58,  # CONTRIBUTION_SOURCE
    "vod_performance": 59,  # VOD_PERFORMANCE
}

# Report display names
REPORT_TYPE_NAMES = {
    # Content Performance
    "content": "Top Content",
    "content_dropoff": "Content Drop-off Analysis",
    "content_interactions": "Content Interactions",
    "engagement_timeline": "Engagement Timeline",
    "content_contributions": "Content Contributions",
    "content_report_reasons": "Content Report Reasons",
    "content_spread": "Content Spread Analysis",
    # User Analytics
    "user_engagement": "User Engagement",
    "specific_user_engagement": "Specific User Engagement",
    "user_top_content": "User Top Content",
    "user_content_dropoff": "User Content Drop-off",
    "user_content_interactions": "User Content Interactions",
    "user_usage": "User Usage Statistics",
    "unique_users": "Unique Users",
    "user_highlights": "User Highlights",
    "specific_user_usage": "Specific User Usage",
    # Geographic
    "geographic": "Geographic Distribution",
    "geographic_country": "Country Distribution",
    "geographic_region": "Regional Distribution",
    "geographic_city": "City Distribution",
    # Platform & Technology
    "platforms": "Platforms",
    "operating_system": "Operating Systems",
    "browsers": "Browsers",
    "operating_system_families": "OS Families",
    "browsers_families": "Browser Families",
    # Creators & Contributors
    "contributors": "Top Contributors",
    "creators": "Top Creators",
    "content_creator": "Top Content by Creator",
    "content_contributors": "Top Content Contributors",
    # Distribution
    "syndication": "Syndication Performance",
    "playback_context": "Playback Context",
    "sources": "Top Traffic Sources",
    "syndication_usage": "Syndication Usage",
    # Usage & Infrastructure
    "partner_usage": "Partner Usage",
    "var_usage": "VAR Usage",
    "vpaas_usage": "VPaaS Usage",
    "entry_usage": "Entry Usage",
    "self_serve_usage": "Self-Serve Usage",
    "cdn_bandwidth": "CDN Bandwidth Usage",
    # Interactive & Advanced
    "percentiles": "Performance Percentiles",
    "player_interactions": "Player Interactions",
    "playback_rate": "Playback Rate Analysis",
    "interactive_video": "Interactive Video Analytics",
    "interactive_nodes": "Interactive Video Nodes",
    # Live & Real-time
    "live_stats": "Live Statistics",
    "realtime_country": "Real-time Country Distribution",
    "realtime_users": "Real-time Users Overview",
    "realtime_qos": "Real-time Quality of Service",
    # Quality of Experience
    "qoe_overview": "QoE Overview",
    "qoe_experience": "QoE Experience Metrics",
    "qoe_engagement": "QoE Engagement Impact",
    "qoe_stream_quality": "QoE Stream Quality",
    "qoe_error_tracking": "QoE Error Tracking",
    # Business Intelligence
    "webcast_highlights": "Webcast Highlights",
    "webcast_engagement": "Webcast Engagement Timeline",
    # Additional
    "discovery": "Discovery Analytics",
    "discovery_realtime": "Real-time Discovery",
    "realtime": "Real-time Analytics",
    "peak_usage": "Peak Usage Times",
    "flavor_params_usage": "Flavor Parameters Usage",
    "content_spread_country": "Content Spread by Country",
    "top_contributors_country": "Top Contributors by Country",
    "contribution_source": "Contribution Sources",
    "vod_performance": "VOD Performance",
}

# Reports that require EndUserReportInputFilter
END_USER_REPORTS = {
    "user_engagement",
    "specific_user_engagement",
    "user_top_content",
    "user_content_dropoff",
    "user_content_interactions",
    "user_usage",
    "engagement_timeline",
    "user_highlights",
    "specific_user_usage",
}

# Reports that require specific object IDs
OBJECT_ID_REQUIRED_REPORTS = {
    "engagement_timeline",  # Requires entry ID
    "specific_user_engagement",  # Requires user ID
    "specific_user_usage",  # Requires user ID
    "content_creator",  # Requires creator/user ID
    "webcast_highlights",  # Requires webcast/event ID
    "webcast_engagement",  # Requires webcast/event ID
}


async def get_analytics_enhanced(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    report_type: str = "content",
    entry_id: Optional[str] = None,
    user_id: Optional[str] = None,
    object_ids: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    categories: Optional[str] = None,
    dimension: Optional[str] = None,
    interval: Optional[str] = None,
    filters: Optional[Dict[str, str]] = None,
    limit: int = 20,
    page_index: int = 1,
    order_by: Optional[str] = None,
    response_format: str = "json",
) -> str:
    """Enhanced analytics with support for all report types and advanced features.

    Args:
        manager: Kaltura client manager
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        report_type: Type of report (see REPORT_TYPE_MAP keys)
        entry_id: Optional specific entry ID
        user_id: Optional specific user ID
        object_ids: Optional comma-separated object IDs
        metrics: Requested metrics (for reference)
        categories: Category filter
        dimension: Dimension for grouping (e.g., "device", "country")
        interval: Time interval (e.g., "days", "months", "years")
        filters: Additional filters (customVar1In, countryIn, etc.)
        limit: Maximum results
        page_index: Page number for pagination
        order_by: Sort field
        response_format: "json" or "csv"
    """
    # Validate dates
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, from_date) or not re.match(date_pattern, to_date):
        return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"}, indent=2)

    # Validate entry ID if provided
    if entry_id and not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    # Get report type ID
    report_type_id = REPORT_TYPE_MAP.get(report_type)
    if not report_type_id:
        return json.dumps(
            {
                "error": f"Unknown report type: {report_type}",
                "available_types": list(REPORT_TYPE_MAP.keys()),
            },
            indent=2,
        )

    # Check if object IDs are required
    if report_type in OBJECT_ID_REQUIRED_REPORTS and not (entry_id or user_id or object_ids):
        return json.dumps(
            {
                "error": f"Report type '{report_type}' requires object IDs",
                "suggestion": "Provide entry_id, user_id, or object_ids parameter",
            },
            indent=2,
        )

    client = manager.get_client()

    try:
        from KalturaClient.Plugins.Core import (
            KalturaEndUserReportInputFilter,
            KalturaFilterPager,
            KalturaReportInputFilter,
            KalturaReportInterval,
        )

        # Convert dates
        start_time = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        end_time = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

        # Create appropriate filter
        if report_type in END_USER_REPORTS:
            report_filter = KalturaEndUserReportInputFilter()
        else:
            report_filter = KalturaReportInputFilter()

        # Set date range
        report_filter.fromDate = start_time
        report_filter.toDate = end_time

        # Set categories if provided
        if categories:
            report_filter.categories = categories

        # Set interval if provided
        if interval:
            interval_map = {
                "days": KalturaReportInterval.DAYS,
                "months": KalturaReportInterval.MONTHS,
                "years": KalturaReportInterval.YEARS,
            }
            if interval in interval_map:
                report_filter.interval = interval_map[interval]

        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if hasattr(report_filter, key):
                    setattr(report_filter, key, value)

        # Create pager
        pager = KalturaFilterPager()
        pager.pageSize = min(limit, 500)  # Allow larger pages
        pager.pageIndex = page_index

        # Prepare object IDs
        if object_ids:
            obj_ids = object_ids
        elif entry_id:
            obj_ids = entry_id
        elif user_id:
            obj_ids = user_id
        else:
            obj_ids = None

        # Get the report type enum value
        # For numeric IDs, just use the ID directly
        kaltura_report_type = report_type_id

        # Call appropriate API method
        if response_format == "csv":
            # Get CSV export URL
            csv_result = client.report.getUrlForReportAsCsv(
                reportTitle=f"{REPORT_TYPE_NAMES.get(report_type, 'Report')}_{from_date}_{to_date}",
                reportText=f"Report from {from_date} to {to_date}",
                headers=",".join(metrics) if metrics else None,
                reportType=kaltura_report_type,
                reportInputFilter=report_filter,
                dimension=dimension,
                pager=pager,
                order=order_by,
                objectIds=obj_ids,
            )

            return json.dumps(
                {
                    "format": "csv",
                    "download_url": csv_result,
                    "expires_in": "300 seconds",
                    "report_type": REPORT_TYPE_NAMES.get(report_type, report_type),
                },
                indent=2,
            )

        else:
            # Get table data
            report_result = client.report.getTable(
                reportType=kaltura_report_type,
                reportInputFilter=report_filter,
                dimension=dimension,
                pager=pager,
                order=order_by,
                objectIds=obj_ids,
            )

            # Parse results
            analytics_data = {
                "reportType": REPORT_TYPE_NAMES.get(report_type, "Analytics Report"),
                "reportTypeCode": report_type,
                "reportTypeId": report_type_id,
                "dateRange": {"from": from_date, "to": to_date},
                "filters": {
                    "categories": categories,
                    "dimension": dimension,
                    "interval": interval,
                    "objectIds": obj_ids,
                    "additionalFilters": filters,
                },
                "pagination": {
                    "pageSize": pager.pageSize,
                    "pageIndex": pager.pageIndex,
                    "totalCount": getattr(report_result, "totalCount", 0),
                },
                "headers": [],
                "data": [],
            }

            # Parse headers
            if report_result.header:
                analytics_data["headers"] = [h.strip() for h in report_result.header.split(",")]

            # Parse data with enhanced handling
            if report_result.data:
                data_rows = report_result.data.split("\n")
                for row in data_rows:
                    if row.strip():
                        # Handle different data formats
                        if ";" in row and report_type == "engagement_timeline":
                            # Special handling for timeline data
                            timeline_data = parse_timeline_data(row)
                            analytics_data["data"].append(timeline_data)
                        else:
                            # Standard CSV parsing
                            row_values = parse_csv_row(row)
                            if len(row_values) >= len(analytics_data["headers"]):
                                row_dict = {}
                                for i, header in enumerate(analytics_data["headers"]):
                                    if i < len(row_values):
                                        row_dict[header] = convert_value(row_values[i])
                                analytics_data["data"].append(row_dict)

            analytics_data["totalResults"] = len(analytics_data["data"])

            # Add summary for certain reports
            if report_type in ["partner_usage", "var_usage", "cdn_bandwidth"]:
                summary_result = client.report.getTotal(
                    reportType=kaltura_report_type,
                    reportInputFilter=report_filter,
                    objectIds=obj_ids,
                )
                if summary_result:
                    analytics_data["summary"] = parse_summary_data(summary_result)

            return json.dumps(analytics_data, indent=2)

    except ImportError as e:
        return json.dumps(
            {
                "error": "Analytics functionality not available",
                "detail": str(e),
                "suggestion": "Ensure Kaltura client has Report plugin",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve analytics: {str(e)}",
                "report_type": report_type,
                "suggestion": "Check permissions and report availability",
            },
            indent=2,
        )


def parse_csv_row(row: str) -> List[str]:
    """Parse CSV row handling quoted values."""
    import csv
    import io

    reader = csv.reader(io.StringIO(row))
    try:
        return next(reader)
    except StopIteration:
        return row.split(",")


def parse_timeline_data(row: str) -> Dict[str, Union[str, List[float]]]:
    """Parse timeline data format (semicolon-separated)."""
    parts = row.split(";")
    if len(parts) >= 2:
        return {
            "timeline": [float(x) for x in parts[0].split(",") if x],
            "metadata": parts[1] if len(parts) > 1 else "",
        }
    return {"timeline": row}


def convert_value(value: str) -> Union[str, int, float]:
    """Convert string values to appropriate types."""
    value = value.strip()
    if not value:
        return value

    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Return as string
    return value


def parse_summary_data(summary_result) -> Dict[str, any]:
    """Parse summary/total data from report."""
    summary = {}
    if hasattr(summary_result, "header") and hasattr(summary_result, "data"):
        headers = [h.strip() for h in summary_result.header.split(",")]
        values = parse_csv_row(summary_result.data)
        for i, header in enumerate(headers):
            if i < len(values):
                summary[header] = convert_value(values[i])
    return summary


# Additional specialized functions


async def get_realtime_analytics(
    manager: KalturaClientManager,
    report_type: str = "realtime_users",
    entry_id: Optional[str] = None,
) -> str:
    """Get real-time analytics data (updated every ~30 seconds)."""
    # Real-time reports don't need date range
    return await get_analytics_enhanced(
        manager=manager,
        from_date=datetime.now().strftime("%Y-%m-%d"),
        to_date=datetime.now().strftime("%Y-%m-%d"),
        report_type=report_type,
        entry_id=entry_id,
        limit=100,
    )


async def get_qoe_analytics(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    metric: str = "overview",
    dimension: Optional[str] = None,
) -> str:
    """Get Quality of Experience analytics."""
    qoe_map = {
        "overview": "qoe_overview",
        "experience": "qoe_experience",
        "engagement": "qoe_engagement",
        "stream": "qoe_stream_quality",
        "errors": "qoe_error_tracking",
    }

    report_type = qoe_map.get(metric, "qoe_overview")
    return await get_analytics_enhanced(
        manager=manager,
        from_date=from_date,
        to_date=to_date,
        report_type=report_type,
        dimension=dimension,
    )


async def get_geographic_analytics(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    level: str = "country",
    country_filter: Optional[str] = None,
) -> str:
    """Get geographic analytics at different levels."""
    geo_map = {
        "world": "geographic",
        "country": "geographic_country",
        "region": "geographic_region",
        "city": "geographic_city",
    }

    filters = {}
    if country_filter and level in ["region", "city"]:
        filters["countryIn"] = country_filter

    return await get_analytics_enhanced(
        manager=manager,
        from_date=from_date,
        to_date=to_date,
        report_type=geo_map.get(level, "geographic_country"),
        filters=filters,
    )
