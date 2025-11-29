"""
A2A Agent Executor for Textbook RAG Agent

Wraps the CrewAI TextbookRagAgent to handle A2A protocol requests.
This is the bridge between A2A server and CrewAI agent.
"""

import json
from typing import Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError

from .agent import TextbookRagAgent


class RagAgentExecutor(AgentExecutor):
    """
    A2A AgentExecutor for the Textbook RAG Agent.
    
    Handles incoming A2A requests, delegates to CrewAI agent,
    and returns results in A2A format.
    """
    
    def __init__(self, textbook_path: Optional[str] = None):
        """
        Initialize the executor with the RAG agent.
        
        Args:
            textbook_path: Optional path to the textbook PDF
        """
        self.agent: Optional[TextbookRagAgent] = None
        self.textbook_path = textbook_path
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazily initialize the agent on first request."""
        if not self._initialized:
            try:
                self.agent = TextbookRagAgent(self.textbook_path)
                self._initialized = True
                print("✅ TextbookRagAgent initialized successfully")
            except FileNotFoundError as e:
                print(f"⚠️ Agent initialization warning: {e}")
                # Agent will return error message on queries
                self._initialized = True
            except Exception as e:
                print(f"❌ Agent initialization error: {e}")
                raise
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute a textbook search request.
        
        Args:
            context: The A2A request context containing the user's query
            event_queue: Queue to send status updates and results
        """
        # Validate request context
        if not context.task_id or not context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not context.message:
            raise ValueError("RequestContext must have a message")
        
        # Create task updater for status updates
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        # Submit task if new
        if not context.current_task:
            await updater.submit()
        
        # Start work
        await updater.start_work()
        
        # Validate request
        if self._validate_request(context):
            raise ServerError(error=InvalidParamsError())
        
        # Get user query
        query = context.get_user_input()
        print(f"📥 Received query: {query}")
        
        # Parse query for topic (optional)
        topic = None
        try:
            # Try to parse as JSON for structured input
            data = json.loads(query)
            if isinstance(data, dict):
                query = data.get("query", query)
                topic = data.get("topic")
        except json.JSONDecodeError:
            # Plain text query, use as-is
            pass
        
        # Ensure agent is initialized
        self._ensure_initialized()
        
        try:
            if self.agent is None:
                result = "Error: No textbook PDF found. Please add a PDF to the data/textbooks directory."
            else:
                # Execute the search
                result = self.agent.search(query, topic)
            
            print(f"📤 Result: {result[:200]}..." if len(result) > 200 else f"📤 Result: {result}")
            
        except Exception as e:
            print(f"❌ Error invoking agent: {e}")
            raise ServerError(error=InternalError()) from e
        
        # Package result as A2A artifact
        parts = [Part(root=TextPart(text=result))]
        
        # Send result and complete task
        await updater.add_artifact(parts)
        await updater.complete()
    
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Handle task cancellation.
        
        Currently not supported for this agent.
        """
        raise ServerError(error=UnsupportedOperationError())
    
    def _validate_request(self, context: RequestContext) -> bool:
        """
        Validate the request context.
        
        Returns:
            True if validation fails, False if valid
        """
        # Currently no additional validation needed
        return False

