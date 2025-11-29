"""
Mastery Calculation MCP Server

This is a Model Context Protocol (MCP) server that provides mastery calculation
capabilities. It demonstrates MCP integration for the Kaggle AI Agents Competition.

The server exposes the following tools:
- calculate_mastery: Calculate and update student mastery using exponential moving average
- get_mastery: Get current mastery level for a student-topic pair
- get_all_mastery: Get all mastery levels for a student

Usage:
    # Run as stdio server (for ADK McpToolset integration)
    python mastery_mcp_server.py
    
    # Or run as SSE server for testing
    python mastery_mcp_server.py --transport sse --port 8001

Integration with ADK:
    from google.adk.tools import McpToolset
    from mcp import StdioConnectionParams
    
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            command="python",
            args=["path/to/mastery_mcp_server.py"]
        )
    )
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import argparse

from mcp.server.fastmcp import FastMCP

# Database path (same as student_flow to share data)
TOOLS_DIR = Path(__file__).parent
STUDENT_FLOW_TOOLS_DIR = TOOLS_DIR.parent.parent / "student_flow" / "tools"
DATABASE_FILE = STUDENT_FLOW_TOOLS_DIR / "student_responses.db"

# Create the MCP server
mcp = FastMCP(
    name="mastery_calculator",
    instructions="""
    This MCP server provides student mastery calculation capabilities.
    
    Mastery is calculated using an Exponential Moving Average (EMA) formula:
    new_mastery = (old_mastery * 0.8) + (new_score * 0.2)
    
    This gives more weight to historical performance while still reflecting recent scores.
    
    Available tools:
    - calculate_mastery: Update mastery based on a new score
    - get_mastery: Get current mastery for a student-topic pair
    - get_all_mastery: Get all mastery levels for a student
    """
)


def _init_database() -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create student_mastery table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_mastery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            mastery_level REAL NOT NULL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, topic)
        )
    """)
    
    conn.commit()
    conn.close()


