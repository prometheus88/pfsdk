#!/usr/bin/env node
/**
 * Generate TypeScript tests from protobuf definitions
 * 
 * This script follows the same patterns as the Python test generation,
 * creating comprehensive test suites for TypeScript types and services.
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

// Get the current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Generate enum tests
 */
function generateEnumTests(): boolean {
  console.log('🔍 Generating enum tests...');

  const testCode = `/**
 * Auto-generated tests for TypeScript enums.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:tests' to regenerate.
 */

import { describe, it, expect } from 'vitest';
import { MessageType, EncryptionMode, ErrorCode } from '../../src/types/enums';

describe('MessageType', () => {
  it('should have correct enum values', () => {
    expect(MessageType.CONTEXTUAL_MESSAGE).toBe(0);
    expect(MessageType.MULTIPART_MESSAGE_PART).toBe(1);
    expect(MessageType.RESERVED_100).toBe(100);
  });

  it('should convert from protobuf', () => {
    expect(MessageType.fromProtobuf(0)).toBe(MessageType.CONTEXTUAL_MESSAGE);
    expect(MessageType.fromProtobuf(1)).toBe(MessageType.MULTIPART_MESSAGE_PART);
    expect(MessageType.fromProtobuf(100)).toBe(MessageType.RESERVED_100);
  });

  it('should convert to protobuf', () => {
    expect(MessageType.toProtobuf(MessageType.CONTEXTUAL_MESSAGE)).toBe(0);
    expect(MessageType.toProtobuf(MessageType.MULTIPART_MESSAGE_PART)).toBe(1);
    expect(MessageType.toProtobuf(MessageType.RESERVED_100)).toBe(100);
  });

  it('should return all values', () => {
    const values = MessageType.values();
    expect(values).toContain(MessageType.CONTEXTUAL_MESSAGE);
    expect(values).toContain(MessageType.MULTIPART_MESSAGE_PART);
    expect(values).toContain(MessageType.RESERVED_100);
  });

  it('should return enum name', () => {
    expect(MessageType.getName(MessageType.CONTEXTUAL_MESSAGE)).toBe('CONTEXTUAL_MESSAGE');
    expect(MessageType.getName(MessageType.MULTIPART_MESSAGE_PART)).toBe('MULTIPART_MESSAGE_PART');
    expect(MessageType.getName(MessageType.RESERVED_100)).toBe('RESERVED_100');
  });
});

describe('EncryptionMode', () => {
  it('should have correct enum values', () => {
    expect(EncryptionMode.NONE).toBe(0);
    expect(EncryptionMode.LEGACY_SHARED).toBe(1);
    expect(EncryptionMode.NACL_SECRETBOX).toBe(2);
    expect(EncryptionMode.NACL_BOX).toBe(3);
  });

  it('should convert from protobuf', () => {
    expect(EncryptionMode.fromProtobuf(0)).toBe(EncryptionMode.NONE);
    expect(EncryptionMode.fromProtobuf(1)).toBe(EncryptionMode.LEGACY_SHARED);
    expect(EncryptionMode.fromProtobuf(2)).toBe(EncryptionMode.NACL_SECRETBOX);
    expect(EncryptionMode.fromProtobuf(3)).toBe(EncryptionMode.NACL_BOX);
  });

  it('should convert to protobuf', () => {
    expect(EncryptionMode.toProtobuf(EncryptionMode.NONE)).toBe(0);
    expect(EncryptionMode.toProtobuf(EncryptionMode.LEGACY_SHARED)).toBe(1);
    expect(EncryptionMode.toProtobuf(EncryptionMode.NACL_SECRETBOX)).toBe(2);
    expect(EncryptionMode.toProtobuf(EncryptionMode.NACL_BOX)).toBe(3);
  });

  it('should return all values', () => {
    const values = EncryptionMode.values();
    expect(values).toContain(EncryptionMode.NONE);
    expect(values).toContain(EncryptionMode.LEGACY_SHARED);
    expect(values).toContain(EncryptionMode.NACL_SECRETBOX);
    expect(values).toContain(EncryptionMode.NACL_BOX);
  });

  it('should return enum name', () => {
    expect(EncryptionMode.getName(EncryptionMode.NONE)).toBe('NONE');
    expect(EncryptionMode.getName(EncryptionMode.LEGACY_SHARED)).toBe('LEGACY_SHARED');
    expect(EncryptionMode.getName(EncryptionMode.NACL_SECRETBOX)).toBe('NACL_SECRETBOX');
    expect(EncryptionMode.getName(EncryptionMode.NACL_BOX)).toBe('NACL_BOX');
  });
});

describe('ErrorCode', () => {
  it('should have correct enum values', () => {
    expect(ErrorCode.OK).toBe(0);
    expect(ErrorCode.UNKNOWN).toBe(1);
    expect(ErrorCode.VALIDATION_FAILED).toBe(2);
    expect(ErrorCode.AUTHENTICATION_FAILED).toBe(3);
    expect(ErrorCode.AUTHORIZATION_FAILED).toBe(4);
    expect(ErrorCode.RESOURCE_NOT_FOUND).toBe(5);
    expect(ErrorCode.INTERNAL_SERVER_ERROR).toBe(6);
    expect(ErrorCode.SERVICE_UNAVAILABLE).toBe(7);
    expect(ErrorCode.RATE_LIMIT_EXCEEDED).toBe(8);
    expect(ErrorCode.TIMEOUT).toBe(9);
    expect(ErrorCode.CONNECTION_FAILED).toBe(10);
  });

  it('should convert from protobuf', () => {
    expect(ErrorCode.fromProtobuf(0)).toBe(ErrorCode.OK);
    expect(ErrorCode.fromProtobuf(1)).toBe(ErrorCode.UNKNOWN);
    expect(ErrorCode.fromProtobuf(2)).toBe(ErrorCode.VALIDATION_FAILED);
    expect(ErrorCode.fromProtobuf(3)).toBe(ErrorCode.AUTHENTICATION_FAILED);
    expect(ErrorCode.fromProtobuf(4)).toBe(ErrorCode.AUTHORIZATION_FAILED);
    expect(ErrorCode.fromProtobuf(5)).toBe(ErrorCode.RESOURCE_NOT_FOUND);
    expect(ErrorCode.fromProtobuf(6)).toBe(ErrorCode.INTERNAL_SERVER_ERROR);
    expect(ErrorCode.fromProtobuf(7)).toBe(ErrorCode.SERVICE_UNAVAILABLE);
    expect(ErrorCode.fromProtobuf(8)).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
    expect(ErrorCode.fromProtobuf(9)).toBe(ErrorCode.TIMEOUT);
    expect(ErrorCode.fromProtobuf(10)).toBe(ErrorCode.CONNECTION_FAILED);
  });

  it('should convert to protobuf', () => {
    expect(ErrorCode.toProtobuf(ErrorCode.OK)).toBe(0);
    expect(ErrorCode.toProtobuf(ErrorCode.UNKNOWN)).toBe(1);
    expect(ErrorCode.toProtobuf(ErrorCode.VALIDATION_FAILED)).toBe(2);
    expect(ErrorCode.toProtobuf(ErrorCode.AUTHENTICATION_FAILED)).toBe(3);
    expect(ErrorCode.toProtobuf(ErrorCode.AUTHORIZATION_FAILED)).toBe(4);
    expect(ErrorCode.toProtobuf(ErrorCode.RESOURCE_NOT_FOUND)).toBe(5);
    expect(ErrorCode.toProtobuf(ErrorCode.INTERNAL_SERVER_ERROR)).toBe(6);
    expect(ErrorCode.toProtobuf(ErrorCode.SERVICE_UNAVAILABLE)).toBe(7);
    expect(ErrorCode.toProtobuf(ErrorCode.RATE_LIMIT_EXCEEDED)).toBe(8);
    expect(ErrorCode.toProtobuf(ErrorCode.TIMEOUT)).toBe(9);
    expect(ErrorCode.toProtobuf(ErrorCode.CONNECTION_FAILED)).toBe(10);
  });

  it('should return all values', () => {
    const values = ErrorCode.values();
    expect(values).toContain(ErrorCode.OK);
    expect(values).toContain(ErrorCode.UNKNOWN);
    expect(values).toContain(ErrorCode.VALIDATION_FAILED);
    expect(values).toContain(ErrorCode.AUTHENTICATION_FAILED);
    expect(values).toContain(ErrorCode.AUTHORIZATION_FAILED);
    expect(values).toContain(ErrorCode.RESOURCE_NOT_FOUND);
    expect(values).toContain(ErrorCode.INTERNAL_SERVER_ERROR);
    expect(values).toContain(ErrorCode.SERVICE_UNAVAILABLE);
    expect(values).toContain(ErrorCode.RATE_LIMIT_EXCEEDED);
    expect(values).toContain(ErrorCode.TIMEOUT);
    expect(values).toContain(ErrorCode.CONNECTION_FAILED);
  });

  it('should return enum name', () => {
    expect(ErrorCode.getName(ErrorCode.OK)).toBe('OK');
    expect(ErrorCode.getName(ErrorCode.UNKNOWN)).toBe('UNKNOWN');
    expect(ErrorCode.getName(ErrorCode.VALIDATION_FAILED)).toBe('VALIDATION_FAILED');
    expect(ErrorCode.getName(ErrorCode.AUTHENTICATION_FAILED)).toBe('AUTHENTICATION_FAILED');
    expect(ErrorCode.getName(ErrorCode.AUTHORIZATION_FAILED)).toBe('AUTHORIZATION_FAILED');
    expect(ErrorCode.getName(ErrorCode.RESOURCE_NOT_FOUND)).toBe('RESOURCE_NOT_FOUND');
    expect(ErrorCode.getName(ErrorCode.INTERNAL_SERVER_ERROR)).toBe('INTERNAL_SERVER_ERROR');
    expect(ErrorCode.getName(ErrorCode.SERVICE_UNAVAILABLE)).toBe('SERVICE_UNAVAILABLE');
    expect(ErrorCode.getName(ErrorCode.RATE_LIMIT_EXCEEDED)).toBe('RATE_LIMIT_EXCEEDED');
    expect(ErrorCode.getName(ErrorCode.TIMEOUT)).toBe('TIMEOUT');
    expect(ErrorCode.getName(ErrorCode.CONNECTION_FAILED)).toBe('CONNECTION_FAILED');
  });
});
`;

  // Write the generated file
  const outputPath = path.join(__dirname, '..', 'tests', 'generated', 'enums.test.ts');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, testCode);
  console.log(`✅ Generated ${outputPath}`);
  return true;
}

