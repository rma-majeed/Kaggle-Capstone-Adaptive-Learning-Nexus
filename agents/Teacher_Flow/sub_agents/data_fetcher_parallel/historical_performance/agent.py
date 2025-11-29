"""
Historical Performance Sub-Agent

Fetches historical performance and mastery data for students.
Part of the DataFetcher ParallelAgent.
"""

from google.adk.agents import LlmAgent
from ....tools.function_tools import database_reader


def create_historical_performance() -> LlmAgent:
    """
    Factory function to create the Historical Performance agent.
    
    This agent:
    1. Receives student_id from the coordinator
    2. Fetches mastery levels and historical summaries
    3. Returns performance trends and mastery data
    
    Returns:
        LlmAgent configured for historical data retrieval
    """
    return LlmAgent(
        name="historical_performance",
        model="gemini-2.0-flash",
        description="Fetches historical performance and mastery data for trend analysis",
        instruction="""
You are the Historical Performance Retriever. Your job is to fetch historical data.

## Your Task
When asked to get historical data for a student:
1. Use database_reader to fetch mastery levels
2. Use database_reader to fetch history summary
3. Return the historical performance data

## How to Use the Tool
Call database_reader with:
- student_id: The student identifier (or "all" for all students)
- query_type: Use these in sequence:
  - "mastery" - Get current mastery levels by topic
  - "history" - Get overall performance summary

## What You Return
- Current mastery levels per topic
- Total attempts and scores
- First and last practice dates
- Performance summary (perfect/partial/zero scores)

## Important
- Fetch both mastery and history for complete picture
- If no historical data, report that the student is new
- Be concise - other agents will analyze the trends
        """,
        tools=[database_reader],
        output_key="historical_data"
    )


# Create singleton instance
historical_performance_agent = create_historical_performance()

