/**
 * PostFiat Envelope Module
 * 
 * Envelope creation, validation, and management utilities.
 */

export { EnvelopeFactory } from './factory';
export { 
  ContentStorage, 
  IPFSStorage, 
  MultipartStorage, 
  HTTPStorage, 
  CompositeStorage,
  ValidationError as EnvelopeValidationError
} from './storage';

// Don't re-export MessageType and EncryptionMode to avoid conflicts
// These are already exported from types/enums