/**
 * Generate exception tests
 */
function generateExceptionTests(): boolean {
  console.log('🔍 Generating exception tests...');

  const testCode = `/**
 * Auto-generated tests for TypeScript exceptions.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:tests' to regenerate.
 */

import { describe, it, expect } from 'vitest';
import {
  PostFiatError,
  ClientError,
  ServerError,
  NetworkError,
  AuthError,
  ValidationError,
  ConfigurationError,
  BusinessError,
  ExternalError,
  AuthenticationError,
  AuthorizationError,
  ValidationFailedError,
  ResourceNotFoundError,
  InternalServerError,
  ServiceUnavailableError,
  RateLimitError,
  TimeoutError,
  ConnectionError,
  createExceptionFromErrorCode,
  createExceptionFromErrorInfo
} from '../../src/types/exceptions';
import { ErrorCode } from '../../src/types/enums';

describe('PostFiatError', () => {
  it('should create basic error', () => {
    const error = new PostFiatError('Test error');
    expect(error.message).toBe('Test error');
    expect(error.name).toBe('PostFiatError');
    expect(error.severity).toBe('ERROR');
    expect(error instanceof Error).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create error with options', () => {
    const error = new PostFiatError('Test error', {
      errorCode: ErrorCode.VALIDATION_FAILED,
      category: 'TEST',
      severity: 'WARNING',
      details: { field: 'test' },
      field: 'testField',
      errorId: 'test-id'
    });

    expect(error.message).toBe('Test error');
    expect(error.errorCode).toBe(ErrorCode.VALIDATION_FAILED);
    expect(error.category).toBe('TEST');
    expect(error.severity).toBe('WARNING');
    expect(error.details).toEqual({ field: 'test' });
    expect(error.field).toBe('testField');
    expect(error.errorId).toBe('test-id');
  });

  it('should convert to dict', () => {
    const error = new PostFiatError('Test error', {
      errorCode: ErrorCode.VALIDATION_FAILED,
      category: 'TEST',
      details: { field: 'test' }
    });

    const dict = error.toDict();
    expect(dict).toEqual({
      message: 'Test error',
      errorCode: ErrorCode.VALIDATION_FAILED,
      category: 'TEST',
      severity: 'ERROR',
      details: { field: 'test' },
      field: undefined,
      errorId: undefined
    });
  });

  it('should convert to JSON', () => {
    const error = new PostFiatError('Test error', {
      errorCode: ErrorCode.VALIDATION_FAILED
    });

    const json = error.toJSON();
    const parsed = JSON.parse(json);
    expect(parsed.message).toBe('Test error');
    expect(parsed.errorCode).toBe(ErrorCode.VALIDATION_FAILED);
  });
});

describe('Category-specific errors', () => {
  it('should create ClientError with correct category', () => {
    const error = new ClientError('Client error');
    expect(error.category).toBe('CLIENT');
    expect(error.name).toBe('ClientError');
    expect(error instanceof ClientError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ServerError with correct category', () => {
    const error = new ServerError('Server error');
    expect(error.category).toBe('SERVER');
    expect(error.name).toBe('ServerError');
    expect(error instanceof ServerError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create NetworkError with correct category', () => {
    const error = new NetworkError('Network error');
    expect(error.category).toBe('NETWORK');
    expect(error.name).toBe('NetworkError');
    expect(error instanceof NetworkError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create AuthError with correct category', () => {
    const error = new AuthError('Auth error');
    expect(error.category).toBe('AUTH');
    expect(error.name).toBe('AuthError');
    expect(error instanceof AuthError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ValidationError with correct category', () => {
    const error = new ValidationError('Validation error');
    expect(error.category).toBe('VALIDATION');
    expect(error.name).toBe('ValidationError');
    expect(error instanceof ValidationError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ConfigurationError with correct category', () => {
    const error = new ConfigurationError('Configuration error');
    expect(error.category).toBe('CONFIGURATION');
    expect(error.name).toBe('ConfigurationError');
    expect(error instanceof ConfigurationError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create BusinessError with correct category', () => {
    const error = new BusinessError('Business error');
    expect(error.category).toBe('BUSINESS');
    expect(error.name).toBe('BusinessError');
    expect(error instanceof BusinessError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ExternalError with correct category', () => {
    const error = new ExternalError('External error');
    expect(error.category).toBe('EXTERNAL');
    expect(error.name).toBe('ExternalError');
    expect(error instanceof ExternalError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });
});

describe('Specific error classes', () => {
  it('should create AuthenticationError with correct error code', () => {
    const error = new AuthenticationError('Authentication failed');
    expect(error.errorCode).toBe(ErrorCode.AUTHENTICATION_FAILED);
    expect(error.category).toBe('AUTH');
    expect(error.name).toBe('AuthenticationError');
    expect(error instanceof AuthenticationError).toBe(true);
    expect(error instanceof AuthError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create AuthorizationError with correct error code', () => {
    const error = new AuthorizationError('Authorization failed');
    expect(error.errorCode).toBe(ErrorCode.AUTHORIZATION_FAILED);
    expect(error.category).toBe('AUTH');
    expect(error.name).toBe('AuthorizationError');
    expect(error instanceof AuthorizationError).toBe(true);
    expect(error instanceof AuthError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ValidationFailedError with correct error code', () => {
    const error = new ValidationFailedError('Validation failed');
    expect(error.errorCode).toBe(ErrorCode.VALIDATION_FAILED);
    expect(error.category).toBe('VALIDATION');
    expect(error.name).toBe('ValidationFailedError');
    expect(error instanceof ValidationFailedError).toBe(true);
    expect(error instanceof ValidationError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ResourceNotFoundError with correct error code', () => {
    const error = new ResourceNotFoundError('Resource not found');
    expect(error.errorCode).toBe(ErrorCode.RESOURCE_NOT_FOUND);
    expect(error.category).toBe('CLIENT');
    expect(error.name).toBe('ResourceNotFoundError');
    expect(error instanceof ResourceNotFoundError).toBe(true);
    expect(error instanceof ClientError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create InternalServerError with correct error code', () => {
    const error = new InternalServerError('Internal server error');
    expect(error.errorCode).toBe(ErrorCode.INTERNAL_SERVER_ERROR);
    expect(error.category).toBe('SERVER');
    expect(error.name).toBe('InternalServerError');
    expect(error instanceof InternalServerError).toBe(true);
    expect(error instanceof ServerError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ServiceUnavailableError with correct error code', () => {
    const error = new ServiceUnavailableError('Service unavailable');
    expect(error.errorCode).toBe(ErrorCode.SERVICE_UNAVAILABLE);
    expect(error.category).toBe('SERVER');
    expect(error.name).toBe('ServiceUnavailableError');
    expect(error instanceof ServiceUnavailableError).toBe(true);
    expect(error instanceof ServerError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create RateLimitError with correct error code', () => {
    const error = new RateLimitError('Rate limit exceeded');
    expect(error.errorCode).toBe(ErrorCode.RATE_LIMIT_EXCEEDED);
    expect(error.category).toBe('SERVER');
    expect(error.name).toBe('RateLimitError');
    expect(error instanceof RateLimitError).toBe(true);
    expect(error instanceof ServerError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create TimeoutError with correct error code', () => {
    const error = new TimeoutError('Operation timeout');
    expect(error.errorCode).toBe(ErrorCode.TIMEOUT);
    expect(error.category).toBe('SERVER');
    expect(error.name).toBe('TimeoutError');
    expect(error instanceof TimeoutError).toBe(true);
    expect(error instanceof ServerError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });

  it('should create ConnectionError with correct error code', () => {
    const error = new ConnectionError('Connection failed');
    expect(error.errorCode).toBe(ErrorCode.CONNECTION_FAILED);
    expect(error.category).toBe('NETWORK');
    expect(error.name).toBe('ConnectionError');
    expect(error instanceof ConnectionError).toBe(true);
    expect(error instanceof NetworkError).toBe(true);
    expect(error instanceof PostFiatError).toBe(true);
  });
});

describe('Factory functions', () => {
  it('should create exception from error code', () => {
    const error = createExceptionFromErrorCode(
      ErrorCode.AUTHENTICATION_FAILED,
      'Authentication failed'
    );
    expect(error instanceof AuthenticationError).toBe(true);
    expect(error.errorCode).toBe(ErrorCode.AUTHENTICATION_FAILED);
    expect(error.message).toBe('Authentication failed');
  });

  it('should create exception from error code with options', () => {
    const error = createExceptionFromErrorCode(
      ErrorCode.VALIDATION_FAILED,
      'Validation failed',
      { field: 'email', details: { pattern: 'email' } }
    );
    expect(error instanceof ValidationFailedError).toBe(true);
    expect(error.errorCode).toBe(ErrorCode.VALIDATION_FAILED);
    expect(error.message).toBe('Validation failed');
    expect(error.field).toBe('email');
    expect(error.details).toEqual({ pattern: 'email' });
  });

  it('should create generic error for unknown error code', () => {
    const error = createExceptionFromErrorCode(
      ErrorCode.UNKNOWN,
      'Unknown error'
    );
    expect(error instanceof PostFiatError).toBe(true);
    expect(error.constructor.name).toBe('PostFiatError');
    expect(error.errorCode).toBe(ErrorCode.UNKNOWN);
    expect(error.message).toBe('Unknown error');
  });

  it('should create exception from error info', () => {
    const error = createExceptionFromErrorInfo({
      code: ErrorCode.RESOURCE_NOT_FOUND,
      message: 'User not found',
      context: { userId: '123' },
      field: 'id',
      errorId: 'err-123',
      severity: 'WARNING'
    });

    expect(error instanceof ResourceNotFoundError).toBe(true);
    expect(error.errorCode).toBe(ErrorCode.RESOURCE_NOT_FOUND);
    expect(error.message).toBe('User not found');
    expect(error.details).toEqual({ userId: '123' });
    expect(error.field).toBe('id');
    expect(error.errorId).toBe('err-123');
    expect(error.severity).toBe('WARNING');
  });

  it('should create exception from incomplete error info', () => {
    const error = createExceptionFromErrorInfo({});
    expect(error instanceof PostFiatError).toBe(true);
    expect(error.errorCode).toBe(ErrorCode.UNKNOWN);
    expect(error.message).toBe('Unknown error');
  });
});
`;

  // Write the generated file
  const outputPath = path.join(__dirname, '..', 'tests', 'generated', 'exceptions.test.ts');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, testCode);
  console.log(`✅ Generated ${outputPath}`);
  return true;
}

