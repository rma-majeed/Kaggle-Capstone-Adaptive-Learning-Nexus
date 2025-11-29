"""
Function Tools for Teacher Flow Sub-Agents

These are plain Python functions that follow ADK function tool conventions:
- Return type must be dict
- All parameters have type hints
- Clear docstrings describing purpose, params, and return
- No default parameter values (ADK requirement)

Tools:
- database_reader: Reads student data from SQLite database
- analytics_tool: Performs statistical analysis on scores
- curriculum_validator: Validates curriculum plan feasibility
"""

import sqlite3
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

# Database path (same as student_flow to share data)
STUDENT_FLOW_TOOLS_DIR = Path(__file__).parent.parent.parent / "student_flow" / "tools"
DATABASE_FILE = STUDENT_FLOW_TOOLS_DIR / "student_responses.db"


def _init_teacher_tables() -> None:
    """Initialize additional tables needed for Teacher Flow."""
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


def database_reader(student_id: str, query_type: str) -> dict:
    """
    Reads student data from the database based on query type.
    
    This tool retrieves various types of student data for analysis.
    
    Args:
        student_id: The student identifier to query data for.
                   Use "all" to get data for all students.
        query_type: Type of data to retrieve. Valid values:
                   - "responses": Get all student responses/attempts
                   - "mastery": Get current mastery levels by topic
                   - "history": Get historical performance summary
                   - "topics": Get list of topics student has practiced
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - data: The requested data (format varies by query_type)
            - count: Number of records returned
            - message: Error message (only on error)
    """
    try:
        _init_teacher_tables()
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if query_type == "responses":
            # Get all responses for a student
            if student_id == "all":
                cursor.execute("""
                    SELECT id, student_id, question_id, score, feedback, timestamp
                    FROM student_responses
                    ORDER BY timestamp DESC
                """)
            else:
                cursor.execute("""
                    SELECT id, student_id, question_id, score, feedback, timestamp
                    FROM student_responses
                    WHERE student_id = ?
                    ORDER BY timestamp DESC
                """, (student_id,))
            
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            
            conn.close()
            return {
                "status": "success",
                "query_type": query_type,
                "student_id": student_id,
                "data": data,
                "count": len(data)
            }
        
        elif query_type == "mastery":
            # Get mastery levels for a student
            if student_id == "all":
                cursor.execute("""
                    SELECT student_id, topic, mastery_level, last_updated
                    FROM student_mastery
                    ORDER BY student_id, topic
                """)
            else:
                cursor.execute("""
                    SELECT student_id, topic, mastery_level, last_updated
                    FROM student_mastery
                    WHERE student_id = ?
                    ORDER BY topic
                """, (student_id,))
            
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            
            conn.close()
            return {
                "status": "success",
                "query_type": query_type,
                "student_id": student_id,
                "data": data,
                "count": len(data)
            }
        
        elif query_type == "history":
            # Get historical performance summary
            if student_id == "all":
                cursor.execute("""
                    SELECT 
                        student_id,
                        COUNT(*) as total_attempts,
                        AVG(score) as avg_score,
                        SUM(CASE WHEN score = 1.0 THEN 1 ELSE 0 END) as perfect_scores,
                        SUM(CASE WHEN score = 0.5 THEN 1 ELSE 0 END) as partial_scores,
                        SUM(CASE WHEN score = 0.0 THEN 1 ELSE 0 END) as zero_scores,
                        MIN(timestamp) as first_attempt,
                        MAX(timestamp) as last_attempt
                    FROM student_responses
                    GROUP BY student_id
                    ORDER BY student_id
                """)
            else:
                cursor.execute("""
                    SELECT 
                        student_id,
                        COUNT(*) as total_attempts,
                        AVG(score) as avg_score,
                        SUM(CASE WHEN score = 1.0 THEN 1 ELSE 0 END) as perfect_scores,
                        SUM(CASE WHEN score = 0.5 THEN 1 ELSE 0 END) as partial_scores,
                        SUM(CASE WHEN score = 0.0 THEN 1 ELSE 0 END) as zero_scores,
                        MIN(timestamp) as first_attempt,
                        MAX(timestamp) as last_attempt
                    FROM student_responses
                    WHERE student_id = ?
                    GROUP BY student_id
                """, (student_id,))
            
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            
            conn.close()
            return {
                "status": "success",
                "query_type": query_type,
                "student_id": student_id,
                "data": data,
                "count": len(data)
            }
        
        elif query_type == "topics":
            # Get list of topics the student has practiced
            # Extract topic from question_id (e.g., FRAC001 -> Fractions)
            topic_mapping = {
                "FRAC": "Fractions",
                "DEC": "Decimals",
                "PERC": "Percentages",
                "GEO": "Geometry",
                "ALG": "Algebra"
            }
            
            if student_id == "all":
                cursor.execute("""
                    SELECT DISTINCT question_id
                    FROM student_responses
                """)
            else:
                cursor.execute("""
                    SELECT DISTINCT question_id
                    FROM student_responses
                    WHERE student_id = ?
                """, (student_id,))
            
            rows = cursor.fetchall()
            
            # Extract unique topics
            topics_found = set()
            for row in rows:
                question_id = row[0]
                for prefix, topic in topic_mapping.items():
                    if question_id.startswith(prefix):
                        topics_found.add(topic)
                        break
            
            conn.close()
            return {
                "status": "success",
                "query_type": query_type,
                "student_id": student_id,
                "data": sorted(list(topics_found)),
                "count": len(topics_found)
            }
        
        else:
            conn.close()
            return {
                "status": "error",
                "message": f"Invalid query_type: {query_type}. Valid values: responses, mastery, history, topics"
            }
    
    except sqlite3.Error as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in database_reader: {str(e)}"
        }


