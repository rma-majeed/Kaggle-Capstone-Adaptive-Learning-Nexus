"""
Student Data Retriever Sub-Agent

Fetches student response data from the database.
Part of the DataFetcher ParallelAgent.
"""

from google.adk.agents import LlmAgent
from ....tools.function_tools import database_reader


def create_student_data_retriever() -> LlmAgent:
    """
    Factory function to create the Student Data Retriever agent.
    
    This agent:
    1. Receives student_id from the coordinator
    2. Calls database_reader tool to fetch student responses
    3. Returns structured student data
    
    Returns:
        LlmAgent configured for student data retrieval
    """
    return LlmAgent(
        name="student_data_retriever",
        model="gemini-2.0-flash",
        description="Fetches student response data from the database for analysis",
        instruction="""
You are the Student Data Retriever. Your job is to fetch student practice data.

## Your Task
When asked to get data for a student:
1. Use the database_reader tool with the student_id
2. Fetch their responses and history
3. Return the structured data

## How to Use the Tool
Call database_reader with:
- student_id: The student identifier (or "all" for all students)
- query_type: One of:
  - "responses" - Get all practice responses
  - "history" - Get performance summary
  - "topics" - Get list of practiced topics

## Response Format
After fetching data, summarize what you found:
- Number of responses
- Topics practiced
- Overall performance summary

## Important
- Always call the tool first before responding
- If no data found, report that clearly
- Be concise - other agents will analyze the data
        """,
        tools=[database_reader],
        output_key="student_data"
    )


# Create singleton instance
student_data_retriever_agent = create_student_data_retriever()

