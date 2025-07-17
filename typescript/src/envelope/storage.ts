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
    descriptor.uri = `ipfs:${cid}`;
    descriptor.contentType = contentType;
    descriptor.contentLength = BigInt(content.length);
    descriptor.contentHash = contentHash;
    
    descriptor.metadata['storage_provider'] = 'ipfs';
    descriptor.metadata['gateway_url'] = this.gatewayUrl;
    if (simulated) {
      descriptor.metadata['simulated'] = 'true';
    }
    
    return descriptor;
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    if (!this.canHandle(descriptor.uri)) {
      throw new ValidationError(`Invalid IPFS URI: ${descriptor.uri}`);
    }

    // Extract CID from URI
    const cid = descriptor.uri.substring(5); // Remove "ipfs:" prefix
    
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
    return uri.startsWith('ipfs:');
  }
}

/**
 * Redis content storage implementation.
 */
export class RedisStorage extends ContentStorage {
  private redisUrl: string;
  private keyPrefix: string;
  private _client: any;

  constructor(redisUrl: string = 'redis://localhost:6379', keyPrefix: string = 'postfiat:content') {
    super();
    this.redisUrl = redisUrl;
    this.keyPrefix = keyPrefix;
  }

  private async getClient() {
    if (!this._client) {
      try {
        const Redis = await import('ioredis');
        this._client = new Redis.default(this.redisUrl);
      } catch (error) {
        throw new Error(
          'ioredis is required for Redis storage. ' +
          'Install with: npm install ioredis'
        );
      }
    }
    return this._client;
  }

  private contentKey(contentHash: Uint8Array): string {
    return `${this.keyPrefix}:${Buffer.from(contentHash).toString('hex')}`;
  }

  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    // Calculate content hash
    const contentHash = createHash('sha256').update(content).digest();
    
    // Store content in Redis
    const key = this.contentKey(contentHash);
    
    // Store content and metadata together
    const contentData = {
      content: Buffer.from(content).toString('base64'),
      content_type: contentType,
      content_length: content.length,
      content_hash: Buffer.from(contentHash).toString('hex')
    };
    
    try {
      const client = await this.getClient();
      await client.set(key, JSON.stringify(contentData));
      
      const descriptor = new ContentDescriptor();
      descriptor.uri = `redis:${Buffer.from(contentHash).toString('hex')}`;
      descriptor.contentType = contentType;
      descriptor.contentLength = BigInt(content.length);
      descriptor.contentHash = contentHash;
      
      descriptor.metadata['storage_provider'] = 'redis';
      descriptor.metadata['redis_key'] = key;
      descriptor.metadata['redis_url'] = this.redisUrl;
      
      return descriptor;
    } catch (error: any) {
      throw new Error(`Failed to store content in Redis: ${error.message}`);
    }
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    if (!this.canHandle(descriptor.uri)) {
      throw new ValidationError(`Invalid Redis URI: ${descriptor.uri}`);
    }

    // Extract content hash from URI
    const contentHashHex = descriptor.uri.substring(6); // Remove "redis:" prefix
    const contentHash = Buffer.from(contentHashHex, 'hex');
    
    const key = this.contentKey(contentHash);
    
    try {
      const client = await this.getClient();
      const contentData = await client.get(key);
      
      if (!contentData) {
        throw new Error(`Content not found in Redis: ${descriptor.uri}`);
      }
      
      const data = JSON.parse(contentData);
      const content = Buffer.from(data.content, 'base64');
      
      // Verify content hash
      const actualHash = createHash('sha256').update(content).digest();
      if (!Buffer.from(actualHash).equals(contentHash)) {
        throw new Error(`Content hash mismatch for ${descriptor.uri}`);
      }
      
      return new Uint8Array(content);
    } catch (error: any) {
      throw new Error(`Failed to retrieve content from Redis: ${error.message}`);
    }
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('redis:');
  }
}

/**
 * Inline content storage - stores content directly in descriptor.
 */
