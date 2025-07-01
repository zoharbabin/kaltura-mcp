# Analytics V2 Guide - Purpose-Based Analytics Functions

## Quick Decision Guide for LLMs

When a user asks about analytics, use this decision tree:

1. **"Show me analytics/metrics/performance"** → `get_analytics()` - Returns tables with detailed data
2. **"Create a chart/graph/visualization"** → `get_analytics_timeseries()` - Returns time-series data for charts  
3. **"Where do viewers drop off?"** → `get_video_retention()` - Returns 101-point retention curve
4. **"What's happening right now?"** → `get_realtime_metrics()` - Returns live data (updates every 30s)
5. **"Check streaming quality"** → `get_quality_metrics()` - Returns QoE scores and buffering rates
6. **"Where are viewers located?"** → `get_geographic_breakdown()` - Returns location-based analytics
7. **"What analytics can you do?"** → `list_analytics_capabilities()` - Returns all capabilities

### Common User Intents Mapped to Functions

| User Says | Use This Function | Example Call |
|-----------|-------------------|--------------|
| "Top 10 videos" | `get_analytics()` | `get_analytics(manager, from_date, to_date, report_type='content', limit=10)` |
| "Daily views trend" | `get_analytics_timeseries()` | `get_analytics_timeseries(manager, from_date, to_date, interval='days')` |
| "Video performance" | `get_analytics()` | `get_analytics(manager, from_date, to_date, entry_id='1_abc123')` |
| "Viewer retention" | `get_video_retention()` | `get_video_retention(manager, entry_id='1_abc123')` |
| "Live viewers" | `get_realtime_metrics()` | `get_realtime_metrics(manager, report_type='viewers')` |
| "Buffering issues" | `get_quality_metrics()` | `get_quality_metrics(manager, from_date, to_date, metric_type='stream')` |
| "Geographic data" | `get_geographic_breakdown()` | `get_geographic_breakdown(manager, from_date, to_date)` |

## Overview

The Analytics V2 module provides purpose-based functions that make it easy for both LLMs and developers to discover and use the right analytics tool for their needs. Instead of requiring knowledge of specific report types, you can now choose functions based on what you want to accomplish.

## Quick Start

```python
from kaltura_mcp.tools import (
    get_analytics,
    get_analytics_timeseries,
    get_video_retention,
    get_realtime_metrics,
    get_quality_metrics,
    get_geographic_breakdown,
    list_analytics_capabilities
)

# Discover what's available
capabilities = await list_analytics_capabilities(manager)

# Get performance rankings
analytics = await get_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content"
)

# Create a chart
timeseries = await get_analytics_timeseries(
    manager,
    from_date="2024-01-01", 
    to_date="2024-01-31",
    interval="days"
)

# Analyze viewer retention
retention = await get_video_retention(
    manager,
    entry_id="1_abc123"
)
```

## Function Reference

### 1. get_analytics()
**Purpose**: Comprehensive reporting and analysis  
**Use When**: You need detailed performance metrics, rankings, comparisons, or tabular data for export

```python
result = await get_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content",  # 60+ report types available
    entry_id=None,          # Optional: specific content
    user_id=None,           # Optional: specific user
    categories=None,        # Optional: filter by category
    dimension=None,         # Optional: group by dimension
    limit=50,               # Results per page
    page_index=1           # Pagination
)
```

**Common Report Types**:
- `content` - Top performing videos
- `user_engagement` - User behavior analysis
- `geographic` - Location distribution
- `platforms` - Device/platform breakdown
- `bandwidth` - Resource usage
- `partner_usage` - Account-level metrics

### 2. get_analytics_timeseries()
**Purpose**: Time-series data for visualization  
**Use When**: Creating charts, tracking trends, building dashboards, monitoring real-time metrics

#### When to Use Time-Series Data

Use `get_analytics_timeseries()` when you need to:

