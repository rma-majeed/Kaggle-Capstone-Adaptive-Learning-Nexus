"""
A2A Server Entry Point for Textbook RAG Agent

This module starts the A2A server for the Textbook RAG Agent.
The agent can then be called by ADK host agents via A2A protocol.

Usage:
    python -m a2a_rag_agent
    
Or from the Teacher_Flow directory:
    python -m a2a_rag_agent
"""

import logging
import os
import sys
from pathlib import Path

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

from .agent_executor import RagAgentExecutor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""
    pass


class MissingTextbookError(Exception):
    """Exception for missing textbook PDF."""
    pass


def get_textbook_path() -> str:
    """
    Get the path to the textbook PDF.
    
    First checks for TEXTBOOK_PATH environment variable,
    then looks in the default data/textbooks directory.
    
    Returns:
        Path to the textbook PDF
        
    Raises:
        MissingTextbookError: If no textbook is found
    """
    # Check environment variable
    if os.getenv("TEXTBOOK_PATH"):
        path = Path(os.getenv("TEXTBOOK_PATH"))
        if path.exists():
            return str(path)
        logger.warning(f"TEXTBOOK_PATH set but file not found: {path}")
    
    # Check default directory
    default_dir = Path(__file__).parent / "data" / "textbooks"
    if default_dir.exists():
        pdf_files = list(default_dir.glob("*.pdf"))
        if pdf_files:
            logger.info(f"Found textbook: {pdf_files[0]}")
            return str(pdf_files[0])
    
    raise MissingTextbookError(
        "No textbook PDF found. Either:\n"
        "  1. Set TEXTBOOK_PATH environment variable, or\n"
        f"  2. Place a PDF in {default_dir}"
    )


def main():
    """
    Entry point for the Textbook RAG Agent A2A server.
    
    Starts the A2A server on localhost:10010.
    """
    host = "localhost"
    port = 10010
    
    try:
        # Validate API key
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")
        
        # Get textbook path (with helpful error if missing)
        try:
            textbook_path = get_textbook_path()
            logger.info(f"📚 Using textbook: {textbook_path}")
        except MissingTextbookError as e:
            logger.warning(f"⚠️ {e}")
            logger.warning("Agent will start but queries will fail until a textbook is added.")
            textbook_path = None
        
        # Define agent capabilities
        capabilities = AgentCapabilities(streaming=False)
        
        # Define agent skill
        skill = AgentSkill(
            id="textbook_search",
            name="Textbook Search",
            description="Search educational textbooks for content to help teachers. "
                       "Can find definitions, examples, explanations, and relevant excerpts.",
            tags=["education", "textbook", "search", "rag", "content"],
            examples=[
                "What does the textbook say about fractions?",
                "Find examples of algebraic equations in the textbook",
                "Search for the definition of prime numbers",
                "What content is available on geometry?",
            ],
        )
        
        # Build agent URL
        agent_host_url = os.getenv("RAG_AGENT_URL") or f"http://{host}:{port}/"
        
        # Create agent card
        agent_card = AgentCard(
            name="Textbook_RAG_Agent",
            description="A RAG agent that searches educational textbooks to help teachers "
                       "find relevant content for curriculum planning and teaching.",
            url=agent_host_url,
            version="1.0.0",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["text/plain"],
            capabilities=capabilities,
            skills=[skill],
        )
        
        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=RagAgentExecutor(textbook_path),
            task_store=InMemoryTaskStore(),
        )
        
        # Create A2A server application
        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )
        
        # Log startup info
        logger.info("=" * 60)
        logger.info("🚀 Starting Textbook RAG Agent (A2A Server)")
        logger.info(f"   URL: {agent_host_url}")
        logger.info(f"   Port: {port}")
        logger.info(f"   Textbook: {textbook_path or 'NOT CONFIGURED'}")
        logger.info("=" * 60)
        
        # Run the server
        uvicorn.run(server.build(), host=host, port=port)
        
    except MissingAPIKeyError as e:
        logger.error(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

