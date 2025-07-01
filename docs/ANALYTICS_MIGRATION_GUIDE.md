# Analytics Migration Guide

## Overview

This guide helps you migrate from the original analytics implementation to the new purpose-based Analytics V2 functions. The new approach makes it easier to discover and use the right analytics tool without needing to know specific report type codes.

## Key Changes

### 1. Purpose-Based Naming
Functions are now named based on what they do, not how they work:
- ❌ `get_analytics(report_type="percentiles")` 
- ✅ `get_video_retention()`

### 2. Simplified Parameters
Functions accept intuitive parameters instead of technical codes:
- ❌ `user_ids="Unknown"` for anonymous users
- ✅ `user_filter="anonymous"`

### 3. Enhanced Output Format
Results are formatted for immediate use:
- Retention data includes pre-calculated insights
- Time-series data is chart-ready
- Geographic data includes percentages and rankings

## Function Mapping

### Basic Analytics
```python
# OLD
result = await get_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    entry_id="1_abc",
    report_type="content"
)

# NEW - Same function, enhanced output
result = await get_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    entry_id="1_abc",
    report_type="content"
)
```

### Video Retention Analysis
```python
# OLD
result = await get_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    entry_id="1_abc",
    report_type="percentiles"
)
# Required manual parsing of percentiles data

# NEW
result = await get_video_retention(
    manager,
    entry_id="1_abc",
    from_date="2024-01-01",  # Optional, defaults to 30 days
    to_date="2024-01-31"     # Optional, defaults to today
)
# Returns parsed retention curve with insights
```

### Time-Series for Charts
```python
# OLD
result = await get_analytics_graph(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content"
)
# Returns {"graphs": [...]}

# NEW
result = await get_analytics_timeseries(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    report_type="content",
    interval="days"  # More explicit
)
# Returns {"series": [...], "metadata": {...}}
```

### Geographic Analysis
```python
# OLD
result = await get_geographic_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    level="country"
)

# NEW
result = await get_geographic_breakdown(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    granularity="country"  # More intuitive parameter name
)
# Includes percentages and top locations
```

### Real-time Metrics
```python
# OLD
result = await get_realtime_analytics(
    manager,
    report_type="realtime_users"
)

# NEW
result = await get_realtime_metrics(
    manager,
    report_type="viewers"  # User-friendly name
)
# Includes timestamp and trend data
```

### Quality Metrics
```python
# OLD
result = await get_qoe_analytics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    metric="qoe_overview"
)

# NEW
result = await get_quality_metrics(
    manager,
    from_date="2024-01-01",
    to_date="2024-01-31",
    metric_type="overview"  # Clearer parameter
)
# Includes quality score and recommendations
```

## Code Examples

### Before Migration
```python
# Complex video retention analysis
result = await get_analytics(
    manager,
    from_date=start_date,
    to_date=end_date,
    entry_id=video_id,
    report_type="percentiles"
)

# Manual parsing required
data = json.loads(result)
retention_data = []
for row in data["data"]:
    percentile = int(row.get("percentile", 0))
    viewers = int(row.get("count_viewers", 0))
    retention_data.append({
        "percentile": percentile,
        "viewers": viewers
    })

# Calculate retention rate manually
if retention_data and retention_data[1]["viewers"] > 0:
    for point in retention_data:
        point["retention_rate"] = (point["viewers"] / retention_data[1]["viewers"]) * 100
```

### After Migration
```python
# Simple video retention analysis
result = await get_video_retention(
    manager,
    entry_id=video_id,
    from_date=start_date,
    to_date=end_date
)

data = json.loads(result)
# Already includes:
# - Parsed retention curve
# - Calculated retention rates
# - Insights (avg retention, completion rate, drop-offs)
# - Video metadata
```

## Backward Compatibility

The original functions remain available for backward compatibility:
- `get_analytics()` - Enhanced with more report types
- `get_analytics_enhanced()` - Still available if needed
- `get_analytics_graph()` - Consider using `get_analytics_timeseries()`
- `get_video_timeline_analytics()` - Consider using `get_video_retention()`

## Step-by-Step Migration

1. **Identify Current Usage**
   ```bash
   # Search for analytics function calls
   grep -r "get_analytics\|get_.*_analytics" your_code/
   ```

2. **Update Imports**
   ```python
   # Add new functions to imports
   from kaltura_mcp.tools import (
       get_analytics,  # Keep existing
       get_analytics_timeseries,  # Add new
       get_video_retention,
       get_realtime_metrics,
       get_quality_metrics,
       get_geographic_breakdown
   )
   ```

3. **Replace Function Calls**
   - Start with visualization code → use `get_analytics_timeseries()`
   - Update retention analysis → use `get_video_retention()`
   - Modernize geographic reports → use `get_geographic_breakdown()`

4. **Update Parameter Names**
   - `level` → `granularity` (geographic)
   - `metric` → `metric_type` (quality)
   - Report type codes → user-friendly names

5. **Adapt Result Processing**
   - Remove manual parsing code
   - Use pre-calculated insights
   - Leverage enhanced formatting

## Common Patterns

### Dashboard Data
```python
# OLD: Multiple calls with manual aggregation
content_data = await get_analytics(manager, from_date, to_date, report_type="content")
user_data = await get_analytics(manager, from_date, to_date, report_type="user_engagement")
geo_data = await get_geographic_analytics(manager, from_date, to_date)

# NEW: Purpose-specific calls with better output
performance = await get_analytics(manager, from_date, to_date, report_type="content")
trends = await get_analytics_timeseries(manager, from_date, to_date, interval="days")
geography = await get_geographic_breakdown(manager, from_date, to_date)
```

### Video Analysis
```python
# OLD: Generic analytics with specific report type
data = await get_analytics(manager, from_date, to_date, 
                          entry_id=video_id, report_type="percentiles")

# NEW: Dedicated function with rich insights
retention = await get_video_retention(manager, entry_id=video_id)
# Includes drop-off analysis, replay detection, completion rates
```

### Live Monitoring
```python
# OLD: Technical report types
data = await get_analytics(manager, from_date, to_date, 
                          report_type="realtime_users")

# NEW: Intuitive function names
viewers = await get_realtime_metrics(manager, report_type="viewers")
# Includes timestamp, trends, and formatted data
```

## Benefits of Migration

1. **Better Discoverability** - Functions named by purpose
2. **Simplified Code** - Less manual parsing required
3. **Enhanced Features** - Additional insights and calculations
4. **Improved Maintenance** - Clearer intent in code
5. **LLM-Friendly** - AI assistants can better understand and suggest functions

## Troubleshooting

### Issue: Function not found
```python
# If you see: AttributeError: module has no attribute 'get_video_retention'
# Solution: Update imports
from kaltura_mcp.tools import get_video_retention
```

### Issue: Parameter errors
```python
# If you see: Unexpected keyword argument 'level'
# Solution: Check parameter names in new functions
# OLD: level="country"
# NEW: granularity="country"
```

### Issue: Different output format
```python
# If parsing fails on new output
# Solution: Check the enhanced format
data = json.loads(result)
print(json.dumps(data, indent=2))  # Inspect structure
```

## Need Help?

1. Run `list_analytics_capabilities()` to see all available functions
2. Check function docstrings for parameter details
3. Review examples in the [Analytics V2 Guide](ANALYTICS_V2_GUIDE.md)
4. Keep old code as reference during migration

Remember: The old functions still work, so you can migrate gradually!