1. **Create Visual Dashboards**
   - Display metrics over time
   - Show trends and patterns
   - Build interactive charts

2. **Perform Trend Analysis**
   - Track performance changes
   - Identify peaks and valleys
   - Compare periods

3. **Generate Reports with Charts**
   - Executive summaries with visuals
   - Performance reports with graphs
   - Engagement analytics with timelines

4. **Monitor Real-time Metrics**
   - Live user activity graphs
   - QoS monitoring dashboards
   - Concurrent viewer charts

```python
result = await get_analytics_timeseries(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content",
    metrics=["plays", "views"],  # Optional: specific metrics
    entry_id=None,               # Optional: specific content
    interval="days",             # hours, days, weeks, months
    dimension=None               # Optional: grouping
)
```

**Returns**: Data formatted for direct use with charting libraries:
```json
{
    "series": [
        {
            "metric": "count_plays",
            "data": [
                {"date": "2024-01-01", "value": 150},
                {"date": "2024-01-02", "value": 175}
            ]
        }
    ],
    "metadata": {
        "interval": "days",
        "report_type": "content"
    }
}
```

#### Example Use Cases

**Content Performance Dashboard**
```python
# Get daily views and engagement for a video
graph_data = await get_analytics_timeseries(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content",
    entry_id="1_xyz123",
    interval="days"
)
```

**Platform Usage Trends**
```python
# Get monthly platform usage metrics
graph_data = await get_analytics_timeseries(
    manager,
    from_date="2024-01-01",
    to_date="2024-12-31",
    report_type="partner_usage",
    interval="months"
)
```

**User Engagement Timeline**
```python
# Get hourly engagement for live events
graph_data = await get_analytics_timeseries(
    manager,
    from_date="2024-01-15",
    to_date="2024-01-15",
    report_type="engagement_timeline",
    entry_id="1_live123",
    interval="hours"
)
```

#### Integration with Visualization Libraries

The time-series data format is designed to work seamlessly with popular visualization libraries:

**Chart.js**
```javascript
const chartData = {
  labels: graphData.series[0].data.map(d => d.date),
  datasets: graphData.series.map(series => ({
    label: series.metric,
    data: series.data.map(d => d.value)
  }))
};
```

**Plotly**
```python
traces = []
for series in graph_data["series"]:
    trace = {
        "x": [p["date"] for p in series["data"]],
        "y": [p["value"] for p in series["data"]],
        "name": series["metric"]
    }
    traces.append(trace)
```

**D3.js**
```javascript
const data = graphData.series[0].data.map(d => ({
  date: new Date(d.date),
  value: d.value
}));
```

#### Common Metrics by Report Type

**Content Reports**
- `count_plays` - Play count
- `sum_time_viewed` - Total watch time
- `avg_time_viewed` - Average watch time
- `count_loads` - Page loads
- `unique_viewers` - Unique viewers
- `avg_completion_rate` - Completion rate

**User Reports**
- `unique_known_users` - Logged-in users
- `sum_time_viewed` - Total viewing time
- `avg_view_drop_off` - Drop-off rate
- `count_plays` - Total plays

**Geographic Reports**
- `count_plays` - Plays by location
- `unique_viewers` - Viewers by location
- `avg_time_viewed` - Watch time by location

**QoE Reports**
- `buffer_time` - Buffering duration
- `avg_bitrate` - Average bitrate
- `error_rate` - Error percentage
- `join_time` - Time to start playback

#### Best Practices

1. **Choose the Right Interval**
   - Use "days" for monthly reports
   - Use "hours" for daily reports
   - Use "months" for yearly reports

2. **Optimize Date Ranges**
   - Limit to necessary time periods
   - Consider data point density

3. **Handle Missing Data**
   - Graph data includes zeros for missing periods
   - Consider interpolation for smoother charts

4. **Combine with Table Data**
   - Use time-series data for visualization
   - Use get_analytics() for detailed analysis

