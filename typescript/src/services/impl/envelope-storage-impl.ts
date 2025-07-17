/**
 * PostFiat Envelope Storage Service Implementation
 * 
 * Generated service implementation that uses the existing envelope storage backends.
 */

import { ConnectError, Code } from '@connectrpc/connect';
import { EnvelopeStore } from '../../envelope/envelope-store';
import { RedisEnvelopeStore } from '../../envelope/stores/redis-store';
import { 
  Envelope,
  StoreEnvelopeRequest, 
  StoreEnvelopeResponse,
  RetrieveEnvelopeRequest, 
  SearchEnvelopesRequest, 
  SearchEnvelopesResponse,
  DeleteEnvelopeRequest, 
  EnvelopeExistsRequest, 
  EnvelopeExistsResponse,
  FindEnvelopesByContentHashRequest, 
  FindEnvelopesByContentHashResponse,
  FindEnvelopesByContextRequest, 
  FindEnvelopesByContextResponse,
  ListEnvelopesBySenderRequest, 
  ListEnvelopesBySenderResponse
} from '../../generated/postfiat/v3/messages_pb';
import { Empty } from '@bufbuild/protobuf';

/**
 * Implementation of PostFiatEnvelopeStorage service using existing envelope stores.
 */
export class EnvelopeStorageServiceImpl {
  private store: EnvelopeStore;

  constructor(store?: EnvelopeStore) {
    this.store = store || this.createDefaultStore();
  }

  /**
   * Store envelope.
   */
  async storeEnvelope(request: StoreEnvelopeRequest): Promise<StoreEnvelopeResponse> {
    try {
      // Validate request
      if (!request.envelope) {
        throw new ConnectError('Envelope is required', Code.InvalidArgument);
      }

      // Get preferred storage if specified
      let store = this.store;
      if (request.preferredStorage) {
        const preferredStore = this.getStoreByType(request.preferredStorage);
        if (!preferredStore) {
          throw new ConnectError(`Unknown storage type: ${request.preferredStorage}`, Code.InvalidArgument);
        }
        store = preferredStore;
      }

      // Store envelope
      const envelopeId = await store.store(request.envelope);
      
      // Create response
      const response = new StoreEnvelopeResponse();
      response.envelopeId = envelopeId;
      response.storageBackend = this.getStoreBackendName(store);
      
      // Add metadata from envelope
      if (request.envelope.metadata) {
        response.metadata = { ...request.envelope.metadata };
      }
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Storage error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Retrieve envelope by ID.
   */
  async retrieveEnvelope(request: RetrieveEnvelopeRequest): Promise<Envelope> {
    try {
      // Validate request
      if (!request.envelopeId) {
        throw new ConnectError('Envelope ID is required', Code.InvalidArgument);
      }

      // Retrieve envelope
      const envelope = await this.store.retrieve(request.envelopeId);
      
      return envelope;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      if (error.message.includes('not found')) {
        throw new ConnectError('Envelope not found', Code.NotFound);
      }
      throw new ConnectError(`Retrieval error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Search envelopes (placeholder - not implemented).
   */
  async searchEnvelopes(request: SearchEnvelopesRequest): Promise<SearchEnvelopesResponse> {
    throw new ConnectError('Search operation not implemented', Code.Unimplemented);
  }

  /**
   * Delete envelope.
   */
  async deleteEnvelope(request: DeleteEnvelopeRequest): Promise<Empty> {
    try {
      // Validate request
      if (!request.envelopeId) {
        throw new ConnectError('Envelope ID is required', Code.InvalidArgument);
      }

      // Delete envelope
      const deleted = await this.store.delete(request.envelopeId);
      
      if (!deleted) {
        throw new ConnectError('Envelope not found', Code.NotFound);
      }
      
      return new Empty();
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Delete error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Check if envelope exists.
   */
  async envelopeExists(request: EnvelopeExistsRequest): Promise<EnvelopeExistsResponse> {
    try {
      // Validate request
      if (!request.envelopeId) {
        throw new ConnectError('Envelope ID is required', Code.InvalidArgument);
      }

      // Check existence
      const exists = await this.store.exists(request.envelopeId);
      
      // Create response
      const response = new EnvelopeExistsResponse();
      response.exists = exists;
      response.storageBackend = this.getStoreBackendName(this.store);
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Existence check error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Find envelopes by content hash.
   */
  async findEnvelopesByContentHash(request: FindEnvelopesByContentHashRequest): Promise<FindEnvelopesByContentHashResponse> {
    try {
      // Validate request
      if (!request.contentHash) {
        throw new ConnectError('Content hash is required', Code.InvalidArgument);
      }

      // Find envelopes
      const envelopes = await this.store.findByContentHash(request.contentHash);
      
      // Apply limit if specified
      let limitedEnvelopes = envelopes;
      if (request.limit > 0) {
        limitedEnvelopes = envelopes.slice(0, Number(request.limit));
      }
      
      // Create response
      const response = new FindEnvelopesByContentHashResponse();
      response.envelopes = limitedEnvelopes;
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Search error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Find envelopes by context.
   */
  async findEnvelopesByContext(request: FindEnvelopesByContextRequest): Promise<FindEnvelopesByContextResponse> {
    try {
      // Validate request
      if (!request.contextHash) {
        throw new ConnectError('Context hash is required', Code.InvalidArgument);
      }

      // Find envelopes
      const envelopes = await this.store.findByContext(request.contextHash);
      
      // Apply limit if specified
      let limitedEnvelopes = envelopes;
      if (request.limit > 0) {
        limitedEnvelopes = envelopes.slice(0, Number(request.limit));
      }
      
      // Create response
      const response = new FindEnvelopesByContextResponse();
      response.envelopes = limitedEnvelopes;
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Search error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * List envelopes by sender.
   */
  async listEnvelopesBySender(request: ListEnvelopesBySenderRequest): Promise<ListEnvelopesBySenderResponse> {
    try {
      // Validate request
      if (!request.sender) {
        throw new ConnectError('Sender is required', Code.InvalidArgument);
      }

      // List envelopes
      const envelopes = await this.store.listBySender(request.sender, Number(request.limit || 100));
      
      // Create response
      const response = new ListEnvelopesBySenderResponse();
      response.envelopes = envelopes;
      response.totalCount = BigInt(envelopes.length);
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`List error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Create default envelope store.
   */
  private createDefaultStore(): EnvelopeStore {
    // For now, default to Redis store
    // In production, you might want to use a composite store or different backend
    return new RedisEnvelopeStore();
  }

  /**
   * Get store backend by type name.
   */
  private getStoreByType(storageType: string): EnvelopeStore | null {
    switch (storageType) {
      case 'redis':
        return new RedisEnvelopeStore();
      // Add other store types as they are implemented
      // case 'evm':
      //   return new EVMEnvelopeStore();
      // case 'xrpl':
      //   return new XRPLEnvelopeStore();
      default:
        return null;
    }
  }

  /**
   * Get backend name for store instance.
   */
  private getStoreBackendName(store: EnvelopeStore): string {
    const className = store.constructor.name;
    if (className.includes('Redis')) {
      return 'redis';
    } else if (className.includes('EVM')) {
      return 'evm';
    } else if (className.includes('XRPL')) {
      return 'xrpl';
    } else {
      return 'unknown';
    }
  }
}