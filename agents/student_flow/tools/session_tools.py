"""
Session State Tools for Student Flow

These tools allow the agent to read/write to Session.State,
which persists within a single conversation.

Tools:
- save_user_info: Save student name and preferred topic
- get_user_info: Retrieve saved user info
- update_session_progress: Track current question, score, used IDs
- get_session_progress: Get current progress

Session State Keys:
- user:name - Student's name
- user:topic - Student's preferred topic  
- session:current_q - Current question number (1-based)
- session:total_q - Total questions in session
- session:score - Running score
- session:used_ids - Comma-separated used question IDs
"""

from google.adk.tools.tool_context import ToolContext


def save_user_info(
    tool_context: ToolContext, 
    student_name: str, 
    preferred_topic: str
) -> dict:
    """
    Saves user information to session state.
    
    Call this at the start of the session when the student introduces
    themselves and chooses a topic. The information persists throughout
    the conversation.
    
    Args:
        tool_context: ADK tool context (automatically provided by ADK)
        student_name: Name of the student (e.g., "Alex", "Sam")
        preferred_topic: Student's chosen topic 
                        (Fractions, Decimals, Percentages, Geometry, Algebra)
    
    Returns:
        dict with status and confirmation message
    """
    tool_context.state["user:name"] = student_name
    tool_context.state["user:topic"] = preferred_topic
    
    return {
        "status": "success",
        "message": f"Saved info for {student_name}, topic: {preferred_topic}",
        "name": student_name,
        "topic": preferred_topic
    }


def get_user_info(tool_context: ToolContext) -> dict:
    """
    Retrieves user information from session state.
    
    Use this to recall the student's name and chosen topic at any
    point during the session.
    
    Args:
        tool_context: ADK tool context (automatically provided by ADK)
    
    Returns:
        dict with user info:
        - status: "success"
        - name: Student's name or "Student" if not set
        - topic: Chosen topic or None if not set
    """
    name = tool_context.state.get("user:name", "Student")
    topic = tool_context.state.get("user:topic", None)
    
    return {
        "status": "success",
        "name": name,
        "topic": topic,
        "has_info": name != "Student"
    }


def update_session_progress(
    tool_context: ToolContext, 
    current_question: int,
    total_questions: int,
    running_score: float,
    used_question_ids: str
) -> dict:
    """
    Updates session progress tracking after each question.
    
    Call this after presenting each question and after evaluating
    each answer to keep track of the session's progress.
    
    Args:
        tool_context: ADK tool context (automatically provided by ADK)
        current_question: Current question number (1-based, e.g., 1, 2, 3)
        total_questions: Total questions in this session (e.g., 5)
        running_score: Accumulated score so far (e.g., 2.5)
        used_question_ids: Comma-separated list of used question IDs
                          (e.g., "FRAC001,FRAC002,FRAC003")
    
    Returns:
        dict with updated progress info
    """
    tool_context.state["session:current_q"] = current_question
    tool_context.state["session:total_q"] = total_questions
    tool_context.state["session:score"] = running_score
    tool_context.state["session:used_ids"] = used_question_ids
    
    # Calculate percentage
    max_possible = float(total_questions)
    percentage = (running_score / max_possible * 100) if max_possible > 0 else 0
    
    return {
        "status": "success",
        "current_question": current_question,
        "total_questions": total_questions,
        "running_score": running_score,
        "max_possible_score": max_possible,
        "percentage": round(percentage, 1),
        "used_ids_count": len(used_question_ids.split(",")) if used_question_ids else 0
    }


def get_session_progress(tool_context: ToolContext) -> dict:
    """
    Gets current session progress.
    
    Use this to report progress to the student at any point,
    especially at the end of the session for a summary.
    
    Args:
        tool_context: ADK tool context (automatically provided by ADK)
    
    Returns:
        dict with progress info:
        - status: "success"
        - current_question: Current question number (0 if not started)
        - total_questions: Total questions in session (0 if not set)
        - score: Running score (0.0 if not started)
        - used_ids: List of used question IDs
        - percentage: Score as percentage
        - is_complete: True if all questions answered
    """
    current_q = tool_context.state.get("session:current_q", 0)
    total_q = tool_context.state.get("session:total_q", 0)
    score = tool_context.state.get("session:score", 0.0)
    used_ids_str = tool_context.state.get("session:used_ids", "")
    
    # Parse used IDs
    used_ids = used_ids_str.split(",") if used_ids_str else []
    used_ids = [uid.strip() for uid in used_ids if uid.strip()]
    
    # Calculate stats
    max_possible = float(total_q)
    percentage = (score / max_possible * 100) if max_possible > 0 else 0
    is_complete = current_q >= total_q and total_q > 0
    
    return {
        "status": "success",
        "current_question": current_q,
        "total_questions": total_q,
        "score": score,
        "max_possible_score": max_possible,
        "percentage": round(percentage, 1),
        "used_ids": used_ids,
        "questions_remaining": max(0, total_q - current_q),
        "is_complete": is_complete
    }


# For direct testing
if __name__ == "__main__":
    print("Session tools defined. These require ToolContext from ADK.")
    print("\nAvailable tools:")
    print("  - save_user_info(tool_context, student_name, preferred_topic)")
    print("  - get_user_info(tool_context)")
    print("  - update_session_progress(tool_context, current_q, total_q, score, used_ids)")
    print("  - get_session_progress(tool_context)")

