# How retention_percentage is Calculated

## Summary

**The `retention_percentage` is calculated by the MCP code, NOT retrieved from Kaltura API.**

## Data Flow

### 1. What Kaltura API Provides

The Kaltura Analytics API returns raw data in this format for the "percentiles" report:
```
Header: percentile,count_viewers,unique_known_users
Data: 
0,100,100
10,85,80
25,65,60
50,45,40
75,30,28
100,20,20
```

This data contains:
- **percentile**: Video progress point (0-100)
- **count_viewers**: Total number of views at that point
- **unique_known_users**: Number of unique users at that point

### 2. MCP Calculation

The MCP code calculates `retention_percentage` in `src/kaltura_mcp/tools/analytics.py`:

```python
# Two-pass approach to handle edge cases

# First pass: collect all data and find max viewers
max_viewers = max((p["viewers"] for p in raw_data_points), default=0)

# Determine initial reference point
initial_viewers = 0
for point in raw_data_points:
    if point["percentile"] == 0 and point["viewers"] > 0:
        initial_viewers = point["viewers"]
        break

if initial_viewers == 0:
    # No viewers at start, use max viewers as reference
    initial_viewers = max_viewers

# Second pass: calculate retention
retention_pct = (viewers / initial_viewers * 100) if initial_viewers > 0 else 0
```

### 3. Formula

```
retention_percentage = (current_viewers / initial_viewers) × 100
```

Where:
- `current_viewers` = viewers at the current percentile
- `initial_viewers` = one of:
  - Viewers at percentile 0 (if > 0), OR
  - Maximum viewers across all percentiles (if percentile 0 has 0 viewers)

### 4. Example Calculations

#### Normal Case (viewers at start):
```
0,100,100    # Start: 100 viewers
10,85,80     # 10%: 85 viewers
50,45,40     # 50%: 45 viewers
```

MCP calculates:
- Initial viewers = 100 (from percentile 0)
- At 0%: retention = (100/100) × 100 = **100%**
- At 10%: retention = (85/100) × 100 = **85%**
- At 50%: retention = (45/100) × 100 = **45%**

#### Edge Case (no viewers at start):
```
0,0,0        # Start: 0 viewers
3,22,2       # 3%: 22 viewers (peak)
10,17,1      # 10%: 17 viewers
50,6,1       # 50%: 6 viewers
```

MCP calculates:
- Initial viewers = 22 (max viewers, since percentile 0 has 0)
- At 0%: retention = (0/22) × 100 = **0%**
- At 3%: retention = (22/22) × 100 = **100%** (peak)
- At 10%: retention = (17/22) × 100 = **77.3%**
- At 50%: retention = (6/22) × 100 = **27.3%**

## Why Calculate It?

1. **Normalized View**: Always shows retention relative to the starting audience
2. **Easy Interpretation**: 100% means everyone is still watching, 50% means half dropped off
3. **Consistent Baseline**: Makes it easy to compare videos with different view counts

## Additional Calculations

The MCP also calculates:
- **replays**: `viewers - unique_users` (how many times content was replayed)
- **time_seconds**: Converts percentile to actual video time
- **time_formatted**: Human-readable time format (MM:SS)

## Benefits

This approach provides:
- Clear percentage-based retention metrics
- Easy-to-understand drop-off rates
- Consistent comparison across videos
- Actionable insights for content optimization