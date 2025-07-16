/**
 * Unit tests for content storage classes.
 * 
 * Tests the manual ContentStorage implementations: IPFSStorage, RedisStorage,
 * InlineStorage, MultipartStorage, and CompositeStorage.
 */

import { createHash } from 'crypto';
import { ContentDescriptor } from '../../../src/generated/postfiat/v3/messages_pb';
import { 
  IPFSStorage, 
  RedisStorage, 
  InlineStorage, 
  MultipartStorage, 
  CompositeStorage 
} from '../../../src/envelope/storage';
import { ValidationError } from '../../../src/envelope/envelope-store';

// Mock modules
jest.mock('ioredis');
jest.mock('ipfs-http-client');

describe('InlineStorage', () => {
  let storage: InlineStorage;
  const testContent = new Uint8Array(Buffer.from('Hello, World!'));
  const testContentType = 'text/plain';

  beforeEach(() => {
    storage = new InlineStorage();
  });

  test('should store content inline', async () => {
    const descriptor = await storage.store(testContent, testContentType);

    expect(descriptor.getUri()).toBe('inline://data');
    expect(descriptor.getContentType()).toBe(testContentType);
    expect(descriptor.getContentLength()).toBe(testContent.length);
    
    const expectedHash = createHash('sha256').update(testContent).digest();
    expect(Buffer.from(descriptor.getContentHash())).toEqual(expectedHash);
    
    expect(descriptor.getMetadataMap().get('storage_provider')).toBe('inline');
    expect(descriptor.getMetadataMap().get('content_data')).toBeDefined();
    
    // Verify content is base64 encoded
    const storedContent = Buffer.from(descriptor.getMetadataMap().get('content_data')!, 'base64');
    expect(storedContent).toEqual(Buffer.from(testContent));
  });

  test('should retrieve content inline', async () => {
    const descriptor = await storage.store(testContent, testContentType);
    const retrievedContent = await storage.retrieve(descriptor);

    expect(retrievedContent).toEqual(testContent);
  });

  test('should handle URI schemes correctly', () => {
    expect(storage.canHandle('inline://data')).toBe(true);
    expect(storage.canHandle('ipfs://QmTest')).toBe(false);
    expect(storage.canHandle('redis://test')).toBe(false);
  });

  test('should reject invalid URI', async () => {
    const descriptor = new ContentDescriptor();
    descriptor.setUri('ipfs://invalid');

    await expect(storage.retrieve(descriptor)).rejects.toThrow(ValidationError);
  });

  test('should reject descriptor without content data', async () => {
    const descriptor = new ContentDescriptor();
    descriptor.setUri('inline://data');

    await expect(storage.retrieve(descriptor)).rejects.toThrow('No inline content data found');
  });

  test('should reject descriptor with hash mismatch', async () => {
    const descriptor = new ContentDescriptor();
    descriptor.setUri('inline://data');
    descriptor.setContentHash(new Uint8Array(Buffer.from('wrong_hash')));
    descriptor.getMetadataMap().set('content_data', Buffer.from(testContent).toString('base64'));

    await expect(storage.retrieve(descriptor)).rejects.toThrow('Content hash mismatch');
  });
});