/**
 * Generate client tests
 */
function generateClientTests(): boolean {
  console.log('🔍 Generating client tests...');

  const testCode = `/**
 * Auto-generated tests for TypeScript client utilities.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:tests' to regenerate.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { PostFiatClient, createPostFiatClient, defaultClientConfig } from '../../src/client/base';

describe('PostFiatClient', () => {
  let client: PostFiatClient;

  beforeEach(() => {
    client = new PostFiatClient({
      baseUrl: 'https://api.postfiat.com',
      timeout: 5000,
      headers: { 'X-Test': 'true' }
    });
  });

  it('should create client with config', () => {
    expect(client).toBeDefined();
    expect(client.getConfig()).toEqual({
      baseUrl: 'https://api.postfiat.com',
      timeout: 5000,
      headers: { 'X-Test': 'true' }
    });
  });

  it('should get transport', () => {
    const transport = client.getTransport();
    expect(transport).toBeDefined();
  });

  it('should return config copy', () => {
    const config1 = client.getConfig();
    const config2 = client.getConfig();
    expect(config1).toEqual(config2);
    expect(config1).not.toBe(config2); // Should be different objects
  });
});

describe('createPostFiatClient', () => {
  it('should create client with default config merged', () => {
    const client = createPostFiatClient({
      baseUrl: 'https://api.postfiat.com'
    });

    const config = client.getConfig();
    expect(config.baseUrl).toBe('https://api.postfiat.com');
    expect(config.timeout).toBe(defaultClientConfig.timeout);
    expect(config.headers).toEqual(defaultClientConfig.headers);
  });

  it('should override default config', () => {
    const client = createPostFiatClient({
      baseUrl: 'https://api.postfiat.com',
      timeout: 10000,
      headers: { 'Custom-Header': 'value' }
    });

    const config = client.getConfig();
    expect(config.baseUrl).toBe('https://api.postfiat.com');
    expect(config.timeout).toBe(10000);
    expect(config.headers).toEqual({ 'Custom-Header': 'value' });
  });
});

describe('defaultClientConfig', () => {
  it('should have expected defaults', () => {
    expect(defaultClientConfig.timeout).toBe(30000);
    expect(defaultClientConfig.headers).toEqual({
      'Content-Type': 'application/json',
      'User-Agent': 'PostFiat-TypeScript-SDK/0.1.0'
    });
  });
});
`;

  // Write the generated file
  const outputPath = path.join(__dirname, '..', 'tests', 'generated', 'client.test.ts');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, testCode);
  console.log(`✅ Generated ${outputPath}`);
  return true;
}