def analytics_tool(scores: list[float], operation: str) -> dict:
    """
    Performs statistical analysis on a list of scores.
    
    This tool provides various analytical operations for student performance data.
    
    Args:
        scores: List of scores to analyze. Each score should be 0.0, 0.5, or 1.0.
               Pass empty list [] if no scores available.
        operation: The analysis operation to perform. Valid values:
                  - "stats": Calculate mean, median, std dev, min, max
                  - "categorize": Count scores by category (perfect, partial, zero)
                  - "trend": Analyze if performance is improving, stable, or declining
                  - "percentile": Calculate percentile rankings
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - operation: The operation performed
            - result: The analysis result (format varies by operation)
            - message: Error message (only on error)
    """
    try:
        if not scores:
            return {
                "status": "success",
                "operation": operation,
                "result": {
                    "message": "No scores provided",
                    "count": 0
                }
            }
        
        if operation == "stats":
            # Calculate basic statistics
            result = {
                "count": len(scores),
                "mean": round(statistics.mean(scores), 4),
                "median": round(statistics.median(scores), 4),
                "min": min(scores),
                "max": max(scores),
                "sum": sum(scores)
            }
            
            # Add standard deviation if more than 1 score
            if len(scores) > 1:
                result["std_dev"] = round(statistics.stdev(scores), 4)
            else:
                result["std_dev"] = 0.0
            
            return {
                "status": "success",
                "operation": operation,
                "result": result
            }
        
        elif operation == "categorize":
            # Categorize scores
            perfect = sum(1 for s in scores if s == 1.0)
            partial = sum(1 for s in scores if s == 0.5)
            zero = sum(1 for s in scores if s == 0.0)
            total = len(scores)
            
            result = {
                "total": total,
                "perfect_count": perfect,
                "perfect_percent": round(perfect / total * 100, 1) if total > 0 else 0,
                "partial_count": partial,
                "partial_percent": round(partial / total * 100, 1) if total > 0 else 0,
                "zero_count": zero,
                "zero_percent": round(zero / total * 100, 1) if total > 0 else 0
            }
            
            return {
                "status": "success",
                "operation": operation,
                "result": result
            }
        
        elif operation == "trend":
            # Analyze performance trend
            if len(scores) < 2:
                return {
                    "status": "success",
                    "operation": operation,
                    "result": {
                        "trend": "insufficient_data",
                        "message": "Need at least 2 scores to analyze trend"
                    }
                }
            
            # Calculate simple linear regression slope
            n = len(scores)
            x_mean = (n - 1) / 2
            y_mean = sum(scores) / n
            
            numerator = sum((i - x_mean) * (score - y_mean) 
                          for i, score in enumerate(scores))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Determine trend
            if slope > 0.05:
                trend = "improving"
            elif slope < -0.05:
                trend = "declining"
            else:
                trend = "stable"
            
            # Calculate recent vs early performance
            mid = n // 2
            early_avg = statistics.mean(scores[:mid]) if mid > 0 else 0
            recent_avg = statistics.mean(scores[mid:]) if mid > 0 else 0
            
            result = {
                "trend": trend,
                "slope": round(slope, 4),
                "early_average": round(early_avg, 4),
                "recent_average": round(recent_avg, 4),
                "improvement": round(recent_avg - early_avg, 4)
            }
            
            return {
                "status": "success",
                "operation": operation,
                "result": result
            }
        
        elif operation == "percentile":
            # Calculate percentile information
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            
            def percentile(p):
                k = (n - 1) * p / 100
                f = int(k)
                c = f + 1 if f + 1 < n else f
                return sorted_scores[f] + (k - f) * (sorted_scores[c] - sorted_scores[f])
            
            result = {
                "count": n,
                "p25": round(percentile(25), 4),
                "p50": round(percentile(50), 4),  # median
                "p75": round(percentile(75), 4),
                "p90": round(percentile(90), 4)
            }
            
            return {
                "status": "success",
                "operation": operation,
                "result": result
            }
        
        else:
            return {
                "status": "error",
                "message": f"Invalid operation: {operation}. Valid values: stats, categorize, trend, percentile"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in analytics_tool: {str(e)}"
        }


