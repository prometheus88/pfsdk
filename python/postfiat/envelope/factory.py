"""PostFiat Envelope Factory

Factory for creating envelopes with automatic size validation and chunking.
"""

import hashlib
import uuid
from typing import List, Set, Union
from ..v3.messages_pb2 import Envelope, CoreMessage, MultiPartMessagePart, MessageType, EncryptionMode
from ..exceptions import ValidationError


class EnvelopeFactory:
    """Factory for creating PostFiat envelopes with size validation and automatic chunking."""
    
    def __init__(self, max_envelope_size: int = 1000):
        """Initialize the envelope factory.
        
        Args:
            max_envelope_size: Maximum allowed envelope size in bytes (default: 1000)
        """
        self.max_envelope_size = max_envelope_size
    
    def create_envelope(
        self,
        content: str,
        context_references: list = None,
        encryption_mode: EncryptionMode = EncryptionMode.PROTECTED,
        metadata: dict = None
    ) -> Union[Envelope, Set[Envelope]]:
        """Create envelope(s) with automatic size validation and chunking.
        
        Args:
            content: The content to wrap in envelope
            context_references: Optional context references
            encryption_mode: Encryption mode for the envelope
            metadata: Additional metadata for the envelope
            
        Returns:
            Single Envelope if under size limit, Set of Envelopes if chunked
            
        Raises:
            ValidationError: If envelope creation fails
        """
        # Merge default metadata with provided metadata
        default_metadata = {"agent_id": "postfiat_research_agent_001"}
        if metadata:
            default_metadata.update(metadata)
        
        # Try to create a single envelope first
        try:
            envelope = self._create_single_envelope(
                content, context_references, encryption_mode, default_metadata
            )
            self._validate_envelope_size(envelope)
            return envelope
        except ValidationError:
            # Need to chunk the content
            return self._create_chunked_envelopes(
                content, context_references, encryption_mode, default_metadata
            )
    
    def _create_single_envelope(
        self,
        content: str,
        context_references: list,
        encryption_mode: EncryptionMode,
        metadata: dict
    ) -> Envelope:
        """Create a single envelope from content."""
        core_message = CoreMessage(
            content=content,
            context_references=context_references or [],
            metadata={"timestamp": "2024-07-07T12:00:00Z"}
        )
        
        message_bytes = core_message.SerializeToString()
        
        envelope = Envelope(
            version=1,
            content_hash=hashlib.sha256(message_bytes).hexdigest(),
            message_type=MessageType.CORE_MESSAGE,
            encryption=encryption_mode,
            message=message_bytes,
            metadata=metadata
        )
        
        return envelope
    
    def _create_chunked_envelopes(
        self,
        content: str,
        context_references: list,
        encryption_mode: EncryptionMode,
        metadata: dict
    ) -> Set[Envelope]:
        """Create multiple envelopes from chunked content."""
        # Generate unique message ID for this chunked message
        message_id = str(uuid.uuid4())
        
        # Calculate hash of complete message
        complete_message_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Estimate chunk size accounting for envelope overhead
        estimated_overhead = 200  # Conservative estimate for envelope fields
        target_content_size = self.max_envelope_size - estimated_overhead
        
        if target_content_size <= 0:
            raise ValidationError(
                f"Maximum size {self.max_envelope_size} too small to accommodate envelope overhead"
            )
        
        # Split content into chunks
        content_bytes = content.encode('utf-8')
        chunks = []
        
        for i in range(0, len(content_bytes), target_content_size):
            chunk_content = content_bytes[i:i + target_content_size]
            chunks.append(chunk_content)
        
        if not chunks:
            raise ValidationError("No chunks created from content")
        
        total_parts = len(chunks)
        envelopes = set()
        
        for part_number, chunk_content in enumerate(chunks, 1):
            # Create multipart message part
            multipart_part = MultiPartMessagePart(
                message_id=message_id,
                part_number=part_number,
                total_parts=total_parts,
                content=chunk_content,
                complete_message_hash=complete_message_hash
            )
            
            # Serialize the multipart message part
            multipart_bytes = multipart_part.SerializeToString()
            
            # Create chunk-specific metadata
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_info": f"part_{part_number}_of_{total_parts}",
                "message_id": message_id
            })
            
            # Create envelope containing this part
            envelope = Envelope(
                version=1,
                content_hash=hashlib.sha256(multipart_bytes).hexdigest(),
                message_type=MessageType.MULTIPART_MESSAGE_PART,
                encryption=encryption_mode,
                message=multipart_bytes,
                metadata=chunk_metadata
            )
            
            # Validate each chunk envelope size
            try:
                self._validate_envelope_size(envelope)
                envelopes.add(envelope)
            except ValidationError as e:
                raise ValidationError(
                    f"Chunk {part_number} still exceeds size limit after chunking: {e}"
                )
        
        return envelopes
    
    def _validate_envelope_size(self, envelope: Envelope) -> None:
        """Validate envelope size against maximum allowed size."""
        envelope_bytes = envelope.SerializeToString()
        envelope_size = len(envelope_bytes)
        
        if envelope_size > self.max_envelope_size:
            raise ValidationError(
                f"Envelope size {envelope_size} bytes exceeds maximum allowed size of {self.max_envelope_size} bytes"
            )
    
    @staticmethod
    def reconstruct_content_from_chunks(envelopes: List[Envelope]) -> str:
        """Reconstruct original content from chunked envelopes.
        
        Args:
            envelopes: List of envelope chunks
            
        Returns:
            Reconstructed original content string
            
        Raises:
            ValidationError: If reconstruction fails or chunks are invalid
        """
        if not envelopes:
            raise ValidationError("No envelopes provided for reconstruction")
        
        # Extract multipart message parts
        parts = []
        message_id = None
        complete_message_hash = None
        
        for envelope in envelopes:
            if envelope.message_type != MessageType.MULTIPART_MESSAGE_PART:
                raise ValidationError(f"Expected MULTIPART_MESSAGE_PART, got {envelope.message_type}")
            
            # Deserialize the multipart message part
            multipart_part = MultiPartMessagePart()
            multipart_part.ParseFromString(envelope.message)
            
            # Validate message ID consistency
            if message_id is None:
                message_id = multipart_part.message_id
                complete_message_hash = multipart_part.complete_message_hash
            elif message_id != multipart_part.message_id:
                raise ValidationError(
                    f"Message ID mismatch: expected {message_id}, got {multipart_part.message_id}"
                )
            elif complete_message_hash != multipart_part.complete_message_hash:
                raise ValidationError("Complete message hash mismatch between chunks")
            
            parts.append(multipart_part)
        
        # Sort parts by part number
        parts.sort(key=lambda p: p.part_number)
        
        # Validate part sequence
        expected_total = parts[0].total_parts if parts else 0
        for i, part in enumerate(parts, 1):
            if part.part_number != i:
                raise ValidationError(f"Missing or out-of-order part: expected {i}, got {part.part_number}")
            if part.total_parts != expected_total:
                raise ValidationError(f"Total parts mismatch: expected {expected_total}, got {part.total_parts}")
        
        if len(parts) != expected_total:
            raise ValidationError(f"Incomplete parts: expected {expected_total}, got {len(parts)}")
        
        # Reconstruct content
        content_bytes = b''.join(part.content for part in parts)
        content = content_bytes.decode('utf-8')
        
        # Validate reconstructed content hash
        reconstructed_hash = hashlib.sha256(content_bytes).hexdigest()
        if reconstructed_hash != complete_message_hash:
            raise ValidationError("Reconstructed content hash does not match expected hash")
        
        return content