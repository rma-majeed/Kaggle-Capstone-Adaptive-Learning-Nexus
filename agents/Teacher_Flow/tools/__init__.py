"""
Teacher Flow Tools Package

Contains function tools and MCP server for Teacher Flow sub-agents:

Function Tools:
- database_reader: Reads student data from SQLite database
- analytics_tool: Performs statistical analysis on scores
- identify_weak_topics: Identifies topics below mastery threshold
- curriculum_validator: Validates curriculum plan feasibility

MCP Server:
- mastery_mcp_server: MCP server for mastery calculation (Kaggle MCP requirement)

Usage:
    # Function tools
    from agents.Teacher_Flow.tools import (
        database_reader,
        analytics_tool,
        identify_weak_topics,
        curriculum_validator
    )
    
    # MCP server (run as subprocess)
    # python agents/Teacher_Flow/tools/mastery_mcp_server.py
"""

from .function_tools import (
    database_reader,
    analytics_tool,
    identify_weak_topics,
    curriculum_validator
)

__all__ = [
    "database_reader",
    "analytics_tool",
    "identify_weak_topics",
    "curriculum_validator"
]

