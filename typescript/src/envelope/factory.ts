/**
 * PostFiat Envelope Factory
 * 
 * Factory for creating envelopes with pluggable content storage strategies.
 */

import { 
  Envelope, 
  CoreMessage, 
  ContentDescriptor,
  PostFiatEnvelopePayload,
  MessageType,
  EncryptionMode 
} from '../generated/postfiat/v3/messages_pb';
import { PostFiatCrypto } from '../crypto/PostFiatCrypto';
import { ContentStorage, IPFSStorage, MultipartStorage, ValidationError } from './storage';
import { createHash } from 'crypto';

/**
 * Factory for creating PostFiat envelopes with pluggable storage
 */
export class EnvelopeFactory {
  private readonly maxEnvelopeSize: number;
  private readonly storage: ContentStorage;

  /**
   * Initialize the envelope factory
   * @param maxEnvelopeSize Maximum allowed envelope size in bytes (default: 1000)
   * @param storage Content storage backend (defaults to IPFS)
   */
  constructor(maxEnvelopeSize: number = 1000, storage?: ContentStorage) {
    this.maxEnvelopeSize = maxEnvelopeSize;
    this.storage = storage || new IPFSStorage();
  }

  /**
   * Create envelope(s) with automatic size handling
   * @param content The content to wrap in envelope
   * @param senderPrivateKey Sender's private key for encryption
   * @param recipientPublicKey Optional recipient's public key
   * @param encryptionMode Encryption mode for the envelope
   * @param metadata Additional metadata for the envelope
   * @param contentType MIME type of the content
   * @returns Single Envelope, tuple of [Envelope, ContentDescriptor], or Set of Envelopes
   */
  async createEnvelope(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode = EncryptionMode.PROTECTED,
    metadata: Record<string, string> = {},
    contentType: string = 'text/plain; charset=utf-8'
  ): Promise<Envelope | [Envelope, ContentDescriptor] | Set<Envelope>> {
    // Merge default metadata with provided metadata
    const defaultMetadata = { 'agent_id': 'postfiat_research_agent_001' };
    const finalMetadata = { ...defaultMetadata, ...metadata };

    // Try to embed content directly if small enough
    const envelope = await this.tryCreateEmbeddedEnvelope(
      content,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode,
      finalMetadata
    );

    if (envelope) {
      // Content fits in envelope
      return envelope;
    }

    // Content too large - use storage backend
    const contentBytes = new TextEncoder().encode(content);
    const descriptor = await this.storage.store(contentBytes, contentType);

    // Handle special case of multipart storage
    if (this.storage instanceof MultipartStorage) {
      // Create multiple envelopes for multipart storage
      return await this.storage.createPartEnvelopes(
        contentBytes,
        descriptor,
        encryptionMode,
        finalMetadata
      );
    }

    // Create minimal envelope that references external content
    const referenceEnvelope = await this.createReferenceEnvelope(
      descriptor,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode,
      finalMetadata
    );

    return [referenceEnvelope, descriptor];
  }

  /**
   * Create a complete PostFiatEnvelopePayload with automatic content handling
   * @param content The content to wrap
   * @param senderPrivateKey Sender's private key for encryption
   * @param recipientPublicKey Optional recipient's public key
   * @param encryptionMode Encryption mode for the envelope
   * @param metadata Additional metadata for the envelope
   * @param contentType MIME type of the content
   * @param postfiatMetadata Additional PostFiat-specific metadata
   * @returns PostFiatEnvelopePayload with envelope and optional ContentDescriptor
   */
  async createEnvelopePayload(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode = EncryptionMode.PROTECTED,
    metadata: Record<string, string> = {},
    contentType: string = 'text/plain; charset=utf-8',
    postfiatMetadata: Record<string, string> = {}
  ): Promise<PostFiatEnvelopePayload> {
    const result = await this.createEnvelope(
      content,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode,
      metadata,
      contentType
    );

    // Default PostFiat metadata
    const defaultPostfiatMetadata = {
      'extension_version': 'v1',
      'processing_mode': 'selective_disclosure'
    };
    const finalPostfiatMetadata = { ...defaultPostfiatMetadata, ...postfiatMetadata };

    const payload = new PostFiatEnvelopePayload();
    
    const metadataMap = payload.getPostfiatMetadataMap();
    Object.entries(finalPostfiatMetadata).forEach(([key, value]) => {
      metadataMap.set(key, value);
    });

    // Handle different return types
    if (result instanceof Envelope) {
      // Simple embedded content
      payload.setEnvelope(result);
    } else if (Array.isArray(result)) {
      // External storage with descriptor
      const [envelope, descriptor] = result;
      payload.setEnvelope(envelope);
      if (descriptor) {
        payload.setContent(descriptor);
      }
    } else if (result instanceof Set) {
      // Multipart envelopes - return payload for first part
      const envelopes = Array.from(result);
      if (envelopes.length === 0) {
        throw new ValidationError('No envelopes created');
      }

      // Sort by part number for consistent ordering
      const sortedEnvelopes = envelopes.sort((a, b) => {
        const aPartInfo = a.getMetadataMap().get('multipart') || '1/1';
        const bPartInfo = b.getMetadataMap().get('multipart') || '1/1';
        const aPart = parseInt(aPartInfo.split('/')[0]);
        const bPart = parseInt(bPartInfo.split('/')[0]);
        return aPart - bPart;
      });

      payload.setEnvelope(sortedEnvelopes[0]);
      metadataMap.set('total_parts', envelopes.length.toString());
    } else {
      throw new ValidationError(`Unexpected result type: ${typeof result}`);
    }

    return payload;
  }

