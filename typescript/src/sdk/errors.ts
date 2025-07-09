/**
 * PostFiat SDK error types
 */
export type PostFiatErrorCode = 
  | 'CLIENT_CREATION_ERROR'
  | 'HEALTH_CHECK_ERROR'
  | 'NETWORK_ERROR'
  | 'AUTHENTICATION_ERROR'
  | 'VALIDATION_ERROR'
  | 'UNKNOWN_ERROR';

/**
 * Custom error class for PostFiat SDK
 */
export class PostFiatError extends Error {
  public readonly code: PostFiatErrorCode;
  public readonly originalError?: unknown;

  constructor(
    message: string,
    code: PostFiatErrorCode = 'UNKNOWN_ERROR',
    originalError?: unknown
  ) {
    super(message);
    this.name = 'PostFiatError';
    this.code = code;
    this.originalError = originalError;

    // Maintain proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PostFiatError);
    }
  }
}

/**
 * Check if an error is a PostFiatError
 */
export function isPostFiatError(error: unknown): error is PostFiatError {
  return error instanceof PostFiatError;
}

/**
 * Create a PostFiatError from an unknown error
 */
export function createPostFiatError(
  error: unknown,
  code: PostFiatErrorCode = 'UNKNOWN_ERROR'
): PostFiatError {
  if (isPostFiatError(error)) {
    return error;
  }

  const message = error instanceof Error ? error.message : String(error);
  return new PostFiatError(message, code, error);
}