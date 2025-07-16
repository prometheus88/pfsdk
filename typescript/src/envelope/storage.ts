/**
 * Storage backends for PostFiat envelope content.
 * 
 * Provides different strategies for storing and retrieving content.
 */

import { ContentDescriptor, Envelope, CoreMessage, MultiPartMessagePart, MessageType, EncryptionMode } from '../generated/postfiat/v3/messages_pb';
import { createHash } from 'crypto';

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Abstract base class for content storage strategies.
 */
export abstract class ContentStorage {
  /**
   * Store content and return a descriptor.
   */
  abstract store(content: Uint8Array, contentType: string): Promise<ContentDescriptor>;

  /**
   * Retrieve content from storage.
   */
  abstract retrieve(descriptor: ContentDescriptor): Promise<Uint8Array>;

  /**
   * Check if this storage can handle the given URI scheme.
   */
  abstract canHandle(uri: string): boolean;
}

/**
 * IPFS content storage implementation.
 */
export class IPFSStorage extends ContentStorage {
  private gatewayUrl: string;
  private _client: any;

  constructor(gatewayUrl: string = 'http://localhost:5001') {
    super();
    this.gatewayUrl = gatewayUrl;
  }

  private async getClient() {
    if (!this._client) {
      try {
        const { create } = await import('ipfs-http-client');
        this._client = create({ url: this.gatewayUrl });
      } catch (error) {
        throw new Error(
          'ipfs-http-client is required for IPFS storage. ' +
          'Install with: npm install ipfs-http-client'
        );
      }
    }
    return this._client;
  }

  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    // Calculate content hash
    const contentHash = createHash('sha256').update(content).digest();
    
    let cid: string;
    let simulated = false;
    
    try {
      // Try actual IPFS storage
      const ipfsClient = await this.getClient();
      const result = await ipfsClient.add(content);
      cid = result.cid.toString();
    } catch (error) {
      // Fallback to simulated CID if IPFS is not available
      cid = `Qm${contentHash.toString('hex').substring(0, 44)}`;
      simulated = true;
    }
    
    const descriptor = new ContentDescriptor();
    descriptor.setUri(`ipfs://${cid}`);
    descriptor.setContentType(contentType);
    descriptor.setContentLength(content.length);
    descriptor.setContentHash(contentHash);
    
    const metadataMap = descriptor.getMetadataMap();
    metadataMap.set('storage_provider', 'ipfs');
    metadataMap.set('gateway_url', this.gatewayUrl);
    if (simulated) {
      metadataMap.set('simulated', 'true');
    }
    
    return descriptor;
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    if (!this.canHandle(descriptor.getUri())) {
      throw new ValidationError(`Invalid IPFS URI: ${descriptor.getUri()}`);
    }

    // Extract CID from URI
    const cid = descriptor.getUri().substring(7); // Remove "ipfs://" prefix
    
    try {
      const ipfsClient = await this.getClient();
      const chunks: Uint8Array[] = [];
      for await (const chunk of ipfsClient.cat(cid)) {
        chunks.push(chunk);
      }
      
      // Combine chunks into single Uint8Array
      const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
      const result = new Uint8Array(totalLength);
      let offset = 0;
      for (const chunk of chunks) {
        result.set(chunk, offset);
        offset += chunk.length;
      }
      return result;
    } catch (error: any) {
      throw new Error(`Failed to retrieve content from IPFS: ${error.message}`);
    }
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('ipfs://');
  }
}

/**
 * Storage-agnostic multipart message chunking.
 * 
 * This storage backend has no knowledge of the underlying ledger.
 * It just creates multipart envelopes that can be stored anywhere.
 */
export class MultipartStorage extends ContentStorage {
  private maxPartSize: number;

  constructor(maxPartSize: number = 800) {
    super();
    this.maxPartSize = maxPartSize;
  }

  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    // Generate unique message ID
    const messageId = crypto.randomUUID();
    
    // Calculate content hash
    const contentHash = createHash('sha256').update(content).digest();
    
    // Calculate number of parts needed
    const totalParts = Math.ceil(content.length / this.maxPartSize);
    
    // Create multipart URI - describes how to find all parts
    const uri = `multipart://${messageId}`;
    
