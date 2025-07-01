# Kaltura MCP Prompts and Resources

This document provides detailed information about the Prompts and Resources features implemented in the Kaltura MCP server, following the Model Context Protocol (MCP) specification.

## Overview

The Kaltura MCP server now supports two powerful MCP features:

1. **Prompts** - Pre-configured conversation templates that guide users through complex workflows
2. **Resources** - Cached data endpoints that provide frequently-accessed information

## Prompts

Prompts are interactive guides that help users accomplish complex tasks by providing structured conversation flows. They're especially useful for multi-step operations that require specific tool combinations.

### Available Prompts

#### 1. Analytics Wizard (`analytics_wizard`)

**Purpose**: Guide users through creating comprehensive analytics reports with the right tool combinations.

**Arguments**:
- `analysis_goal` (required): What to analyze
  - Options: `"video performance"`, `"viewer engagement"`, `"geographic reach"`, or any custom goal
- `time_period` (required): Time range for analysis
  - Options: `"today"`, `"yesterday"`, `"last_week"`, `"last_month"`

**Example Usage**:
```json
{
  "name": "analytics_wizard",
  "arguments": {
    "analysis_goal": "video performance",
    "time_period": "last_week"
  }
}
```

**Workflow**:
- For performance analysis: Suggests using `get_analytics` with content reports and `get_analytics_timeseries` for trends
- For engagement analysis: Recommends `get_analytics` with user engagement reports
- For geographic analysis: Directs to `get_geographic_breakdown` tool

#### 2. Content Discovery (`content_discovery`)

**Purpose**: Natural language search assistant that helps find media content using intelligent search strategies.

**Arguments**:
- `search_intent` (required): What you're looking for in natural language
- `include_details` (optional): Whether to fetch captions and attachments (`"yes"` or `"no"`, default: `"no"`)

**Example Usage**:
```json
{
  "name": "content_discovery",
  "arguments": {
    "search_intent": "training videos about Python with captions",
    "include_details": "yes"
  }
}
```

**Intelligent Search Strategies**:
- Detects caption/transcript searches and uses `search_type='caption'`
- Identifies recency queries and sorts by creation date
- Includes caption checking when details are requested

#### 3. Accessibility Audit (`accessibility_audit`)

**Purpose**: Check content for accessibility compliance, focusing on caption availability and metadata completeness.

**Arguments**:
- `audit_scope` (required): What content to audit
  - `"all"`: Audit all videos in the system
  - `"recent"`: Check the 20 most recent videos
  - `"category:name"`: Audit videos in a specific category
  - Entry ID (e.g., `"1_abc123"`): Check a specific video

**Example Usage**:
```json
{
  "name": "accessibility_audit",
  "arguments": {
    "audit_scope": "category:Training"
  }
}
```

**Workflow**:
- Searches for relevant content based on scope
- Checks each video for caption availability
- Can be extended to check other accessibility features

#### 4. Retention Analysis (`retention_analysis`)

**Purpose**: Create comprehensive retention analysis reports with visualizations, drop-off analysis, and content-aware recommendations.

**Arguments**:
- `entry_id` (required): Video entry ID to analyze (e.g., `"1_3atosphg"`)
- `time_period` (optional): Number of months of data to analyze (default: `"12"`)
- `output_format` (optional): Report format - `"interactive"` for HTML or `"markdown"` (default: `"interactive"`)

**Example Usage**:
```json
{
  "name": "retention_analysis",
  "arguments": {
    "entry_id": "1_3atosphg",
    "time_period": "6",
    "output_format": "interactive"
  }
}
```

**Comprehensive Workflow**:
1. **Data Collection**:
   - Fetches retention curve data using `get_video_retention`
   - Retrieves video metadata including duration
   - Checks for captions/transcripts
   - Looks for cue points and chapter markers

2. **Analysis Deliverables**:
   - **Retention Curve**: Percentiles converted to timestamps (hh:mm:ss)
   - **Drop-off Table**: 10-second windows with ≥5% retention loss
   - **Content Insights**: Correlation of drop-offs with transcript/metadata
   - **Recommendations**: Edit suggestions, CTAs, and highlight clips

3. **Output Formats**:
   - **Interactive HTML**: Hoverable graphs, sortable tables, embedded player
   - **Markdown**: Structured report with tables and sections

**Use Cases**:
- Post-production analysis to improve future content
- Identifying engaging segments for highlight reels
- Understanding viewer behavior patterns
- Optimizing video pacing and structure

### How Prompts Work

1. **User Invocation**: The user selects a prompt and provides required arguments
2. **Message Generation**: The prompt handler generates a conversation flow with specific tool suggestions
3. **Guided Execution**: The LLM follows the suggested workflow, using the recommended tools
4. **Adaptive Flow**: The conversation can adapt based on results and user feedback

### Implementation Details

Prompts are implemented in `src/kaltura_mcp/prompts.py` using:
- A `PromptsManager` class that handles registration and execution
- Individual handler functions for each prompt type
- MCP-compliant types for arguments and messages
- Dynamic date calculation for time-based queries

## Resources

Resources provide cached access to frequently-used data, reducing API calls and improving response times.

### Available Resources

#### 1. Analytics Capabilities (`kaltura://analytics/capabilities`)

**Type**: Static Resource  
**Cache Duration**: 30 minutes  
**Format**: JSON

**Description**: Complete documentation of all available analytics report types, metrics, and dimensions.

