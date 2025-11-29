"""
Student Flow Sub-Agents Package

This package contains 3 specialized sub-agents for interactive practice sessions:
- QuestionPresenter: Fetches and presents questions from the question bank
- HintProvider: Provides progressive hints using Google Search
- ResponseCollector: Saves student responses to the database

Each sub-agent is wrapped as AgentTool for use by the root coordinator.
"""

from google.adk.tools import AgentTool

# Import factory functions from each sub-agent
from .question_presenter.agent import create_question_presenter, question_presenter_agent
from .hint_provider.agent import create_hint_provider, hint_provider_agent
from .response_collector.agent import create_response_collector, response_collector_agent


def create_question_presenter_tool() -> AgentTool:
    """
    Creates an AgentTool-wrapped QuestionPresenter for use by the root agent.
    
    Returns:
        AgentTool wrapping the QuestionPresenter LlmAgent
    """
    return AgentTool(agent=create_question_presenter())


def create_hint_provider_tool() -> AgentTool:
    """
    Creates an AgentTool-wrapped HintProvider for use by the root agent.
    
    Returns:
        AgentTool wrapping the HintProvider LlmAgent
    """
    return AgentTool(agent=create_hint_provider())


def create_response_collector_tool() -> AgentTool:
    """
    Creates an AgentTool-wrapped ResponseCollector for use by the root agent.
    
    Returns:
        AgentTool wrapping the ResponseCollector LlmAgent
    """
    return AgentTool(agent=create_response_collector())


__all__ = [
    # Factory functions for creating sub-agents
    'create_question_presenter',
    'create_hint_provider',
    'create_response_collector',
    
    # Singleton agent instances
    'question_presenter_agent',
    'hint_provider_agent',
    'response_collector_agent',
    
    # AgentTool factory functions (for root agent)
    'create_question_presenter_tool',
    'create_hint_provider_tool',
    'create_response_collector_tool',
]
