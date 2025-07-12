/**
 * Tests for PostFiat SDK Opinionated Crypto Implementation
 */

import { PostFiatCrypto, PostFiatEnvelopeBuilder, EncryptionResult } from '../../../src/crypto/PostFiatCrypto';
import { EncryptionMode, KeyType } from '../../../src/generated/postfiat/v3/messages_pb';

// Mock crypto for Jest environment
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

const { webcrypto } = require('crypto');
Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto
});

describe('PostFiatCrypto', () => {
  let aliceKeys: { publicKey: string; privateKey: string };
  let bobKeys: { publicKey: string; privateKey: string };

  beforeEach(async () => {
    // Generate test key pairs
    aliceKeys = await PostFiatCrypto.generateKeyPair();
    bobKeys = await PostFiatCrypto.generateKeyPair();
  });

  describe('Key Generation', () => {
    it('should generate valid key pairs', async () => {
      const keyPair = await PostFiatCrypto.generateKeyPair();
      
      expect(keyPair.publicKey).toBeDefined();
      expect(keyPair.privateKey).toBeDefined();
      expect(typeof keyPair.publicKey).toBe('string');
      expect(typeof keyPair.privateKey).toBe('string');
      expect(keyPair.publicKey.length).toBeGreaterThan(0);
      expect(keyPair.privateKey.length).toBeGreaterThan(0);
    });

    it('should generate unique key pairs', async () => {
      const keyPair1 = await PostFiatCrypto.generateKeyPair();
      const keyPair2 = await PostFiatCrypto.generateKeyPair();
      
      expect(keyPair1.publicKey).not.toBe(keyPair2.publicKey);
      expect(keyPair1.privateKey).not.toBe(keyPair2.privateKey);
    });
  });

  describe('Encryption - NONE mode', () => {
    it('should handle unencrypted content', async () => {
      const content = 'Hello, PostFiat!';
      const result = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.NONE
      );

      expect(result.mode).toBe(EncryptionMode.NONE);
      expect(result.data).toEqual(new TextEncoder().encode(content));
      expect(result.contentHash).toBeDefined();
      expect(result.metadata['X-PostFiat-Encryption']).toBe('none');
      expect(result.accessGrants).toHaveLength(0);
    });
  });

  describe('Encryption - PROTECTED mode', () => {
    it('should encrypt with secretbox', async () => {
      const content = 'Secret message';
      const result = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.PROTECTED
      );

      expect(result.mode).toBe(EncryptionMode.PROTECTED);
      expect(result.data).toBeDefined();
      expect(result.data.length).toBeGreaterThan(content.length); // Should include nonce
      expect(result.contentHash).toBeDefined();
      expect(result.metadata['X-PostFiat-Encryption']).toBe('secretbox');
      expect(result.metadata['X-PostFiat-Nonce']).toBeDefined();
      expect(result.accessGrants).toHaveLength(1);
      expect(result.accessGrants[0].keyType).toBe(KeyType.CONTENT_KEY);
    });
  });

  describe('Encryption - PUBLIC_KEY mode', () => {
    it('should encrypt with NaCl box', async () => {
      const content = 'Private message to Bob';
      const result = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.PUBLIC_KEY
      );

      expect(result.mode).toBe(EncryptionMode.PUBLIC_KEY);
      expect(result.data).toBeDefined();
      expect(result.data.length).toBeGreaterThan(content.length); // Should include nonce
      expect(result.contentHash).toBeDefined();
      expect(result.metadata['X-PostFiat-Encryption']).toBe('nacl-box');
      expect(result.metadata['X-PostFiat-NaCl-Nonce']).toBeDefined();
      expect(result.metadata['X-PostFiat-Recipient-PublicKey']).toBe(bobKeys.publicKey);
      expect(result.accessGrants).toHaveLength(1);
      expect(result.accessGrants[0].keyType).toBe(KeyType.CONTENT_KEY);
    });
  });

  describe('Decryption', () => {
    it('should decrypt unencrypted content', async () => {
      // First encrypt
      const content = 'Hello, World!';
      const encryptedResult = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.NONE
      );

      // Create mock envelope
      const envelope = {
        encryption: encryptedResult.mode,
        message: encryptedResult.data,
        metadata: encryptedResult.metadata,
        accessGrants: encryptedResult.accessGrants
      } as any;

      // Decrypt
      const decryptedResult = await PostFiatCrypto.decrypt(envelope, bobKeys.privateKey);
      expect(decryptedResult.content).toBe(content);
      expect(decryptedResult.metadata).toEqual(encryptedResult.metadata);
    });

    it('should decrypt secretbox encrypted content', async () => {
      // First encrypt
      const content = 'Secret message!';
      const encryptedResult = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.PROTECTED
      );

      // Create mock envelope
      const envelope = {
        encryption: encryptedResult.mode,
        message: encryptedResult.data,
        metadata: encryptedResult.metadata,
        accessGrants: encryptedResult.accessGrants
      } as any;

      // Decrypt
      const decryptedResult = await PostFiatCrypto.decrypt(envelope, bobKeys.privateKey);
      expect(decryptedResult.content).toBe(content);
    });

    it('should decrypt NaCl box encrypted content', async () => {
      // First encrypt
      const content = 'Private message!';
      const encryptedResult = await PostFiatCrypto.encryptForRecipient(
        content,
        bobKeys.publicKey,
        aliceKeys.privateKey,
        EncryptionMode.PUBLIC_KEY
      );

      // Create mock envelope
      const envelope = {
        encryption: encryptedResult.mode,
        message: encryptedResult.data,
        metadata: encryptedResult.metadata,
        accessGrants: encryptedResult.accessGrants
      } as any;

      // Decrypt
      const decryptedResult = await PostFiatCrypto.decrypt(envelope, bobKeys.privateKey);
      expect(decryptedResult.content).toBe(content);
    });
  });

  describe('Access Grants', () => {
    it('should create content access grants', () => {
      const keyMaterial = new Uint8Array([1, 2, 3, 4]);
      const grant = PostFiatCrypto.createAccessGrant(
        KeyType.CONTENT_KEY,
        'test-content',
        keyMaterial,
        bobKeys.publicKey
      );

      expect(grant.keyType).toBe(KeyType.CONTENT_KEY);
      expect(grant.targetId).toBe('test-content');
      expect(grant.encryptedKeyMaterial).toEqual(keyMaterial);
    });

    it('should create group access grants', () => {
      const keyMaterial = new Uint8Array([5, 6, 7, 8]);
      const grant = PostFiatCrypto.createAccessGrant(
        KeyType.GROUP_KEY,
        'test-group',
        keyMaterial,
        bobKeys.publicKey
      );

      expect(grant.keyType).toBe(KeyType.GROUP_KEY);
      expect(grant.targetId).toBe('test-group');
      expect(grant.encryptedKeyMaterial).toEqual(keyMaterial);
    });
  });

  describe('Error Handling', () => {
    it('should throw error for unsupported encryption mode', async () => {
      await expect(
        PostFiatCrypto.encryptForRecipient(
          'test',
          bobKeys.publicKey,
          aliceKeys.privateKey,
          999 as EncryptionMode // Invalid mode
        )
      ).rejects.toThrow('Unsupported encryption mode');
    });

    it('should throw error for unsupported decryption mode', async () => {
      const envelope = {
        encryption: 999 as EncryptionMode, // Invalid mode
        message: new Uint8Array(),
        metadata: {}
      } as any;

      await expect(
        PostFiatCrypto.decrypt(envelope, bobKeys.privateKey)
      ).rejects.toThrow('Unsupported encryption mode');
    });
  });
});

