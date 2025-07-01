"""Enhanced Analytics - Complete implementation with all report types and advanced features."""

import json
import re
from datetime import datetime, timedelta
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
    "percentiles": 43,  # PERCENTILES - Video timeline retention analysis
    "video_timeline": 43,  # Alias for PERCENTILES - clearer for LLMs
    "retention_curve": 43,  # Another alias for PERCENTILES
    "viewer_retention": 43,  # PERCENTILES - Per-video retention analysis
    "drop_off_analysis": 43,  # PERCENTILES - Where viewers stop watching
    "replay_detection": 43,  # PERCENTILES - Identify replay hotspots
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
    "percentiles": "Video Timeline Retention (Percentiles)",
    "video_timeline": "Video Timeline Retention Analysis",
    "retention_curve": "Viewer Retention Curve",
    "viewer_retention": "Per-Video Viewer Retention",
    "drop_off_analysis": "Video Drop-off Analysis",
    "replay_detection": "Replay Hotspot Detection",
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


async def get_analytics_graph(
    manager: KalturaClientManager,
    from_date: str,
    to_date: str,
    report_type: str = "content",
    entry_id: Optional[str] = None,
    user_id: Optional[str] = None,
    object_ids: Optional[str] = None,
    interval: str = "days",
    dimension: Optional[str] = None,
    filters: Optional[Dict[str, str]] = None,
) -> str:
    """
    Get analytics data in graph format suitable for visualization.

    This function returns time-series data for creating charts and graphs.
    Use this when you need data for visualization purposes.

    Args:
        manager: Kaltura client manager
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        report_type: Type of analytics report
        entry_id: Specific entry ID (if applicable)
        user_id: Specific user ID (if applicable)
        object_ids: Comma-separated object IDs
        interval: Time interval (days, weeks, months)
        dimension: Additional dimension for grouping
        filters: Additional filters

    Returns:
        JSON with graph data including:
        - Multiple metrics as separate time series
        - Each series has metric name and array of date/value pairs
        - Summary totals for the period

    Example response:
        {
            "graphs": [
                {
                    "metric": "count_plays",
                    "data": [
                        {"date": "2024-01-01", "value": 100},
                        {"date": "2024-01-02", "value": 150}
                    ]
                },
                {
                    "metric": "sum_time_viewed",
                    "data": [
                        {"date": "2024-01-01", "value": 3600},
                        {"date": "2024-01-02", "value": 5400}
                    ]
                }
            ],
            "summary": {
                "total_plays": 250,
                "total_time_viewed": 9000
            }
        }
    """
    # Validate inputs
    if report_type not in REPORT_TYPE_MAP:
        return json.dumps(
            {
                "error": f"Unknown report type: {report_type}",
                "available_types": list(REPORT_TYPE_MAP.keys()),
            },
            indent=2,
        )

    # Validate entry ID if provided
    if entry_id and not validate_entry_id(entry_id):
        return json.dumps({"error": "Invalid entry ID format"}, indent=2)

    # Check if report type requires specific IDs
    requires_object_ids = [
        "engagement_timeline",
        "specific_user_engagement",
        "specific_user_usage",
    ]
    if report_type in requires_object_ids and not (entry_id or user_id or object_ids):
        return json.dumps({"error": f"Report type '{report_type}' requires object IDs"}, indent=2)

    try:
        # Try to import KalturaReportType
        try:
            from KalturaClient.Plugins.Report import (
                KalturaEndUserReportInputFilter,
                KalturaReportInputFilter,
            )
        except ImportError:
            # Fallback if imports fail
            pass

        # Get client
        client = manager.get_client()

        # Build report filter
        try:
            # Try to use KalturaEndUserReportInputFilter for user-facing reports
            user_reports = [
                "user_engagement",
                "specific_user_engagement",
                "user_top_content",
                "user_usage",
                "specific_user_usage",
            ]

            if report_type in user_reports:
                report_filter = KalturaEndUserReportInputFilter()
            else:
                report_filter = KalturaReportInputFilter()
        except Exception:
            # Fallback to generic object with toParams method
            class FallbackFilter:
                def __init__(self):
                    pass

                def toParams(self):
                    """Return dict representation for API calls."""
                    return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

            report_filter = FallbackFilter()

        # Set filter properties
        report_filter.fromDate = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        report_filter.toDate = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

        # Set interval
        if hasattr(report_filter, "interval"):
            interval_map = {
                "days": "days",
                "weeks": "weeks",
                "months": "months",
                "years": "years",
            }
            report_filter.interval = interval_map.get(interval, "days")

        # Add object filters
        if entry_id:
            report_filter.entryIdIn = entry_id
        if user_id:
            report_filter.userIds = user_id

        # Set object IDs
        obj_ids = object_ids
        if entry_id and not obj_ids:
            obj_ids = entry_id
        elif user_id and not obj_ids:
            obj_ids = user_id
        else:
            obj_ids = None

        # Get report type ID
        report_type_id = REPORT_TYPE_MAP[report_type]

        # Call getGraphs API
        graphs_result = client.report.getGraphs(
            reportType=report_type_id,
            reportInputFilter=report_filter,
            dimension=dimension,
            objectIds=obj_ids,
        )

        # Also get totals
        totals_result = client.report.getTotal(
            reportType=report_type_id,
            reportInputFilter=report_filter,
            objectIds=obj_ids,
        )

        # Parse results
        response = {
            "reportType": REPORT_TYPE_NAMES.get(report_type, "Analytics Report"),
            "reportTypeCode": report_type,
            "reportTypeId": report_type_id,
            "dateRange": {"from": from_date, "to": to_date, "interval": interval},
            "graphs": [],
            "summary": {},
        }

        # Parse graph data
        if graphs_result and isinstance(graphs_result, list):
            for graph in graphs_result:
                if hasattr(graph, "id") and hasattr(graph, "data"):
                    graph_data = {"metric": graph.id, "data": parse_graph_data(graph.data)}
                    response["graphs"].append(graph_data)

        # Parse totals
        if totals_result:
            response["summary"] = parse_summary_data(totals_result)

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve graph data: {str(e)}",
                "report_type": report_type,
                "suggestion": "Use get_analytics_enhanced for table data instead",
            },
            indent=2,
        )


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
        response_format: "json", "csv", or "raw" (returns unprocessed API response)
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

    # If requesting raw format and imports might fail, return early with a simpler approach
    if response_format == "raw":
        try:
            # Try the simple approach first for raw format
            client = manager.get_client()

            # Direct API call without complex objects
            start_time = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
            end_time = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

            # Try to get the report directly
            try:
                # Prepare object IDs
                if object_ids:
                    obj_ids = object_ids
                elif entry_id:
                    obj_ids = entry_id
                elif user_id:
                    obj_ids = user_id
                else:
                    obj_ids = None

                # Try direct call with minimal parameters
                report_result = client.report.getTable(
                    reportType=report_type_id,
                    reportInputFilter={
                        "fromDate": start_time,
                        "toDate": end_time,
                        "entryIdIn": entry_id if entry_id else None,
                        "userIds": user_id if user_id else None,
                        "categories": categories if categories else None,
                    },
                    pager={"pageSize": min(limit, 500), "pageIndex": page_index},
                    order=order_by,
                    objectIds=obj_ids,
                )

                # Return raw response
                return json.dumps(
                    {
                        "kaltura_response": {
                            "header": getattr(report_result, "header", ""),
                            "data": getattr(report_result, "data", ""),
                            "totalCount": getattr(report_result, "totalCount", 0),
                        },
                        "request_info": {
                            "report_type": report_type,
                            "report_type_id": report_type_id,
                            "from_date": from_date,
                            "to_date": to_date,
                            "entry_id": entry_id,
                            "user_id": user_id,
                        },
                    },
                    indent=2,
                )
            except Exception:
                # If direct call fails, fall through to normal processing
                pass
        except Exception:
            # If anything fails, continue with normal processing
            pass

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
        if response_format == "raw":
            # Get raw table data without processing
            report_result = client.report.getTable(
                reportType=kaltura_report_type,
                reportInputFilter=report_filter,
                pager=pager,
                order=order_by,
                objectIds=obj_ids,
            )

            # Return raw Kaltura response with minimal wrapping
            return json.dumps(
                {
                    "kaltura_response": {
                        "header": getattr(report_result, "header", ""),
                        "data": getattr(report_result, "data", ""),
                        "totalCount": getattr(report_result, "totalCount", 0),
                    },
                    "request_info": {
                        "report_type": report_type,
                        "report_type_id": report_type_id,
                        "from_date": from_date,
                        "to_date": to_date,
                        "entry_id": entry_id,
                        "user_id": user_id,
                    },
                },
                indent=2,
            )

        elif response_format == "csv":
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
            # Note: getTable doesn't support dimension parameter
            # If dimension is requested, we'll include it in metadata but cannot group by it
            report_result = client.report.getTable(
                reportType=kaltura_report_type,
                reportInputFilter=report_filter,
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
                        elif report_type in [
                            "percentiles",
                            "video_timeline",
                            "retention_curve",
                            "viewer_retention",
                            "drop_off_analysis",
                            "replay_detection",
                        ]:
                            # Special handling for PERCENTILES report (ID 43)
                            # This report uses semicolon-separated rows with pipe-separated values
                            if "|" in row:
                                values = row.split("|")
                                if len(values) >= 3:
                                    row_dict = {
                                        "percentile": convert_value(values[0]),
                                        "count_viewers": convert_value(values[1]),
                                        "unique_known_users": convert_value(values[2]),
                                    }
                                    analytics_data["data"].append(row_dict)
                            else:
                                # Fallback to standard CSV parsing if no pipes found
                                row_values = parse_csv_row(row)
                                if len(row_values) >= len(analytics_data["headers"]):
                                    row_dict = {}
                                    for i, header in enumerate(analytics_data["headers"]):
                                        if i < len(row_values):
                                            row_dict[header] = convert_value(row_values[i])
                                    analytics_data["data"].append(row_dict)
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

            # Add note if dimension was requested but not applied
            if dimension:
                analytics_data["note"] = (
                    f"Dimension '{dimension}' was requested but grouping is not supported in table format. "
                    "Use get_analytics_graph() or response_format='graph' for dimensional analysis."
                )

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

    # Check if value contains semicolons (might be unparsed data)
    if ";" in value:
        # Try to extract the first numeric part before semicolon
        parts = value.split(";")
        first_part = parts[0].strip()
        # Try to convert the first part to int or float
        try:
            if "." in first_part:
                return float(first_part)
            else:
                return int(first_part)
        except ValueError:
            # Return as string if can't parse
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


def parse_graph_data(graph_data: str) -> List[Dict[str, Union[str, float]]]:
    """Parse graph data format (date|value;date|value)."""
    points = []
    if not graph_data:
        return points

    # Split by semicolon to get individual data points
    data_points = graph_data.rstrip(";").split(";")

    for point in data_points:
        if "|" in point:
            date_str, value_str = point.split("|", 1)
            # Convert date from YYYYMMDD to YYYY-MM-DD
            if len(date_str) == 8:
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            else:
                formatted_date = date_str

            points.append({"date": formatted_date, "value": convert_value(value_str)})

    return points


def parse_percentiles_data(data: str, delimiter: str = "|") -> List[Dict[str, Union[int, float]]]:
    """Parse percentiles report data (percentile|count_viewers|unique_known_users)."""
    rows = []
    if not data:
        return rows

    # Remove trailing semicolon and split by rows
    data_rows = data.rstrip(";").split(";")

    for row in data_rows:
        if row.strip():
            values = row.split(delimiter)
            if len(values) >= 3:
                rows.append(
                    {
                        "percentile": int(values[0]),
                        "count_viewers": int(values[1]),
                        "unique_known_users": int(values[2]),
                        "replay_count": int(values[1]) - int(values[2]),  # Calculate replays
                    }
                )

    return rows


def calculate_retention_curve(percentiles_data: List[Dict]) -> List[Dict[str, float]]:
    """Calculate normalized retention curve from percentiles data."""
    if not percentiles_data or len(percentiles_data) < 2:
        return []

    # Find the baseline (usually at percentile 1)
    baseline = next((row["count_viewers"] for row in percentiles_data if row["percentile"] == 1), 1)
    if baseline == 0:
        baseline = 1  # Avoid division by zero

    retention_curve = []
    for row in percentiles_data:
        retention_curve.append(
            {
                "percentile": row["percentile"],
                "retention_rate": (row["count_viewers"] / baseline) * 100,
                "viewers": row["count_viewers"],
                "unique_users": row["unique_known_users"],
                "replays": row["replay_count"],
            }
        )

    return retention_curve


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


async def get_video_timeline_analytics(
    manager: KalturaClientManager,
    entry_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    user_ids: Optional[str] = None,
    compare_cohorts: bool = False,
) -> str:
    """
    Get granular video timeline analytics using PERCENTILES report (ID 43).

    This function provides detailed retention curve data showing exactly where
    viewers drop off or replay content within a single video. Perfect for:
    - Creating retention curve visualizations
    - Identifying drop-off points
    - Detecting replay hotspots
    - Comparing viewer behavior between cohorts

    Args:
        manager: Kaltura client manager
        entry_id: Single video entry ID (required)
        from_date: Start date (defaults to 30 days ago)
        to_date: End date (defaults to today)
        user_ids: Optional user filter:
            - None/omitted: All viewers
            - "Unknown": Anonymous viewers only
            - "user@example.com": Specific user
            - "user1,user2,user3": Multiple users
        compare_cohorts: If True, returns both all viewers and filtered cohort

    Returns:
        JSON with raw Kaltura API response and context
    """
    # Validate entry ID
    if not entry_id or not validate_entry_id(entry_id):
        return json.dumps({"error": "Valid entry_id required for timeline analytics"}, indent=2)

    # Default date range if not provided
    if not from_date or not to_date:
        end = datetime.now()
        start = end - timedelta(days=30)
        from_date = from_date or start.strftime("%Y-%m-%d")
        to_date = to_date or end.strftime("%Y-%m-%d")

    # Use the core implementation with raw format
    result = await get_analytics_enhanced(
        manager=manager,
        from_date=from_date,
        to_date=to_date,
        report_type="percentiles",
        entry_id=entry_id,
        object_ids=entry_id,
        user_id=user_ids,
        limit=500,
        response_format="raw",
    )

    # Parse and enhance the result
    try:
        data = json.loads(result)
        if "error" in data:
            return result

        # Add context
        enhanced_result = {
            "video_id": entry_id,
            "date_range": {"from": from_date, "to": to_date},
            "filter": {"user_ids": user_ids or "all"},
            "kaltura_raw_response": data.get("kaltura_response", {}),
            "report_info": {
                "report_type": "PERCENTILES",
                "report_id": 43,
                "description": "Video timeline retention data with 101 percentile points (0-100)",
                "data_format": "CSV format with headers in 'header' field and data rows in 'data' field",
            },
        }
        return json.dumps(enhanced_result, indent=2)
    except Exception as e:
        return json.dumps(
            {
                "error": f"Failed to retrieve timeline analytics: {str(e)}",
                "entry_id": entry_id,
                "date_range": {"from": from_date, "to": to_date},
            },
            indent=2,
        )


def analyze_retention_insights(retention_curve: List[Dict]) -> Dict[str, any]:
    """Analyze retention curve to extract key insights."""
    if not retention_curve:
        return {}

    # Calculate average retention
    total_retention = sum(point["retention_rate"] for point in retention_curve)
    avg_retention = total_retention / len(retention_curve) if retention_curve else 0

    # Find major drop-off points (>5% drop)
    drop_offs = []
    for i in range(1, len(retention_curve)):
        drop = retention_curve[i - 1]["retention_rate"] - retention_curve[i]["retention_rate"]
        if drop > 5:
            drop_offs.append(
                {"percentile": retention_curve[i]["percentile"], "drop_percentage": round(drop, 2)}
            )

    # Find replay hotspots (high replay count)
    replay_hotspots = []
    for point in retention_curve:
        if point["replays"] > 0 and point["unique_users"] > 0:
            replay_ratio = point["replays"] / point["unique_users"]
            if replay_ratio > 0.2:  # 20% replay rate
                replay_hotspots.append(
                    {"percentile": point["percentile"], "replay_ratio": round(replay_ratio, 2)}
                )

    # Find 50% retention point
    fifty_percent_point = next(
        (p["percentile"] for p in retention_curve if p["retention_rate"] <= 50), 100
    )

    # Completion rate (viewers at 95%+)
    completion_rate = next(
        (p["retention_rate"] for p in retention_curve if p["percentile"] >= 95), 0
    )

    return {
        "avg_retention": round(avg_retention, 2),
        "fifty_percent_point": fifty_percent_point,
        "completion_rate": round(completion_rate, 2),
        "major_drop_offs": drop_offs[:5],  # Top 5 drop-off points
        "replay_hotspots": sorted(replay_hotspots, key=lambda x: x["replay_ratio"], reverse=True)[
            :5
        ],
        "engagement_score": round((avg_retention + completion_rate) / 2, 2),
    }


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
