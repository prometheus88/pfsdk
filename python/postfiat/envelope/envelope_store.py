"""
Abstract envelope storage interface with dependency injection.

This module provides the base interface for envelope persistence and retrieval
across different storage backends (Redis, Ethereum, XRPL).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

from ..v3.messages_pb2 import Envelope


class EnvelopeStore(ABC):
    """Abstract interface for envelope persistence and retrieval."""
    
    @abstractmethod
    async def store(self, envelope: Envelope) -> str:
        """Store an envelope and return its unique identifier.
        
        Args:
            envelope: The envelope to store (contains all metadata in envelope.metadata)
            
        Returns:
            Unique identifier for the stored envelope
            
        Raises:
            StorageError: If storage operation fails
        """
        pass
    
    @abstractmethod
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve an envelope by its identifier.
        
        Args:
            envelope_id: Unique identifier for the envelope
            
        Returns:
            The retrieved envelope
            
        Raises:
            EnvelopeNotFoundError: If envelope is not found
            StorageError: If retrieval operation fails
        """
        pass
    
    @abstractmethod
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find envelopes by their content hash.
        
        Args:
            content_hash: Content hash to search for
            
        Returns:
            List of envelopes with matching content hash
        """
        pass
    
    @abstractmethod
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find envelopes that reference a specific context.
        
        Args:
            context_hash: Context hash to search for
            
        Returns:
            List of envelopes referencing the context
        """
        pass
    
    @abstractmethod
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List envelopes by sender.
        
        Args:
            sender: Sender identifier
            limit: Maximum number of envelopes to return
            
        Returns:
            List of envelopes from the sender
        """
        pass
    
    @abstractmethod
    async def delete(self, envelope_id: str) -> bool:
        """Delete an envelope.
        
        Args:
            envelope_id: Unique identifier for the envelope
            
        Returns:
            True if envelope was deleted, False if not found
            
        Raises:
            StorageError: If deletion operation fails
        """
        pass
    
    @abstractmethod
    async def exists(self, envelope_id: str) -> bool:
        """Check if an envelope exists.
        
        Args:
            envelope_id: Unique identifier for the envelope
            
        Returns:
            True if envelope exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_envelope_metadata(self, envelope_id: str) -> Dict[str, str]:
        """Get storage-specific metadata for an envelope.
        
        Args:
            envelope_id: Unique identifier for the envelope
            
        Returns:
            Storage-specific metadata (transaction_id, block_number, etc.)
            
        Raises:
            EnvelopeNotFoundError: If envelope is not found
        """
        pass
    
    @abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the storage backend.
        
        Returns:
            Dictionary containing backend information
        """
        pass


class CompositeEnvelopeStore(EnvelopeStore):
    """Composite envelope store that delegates to multiple backends."""
    
    def __init__(self, stores: Dict[str, EnvelopeStore], default_store: str):
        """Initialize composite store.
        
        Args:
            stores: Dictionary of store name to store instance
            default_store: Name of the default store to use
        """
        self.stores = stores
        self.default_store = default_store
        
        if default_store not in stores:
            raise ValueError(f"Default store '{default_store}' not found in stores")
    
    def get_store(self, store_name: Optional[str] = None) -> EnvelopeStore:
        """Get a specific store instance.
        
        Args:
            store_name: Name of the store, or None for default
            
        Returns:
            Store instance
        """
        if store_name is None:
            store_name = self.default_store
        
        if store_name not in self.stores:
            raise ValueError(f"Store '{store_name}' not found")
        
        return self.stores[store_name]
    
    async def store(self, envelope: Envelope) -> str:
        """Store using default store."""
        return await self.get_store().store(envelope)
    
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve from all stores until found."""
        for store in self.stores.values():
            try:
                return await store.retrieve(envelope_id)
            except EnvelopeNotFoundError:
                continue
        
        raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found in any store")
    
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find across all stores and combine results."""
        results = []
        for store in self.stores.values():
            results.extend(await store.find_by_content_hash(content_hash))
        return results
    
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find across all stores and combine results."""
        results = []
        for store in self.stores.values():
            results.extend(await store.find_by_context(context_hash))
        return results
    
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List across all stores and combine results."""
        results = []
        remaining_limit = limit
        
        for store in self.stores.values():
            if remaining_limit <= 0:
                break
            
            store_results = await store.list_by_sender(sender, remaining_limit)
            results.extend(store_results)
            remaining_limit -= len(store_results)
        
        return results[:limit]
    
    async def delete(self, envelope_id: str) -> bool:
        """Delete from all stores."""
        deleted = False
        for store in self.stores.values():
            if await store.delete(envelope_id):
                deleted = True
        return deleted
    
    async def exists(self, envelope_id: str) -> bool:
        """Check existence across all stores."""
        for store in self.stores.values():
            if await store.exists(envelope_id):
                return True
        return False
    
    async def get_envelope_metadata(self, envelope_id: str) -> Dict[str, str]:
        """Get storage metadata from first store that has the envelope."""
        for store in self.stores.values():
            try:
                return await store.get_envelope_metadata(envelope_id)
            except EnvelopeNotFoundError:
                continue
        
        raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found in any store")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get info about all backends."""
        return {
            "type": "composite",
            "default_store": self.default_store,
            "stores": {name: store.get_backend_info() for name, store in self.stores.items()}
        }


# Custom exceptions
class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class EnvelopeNotFoundError(StorageError):
    """Exception raised when an envelope is not found."""
    pass


class ValidationError(StorageError):
    """Exception raised for validation errors."""
    pass