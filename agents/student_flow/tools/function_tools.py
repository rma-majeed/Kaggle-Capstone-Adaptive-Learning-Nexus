"""
Function Tools for Student Flow Sub-Agents

These are plain Python functions that follow ADK function tool conventions:
- Return type must be dict
- All parameters have type hints
- Clear docstrings describing purpose, params, and return
- No default parameter values (ADK requirement)

Tools:
- question_bank: Fetches questions from JSON file
- database_writer: Saves student responses to SQLite database
"""

import json
import sqlite3
import random
from datetime import datetime
from pathlib import Path

# Get the directory where this file is located
TOOLS_DIR = Path(__file__).parent

# Paths to data files
QUESTIONS_FILE = TOOLS_DIR / "questions.json"
DATABASE_FILE = TOOLS_DIR / "student_responses.db"


def _init_database() -> None:
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            score REAL NOT NULL,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def _load_questions() -> dict:
    """Load questions from the JSON file."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def question_bank(topic: str, mastery: float, used_ids: list[str]) -> dict:
    """
    Fetches a practice question from the question bank based on topic and mastery level.
    
    This tool reads from a JSON file containing math questions for grades 5-8.
    It selects a question that hasn't been used yet in the current session.
    
    Args:
        topic: The subject area to get a question for. 
               Valid values: Fractions, Decimals, Percentages, Geometry, Algebra
        mastery: Student's current mastery level from 0.0 to 1.0.
                 Used for difficulty selection (not fully implemented yet).
        used_ids: List of question IDs already shown in this session.
                  Pass empty list [] if starting fresh.
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - question_id: Unique identifier for the question
            - topic: The topic of the question
            - prompt: The question text to show the student
            - hints: List of progressive hints
            - expected_answer: The correct answer
            - message: Additional info (only on error)
    """
    try:
        # Load all questions
        data = _load_questions()
        all_questions = data.get("questions", [])
        
        # Filter by topic (case-insensitive)
        topic_lower = topic.lower()
        topic_questions = [
            q for q in all_questions 
            if q.get("topic", "").lower() == topic_lower
        ]
        
        if not topic_questions:
            # If exact match fails, try partial match
            topic_questions = [
                q for q in all_questions 
                if topic_lower in q.get("topic", "").lower()
            ]
        
        if not topic_questions:
            return {
                "status": "error",
                "message": f"No questions found for topic: {topic}. Available topics: {data.get('topics', [])}"
            }
        
        # Filter out already used questions
        if used_ids:
            available = [q for q in topic_questions if q.get("id") not in used_ids]
        else:
            available = topic_questions
        
        if not available:
            # If all questions used, reset and pick from all
            available = topic_questions
        
        # Select a question (random for now, could use mastery for difficulty)
        selected = random.choice(available)
        
        return {
            "status": "success",
            "question_id": selected.get("id", "UNKNOWN"),
            "topic": selected.get("topic", topic),
            "prompt": selected.get("prompt", ""),
            "hints": selected.get("hints", []),
            "expected_answer": selected.get("expected_answer", "")
        }
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Question bank file not found at {QUESTIONS_FILE}"
        }
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "message": f"Error parsing question bank JSON: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in question_bank: {str(e)}"
        }


def database_writer(student_id: str, question_id: str, score: float, feedback: str) -> dict:
    """
    Saves a student's response to the SQLite database.
    
    This tool persists student practice data for later analysis by teachers.
    The database file is automatically created if it doesn't exist.
    
    Args:
        student_id: Identifier for the student. Use "practice_student" for anonymous sessions.
        question_id: The ID of the question that was answered (from question_bank).
        score: The score achieved:
               - 1.0 = Correct on first attempt
               - 0.5 = Correct on second attempt  
               - 0.0 = Incorrect after all attempts
        feedback: Optional feedback text about the attempt. Pass empty string if none.
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - record_id: The database ID of the saved record (on success)
            - student_id: Echo of the student_id
            - score: Echo of the score
            - message: Error message (only on error)
    """
    try:
        # Ensure database exists
        _init_database()
        
        # Connect and insert
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO student_responses (student_id, question_id, score, feedback, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, question_id, score, feedback, datetime.now().isoformat()))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "record_id": record_id,
            "student_id": student_id,
            "question_id": question_id,
            "score": score,
            "message": "Response saved successfully"
        }
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in database_writer: {str(e)}"
        }


# Optional: Test the functions when run directly
if __name__ == "__main__":
    print("Testing question_bank...")
    result = question_bank(topic="Fractions", mastery=0.5, used_ids=[])
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print("\nTesting database_writer...")
    result = database_writer(
        student_id="test_student",
        question_id="FRAC001",
        score=1.0,
        feedback="Great job!"
    )
    print(f"Result: {json.dumps(result, indent=2)}")

