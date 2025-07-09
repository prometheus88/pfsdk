import { describe, it, expect, vi } from 'vitest';
import { delay, isBrowser, isNode, formatTimestamp, parseTimestamp, debounce } from './index';

describe('utils', () => {
  describe('delay', () => {
    it('should delay execution', async () => {
      const start = Date.now();
      await delay(100);
      const end = Date.now();
      
      expect(end - start).toBeGreaterThanOrEqual(90); // Allow for small timing variations
    });
  });

  describe('environment detection', () => {
    it('should detect browser environment', () => {
      // In jsdom environment, this should return true
      expect(isBrowser()).toBe(true);
    });

    it('should detect Node.js environment', () => {
      expect(isNode()).toBe(true);
    });
  });

  describe('timestamp utilities', () => {
    it('should format timestamp to ISO string', () => {
      const timestamp = 1640995200000; // 2022-01-01T00:00:00.000Z
      const formatted = formatTimestamp(timestamp);
      
      expect(formatted).toBe('2022-01-01T00:00:00.000Z');
    });

    it('should parse ISO string to timestamp', () => {
      const isoString = '2022-01-01T00:00:00.000Z';
      const timestamp = parseTimestamp(isoString);
      
      expect(timestamp).toBe(1640995200000);
    });
  });

  describe('debounce', () => {
    it('should debounce function calls', async () => {
      const fn = vi.fn();
      const debouncedFn = debounce(fn, 100);
      
      // Call multiple times quickly
      debouncedFn();
      debouncedFn();
      debouncedFn();
      
      // Should not have been called yet
      expect(fn).not.toHaveBeenCalled();
      
      // Wait for debounce
      await delay(150);
      
      // Should have been called once
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });
});