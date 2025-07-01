# Enhanced Interactive Retention Analysis Prompt

## Overview

The `retention_analysis` prompt has been enhanced to create highly interactive, visual analytics that help content creators understand exactly how their videos perform and why.

## Key Enhancements

### 1. **Interactive Visualization Focus**
- Creates modern, interactive graphs with hover tooltips
- Shows engagement levels throughout the video timeline
- Provides instant insights on hover for any point in the video

### 2. **Content-Performance Correlation**
- Links specific video moments to their performance metrics
- Shows what's happening in the video at each engagement change
- Explains why viewers engage, replay, or drop off

### 3. **Visual Design Requirements**
The prompt now specifically requests:

#### Main Interactive Graph
- X-axis: Video time (MM:SS format) - never percentiles
- Y-axis: Engagement percentage (0-100%)
- Color-coded line: Green (>80%), Yellow (50-80%), Red (<50%)
- Interactive hover tooltips showing:
  - Exact time in video
  - Engagement percentage
  - Number of viewers
  - Content description at that moment
  - Insight about why engagement changed

#### Engagement Heatmap Timeline
- Visual bar showing engagement levels
- Colored segments for different content sections
- Clickable sections for detailed analysis

#### Interactive Insights Panel
- Synchronized with graph interactions
- Shows transcript/content for selected time
- Displays performance metrics
- Suggests improvements

#### Smart Recommendations
- Clickable timestamps
- Visual indicators for hotspots
- Content optimization suggestions

## Example Prompt Usage

```python
# Using the retention_analysis prompt
result = await prompts_manager.get_prompt(
    "retention_analysis",
    manager,
    {
        "entry_id": "1_3atosphg",
        "time_period": "12",  # Last 12 months
        "output_format": "interactive"  # HTML visualization
    }
)
```

## Expected Output

The LLM will create an interactive HTML visualization that includes:

1. **Beautiful Line Chart**
   - Smooth engagement curve over video time
   - Interactive hover effects
   - Color gradients indicating performance

2. **Rich Hover Tooltips**
   ```html
   <div class="tooltip">
     <strong>Time:</strong> 05:23<br>
     <strong>Engagement:</strong> 78%<br>
     <strong>Viewers:</strong> 234<br>
     <strong>Content:</strong> Introduction to main topic<br>
     <strong>Insight:</strong> Slight drop as viewers skip intro
   </div>
   ```

3. **Actionable Insights**
   - "At 05:23, 15% of viewers dropped off during the lengthy introduction"
   - "The segment from 10:15-12:30 has 45% replay rate - consider creating a clip"
   - "Engagement peaks at 23:45 when demonstrating the key feature"

## Benefits

1. **Visual Understanding**: Creators instantly see performance patterns
2. **Contextual Insights**: Know exactly what content works and why
3. **Actionable Recommendations**: Clear suggestions for improvement
4. **Interactive Exploration**: Dig deeper into specific moments
5. **Professional Presentation**: Beautiful, shareable reports

## Technical Implementation

The prompt ensures the LLM:
- Uses modern charting libraries (Chart.js, D3.js, Plotly)
- Creates responsive, mobile-friendly visualizations
- Includes proper error handling for missing data
- Provides fallback text descriptions for accessibility

## Integration with Video Players

When possible, the visualization can integrate with video players to:
- Seek to specific times on click
- Synchronize playback with graph highlighting
- Show real-time engagement as video plays

This enhanced prompt transforms raw retention data into a powerful tool for content optimization!