def identify_weak_topics(mastery_data: dict[str, float], threshold: float) -> dict:
    """
    Identifies topics below the mastery threshold.
    
    This tool analyzes mastery levels and returns topics that need improvement.
    
    Args:
        mastery_data: Dictionary mapping topic names to mastery levels.
                     Example: {"Fractions": 0.65, "Decimals": 0.42, "Algebra": 0.8}
        threshold: Mastery level below which a topic is considered "weak".
                  Typical value is 0.6 (60%).
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - weak_topics: List of weak topics with priority ranking
            - strong_topics: List of topics above threshold
            - message: Error message (only on error)
    """
    try:
        if not mastery_data:
            return {
                "status": "success",
                "weak_topics": [],
                "strong_topics": [],
                "message": "No mastery data provided"
            }
        
        weak = []
        strong = []
        
        for topic, mastery in mastery_data.items():
            if mastery < threshold:
                weak.append({"topic": topic, "mastery": round(mastery, 4)})
            else:
                strong.append({"topic": topic, "mastery": round(mastery, 4)})
        
        # Sort weak topics by mastery (weakest first) and add priority
        weak.sort(key=lambda x: x["mastery"])
        for i, item in enumerate(weak, 1):
            item["priority"] = i
        
        # Sort strong topics by mastery (strongest first)
        strong.sort(key=lambda x: x["mastery"], reverse=True)
        
        return {
            "status": "success",
            "threshold": threshold,
            "weak_topics": weak,
            "weak_count": len(weak),
            "strong_topics": strong,
            "strong_count": len(strong)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in identify_weak_topics: {str(e)}"
        }


