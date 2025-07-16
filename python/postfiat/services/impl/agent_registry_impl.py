"""
PostFiat Agent Registry Service Implementation

Generated service implementation for agent card management.
"""

import grpc
from typing import Optional, Dict, List
import uuid
import json

from postfiat.v3.messages_pb2_grpc import PostFiatAgentRegistryServiceServicer
from postfiat.v3.messages_pb2 import (
    StoreAgentCardRequest,
    SearchAgentsRequest,
    SearchAgentsResponse,
    DeleteAgentCardRequest,
    GetAgentByEnvelopeRequest,
    AgentSearchResult,
    Envelope
)
from a2a.v1.a2a_pb2 import GetAgentCardRequest, AgentCard
from postfiat.envelope.storage import ContentStorage, InlineStorage
from postfiat.exceptions import ValidationError
from google.protobuf.empty_pb2 import Empty


class AgentRegistryServiceImpl(PostFiatAgentRegistryServiceServicer):
    """Implementation of PostFiatAgentRegistry service."""
    
    def __init__(self, storage: Optional[ContentStorage] = None):
        """Initialize with storage backend.
        
        Args:
            storage: Storage backend for agent cards. If None, uses inline storage.
        """
        self.storage = storage or InlineStorage()
        self.agent_cards: Dict[str, AgentCard] = {}  # In-memory cache
        self.agent_metadata: Dict[str, dict] = {}  # PostFiat-specific metadata
    
    def GetAgentCard(self, request: GetAgentCardRequest, context: grpc.ServicerContext) -> AgentCard:
        """Get agent card (A2A compliant)."""
        try:
            # For now, return a default agent card
            # In a real implementation, this would lookup the agent
            agent_card = AgentCard()
            agent_card.name = "PostFiat Agent"
            agent_card.description = "A PostFiat-enabled agent"
            agent_card.version = "1.0.0"
            agent_card.protocol_version = "1.0"
            agent_card.url = "https://postfiat.org"
            
            return agent_card
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving agent card: {str(e)}")
            return AgentCard()
    
    def StoreAgentCard(self, request: StoreAgentCardRequest, context: grpc.ServicerContext) -> AgentCard:
        """Store agent card with PostFiat capabilities."""
        try:
            # Generate agent ID if not provided
            agent_id = request.agent_id or str(uuid.uuid4())
            
            # Store agent card
            self.agent_cards[agent_id] = request.agent_card
            
            # Store PostFiat-specific metadata
            postfiat_metadata = {
                "agent_id": agent_id,
                "envelope_processing": request.postfiat_capabilities.envelope_processing,
                "ledger_persistence": request.postfiat_capabilities.ledger_persistence,
                "context_dag_traversal": request.postfiat_capabilities.context_dag_traversal,
                "max_context_depth": request.postfiat_capabilities.max_context_depth,
                "supported_encryption_modes": list(request.postfiat_capabilities.supported_encryption_modes),
                "public_encryption_key": request.postfiat_capabilities.public_encryption_key.hex() if request.postfiat_capabilities.public_encryption_key else "",
                "public_key_algorithm": request.postfiat_capabilities.public_key_algorithm,
                "supported_semantic_capabilities": list(request.postfiat_capabilities.supported_semantic_capabilities)
            }
            
            self.agent_metadata[agent_id] = postfiat_metadata
            
            # Store in persistent storage
            self._store_agent_persistently(agent_id, request.agent_card, postfiat_metadata)
            
            return request.agent_card
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error storing agent card: {str(e)}")
            return AgentCard()
    
    def SearchAgents(self, request: SearchAgentsRequest, context: grpc.ServicerContext) -> SearchAgentsResponse:
        """Search agents by capabilities, name, etc."""
        try:
            results = []
            
            # Simple search implementation
            for agent_id, agent_card in self.agent_cards.items():
                score = self._calculate_relevance_score(agent_card, request)
                
                if score > 0:
                    result = AgentSearchResult()
                    result.agent_id = agent_id
                    result.agent_card.CopyFrom(agent_card)
                    result.relevance_score = score
                    
                    # Add PostFiat capabilities if available
                    if agent_id in self.agent_metadata:
                        metadata = self.agent_metadata[agent_id]
                        result.postfiat_capabilities.envelope_processing = metadata.get("envelope_processing", False)
                        result.postfiat_capabilities.ledger_persistence = metadata.get("ledger_persistence", False)
                        result.postfiat_capabilities.context_dag_traversal = metadata.get("context_dag_traversal", False)
                        result.postfiat_capabilities.max_context_depth = metadata.get("max_context_depth", 0)
                    
                    results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Apply limit
            if request.limit > 0:
                results = results[:request.limit]
            
            # Create response
            response = SearchAgentsResponse()
            response.results.extend(results)
            response.total_count = len(results)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error searching agents: {str(e)}")
            return SearchAgentsResponse()
    
    def DeleteAgentCard(self, request: DeleteAgentCardRequest, context: grpc.ServicerContext) -> Empty:
        """Delete agent card."""
        try:
            agent_id = request.agent_id
            
            # Remove from caches
            if agent_id in self.agent_cards:
                del self.agent_cards[agent_id]
            
            if agent_id in self.agent_metadata:
                del self.agent_metadata[agent_id]
            
            # Remove from persistent storage
            self._delete_agent_persistently(agent_id)
            
            return Empty()
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting agent card: {str(e)}")
            return Empty()
    
    def GetAgentByEnvelope(self, request: GetAgentByEnvelopeRequest, context: grpc.ServicerContext) -> AgentCard:
        """Get agent by envelope sender."""
        try:
            # Extract sender information from envelope
            envelope = request.envelope
            sender = envelope.metadata.get("sender", "")
            
            # Search for agent by sender
            for agent_id, agent_card in self.agent_cards.items():
                # Simple matching - in real implementation, this would be more sophisticated
                if sender in agent_card.name or sender in agent_card.description:
                    return agent_card
            
            # If no match found, return empty card
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Agent not found for envelope sender")
            return AgentCard()
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error finding agent by envelope: {str(e)}")
            return AgentCard()
    
    def _calculate_relevance_score(self, agent_card: AgentCard, request: SearchAgentsRequest) -> float:
        """Calculate relevance score for search."""
        score = 0.0
        
        # Query matching
        if request.query:
            query_lower = request.query.lower()
            if query_lower in agent_card.name.lower():
                score += 2.0
            if query_lower in agent_card.description.lower():
                score += 1.0
        
        # Capability matching
        if request.capabilities:
            for capability in request.capabilities:
                # Check if capability is in agent's skills
                for skill in agent_card.skills:
                    if capability.lower() in skill.name.lower() or capability.lower() in skill.description.lower():
                        score += 1.5
        
        # Organization matching
        if request.organization:
            if request.organization.lower() in agent_card.provider.organization.lower():
                score += 1.0
        
        # If no specific criteria, give base score
        if not request.query and not request.capabilities and not request.organization:
            score = 1.0
        
        return score
    
    def _store_agent_persistently(self, agent_id: str, agent_card: AgentCard, metadata: dict):
        """Store agent card in persistent storage."""
        try:
            # Serialize agent card and metadata
            agent_data = {
                "agent_id": agent_id,
                "agent_card": agent_card.SerializeToString().hex(),
                "postfiat_metadata": metadata
            }
            
            # Store using content storage
            content = json.dumps(agent_data).encode()
            descriptor = self.storage.store(content, "application/json")
            
            # Store mapping for retrieval
            # In a real implementation, this would be in a database
            
        except Exception as e:
            print(f"Warning: Failed to store agent persistently: {e}")
    
    def _delete_agent_persistently(self, agent_id: str):
        """Delete agent card from persistent storage."""
        try:
            # In a real implementation, this would delete from database
            pass
        except Exception as e:
            print(f"Warning: Failed to delete agent persistently: {e}")