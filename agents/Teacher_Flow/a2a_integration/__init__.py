"""
A2A Integration Package

Provides tools for the ADK host agent to communicate with remote A2A agents.
"""

from .remote_connection import RemoteAgentConnection
from .rag_agent_tool import (
    query_textbook_rag_agent,
    create_rag_agent_tool,
)

__all__ = [
    "RemoteAgentConnection",
    "query_textbook_rag_agent",
    "create_rag_agent_tool",
]

