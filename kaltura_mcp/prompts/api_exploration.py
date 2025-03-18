"""
API exploration prompts for the Kaltura-MCP Server intelligent prompting library.

This module provides prompts for API exploration tasks such as API discovery,
parameter explanation, usage examples, and error troubleshooting.
"""
from typing import Dict, Any, List, Optional
from .base import BasePrompt


class ApiExplorationPrompts:
    """Collection of API exploration prompts."""
    
    @staticmethod
    def api_discovery() -> BasePrompt:
        """Create a prompt for API discovery."""
        prompt = BasePrompt(
            name="api_discovery",
            description="Discover and explore available Kaltura API services and actions"
        )
        
        prompt.set_system_message("""
You are an API exploration assistant for the Kaltura video platform. Your task is to help
users discover and understand the available API services, actions, and capabilities.

When helping with API discovery:
1. Provide clear explanations of available services and their purposes
2. Organize information in a logical and accessible way
3. Highlight commonly used services and actions
4. Explain relationships between different services
5. Consider the user's specific needs and use cases
6. Provide guidance on best practices for API usage

Your responses should be informative, well-structured, and tailored to the user's level of expertise.
""")
        
        prompt.set_user_message_template("""
Please help me explore the Kaltura API with the following parameters:

Exploration Focus: {exploration_focus}
API Knowledge Level: {api_knowledge_level}
Use Case: {use_case}

Specific Questions:
{specific_questions}

Additional context: {additional_context}

Please provide a comprehensive overview of the relevant API services and actions.
""")
        
        prompt.add_required_tool("kaltura.media.list")
        prompt.add_required_resource("kaltura://media/list")
        
        return prompt
