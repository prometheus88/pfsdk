/**
 * PostFiat Agent Registry Service Implementation
 * 
 * Generated service implementation for agent card management.
 */

import { ConnectError, Code } from '@connectrpc/connect';
import { ContentStorage, InlineStorage } from '../../envelope/storage';
import { 
  StoreAgentCardRequest, 
  SearchAgentsRequest, 
  SearchAgentsResponse,
  DeleteAgentCardRequest, 
  GetAgentByEnvelopeRequest,
  AgentSearchResult,
  Envelope
} from '../../generated/postfiat/v3/messages_pb';
import { GetAgentCardRequest, AgentCard } from '../../generated/a2a/v1/a2a_pb';
import { Empty } from '@bufbuild/protobuf';

/**
 * Implementation of PostFiatAgentRegistry service.
 */
export class AgentRegistryServiceImpl {
  private storage: ContentStorage;
  private agentCards: Map<string, AgentCard>;
  private agentMetadata: Map<string, any>;

  constructor(storage?: ContentStorage) {
    this.storage = storage || new InlineStorage();
    this.agentCards = new Map();
    this.agentMetadata = new Map();
  }

  /**
   * Get agent card (A2A compliant).
   */
  async getAgentCard(request: GetAgentCardRequest): Promise<AgentCard> {
    try {
      // For now, return a default agent card
      // In a real implementation, this would lookup the agent
      const agentCard = new AgentCard();
      agentCard.name = 'PostFiat Agent';
      agentCard.description = 'A PostFiat-enabled agent';
      agentCard.version = '1.0.0';
      agentCard.protocolVersion = '1.0';
      agentCard.url = 'https://postfiat.org';
      
      return agentCard;
    } catch (error) {
      throw new ConnectError(`Error retrieving agent card: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Store agent card with PostFiat capabilities.
   */
  async storeAgentCard(request: StoreAgentCardRequest): Promise<AgentCard> {
    try {
      // Validate request
      if (!request.agentCard) {
        throw new ConnectError('Agent card is required', Code.InvalidArgument);
      }

      // Generate agent ID if not provided
      const agentId = request.agentId || this.generateAgentId();
      
      // Store agent card
      this.agentCards.set(agentId, request.agentCard);
      
      // Store PostFiat-specific metadata
      const postfiatMetadata = {
        agentId,
        envelopeProcessing: request.postfiatCapabilities?.envelopeProcessing || false,
        ledgerPersistence: request.postfiatCapabilities?.ledgerPersistence || false,
        contextDagTraversal: request.postfiatCapabilities?.contextDagTraversal || false,
        maxContextDepth: request.postfiatCapabilities?.maxContextDepth || 0,
        supportedEncryptionModes: request.postfiatCapabilities?.supportedEncryptionModes || [],
        publicEncryptionKey: request.postfiatCapabilities?.publicEncryptionKey || new Uint8Array(),
        publicKeyAlgorithm: request.postfiatCapabilities?.publicKeyAlgorithm || '',
        supportedSemanticCapabilities: request.postfiatCapabilities?.supportedSemanticCapabilities || []
      };
      
      this.agentMetadata.set(agentId, postfiatMetadata);
      
      // Store in persistent storage
      await this.storeAgentPersistently(agentId, request.agentCard, postfiatMetadata);
      
      return request.agentCard;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Error storing agent card: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Search agents by capabilities, name, etc.
   */
  async searchAgents(request: SearchAgentsRequest): Promise<SearchAgentsResponse> {
    try {
      const results: AgentSearchResult[] = [];
      
      // Simple search implementation
      for (const [agentId, agentCard] of this.agentCards) {
        const score = this.calculateRelevanceScore(agentCard, request);
        
        if (score > 0) {
          const result = new AgentSearchResult();
          result.agentId = agentId;
          result.agentCard = agentCard;
          result.relevanceScore = score;
          
          // Add PostFiat capabilities if available
          const metadata = this.agentMetadata.get(agentId);
          if (metadata) {
            // Note: This would need proper protobuf message creation
            // result.postfiatCapabilities = this.createPostFiatCapabilities(metadata);
          }
          
          results.push(result);
        }
      }
      
      // Sort by relevance score
      results.sort((a, b) => b.relevanceScore - a.relevanceScore);
      
      // Apply limit
      let limitedResults = results;
      if (request.limit > 0) {
        limitedResults = results.slice(0, Number(request.limit));
      }
      
      // Create response
      const response = new SearchAgentsResponse();
      response.results = limitedResults;
      response.totalCount = BigInt(limitedResults.length);
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Error searching agents: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Delete agent card.
   */
  async deleteAgentCard(request: DeleteAgentCardRequest): Promise<Empty> {
    try {
      // Validate request
      if (!request.agentId) {
        throw new ConnectError('Agent ID is required', Code.InvalidArgument);
      }

      const agentId = request.agentId;
      
      // Remove from caches
      this.agentCards.delete(agentId);
      this.agentMetadata.delete(agentId);
      
      // Remove from persistent storage
      await this.deleteAgentPersistently(agentId);
      
      return new Empty();
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Error deleting agent card: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Get agent by envelope sender.
   */
  async getAgentByEnvelope(request: GetAgentByEnvelopeRequest): Promise<AgentCard> {
    try {
      // Validate request
      if (!request.envelope) {
        throw new ConnectError('Envelope is required', Code.InvalidArgument);
      }

      // Extract sender information from envelope
      const envelope = request.envelope;
      const sender = envelope.metadata?.['sender'] || '';
      
      // Search for agent by sender
      for (const [agentId, agentCard] of this.agentCards) {
        // Simple matching - in real implementation, this would be more sophisticated
        if (agentCard.name.includes(sender) || agentCard.description.includes(sender)) {
          return agentCard;
        }
      }
      
      // If no match found, return empty card
      throw new ConnectError('Agent not found for envelope sender', Code.NotFound);
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Error finding agent by envelope: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Calculate relevance score for search.
   */
  private calculateRelevanceScore(agentCard: AgentCard, request: SearchAgentsRequest): number {
    let score = 0;
    
    // Query matching
    if (request.query) {
      const queryLower = request.query.toLowerCase();
      if (agentCard.name.toLowerCase().includes(queryLower)) {
        score += 2.0;
      }
      if (agentCard.description.toLowerCase().includes(queryLower)) {
        score += 1.0;
      }
    }
    
    // Capability matching
    if (request.capabilities && request.capabilities.length > 0) {
      for (const capability of request.capabilities) {
        // Check if capability is in agent's skills
        for (const skill of agentCard.skills) {
          if (skill.name.toLowerCase().includes(capability.toLowerCase()) || 
              skill.description.toLowerCase().includes(capability.toLowerCase())) {
            score += 1.5;
          }
        }
      }
    }
    
    // Organization matching
    if (request.organization) {
      if (agentCard.provider?.organization?.toLowerCase().includes(request.organization.toLowerCase())) {
        score += 1.0;
      }
    }
    
    // If no specific criteria, give base score
    if (!request.query && (!request.capabilities || request.capabilities.length === 0) && !request.organization) {
      score = 1.0;
    }
    
    return score;
  }

  /**
   * Generate a unique agent ID.
   */
  private generateAgentId(): string {
    return `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Store agent card in persistent storage.
   */
  private async storeAgentPersistently(agentId: string, agentCard: AgentCard, metadata: any): Promise<void> {
    try {
      // Serialize agent card and metadata
      const agentData = {
        agentId,
        agentCard: Buffer.from(agentCard.toBinary()).toString('hex'),
        postfiatMetadata: metadata
      };
      
      // Store using content storage
      const content = new TextEncoder().encode(JSON.stringify(agentData));
      await this.storage.store(content, 'application/json');
      
      // Store mapping for retrieval
      // In a real implementation, this would be in a database
    } catch (error) {
      console.warn(`Failed to store agent persistently: ${error.message}`);
    }
  }

  /**
   * Delete agent card from persistent storage.
   */
  private async deleteAgentPersistently(agentId: string): Promise<void> {
    try {
      // In a real implementation, this would delete from database
    } catch (error) {
      console.warn(`Failed to delete agent persistently: ${error.message}`);
    }
  }
}