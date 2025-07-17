/**
 * Redis envelope storage implementation.
 * 
 * This module provides Redis-based envelope storage with indexing capabilities.
 * Uses the envelope's built-in fields and metadata map for all data.
 */

import { createHash } from 'crypto';
import { Envelope } from '../../generated/postfiat/v3/messages_pb';
import { EnvelopeStore, EnvelopeNotFoundError, StorageError } from '../envelope-store';

/**
 * Redis-based envelope storage with indexing
 */
export class RedisEnvelopeStore extends EnvelopeStore {
  private redisUrl: string;
  private keyPrefix: string;
  private _client: any;

  constructor(redisUrl: string = 'redis://localhost:6379', keyPrefix: string = 'postfiat') {
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

  private envelopeKey(envelopeId: string): string {
    return `${this.keyPrefix}:envelope:${envelopeId}`;
  }

  private metadataKey(envelopeId: string): string {
    return `${this.keyPrefix}:metadata:${envelopeId}`;
  }

  private contentHashKey(contentHash: Uint8Array): string {
    return `${this.keyPrefix}:content_hash:${Buffer.from(contentHash).toString('hex')}`;
  }

  private contextKey(contextHash: Uint8Array): string {
    return `${this.keyPrefix}:context:${Buffer.from(contextHash).toString('hex')}`;
  }

  private senderKey(sender: string): string {
    return `${this.keyPrefix}:sender:${sender}`;
  }

  private generateEnvelopeId(envelope: Envelope): string {
    const envelopeBytes = envelope.toBinary();
    return createHash('sha256').update(envelopeBytes).digest('hex');
  }

  async store(envelope: Envelope): Promise<string> {
    try {
      const client = await this.getClient();
      const envelopeId = this.generateEnvelopeId(envelope);

      // Add storage-specific metadata to envelope
      const metadataMap = envelope.getMetadataMap();
      metadataMap.set('storage_backend', 'redis');
      metadataMap.set('envelope_id', envelopeId);

      // Serialize envelope
      const envelopeData = Buffer.from(envelope.toBinary());

      // Prepare storage metadata (Redis-specific info)
      const storageMetadata = {
        envelope_id: envelopeId,
        storage_backend: 'redis',
        stored_at: Date.now().toString()
      };

      // Use Redis pipeline for atomic operations
      const pipeline = client.pipeline();

      // Store envelope and storage metadata
      pipeline.set(this.envelopeKey(envelopeId), envelopeData);
      pipeline.set(this.metadataKey(envelopeId), JSON.stringify(storageMetadata));

      // Update indexes
      pipeline.sadd(this.contentHashKey(envelope.getContentHash()), envelopeId);

      // Index context references
      for (const contextRef of envelope.getPublicReferencesList()) {
        pipeline.sadd(this.contextKey(contextRef.getContentHash()), envelopeId);
      }

      // Index sender if provided in envelope metadata
      const sender = metadataMap.get('sender');
      if (sender) {
        const timestamp = parseFloat(metadataMap.get('timestamp') || '0');
        pipeline.zadd(this.senderKey(sender), timestamp, envelopeId);
      }

      await pipeline.exec();

      return envelopeId;
    } catch (error: any) {
      throw new StorageError(`Failed to store envelope: ${error.message}`);
    }
  }

  async retrieve(envelopeId: string): Promise<Envelope> {
    try {
      const client = await this.getClient();
      const envelopeData = await client.getBuffer(this.envelopeKey(envelopeId));

      if (!envelopeData) {
        throw new EnvelopeNotFoundError(`Envelope '${envelopeId}' not found`);
      }

      return Envelope.fromBinary(new Uint8Array(envelopeData));
    } catch (error: any) {
      if (error instanceof EnvelopeNotFoundError) {
        throw error;
      }
      throw new StorageError(`Failed to retrieve envelope: ${error.message}`);
    }
  }

  async findByContentHash(contentHash: Uint8Array): Promise<Envelope[]> {
    try {
      const client = await this.getClient();
      const envelopeIds = await client.smembers(this.contentHashKey(contentHash));

      const envelopes: Envelope[] = [];
      for (const envelopeId of envelopeIds) {
        try {
          const envelope = await this.retrieve(envelopeId);
          envelopes.push(envelope);
        } catch (error) {
          if (error instanceof EnvelopeNotFoundError) {
            // Clean up stale index entry
            await client.srem(this.contentHashKey(contentHash), envelopeId);
          }
        }
      }

      return envelopes;
    } catch (error: any) {
      throw new StorageError(`Failed to find envelopes by content hash: ${error.message}`);
    }
  }

  async findByContext(contextHash: Uint8Array): Promise<Envelope[]> {
    try {
      const client = await this.getClient();
      const envelopeIds = await client.smembers(this.contextKey(contextHash));

      const envelopes: Envelope[] = [];
      for (const envelopeId of envelopeIds) {
        try {
          const envelope = await this.retrieve(envelopeId);
          envelopes.push(envelope);
        } catch (error) {
          if (error instanceof EnvelopeNotFoundError) {
            // Clean up stale index entry
            await client.srem(this.contextKey(contextHash), envelopeId);
          }
        }
      }

      return envelopes;
    } catch (error: any) {
      throw new StorageError(`Failed to find envelopes by context: ${error.message}`);
    }
  }

  async listBySender(sender: string, limit: number = 100): Promise<Envelope[]> {
    try {
      const client = await this.getClient();
      // Get envelope IDs sorted by timestamp (most recent first)
      const envelopeIds = await client.zrevrange(this.senderKey(sender), 0, limit - 1);

      const envelopes: Envelope[] = [];
      for (const envelopeId of envelopeIds) {
        try {
          const envelope = await this.retrieve(envelopeId);
          envelopes.push(envelope);
        } catch (error) {
          if (error instanceof EnvelopeNotFoundError) {
            // Clean up stale index entry
            await client.zrem(this.senderKey(sender), envelopeId);
          }
        }
      }

      return envelopes;
    } catch (error: any) {
      throw new StorageError(`Failed to list envelopes by sender: ${error.message}`);
    }
  }

  async delete(envelopeId: string): Promise<boolean> {
    try {
      const client = await this.getClient();
      
      // Get envelope first to clean up indexes
      const envelope = await this.retrieve(envelopeId);

      const pipeline = client.pipeline();

      // Delete envelope and storage metadata
      pipeline.del(this.envelopeKey(envelopeId));
      pipeline.del(this.metadataKey(envelopeId));

      // Clean up indexes
      pipeline.srem(this.contentHashKey(envelope.getContentHash()), envelopeId);

      // Clean up context reference indexes
      for (const contextRef of envelope.getPublicReferencesList()) {
        pipeline.srem(this.contextKey(contextRef.getContentHash()), envelopeId);
      }

      // Clean up sender index if present
      const sender = envelope.getMetadataMap().get('sender');
      if (sender) {
        pipeline.zrem(this.senderKey(sender), envelopeId);
      }

      const results = await pipeline.exec();

      // Check if envelope was actually deleted
      return results && results[0] && results[0][1] > 0;
    } catch (error: any) {
      if (error instanceof EnvelopeNotFoundError) {
        return false;
      }
      throw new StorageError(`Failed to delete envelope: ${error.message}`);
    }
  }

  async exists(envelopeId: string): Promise<boolean> {
    try {
      const client = await this.getClient();
      const exists = await client.exists(this.envelopeKey(envelopeId));
      return exists > 0;
    } catch (error: any) {
      throw new StorageError(`Failed to check envelope existence: ${error.message}`);
    }
  }

  async getEnvelopeMetadata(envelopeId: string): Promise<Record<string, string>> {
    try {
      const client = await this.getClient();
      const metadataData = await client.get(this.metadataKey(envelopeId));

      if (!metadataData) {
        throw new EnvelopeNotFoundError(`Envelope '${envelopeId}' not found`);
      }

      return JSON.parse(metadataData);
    } catch (error: any) {
      if (error instanceof EnvelopeNotFoundError) {
        throw error;
      }
      throw new StorageError(`Failed to get envelope metadata: ${error.message}`);
    }
  }

  getBackendInfo(): Record<string, any> {
    return {
      type: 'redis',
      url: this.redisUrl,
      key_prefix: this.keyPrefix
    };
  }
}