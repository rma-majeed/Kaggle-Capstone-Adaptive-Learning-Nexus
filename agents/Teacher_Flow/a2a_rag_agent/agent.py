"""
Textbook RAG Agent (CrewAI)

A CrewAI agent that searches PDF textbooks to find educational content.
This agent is exposed via A2A protocol to be called by the ADK host agent.

Demonstrates:
- CrewAI agent with PDFSearchTool
- A2A protocol integration
- RAG (Retrieval Augmented Generation) pattern
- Google Gemini embeddings (instead of default OpenAI)
"""

import os
from pathlib import Path
from typing import Optional

from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import PDFSearchTool
from dotenv import load_dotenv

load_dotenv()

# Default textbook directory
DEFAULT_TEXTBOOK_DIR = Path(__file__).parent / "data" / "textbooks"


def create_pdf_tool_with_google_embeddings(pdf_path: str) -> PDFSearchTool:
    """
    Create a PDFSearchTool configured to use Google embeddings.
    
    This uses Google's embedding-001 model instead of OpenAI's default,
    allowing the tool to work with just GOOGLE_API_KEY.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        PDFSearchTool configured with Google embeddings
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    # Configure PDFSearchTool with Google embeddings
    # Using google-generativeai provider with embedding-001 model
    # Note: Provider must be exactly "google-generativeai" (not "google")
    config = {
        "llm": {
            "provider": "google",
            "config": {
                "model": "gemini-2.0-flash",
                "api_key": google_api_key,
            }
        },
        "embedding_model": {
            "provider": "google-generativeai",
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "api_key": google_api_key,
            }
        }
    }
    
    print(f"🔧 Configuring PDFSearchTool with Google embeddings")
    print(f"   Embedding model: models/embedding-001")
    print(f"   LLM: gemini-2.0-flash")
    
    return PDFSearchTool(pdf=pdf_path, config=config)


class TextbookRagAgent:
    """
    CrewAI-based Textbook RAG Agent.
    
    Assists teachers by retrieving relevant content from textbooks
    to answer questions about educational topics.
    
    Uses Google embeddings (embedding-001) instead of OpenAI,
    so only GOOGLE_API_KEY is required.
    """
    
    SUPPORTED_CONTENT_TYPES = ["text/plain"]
    
    def __init__(self, textbook_path: Optional[str] = None):
        """
        Initialize the Textbook RAG Agent.
        
        Args:
            textbook_path: Path to the PDF textbook. If None, uses first PDF in default dir.
        """
        # Validate API key first
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        # Resolve textbook path
        if textbook_path:
            self.textbook_path = Path(textbook_path)
        else:
            # Find first PDF in default directory
            pdf_files = list(DEFAULT_TEXTBOOK_DIR.glob("*.pdf"))
            if pdf_files:
                self.textbook_path = pdf_files[0]
            else:
                raise FileNotFoundError(
                    f"No PDF files found in {DEFAULT_TEXTBOOK_DIR}. "
                    "Please add a textbook PDF or specify a path."
                )
        
        if not self.textbook_path.exists():
            raise FileNotFoundError(f"Textbook not found: {self.textbook_path}")
        
        print(f"📚 Loading textbook: {self.textbook_path}")
        
        # Initialize PDF Search Tool with Google embeddings
        self.pdf_tool = create_pdf_tool_with_google_embeddings(str(self.textbook_path))
        #self.pdf_tool = create_pdf_tool_with_google_embeddings(str(DEFAULT_TEXTBOOK_DIR))
        # Initialize LLM (also using Google/Gemini)
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        
        # Create the CrewAI Agent
        self.agent = Agent(
            role="Educational Content Specialist",
            goal="Find accurate and relevant information from textbooks to support teachers",
            backstory="""You are an expert educational content specialist with deep 
            knowledge of curriculum materials. Your job is to help teachers find 
            exactly what they need in textbooks. You have access to a PDF textbook 
            and can search it instantly. When a teacher asks a question, you look 
            it up in the textbook and provide precise, cited information.
            
            You always:
            - Quote directly from the textbook when possible
            - Provide page references if available
            - Explain concepts in teacher-friendly language
            - Suggest how the content could be used in teaching
            """,
            tools=[self.pdf_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )
    
    def search(self, query: str, topic: Optional[str] = None) -> str:
        """
        Search the textbook for information matching the query.
        
        Args:
            query: The question or topic to search for
            topic: Optional topic context to refine the search
            
        Returns:
            String containing the search results and relevant excerpts
        """
        topic_context = f"Topic context: {topic}" if topic else ""
        
        task = Task(
            description=f"""
            Search the textbook for information about: "{query}"
            {topic_context}
            
            Instructions:
            1. Use the PDFSearchTool to find relevant sections in the textbook.
            2. Extract key definitions, examples, and explanations.
            3. Provide direct quotes from the textbook when relevant.
            4. Include page references if available.
            5. Summarize the key points that would be useful for a teacher.
            
            If the information is not found in the textbook, clearly state that.
            """,
            agent=self.agent,
            expected_output="""A comprehensive answer based on the textbook content, including:
            - Direct quotes or excerpts from the textbook
            - Key concepts and definitions found
            - Relevant examples from the text
            - Page references if available
            - A brief summary for the teacher"""
        )
        
        # Execute via CrewAI
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )
        
        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            return f"Error searching textbook: {str(e)}"
    
    def get_textbook_info(self) -> dict:
        """Get information about the loaded textbook."""
        return {
            "path": str(self.textbook_path),
            "name": self.textbook_path.name,
            "exists": self.textbook_path.exists(),
        }


# Singleton instance (created when module is imported with a textbook)
_agent_instance: Optional[TextbookRagAgent] = None


def get_agent(textbook_path: Optional[str] = None) -> TextbookRagAgent:
    """
    Get or create the TextbookRagAgent singleton.
    
    Args:
        textbook_path: Optional path to textbook PDF
        
    Returns:
        TextbookRagAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TextbookRagAgent(textbook_path)
    return _agent_instance

