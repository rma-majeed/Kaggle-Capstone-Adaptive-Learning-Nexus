"""
Question Data Retriever Sub-Agent

Fetches question metadata from the question bank.
Part of the DataFetcher ParallelAgent.
Reuses the question_bank tool from student_flow.
"""

from google.adk.agents import LlmAgent
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Reuse question_bank from student_flow
from agents.student_flow.tools.function_tools import question_bank


def create_question_data_retriever() -> LlmAgent:
    """
    Factory function to create the Question Data Retriever agent.
    
    This agent:
    1. Receives topic or question_id from the coordinator
    2. Calls question_bank tool to fetch question details
    3. Returns question metadata (prompt, hints, expected_answer)
    
    Returns:
        LlmAgent configured for question data retrieval
    """
    return LlmAgent(
        name="question_data_retriever",
        model="gemini-2.0-flash",
        description="Fetches question metadata from the question bank for teacher analysis",
        instruction="""
You are the Question Data Retriever. Your job is to fetch question details.

## Your Task
When asked to get question data:
1. Use the question_bank tool to fetch questions
2. Return the question details for analysis

## How to Use the Tool
Call question_bank with:
- topic: The subject area (Fractions, Decimals, Percentages, Geometry, Algebra)
- mastery: Use 0.5 (we just want to see the questions)
- used_ids: Pass empty list [] to get any question

## What You Return
- Question ID
- Question prompt
- Available hints
- Expected answer
- Difficulty level (if available)

## Important
- You may be asked to fetch multiple questions for different topics
- If a topic doesn't exist, report the error
- Be concise - focus on the data, not analysis
        """,
        tools=[question_bank],
        output_key="question_data"
    )


# Create singleton instance
question_data_retriever_agent = create_question_data_retriever()

