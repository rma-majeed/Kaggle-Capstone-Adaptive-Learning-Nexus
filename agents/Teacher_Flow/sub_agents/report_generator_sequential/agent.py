"""
Report Generator - SequentialAgent

Generates comprehensive reports for teachers.
Creates summary first, then actionable recommendations.
"""

from google.adk.agents import SequentialAgent
from .summary_creator.agent import create_summary_creator
from .recommendation_engine.agent import create_recommendation_engine


def create_report_generator() -> SequentialAgent:
    """
    Factory function to create the Report Generator sequential agent.
    
    This agent:
    1. Creates a comprehensive student summary
    2. Generates actionable recommendations
    3. Produces the final teacher report
    
    Pipeline:
    1. SummaryCreator → student_summary
    2. RecommendationEngine → recommendations
    
    Returns:
        SequentialAgent configured for report generation
    """
    return SequentialAgent(
        name="report_generator",
        description="Generates comprehensive reports with summaries and recommendations for teachers",
        sub_agents=[
            create_summary_creator(),
            create_recommendation_engine()
        ]
    )


# Create singleton instance
report_generator_agent = create_report_generator()