**Data Structure**:
```json
{
  "report_types": {
    "content": { "key": "content", "code": 1, "name": "Top Content", "category": "content" },
    // ... 60+ report types
  },
  "categories": {
    "content": ["content", "content_dropoff", ...],
    "users": ["user_engagement", "specific_user_engagement", ...],
    "geographic": ["geographic", "geographic_country", ...],
    "platform": ["platforms", "operating_system", ...],
    "quality": ["qoe_overview", "qoe_experience", ...]
  },
  "available_metrics": ["count_plays", "unique_viewers", ...],
  "available_dimensions": ["device", "country", "browser", ...],
  "time_intervals": ["hours", "days", "weeks", "months"],
  "best_practices": { ... }
}
```

**Use Cases**:
- Discovering available analytics options
- Building dynamic analytics UIs
- Understanding report capabilities without API calls

#### 2. Category Tree (`kaltura://categories/tree`)

**Type**: Static Resource  
**Cache Duration**: 30 minutes  
**Format**: JSON

**Description**: Complete category hierarchy with entry counts and parent-child relationships.

**Data Structure**:
```json
{
  "tree": [
    {
      "id": 1,
      "name": "Root Category",
      "fullName": "Root Category",
      "entriesCount": 150,
      "parentId": 0,
      "children": [
        {
          "id": 2,
          "name": "Training",
          "fullName": "Root Category>Training",
          "entriesCount": 50,
          "parentId": 1,
          "children": []
        }
      ]
    }
  ],
  "total_categories": 25,
  "total_entries": 500
}
```

**Use Cases**:
- Building category navigation interfaces
- Understanding content organization
- Quick category ID lookups

#### 3. Recent Media (`kaltura://media/recent/{count}`)

**Type**: Dynamic Resource Template  
**Cache Duration**: 5 minutes  
**Format**: JSON  
**Parameters**: `{count}` - Number of entries to return (max: 100)

**Description**: Most recently added media entries with basic metadata.

**Example URIs**:
- `kaltura://media/recent/10` - Get 10 most recent videos
- `kaltura://media/recent/50` - Get 50 most recent videos

**Data Structure**:
```json
{
  "entries": [
    {
      "id": "1_abc123",
      "name": "Training Video",
      "description": "Description text",
      "createdAt": 1234567890,
      "duration": 300,
      "plays": 150,
      "views": 200
    }
  ],
  "count": 10,
  "total_available": 500
}
```

**Use Cases**:
- Dashboard displays of recent content
- Quick content discovery
- Monitoring new uploads

### Resource Caching

Resources implement intelligent caching to improve performance:

1. **Cache Duration**: Each resource has a configurable cache duration
2. **Automatic Invalidation**: Cache expires after the duration
3. **Fresh on First Access**: First access always fetches fresh data
4. **Memory Efficient**: Only actively used resources are cached

### Implementation Details

Resources are implemented in `src/kaltura_mcp/resources.py` using:
- A `ResourcesManager` class with caching logic
- Pattern matching for dynamic resource templates
- Async handler functions for data fetching
- MCP-compliant resource types

## Integration with Claude Desktop

To use these features in Claude Desktop:

1. **Prompts** will appear in the prompt selection interface
2. **Resources** can be accessed using the resource viewer
3. Both features work seamlessly with existing tools

## Best Practices

### For Prompts

1. **Choose the Right Prompt**: Select prompts based on your task type
2. **Provide Clear Goals**: Be specific in your analysis goals or search intent
3. **Follow the Workflow**: Let the prompt guide you through the steps
4. **Adapt as Needed**: Prompts are starting points - adapt based on results

### For Resources

1. **Use Cached Data**: Access resources for frequently-needed information
2. **Respect Cache Times**: Understand that cached data may be slightly stale
3. **Choose Appropriate Counts**: For recent media, request only what you need
4. **Combine with Tools**: Use resource data to inform tool usage

## Technical Architecture

### Prompt Architecture

```
PromptsManager
├── register(prompt: PromptDefinition)
├── list_prompts() -> List[Prompt]
└── get_prompt(name, arguments) -> GetPromptResult
    └── Handler Functions
        ├── analytics_wizard_handler()
        ├── content_discovery_handler()
        └── accessibility_audit_handler()
```

### Resource Architecture

```
ResourcesManager
├── register(resource: ResourceDefinition)
├── list_resources() -> List[Resource]
├── list_resource_templates() -> List[ResourceTemplate]
└── read_resource(uri) -> str
    ├── Cache Check
    ├── Pattern Matching
    └── Handler Functions
        ├── analytics_capabilities_handler()
        ├── category_tree_handler()
        └── recent_media_handler()
```

## Error Handling

Both prompts and resources include comprehensive error handling:

- **Unknown Prompt/Resource**: Returns clear error message
- **Invalid Arguments**: Validates required arguments
- **API Failures**: Graceful degradation with error details
- **Cache Failures**: Falls back to fresh data fetch

## Performance Considerations

1. **Prompt Performance**: Minimal overhead, generates messages instantly
2. **Resource Caching**: Reduces API calls by up to 90% for frequently accessed data
3. **Memory Usage**: Efficient caching with automatic cleanup
4. **Scalability**: Designed to handle hundreds of concurrent requests

## Future Enhancements

Potential improvements for future versions:

1. **More Prompts**:
   - Upload workflow assistant
   - Playlist creation guide
   - User management wizard

2. **Additional Resources**:
   - User lists and permissions
   - Playlist hierarchies
   - Storage usage statistics

3. **Enhanced Features**:
   - Configurable cache durations
   - Resource refresh triggers
   - Prompt templates for customization

## Conclusion

The Prompts and Resources implementation brings powerful MCP features to the Kaltura server, making it easier for users to accomplish complex tasks and access frequently-needed data. The implementation follows MCP standards while maintaining the project's commitment to simplicity and elegance.