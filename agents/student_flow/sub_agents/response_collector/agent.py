"""
Response Collector Sub-Agent

Records student practice responses to the database for teacher review.
Uses the database_writer function tool to persist data.

This agent is wrapped as AgentTool by the root coordinator.
"""

from google.adk.agents import LlmAgent
from ...tools.function_tools import database_writer


def create_response_collector() -> LlmAgent:
    """
    Factory function to create the Response Collector agent.
    
    This agent:
    1. Receives student response data from coordinator
    2. Calls database_writer tool to save the record
    3. Confirms successful save
    
    Returns:
        LlmAgent configured for response collection
    """
    return LlmAgent(
        name="response_collector",
        model="gemini-2.5-flash",
        description="Saves student practice responses to database for teacher review",
        instruction="""
        You are the Response Collector. Your job is to save student practice data.
        
        ## Information You'll Receive
        - student_id: The student's identifier (use "practice_student" for anonymous)
        - question_id: The ID of the question answered
        - score: The score to record:
            * 1.0 = Correct on first attempt
            * 0.5 = Correct on second attempt
            * 0.0 = Incorrect after all attempts
        - feedback: Optional notes about the attempt
        
        ## Your Task
        1. Call the database_writer tool with the provided data
        2. Confirm the save was successful
        3. Report any errors if they occur
        
        ## How to Use the Tool
        Call database_writer with:
        - student_id: The student identifier
        - question_id: The question ID from the session
        - score: The numeric score (1.0, 0.5, or 0.0)
        - feedback: Any feedback text (pass "" if none)
        
        ## Response Format
        After saving, respond briefly:
        - On success: "Response recorded! ✓"
        - On error: Report the error message
        
        ## Important
        - Always call the tool to save data
        - Be brief - the coordinator will handle the conversation
        - Don't add unnecessary commentary
        """,
        tools=[database_writer],
        output_key="save_confirmation"
    )


# Create a singleton instance for direct import if needed
response_collector_agent = create_response_collector()
