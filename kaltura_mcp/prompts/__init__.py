"""
Intelligent prompting library for the Kaltura-MCP Server.

This module provides a set of prompts for common Kaltura workflows and tasks.
"""

from .api_exploration import ApiExplorationPrompts
from .base import BasePrompt
from .content_enrichment import ContentEnrichmentPrompts
from .content_workflow import ContentWorkflowPrompts
from .reporting import ReportingPrompts
from .user_management import UserManagementPrompts

__all__ = [
    "BasePrompt",
    "ContentWorkflowPrompts",
    "ContentEnrichmentPrompts",
    "UserManagementPrompts",
    "ReportingPrompts",
    "ApiExplorationPrompts",
]
