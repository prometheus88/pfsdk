"""Storage backends for PostFiat envelope content.

Provides different strategies for storing and retrieving content.
"""

from abc import ABC, abstractmethod
from typing import Tuple, List
import hashlib
import uuid
import json
import base64
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
        self._client = None
    
    @property
    def client(self):
        """Lazy-load IPFS client."""
        if self._client is None:
            try:
                import ipfshttpclient
                self._client = ipfshttpclient.connect(self.gateway_url)
            except ImportError:
                raise ImportError(
                    "ipfshttpclient is required for IPFS storage. "
                    "Install with: pip install postfiat-sdk[storage]"
                )
            except Exception as e:
                raise ConnectionError(f"Failed to connect to IPFS at {self.gateway_url}: {e}")
        return self._client
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content in IPFS."""
        # Calculate content hash
        content_hash = hashlib.sha256(content).digest()
        
        try:
            # Add content to IPFS
            result = self.client.add_bytes(content)
            cid = result
            
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
        except Exception as e:
            # Fallback to simulated CID if IPFS is not available
            cid = f"Qm{content_hash.hex()[:44]}"
            return ContentDescriptor(
                uri=f"ipfs://{cid}",
                content_type=content_type,
                content_length=len(content),
                content_hash=content_hash,
                metadata={
                    "storage_provider": "ipfs",
                    "gateway_url": self.gateway_url,
                    "simulated": "true",
                    "error": str(e)
                }
            )
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content from IPFS."""
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid IPFS URI: {descriptor.uri}")
        
        # Extract CID from URI
        cid = descriptor.uri[7:]  # Remove "ipfs://" prefix
        
        try:
            # Retrieve content from IPFS
            return self.client.cat(cid)
        except Exception as e:
            raise IOError(f"Failed to retrieve content from IPFS: {e}")
    
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
    ) -> List[Envelope]:
        """Create multipart envelopes for ledger storage.
        
        Args:
            content: Content to split into parts
            descriptor: Content descriptor with multipart metadata
            encryption_mode: Encryption mode for envelopes
            base_metadata: Base metadata for all envelopes
            
        Returns:
            List of envelopes containing multipart message parts
        """
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid ledger URI: {descriptor.uri}")
        
        message_id = descriptor.metadata.get("message_id")
        total_parts = int(descriptor.metadata.get("total_parts", "0"))
        
        if not message_id or total_parts == 0:
            raise ValidationError("Missing multipart metadata")
        
        envelopes = []
        
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
                content_hash=hashlib.sha256(message_bytes).digest(),
                message_type=MessageType.MULTIPART_MESSAGE_PART,
                encryption=encryption_mode,
                message=message_bytes,
                metadata=metadata
            )
            
            envelopes.append(envelope)
        
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


class RedisStorage(ContentStorage):
    """Redis content storage implementation."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", key_prefix: str = "postfiat:content"):
        """Initialize Redis storage.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self._client = None
    
    @property
    def client(self):
        """Lazy-load Redis client."""
        if self._client is None:
            try:
                import redis
                self._client = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError(
                    "redis is required for Redis storage. "
                    "Install with: pip install postfiat-sdk[storage]"
                )
        return self._client
    
    def _content_key(self, content_hash: bytes) -> str:
        """Get Redis key for content."""
        return f"{self.key_prefix}:{content_hash.hex()}"
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content in Redis."""
        # Calculate content hash
        content_hash = hashlib.sha256(content).digest()
        
        # Store content in Redis
        key = self._content_key(content_hash)
        
        # Store content and metadata together
        content_data = {
            "content": base64.b64encode(content).decode(),
            "content_type": content_type,
            "content_length": len(content),
            "content_hash": content_hash.hex()
        }
        
        try:
            self.client.set(key, json.dumps(content_data))
            
            return ContentDescriptor(
                uri=f"redis://{content_hash.hex()}",
                content_type=content_type,
                content_length=len(content),
                content_hash=content_hash,
                metadata={
                    "storage_provider": "redis",
                    "redis_key": key,
                    "redis_url": self.redis_url
                }
            )
        except Exception as e:
            raise IOError(f"Failed to store content in Redis: {e}")
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content from Redis."""
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid Redis URI: {descriptor.uri}")
        
        # Extract content hash from URI
        content_hash_hex = descriptor.uri[8:]  # Remove "redis://" prefix
        content_hash = bytes.fromhex(content_hash_hex)
        
        key = self._content_key(content_hash)
        
        try:
            content_data = self.client.get(key)
            if content_data is None:
                raise IOError(f"Content not found in Redis: {descriptor.uri}")
            
            data = json.loads(content_data)
            content = base64.b64decode(data["content"])
            
            # Verify content hash
            if hashlib.sha256(content).digest() != content_hash:
                raise IOError(f"Content hash mismatch for {descriptor.uri}")
            
            return content
        except Exception as e:
            raise IOError(f"Failed to retrieve content from Redis: {e}")
    
    def can_handle(self, uri: str) -> bool:
        """Check if URI is a Redis URI."""
        return uri.startswith("redis://")


class InlineStorage(ContentStorage):
    """Inline content storage - stores content directly in descriptor."""
    
    def store(self, content: bytes, content_type: str) -> ContentDescriptor:
        """Store content inline in descriptor."""
        # Calculate content hash
        content_hash = hashlib.sha256(content).digest()
        
        # Encode content as base64 for inline storage
        content_b64 = base64.b64encode(content).decode()
        
        return ContentDescriptor(
            uri=f"inline://data",
            content_type=content_type,
            content_length=len(content),
            content_hash=content_hash,
            metadata={
                "storage_provider": "inline",
                "content_data": content_b64
            }
        )
    
    def retrieve(self, descriptor: ContentDescriptor) -> bytes:
        """Retrieve content from descriptor metadata."""
        if not self.can_handle(descriptor.uri):
            raise ValidationError(f"Invalid inline URI: {descriptor.uri}")
        
        try:
            content_b64 = descriptor.metadata.get("content_data")
            if not content_b64:
                raise IOError(f"No inline content data found in descriptor")
            
            content = base64.b64decode(content_b64)
            
            # Verify content hash
            if hashlib.sha256(content).digest() != descriptor.content_hash:
                raise IOError(f"Content hash mismatch for inline content")
            
            return content
        except Exception as e:
            raise IOError(f"Failed to retrieve inline content: {e}")
    
    def can_handle(self, uri: str) -> bool:
        """Check if URI is an inline URI."""
        return uri.startswith("inline://")