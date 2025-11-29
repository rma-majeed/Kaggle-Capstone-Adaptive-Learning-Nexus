"""
Teacher Flow Package

Automated data analysis and curriculum optimization for teachers,
demonstrating advanced ADK agent orchestration.

Architecture:
    TeacherAnalysisCoordinator (Root Agent - LlmAgent)
    ├── data_fetcher_tool (AgentTool → ParallelAgent)
    ├── analysis_pipeline_tool (AgentTool → SequentialAgent)
    ├── curriculum_optimizer_tool (AgentTool → LoopAgent)
    └── report_generator_tool (AgentTool → SequentialAgent)

Features Demonstrated:
    - ParallelAgent: Concurrent data fetching
    - SequentialAgent: Pipeline processing
    - LoopAgent: Iterative optimization
    - MCP Integration: Mastery calculation via MCP server
    - Function Tools: Database access and analytics
    - Explicit Routing: Request-based agent selection

Usage:
    # For ADK web interface
    from agents.Teacher_Flow import root_agent
    
    # Or create a new instance
    from agents.Teacher_Flow import create_teacher_analysis_coordinator
    coordinator = create_teacher_analysis_coordinator()
"""

from .agent import root_agent, create_teacher_analysis_coordinator

__all__ = [
    'root_agent',
    'create_teacher_analysis_coordinator'
]

