/**
 * Common types used throughout the SDK
 */

/**
 * Base response type for all API calls
 */
export interface BaseResponse {
  success: boolean;
  message?: string;
  timestamp: number;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number;
  limit?: number;
  cursor?: string;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> extends BaseResponse {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
    nextCursor?: string;
  };
}

/**
 * Error response type
 */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  timestamp: number;
}