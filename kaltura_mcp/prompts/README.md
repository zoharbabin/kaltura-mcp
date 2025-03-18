# Intelligent Prompting Library for Kaltura-MCP Server

This directory contains the intelligent prompting library for the Kaltura-MCP Server. The library provides a set of prompts for common Kaltura workflows and tasks, designed to be used with Large Language Models (LLMs).

## Overview

The intelligent prompting library is designed to help LLMs interact with the Kaltura-MCP Server effectively. It provides structured prompts for various tasks, including:

- Content workflow automation (moderation, tagging, categorization, distribution)
- Content enrichment (summaries, descriptions, subtitles, translations)
- User management (role assignment, permission management, activity analysis)
- Reporting and analytics (trend identification, recommendation generation)
- API exploration and learning (API discovery)

## Structure

The library is organized into the following components:

- `base.py`: Base prompt class with common functionality
- `content_workflow.py`: Prompts for content workflow automation
- `content_enrichment.py`: Prompts for content enrichment
- `user_management.py`: Prompts for user management
- `reporting.py`: Prompts for reporting and analytics
- `api_exploration.py`: Prompts for API exploration and learning

## Usage

### Basic Usage

```python
from kaltura_mcp.prompts import ContentWorkflowPrompts

# Create a moderation review prompt
prompt = ContentWorkflowPrompts.moderation_review()

# Format the user message with specific parameters
user_message = prompt.format_user_message(
    title="My Video",
    description="This is my video description",
    tags="tag1, tag2, tag3",
    duration=120,
    user_id="user123",
    category_name="Education",
    additional_context="This is a new upload"
)

# Get the system message
system_message = prompt.system_message

# Use the prompt with an LLM
# (implementation depends on the LLM client you're using)
```

### Serialization

Prompts can be serialized to and deserialized from JSON or YAML:

```python
from kaltura_mcp.prompts import ContentWorkflowPrompts

# Create a prompt
prompt = ContentWorkflowPrompts.moderation_review()

# Serialize to JSON
json_str = prompt.to_json()

# Serialize to YAML
yaml_str = prompt.to_yaml()

# Deserialize from JSON
from kaltura_mcp.prompts.base import BasePrompt
prompt_from_json = BasePrompt.from_json(json_str)

# Deserialize from YAML
prompt_from_yaml = BasePrompt.from_yaml(yaml_str)
```

### Creating Custom Prompts

You can create custom prompts by extending the `BasePrompt` class:

```python
from kaltura_mcp.prompts.base import BasePrompt

# Create a custom prompt
prompt = BasePrompt(
    name="my_custom_prompt",
    description="My custom prompt description"
)

# Set the system message
prompt.set_system_message("You are a helpful assistant...")

# Set the user message template
prompt.set_user_message_template("Please help me with {task}...")

# Add an example
prompt.add_example(
    user_message="Please help me with task X...",
    assistant_message="I'll help you with task X..."
)

# Add required tools and resources
prompt.add_required_tool("kaltura.media.get")
prompt.add_required_resource("kaltura://media/{entry_id}")
```

## Available Prompts

### Content Workflow Prompts

- `moderation_review()`: Review content for moderation issues
- `auto_tagging()`: Automatically generate relevant tags for content
- `category_suggestion()`: Suggest appropriate categories for content
- `distribution_planning()`: Plan optimal distribution strategy for content
- `content_approval_workflow()`: Guide content through an approval workflow

### Content Enrichment Prompts

- `video_summary()`: Generate concise and informative summaries of video content
- `description_generation()`: Generate engaging and informative video descriptions
- `subtitle_generation()`: Generate accurate and well-formatted subtitles for video content
- `content_translation()`: Translate video content while preserving meaning and context
- `thumbnail_suggestion()`: Suggest effective thumbnail concepts for video content

### User Management Prompts

- `role_assignment()`: Recommend appropriate user roles based on responsibilities and requirements
- `permission_management()`: Analyze and optimize user permissions for security and efficiency
- `user_activity_analysis()`: Analyze user activity patterns and provide insights
- `user_engagement_strategy()`: Develop strategies to improve user engagement and adoption

### Reporting Prompts

- `trend_identification()`: Identify and analyze significant trends in platform usage and content performance
- `recommendation_generation()`: Generate data-driven recommendations for content strategy and platform optimization

### API Exploration Prompts

- `api_discovery()`: Discover and explore available Kaltura API services and actions

## Contributing

To add new prompts to the library:

1. Create a new prompt class or extend an existing one
2. Implement the required methods and properties
3. Add examples to demonstrate usage
4. Update the documentation

## License

This library is part of the Kaltura-MCP Server project and is licensed under the same terms.