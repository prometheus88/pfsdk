import { createTransport } from '@connectrpc/connect-web';
import { createClient } from '@connectrpc/connect';
import { PostFiatError } from './errors';
import type { ClientOptions } from './config';

/**
 * Main PostFiat SDK client
 */
export class PostFiatClient {
  private transport: ReturnType<typeof createTransport>;
  private options: ClientOptions;

  constructor(options: ClientOptions) {
    this.options = options;
    
    this.transport = createTransport({
      baseUrl: options.endpoint,
      httpVersion: '2',
      ...(options.fetch && { fetch: options.fetch }),
    });
  }

  /**
   * Get the underlying transport for creating service clients
   */
  get _transport() {
    return this.transport;
  }

  /**
   * Create a client for a specific service
   * This method will be used to create clients for generated services
   */
  createServiceClient<T>(serviceDefinition: any): T {
    try {
      return createClient(serviceDefinition, this.transport) as T;
    } catch (error) {
      throw new PostFiatError(
        'Failed to create service client',
        'CLIENT_CREATION_ERROR',
        error
      );
    }
  }

  /**
   * Health check method
   */
  async health(): Promise<{ status: string; timestamp: number }> {
    try {
      // This would normally call a health check endpoint
      // For now, return a mock response
      return {
        status: 'healthy',
        timestamp: Date.now(),
      };
    } catch (error) {
      throw new PostFiatError(
        'Health check failed',
        'HEALTH_CHECK_ERROR',
        error
      );
    }
  }
}