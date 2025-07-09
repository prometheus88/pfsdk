import { describe, it, expect, vi } from 'vitest';
import { PostFiatClient } from './client';
import { environments } from './config';

// Mock the connect-web transport
vi.mock('@connectrpc/connect-web', () => ({
  createTransport: vi.fn(() => ({
    stream: vi.fn(),
    unary: vi.fn(),
  })),
}));

describe('PostFiatClient', () => {
  it('should create a client with configuration', () => {
    const client = new PostFiatClient({
      ...environments.local,
      apiKey: 'test-key',
    });

    expect(client).toBeInstanceOf(PostFiatClient);
    expect(client._transport).toBeDefined();
  });

  it('should perform health check', async () => {
    const client = new PostFiatClient(environments.local);
    
    const result = await client.health();
    
    expect(result).toEqual({
      status: 'healthy',
      timestamp: expect.any(Number),
    });
  });
});