def curriculum_validator(curriculum_plan: list[dict]) -> dict:
    """
    Validates a curriculum plan for feasibility and quality.
    
    This tool checks if a proposed curriculum plan is realistic and well-structured.
    
    Args:
        curriculum_plan: List of curriculum items. Each item should have:
                        - topic: Subject topic name
                        - estimated_sessions: Number of practice sessions planned
                        - target_mastery: Target mastery level (0.0 to 1.0)
                        - current_mastery: Current mastery level (optional)
                        - priority: Priority level (optional)
    
    Returns:
        dict containing:
            - status: "success" or "error"
            - valid: True if plan passes all checks, False otherwise
            - issues: List of issues found
            - warnings: List of warnings (non-blocking)
            - total_sessions: Sum of all estimated sessions
            - message: Error message (only on error)
    """
    try:
        if not curriculum_plan:
            return {
                "status": "success",
                "valid": False,
                "issues": ["Empty curriculum plan provided"],
                "warnings": [],
                "total_sessions": 0
            }
        
        issues = []
        warnings = []
        total_sessions = 0
        
        for i, item in enumerate(curriculum_plan):
            topic = item.get("topic", f"Item {i+1}")
            
            # Check required fields
            if "topic" not in item:
                issues.append(f"Item {i+1}: Missing 'topic' field")
            
            if "estimated_sessions" not in item:
                issues.append(f"{topic}: Missing 'estimated_sessions' field")
            else:
                sessions = item.get("estimated_sessions", 0)
                total_sessions += sessions
                
                # Check session count
                if sessions <= 0:
                    issues.append(f"{topic}: Sessions must be positive (got {sessions})")
                elif sessions > 10:
                    warnings.append(f"{topic}: High session count ({sessions}) - may be too ambitious")
            
            if "target_mastery" not in item:
                warnings.append(f"{topic}: Missing 'target_mastery' - assuming 0.8")
            else:
                target = item.get("target_mastery", 0)
                
                # Check target mastery
                if target > 0.95:
                    warnings.append(f"{topic}: Target mastery {target} is very high - may be unrealistic")
                elif target < 0.5:
                    warnings.append(f"{topic}: Target mastery {target} is low - consider higher goal")
                
                # Check if target is higher than current
                current = item.get("current_mastery", 0)
                if current >= target:
                    warnings.append(f"{topic}: Current mastery ({current}) already meets target ({target})")
        
        # Check total sessions
        if total_sessions > 30:
            issues.append(f"Total sessions ({total_sessions}) exceeds recommended maximum of 30")
        elif total_sessions > 20:
            warnings.append(f"Total sessions ({total_sessions}) is high - consider spacing over time")
        
        # Check for duplicate topics
        topics = [item.get("topic") for item in curriculum_plan if "topic" in item]
        if len(topics) != len(set(topics)):
            issues.append("Duplicate topics found in curriculum plan")
        
        return {
            "status": "success",
            "valid": len(issues) == 0,
            "issues": issues,
            "issues_count": len(issues),
            "warnings": warnings,
            "warnings_count": len(warnings),
            "total_sessions": total_sessions,
            "topics_count": len(curriculum_plan)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error in curriculum_validator: {str(e)}"
        }


# Export all tools
__all__ = [
    "database_reader",
    "analytics_tool",
    "identify_weak_topics",
    "curriculum_validator"
]


# Test when run directly
if __name__ == "__main__":
    import json
    
    print("Testing database_reader...")
    result = database_reader(student_id="test_student_1", query_type="responses")
    print(f"Responses: {json.dumps(result, indent=2)}")
    
    print("\nTesting analytics_tool...")
    result = analytics_tool(scores=[1.0, 0.5, 1.0, 0.0, 1.0, 0.5], operation="stats")
    print(f"Stats: {json.dumps(result, indent=2)}")
    
    print("\nTesting identify_weak_topics...")
    result = identify_weak_topics(
        mastery_data={"Fractions": 0.65, "Decimals": 0.42, "Algebra": 0.8},
        threshold=0.6
    )
    print(f"Weak topics: {json.dumps(result, indent=2)}")
    
    print("\nTesting curriculum_validator...")
    result = curriculum_validator([
        {"topic": "Decimals", "estimated_sessions": 5, "target_mastery": 0.7, "current_mastery": 0.42},
        {"topic": "Fractions", "estimated_sessions": 3, "target_mastery": 0.8, "current_mastery": 0.65}
    ])
    print(f"Validation: {json.dumps(result, indent=2)}")

