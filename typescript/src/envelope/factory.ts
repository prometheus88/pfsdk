/**
 * PostFiat Envelope Factory
 * 
 * Factory for creating envelopes with automatic size validation and chunking.
 * Integrates with the PostFiat crypto implementation for secure envelope creation.
 */

import { 
  Envelope, 
  CoreMessage, 
  MultiPartMessagePart,
  MessageType,
  EncryptionMode 
} from '../generated/postfiat/v3/messages_pb';
import { PostFiatCrypto } from '../crypto/PostFiatCrypto';

/**
 * Validation error for envelope operations
 */
export class EnvelopeValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'EnvelopeValidationError';
  }
}

/**
 * Factory for creating PostFiat envelopes with size validation and automatic chunking
 */
export class EnvelopeFactory {
  private readonly maxEnvelopeSize: number;

  /**
   * Initialize the envelope factory
   * @param maxEnvelopeSize Maximum allowed envelope size in bytes (default: 1000)
   */
  constructor(maxEnvelopeSize: number = 1000) {
    this.maxEnvelopeSize = maxEnvelopeSize;
  }

  /**
   * Create envelope(s) with automatic size validation and chunking
   * @param content The content to wrap in envelope
   * @param senderPrivateKey Sender's private key for encryption
   * @param recipientPublicKey Optional recipient's public key
   * @param encryptionMode Encryption mode for the envelope
   * @param metadata Additional metadata for the envelope
   * @returns Single Envelope if under size limit, Set of Envelopes if chunked
   */
  async createEnvelope(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode = EncryptionMode.PROTECTED,
    metadata: Record<string, string> = {}
  ): Promise<Envelope | Set<Envelope>> {
    // Merge default metadata with provided metadata
    const defaultMetadata = { 'agent_id': 'postfiat_research_agent_001' };
    const finalMetadata = { ...defaultMetadata, ...metadata };

    // Try to create a single envelope first
    try {
      const envelope = await this.createSingleEnvelope(
        content,
        senderPrivateKey,
        recipientPublicKey,
        encryptionMode,
        finalMetadata
      );
      this.validateEnvelopeSize(envelope);
      return envelope;
    } catch (error) {
      if (error instanceof EnvelopeValidationError) {
        // Need to chunk the content
        return await this.createChunkedEnvelopes(
          content,
          senderPrivateKey,
          recipientPublicKey,
          encryptionMode,
          finalMetadata
        );
      }
      throw error;
    }
  }

  /**
   * Create a single envelope from content
   */
  private async createSingleEnvelope(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode,
    metadata: Record<string, string>
  ): Promise<Envelope> {
    // Create core message
    const coreMessage = new CoreMessage();
    coreMessage.content = content;
    coreMessage.contextReferences = [];
    coreMessage.metadata = { 'timestamp': '2024-07-07T12:00:00Z' };

    // Serialize core message
    const messageBytes = coreMessage.toBinary();

    // Create envelope using crypto module
    const envelope = await PostFiatCrypto.createEncryptedEnvelope(
      content,
      senderPrivateKey,
      recipientPublicKey,
      encryptionMode
    );

    // Override message type and add metadata
    envelope.messageType = MessageType.CORE_MESSAGE;
    envelope.message = messageBytes;
    envelope.metadata = { ...envelope.metadata, ...metadata };

    return envelope;
  }

  /**
   * Create multiple envelopes from chunked content
   */
  private async createChunkedEnvelopes(
    content: string,
    senderPrivateKey: string,
    recipientPublicKey?: string,
    encryptionMode: EncryptionMode,
    metadata: Record<string, string>
  ): Promise<Set<Envelope>> {
    // Generate unique message ID for this chunked message
    const messageId = crypto.randomUUID();

    // Calculate hash of complete message
    const contentBytes = new TextEncoder().encode(content);
    const hashBuffer = await crypto.subtle.digest('SHA-256', contentBytes);
    const completeMessageHash = Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    // Estimate chunk size accounting for envelope overhead
    const estimatedOverhead = 200; // Conservative estimate for envelope fields
    const targetContentSize = this.maxEnvelopeSize - estimatedOverhead;

    if (targetContentSize <= 0) {
      throw new EnvelopeValidationError(
        `Maximum size ${this.maxEnvelopeSize} too small to accommodate envelope overhead`
      );
    }

    // Split content into chunks
    const chunks: Uint8Array[] = [];
    for (let i = 0; i < contentBytes.length; i += targetContentSize) {
      const chunkContent = contentBytes.slice(i, i + targetContentSize);
      chunks.push(chunkContent);
    }

    if (chunks.length === 0) {
      throw new EnvelopeValidationError('No chunks created from content');
    }

    const totalParts = chunks.length;
    const envelopes = new Set<Envelope>();

    for (let partNumber = 1; partNumber <= chunks.length; partNumber++) {
      const chunkContent = chunks[partNumber - 1];

      // Create multipart message part
      const multipartPart = new MultiPartMessagePart();
      multipartPart.messageId = messageId;
      multipartPart.partNumber = partNumber;
      multipartPart.totalParts = totalParts;
      multipartPart.content = chunkContent;
      multipartPart.completeMessageHash = completeMessageHash;

      // Serialize the multipart message part
      const multipartBytes = multipartPart.toBinary();

      // Create chunk-specific metadata
      const chunkMetadata = {
        ...metadata,
        'chunk_info': `part_${partNumber}_of_${totalParts}`,
        'message_id': messageId
      };

      // Create envelope using crypto module for the serialized multipart data
      const envelope = await PostFiatCrypto.createEncryptedEnvelope(
        new TextDecoder().decode(multipartBytes), // Convert binary to string for crypto
        senderPrivateKey,
        recipientPublicKey,
        encryptionMode
      );

      // Override fields for multipart envelope
      envelope.messageType = MessageType.MULTIPART_MESSAGE_PART;
      envelope.message = multipartBytes;
      envelope.metadata = { ...envelope.metadata, ...chunkMetadata };

      // Validate each chunk envelope size
      try {
        this.validateEnvelopeSize(envelope);
        envelopes.add(envelope);
      } catch (error) {
        throw new EnvelopeValidationError(
          `Chunk ${partNumber} still exceeds size limit after chunking: ${error.message}`
        );
      }
    }

    return envelopes;
  }

