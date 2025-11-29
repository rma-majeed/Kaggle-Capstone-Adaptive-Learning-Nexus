"""
Data Fetcher - ParallelAgent

Fetches student data from multiple sources in parallel.
This agent runs its sub-agents concurrently for efficient data retrieval.
"""

from google.adk.agents import ParallelAgent
from .student_data_retriever.agent import create_student_data_retriever
from .question_data_retriever.agent import create_question_data_retriever
from .historical_performance.agent import create_historical_performance


def create_data_fetcher() -> ParallelAgent:
    """
    Factory function to create the Data Fetcher parallel agent.
    
    This agent:
    1. Runs 3 sub-agents in parallel
    2. Each sub-agent fetches different data
    3. Results are combined for downstream processing
    
    Returns:
        ParallelAgent configured for parallel data fetching
    """
    return ParallelAgent(
        name="data_fetcher",
        description="Fetches student data from multiple sources in parallel for comprehensive analysis",
        sub_agents=[
            create_student_data_retriever(),
            create_question_data_retriever(),
            create_historical_performance()
        ]
    )


# Create singleton instance
data_fetcher_agent = create_data_fetcher()

