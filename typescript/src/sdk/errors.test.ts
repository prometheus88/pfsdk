import { describe, it, expect } from 'vitest';
import { PostFiatError, isPostFiatError, createPostFiatError } from './errors';

describe('PostFiatError', () => {
  it('should create error with message and code', () => {
    const error = new PostFiatError('Test error', 'VALIDATION_ERROR');
    
    expect(error.message).toBe('Test error');
    expect(error.code).toBe('VALIDATION_ERROR');
    expect(error.name).toBe('PostFiatError');
  });

  it('should default to UNKNOWN_ERROR code', () => {
    const error = new PostFiatError('Test error');
    
    expect(error.code).toBe('UNKNOWN_ERROR');
  });

  it('should identify PostFiatError instances', () => {
    const error = new PostFiatError('Test error');
    const regularError = new Error('Regular error');
    
    expect(isPostFiatError(error)).toBe(true);
    expect(isPostFiatError(regularError)).toBe(false);
  });

  it('should create PostFiatError from unknown error', () => {
    const originalError = new Error('Original error');
    const postFiatError = createPostFiatError(originalError, 'NETWORK_ERROR');
    
    expect(postFiatError).toBeInstanceOf(PostFiatError);
    expect(postFiatError.message).toBe('Original error');
    expect(postFiatError.code).toBe('NETWORK_ERROR');
    expect(postFiatError.originalError).toBe(originalError);
  });
});