  /**
   * Validate envelope size against maximum allowed size
   */
  private validateEnvelopeSize(envelope: Envelope): void {
    const envelopeBytes = envelope.toBinary();
    const envelopeSize = envelopeBytes.length;

    if (envelopeSize > this.maxEnvelopeSize) {
      throw new EnvelopeValidationError(
        `Envelope size ${envelopeSize} bytes exceeds maximum allowed size of ${this.maxEnvelopeSize} bytes`
      );
    }
  }

  /**
   * Reconstruct original content from chunked envelopes
   * @param envelopes Array of envelope chunks
   * @returns Reconstructed original content string
   */
  static async reconstructContentFromChunks(envelopes: Envelope[]): Promise<string> {
    if (envelopes.length === 0) {
      throw new EnvelopeValidationError('No envelopes provided for reconstruction');
    }

    // Extract multipart message parts
    const parts: MultiPartMessagePart[] = [];
    let messageId: string | null = null;
    let completeMessageHash: string | null = null;

    for (const envelope of envelopes) {
      if (envelope.messageType !== MessageType.MULTIPART_MESSAGE_PART) {
        throw new EnvelopeValidationError(
          `Expected MULTIPART_MESSAGE_PART, got ${envelope.messageType}`
        );
      }

      // Deserialize the multipart message part
      const multipartPart = MultiPartMessagePart.fromBinary(envelope.message);

      // Validate message ID consistency
      if (messageId === null) {
        messageId = multipartPart.messageId;
        completeMessageHash = multipartPart.completeMessageHash;
      } else if (messageId !== multipartPart.messageId) {
        throw new EnvelopeValidationError(
          `Message ID mismatch: expected ${messageId}, got ${multipartPart.messageId}`
        );
      } else if (completeMessageHash !== multipartPart.completeMessageHash) {
        throw new EnvelopeValidationError('Complete message hash mismatch between chunks');
      }

      parts.push(multipartPart);
    }

    // Sort parts by part number
    parts.sort((a, b) => a.partNumber - b.partNumber);

    // Validate part sequence
    const expectedTotal = parts[0]?.totalParts || 0;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const expectedPartNumber = i + 1;
      if (part.partNumber !== expectedPartNumber) {
        throw new EnvelopeValidationError(
          `Missing or out-of-order part: expected ${expectedPartNumber}, got ${part.partNumber}`
        );
      }
      if (part.totalParts !== expectedTotal) {
        throw new EnvelopeValidationError(
          `Total parts mismatch: expected ${expectedTotal}, got ${part.totalParts}`
        );
      }
    }

    if (parts.length !== expectedTotal) {
      throw new EnvelopeValidationError(
        `Incomplete parts: expected ${expectedTotal}, got ${parts.length}`
      );
    }

    // Reconstruct content
    const contentChunks: Uint8Array[] = parts.map(part => part.content);
    const totalLength = contentChunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const contentBytes = new Uint8Array(totalLength);

    let offset = 0;
    for (const chunk of contentChunks) {
      contentBytes.set(chunk, offset);
      offset += chunk.length;
    }

    const content = new TextDecoder().decode(contentBytes);

    // Validate reconstructed content hash
    const hashBuffer = await crypto.subtle.digest('SHA-256', contentBytes);
    const reconstructedHash = Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    if (reconstructedHash !== completeMessageHash) {
      throw new EnvelopeValidationError('Reconstructed content hash does not match expected hash');
    }

    return content;
  }
}