describe('RedisStorage', () => {
  let storage: RedisStorage;
  const testContent = new Uint8Array(Buffer.from('Hello, Redis!'));
  const testContentType = 'text/plain';

  beforeEach(() => {
    storage = new RedisStorage();
    jest.clearAllMocks();
  });

  test('should store content in Redis', async () => {
    const mockClient = {
      set: jest.fn().mockResolvedValue('OK')
    };
    
    // Mock Redis import
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const descriptor = await storage.store(testContent, testContentType);

    const contentHash = createHash('sha256').update(testContent).digest();
    expect(descriptor.getUri()).toBe(`redis://${contentHash.toString('hex')}`);
    expect(descriptor.getContentType()).toBe(testContentType);
    expect(descriptor.getContentLength()).toBe(testContent.length);
    expect(Buffer.from(descriptor.getContentHash())).toEqual(contentHash);
    expect(descriptor.getMetadataMap().get('storage_provider')).toBe('redis');
  });

  test('should retrieve content from Redis', async () => {
    const mockClient = {
      set: jest.fn().mockResolvedValue('OK'),
      get: jest.fn()
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    // Store first to get descriptor
    const descriptor = await storage.store(testContent, testContentType);
    
    // Mock Redis get response
    const contentData = {
      content: Buffer.from(testContent).toString('base64'),
      content_type: testContentType,
      content_length: testContent.length,
      content_hash: createHash('sha256').update(testContent).digest().toString('hex')
    };
    mockClient.get.mockResolvedValue(JSON.stringify(contentData));
    
    const retrievedContent = await storage.retrieve(descriptor);
    expect(retrievedContent).toEqual(testContent);
  });

  test('should handle URI schemes correctly', () => {
    expect(storage.canHandle('redis://test')).toBe(true);
    expect(storage.canHandle('ipfs://QmTest')).toBe(false);
    expect(storage.canHandle('inline://data')).toBe(false);
  });

  test('should reject content not found in Redis', async () => {
    const mockClient = {
      get: jest.fn().mockResolvedValue(null)
    };
    
    const mockRedis = {
      default: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ioredis', () => mockRedis);
    
    const descriptor = new ContentDescriptor();
    descriptor.setUri('redis://nonexistent');

    await expect(storage.retrieve(descriptor)).rejects.toThrow('Content not found in Redis');
  });

  test('should handle import error', async () => {
    jest.doMock('ioredis', () => {
      throw new Error('Module not found');
    });

    await expect(storage.store(testContent, testContentType)).rejects.toThrow('ioredis is required');
  });
});

describe('IPFSStorage', () => {
  let storage: IPFSStorage;
  const testContent = new Uint8Array(Buffer.from('Hello, IPFS!'));
  const testContentType = 'text/plain';

  beforeEach(() => {
    storage = new IPFSStorage();
    jest.clearAllMocks();
  });

  test('should store content in IPFS', async () => {
    const mockClient = {
      add: jest.fn().mockResolvedValue({ cid: { toString: () => 'QmTestHash' } })
    };
    
    const mockIPFS = {
      create: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ipfs-http-client', () => mockIPFS);
    
    const descriptor = await storage.store(testContent, testContentType);

    expect(descriptor.getUri()).toBe('ipfs://QmTestHash');
    expect(descriptor.getContentType()).toBe(testContentType);
    expect(descriptor.getMetadataMap().get('storage_provider')).toBe('ipfs');
    expect(descriptor.getMetadataMap().get('simulated')).toBeUndefined();
  });

  test('should fallback to simulated CID on error', async () => {
    jest.doMock('ipfs-http-client', () => {
      throw new Error('IPFS connection failed');
    });

    const descriptor = await storage.store(testContent, testContentType);

    expect(descriptor.getUri()).toMatch(/^ipfs:\/\/Qm/);
    expect(descriptor.getMetadataMap().get('simulated')).toBe('true');
  });

  test('should retrieve content from IPFS', async () => {
    const mockClient = {
      cat: jest.fn().mockImplementation(async function* () {
        yield testContent;
      })
    };
    
    const mockIPFS = {
      create: jest.fn().mockReturnValue(mockClient)
    };
    
    jest.doMock('ipfs-http-client', () => mockIPFS);
    
    const descriptor = new ContentDescriptor();
    descriptor.setUri('ipfs://QmTestHash');

    const retrievedContent = await storage.retrieve(descriptor);
    expect(retrievedContent).toEqual(testContent);
  });

  test('should handle URI schemes correctly', () => {
    expect(storage.canHandle('ipfs://QmTest')).toBe(true);
    expect(storage.canHandle('redis://test')).toBe(false);
    expect(storage.canHandle('inline://data')).toBe(false);
  });

  test('should handle import error', async () => {
    jest.doMock('ipfs-http-client', () => {
      throw new Error('Module not found');
    });

    await expect(storage.store(testContent, testContentType)).rejects.toThrow('ipfs-http-client is required');
  });
});

describe('MultipartStorage', () => {
  let storage: MultipartStorage;
  const testContent = new Uint8Array(Buffer.from('x'.repeat(250))); // Will need 3 parts
  const testContentType = 'application/octet-stream';

  beforeEach(() => {
    storage = new MultipartStorage(100); // 100 byte parts
  });

  test('should store content requiring multipart', async () => {
    const descriptor = await storage.store(testContent, testContentType);

    expect(descriptor.getUri()).toMatch(/^multipart:\/\//);
    expect(descriptor.getContentType()).toBe(testContentType);
    expect(descriptor.getContentLength()).toBe(testContent.length);
    
    const expectedHash = createHash('sha256').update(testContent).digest();
    expect(Buffer.from(descriptor.getContentHash())).toEqual(expectedHash);
    
    expect(descriptor.getMetadataMap().get('storage_provider')).toBe('multipart');
    expect(descriptor.getMetadataMap().get('total_parts')).toBe('3');
    expect(descriptor.getMetadataMap().get('part_size')).toBe('100');
  });

  test('should handle single part content', async () => {
    const smallContent = new Uint8Array(Buffer.from('small'));
    const storage = new MultipartStorage(100);

    const descriptor = await storage.store(smallContent, testContentType);
    expect(descriptor.getMetadataMap().get('total_parts')).toBe('1');
  });

  test('should handle URI schemes correctly', () => {
    expect(storage.canHandle('multipart://test-id')).toBe(true);
    expect(storage.canHandle('ipfs://QmTest')).toBe(false);
    expect(storage.canHandle('redis://test')).toBe(false);
  });

  test('should create part envelopes', async () => {
    const descriptor = await storage.store(testContent, testContentType);
    const envelopes = await storage.createPartEnvelopes(testContent, descriptor);

    expect(envelopes.length).toBe(3);
    // Additional envelope validation would require more complex mocking
  });
});

describe('CompositeStorage', () => {
  let inlineStorage: InlineStorage;
  let redisStorage: RedisStorage;
  let ipfsStorage: IPFSStorage;
  let compositeStorage: CompositeStorage;
  const testContent = new Uint8Array(Buffer.from('Hello, Composite!'));
  const testContentType = 'text/plain';

  beforeEach(() => {
    inlineStorage = new InlineStorage();
    redisStorage = new RedisStorage();
    ipfsStorage = new IPFSStorage();
    compositeStorage = new CompositeStorage([inlineStorage, redisStorage, ipfsStorage]);
  });

  test('should store using first storage backend', async () => {
    const descriptor = await compositeStorage.store(testContent, testContentType);

    // Should use inline storage (first in list)
    expect(descriptor.getUri()).toBe('inline://data');
    expect(descriptor.getMetadataMap().get('storage_provider')).toBe('inline');
  });

  test('should retrieve using appropriate storage backend', async () => {
    // Store content in inline storage
    const inlineDescriptor = await inlineStorage.store(testContent, testContentType);

    // Should retrieve using inline storage
    const retrievedContent = await compositeStorage.retrieve(inlineDescriptor);
    expect(retrievedContent).toEqual(testContent);
  });

  test('should reject unsupported URI', async () => {
    const descriptor = new ContentDescriptor();
    descriptor.setUri('unknown://test');

    await expect(compositeStorage.retrieve(descriptor)).rejects.toThrow(ValidationError);
  });

  test('should handle multiple URI schemes', () => {
    expect(compositeStorage.canHandle('inline://data')).toBe(true);
    expect(compositeStorage.canHandle('redis://test')).toBe(true);
    expect(compositeStorage.canHandle('ipfs://QmTest')).toBe(true);
    expect(compositeStorage.canHandle('unknown://test')).toBe(false);
  });
});