### 3. get_video_retention()
**Purpose**: Detailed viewer retention analysis  
**Use When**: Optimizing content, finding drop-off points, identifying engaging segments

#### Overview

The Video Retention feature provides granular, frame-by-frame retention data for individual videos using Kaltura's PERCENTILES report. This powerful analytics tool helps you understand exactly how viewers engage with your content throughout its duration.

#### When to Use Video Retention Analysis

Use `get_video_retention()` when you need to:

1. **Analyze Viewer Retention**
   - See exactly where viewers drop off within a video
   - Identify the "cliff moments" that cause mass exits
   - Track completion rates with precision

2. **Detect Replay Patterns**
   - Find segments viewers watch multiple times
   - Identify confusing or highly engaging content
   - Optimize content based on replay behavior

3. **Compare Audience Segments**
   - Anonymous vs. logged-in viewer behavior
   - Different user cohorts' viewing patterns
   - A/B test content variations

4. **Optimize Video Content**
   - Trim unnecessary intro/outro segments
   - Restructure content based on retention data
   - Place key information at optimal points

```python
result = await get_video_retention(
    manager,
    entry_id="1_abc123",        # Required: video to analyze
    from_date=None,             # Optional: defaults to 30 days
    to_date=None,               # Optional: defaults to today
    user_filter=None,           # Optional: segment analysis
    compare_segments=False      # Compare filtered vs all
)
```

**User Filter Options**:
- `None` - All viewers (default)
- `"anonymous"` - Non-logged-in viewers only
- `"registered"` - Logged-in viewers only
- `"user@email.com"` - Specific user
- `"cohort:premium"` - Named user cohort
- `"Unknown"` - Anonymous viewers (alternative)
- Comma-separated emails for multiple users

**Returns**: 101-point retention curve with insights:
```json
{
    "video": {
        "id": "1_abc123",
        "title": "Product Demo"
    },
    "retention_curve": [
        {"percent": 0, "retention": 100.0, "viewers": 1000},
        {"percent": 25, "retention": 75.0, "viewers": 750},
        {"percent": 50, "retention": 55.0, "viewers": 550}
    ],
    "insights": {
        "average_retention": 65.5,
        "completion_rate": 42.0,
        "major_dropoffs": [
            {"percent": 25, "loss": 15.0}
        ],
        "replay_segments": [
            {"percent": 45, "replay_rate": 0.35}
        ]
    }
}
```

#### Key Concepts

**Percentiles**
- The video is divided into 101 equal segments (0-100%)
- Each percentile represents 1% of the video duration
- Data shows how many viewers reached each point

**Metrics Explained**
- **count_viewers**: Total playback events at this point (includes replays)
- **unique_known_users**: Distinct logged-in users who reached this point
- **replay_count**: Difference between total views and unique users
- **retention_rate**: Percentage of initial viewers still watching

#### Usage Examples

**Basic Retention Curve**
```python
# Get retention data for a single video
result = await get_video_retention(
    manager,
    entry_id="1_abc123"
)
```

**Anonymous vs. Logged-in Comparison**
```python
# Compare anonymous viewers to all viewers
result = await get_video_retention(
    manager,
    entry_id="1_abc123",
    user_filter="anonymous",
    compare_segments=True
)
```

**Specific User Analysis**
```python
# Analyze viewing pattern for a specific user
result = await get_video_retention(
    manager,
    entry_id="1_abc123",
    user_filter="john.doe@example.com"
)
```

**Multiple User Cohort**
```python
# Analyze a group of users (e.g., premium subscribers)
result = await get_video_retention(
    manager,
    entry_id="1_abc123",
    user_filter="user1@example.com,user2@example.com,user3@example.com"
)
```

#### Common Patterns & What They Mean

**The "J-Curve"**
- Sharp initial drop (0-5%)
- Steady decline (5-90%)
- Slight uptick at end (90-100%)
- **Meaning**: Normal pattern, viewers sample then commit

