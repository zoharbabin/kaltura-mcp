"""Simple prompts implementation for Kaltura MCP."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import mcp.types as types

from .kaltura_client import KalturaClientManager


@dataclass
class PromptDefinition:
    """Simple prompt definition."""

    name: str
    description: str
    arguments: List[types.PromptArgument]
    handler: Callable


class PromptsManager:
    """Manages MCP prompts with simple patterns."""

    def __init__(self):
        self.prompts: Dict[str, PromptDefinition] = {}

    def register(self, prompt: PromptDefinition) -> None:
        """Register a prompt."""
        self.prompts[prompt.name] = prompt

    def list_prompts(self) -> List[types.Prompt]:
        """List all prompts for MCP."""
        return [
            types.Prompt(name=p.name, description=p.description, arguments=p.arguments)
            for p in self.prompts.values()
        ]

    async def get_prompt(
        self, name: str, manager: KalturaClientManager, arguments: Optional[Dict[str, Any]] = None
    ) -> types.GetPromptResult:
        """Execute a prompt and return messages."""
        if name not in self.prompts:
            raise ValueError(f"Unknown prompt: {name}")

        prompt = self.prompts[name]
        messages = await prompt.handler(manager, arguments or {})
        return types.GetPromptResult(messages=messages)


# Global prompts manager
prompts_manager = PromptsManager()


# Analytics Wizard Prompt
async def analytics_wizard_handler(
    manager: KalturaClientManager, arguments: Dict[str, Any]
) -> List[types.PromptMessage]:
    """Generate analytics wizard workflow."""
    goal = arguments.get("analysis_goal", "performance").lower()
    time_period = arguments.get("time_period", "last_week")

    # Convert time period to dates
    today = datetime.now()
    date_map = {
        "today": (today, today),
        "yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "last_week": (today - timedelta(days=7), today),
        "last_month": (today - timedelta(days=30), today),
    }

    start, end = date_map.get(time_period, date_map["last_week"])
    from_date = start.strftime("%Y-%m-%d")
    to_date = end.strftime("%Y-%m-%d")

    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"I need to analyze {goal} for {time_period}. Please help me understand the data.",
            ),
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you analyze your content. Let me gather the relevant data.",
            ),
        ),
    ]

    # Add workflow based on goal
    if "performance" in goal or "video" in goal:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"First, use get_analytics with from_date='{from_date}', to_date='{to_date}', "
                    f"report_type='content' to see top performing videos. Then use get_analytics_timeseries "
                    f"to see trends over time.",
                ),
            )
        )
    elif "engagement" in goal:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Use get_analytics with from_date='{from_date}', to_date='{to_date}', "
                    f"report_type='user_engagement' to analyze how viewers interact with content.",
                ),
            )
        )
    elif "geographic" in goal:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Use get_geographic_breakdown with from_date='{from_date}', to_date='{to_date}' "
                    f"to see where your viewers are located.",
                ),
            )
        )
    else:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Analyze the data from {from_date} to {to_date} using appropriate analytics tools.",
                ),
            )
        )

    return messages


# Content Discovery Prompt
async def content_discovery_handler(
    manager: KalturaClientManager, arguments: Dict[str, Any]
) -> List[types.PromptMessage]:
    """Generate content discovery workflow."""
    intent = arguments.get("search_intent", "")
    include_details = arguments.get("include_details", "no").lower() == "yes"

    messages = [
        types.PromptMessage(
            role="user", content=types.TextContent(type="text", text=f"I'm looking for: {intent}")
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you find the content. Let me search based on your requirements.",
            ),
        ),
    ]

    # Determine search strategy
    if "caption" in intent.lower() or "transcript" in intent.lower():
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Use search_entries_intelligent with query='{intent}', search_type='caption', "
                    f"include_highlights=True to find content with matching captions.",
                ),
            )
        )
    elif "recent" in intent.lower() or "latest" in intent.lower():
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Use search_entries_intelligent with sort_field='created_at', sort_order='desc' "
                    "to find the most recent content.",
                ),
            )
        )
    else:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Use search_entries_intelligent with query='{intent}' to find matching content.",
                ),
            )
        )

    if include_details:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="For each result, also check for available captions using list_caption_assets.",
                ),
            )
        )

    return messages


# Accessibility Audit Prompt
async def accessibility_audit_handler(
    manager: KalturaClientManager, arguments: Dict[str, Any]
) -> List[types.PromptMessage]:
    """Generate accessibility audit workflow."""
    scope = arguments.get("audit_scope", "recent")

    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text", text=f"I need to audit {scope} for accessibility compliance."
            ),
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll help you check content for accessibility. This includes captions and metadata.",
            ),
        ),
    ]

    if scope == "all":
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="First, use search_entries_intelligent with media_type='video' to find all videos. "
                    "Then for each video, use list_caption_assets to check caption availability.",
                ),
            )
        )
    elif scope == "recent":
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Use search_entries_intelligent with sort_field='created_at', sort_order='desc', "
                    "max_results=20 to get recent videos. Then check each for captions.",
                ),
            )
        )
    elif scope.startswith("category:"):
        category = scope.replace("category:", "")
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Search for videos in category '{category}' and check their caption availability.",
                ),
            )
        )
    else:
        # Assume it's an entry ID
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Check entry {scope} for accessibility using get_media_entry and list_caption_assets.",
                ),
            )
        )

    return messages


# Retention Analysis Prompt
async def retention_analysis_handler(
    manager: KalturaClientManager, arguments: Dict[str, Any]
) -> List[types.PromptMessage]:
    """Generate comprehensive retention analysis workflow."""
    entry_id = arguments.get("entry_id", "")
    time_period = arguments.get("time_period", "12")
    output_format = arguments.get("output_format", "interactive").lower()

    # Calculate date range
    today = datetime.now()
    months = int(time_period) if time_period.isdigit() else 12
    start_date = today - timedelta(days=months * 30)
    from_date = start_date.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    messages = [
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Create an interactive retention-analysis report for video **{entry_id}** "
                f"using the last {months} months of viewer data.",
            ),
        ),
        types.PromptMessage(
            role="assistant",
            content=types.TextContent(
                type="text",
                text="I'll create an interactive visual retention analysis that shows engagement levels throughout the video. "
                "The visualization will include hover tooltips with content insights, helping you understand exactly "
                "what content works, why viewers engage or drop off, and how to optimize your videos. "
                "The X-axis will show video time (MM:SS format) for clear, actionable insights.",
            ),
        ),
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"First, use get_video_retention with entry_id='{entry_id}', "
                f"from_date='{from_date}', to_date='{to_date}' to get the retention data. "
                f"IMPORTANT: The data will include BOTH percentiles AND time values (time_seconds, time_formatted) already calculated.",
            ),
        ),
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text=f"Next, check for available content metadata:\n"
                f"1. Use list_caption_assets with entry_id='{entry_id}' to find transcripts\n"
                f"2. If captions exist, use get_caption_content to retrieve the transcript\n"
                f"3. Look for cue points and chapter markers in the video metadata",
            ),
        ),
        types.PromptMessage(
            role="user",
            content=types.TextContent(
                type="text",
                text="Now analyze the retention data to create an INTERACTIVE and VISUAL report:\n"
                "1. **Interactive Retention Graph** - CRITICAL REQUIREMENTS:\n"
                "   - X-axis: Use time_formatted (MM:SS) - video time, NOT percentiles!\n"
                "   - Y-axis: Engagement level (retention_percentage)\n"
                "   - Make it interactive with hover functionality showing:\n"
                "     • Exact time in video (MM:SS)\n"
                "     • Engagement percentage\n"
                "     • Number of viewers at that point\n"
                "     • Content insights: What's happening in the video at this moment\n"
                "     • Why engagement changed (if caption/transcript available)\n"
                "   - Color-code the line: Green (high engagement), Yellow (medium), Red (low)\n"
                "2. **Engagement Insights Table** - Interactive sections showing:\n"
                "   - Time ranges with significant changes\n"
                "   - What content corresponds to each section\n"
                "   - Performance analysis of that content\n"
                "3. **Content-Analytics Correlation** - Visual connections between:\n"
                "   - Specific content moments and their performance\n"
                "   - Topics/segments that drive engagement\n"
                "   - Areas where viewers replay or skip\n"
                "4. **Actionable Recommendations** - Based on the visual data:\n"
                "   - How to improve low-engagement sections\n"
                "   - What content patterns to replicate\n"
                "   - Optimal video structure based on retention patterns",
            ),
        ),
    ]

    if output_format == "interactive":
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Create an INTERACTIVE HTML visualization that includes:\n"
                    "**1. Main Interactive Graph:**\n"
                    "- Use a modern charting library (Chart.js, D3.js, or Plotly)\n"
                    "- X-axis: Video time from 00:00 to end (use time_formatted values)\n"
                    "- Y-axis: Engagement percentage (0-100%)\n"
                    "- Smooth line chart with data points\n"
                    "- Color gradient: Green (>80%), Yellow (50-80%), Red (<50%)\n"
                    "- Interactive hover tooltips showing:\n"
                    "  <div style='background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px;'>\n"
                    "    <strong>Time:</strong> MM:SS<br>\n"
                    "    <strong>Engagement:</strong> XX%<br>\n"
                    "    <strong>Viewers:</strong> XXX<br>\n"
                    "    <strong>Content:</strong> [What's happening at this moment]<br>\n"
                    "    <strong>Insight:</strong> [Why engagement changed]\n"
                    "  </div>\n"
                    "- Click on any point to seek video to that time (if embedded)\n\n"
                    "**2. Engagement Heatmap Timeline:**\n"
                    "- Visual bar below the graph showing engagement levels\n"
                    "- Colored segments corresponding to content sections\n"
                    "- Click to jump to detailed analysis of that section\n\n"
                    "**3. Interactive Insights Panel:**\n"
                    "- Synchronized with graph hover/click\n"
                    "- Shows content transcript/description for selected time\n"
                    "- Displays performance metrics for that segment\n"
                    "- Suggests improvements based on engagement data\n\n"
                    "**4. Smart Recommendations:**\n"
                    "- Clickable timestamps that highlight on the graph\n"
                    "- Visual indicators for replay hotspots and drop-off points\n"
                    "- Content optimization suggestions with examples\n\n"
                    "Make it beautiful, intuitive, and insightful - helping creators understand exactly how their content performs and why!",
                ),
            )
        )
    else:
        messages.append(
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text="Format the output as a structured markdown report with clear sections "
                    "and tables for easy reading and sharing.",
                ),
            )
        )

    return messages


# Register prompts
prompts_manager.register(
    PromptDefinition(
        name="analytics_wizard",
        description="Interactive guide for creating comprehensive analytics reports",
        arguments=[
            types.PromptArgument(
                name="analysis_goal",
                description="What to analyze: 'video performance', 'viewer engagement', 'geographic reach'",
                required=True,
            ),
            types.PromptArgument(
                name="time_period",
                description="Time period: 'today', 'yesterday', 'last_week', 'last_month'",
                required=True,
            ),
        ],
        handler=analytics_wizard_handler,
    )
)

prompts_manager.register(
    PromptDefinition(
        name="content_discovery",
        description="Natural language search assistant for finding media",
        arguments=[
            types.PromptArgument(
                name="search_intent",
                description="What you're looking for in natural language",
                required=True,
            ),
            types.PromptArgument(
                name="include_details",
                description="Include captions and attachments? (yes/no)",
                required=False,
            ),
        ],
        handler=content_discovery_handler,
    )
)

prompts_manager.register(
    PromptDefinition(
        name="accessibility_audit",
        description="Check content for accessibility compliance",
        arguments=[
            types.PromptArgument(
                name="audit_scope",
                description="Scope: 'all', 'recent', 'category:name', or entry_id",
                required=True,
            )
        ],
        handler=accessibility_audit_handler,
    )
)

prompts_manager.register(
    PromptDefinition(
        name="retention_analysis",
        description="Create interactive visual retention analysis with engagement insights, hover tooltips, and content-performance correlation",
        arguments=[
            types.PromptArgument(
                name="entry_id",
                description="Video entry ID to analyze (e.g., '1_3atosphg')",
                required=True,
            ),
            types.PromptArgument(
                name="time_period",
                description="Number of months of data to analyze (default: 12)",
                required=False,
            ),
            types.PromptArgument(
                name="output_format",
                description="Report format: 'interactive' (HTML) or 'markdown' (default: interactive)",
                required=False,
            ),
        ],
        handler=retention_analysis_handler,
    )
)
