"""PostFiat Envelope Factory

Factory for creating envelopes with pluggable content storage strategies.
"""

import hashlib
from typing import Optional, Tuple, Union, Set
from ..v3.messages_pb2 import (
    Envelope, CoreMessage, ContentDescriptor, 
    PostFiatEnvelopePayload, MessageType, EncryptionMode
)
from ..exceptions import ValidationError
from .storage import ContentStorage, IPFSStorage, MultipartStorage


class EnvelopeFactory:
    """Factory for creating PostFiat envelopes with pluggable storage."""
    
    def __init__(
        self, 
        max_envelope_size: int = 1000,
        storage: Optional[ContentStorage] = None
    ):
        """Initialize the envelope factory.
        
        Args:
            max_envelope_size: Maximum allowed envelope size in bytes (default: 1000)
            storage: Content storage backend (defaults to IPFS)
        """
        self.max_envelope_size = max_envelope_size
        self.storage = storage or IPFSStorage()
    
    def create_envelope(
        self,
        content: str,
        context_references: list = None,
        encryption_mode: EncryptionMode = EncryptionMode.PROTECTED,
        metadata: dict = None,
        content_type: str = "text/plain; charset=utf-8"
    ) -> Union[Envelope, Tuple[Envelope, ContentDescriptor], Set[Envelope]]:
        """Create envelope(s) with automatic size handling.
        
        Returns one of:
        - Single Envelope (if content fits)
        - Tuple[Envelope, ContentDescriptor] (if using external storage)
        - Set[Envelope] (if using ledger multipart storage)
        
        Args:
            content: The content to wrap in envelope
            context_references: Optional context references
            encryption_mode: Encryption mode for the envelope
            metadata: Additional metadata for the envelope
            content_type: MIME type of the content
            
        Returns:
            Envelope(s) and optional ContentDescriptor
            
        Raises:
            ValidationError: If envelope creation fails
        """
        # Merge default metadata with provided metadata
        default_metadata = {"agent_id": "postfiat_research_agent_001"}
        if metadata:
            default_metadata.update(metadata)
        
        # Try to embed content directly if small enough
        envelope = self._try_create_embedded_envelope(
            content, context_references, encryption_mode, default_metadata
        )
        
        if envelope:
            # Content fits in envelope
            return envelope
        
        # Content too large - use storage backend
        content_bytes = content.encode('utf-8')
        descriptor = self.storage.store(content_bytes, content_type)
        
        # Handle special case of multipart storage
        if isinstance(self.storage, MultipartStorage):
            # Create multiple envelopes for multipart storage
            return self.storage.create_part_envelopes(
                content_bytes, descriptor, encryption_mode, default_metadata
            )
        
        # Create minimal envelope that references external content
        reference_envelope = self._create_reference_envelope(
            descriptor, context_references, encryption_mode, default_metadata
        )
        
        return reference_envelope, descriptor
    
    def create_envelope_payload(
        self,
        content: str,
        context_references: list = None,
        encryption_mode: EncryptionMode = EncryptionMode.PROTECTED,
        metadata: dict = None,
        content_type: str = "text/plain; charset=utf-8",
        postfiat_metadata: dict = None
    ) -> PostFiatEnvelopePayload:
        """Create a complete PostFiatEnvelopePayload with automatic content handling.
        
        Args:
            content: The content to wrap
            context_references: Optional context references
            encryption_mode: Encryption mode for the envelope
            metadata: Additional metadata for the envelope
            content_type: MIME type of the content
            postfiat_metadata: Additional PostFiat-specific metadata
            
        Returns:
            PostFiatEnvelopePayload with envelope and optional ContentDescriptor
        """
        result = self.create_envelope(
            content, context_references, encryption_mode, metadata, content_type
        )
        
        # Default PostFiat metadata
        default_postfiat_metadata = {
            "extension_version": "v1",
            "processing_mode": "selective_disclosure"
        }
        if postfiat_metadata:
            default_postfiat_metadata.update(postfiat_metadata)
        
        # Handle different return types
        if isinstance(result, Envelope):
            # Simple embedded content
            payload = PostFiatEnvelopePayload(
                envelope=result,
                postfiat_metadata=default_postfiat_metadata
            )
        elif isinstance(result, tuple):
            # External storage with descriptor
            envelope, descriptor = result
            payload = PostFiatEnvelopePayload(
                envelope=envelope,
                postfiat_metadata=default_postfiat_metadata
            )
            if descriptor:
                payload.content.CopyFrom(descriptor)
        elif isinstance(result, set):
            # Multipart envelopes - return payload for first part
            envelopes = list(result)
            if not envelopes:
                raise ValidationError("No envelopes created")
            
            # Sort by part number for consistent ordering
            sorted_envelopes = sorted(
                envelopes, 
                key=lambda e: int(e.metadata.get("multipart", "1/1").split("/")[0])
            )
            
            payload = PostFiatEnvelopePayload(
                envelope=sorted_envelopes[0],
                postfiat_metadata=default_postfiat_metadata
            )
            payload.postfiat_metadata["total_parts"] = str(len(envelopes))
        else:
            raise ValidationError(f"Unexpected result type: {type(result)}")
        
        return payload
    
    def _try_create_embedded_envelope(
        self,
        content: str,
        context_references: list,
        encryption_mode: EncryptionMode,
        metadata: dict
    ) -> Optional[Envelope]:
        """Try to create envelope with embedded content."""
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
        
        # Check if it fits
        envelope_bytes = envelope.SerializeToString()
        if len(envelope_bytes) <= self.max_envelope_size:
            return envelope
        
        return None
    
    def _create_reference_envelope(
        self,
        content_descriptor: ContentDescriptor,
        context_references: list,
        encryption_mode: EncryptionMode,
        metadata: dict
    ) -> Envelope:
        """Create minimal envelope that references external content."""
        # Create a minimal core message that references the external content
        core_message = CoreMessage(
            content=f"Content stored at: {content_descriptor.uri}",
            context_references=context_references or [],
            metadata={
                "timestamp": "2024-07-07T12:00:00Z",
                "content_uri": content_descriptor.uri,
                "content_type": content_descriptor.content_type
            }
        )
        
        message_bytes = core_message.SerializeToString()
        
        # Add reference to external content in envelope metadata
        envelope_metadata = metadata.copy()
        envelope_metadata["content_uri"] = content_descriptor.uri
        
        envelope = Envelope(
            version=1,
            content_hash=hashlib.sha256(message_bytes).hexdigest(),
            message_type=MessageType.CORE_MESSAGE,
            encryption=encryption_mode,
            message=message_bytes,
            metadata=envelope_metadata
        )
        
        return envelope
    
    @staticmethod
    def reconstruct_content_from_chunks(envelopes: list[Envelope]) -> str:
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
        
        # Import here to avoid circular dependency
        from ..v3.messages_pb2 import MultiPartMessagePart
        
        # Extract multipart message parts
        parts = []
        message_id = None
        complete_message_hash = None
        
        for envelope in envelopes:
            if envelope.message_type != MessageType.MULTIPART_MESSAGE_PART:
                raise ValidationError(
                    f"Expected MULTIPART_MESSAGE_PART, got {envelope.message_type}"
                )
            
            # Deserialize the multipart message part
            multipart_part = MultiPartMessagePart()
            multipart_part.ParseFromString(envelope.message)
            
            # Validate message ID consistency
            if message_id is None:
                message_id = multipart_part.message_id
                complete_message_hash = multipart_part.complete_message_hash
            elif message_id != multipart_part.message_id:
                raise ValidationError(
                    f"Message ID mismatch: expected {message_id}, "
                    f"got {multipart_part.message_id}"
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
                raise ValidationError(
                    f"Missing or out-of-order part: expected {i}, "
                    f"got {part.part_number}"
                )
            if part.total_parts != expected_total:
                raise ValidationError(
                    f"Total parts mismatch: expected {expected_total}, "
                    f"got {part.total_parts}"
                )
        
        if len(parts) != expected_total:
            raise ValidationError(
                f"Incomplete parts: expected {expected_total}, got {len(parts)}"
            )
        
        # Reconstruct content
        content_bytes = b''.join(part.content for part in parts)
        content = content_bytes.decode('utf-8')
        
        # Validate reconstructed content hash
        reconstructed_hash = hashlib.sha256(content_bytes).hexdigest()
        if reconstructed_hash != complete_message_hash:
            raise ValidationError(
                "Reconstructed content hash does not match expected hash"
            )
        
        return content