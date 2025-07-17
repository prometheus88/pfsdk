"""
Redis envelope storage implementation.

This module provides Redis-based envelope storage with indexing capabilities.
Uses the envelope's built-in fields and metadata map for all data.
"""

import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime

from ..envelope_store import EnvelopeStore, EnvelopeNotFoundError, StorageError
from ...v3.messages_pb2 import Envelope


class RedisEnvelopeStore(EnvelopeStore):
    """Redis-based envelope storage with indexing."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", key_prefix: str = "postfiat"):
        """Initialize Redis envelope store.
        
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
                import redis.asyncio as redis
                self._client = redis.from_url(self.redis_url)
            except ImportError:
                raise ImportError(
                    "redis is required for Redis storage. "
                    "Install with: pip install postfiat-sdk[storage]"
                )
        return self._client
    
    def _envelope_key(self, envelope_id: str) -> str:
        """Get Redis key for envelope data."""
        return f"{self.key_prefix}:envelope:{envelope_id}"
    
    def _metadata_key(self, envelope_id: str) -> str:
        """Get Redis key for envelope metadata."""
        return f"{self.key_prefix}:metadata:{envelope_id}"
    
    def _content_hash_key(self, content_hash: bytes) -> str:
        """Get Redis key for content hash index."""
        return f"{self.key_prefix}:content_hash:{content_hash.hex()}"
    
    def _context_key(self, context_hash: bytes) -> str:
        """Get Redis key for context reference index."""
        return f"{self.key_prefix}:context:{context_hash.hex()}"
    
    def _sender_key(self, sender: str) -> str:
        """Get Redis key for sender index."""
        return f"{self.key_prefix}:sender:{sender}"
    
    def _generate_envelope_id(self, envelope: Envelope) -> str:
        """Generate unique envelope ID from envelope content."""
        envelope_bytes = envelope.SerializeToString()
        return hashlib.sha256(envelope_bytes).hexdigest()
    
    async def store(self, envelope: Envelope) -> str:
        """Store envelope in Redis with indexing."""
        try:
            envelope_id = self._generate_envelope_id(envelope)
            
            # Add storage-specific metadata to envelope
            envelope.metadata["storage_backend"] = "redis"
            envelope.metadata["envelope_id"] = envelope_id
            
            # Serialize envelope
            envelope_data = envelope.SerializeToString()
            
            # Prepare storage metadata (Redis-specific info)
            storage_metadata = {
                "envelope_id": envelope_id,
                "storage_backend": "redis",
                "stored_at": str(datetime.now().timestamp())
            }
            
            # Use Redis pipeline for atomic operations
            pipe = self.client.pipeline()
            
            # Store envelope and storage metadata
            pipe.set(self._envelope_key(envelope_id), envelope_data)
            pipe.set(self._metadata_key(envelope_id), json.dumps(storage_metadata))
            
            # Update indexes
            pipe.sadd(self._content_hash_key(envelope.content_hash), envelope_id)
            
            # Index context references
            for context_ref in envelope.public_references:
                pipe.sadd(self._context_key(context_ref.content_hash), envelope_id)
            
            # Index sender if provided in envelope metadata
            sender = envelope.metadata.get("sender")
            if sender:
                pipe.zadd(self._sender_key(sender), {
                    envelope_id: float(envelope.metadata.get("timestamp", "0"))
                })
            
            await pipe.execute()
            
            return envelope_id
            
        except Exception as e:
            raise StorageError(f"Failed to store envelope: {e}")
    
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve envelope from Redis."""
        try:
            envelope_data = await self.client.get(self._envelope_key(envelope_id))
            
            if envelope_data is None:
                raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found")
            
            envelope = Envelope()
            envelope.ParseFromString(envelope_data)
            return envelope
            
        except EnvelopeNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve envelope: {e}")
    
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find envelopes by content hash."""
        try:
            envelope_ids = await self.client.smembers(self._content_hash_key(content_hash))
            
            envelopes = []
            for envelope_id in envelope_ids:
                try:
                    envelope = await self.retrieve(envelope_id.decode())
                    envelopes.append(envelope)
                except EnvelopeNotFoundError:
                    # Clean up stale index entry
                    await self.client.srem(self._content_hash_key(content_hash), envelope_id)
            
            return envelopes
            
        except Exception as e:
            raise StorageError(f"Failed to find envelopes by content hash: {e}")
    
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find envelopes by context reference."""
        try:
            envelope_ids = await self.client.smembers(self._context_key(context_hash))
            
            envelopes = []
            for envelope_id in envelope_ids:
                try:
                    envelope = await self.retrieve(envelope_id.decode())
                    envelopes.append(envelope)
                except EnvelopeNotFoundError:
                    # Clean up stale index entry
                    await self.client.srem(self._context_key(context_hash), envelope_id)
            
            return envelopes
            
        except Exception as e:
            raise StorageError(f"Failed to find envelopes by context: {e}")
    
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List envelopes by sender (most recent first)."""
        try:
            # Get envelope IDs sorted by timestamp (most recent first)
            envelope_ids = await self.client.zrevrange(self._sender_key(sender), 0, limit - 1)
            
            envelopes = []
            for envelope_id in envelope_ids:
                try:
                    envelope = await self.retrieve(envelope_id.decode())
                    envelopes.append(envelope)
                except EnvelopeNotFoundError:
                    # Clean up stale index entry
                    await self.client.zrem(self._sender_key(sender), envelope_id)
            
            return envelopes
            
        except Exception as e:
            raise StorageError(f"Failed to list envelopes by sender: {e}")
    
    async def delete(self, envelope_id: str) -> bool:
        """Delete envelope and clean up indexes."""
        try:
            # Get envelope first to clean up indexes
            envelope = await self.retrieve(envelope_id)
            
            pipe = self.client.pipeline()
            
            # Delete envelope and storage metadata
            pipe.delete(self._envelope_key(envelope_id))
            pipe.delete(self._metadata_key(envelope_id))
            
            # Clean up indexes
            pipe.srem(self._content_hash_key(envelope.content_hash), envelope_id)
            
            # Clean up context reference indexes
            for context_ref in envelope.public_references:
                pipe.srem(self._context_key(context_ref.content_hash), envelope_id)
            
            # Clean up sender index if present
            sender = envelope.metadata.get("sender")
            if sender:
                pipe.zrem(self._sender_key(sender), envelope_id)
            
            results = await pipe.execute()
            
            # Check if envelope was actually deleted
            return results[0] > 0  # delete() returns number of keys deleted
            
        except EnvelopeNotFoundError:
            return False
        except Exception as e:
            raise StorageError(f"Failed to delete envelope: {e}")
    
    async def exists(self, envelope_id: str) -> bool:
        """Check if envelope exists."""
        try:
            return await self.client.exists(self._envelope_key(envelope_id))
        except Exception as e:
            raise StorageError(f"Failed to check envelope existence: {e}")
    
    async def get_envelope_metadata(self, envelope_id: str) -> Dict[str, str]:
        """Get Redis-specific storage metadata."""
        try:
            metadata_data = await self.client.get(self._metadata_key(envelope_id))
            
            if metadata_data is None:
                raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found")
            
            return json.loads(metadata_data)
            
        except EnvelopeNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to get envelope metadata: {e}")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get Redis backend information."""
        return {
            "type": "redis",
            "url": self.redis_url,
            "key_prefix": self.key_prefix
        }