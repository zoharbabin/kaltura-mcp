# Retention Analysis Prompt Example

This document demonstrates how an LLM (like Claude) would use the retention analysis prompt in the Kaltura MCP server.

## How the LLM Accesses the Prompt

### 1. Discovery Phase
When the LLM connects to the Kaltura MCP server, it can discover available prompts by calling the `list_prompts` function. The server will return:

```json
[
  {
    "name": "retention_analysis",
    "description": "Create comprehensive retention analysis report with visualizations and recommendations",
    "arguments": [
      {
        "name": "entry_id",
        "description": "Video entry ID to analyze (e.g., '1_3atosphg')",
        "required": true
      },
      {
        "name": "time_period",
        "description": "Number of months of data to analyze (default: 12)",
        "required": false
      },
      {
        "name": "output_format",
        "description": "Report format: 'interactive' (HTML) or 'markdown' (default: interactive)",
        "required": false
      }
    ]
  }
  // ... other prompts
]
```

### 2. Invocation Phase
When a user asks for a retention analysis, the LLM would invoke the prompt:

```json
{
  "method": "get_prompt",
  "params": {
    "name": "retention_analysis",
    "arguments": {
      "entry_id": "1_3atosphg",
      "time_period": "6",
      "output_format": "interactive"
    }
  }
}
```

### 3. Execution Phase
The server returns a structured conversation flow that guides the LLM through the analysis:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Create an interactive retention-analysis report for video **1_3atosphg** using the last 6 months of viewer data."
    },
    {
      "role": "assistant",
      "content": "I'll create a comprehensive retention analysis report with visualizations and recommendations. Let me gather all the necessary data."
    },
    {
      "role": "user",
      "content": "First, use get_video_retention with entry_id='1_3atosphg', from_date='2024-07-01', to_date='2025-01-01' to get the retention curve data. Then use get_media_entry with entry_id='1_3atosphg' to get video metadata including duration."
    },
    {
      "role": "user",
      "content": "Next, check for available content metadata:\n1. Use list_caption_assets with entry_id='1_3atosphg' to find transcripts\n2. If captions exist, use get_caption_content to retrieve the transcript\n3. Look for cue points and chapter markers in the video metadata"
    },
    {
      "role": "user",
      "content": "Now analyze the retention data to create:\n1. **Retention curve** - Convert percentiles to timestamps (hh:mm:ss format)\n2. **Drop-off table** - Identify 10-second windows with ≥5% retention loss\n3. **Content insights** - Correlate drop-offs with transcript/metadata\n4. **Recommendations** - Suggest edits, CTAs, and highlight clips"
    },
    {
      "role": "user",
      "content": "Format the output as an interactive HTML report with:\n- Hoverable retention curve showing insights in tooltips\n- Sortable drop-off table\n- Expandable recommendation sections\n- Embedded video player with timestamp links"
    }
  ]
}
```

## How the LLM Follows the Workflow

The LLM would then execute the suggested tools in sequence:

### Step 1: Get Retention Data
```python
# LLM calls get_video_retention
result = await get_video_retention(
    entry_id="1_3atosphg",
    from_date="2024-07-01",
    to_date="2025-01-01"
)
```

### Step 2: Get Video Metadata
```python
# LLM calls get_media_entry
metadata = await get_media_entry(entry_id="1_3atosphg")
# Extract duration to convert percentiles to timestamps
```

### Step 3: Check for Captions
```python
# LLM calls list_caption_assets
captions = await list_caption_assets(entry_id="1_3atosphg")
if captions:
    # Get transcript for content correlation
    transcript = await get_caption_content(caption_asset_id=captions[0].id)
```

### Step 4: Generate Report
The LLM would then:
1. Convert retention percentiles (0-100) to video timestamps using the duration
2. Identify drop-off points where retention decreases by ≥5%
3. Correlate drop-offs with transcript content
4. Generate recommendations based on patterns
5. Format everything as an interactive HTML report

## Example User Interaction

**User**: "Analyze the retention for video 1_3atosphg over the last 6 months and create an interactive report"

**Assistant**: "I'll analyze the retention data for video 1_3atosphg and create a comprehensive interactive report. Let me gather the data..."

[Assistant executes the workflow from the prompt]

**Assistant**: "Here's your retention analysis report:

### Video Retention Analysis Report
**Video ID**: 1_3atosphg  
**Analysis Period**: Last 6 months  
**Total Duration**: 12:34

#### Key Findings:
- Average retention: 68.5%
- Major drop-off at 02:15 (-8.3%)
- Highest engagement: 08:45-09:30
- 45% completion rate

[Interactive HTML visualization would be embedded here]

#### Recommendations:
1. **Edit Suggestion**: Consider trimming content at 02:10-02:30 where 8.3% of viewers drop off
2. **Highlight Reel**: Create a 2-minute clip from 08:45-10:45 (highest engagement)
3. **CTA Placement**: Add call-to-action at 11:30 before final drop-off

Would you like me to generate the highlight reel timestamps or analyze a different video?"

## Benefits of This Approach

1. **Structured Workflow**: The prompt ensures the LLM follows best practices
2. **Complete Analysis**: All necessary data is gathered systematically
3. **Flexible Output**: Supports both interactive and markdown formats
4. **Actionable Insights**: Delivers specific recommendations, not just data
5. **Reusable Pattern**: Users can easily analyze multiple videos

## Integration with MCP

This prompt template leverages MCP's prompt system to:
- **Reduce Complexity**: Users don't need to know the exact tool sequence
- **Ensure Consistency**: Every retention analysis follows the same thorough process
- **Enable Discovery**: LLMs can suggest this analysis when appropriate
- **Improve Results**: Structured workflow leads to better, more complete reports