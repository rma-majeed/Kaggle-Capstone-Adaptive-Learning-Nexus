"""
Report Generator Sequential Sub-Agents Package

Contains agents for report generation:
- SummaryCreator: Creates student summaries
- RecommendationEngine: Generates teaching recommendations
"""

from .summary_creator.agent import (
    create_summary_creator,
    summary_creator_agent
)
from .recommendation_engine.agent import (
    create_recommendation_engine,
    recommendation_engine_agent
)

__all__ = [
    'create_summary_creator',
    'summary_creator_agent',
    'create_recommendation_engine',
    'recommendation_engine_agent',
]

