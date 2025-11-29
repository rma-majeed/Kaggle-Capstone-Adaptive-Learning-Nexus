"""
RAG Agent Tool for ADK Host Agent

Provides a tool for the ADK host agent to query the Textbook RAG Agent
via A2A protocol.

Note: This tool is async-compatible with ADK's uvloop.
      Do NOT use nest_asyncio as it's incompatible with uvloop.
"""

import asyncio
import json
import uuid
from typing import Optional

import httpx
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)

# Default RAG agent URL
DEFAULT_RAG_AGENT_URL = "http://localhost:10010"


async def _async_query_rag_agent(
    query: str,
    topic: Optional[str] = None,
    agent_url: str = DEFAULT_RAG_AGENT_URL,
    timeout: float = 120.0,
) -> dict:
    """
    Internal async function to query the RAG agent.
    
    Args:
        query: The search query
        topic: Optional topic context
        agent_url: RAG agent URL
        timeout: Request timeout
        
    Returns:
        Dict with status and response
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Resolve agent card
            resolver = A2ACardResolver(client, agent_url)
            try:
                card = await resolver.get_agent_card()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"RAG agent not available at {agent_url}. "
                              f"Make sure the A2A server is running. Error: {str(e)}"
                }
            
            # Create A2A client
            a2a_client = A2AClient(client, card, url=agent_url)
            
            # Build message payload
            message_text = query
            if topic:
                message_text = json.dumps({"query": query, "topic": topic})
            
            message_id = str(uuid.uuid4())
            context_id = str(uuid.uuid4())
            
            # Note: Do NOT include taskId - let the server assign it
            # Including a non-existent taskId causes "Task does not exist" error
            payload = {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message_text}],
                    "messageId": message_id,
                    "contextId": context_id,
                }
            }
            
            # Create and send request
            message_request = SendMessageRequest(
                id=message_id,
                params=MessageSendParams.model_validate(payload),
            )
            
            response: SendMessageResponse = await a2a_client.send_message(message_request)
            
            # Parse response
            if not isinstance(response.root, SendMessageSuccessResponse):
                return {
                    "status": "error",
                    "message": "Received non-success response from RAG agent"
                }
            
            if not isinstance(response.root.result, Task):
                return {
                    "status": "error", 
                    "message": "Received non-task response from RAG agent"
                }
            
            # Extract response text from artifacts
            response_content = response.root.model_dump_json(exclude_none=True)
            json_content = json.loads(response_content)
            
            response_text = ""
            if json_content.get("result", {}).get("artifacts"):
                for artifact in json_content["result"]["artifacts"]:
                    if artifact.get("parts"):
                        for part in artifact["parts"]:
                            if part.get("text"):
                                response_text += part["text"]
            
            return {
                "status": "success",
                "query": query,
                "topic": topic,
                "response": response_text,
                "source": "Textbook_RAG_Agent",
            }
            
        except httpx.ConnectError as e:
            return {
                "status": "error",
                "message": f"Cannot connect to RAG agent at {agent_url}. "
                          f"Make sure to start the A2A server first with: "
                          f"'python -m a2a_rag_agent'. Error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying RAG agent: {str(e)}"
            }


async def query_textbook_rag_agent(
    query: str,
    topic: str,
) -> dict:
    """
    Query the Textbook RAG Agent via A2A protocol.
    
    This tool searches educational textbooks to find relevant content
    for teachers. Use this when a teacher explicitly asks for
    information from textbooks.
    
    This is an async function that works with ADK's uvloop event loop.
    
    Args:
        query: The search query or question to find in the textbook.
               Example: "What are the key concepts about fractions?"
        topic: The educational topic context.
               Example: "Fractions", "Algebra", "Geometry"
    
    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - query: The original query
        - topic: The topic context
        - response: The textbook content found (if successful)
        - source: "Textbook_RAG_Agent"
        - message: Error message (if failed)
    
    Example:
        result = await query_textbook_rag_agent(
            query="Explain how to add fractions with different denominators",
            topic="Fractions"
        )
    """
    return await _async_query_rag_agent(query, topic)


def create_rag_agent_tool():
    """
    Create the RAG agent tool for use in ADK agents.
    
    Returns:
        The query_textbook_rag_agent async function configured as a tool
    """
    return query_textbook_rag_agent
