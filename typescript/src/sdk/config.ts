/**
 * Configuration for PostFiat SDK client
 */
export interface PostFiatConfig {
  /** gRPC endpoint URL */
  endpoint: string;
  /** API key for authentication */
  apiKey?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Options for creating a PostFiat client
 */
export interface ClientOptions extends PostFiatConfig {
  /** Custom headers to include in requests */
  headers?: Record<string, string>;
  /** Custom fetch implementation */
  fetch?: typeof fetch;
}

/**
 * Predefined environments for easy configuration
 */
export const environments = {
  local: {
    endpoint: 'http://localhost:8080',
    debug: true,
  },
  development: {
    endpoint: 'https://api-dev.postfiat.com',
    debug: true,
  },
  staging: {
    endpoint: 'https://api-staging.postfiat.com',
    debug: false,
  },
  production: {
    endpoint: 'https://api.postfiat.com',
    debug: false,
  },
} as const;

/**
 * Create a configuration object for the PostFiat client
 */
export function createConfig(
  env: keyof typeof environments,
  overrides: Partial<PostFiatConfig> = {}
): PostFiatConfig {
  return {
    ...environments[env],
    ...overrides,
  };
}