"""
Question Presenter Sub-Agent

Fetches adaptive questions from question bank and presents them clearly.
Uses the question_bank function tool to retrieve questions.

This agent is wrapped as AgentTool by the root coordinator.
"""

from google.adk.agents import LlmAgent
from ...tools.function_tools import question_bank


def create_question_presenter() -> LlmAgent:
    """
    Factory function to create the Question Presenter agent.
    
    This agent:
    1. Receives topic from the coordinator
    2. Calls question_bank tool to fetch a question
    3. Returns the formatted question for the student
    
    Returns:
        LlmAgent configured for question presentation
    """
    return LlmAgent(
        name="question_presenter",
        model="gemini-2.5-flash",
        description="Fetches and presents practice questions from the question bank",
        instruction="""
        You are the Question Presenter. Your job is to fetch and present questions to students.
        
        ## Your Task
        When the coordinator asks you to get a question:
        1. Use the question_bank tool with the provided topic
        2. Format the question nicely for the student
        3. Return the question details
        
        ## How to Use the Tool
        Call question_bank with:
        - topic: The subject area (e.g., "Fractions", "Decimals", "Percentages", "Geometry", "Algebra")
        - mastery: Use 0.5 as default for medium difficulty
        - used_ids: List of question IDs already shown (pass [] if none)
        
        ## Response Format
        After getting the question, respond with:
        - The question prompt clearly formatted
        - Store the question_id and expected_answer for later use
        
        ## Important
        - Always call the tool first before presenting
        - If the tool returns an error, report it clearly
        - Be encouraging and clear in your presentation
        """,
        tools=[question_bank],
        output_key="current_question"
    )


# Create a singleton instance for direct import if needed
question_presenter_agent = create_question_presenter()
