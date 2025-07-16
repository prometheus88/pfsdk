/**
 * Unit tests for envelope store classes.
 * 
 * Tests the manual EnvelopeStore implementations: RedisEnvelopeStore
 * and CompositeEnvelopeStore.
 */

import { createHash } from 'crypto';
import { Envelope, MessageType, EncryptionMode, ContextReference } from '../../../src/generated/postfiat/v3/messages_pb';
import { 
  EnvelopeStore, 
  CompositeEnvelopeStore, 
  EnvelopeNotFoundError, 
  StorageError 
} from '../../../src/envelope/envelope-store';
import { RedisEnvelopeStore } from '../../../src/envelope/stores/redis-store';

// Mock modules
jest.mock('ioredis');

describe('RedisEnvelopeStore', () => {
  let store: RedisEnvelopeStore;
  let testEnvelope: Envelope;

  beforeEach(() => {
    store = new RedisEnvelopeStore();
    
    testEnvelope = new Envelope();
    testEnvelope.setVersion(1);
    testEnvelope.setContentHash(new Uint8Array(Buffer.from('test_hash')));
    testEnvelope.setMessageType(MessageType.CORE_MESSAGE);
    testEnvelope.setEncryption(EncryptionMode.PROTECTED);
    testEnvelope.setMessage(new Uint8Array(Buffer.from('test_message')));
    testEnvelope.getMetadataMap().set('sender', 'test_sender');
    testEnvelope.getMetadataMap().set('timestamp', Date.now().toString());
    
    jest.clearAllMocks();
  });

  test('should store envelope in Redis', async () => {
    const mockClient = {
      pipeline: jest.fn().mockReturnValue({
        set: jest.fn(),
        sadd: jest.fn(),
        zadd: jest.fn(),
        exec: jest.fn().mockResolvedValue([])
      })
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const envelopeId = await store.store(testEnvelope);

    // Verify envelope_id is a valid hash
    expect(typeof envelopeId).toBe('string');
    expect(envelopeId).toHaveLength(64); // SHA256 hex length
    
    // Verify Redis operations
    expect(mockClient.pipeline).toHaveBeenCalled();
    
    // Verify metadata was added
    expect(testEnvelope.getMetadataMap().get('storage_backend')).toBe('redis');
    expect(testEnvelope.getMetadataMap().get('envelope_id')).toBe(envelopeId);
  });

  test('should retrieve envelope from Redis', async () => {
    const mockClient = {
      getBuffer: jest.fn()
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    // Mock envelope data
    const envelopeData = Buffer.from(testEnvelope.toBinary());
    mockClient.getBuffer.mockResolvedValue(envelopeData);
    
    const envelopeId = 'test_id';
    const retrievedEnvelope = await store.retrieve(envelopeId);

    // Verify Redis call
    expect(mockClient.getBuffer).toHaveBeenCalledWith('postfiat:envelope:test_id');
    
    // Verify envelope content
    expect(retrievedEnvelope.getVersion()).toBe(testEnvelope.getVersion());
    expect(Buffer.from(retrievedEnvelope.getContentHash())).toEqual(Buffer.from(testEnvelope.getContentHash()));
    expect(retrievedEnvelope.getMessageType()).toBe(testEnvelope.getMessageType());
  });

  test('should handle envelope not found', async () => {
    const mockClient = {
      getBuffer: jest.fn().mockResolvedValue(null)
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    await expect(store.retrieve('nonexistent')).rejects.toThrow(EnvelopeNotFoundError);
  });

  test('should find envelopes by content hash', async () => {
    const mockClient = {
      smembers: jest.fn().mockResolvedValue(['envelope_id_1', 'envelope_id_2']),
      getBuffer: jest.fn().mockResolvedValue(Buffer.from(testEnvelope.toBinary()))
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const contentHash = new Uint8Array(Buffer.from('test_hash'));
    const envelopes = await store.findByContentHash(contentHash);

    // Verify Redis operations
    const expectedKey = `postfiat:content_hash:${Buffer.from(contentHash).toString('hex')}`;
    expect(mockClient.smembers).toHaveBeenCalledWith(expectedKey);
    
    // Should retrieve each envelope
    expect(envelopes).toHaveLength(2);
    expect(envelopes.every(env => env instanceof Envelope)).toBe(true);
  });

  test('should find envelopes by context', async () => {
    const mockClient = {
      smembers: jest.fn().mockResolvedValue(['envelope_id_1']),
      getBuffer: jest.fn().mockResolvedValue(Buffer.from(testEnvelope.toBinary()))
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const contextHash = new Uint8Array(Buffer.from('context_hash'));
    const envelopes = await store.findByContext(contextHash);

    // Verify Redis operations
    const expectedKey = `postfiat:context:${Buffer.from(contextHash).toString('hex')}`;
    expect(mockClient.smembers).toHaveBeenCalledWith(expectedKey);
    
    expect(envelopes).toHaveLength(1);
  });

  test('should list envelopes by sender', async () => {
    const mockClient = {
      zrevrange: jest.fn().mockResolvedValue(['envelope_id_1', 'envelope_id_2']),
      getBuffer: jest.fn().mockResolvedValue(Buffer.from(testEnvelope.toBinary()))
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const sender = 'test_sender';
    const envelopes = await store.listBySender(sender, 10);

    // Verify Redis operations
    expect(mockClient.zrevrange).toHaveBeenCalledWith('postfiat:sender:test_sender', 0, 9);
    
    expect(envelopes).toHaveLength(2);
  });

  test('should check if envelope exists', async () => {
    const mockClient = {
      exists: jest.fn().mockResolvedValue(1)
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const exists = await store.exists('test_id');

    expect(exists).toBe(true);
    expect(mockClient.exists).toHaveBeenCalledWith('postfiat:envelope:test_id');
  });

  test('should delete envelope', async () => {
    const mockClient = {
      getBuffer: jest.fn().mockResolvedValue(Buffer.from(testEnvelope.toBinary())),
      pipeline: jest.fn().mockReturnValue({
        del: jest.fn(),
        srem: jest.fn(),
        zrem: jest.fn(),
        exec: jest.fn().mockResolvedValue([[null, 1], [null, 1]]) // Simulate successful deletion
      })
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const deleted = await store.delete('test_id');

    expect(deleted).toBe(true);
    expect(mockClient.pipeline).toHaveBeenCalled();
  });

  test('should handle delete of non-existent envelope', async () => {
    const mockClient = {
      getBuffer: jest.fn().mockResolvedValue(null)
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const deleted = await store.delete('nonexistent');

    expect(deleted).toBe(false);
  });

  test('should get envelope metadata', async () => {
    const mockClient = {
      get: jest.fn().mockResolvedValue(JSON.stringify({
        envelope_id: 'test_id',
        storage_backend: 'redis',
        stored_at: '1234567890'
      }))
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const metadata = await store.getEnvelopeMetadata('test_id');

    expect(metadata.envelope_id).toBe('test_id');
    expect(metadata.storage_backend).toBe('redis');
    expect(mockClient.get).toHaveBeenCalledWith('postfiat:metadata:test_id');
  });

  test('should get backend info', () => {
    const info = store.getBackendInfo();

    expect(info.type).toBe('redis');
    expect(info.url).toBe('redis://localhost:6379');
    expect(info.key_prefix).toBe('postfiat');
  });

  test('should handle import error', async () => {
    jest.doMock('ioredis', () => {
      throw new Error('Module not found');
    });

    await expect(store.store(testEnvelope)).rejects.toThrow('ioredis is required');
  });
});

describe('CompositeEnvelopeStore', () => {
  let redisStore: jest.Mocked<EnvelopeStore>;
  let mockStore: jest.Mocked<EnvelopeStore>;
  let compositeStore: CompositeEnvelopeStore;
  let testEnvelope: Envelope;

  beforeEach(() => {
    // Create mocked stores
    redisStore = {
      store: jest.fn(),
      retrieve: jest.fn(),
      findByContentHash: jest.fn(),
      findByContext: jest.fn(),
      listBySender: jest.fn(),
      delete: jest.fn(),
      exists: jest.fn(),
      getEnvelopeMetadata: jest.fn(),
      getBackendInfo: jest.fn()
    };

    mockStore = {
      store: jest.fn(),
      retrieve: jest.fn(),
      findByContentHash: jest.fn(),
      findByContext: jest.fn(),
      listBySender: jest.fn(),
      delete: jest.fn(),
      exists: jest.fn(),
      getEnvelopeMetadata: jest.fn(),
      getBackendInfo: jest.fn()
    };

    const stores = {
      redis: redisStore,
      mock: mockStore
    };

    compositeStore = new CompositeEnvelopeStore(stores, 'redis');

    testEnvelope = new Envelope();
    testEnvelope.setVersion(1);
    testEnvelope.setContentHash(new Uint8Array(Buffer.from('test_hash')));
  });

  test('should store using default store', async () => {
    redisStore.store.mockResolvedValue('envelope_id');

    const envelopeId = await compositeStore.store(testEnvelope);

    expect(redisStore.store).toHaveBeenCalledWith(testEnvelope);
    expect(envelopeId).toBe('envelope_id');
  });

  test('should retrieve from first available store', async () => {
    // First store raises not found, second succeeds
    redisStore.retrieve.mockRejectedValue(new EnvelopeNotFoundError('Not found'));
    mockStore.retrieve.mockResolvedValue(testEnvelope);

    const envelope = await compositeStore.retrieve('test_id');

    expect(redisStore.retrieve).toHaveBeenCalledWith('test_id');
    expect(mockStore.retrieve).toHaveBeenCalledWith('test_id');
    expect(envelope).toBe(testEnvelope);
  });

  test('should handle envelope not found in any store', async () => {
    redisStore.retrieve.mockRejectedValue(new EnvelopeNotFoundError('Not found'));
    mockStore.retrieve.mockRejectedValue(new EnvelopeNotFoundError('Not found'));

    await expect(compositeStore.retrieve('test_id')).rejects.toThrow(EnvelopeNotFoundError);
  });

  test('should find by content hash across all stores', async () => {
    const envelope1 = new Envelope();
    const envelope2 = new Envelope();
    
    redisStore.findByContentHash.mockResolvedValue([envelope1]);
    mockStore.findByContentHash.mockResolvedValue([envelope2]);

    const contentHash = new Uint8Array(Buffer.from('test_hash'));
    const envelopes = await compositeStore.findByContentHash(contentHash);

    expect(envelopes).toHaveLength(2);
    expect(envelopes).toContain(envelope1);
    expect(envelopes).toContain(envelope2);
  });

  test('should find by context across all stores', async () => {
    const envelope1 = new Envelope();
    
    redisStore.findByContext.mockResolvedValue([envelope1]);
    mockStore.findByContext.mockResolvedValue([]);

    const contextHash = new Uint8Array(Buffer.from('context_hash'));
    const envelopes = await compositeStore.findByContext(contextHash);

    expect(envelopes).toHaveLength(1);
    expect(envelopes).toContain(envelope1);
  });

  test('should list by sender with limit', async () => {
    const envelope1 = new Envelope();
    const envelope2 = new Envelope();
    
    redisStore.listBySender.mockResolvedValue([envelope1, envelope2]);
    mockStore.listBySender.mockResolvedValue([testEnvelope]);

    const envelopes = await compositeStore.listBySender('test_sender', 2);

    expect(envelopes).toHaveLength(2);
    expect(redisStore.listBySender).toHaveBeenCalledWith('test_sender', 2);
    expect(mockStore.listBySender).toHaveBeenCalledWith('test_sender', 0); // Remaining limit
  });

  test('should check exists across all stores', async () => {
    redisStore.exists.mockResolvedValue(false);
    mockStore.exists.mockResolvedValue(true);

    const exists = await compositeStore.exists('test_id');

    expect(exists).toBe(true);
    expect(redisStore.exists).toHaveBeenCalledWith('test_id');
    expect(mockStore.exists).toHaveBeenCalledWith('test_id');
  });

  test('should delete from all stores', async () => {
    redisStore.delete.mockResolvedValue(true);
    mockStore.delete.mockResolvedValue(false);

    const deleted = await compositeStore.delete('test_id');

    expect(deleted).toBe(true);
    expect(redisStore.delete).toHaveBeenCalledWith('test_id');
    expect(mockStore.delete).toHaveBeenCalledWith('test_id');
  });

  test('should get specific store by name', () => {
    const store = compositeStore.getStore('mock');
    expect(store).toBe(mockStore);
  });

  test('should get default store', () => {
    const store = compositeStore.getStore();
    expect(store).toBe(redisStore);
  });

  test('should handle nonexistent store', () => {
    expect(() => compositeStore.getStore('nonexistent')).toThrow('Store \'nonexistent\' not found');
  });

  test('should handle invalid default store', () => {
    const stores = { redis: redisStore };
    
    expect(() => new CompositeEnvelopeStore(stores, 'invalid')).toThrow('Default store \'invalid\' not found');
  });

  test('should get backend info', () => {
    redisStore.getBackendInfo.mockReturnValue({ type: 'redis' });
    mockStore.getBackendInfo.mockReturnValue({ type: 'mock' });

    const info = compositeStore.getBackendInfo();

    expect(info.type).toBe('composite');
    expect(info.defaultStore).toBe('redis');
    expect(info.stores.redis).toEqual({ type: 'redis' });
    expect(info.stores.mock).toEqual({ type: 'mock' });
  });

  test('should get envelope metadata from first available store', async () => {
    redisStore.getEnvelopeMetadata.mockRejectedValue(new EnvelopeNotFoundError('Not found'));
    mockStore.getEnvelopeMetadata.mockResolvedValue({ envelope_id: 'test_id' });

    const metadata = await compositeStore.getEnvelopeMetadata('test_id');

    expect(metadata.envelope_id).toBe('test_id');
    expect(redisStore.getEnvelopeMetadata).toHaveBeenCalledWith('test_id');
    expect(mockStore.getEnvelopeMetadata).toHaveBeenCalledWith('test_id');
  });

  test('should handle metadata not found in any store', async () => {
    redisStore.getEnvelopeMetadata.mockRejectedValue(new EnvelopeNotFoundError('Not found'));
    mockStore.getEnvelopeMetadata.mockRejectedValue(new EnvelopeNotFoundError('Not found'));

    await expect(compositeStore.getEnvelopeMetadata('test_id')).rejects.toThrow(EnvelopeNotFoundError);
  });
});