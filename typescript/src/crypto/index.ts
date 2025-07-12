/**
 * PostFiat SDK Crypto Module
 * 
 * Opinionated crypto implementation that eliminates the need for developers
 * to understand or implement cryptographic operations.
 * 
 * Features:
 * - Zero crypto knowledge required
 * - One-line encryption/decryption  
 * - Built-in security best practices
 * - Perfect type safety with PostFiat protocol
 */

export { PostFiatCrypto, PostFiatEnvelopeBuilder } from './PostFiatCrypto';
export type { EncryptionResult, DecryptionResult, KeyPair } from './PostFiatCrypto';

// Re-export relevant types from protobuf for convenience
export { EncryptionMode, KeyType } from '../generated/postfiat/v3/messages_pb';