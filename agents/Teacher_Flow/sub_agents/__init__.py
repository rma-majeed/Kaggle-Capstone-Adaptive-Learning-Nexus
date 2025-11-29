"""
Teacher Flow Sub-Agents Package

This package contains 4 workflow agents for teacher analysis:

1. DataFetcher (ParallelAgent) - Fetches data in parallel
   - StudentDataRetriever
   - QuestionDataRetriever
   - HistoricalPerformance

2. AnalysisPipeline (SequentialAgent) - Sequential analysis
   - AnswerScorer
   - PatternAnalyzer
   - MasteryCalculator

3. CurriculumOptimizer (LoopAgent) - Iterative optimization
   - CurriculumGenerator
   - PlanValidator

4. ReportGenerator (SequentialAgent) - Report creation
   - SummaryCreator
   - RecommendationEngine
"""

from google.adk.tools import AgentTool

# Import workflow agent factories
from .data_fetcher_parallel.agent import create_data_fetcher, data_fetcher_agent
from .analysis_pipeline_sequential.agent import create_analysis_pipeline, analysis_pipeline_agent
from .curriculum_optimizer_loop.agent import create_curriculum_optimizer, curriculum_optimizer_agent
from .report_generator_sequential.agent import create_report_generator, report_generator_agent

# Import leaf agent factories (for direct access if needed)
from .data_fetcher_parallel import (
    create_student_data_retriever,
    create_question_data_retriever,
    create_historical_performance
)
from .analysis_pipeline_sequential import (
    create_answer_scorer,
    create_pattern_analyzer,
    create_mastery_calculator,
    create_mastery_calculator_with_mcp
)
from .curriculum_optimizer_loop import (
    create_curriculum_generator,
    create_plan_validator
)
from .report_generator_sequential import (
    create_summary_creator,
    create_recommendation_engine
)


# AgentTool factory functions for root agent
def create_data_fetcher_tool() -> AgentTool:
    """Creates an AgentTool-wrapped DataFetcher for use by the root agent."""
    return AgentTool(agent=create_data_fetcher())


def create_analysis_pipeline_tool() -> AgentTool:
    """Creates an AgentTool-wrapped AnalysisPipeline for use by the root agent."""
    return AgentTool(agent=create_analysis_pipeline())


def create_curriculum_optimizer_tool() -> AgentTool:
    """Creates an AgentTool-wrapped CurriculumOptimizer for use by the root agent."""
    return AgentTool(agent=create_curriculum_optimizer())


def create_report_generator_tool() -> AgentTool:
    """Creates an AgentTool-wrapped ReportGenerator for use by the root agent."""
    return AgentTool(agent=create_report_generator())


__all__ = [
    # Workflow agent factories
    'create_data_fetcher',
    'create_analysis_pipeline',
    'create_curriculum_optimizer',
    'create_report_generator',
    
    # Workflow agent singletons
    'data_fetcher_agent',
    'analysis_pipeline_agent',
    'curriculum_optimizer_agent',
    'report_generator_agent',
    
    # AgentTool factories (for root agent)
    'create_data_fetcher_tool',
    'create_analysis_pipeline_tool',
    'create_curriculum_optimizer_tool',
    'create_report_generator_tool',
    
    # Leaf agent factories
    'create_student_data_retriever',
    'create_question_data_retriever',
    'create_historical_performance',
    'create_answer_scorer',
    'create_pattern_analyzer',
    'create_mastery_calculator',
    'create_mastery_calculator_with_mcp',
    'create_curriculum_generator',
    'create_plan_validator',
    'create_summary_creator',
    'create_recommendation_engine',
]

