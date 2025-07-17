/**
 * Abstract envelope storage interface with dependency injection.
 * 
 * This module provides the base interface for envelope persistence and retrieval
 * across different storage backends (Redis, Ethereum, XRPL).
 */

import { Envelope } from '../generated/postfiat/v3/messages_pb';

/**
 * Custom exceptions for envelope storage
 */
export class StorageError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'StorageError';
  }
}

export class EnvelopeNotFoundError extends StorageError {
  constructor(message: string) {
    super(message);
    this.name = 'EnvelopeNotFoundError';
  }
}

export class ValidationError extends StorageError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Abstract interface for envelope persistence and retrieval
 */
export abstract class EnvelopeStore {
  /**
   * Store an envelope and return its unique identifier
   * @param envelope The envelope to store (contains all metadata in envelope.metadata)
   * @returns Unique identifier for the stored envelope
   */
  abstract store(envelope: Envelope): Promise<string>;

  /**
   * Retrieve an envelope by its identifier
   * @param envelopeId Unique identifier for the envelope
   * @returns The retrieved envelope
   */
  abstract retrieve(envelopeId: string): Promise<Envelope>;

  /**
   * Find envelopes by their content hash
   * @param contentHash Content hash to search for
   * @returns List of envelopes with matching content hash
   */
  abstract findByContentHash(contentHash: Uint8Array): Promise<Envelope[]>;

  /**
   * Find envelopes that reference a specific context
   * @param contextHash Context hash to search for
   * @returns List of envelopes referencing the context
   */
  abstract findByContext(contextHash: Uint8Array): Promise<Envelope[]>;

  /**
   * List envelopes by sender
   * @param sender Sender identifier
   * @param limit Maximum number of envelopes to return
   * @returns List of envelopes from the sender
   */
  abstract listBySender(sender: string, limit?: number): Promise<Envelope[]>;

  /**
   * Delete an envelope
   * @param envelopeId Unique identifier for the envelope
   * @returns True if envelope was deleted, false if not found
   */
  abstract delete(envelopeId: string): Promise<boolean>;

  /**
   * Check if an envelope exists
   * @param envelopeId Unique identifier for the envelope
   * @returns True if envelope exists, false otherwise
   */
  abstract exists(envelopeId: string): Promise<boolean>;

  /**
   * Get storage-specific metadata for an envelope
   * @param envelopeId Unique identifier for the envelope
   * @returns Storage-specific metadata (transaction_id, block_number, etc.)
   */
  abstract getEnvelopeMetadata(envelopeId: string): Promise<Record<string, string>>;

  /**
   * Get information about the storage backend
   * @returns Dictionary containing backend information
   */
  abstract getBackendInfo(): Record<string, any>;
}

/**
 * Composite envelope store that delegates to multiple backends
 */
export class CompositeEnvelopeStore extends EnvelopeStore {
  private stores: Map<string, EnvelopeStore>;
  private defaultStore: string;

  constructor(stores: Record<string, EnvelopeStore>, defaultStore: string) {
    super();
    this.stores = new Map(Object.entries(stores));
    this.defaultStore = defaultStore;

    if (!this.stores.has(defaultStore)) {
      throw new Error(`Default store '${defaultStore}' not found in stores`);
    }
  }

  /**
   * Get a specific store instance
   * @param storeName Name of the store, or undefined for default
   * @returns Store instance
   */
  getStore(storeName?: string): EnvelopeStore {
    const name = storeName || this.defaultStore;
    
    const store = this.stores.get(name);
    if (!store) {
      throw new Error(`Store '${name}' not found`);
    }
    
    return store;
  }

  async store(envelope: Envelope): Promise<string> {
    return await this.getStore().store(envelope);
  }

  async retrieve(envelopeId: string): Promise<Envelope> {
    for (const store of this.stores.values()) {
      try {
        return await store.retrieve(envelopeId);
      } catch (error) {
        if (error instanceof EnvelopeNotFoundError) {
          continue;
        }
        throw error;
      }
    }
    
    throw new EnvelopeNotFoundError(`Envelope '${envelopeId}' not found in any store`);
  }

  async findByContentHash(contentHash: Uint8Array): Promise<Envelope[]> {
    const results: Envelope[] = [];
    for (const store of this.stores.values()) {
      const storeResults = await store.findByContentHash(contentHash);
      results.push(...storeResults);
    }
    return results;
  }

  async findByContext(contextHash: Uint8Array): Promise<Envelope[]> {
    const results: Envelope[] = [];
    for (const store of this.stores.values()) {
      const storeResults = await store.findByContext(contextHash);
      results.push(...storeResults);
    }
    return results;
  }

  async listBySender(sender: string, limit: number = 100): Promise<Envelope[]> {
    const results: Envelope[] = [];
    let remainingLimit = limit;

    for (const store of this.stores.values()) {
      if (remainingLimit <= 0) {
        break;
      }

      const storeResults = await store.listBySender(sender, remainingLimit);
      results.push(...storeResults);
      remainingLimit -= storeResults.length;
    }

    return results.slice(0, limit);
  }

  async delete(envelopeId: string): Promise<boolean> {
    let deleted = false;
    for (const store of this.stores.values()) {
      if (await store.delete(envelopeId)) {
        deleted = true;
      }
    }
    return deleted;
  }

  async exists(envelopeId: string): Promise<boolean> {
    for (const store of this.stores.values()) {
      if (await store.exists(envelopeId)) {
        return true;
      }
    }
    return false;
  }

  async getEnvelopeMetadata(envelopeId: string): Promise<Record<string, string>> {
    for (const store of this.stores.values()) {
      try {
        return await store.getEnvelopeMetadata(envelopeId);
      } catch (error) {
        if (error instanceof EnvelopeNotFoundError) {
          continue;
        }
        throw error;
      }
    }
    
    throw new EnvelopeNotFoundError(`Envelope '${envelopeId}' not found in any store`);
  }

  getBackendInfo(): Record<string, any> {
    const storeInfo: Record<string, any> = {};
    for (const [name, store] of this.stores.entries()) {
      storeInfo[name] = store.getBackendInfo();
    }

    return {
      type: 'composite',
      defaultStore: this.defaultStore,
      stores: storeInfo
    };
  }
}