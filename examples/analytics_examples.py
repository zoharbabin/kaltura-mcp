#!/usr/bin/env python3
"""
Kaltura Analytics Examples - Comprehensive guide to all report types

This file demonstrates how to use every available analytics report type
through the Kaltura MCP (Model Context Protocol) server.
"""

import asyncio
import json
from datetime import datetime, timedelta

# Example configuration
ENTRY_ID = "1_abc123"  # Replace with your video entry ID
FROM_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
TO_DATE = datetime.now().strftime("%Y-%m-%d")


# ============================================================================
# CONTENT PERFORMANCE EXAMPLES
# ============================================================================


async def example_engagement_timeline():
    """
    USER_ENGAGEMENT_TIMELINE (34) - Find most engaging video segments

    This report shows engagement throughout the video timeline, revealing:
    - Which parts get watched most
    - Which segments get replayed
    - Where viewers skip ahead
    """
    request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "engagement_timeline",
            "entry_id": ENTRY_ID,
            "limit": 100,
        },
    }

    # Expected response includes timeline data with:
    # - position: timestamp in video (seconds)
    # - views: number of views at this position
    # - replays: how many times this segment was replayed
    # - completion_rate: % of viewers who reached this point

    print("Finding most engaging moments in your video...")
    return request


async def example_content_dropoff():
    """
    CONTENT_DROPOFF (2) - Analyze where viewers stop watching

    Identifies problematic sections where viewers leave
    """
    request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "content_dropoff",
            "entry_id": ENTRY_ID,
        },
    }

    # Response shows retention curve with drop-off points
    return request


async def example_content_interactions():
    """
    CONTENT_INTERACTIONS (3) - Track user interactions

    Measures engagement features usage
    """
    request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "content_interactions",
            "entry_id": ENTRY_ID,
        },
    }

    # Shows likes, shares, comments, downloads per video
    return request


# ============================================================================
# USER ANALYTICS EXAMPLES
# ============================================================================


async def example_user_engagement():
    """
    USER_ENGAGEMENT (11) - Overall user behavior patterns
    """
    request = {
        "tool": "get_analytics",
        "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "user_engagement"},
    }

    # Returns user engagement metrics across all content
    return request


async def example_unique_users():
    """
    UNIQUE_USERS_PLAY (35) - Unique viewer analytics
    """
    request = {
        "tool": "get_analytics",
        "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "unique_users"},
    }

    # Shows unique viewer counts and growth trends
    return request


# ============================================================================
# GEOGRAPHIC ANALYTICS EXAMPLES
# ============================================================================


async def example_geographic_hierarchy():
    """
    Geographic reports at different granularity levels
    """
    # Country level
    country_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "geographic_country",
            "limit": 50,
        },
    }

    # Region/State level
    region_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "geographic_region",
            "limit": 50,
        },
    }

    # City level
    city_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "geographic_city",
            "limit": 100,
        },
    }

    return [country_request, region_request, city_request]


# ============================================================================
# PLATFORM & TECHNOLOGY EXAMPLES
# ============================================================================


async def example_platform_analysis():
    """
    Comprehensive platform and technology breakdown
    """
    requests = []

    # Device platforms (mobile, desktop, TV)
    requests.append(
        {
            "tool": "get_analytics",
            "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "platforms"},
        }
    )

    # Operating systems with versions
    requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "operating_system",
            },
        }
    )

    # OS families (Windows vs Mac vs Linux)
    requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "operating_system_families",
            },
        }
    )

    # Browser breakdown
    requests.append(
        {
            "tool": "get_analytics",
            "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "browsers"},
        }
    )

    return requests


# ============================================================================
# ADVANCED ANALYTICS EXAMPLES
# ============================================================================


async def example_playback_behavior():
    """
    Advanced playback analytics
    """
    # Playback speed preferences
    speed_request = {
        "tool": "get_analytics",
        "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "playback_rate"},
    }

    # Player control usage
    controls_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "player_interactions",
        },
    }

    return [speed_request, controls_request]


async def example_traffic_sources():
    """
    TOP_SOURCES (41) - Where your traffic comes from
    """
    request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "sources",
            "limit": 25,
        },
    }

    # Shows referrer domains, direct traffic, search engines
    return request