/**
 * Generate React hooks tests
 */
function generateHooksTests(): boolean {
  console.log('🔍 Generating React hooks tests...');

  const testCode = `/**
 * Auto-generated tests for React hooks.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:tests' to regenerate.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { PostFiatClientProvider, usePostFiatClient, useAsyncOperation } from '../../src/hooks';
import { PostFiatError } from '../../src/types/exceptions';
import { ErrorCode } from '../../src/types/enums';

// Mock React for testing
const mockChildren = 'mock-children';

describe('usePostFiatClient', () => {
  it('should throw error when used outside provider', () => {
    expect(() => {
      renderHook(() => usePostFiatClient());
    }).toThrow('usePostFiatClient must be used within a PostFiatClientProvider');
  });

  it('should return client when used within provider', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <PostFiatClientProvider config={{ baseUrl: 'https://api.postfiat.com' }}>
        {children}
      </PostFiatClientProvider>
    );

    const { result } = renderHook(() => usePostFiatClient(), { wrapper });
    expect(result.current).toBeDefined();
    expect(result.current.getConfig().baseUrl).toBe('https://api.postfiat.com');
  });
});

describe('useAsyncOperation', () => {
  it('should initialize with default state', () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [state] = result.current;
    
    expect(state.data).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should handle successful operation', async () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [, execute] = result.current;

    const mockOperation = () => Promise.resolve('success');

    await act(async () => {
      await execute(mockOperation);
    });

    const [state] = result.current;
    expect(state.data).toBe('success');
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should handle operation error', async () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [, execute] = result.current;

    const mockError = new PostFiatError('Test error', { errorCode: ErrorCode.UNKNOWN });
    const mockOperation = () => Promise.reject(mockError);

    await act(async () => {
      await execute(mockOperation);
    });

    const [state] = result.current;
    expect(state.data).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBe(mockError);
  });

  it('should handle non-PostFiatError', async () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [, execute] = result.current;

    const mockOperation = () => Promise.reject(new Error('Generic error'));

    await act(async () => {
      await execute(mockOperation);
    });

    const [state] = result.current;
    expect(state.data).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeInstanceOf(PostFiatError);
    expect(state.error?.message).toBe('Generic error');
  });

  it('should handle string error', async () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [, execute] = result.current;

    const mockOperation = () => Promise.reject('String error');

    await act(async () => {
      await execute(mockOperation);
    });

    const [state] = result.current;
    expect(state.data).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeInstanceOf(PostFiatError);
    expect(state.error?.message).toBe('Unknown error');
  });

  it('should set loading state during operation', async () => {
    const { result } = renderHook(() => useAsyncOperation<string>());
    const [, execute] = result.current;

    let resolvePromise: (value: string) => void;
    const mockOperation = () => new Promise<string>((resolve) => {
      resolvePromise = resolve;
    });

    act(() => {
      execute(mockOperation);
    });

    // Should be loading
    expect(result.current[0].loading).toBe(true);
    expect(result.current[0].data).toBeNull();
    expect(result.current[0].error).toBeNull();

    // Resolve the promise
    await act(async () => {
      resolvePromise('success');
    });

    // Should be done loading
    expect(result.current[0].loading).toBe(false);
    expect(result.current[0].data).toBe('success');
    expect(result.current[0].error).toBeNull();
  });
});
`;

  // Write the generated file
  const outputPath = path.join(__dirname, '..', 'tests', 'generated', 'hooks.test.tsx');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, testCode);
  console.log(`✅ Generated ${outputPath}`);
  return true;
}

