# Retention Analysis with Time Conversion Example

This document demonstrates how the optimized retention analysis works with proper time conversion.

## Key Improvements

### 1. Enhanced `get_video_retention` Tool

The tool now automatically:
- Fetches video duration from metadata
- Converts percentiles to actual timestamps
- Provides both formats for maximum clarity

### 2. Example Output from `get_video_retention`

```json
{
  "video": {
    "id": "1_3atosphg",
    "title": "Introduction to Python Programming",
    "duration_seconds": 1200,
    "duration_formatted": "20:00"
  },
  "retention_data": [
    {
      "percentile": 0,
      "time_seconds": 0,
      "time_formatted": "00:00",
      "viewers": 1000,
      "unique_users": 1000,
      "retention_percentage": 100.0,
      "replays": 0
    },
    {
      "percentile": 10,
      "time_seconds": 120,
      "time_formatted": "02:00",
      "viewers": 850,
      "unique_users": 800,
      "retention_percentage": 85.0,
      "replays": 50
    },
    {
      "percentile": 25,
      "time_seconds": 300,
      "time_formatted": "05:00",
      "viewers": 650,
      "unique_users": 640,
      "retention_percentage": 65.0,
      "replays": 10
    },
    {
      "percentile": 50,
      "time_seconds": 600,
      "time_formatted": "10:00",
      "viewers": 450,
      "unique_users": 445,
      "retention_percentage": 45.0,
      "replays": 5
    }
  ],
  "insights": {
    "average_retention": 65.5,
    "completion_rate": 38.0,
    "fifty_percent_point": "08:30",
    "major_dropoffs": [
      {
        "time": "02:00",
        "time_seconds": 120,
        "percentile": 10,
        "retention_loss": 15.0
      },
      {
        "time": "05:00",
        "time_seconds": 300,
        "percentile": 25,
        "retention_loss": 20.0
      }
    ],
    "replay_hotspots": [
      {
        "time": "02:00",
        "time_seconds": 120,
        "percentile": 10,
        "replay_rate": 0.06
      }
    ]
  }
}
```

### 3. Optimized Prompt Instructions

The retention_analysis prompt now explicitly instructs:
- **X-axis MUST use time_formatted** (MM:SS format)
- **Never use percentiles on the X-axis**
- Data already includes time conversion
- All recommendations reference timestamps

### 4. Clear Graph Instructions

When the LLM creates the retention curve:
```
X-axis: Video time from 00:00 to 20:00
Y-axis: Retention percentage (0-100%)

Each data point plots:
- X: time_formatted (e.g., "02:00", "05:00", "10:00")
- Y: retention_percentage (e.g., 85.0, 65.0, 45.0)
```

## Benefits of This Approach

1. **No Confusion**: LLMs receive pre-calculated time values
2. **Accurate Visualization**: X-axis always shows actual video time
3. **Easy Correlation**: Drop-offs linked to specific moments in the video
4. **Better Insights**: "Users drop off at 2:00" vs "Users drop off at 10th percentile"

## Example LLM Response

With these improvements, the LLM will generate reports like:

**Retention Analysis for "Introduction to Python Programming"**

📊 **Retention Curve**
```
100% |•
     |  •
 85% |    •
     |      •
 65% |        •
     |          •
 45% |              •
     |________________•___
     0:00  5:00  10:00  15:00  20:00
           Video Time (MM:SS)
```

**Major Drop-offs:**
- **02:00** - 15% viewer loss (Introduction ends, main content begins)
- **05:00** - 20% viewer loss (Complex topic introduction)

**Recommendations:**
1. Add a preview at **01:45** to retain viewers before the 02:00 drop
2. Break down the complex topic at **04:45** with simpler examples
3. Consider adding chapter markers at **05:00**, **10:00**, and **15:00**

This clear time-based approach ensures that everyone understands exactly when events occur in the video!