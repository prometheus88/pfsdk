/**
 * Utility functions for the PostFiat SDK
 */

/**
 * Delay execution for a specified number of milliseconds
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Check if we're running in a browser environment
 */
export function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}

/**
 * Check if we're running in a Node.js environment
 */
export function isNode(): boolean {
  return typeof process !== 'undefined' && 
         process.versions && 
         typeof process.versions.node === 'string';
}

/**
 * Format a timestamp to ISO string
 */
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toISOString();
}

/**
 * Parse an ISO string to timestamp
 */
export function parseTimestamp(isoString: string): number {
  return new Date(isoString).getTime();
}

/**
 * Simple debounce implementation
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | undefined;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}