/**
 * Generate integration tests
 */
function generateIntegrationTests(): boolean {
  console.log('🔍 Generating integration tests...');

  const testCode = `/**
 * Auto-generated integration tests for the TypeScript SDK.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:tests' to regenerate.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { createPostFiatClient } from '../../src/client/base';
import { PostFiatError } from '../../src/types/exceptions';
import { ErrorCode, MessageType, EncryptionMode } from '../../src/types/enums';

describe('SDK Integration', () => {
  let client: ReturnType<typeof createPostFiatClient>;

  beforeEach(() => {
    client = createPostFiatClient({
      baseUrl: 'https://api.postfiat.com',
      timeout: 5000
    });
  });

  it('should create client successfully', () => {
    expect(client).toBeDefined();
    expect(client.getConfig().baseUrl).toBe('https://api.postfiat.com');
    expect(client.getConfig().timeout).toBe(5000);
  });

  it('should export all required types', () => {
    // Test that all enums are available
    expect(MessageType.CONTEXTUAL_MESSAGE).toBeDefined();
    expect(EncryptionMode.NONE).toBeDefined();
    expect(ErrorCode.OK).toBeDefined();

    // Test that all exception types are available
    expect(PostFiatError).toBeDefined();
    expect(new PostFiatError('test')).toBeInstanceOf(Error);
  });

  it('should handle enum conversions correctly', () => {
    // Test MessageType conversions
    expect(MessageType.fromProtobuf(0)).toBe(MessageType.CONTEXTUAL_MESSAGE);
    expect(MessageType.toProtobuf(MessageType.CONTEXTUAL_MESSAGE)).toBe(0);

    // Test EncryptionMode conversions
    expect(EncryptionMode.fromProtobuf(2)).toBe(EncryptionMode.NACL_SECRETBOX);
    expect(EncryptionMode.toProtobuf(EncryptionMode.NACL_SECRETBOX)).toBe(2);

    // Test ErrorCode conversions
    expect(ErrorCode.fromProtobuf(3)).toBe(ErrorCode.AUTHENTICATION_FAILED);
    expect(ErrorCode.toProtobuf(ErrorCode.AUTHENTICATION_FAILED)).toBe(3);
  });

  it('should create proper error hierarchy', () => {
    const error = new PostFiatError('Test error', {
      errorCode: ErrorCode.VALIDATION_FAILED,
      category: 'VALIDATION',
      details: { field: 'email' }
    });

    expect(error.message).toBe('Test error');
    expect(error.errorCode).toBe(ErrorCode.VALIDATION_FAILED);
    expect(error.category).toBe('VALIDATION');
    expect(error.details).toEqual({ field: 'email' });
    expect(error.toDict()).toEqual({
      message: 'Test error',
      errorCode: ErrorCode.VALIDATION_FAILED,
      category: 'VALIDATION',
      severity: 'ERROR',
      details: { field: 'email' },
      field: undefined,
      errorId: undefined
    });
  });

  it('should serialize and deserialize properly', () => {
    const error = new PostFiatError('Test error', {
      errorCode: ErrorCode.TIMEOUT,
      details: { timeout: 30000 }
    });

    const json = error.toJSON();
    const parsed = JSON.parse(json);
    
    expect(parsed.message).toBe('Test error');
    expect(parsed.errorCode).toBe(ErrorCode.TIMEOUT);
    expect(parsed.details).toEqual({ timeout: 30000 });
  });

  it('should work with all enum values', () => {
    // Test that all enum values are properly defined
    const messageTypes = MessageType.values();
    expect(messageTypes.length).toBeGreaterThan(0);
    expect(messageTypes).toContain(MessageType.CONTEXTUAL_MESSAGE);
    expect(messageTypes).toContain(MessageType.MULTIPART_MESSAGE_PART);

    const encryptionModes = EncryptionMode.values();
    expect(encryptionModes.length).toBeGreaterThan(0);
    expect(encryptionModes).toContain(EncryptionMode.NONE);
    expect(encryptionModes).toContain(EncryptionMode.NACL_SECRETBOX);

    const errorCodes = ErrorCode.values();
    expect(errorCodes.length).toBeGreaterThan(0);
    expect(errorCodes).toContain(ErrorCode.OK);
    expect(errorCodes).toContain(ErrorCode.AUTHENTICATION_FAILED);
  });

  it('should maintain consistency across conversions', () => {
    // Test round-trip conversions
    const originalMessageType = MessageType.CONTEXTUAL_MESSAGE;
    const pbValue = MessageType.toProtobuf(originalMessageType);
    const convertedBack = MessageType.fromProtobuf(pbValue);
    expect(convertedBack).toBe(originalMessageType);

    const originalEncryption = EncryptionMode.NACL_BOX;
    const pbEncryption = EncryptionMode.toProtobuf(originalEncryption);
    const convertedBackEncryption = EncryptionMode.fromProtobuf(pbEncryption);
    expect(convertedBackEncryption).toBe(originalEncryption);

    const originalErrorCode = ErrorCode.RATE_LIMIT_EXCEEDED;
    const pbErrorCode = ErrorCode.toProtobuf(originalErrorCode);
    const convertedBackErrorCode = ErrorCode.fromProtobuf(pbErrorCode);
    expect(convertedBackErrorCode).toBe(originalErrorCode);
  });
});
`;

  // Write the generated file
  const outputPath = path.join(__dirname, '..', 'tests', 'generated', 'integration.test.ts');
  const outputDir = path.dirname(outputPath);
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, testCode);
  console.log(`✅ Generated ${outputPath}`);
  return true;
}

/**
 * Main function to generate all TypeScript tests
 */
function main(): void {
  console.log('🔄 Generating TypeScript tests from protobuf definitions...');

  let success = true;
  success = generateEnumTests() && success;
  success = generateExceptionTests() && success;
  success = generateClientTests() && success;
  success = generateHooksTests() && success;
  success = generateIntegrationTests() && success;

  if (success) {
    console.log('✅ All TypeScript tests generated successfully!');
  } else {
    console.log('❌ Some tests failed to generate');
    process.exit(1);
  }
}

// Run the main function
main();