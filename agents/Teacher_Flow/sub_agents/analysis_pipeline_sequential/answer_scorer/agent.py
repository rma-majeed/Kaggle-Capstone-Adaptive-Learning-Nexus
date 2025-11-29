"""
Answer Scorer Sub-Agent

Scores and evaluates student answers using LLM reasoning.
Part of the AnalysisPipeline SequentialAgent.
No external tools - uses LLM evaluation.
"""

from google.adk.agents import LlmAgent


def create_answer_scorer() -> LlmAgent:
    """
    Factory function to create the Answer Scorer agent.
    
    This agent:
    1. Receives student responses from earlier in the pipeline
    2. Evaluates the quality of answers using LLM reasoning
    3. Provides detailed scoring breakdown
    
    Returns:
        LlmAgent configured for answer scoring
    """
    return LlmAgent(
        name="answer_scorer",
        model="gemini-2.0-flash",
        description="Evaluates and scores student answers using LLM reasoning",
        instruction="""
You are the Answer Scorer. Your job is to evaluate student answer quality.

## Your Task
Given student response data, analyze and score the quality of their performance.

## Scoring Framework

### Score Categories:
- **1.0 (Perfect)**: Correct on first attempt - shows strong understanding
- **0.5 (Partial)**: Correct on second attempt - needed hints but got there
- **0.0 (Incorrect)**: Failed after all attempts - needs more practice

### What You Analyze:
1. **Score Distribution**: How many perfect/partial/zero scores
2. **Topic Performance**: Which topics have better scores
3. **Improvement Patterns**: Do scores improve over time
4. **Common Mistakes**: Any patterns in incorrect answers

## Input You Receive
- student_data: Raw response records with scores
- question_data: Question details for context

## Output Format
Provide a structured analysis:
```
SCORING ANALYSIS
================
Total Attempts: X
- Perfect (1.0): X (X%)
- Partial (0.5): X (X%)
- Incorrect (0.0): X (X%)

Overall Score: X.XX / 1.0

Topic Breakdown:
- Topic1: avg X.XX
- Topic2: avg X.XX

Observations:
- [Key finding 1]
- [Key finding 2]
```

## Important
- Be objective and data-driven
- Highlight both strengths and areas for improvement
- Pass your analysis to the next agent in the pipeline
        """,
        tools=[],  # No external tools - LLM reasoning only
        output_key="scored_answers"
    )


# Create singleton instance
answer_scorer_agent = create_answer_scorer()

