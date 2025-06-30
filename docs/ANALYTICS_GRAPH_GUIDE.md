# Kaltura Analytics Graph Data Guide

## When to Use Graph Data

The Kaltura MCP provides specialized graph data functionality (`get_analytics_graph`) that returns time-series data optimized for visualization. This guide explains when and how to use graph data versus table data.

## Key Differences

### Table Data (`get_analytics` / `get_analytics_enhanced`)
- Returns data in tabular format (rows and columns)
- Best for detailed reports and data analysis
- Includes all available fields and dimensions
- Suitable for export to spreadsheets

### Graph Data (`get_analytics_graph`)
- Returns time-series data with date/value pairs
- Optimized for creating charts and visualizations
- Multiple metrics returned as separate series
- Includes summary totals for the period
- Perfect for dashboards and trend analysis

## When to Use Graph Data

Use `get_analytics_graph` when you need to:

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

## Example Use Cases

### 1. Content Performance Dashboard
```python
# Get daily views and engagement for a video
graph_data = await get_analytics_graph(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content",
    entry_id="1_xyz123",
    interval="days"
)
```

Returns:
- `count_plays` - Daily play counts
- `sum_time_viewed` - Total watch time per day
- `avg_time_viewed` - Average view duration
- `unique_viewers` - Unique viewers per day
- `avg_completion_rate` - Completion rates

### 2. Platform Usage Trends
```python
# Get monthly platform usage metrics
graph_data = await get_analytics_graph(
    manager,
    from_date="2024-01-01",
    to_date="2024-12-31",
    report_type="partner_usage",
    interval="months"
)
```

Returns:
- `bandwidth_consumption` - Monthly bandwidth usage
- `storage_added` - Storage growth over time
- `transcoding_consumption` - Transcoding usage trends

### 3. User Engagement Timeline
```python
# Get hourly engagement for live events
graph_data = await get_analytics_graph(
    manager,
    from_date="2024-01-15",
    to_date="2024-01-15",
    report_type="engagement_timeline",
    entry_id="1_live123",
    interval="hours"
)
```

Returns:
- Viewer engagement throughout the event
- Peak concurrent viewers
- Drop-off points

## Response Format

The graph data response includes:

```json
{
  "reportType": "Top Content",
  "reportTypeCode": "content",
  "dateRange": {
    "from": "2024-01-01",
    "to": "2024-01-31",
    "interval": "days"
  },
  "graphs": [
    {
      "metric": "count_plays",
      "data": [
        {"date": "2024-01-01", "value": 150},
        {"date": "2024-01-02", "value": 200},
        // ... more data points
      ]
    },
    {
      "metric": "avg_time_viewed",
      "data": [
        {"date": "2024-01-01", "value": 45.5},
        {"date": "2024-01-02", "value": 52.3},
        // ... more data points
      ]
    }
  ],
  "summary": {
    "total_plays": 5430,
    "avg_time_viewed": 48.5,
    "unique_viewers": 1832
  }
}
```

## Integration with Visualization Libraries

The graph data format is designed to work seamlessly with popular visualization libraries:

### Chart.js
```javascript
const chartData = {
  labels: graphData.graphs[0].data.map(d => d.date),
  datasets: graphData.graphs.map(graph => ({
    label: graph.metric,
    data: graph.data.map(d => d.value)
  }))
};
```

### Plotly
```python
traces = []
for graph in graph_data["graphs"]:
    trace = {
        "x": [p["date"] for p in graph["data"]],
        "y": [p["value"] for p in graph["data"]],
        "name": graph["metric"]
    }
    traces.append(trace)
```

### D3.js
```javascript
const data = graphData.graphs[0].data.map(d => ({
  date: new Date(d.date),
  value: d.value
}));
```

## Best Practices

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
   - Use graph data for visualization
   - Use table data for detailed analysis

## Common Metrics by Report Type

### Content Reports
- `count_plays` - Play count
- `sum_time_viewed` - Total watch time
- `avg_time_viewed` - Average watch time
- `count_loads` - Page loads
- `unique_viewers` - Unique viewers
- `avg_completion_rate` - Completion rate

### User Reports
- `unique_known_users` - Logged-in users
- `sum_time_viewed` - Total viewing time
- `avg_view_drop_off` - Drop-off rate
- `count_plays` - Total plays

### Geographic Reports
- `count_plays` - Plays by location
- `unique_viewers` - Viewers by location
- `avg_time_viewed` - Watch time by location

### QoE Reports
- `buffer_time` - Buffering duration
- `avg_bitrate` - Average bitrate
- `error_rate` - Error percentage
- `join_time` - Time to start playback

## Examples

See `/examples/analytics_graph_visualization.py` for complete examples of:
- Retrieving graph data
- Formatting for different chart libraries
- Creating HTML dashboards
- Handling real-time updates