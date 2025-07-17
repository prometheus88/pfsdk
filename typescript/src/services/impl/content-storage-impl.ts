/**
 * PostFiat Content Storage Service Implementation
 * 
 * Generated service implementation that uses the existing content storage backends.
 */

import { ConnectError, Code } from '@connectrpc/connect';
import { ContentStorage, InlineStorage, IPFSStorage, RedisStorage, MultipartStorage, CompositeStorage } from '../../envelope/storage';
import { 
  ContentDescriptor, 
  ContentResponse,
  StoreContentRequest, 
  RetrieveContentRequest, 
  DeleteContentRequest, 
  CanHandleUriRequest, 
  CanHandleUriResponse 
} from '../../generated/postfiat/v3/messages_pb';
import { Empty } from '@bufbuild/protobuf';

/**
 * Implementation of PostFiatContentStorage service using existing content storage backends.
 */
export class ContentStorageServiceImpl {
  private storage: ContentStorage;

  constructor(storage?: ContentStorage) {
    this.storage = storage || this.createDefaultStorage();
  }

  /**
   * Store content.
   */
  async storeContent(request: StoreContentRequest): Promise<ContentDescriptor> {
    try {
      // Validate request
      if (!request.content || request.content.length === 0) {
        throw new ConnectError('Content cannot be empty', Code.InvalidArgument);
      }

      if (!request.contentType) {
        throw new ConnectError('Content type is required', Code.InvalidArgument);
      }

      // Store content using the storage backend
      const descriptor = await this.storage.store(request.content, request.contentType);
      
      return descriptor;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`Storage error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Retrieve content by descriptor.
   */
  async retrieveContent(request: RetrieveContentRequest): Promise<ContentResponse> {
    try {
      // Validate request
      if (!request.descriptor) {
        throw new ConnectError('Content descriptor is required', Code.InvalidArgument);
      }

      // Retrieve content using the storage backend
      const content = await this.storage.retrieve(request.descriptor);
      
      // Create response
      const response = new ContentResponse();
      response.content = content;
      response.contentType = request.descriptor.contentType;
      response.size = BigInt(content.length);
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      if (error.message.includes('not found')) {
        throw new ConnectError('Content not found', Code.NotFound);
      }
      throw new ConnectError(`Retrieval error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Delete content (placeholder - not implemented in base storage).
   */
  async deleteContent(request: DeleteContentRequest): Promise<Empty> {
    throw new ConnectError('Delete operation not implemented', Code.Unimplemented);
  }

  /**
   * Check if storage can handle a URI scheme.
   */
  async canHandleUri(request: CanHandleUriRequest): Promise<CanHandleUriResponse> {
    try {
      // Validate request
      if (!request.uri) {
        throw new ConnectError('URI is required', Code.InvalidArgument);
      }

      // Check if storage can handle the URI
      const canHandle = this.storage.canHandle(request.uri);
      
      // Create response
      const response = new CanHandleUriResponse();
      response.canHandle = canHandle;
      response.storageBackend = this.getStorageBackendName();
      
      return response;
    } catch (error) {
      if (error instanceof ConnectError) {
        throw error;
      }
      throw new ConnectError(`URI check error: ${error.message}`, Code.Internal);
    }
  }

  /**
   * Create default storage backend.
   */
  private createDefaultStorage(): ContentStorage {
    // Create a composite storage with multiple backends
    const inlineStorage = new InlineStorage();
    const ipfsStorage = new IPFSStorage();
    
    // For production, you might want to add Redis storage
    // const redisStorage = new RedisStorage();
    
    return new CompositeStorage([
      inlineStorage,
      ipfsStorage
    ]);
  }

  /**
   * Get storage backend name for current storage instance.
   */
  private getStorageBackendName(): string {
    const className = this.storage.constructor.name;
    if (className.includes('Inline')) {
      return 'inline';
    } else if (className.includes('IPFS')) {
      return 'ipfs';
    } else if (className.includes('Redis')) {
      return 'redis';
    } else if (className.includes('Composite')) {
      return 'composite';
    } else {
      return 'unknown';
    }
  }
}