    const descriptor = new ContentDescriptor();
    descriptor.setUri(uri);
    descriptor.setContentType(contentType);
    descriptor.setContentLength(content.length);
    descriptor.setContentHash(contentHash);
    
    const metadataMap = descriptor.getMetadataMap();
    metadataMap.set('storage_provider', 'multipart');
    metadataMap.set('message_id', messageId);
    metadataMap.set('total_parts', totalParts.toString());
    metadataMap.set('part_size', this.maxPartSize.toString());
    
    return descriptor;
  }

  /**
   * Create multipart envelopes for multipart storage.
   */
  async createPartEnvelopes(
    content: Uint8Array,
    descriptor: ContentDescriptor,
    encryptionMode: EncryptionMode = EncryptionMode.PROTECTED,
    baseMetadata: { [key: string]: string } = {}
  ): Promise<Set<Envelope>> {
    if (!this.canHandle(descriptor.getUri())) {
      throw new ValidationError(`Invalid multipart URI: ${descriptor.getUri()}`);
    }

    const messageId = descriptor.getMetadataMap().get('message_id');
    const totalParts = parseInt(descriptor.getMetadataMap().get('total_parts') || '0');

    if (!messageId || totalParts === 0) {
      throw new ValidationError('Missing multipart metadata');
    }

    const envelopes = new Set<Envelope>();

    for (let i = 0; i < content.length; i += this.maxPartSize) {
      const partNumber = Math.floor(i / this.maxPartSize) + 1;
      const chunkContent = content.slice(i, i + this.maxPartSize);

      // Create multipart message part
      const multipart = new MultiPartMessagePart();
      multipart.setMessageId(messageId);
      multipart.setPartNumber(partNumber);
      multipart.setTotalParts(totalParts);
      multipart.setContent(chunkContent);
      multipart.setCompleteMessageHash(descriptor.getContentHash_asB64());

      // Create envelope for this part
      const messageBytes = multipart.serializeBinary();

      const metadata = { ...baseMetadata };
      metadata['multipart'] = `${partNumber}/${totalParts}`;
      metadata['message_id'] = messageId;

      const envelope = new Envelope();
      envelope.setVersion(1);
      envelope.setContentHash(createHash('sha256').update(messageBytes).digest('hex'));
      envelope.setMessageType(MessageType.MULTIPART_MESSAGE_PART);
      envelope.setEncryption(encryptionMode);
      envelope.setMessage(messageBytes);
      
      const metadataMap = envelope.getMetadataMap();
      Object.entries(metadata).forEach(([key, value]) => {
        metadataMap.set(key, value);
      });

      envelopes.add(envelope);
    }

    return envelopes;
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    throw new Error('Multipart retrieval requires collecting all envelope parts by message_id');
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('multipart://');
  }
}

/**
 * HTTP/HTTPS content storage implementation.
 */
export class HTTPStorage extends ContentStorage {
  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    // This would typically POST to a content server
    throw new Error('HTTP storage not yet implemented');
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    if (!this.canHandle(descriptor.getUri())) {
      throw new ValidationError(`Invalid HTTP URI: ${descriptor.getUri()}`);
    }

    // TODO: Implement HTTP retrieval
    // const response = await fetch(descriptor.getUri());
    // return new Uint8Array(await response.arrayBuffer());
    
    throw new Error('HTTP retrieval not yet implemented');
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('http://') || uri.startsWith('https://');
  }
}

/**
 * Composite storage that delegates to appropriate backend.
 */
export class CompositeStorage extends ContentStorage {
  private storages: ContentStorage[];

  constructor(storages: ContentStorage[]) {
    super();
    this.storages = storages;
  }

  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    if (this.storages.length === 0) {
      throw new ValidationError('No storage backends configured');
    }

    // Use first storage backend for storing
    return this.storages[0].store(content, contentType);
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    for (const storage of this.storages) {
      if (storage.canHandle(descriptor.getUri())) {
        return storage.retrieve(descriptor);
      }
    }

    throw new ValidationError(`No storage backend can handle URI: ${descriptor.getUri()}`);
  }

  canHandle(uri: string): boolean {
    return this.storages.some(storage => storage.canHandle(uri));
  }
}