**The "Cliff"**
- Sudden massive drop at specific point
- **Meaning**: Content issue, ad placement, or topic change

**The "Sawtooth"**
- Multiple spikes and drops
- **Meaning**: Chaptered content or varying engagement

**The "Plateau"**
- Flat retention after initial drop
- **Meaning**: Highly engaged core audience

#### Visualization Recipes

**Standard Retention Curve**
```javascript
// Using Chart.js
const data = {
    labels: retentionCurve.map(p => `${p.percent}%`),
    datasets: [{
        label: 'Viewer Retention',
        data: retentionCurve.map(p => p.retention),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
};
```

**Drop-off Heatmap**
```python
# Highlight major drop-off points
drop_offs = insights["major_dropoffs"]
# Mark these points on your visualization with red indicators
```

**Replay Intensity Chart**
```javascript
// Show replay patterns
const replayData = retentionCurve.map(p => ({
    x: p.percent,
    y: p.replay_rate
}));
```

#### Best Practices

1. **Date Range Selection**
   - Use 30+ days for statistical significance
   - Recent 7 days for trending content
   - Full history for evergreen analysis

2. **Cohort Comparison**
   ```python
   # Always compare to baseline
   baseline = await get_video_retention(manager, entry_id="1_abc")
   test_cohort = await get_video_retention(manager, entry_id="1_abc", user_filter="test_group")
   ```

3. **Action Thresholds**
   - **>10% single drop**: Investigate content at that point
   - **<50% completion**: Consider video length/structure
   - **>30% replay ratio**: Extract and highlight that segment

4. **Combining with Other Data**
   ```python
   # Combine with standard analytics
   retention = await get_video_retention(manager, entry_id="1_abc")
   overview = await get_analytics(manager, report_type="content", entry_id="1_abc")
   # Correlate retention with overall performance
   ```

#### Prompt Examples for LLMs

**Analysis Prompts**
- "Show me the retention curve for video 1_abc123"
- "Where do viewers drop off in our product demo video?"
- "Find replay hotspots in our tutorial video"
- "Compare anonymous vs logged-in retention for video 1_xyz"

**Optimization Prompts**
- "Analyze why viewers leave at the 3-minute mark"
- "Suggest edit points based on retention data"
- "Identify the most engaging segments to create highlights"
- "Show me which parts of the video get replayed most"

**Reporting Prompts**
- "Create a retention report for our top 5 videos"
- "Generate insights on viewer behavior patterns"
- "Build a dashboard showing video performance metrics"
- "Compare this week's videos to last week's retention"

#### Technical Notes

**Performance**
- Each call returns exactly 101 data points
- Fast response time (<1s typically)
- Can batch multiple videos via parallel calls

**Limitations**
- Requires ADMIN-type KS (session)
- One video per API call
- 24-hour delay for analytics processing
- Minimum view threshold may apply

**Error Handling**
```python
if "error" in result:
    if "SERVICE_FORBIDDEN" in result["error"]:
        # KS permission issue
    elif "zero data" in result["error"]:
        # No analytics yet (too recent or no views)
```

### 4. get_realtime_metrics()
**Purpose**: Live analytics data  
**Use When**: Monitoring live events, real-time dashboards, immediate feedback

```python
result = await get_realtime_metrics(
    manager,
    report_type="viewers",      # viewers, geographic, quality
    entry_id=None              # Optional: specific content
)
```

**Report Types**:
- `viewers` - Current active viewers
- `geographic` - Live viewer locations
- `quality` - Real-time streaming quality

### 5. get_quality_metrics()
**Purpose**: Quality of Experience (QoE) analysis  
**Use When**: Monitoring streaming performance, troubleshooting issues

```python
result = await get_quality_metrics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    metric_type="overview",     # overview, experience, stream, errors
    entry_id=None,             # Optional: specific content
    dimension=None             # Optional: device, geography
)
```

