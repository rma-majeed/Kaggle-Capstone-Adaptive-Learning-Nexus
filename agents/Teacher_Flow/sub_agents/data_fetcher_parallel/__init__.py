"""
Data Fetcher Parallel Sub-Agents Package

Contains agents for parallel data fetching:
- StudentDataRetriever: Fetches student response data
- QuestionDataRetriever: Fetches question metadata
- HistoricalPerformance: Fetches historical and mastery data
"""

from .student_data_retriever.agent import (
    create_student_data_retriever,
    student_data_retriever_agent
)
from .question_data_retriever.agent import (
    create_question_data_retriever,
    question_data_retriever_agent
)
from .historical_performance.agent import (
    create_historical_performance,
    historical_performance_agent
)

__all__ = [
    'create_student_data_retriever',
    'student_data_retriever_agent',
    'create_question_data_retriever',
    'question_data_retriever_agent',
    'create_historical_performance',
    'historical_performance_agent',
]