  /**
   * Try to create envelope with embedded content
   */
  private async tryCreateEmbeddedEnvelope(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode,
    metadata: Record<string, string>
  ): Promise<Envelope | null> {
    // Create core message
    const coreMessage = new CoreMessage();
    coreMessage.setContent(content);
    coreMessage.setContextReferencesList([]);
    
    const coreMetadataMap = coreMessage.getMetadataMap();
    coreMetadataMap.set('timestamp', '2024-07-07T12:00:00Z');

    // Serialize core message
    const messageBytes = coreMessage.serializeBinary();

    // Create envelope using crypto module
    const envelope = await PostFiatCrypto.createEncryptedEnvelope(
      content,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode
    );

    // Override message type and add metadata
    envelope.setMessageType(MessageType.CORE_MESSAGE);
    envelope.setMessage(messageBytes);
    
    const envelopeMetadataMap = envelope.getMetadataMap();
    Object.entries(metadata).forEach(([key, value]) => {
      envelopeMetadataMap.set(key, value);
    });

    // Check if it fits
    const envelopeBytes = envelope.serializeBinary();
    if (envelopeBytes.length <= this.maxEnvelopeSize) {
      return envelope;
    }

    return null;
  }

  /**
   * Create minimal envelope that references external content
   */
  private async createReferenceEnvelope(
    contentDescriptor: ContentDescriptor,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode,
    metadata: Record<string, string>
  ): Promise<Envelope> {
    // Create a minimal core message that references the external content
    const coreMessage = new CoreMessage();
    coreMessage.setContent(`Content stored at: ${contentDescriptor.getUri()}`);
    coreMessage.setContextReferencesList([]);
    
    const coreMetadataMap = coreMessage.getMetadataMap();
    coreMetadataMap.set('timestamp', '2024-07-07T12:00:00Z');
    coreMetadataMap.set('content_uri', contentDescriptor.getUri());
    coreMetadataMap.set('content_type', contentDescriptor.getContentType());

    const messageBytes = coreMessage.serializeBinary();

    // Create envelope using crypto module
    const envelope = await PostFiatCrypto.createEncryptedEnvelope(
      `Content stored at: ${contentDescriptor.getUri()}`,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode
    );

    // Override message type and add metadata
    envelope.setMessageType(MessageType.CORE_MESSAGE);
    envelope.setMessage(messageBytes);
    
    const envelopeMetadataMap = envelope.getMetadataMap();
    Object.entries(metadata).forEach(([key, value]) => {
      envelopeMetadataMap.set(key, value);
    });
    envelopeMetadataMap.set('content_uri', contentDescriptor.getUri());

    return envelope;
  }

  /**
   * Reconstruct original content from chunked envelopes
   * @param envelopes Array of envelope chunks
   * @returns Reconstructed original content string
   */
  static async reconstructContentFromChunks(envelopes: Envelope[]): Promise<string> {
    if (envelopes.length === 0) {
      throw new ValidationError('No envelopes provided for reconstruction');
    }

    // Import MultiPartMessagePart here to avoid circular dependency
    const { MultiPartMessagePart } = await import('../generated/postfiat/v3/messages_pb');

    // Extract multipart message parts
    const parts: any[] = [];
    let messageId: string | null = null;
    let completeMessageHash: string | null = null;

    for (const envelope of envelopes) {
      if (envelope.getMessageType() !== MessageType.MULTIPART_MESSAGE_PART) {
        throw new ValidationError(
          `Expected MULTIPART_MESSAGE_PART, got ${envelope.getMessageType()}`
        );
      }

      // Deserialize the multipart message part
      const multipartPart = MultiPartMessagePart.deserializeBinary(envelope.getMessage_asU8());

      // Validate message ID consistency
      if (messageId === null) {
        messageId = multipartPart.getMessageId();
        completeMessageHash = multipartPart.getCompleteMessageHash();
      } else if (messageId !== multipartPart.getMessageId()) {
        throw new ValidationError(
          `Message ID mismatch: expected ${messageId}, got ${multipartPart.getMessageId()}`
        );
      } else if (completeMessageHash !== multipartPart.getCompleteMessageHash()) {
        throw new ValidationError('Complete message hash mismatch between chunks');
      }

      parts.push(multipartPart);
    }

    // Sort parts by part number
    parts.sort((a, b) => a.getPartNumber() - b.getPartNumber());

    // Validate part sequence
    const expectedTotal = parts[0]?.getTotalParts() || 0;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const expectedPartNumber = i + 1;
      if (part.getPartNumber() !== expectedPartNumber) {
        throw new ValidationError(
          `Missing or out-of-order part: expected ${expectedPartNumber}, got ${part.getPartNumber()}`
        );
      }
      if (part.getTotalParts() !== expectedTotal) {
        throw new ValidationError(
          `Total parts mismatch: expected ${expectedTotal}, got ${part.getTotalParts()}`
        );
      }
    }

    if (parts.length !== expectedTotal) {
      throw new ValidationError(
        `Incomplete parts: expected ${expectedTotal}, got ${parts.length}`
      );
    }

    // Reconstruct content
    const contentChunks: Uint8Array[] = parts.map(part => part.getContent_asU8());
    const totalLength = contentChunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const contentBytes = new Uint8Array(totalLength);

    let offset = 0;
    for (const chunk of contentChunks) {
      contentBytes.set(chunk, offset);
      offset += chunk.length;
    }

    const content = new TextDecoder().decode(contentBytes);

    // Validate reconstructed content hash
    const reconstructedHash = createHash('sha256').update(contentBytes).digest('hex');
    if (reconstructedHash !== completeMessageHash) {
      throw new ValidationError('Reconstructed content hash does not match expected hash');
    }

    return content;
  }
}