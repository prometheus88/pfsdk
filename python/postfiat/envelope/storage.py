"""Storage backends for PostFiat envelope content.

Provides different strategies for storing and retrieving content.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Set
import hashlib
import uuid
from ..v3.messages_pb2 import (
    ContentDescriptor, Envelope, CoreMessage, 
    MultiPartMessagePart, MessageType, EncryptionMode
)
from ..exceptions import ValidationError


class ContentStorage(ABC):
    """Abstract base class for content storage strategies."""
    
    @abstractmethod
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content and return a descriptor.
        
        Args:
            content: Raw content bytes to store
            content_type: MIME type of the content
            
        Returns:
            ContentDescriptor with URI and metadata
        """
        pass
    
    @abstractmethod
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content from storage.
        
        Args:
            descriptor: Content descriptor with URI
            
        Returns:
            Raw content bytes
        """
        pass
    
    @abstractmethod
    def can_handle(self, uri: str) -> bool:
        """Check if this storage can handle the given URI scheme.
        
        Args:
            uri: URI to check
            
        Returns:
            True if this storage can handle the URI
        """
        pass


class IPFSStorage(ContentStorage):
    """IPFS content storage implementation."""
    
    def __init__(self, gateway_url: str = "http://localhost:5001"):
        """Initialize IPFS storage.
        
        Args:
            gateway_url: IPFS API gateway URL
        """
        self.gateway_url = gateway_url
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content in IPFS."""
        # Calculate content hash
        content_hash = hashlib.sha256(content).digest()
        
        # TODO: Actual IPFS implementation
        # import ipfshttpclient
        # client = ipfshttpclient.connect(self.gateway_url)
        # result = client.add_bytes(content)
        # cid = result['Hash']
        
        # For now, simulate with hash-based CID
        cid = f"Qm{content_hash.hex()[:44]}"
        
        return ContentDescriptor(
            uri=f"ipfs://{cid}",
            content_type=content_type,
            content_length=len(content),
            content_hash=content_hash,
            metadata={
                "storage_provider": "ipfs",
                "gateway_url": self.gateway_url
            }
        )
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content from IPFS."""
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid IPFS URI: {descriptor.uri}")
        
        # Extract CID from URI
        cid = descriptor.uri[7:]  # Remove "ipfs://" prefix
        
        # TODO: Actual IPFS retrieval
        # import ipfshttpclient
        # client = ipfshttpclient.connect(self.gateway_url)
        # return client.cat(cid)
        
        raise NotImplementedError("IPFS retrieval not yet implemented")
    
    def can_handle(self, uri: str) -> bool:
        """Check if URI is an IPFS URI."""
        return uri.startswith("ipfs://")


class MultipartStorage(ContentStorage):
    """Storage-agnostic multipart message chunking.
    
    This storage backend has no knowledge of the underlying ledger.
    It just creates multipart envelopes that can be stored anywhere.
    """
    
    def __init__(self, max_part_size: int = 800):
        """Initialize multipart storage.
        
        Args:
            max_part_size: Maximum size per envelope part in bytes
        """
        self.max_part_size = max_part_size
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Create multipart descriptor - no actual storage happens here."""
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        # Calculate content hash
        content_hash = hashlib.sha256(content).digest()
        
        # Calculate number of parts needed
        total_parts = (len(content) + self.max_part_size - 1) // self.max_part_size
        
        # Create multipart URI - describes how to find all parts
        uri = f"multipart://{message_id}"
        
        return ContentDescriptor(
            uri=uri,
            content_type=content_type,
            content_length=len(content),
            content_hash=content_hash,
            metadata={
                "storage_provider": "multipart",
                "message_id": message_id,
                "total_parts": str(total_parts),
                "part_size": str(self.max_part_size)
            }
        )
    
    def create_part_envelopes(
        self, 
        content: bytes, 
        descriptor: ContentDescriptor,
        encryption_mode: EncryptionMode = EncryptionMode.PROTECTED,
        base_metadata: dict = None
    ) -> Set[Envelope]:
        """Create multipart envelopes for ledger storage.
        
        Args:
            content: Content to split into parts
            descriptor: Content descriptor with multipart metadata
            encryption_mode: Encryption mode for envelopes
            base_metadata: Base metadata for all envelopes
            
        Returns:
            Set of envelopes containing multipart message parts
        """
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid ledger URI: {descriptor.uri}")
        
        message_id = descriptor.metadata.get("message_id")
        total_parts = int(descriptor.metadata.get("total_parts", "0"))
        
        if not message_id or total_parts == 0:
            raise ValidationError("Missing multipart metadata")
        
        envelopes = set()
        
        for i in range(0, len(content), self.max_part_size):
            part_number = (i // self.max_part_size) + 1
            chunk_content = content[i:i + self.max_part_size]
            
            # Create multipart message part
            multipart = MultiPartMessagePart(
                message_id=message_id,
                part_number=part_number,
                total_parts=total_parts,
                content=chunk_content,
                complete_message_hash=descriptor.content_hash.hex()
            )
            
            # Create envelope for this part
            message_bytes = multipart.SerializeToString()
            
            metadata = (base_metadata or {}).copy()
            metadata.update({
                "multipart": f"{part_number}/{total_parts}",
                "message_id": message_id
            })
            
            envelope = Envelope(
                version=1,
                content_hash=hashlib.sha256(message_bytes).hexdigest(),
                message_type=MessageType.MULTIPART_MESSAGE_PART,
                encryption=encryption_mode,
                message=message_bytes,
                metadata=metadata
            )
            
            envelopes.add(envelope)
        
        return envelopes
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve requires collecting all parts - not implemented here."""
        raise NotImplementedError(
            "Multipart retrieval requires collecting all envelope parts by message_id"
        )
    
    def can_handle(self, uri: str) -> bool:
        """Check if URI is a multipart URI."""
        return uri.startswith("multipart://")


class HTTPStorage(ContentStorage):
    """HTTP/HTTPS content storage implementation."""
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content via HTTP POST."""
        # This would typically POST to a content server
        raise NotImplementedError("HTTP storage not yet implemented")
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content via HTTP GET."""
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid HTTP URI: {descriptor.uri}")
        
        # TODO: Implement HTTP retrieval
        # import requests
        # response = requests.get(descriptor.uri)
        # return response.content
        
        raise NotImplementedError("HTTP retrieval not yet implemented")
    
    def can_handle(self, uri: str) -> bool:
        """Check if URI is an HTTP/HTTPS URI."""
        return uri.startswith("http://") or uri.startswith("https://")


class CompositeStorage(ContentStorage):
    """Composite storage that delegates to appropriate backend."""
    
    def __init__(self, storages: List[ContentStorage]):
        """Initialize with list of storage backends.
        
        Args:
            storages: List of storage backends to use
        """
        self.storages = storages
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store using the first available storage backend."""
        if not self.storages:
            raise ValidationError("No storage backends configured")
        
        # Use first storage backend for storing
        return self.storages[0].store(content, content_type)
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve using appropriate storage backend based on URI."""
        for storage in self.storages:
            if storage.can_handle(descriptor.uri):
                return storage.retrieve(descriptor)
        
        raise ValidationError(f"No storage backend can handle URI: {descriptor.uri}")
    
    def can_handle(self, uri: str) -> bool:
        """Check if any storage backend can handle the URI."""
        return any(storage.can_handle(uri) for storage in self.storages)