describe('PostFiatEnvelopeBuilder', () => {
  let aliceKeys: { publicKey: string; privateKey: string };
  let bobKeys: { publicKey: string; privateKey: string };

  beforeEach(async () => {
    aliceKeys = await PostFiatCrypto.generateKeyPair();
    bobKeys = await PostFiatCrypto.generateKeyPair();
  });

  describe('Envelope Creation', () => {
    it('should create encrypted envelope with one line of code', async () => {
      const content = 'Hello from PostFiat SDK!';
      const envelope = await PostFiatEnvelopeBuilder.createEncryptedEnvelope(
        content,
        aliceKeys.privateKey,
        bobKeys.publicKey,
        EncryptionMode.PUBLIC_KEY
      );

      expect(envelope.version).toBe(1);
      expect(envelope.encryption).toBe(EncryptionMode.PUBLIC_KEY);
      expect(envelope.message).toBeDefined();
      expect(envelope.contentHash).toBeDefined();
      expect(envelope.accessGrants).toHaveLength(1);
      expect(envelope.metadata).toBeDefined();
      expect(envelope.metadata?.['X-PostFiat-Encryption']).toBe('nacl-box');
    });

    it('should create unencrypted envelope', async () => {
      const content = 'Public message';
      const envelope = await PostFiatEnvelopeBuilder.createEncryptedEnvelope(
        content,
        aliceKeys.privateKey,
        undefined,
        EncryptionMode.NONE
      );

      expect(envelope.encryption).toBe(EncryptionMode.NONE);
      expect(envelope.accessGrants).toHaveLength(0);
      expect(envelope.metadata?.['X-PostFiat-Encryption']).toBe('none');
    });

    it('should demonstrate developer experience improvement', async () => {
      // Before: 50+ lines of crypto code
      // After: One line with PostFiat SDK
      const envelope = await PostFiatEnvelopeBuilder.createEncryptedEnvelope(
        'This is so much easier!',
        aliceKeys.privateKey,
        bobKeys.publicKey
      );

      // Verify the envelope is properly created
      expect(envelope).toBeDefined();
      expect(envelope.encryption).toBe(EncryptionMode.PUBLIC_KEY);
      expect(envelope.message).toBeDefined();
      expect(envelope.contentHash).toBeDefined();
      
      // Should be able to decrypt it back
      const decrypted = await PostFiatCrypto.decrypt(envelope, bobKeys.privateKey);
      expect(decrypted.content).toBe('This is so much easier!');
    });
  });
});