**Metric Types**:
- `overview` - General quality summary
- `experience` - User experience metrics
- `engagement` - Quality impact on engagement
- `stream` - Technical streaming metrics
- `errors` - Error tracking and analysis

### 6. get_geographic_breakdown()
**Purpose**: Location-based analytics  
**Use When**: Understanding global reach, regional strategies, market analysis

```python
result = await get_geographic_breakdown(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    granularity="country",      # world, country, region, city
    region_filter=None,         # Optional: filter region
    metrics=None               # Optional: specific metrics
)
```

**Granularity Levels**:
- `world` - Global overview
- `country` - Country-level breakdown
- `region` - State/province level (requires region_filter)
- `city` - City-level detail (requires region_filter)

### 7. list_analytics_capabilities()
**Purpose**: Discover available analytics functions  
**Use When**: Learning the system, finding the right tool

```python
result = await list_analytics_capabilities(manager)
```

## Common Use Cases

### 1. Content Performance Dashboard
```python
# Get current metrics
analytics = await get_analytics(
    manager, from_date, to_date, 
    report_type="content", limit=10
)

# Get trend data for top video
top_video = analytics["data"][0]["entry_id"]
trends = await get_analytics_timeseries(
    manager, from_date, to_date,
    entry_id=top_video, interval="days"
)

# Get retention analysis
retention = await get_video_retention(
    manager, entry_id=top_video
)
```

### 2. Live Event Monitoring
```python
# Real-time viewers
viewers = await get_realtime_metrics(
    manager, report_type="viewers", 
    entry_id="1_live_event"
)

# Geographic distribution
geo = await get_realtime_metrics(
    manager, report_type="geographic",
    entry_id="1_live_event"
)

# Quality monitoring
quality = await get_realtime_metrics(
    manager, report_type="quality",
    entry_id="1_live_event"
)
```

### 3. User Segment Analysis
```python
# Compare anonymous vs registered retention
anon_retention = await get_video_retention(
    manager, entry_id="1_abc",
    user_filter="anonymous"
)

reg_retention = await get_video_retention(
    manager, entry_id="1_abc",
    user_filter="registered"
)

# Or compare in one call
comparison = await get_video_retention(
    manager, entry_id="1_abc",
    user_filter="anonymous",
    compare_segments=True
)
```

### 4. Regional Content Strategy
```python
# Country breakdown
countries = await get_geographic_breakdown(
    manager, from_date, to_date,
    granularity="country"
)

# US state analysis
us_states = await get_geographic_breakdown(
    manager, from_date, to_date,
    granularity="region",
    region_filter="US"
)

# California cities
ca_cities = await get_geographic_breakdown(
    manager, from_date, to_date,
    granularity="city",
    region_filter="US-CA"
)
```

## Best Practices

1. **Start with list_analytics_capabilities()** to understand available options
2. **Use get_analytics()** for detailed reports and exports
3. **Use get_analytics_timeseries()** for visualizations
4. **Use get_video_retention()** for content optimization
5. **Cache results** when appropriate - most data updates hourly
6. **Use pagination** for large result sets
7. **Specify dimensions** to get more granular insights

## Error Handling

All functions return JSON with consistent error format:
```json
{
    "error": "Error message",
    "details": "Additional context",
    "suggestion": "How to fix"
}
```

Common errors:
- Invalid date format - Use YYYY-MM-DD
- Invalid entry ID - Check format (e.g., "1_abc123")
- Missing permissions - Ensure analytics access is enabled
- Report type not found - Check available types

## Performance Tips

1. **Batch requests** when possible
2. **Use appropriate intervals** - don't request hourly data for year-long ranges
3. **Leverage caching** - most reports update hourly
4. **Use pagination** for large datasets
5. **Request only needed metrics** to reduce payload size

## Support

For issues or questions:
- Check `list_analytics_capabilities()` for available options
- Ensure your Kaltura account has analytics enabled
- Verify API permissions include report access
- Review error messages for specific guidance