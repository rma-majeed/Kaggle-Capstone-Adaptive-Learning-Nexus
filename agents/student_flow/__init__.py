"""
Student Flow Package (Memory-Enabled)

Interactive practice session for students demonstrating ADK multi-agent orchestration
with session state tracking and long-term memory capabilities.

Architecture:
    StudentPracticeCoordinator (Root Agent - LlmAgent)
    ├── Session State Tools
    │   ├── save_user_info - Save student name and topic
    │   ├── get_user_info - Retrieve student info
    │   ├── update_session_progress - Track progress
    │   └── get_session_progress - Get current stats
    ├── Memory Tool
    │   └── load_memory - Search past sessions (ADK built-in)
    ├── Callback
    │   └── auto_save_to_memory - Auto-save session after each turn
    └── Sub-Agent Tools
        ├── question_presenter_tool (AgentTool)
        ├── hint_provider_tool (AgentTool)
        └── response_collector_tool (AgentTool)

Usage:
    # For ADK web interface (uses root_agent)
    from agents.student_flow import root_agent
    
    # Or create a new instance
    from agents.student_flow import create_student_practice_coordinator
    coordinator = create_student_practice_coordinator()

Memory Features:
    - Session.State: Tracks name, topic, progress within conversation
    - load_memory: Agent searches past sessions for returning students
    - auto_save_to_memory: Callback saves session after each turn

ADK Web Startup Commands:
    
    # Basic (in-memory sessions, memory resets on restart):
    adk web agents/
    
    # With persistent sessions (SQLite - survives restart):
    adk web --session_service_uri="sqlite:///agents/student_flow/data/student_sessions.db" agents/

Memory Behavior:
    - InMemoryMemoryService: Auto-enabled when load_memory tool is present
    - DatabaseSessionService: Enabled via --session_service_uri flag
    - auto_save_to_memory: Runs after each agent turn to save session to memory
"""

from .agent import root_agent, create_student_practice_coordinator, auto_save_to_memory
from .tools import (
    save_user_info,
    get_user_info,
    update_session_progress,
    get_session_progress
)

__all__ = [
    # Agent
    'root_agent',
    'create_student_practice_coordinator',
    # Callback
    'auto_save_to_memory',
    # Session state tools
    'save_user_info',
    'get_user_info',
    'update_session_progress',
    'get_session_progress'
]

