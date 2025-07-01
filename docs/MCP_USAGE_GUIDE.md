# Kaltura MCP Usage Guide for LLMs

## Quick Tool Selection Guide

### Finding Content
- **First time exploring?** → `search_entries(query='*', sort_field='created_at', sort_order='desc')` to list newest videos
- **Looking for specific content?** → `search_entries(query='your keywords')`
- **Need video details?** → `get_media_entry(entry_id='1_abc123')`
- **Browse by category?** → `list_categories()` then filter searches

### Getting Analytics
1. **Always start with** → `list_analytics_capabilities()` when user asks about analytics
2. **For reports/tables** → `get_analytics()`
3. **For charts/graphs** → `get_analytics_timeseries()`
4. **For retention analysis** → `get_video_retention()`
5. **For live data** → `get_realtime_metrics()`

### Working with Media
- **Download video** → `get_download_url(entry_id='1_abc123')`
- **Get thumbnail** → `get_thumbnail_url(entry_id='1_abc123', width=400, height=300)`
- **Access captions** → `list_caption_assets(entry_id='1_abc123')` then `get_caption_content()`
- **Get attachments** → `list_attachment_assets(entry_id='1_abc123')` then `get_attachment_content()`

## Common Workflows

### Workflow 1: Find and Analyze Popular Content
```python
# 1. Find top videos
search_results = search_entries(query='*', sort_field='plays', sort_order='desc', max_results=10)

# 2. Get details for top video
video_details = get_media_entry(entry_id='1_abc123')

# 3. Analyze its performance
analytics = get_analytics(from_date='2024-01-01', to_date='2024-01-31', entry_id='1_abc123')

# 4. Check retention
retention = get_video_retention(entry_id='1_abc123')
```

### Workflow 2: Create Performance Dashboard
```python
# 1. Get overview metrics
platform_analytics = get_analytics(from_date='2024-01-01', to_date='2024-01-31')

# 2. Get trend data for charts
trends = get_analytics_timeseries(from_date='2024-01-01', to_date='2024-01-31', interval='days')

# 3. Check geographic distribution
geo_data = get_geographic_breakdown(from_date='2024-01-01', to_date='2024-01-31')

# 4. Monitor real-time
live_data = get_realtime_metrics()
```

### Workflow 3: Content Accessibility Check
```python
# 1. Find video
video = search_entries(query='training video')

# 2. Check for captions
captions = list_caption_assets(entry_id='1_abc123')

# 3. Download transcript if available
if captions:
    transcript = get_caption_content(caption_asset_id='1_xyz789')
```

## Key Patterns for Success

### 1. Always Provide Context
When showing results, explain what the data means:
- ❌ "Here's the data: {json}"
- ✅ "The video has been viewed 1,234 times with an average watch time of 5:32. Peak viewership was on January 15th."

### 2. Use Appropriate Date Ranges
- **Last 7 days**: Short-term trends, recent content
- **Last 30 days**: Standard reporting period
- **Last 90 days**: Quarterly analysis
- **Custom ranges**: Based on user's specific needs

### 3. Handle No Results Gracefully
- If search returns empty: "No videos found matching 'keyword'. Try broadening your search or use '*' to see all content."
- If no captions: "This video doesn't have captions available. Would you like me to check other videos?"

### 4. Suggest Next Steps
After each result, suggest logical follow-ups:
- After search: "Would you like details on any of these videos?"
- After analytics: "Would you like to see this data as a chart?"
- After retention: "The major drop-off at 25% suggests reviewing that section of the video."

## Parameter Tips

### Entry IDs
- Format: Always `'0_abc123'` or `'1_xyz789'` (number_alphanumeric)
- Get from: `search_entries()` results or `get_media_entry()`

### Dates
- Format: Always `'YYYY-MM-DD'` (e.g., `'2024-01-15'`)
- Default behavior: Most tools default to last 30 days if not specified

### Report Types
- Run `list_analytics_capabilities()` to see all 60+ options
- Common ones: `'content'`, `'user_engagement'`, `'geographic'`, `'platforms'`

### Sort Fields
- For newest content: `sort_field='created_at'`
- For most popular: `sort_field='plays'` or `sort_field='views'`
- For recently updated: `sort_field='updated_at'`

## Error Handling

Common errors and solutions:

1. **"Invalid entry_id"**: The video ID format is wrong or doesn't exist
   - Solution: Use `search_entries()` to find valid IDs

2. **"No data available"**: The date range has no analytics data
   - Solution: Try a different date range or check if content was published during that period

3. **"Permission denied"**: The user doesn't have access to this content
   - Solution: Try different content or check with administrator

## Best Practices

1. **Start broad, then narrow**: Use `search_entries(query='*')` to explore, then refine
2. **Chain tools logically**: Search → Get Details → Analyze → Take Action
3. **Batch related requests**: If analyzing multiple videos, gather all IDs first
4. **Cache repeated calls**: Analytics data updates hourly, so cache results when appropriate
5. **Provide examples**: When user is unclear, show them example queries

## Quick Reference Card

| Task | Tool | Key Parameters |
|------|------|----------------|
| List all videos | `search_entries` | `query='*'` |
| Find newest | `search_entries` | `query='*', sort_field='created_at', sort_order='desc'` |
| Search content | `search_entries` | `query='keywords'` |
| Video details | `get_media_entry` | `entry_id='1_abc123'` |
| Performance data | `get_analytics` | `from_date, to_date, report_type='content'` |
| Create charts | `get_analytics_timeseries` | `from_date, to_date, interval='days'` |
| Retention curve | `get_video_retention` | `entry_id='1_abc123'` |
| Live metrics | `get_realtime_metrics` | `report_type='viewers'` |
| Download video | `get_download_url` | `entry_id='1_abc123'` |
| Get thumbnail | `get_thumbnail_url` | `entry_id='1_abc123', width=400` |

Remember: When in doubt, start with `search_entries(query='*')` to see what's available!