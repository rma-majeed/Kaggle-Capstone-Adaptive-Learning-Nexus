"""
Analysis Pipeline - SequentialAgent

Analyzes student performance in a sequential pipeline.
Each agent processes data and passes results to the next.
"""

from google.adk.agents import SequentialAgent
from .answer_scorer.agent import create_answer_scorer
from .pattern_analyzer.agent import create_pattern_analyzer
from .mastery_calculator.agent import create_mastery_calculator


def create_analysis_pipeline() -> SequentialAgent:
    """
    Factory function to create the Analysis Pipeline sequential agent.
    
    This agent:
    1. Runs 3 sub-agents in sequence
    2. Each agent builds on the previous output
    3. Final output includes complete analysis
    
    Pipeline:
    1. AnswerScorer → scored_answers
    2. PatternAnalyzer → analysis_patterns
    3. MasteryCalculator → mastery_levels
    
    Returns:
        SequentialAgent configured for sequential analysis
    """
    return SequentialAgent(
        name="analysis_pipeline",
        description="Analyzes student performance through scoring, pattern analysis, and mastery calculation",
        sub_agents=[
            create_answer_scorer(),
            create_pattern_analyzer(),
            create_mastery_calculator()
        ]
    )


# Create singleton instance
analysis_pipeline_agent = create_analysis_pipeline()

