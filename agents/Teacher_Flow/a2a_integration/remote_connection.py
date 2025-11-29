"""
Remote Agent Connection Manager

Manages connections to remote A2A agents.
Handles agent card resolution, connection pooling, and message sending.
"""

import httpx
from typing import Optional, Callable
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    SendMessageResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)
from dotenv import load_dotenv

load_dotenv()

# Type aliases
TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


class RemoteAgentConnection:
    """
    Manages connection to a remote A2A agent.
    
    Handles:
    - HTTP client lifecycle
    - Agent card resolution
    - Message sending
    - Response parsing
    """
    
    def __init__(
        self,
        agent_card: AgentCard,
        agent_url: str,
        timeout: float = 60.0,
    ):
        """
        Initialize a connection to a remote agent.
        
        Args:
            agent_card: The agent's capability card
            agent_url: The agent's URL
            timeout: HTTP request timeout in seconds
        """
        print(f"🔗 Connecting to remote agent: {agent_card.name}")
        print(f"   URL: {agent_url}")
        
        self._httpx_client = httpx.AsyncClient(timeout=timeout)
        self.agent_client = A2AClient(
            self._httpx_client,
            agent_card,
            url=agent_url,
        )
        self.card = agent_card
        self.url = agent_url
        self.conversation_name: Optional[str] = None
        self.pending_tasks: set = set()
    
    def get_agent_card(self) -> AgentCard:
        """Get the agent's capability card."""
        return self.card
    
    async def send_message(
        self,
        message_request: SendMessageRequest,
    ) -> SendMessageResponse:
        """
        Send a message to the remote agent.
        
        Args:
            message_request: The A2A message request
            
        Returns:
            The agent's response
        """
        return await self.agent_client.send_message(message_request)
    
    async def close(self):
        """Close the HTTP client connection."""
        await self._httpx_client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


async def resolve_agent_card(
    agent_url: str,
    timeout: float = 30.0,
) -> Optional[AgentCard]:
    """
    Resolve an agent's capability card from its URL.
    
    Args:
        agent_url: The agent's URL (e.g., "http://localhost:10010")
        timeout: HTTP request timeout
        
    Returns:
        The agent's card, or None if resolution fails
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resolver = A2ACardResolver(client, agent_url)
            card = await resolver.get_agent_card()
            print(f"✅ Resolved agent card: {card.name}")
            return card
        except httpx.ConnectError as e:
            print(f"❌ Failed to connect to {agent_url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Failed to resolve agent card: {e}")
            return None


async def create_remote_connection(
    agent_url: str,
    timeout: float = 60.0,
) -> Optional[RemoteAgentConnection]:
    """
    Create a connection to a remote A2A agent.
    
    Args:
        agent_url: The agent's URL
        timeout: HTTP request timeout
        
    Returns:
        RemoteAgentConnection if successful, None otherwise
    """
    card = await resolve_agent_card(agent_url, timeout=30.0)
    if card is None:
        return None
    
    return RemoteAgentConnection(
        agent_card=card,
        agent_url=agent_url,
        timeout=timeout,
    )

