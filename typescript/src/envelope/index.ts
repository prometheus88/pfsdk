/**
 * PostFiat Envelope Module
 * 
 * Envelope creation, validation, and management utilities.
 */

export { EnvelopeFactory, EnvelopeValidationError } from './factory';

// Re-export relevant types from protobuf for convenience
export { MessageType, EncryptionMode } from '../generated/postfiat/v3/messages_pb';