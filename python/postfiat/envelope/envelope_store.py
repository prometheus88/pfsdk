"""
Abstract envelope storage interface with dependency injection.

This module provides the base interface for envelope persistence and retrieval
across different storage backends (Redis, Ethereum, XRPL).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

from ..v3.messages_pb2 import Envelope
from ..logging import get_logger


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
        self.logger = get_logger("store.composite")
        self.stores = stores
        self.default_store = default_store
        
        if default_store not in stores:
            raise ValueError(f"Default store '{default_store}' not found in stores")
            
        self.logger.info(
            "Initialized composite envelope store",
            store_count=len(stores),
            store_names=list(stores.keys()),
            default_store=default_store
        )
    
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
        self.logger.info(
            "Storing envelope in composite store",
            message_type=envelope.message_type,
            default_store=self.default_store
        )
        return await self.get_store().store(envelope)
    
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve from all stores until found."""
        self.logger.info(
            "Retrieving envelope from composite store",
            envelope_id=envelope_id[:16] + "...",
            store_count=len(self.stores)
        )
        
        for store_name, store in self.stores.items():
            try:
                envelope = await store.retrieve(envelope_id)
                self.logger.info(
                    "Envelope found in store",
                    envelope_id=envelope_id[:16] + "...",
                    store_name=store_name,
                    message_type=envelope.message_type
                )
                return envelope
            except EnvelopeNotFoundError:
                continue
        
        self.logger.warning(
            "Envelope not found in any store",
            envelope_id=envelope_id[:16] + "...",
            searched_stores=list(self.stores.keys())
        )
        raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found in any store")
    
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find across all stores and combine results."""
        self.logger.info(
            "Finding envelopes by content hash across all stores",
            content_hash=content_hash.hex()[:16] + "...",
            store_count=len(self.stores)
        )
        
        results = []
        for store_name, store in self.stores.items():
            store_results = await store.find_by_content_hash(content_hash)
            if store_results:
                self.logger.debug(
                    "Found envelopes in store",
                    store_name=store_name,
                    count=len(store_results),
                    content_hash=content_hash.hex()[:16] + "..."
                )
            results.extend(store_results)
        
        self.logger.info(
            "Content hash search completed",
            total_found=len(results),
            content_hash=content_hash.hex()[:16] + "..."
        )
        return results
    
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find across all stores and combine results."""
        self.logger.info(
            "Finding envelopes by context hash across all stores",
            context_hash=context_hash.hex()[:16] + "...",
            store_count=len(self.stores)
        )
        
        results = []
        for store_name, store in self.stores.items():
            store_results = await store.find_by_context(context_hash)
            if store_results:
                self.logger.debug(
                    "Found envelopes in store",
                    store_name=store_name,
                    count=len(store_results),
                    context_hash=context_hash.hex()[:16] + "..."
                )
            results.extend(store_results)
        
        self.logger.info(
            "Context hash search completed",
            total_found=len(results),
            context_hash=context_hash.hex()[:16] + "..."
        )
        return results
    
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List across all stores and combine results."""
        self.logger.info(
            "Listing envelopes by sender across all stores",
            sender=sender,
            limit=limit,
            store_count=len(self.stores)
        )
        
        results = []
        remaining_limit = limit
        
        for store_name, store in self.stores.items():
            if remaining_limit <= 0:
                break
            
            store_results = await store.list_by_sender(sender, remaining_limit)
            if store_results:
                self.logger.debug(
                    "Found envelopes in store",
                    store_name=store_name,
                    count=len(store_results),
                    sender=sender
                )
            results.extend(store_results)
            remaining_limit -= len(store_results)
        
        final_results = results[:limit]
        self.logger.info(
            "Sender listing completed",
            sender=sender,
            total_found=len(final_results),
            requested_limit=limit
        )
        return final_results
    
    async def delete(self, envelope_id: str) -> bool:
        """Delete from all stores."""
        self.logger.info(
            "Deleting envelope from all stores",
            envelope_id=envelope_id[:16] + "...",
            store_count=len(self.stores)
        )
        
        deleted = False
        for store_name, store in self.stores.items():
            try:
                if await store.delete(envelope_id):
                    self.logger.info(
                        "Envelope deleted from store",
                        envelope_id=envelope_id[:16] + "...",
                        store_name=store_name
                    )
                    deleted = True
            except Exception as e:
                self.logger.warning(
                    "Failed to delete from store",
                    envelope_id=envelope_id[:16] + "...",
                    store_name=store_name,
                    error=str(e)
                )
        
        self.logger.info(
            "Delete operation completed",
            envelope_id=envelope_id[:16] + "...",
            deleted=deleted
        )
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