export class InlineStorage extends ContentStorage {
  async store(content: Uint8Array, contentType: string): Promise<ContentDescriptor> {
    // Calculate content hash
    const contentHash = createHash('sha256').update(content).digest();
    
    // Encode content as base64 for inline storage
    const contentB64 = Buffer.from(content).toString('base64');
    
    const descriptor = new ContentDescriptor();
    descriptor.uri = `data:${contentType};base64,${contentB64}`;
    descriptor.contentType = contentType;
    descriptor.contentLength = BigInt(content.length);
    descriptor.contentHash = contentHash;
    
    descriptor.metadata['storage_provider'] = 'inline';
    descriptor.metadata['content_data'] = contentB64;
    
    return descriptor;
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    if (!this.canHandle(descriptor.uri)) {
      throw new ValidationError(`Invalid data URI: ${descriptor.uri}`);
    }

    try {
      // Parse data URI: data:contentType;base64,data
      const match = descriptor.uri.match(/^data:([^;]+);base64,(.+)$/);
      if (!match) {
        throw new Error('Invalid data URI format');
      }
      
      const contentB64 = match[2];
      const content = Buffer.from(contentB64, 'base64');
      
      // Verify content hash
      const actualHash = createHash('sha256').update(content).digest();
      if (!Buffer.from(actualHash).equals(Buffer.from(descriptor.contentHash))) {
        throw new Error('Content hash mismatch for inline content');
      }
      
      return new Uint8Array(content);
    } catch (error: any) {
      throw new Error(`Failed to retrieve inline content: ${error.message}`);
    }
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('data:');
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
    const uri = `multipart:${messageId}`;
    
    const descriptor = new ContentDescriptor();
    descriptor.uri = uri;
    descriptor.contentType = contentType;
    descriptor.contentLength = BigInt(content.length);
    descriptor.contentHash = contentHash;
    
    descriptor.metadata['storage_provider'] = 'multipart';
    descriptor.metadata['message_id'] = messageId;
    descriptor.metadata['total_parts'] = totalParts.toString();
    descriptor.metadata['part_size'] = this.maxPartSize.toString();
    
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
    if (!this.canHandle(descriptor.uri)) {
      throw new ValidationError(`Invalid multipart URI: ${descriptor.uri}`);
    }

    const messageId = descriptor.metadata['message_id'];
    const totalParts = parseInt(descriptor.metadata['total_parts'] || '0');

    if (!messageId || totalParts === 0) {
      throw new ValidationError('Missing multipart metadata');
    }

    const envelopes = new Set<Envelope>();

    for (let i = 0; i < content.length; i += this.maxPartSize) {
      const partNumber = Math.floor(i / this.maxPartSize) + 1;
      const chunkContent = content.slice(i, i + this.maxPartSize);

      // Create multipart message part
      const multipart = new MultiPartMessagePart();
      multipart.messageId = messageId;
      multipart.partNumber = partNumber;
      multipart.totalParts = totalParts;
      multipart.content = chunkContent;
      multipart.completeMessageHash = Buffer.from(descriptor.contentHash).toString('base64');

      // Create envelope for this part
      const messageBytes = multipart.toBinary();

      const metadata = { ...baseMetadata };
      metadata['multipart'] = `${partNumber}/${totalParts}`;
      metadata['message_id'] = messageId;

      const envelope = new Envelope();
      envelope.version = 1;
      envelope.contentHash = createHash('sha256').update(messageBytes).digest('hex');
      envelope.messageType = MessageType.MULTIPART_MESSAGE_PART;
      envelope.encryption = encryptionMode;
      envelope.message = messageBytes;
      
      Object.entries(metadata).forEach(([key, value]) => {
        envelope.metadata[key] = value;
      });

      envelopes.add(envelope);
    }

    return envelopes;
  }

  async retrieve(descriptor: ContentDescriptor): Promise<Uint8Array> {
    throw new Error('Multipart retrieval requires collecting all envelope parts by message_id');
  }

  canHandle(uri: string): boolean {
    return uri.startsWith('multipart:');
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
    if (!this.canHandle(descriptor.uri)) {
      throw new ValidationError(`Invalid HTTP URI: ${descriptor.uri}`);
    }

    // TODO: Implement HTTP retrieval
    // const response = await fetch(descriptor.uri);
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
      if (storage.canHandle(descriptor.uri)) {
        return storage.retrieve(descriptor);
      }
    }

    throw new ValidationError(`No storage backend can handle URI: ${descriptor.uri}`);
  }

  canHandle(uri: string): boolean {
    return this.storages.some(storage => storage.canHandle(uri));
  }
}