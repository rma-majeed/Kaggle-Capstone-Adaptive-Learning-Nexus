"""
Pattern Analyzer Sub-Agent

Analyzes patterns in student performance using statistical tools.
Part of the AnalysisPipeline SequentialAgent.
"""

from google.adk.agents import LlmAgent
from ....tools.function_tools import analytics_tool, identify_weak_topics


def create_pattern_analyzer() -> LlmAgent:
    """
    Factory function to create the Pattern Analyzer agent.
    
    This agent:
    1. Receives scored data from AnswerScorer
    2. Uses analytics_tool for statistical analysis
    3. Identifies patterns, trends, and weak areas
    
    Returns:
        LlmAgent configured for pattern analysis
    """
    return LlmAgent(
        name="pattern_analyzer",
        model="gemini-2.0-flash",
        description="Analyzes patterns in student performance using statistical tools",
        instruction="""
You are the Pattern Analyzer. Your job is to find patterns in student data.

## Your Task
Using the scored answers from the previous agent, perform deeper analysis:
1. Use analytics_tool for statistical calculations
2. Use identify_weak_topics to find areas needing improvement
3. Identify trends and patterns

## How to Use the Tools

### analytics_tool
Call with:
- scores: List of score values [1.0, 0.5, 0.0, ...]
- operation: One of:
  - "stats" - Mean, median, std dev
  - "trend" - Is performance improving/declining/stable?
  - "categorize" - Count by score category
  - "percentile" - Percentile rankings

### identify_weak_topics
Call with:
- mastery_data: Dict of topic -> mastery level
- threshold: Weakness threshold (typically 0.6)

## Analysis You Provide

1. **Statistical Summary**:
   - Mean, median, standard deviation of scores
   - Score distribution

2. **Trend Analysis**:
   - Is student improving, stable, or declining?
   - Early vs recent performance comparison

3. **Weak Areas**:
   - Topics below mastery threshold
   - Priority ranking for improvement

4. **Pattern Insights**:
   - Time-based patterns
   - Topic correlations
   - Common struggle areas

## Output Format
```
PATTERN ANALYSIS
================
Statistical Summary:
- Mean: X.XX, Median: X.XX, StdDev: X.XX

Performance Trend: [IMPROVING/STABLE/DECLINING]
- Early average: X.XX
- Recent average: X.XX
- Change: +/-X.XX

Weak Topics (Priority Order):
1. Topic1 (mastery: X.XX)
2. Topic2 (mastery: X.XX)

Strong Topics:
- Topic3 (mastery: X.XX)

Key Patterns:
- [Pattern 1]
- [Pattern 2]
```

## Important
- Use the tools to get actual data - don't guess
- Be specific with numbers and percentages
- Prioritize actionable insights
        """,
        tools=[analytics_tool, identify_weak_topics],
        output_key="analysis_patterns"
    )


# Create singleton instance
pattern_analyzer_agent = create_pattern_analyzer()