# ============================================================================
# CREATOR & CONTRIBUTOR EXAMPLES
# ============================================================================


async def example_creator_analytics():
    """
    Content creator performance metrics
    """
    # Top creators by performance
    creators_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "creators",
            "limit": 20,
        },
    }

    # Top content by specific creator
    creator_content_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "content_creator",
            "limit": 50,
        },
    }

    return [creators_request, creator_content_request]


# ============================================================================
# USAGE & INFRASTRUCTURE EXAMPLES
# ============================================================================


async def example_usage_reports():
    """
    Infrastructure and usage analytics
    """
    # Overall account usage
    usage_request = {
        "tool": "get_analytics",
        "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "partner_usage"},
    }

    # CDN bandwidth details
    cdn_request = {
        "tool": "get_analytics",
        "arguments": {"from_date": FROM_DATE, "to_date": TO_DATE, "report_type": "cdn_bandwidth"},
    }

    # Per-entry resource usage
    entry_usage_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "entry_usage",
            "entry_id": ENTRY_ID,
        },
    }

    return [usage_request, cdn_request, entry_usage_request]


# ============================================================================
# CATEGORY-BASED FILTERING EXAMPLE
# ============================================================================


async def example_category_analytics():
    """
    Filter any report by category
    """
    request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "content",
            "categories": "Training>Sales",  # Full category path
            "limit": 20,
        },
    }

    # Returns analytics filtered to specific category
    return request


# ============================================================================
# INTERACTIVE VIDEO EXAMPLES
# ============================================================================


async def example_interactive_video():
    """
    Interactive video element analytics
    """
    # Overall interactive video metrics
    interactive_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "interactive_video",
            "entry_id": ENTRY_ID,
        },
    }

    # Most visited interactive nodes/hotspots
    nodes_request = {
        "tool": "get_analytics",
        "arguments": {
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "report_type": "interactive_nodes",
            "entry_id": ENTRY_ID,
        },
    }

    return [interactive_request, nodes_request]


# ============================================================================
# COMBINED ANALYSIS EXAMPLE
# ============================================================================


async def comprehensive_video_analysis(entry_id: str):
    """
    Complete video performance analysis combining multiple reports
    """
    analysis_requests = []

    # 1. Overall performance
    analysis_requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "content",
                "entry_id": entry_id,
            },
        }
    )

    # 2. Engagement timeline - find most engaging moments
    analysis_requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "engagement_timeline",
                "entry_id": entry_id,
            },
        }
    )

    # 3. Drop-off analysis
    analysis_requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "content_dropoff",
                "entry_id": entry_id,
            },
        }
    )

    # 4. Geographic distribution
    analysis_requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "geographic_country",
                "entry_id": entry_id,
            },
        }
    )

    # 5. Platform breakdown
    analysis_requests.append(
        {
            "tool": "get_analytics",
            "arguments": {
                "from_date": FROM_DATE,
                "to_date": TO_DATE,
                "report_type": "platforms",
                "entry_id": entry_id,
            },
        }
    )

    return analysis_requests


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """
    Run example analytics requests
    """
    print("Kaltura Analytics Examples")
    print("=" * 50)

    # Example 1: Find most engaging video segments
    print("\n1. Engagement Timeline Analysis:")
    timeline_request = await example_engagement_timeline()
    print(json.dumps(timeline_request, indent=2))

    # Example 2: Geographic analysis
    print("\n2. Geographic Analytics:")
    geo_requests = await example_geographic_hierarchy()
    for req in geo_requests:
        print(f"  - {req['arguments']['report_type']}")

    # Example 3: Platform analysis
    print("\n3. Platform & Technology:")
    platform_requests = await example_platform_analysis()
    print(f"  - Analyzing {len(platform_requests)} platform dimensions")

    # Example 4: Comprehensive video analysis
    print("\n4. Complete Video Analysis:")
    video_analysis = await comprehensive_video_analysis(ENTRY_ID)
    print(f"  - Running {len(video_analysis)} reports for entry {ENTRY_ID}")

    print("\n" + "=" * 50)
    print("To run these examples through MCP:")
    print("1. Start the Kaltura MCP server")
    print("2. Send these requests through your MCP client")
    print("3. Analyze the returned JSON data")


if __name__ == "__main__":
    asyncio.run(main())
