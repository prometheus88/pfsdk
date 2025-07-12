/**
 * Jest setup file for PostFiat SDK tests
 * Configures global environment for integration tests
 */

// Mock TextEncoder/TextDecoder for Jest environment if not available
if (typeof global.TextEncoder === 'undefined') {
  global.TextEncoder = require('util').TextEncoder;
}

if (typeof global.TextDecoder === 'undefined') {
  global.TextDecoder = require('util').TextDecoder;
}

// Set up crypto for Jest environment using Node.js crypto
if (typeof global.crypto === 'undefined') {
  const { webcrypto } = require('crypto');
  Object.defineProperty(global, 'crypto', {
    value: webcrypto,
    writable: true
  });
}

// Mock localStorage for tests
if (typeof global.localStorage === 'undefined') {
  global.localStorage = {
    store: {},
    getItem: function(key) {
      return this.store[key] || null;
    },
    setItem: function(key, value) {
      this.store[key] = value.toString();
    },
    removeItem: function(key) {
      delete this.store[key];
    },
    clear: function() {
      this.store = {};
    }
  };
}

// Increase timeout for integration tests
jest.setTimeout(60000);