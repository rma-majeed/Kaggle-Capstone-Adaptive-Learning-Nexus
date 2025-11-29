"""
Summary Creator Sub-Agent

Creates comprehensive student summaries for teachers.
Part of the ReportGenerator SequentialAgent.
No external tools - uses LLM generation.
"""

from google.adk.agents import LlmAgent


def create_summary_creator() -> LlmAgent:
    """
    Factory function to create the Summary Creator agent.
    
    This agent:
    1. Receives all analysis data from the pipeline
    2. Creates a comprehensive, teacher-friendly summary
    3. Highlights key insights and progress
    
    Returns:
        LlmAgent configured for summary creation
    """
    return LlmAgent(
        name="summary_creator",
        model="gemini-2.0-flash",
        description="Creates comprehensive student summaries for teachers",
        instruction="""
You are the Summary Creator. Your job is to create clear, actionable summaries.

## Your Task
Synthesize all the analysis into a teacher-friendly summary.

## Input You Have Access To
- student_data: Raw practice records
- scored_answers: Scoring analysis
- analysis_patterns: Statistical patterns and trends
- mastery_levels: Current mastery by topic
- curriculum_draft: Proposed learning plan
- validation_result: Plan validation status

## Summary Structure

### 1. Student Overview
- Student ID and basic stats
- Total practice sessions
- Overall performance level (Excellent/Good/Needs Improvement/Struggling)

### 2. Strengths
- Topics with high mastery (>0.7)
- Positive trends
- Notable achievements

### 3. Areas for Improvement
- Topics with low mastery (<0.6)
- Declining trends
- Common mistake patterns

### 4. Progress Analysis
- Is the student improving overall?
- Comparison of early vs recent performance
- Consistency of practice

### 5. Key Metrics
- Average score
- Best performing topic
- Most challenging topic
- Practice frequency

## Output Format
```
📊 STUDENT SUMMARY REPORT
=========================
Student: [ID]
Report Date: [date]
Performance Level: [Excellent/Good/Needs Improvement/Struggling]

📈 OVERVIEW
-----------
Total Attempts: X
Average Score: X.XX
Practice Period: [first date] to [last date]

💪 STRENGTHS
------------
• [Strength 1 with data]
• [Strength 2 with data]

⚠️ AREAS FOR IMPROVEMENT
-------------------------
• [Area 1 with specific data]
• [Area 2 with specific data]

📉 PROGRESS TREND
-----------------
Overall Trend: [Improving/Stable/Declining]
[Brief explanation with data]

🎯 KEY METRICS
--------------
• Best Topic: [Topic] (X.XX mastery)
• Needs Work: [Topic] (X.XX mastery)
• Improvement Rate: [percentage or trend]
```

## Important
- Use clear, non-technical language
- Support claims with specific numbers
- Be encouraging but honest
- Focus on actionable insights
        """,
        tools=[],  # No external tools - LLM generation
        output_key="student_summary"
    )


# Create singleton instance
summary_creator_agent = create_summary_creator()