@mcp.tool()
def calculate_mastery(student_id: str, topic: str, new_score: float) -> dict:
    """
    Calculate and update student mastery using exponential moving average.
    
    The mastery is updated using the formula:
    new_mastery = (old_mastery * 0.8) + (new_score * 0.2)
    
    This gives 80% weight to historical performance and 20% to the new score,
    providing a balanced view that responds to improvement while being stable.
    
    Args:
        student_id: The student identifier (e.g., "S001", "practice_student")
        topic: The subject topic (Fractions, Decimals, Percentages, Geometry, Algebra)
        new_score: The score from the latest attempt:
                   - 1.0 = Correct on first attempt
                   - 0.5 = Correct on second attempt
                   - 0.0 = Incorrect after all attempts
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - student_id: The student identifier
            - topic: The topic
            - previous_mastery: Mastery level before update
            - new_mastery: Mastery level after update
            - change: The change in mastery level
            - message: Description of what happened
    """
    try:
        _init_database()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get current mastery
        cursor.execute("""
            SELECT mastery_level FROM student_mastery
            WHERE student_id = ? AND topic = ?
        """, (student_id, topic))
        
        row = cursor.fetchone()
        
        if row is None:
            # No existing mastery - create new record
            # For first attempt, use the score directly as initial mastery
            previous_mastery = 0.0
            new_mastery = new_score
            
            cursor.execute("""
                INSERT INTO student_mastery (student_id, topic, mastery_level, last_updated)
                VALUES (?, ?, ?, ?)
            """, (student_id, topic, new_mastery, datetime.now().isoformat()))
            
            message = f"Created new mastery record for {student_id} in {topic}"
        else:
            # Update existing mastery using EMA formula
            previous_mastery = row[0]
            new_mastery = (previous_mastery * 0.8) + (new_score * 0.2)
            
            cursor.execute("""
                UPDATE student_mastery
                SET mastery_level = ?, last_updated = ?
                WHERE student_id = ? AND topic = ?
            """, (new_mastery, datetime.now().isoformat(), student_id, topic))
            
            message = f"Updated mastery for {student_id} in {topic}"
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "student_id": student_id,
            "topic": topic,
            "previous_mastery": round(previous_mastery, 4),
            "new_mastery": round(new_mastery, 4),
            "change": round(new_mastery - previous_mastery, 4),
            "score_applied": new_score,
            "message": message
        }
    
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def get_mastery(student_id: str, topic: str) -> dict:
    """
    Get the current mastery level for a specific student-topic pair.
    
    Args:
        student_id: The student identifier
        topic: The subject topic to check
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - student_id: The student identifier
            - topic: The topic
            - mastery_level: Current mastery level (0.0 to 1.0)
            - last_updated: When the mastery was last updated
            - exists: Whether a mastery record exists
    """
    try:
        _init_database()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mastery_level, last_updated FROM student_mastery
            WHERE student_id = ? AND topic = ?
        """, (student_id, topic))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return {
                "status": "success",
                "student_id": student_id,
                "topic": topic,
                "mastery_level": 0.0,
                "last_updated": None,
                "exists": False,
                "message": f"No mastery record found for {student_id} in {topic}"
            }
        else:
            return {
                "status": "success",
                "student_id": student_id,
                "topic": topic,
                "mastery_level": round(row[0], 4),
                "last_updated": row[1],
                "exists": True
            }
    
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def get_all_mastery(student_id: str) -> dict:
    """
    Get all mastery levels for a student across all topics.
    
    Args:
        student_id: The student identifier
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - student_id: The student identifier
            - mastery_by_topic: Dict mapping topic to mastery level
            - topics_count: Number of topics with mastery records
            - average_mastery: Average mastery across all topics
            - weakest_topic: Topic with lowest mastery
            - strongest_topic: Topic with highest mastery
    """
    try:
        _init_database()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT topic, mastery_level, last_updated FROM student_mastery
            WHERE student_id = ?
            ORDER BY topic
        """, (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                "status": "success",
                "student_id": student_id,
                "mastery_by_topic": {},
                "topics_count": 0,
                "average_mastery": 0.0,
                "weakest_topic": None,
                "strongest_topic": None,
                "message": f"No mastery records found for {student_id}"
            }
        
        mastery_by_topic = {}
        for topic, mastery, _ in rows:
            mastery_by_topic[topic] = round(mastery, 4)
        
        avg_mastery = sum(mastery_by_topic.values()) / len(mastery_by_topic)
        weakest = min(mastery_by_topic.items(), key=lambda x: x[1])
        strongest = max(mastery_by_topic.items(), key=lambda x: x[1])
        
        return {
            "status": "success",
            "student_id": student_id,
            "mastery_by_topic": mastery_by_topic,
            "topics_count": len(mastery_by_topic),
            "average_mastery": round(avg_mastery, 4),
            "weakest_topic": {"topic": weakest[0], "mastery": weakest[1]},
            "strongest_topic": {"topic": strongest[0], "mastery": strongest[1]}
        }
    
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
def bulk_update_mastery(updates: list[dict]) -> dict:
    """
    Update mastery for multiple student-topic pairs at once.
    
    This is useful when processing multiple responses from a practice session.
    
    Args:
        updates: List of update dicts, each containing:
                 - student_id: The student identifier
                 - topic: The subject topic
                 - score: The score to apply (0.0, 0.5, or 1.0)
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - processed: Number of updates processed
            - results: List of individual update results
    """
    try:
        results = []
        
        for update in updates:
            student_id = update.get("student_id")
            topic = update.get("topic")
            score = update.get("score")
            
            if not all([student_id, topic, score is not None]):
                results.append({
                    "status": "error",
                    "message": "Missing required fields",
                    "input": update
                })
                continue
            
            result = calculate_mastery(student_id, topic, score)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("status") == "success")
        
        return {
            "status": "success",
            "processed": len(updates),
            "successful": successful,
            "failed": len(updates) - successful,
            "results": results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Mastery Calculation MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port for SSE transport (default: 8001)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", port=args.port)


if __name__ == "__main__":
    main()

