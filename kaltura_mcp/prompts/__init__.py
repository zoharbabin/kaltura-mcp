"""
Intelligent prompting library for the Kaltura-MCP Server.

This module provides a set of prompts for common Kaltura workflows and tasks.
"""

from .base import BasePrompt
from .content_workflow import ContentWorkflowPrompts
from .content_enrichment import ContentEnrichmentPrompts
from .user_management import UserManagementPrompts
from .reporting import ReportingPrompts
from .api_exploration import ApiExplorationPrompts

__all__ = [
    'BasePrompt',
    'ContentWorkflowPrompts',
    'ContentEnrichmentPrompts',
    'UserManagementPrompts',
    'ReportingPrompts',
    'ApiExplorationPrompts',
]