"""
PostFiat Envelope Storage Service Implementation

Generated service implementation that uses the existing envelope storage backends.
"""

import grpc
from typing import Optional, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from postfiat.v3.messages_pb2_grpc import PostFiatEnvelopeStorageServiceServicer
from postfiat.v3.messages_pb2 import (
    StoreEnvelopeRequest,
    StoreEnvelopeResponse,
    RetrieveEnvelopeRequest,
    SearchEnvelopesRequest,
    SearchEnvelopesResponse,
    DeleteEnvelopeRequest,
    EnvelopeExistsRequest,
    EnvelopeExistsResponse,
    FindEnvelopesByContentHashRequest,
    FindEnvelopesByContentHashResponse,
    FindEnvelopesByContextRequest,
    FindEnvelopesByContextResponse,
    ListEnvelopesBySenderRequest,
    ListEnvelopesBySenderResponse,
    Envelope
)
from postfiat.envelope.envelope_store import EnvelopeStore
from postfiat.envelope.stores.redis_store import RedisEnvelopeStore
from postfiat.envelope.stores.evm_store import EVMEnvelopeStore
from postfiat.envelope.stores.xrpl_store import XRPLEnvelopeStore
from postfiat.exceptions import ValidationError
from google.protobuf.empty_pb2 import Empty


class EnvelopeStorageServiceImpl(PostFiatEnvelopeStorageServiceServicer):
    """Implementation of PostFiatEnvelopeStorage service using existing envelope stores."""
    
    def __init__(self, store: Optional[EnvelopeStore] = None):
        """Initialize with envelope store.
        
        Args:
            store: Envelope store backend. If None, creates default Redis store.
        """
        self.store = store or RedisEnvelopeStore()
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def StoreEnvelope(self, request: StoreEnvelopeRequest, context: grpc.ServicerContext) -> StoreEnvelopeResponse:
        """Store envelope."""
        try:
            # Convert protobuf envelope to storage envelope
            envelope = self._pb_to_storage_envelope(request.envelope)
            
            # Get preferred storage if specified
            store = self.store
            if request.preferred_storage:
                store = self._get_store_by_type(request.preferred_storage)
                if not store:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(f"Unknown storage type: {request.preferred_storage}")
                    return StoreEnvelopeResponse()
            
            # Store envelope (run async operation in executor)
            future = self.executor.submit(self._store_envelope_async, store, envelope)
            envelope_id = future.result(timeout=30)  # 30 second timeout
            
            # Create response
            response = StoreEnvelopeResponse()
            response.envelope_id = envelope_id
            response.storage_backend = self._get_store_backend_name(store)
            
            # Add metadata from envelope
            for key, value in envelope.metadata.items():
                response.metadata[key] = value
            
            return response
            
        except ValidationError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return StoreEnvelopeResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Storage error: {str(e)}")
            return StoreEnvelopeResponse()
    
    def RetrieveEnvelope(self, request: RetrieveEnvelopeRequest, context: grpc.ServicerContext) -> Envelope:
        """Retrieve envelope by ID."""
        try:
            # Retrieve envelope (run async operation in executor)
            future = self.executor.submit(self._retrieve_envelope_async, request.envelope_id)
            envelope = future.result(timeout=30)  # 30 second timeout
            
            # Convert to protobuf
            return self._storage_to_pb_envelope(envelope)
            
        except FileNotFoundError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Envelope not found")
            return Envelope()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Retrieval error: {str(e)}")
            return Envelope()
    
    def SearchEnvelopes(self, request: SearchEnvelopesRequest, context: grpc.ServicerContext) -> SearchEnvelopesResponse:
        """Search envelopes (placeholder - not implemented)."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Search operation not implemented")
        return SearchEnvelopesResponse()
    
    def DeleteEnvelope(self, request: DeleteEnvelopeRequest, context: grpc.ServicerContext) -> Empty:
        """Delete envelope."""
        try:
            # Delete envelope (run async operation in executor)
            future = self.executor.submit(self._delete_envelope_async, request.envelope_id)
            deleted = future.result(timeout=30)  # 30 second timeout
            
            if not deleted:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Envelope not found")
            
            return Empty()
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Delete error: {str(e)}")
            return Empty()
    
    def EnvelopeExists(self, request: EnvelopeExistsRequest, context: grpc.ServicerContext) -> EnvelopeExistsResponse:
        """Check if envelope exists."""
        try:
            # Check existence (run async operation in executor)
            future = self.executor.submit(self._envelope_exists_async, request.envelope_id)
            exists = future.result(timeout=30)  # 30 second timeout
            
            response = EnvelopeExistsResponse()
            response.exists = exists
            response.storage_backend = self._get_store_backend_name(self.store)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Existence check error: {str(e)}")
            return EnvelopeExistsResponse()
    
    def FindEnvelopesByContentHash(self, request: FindEnvelopesByContentHashRequest, context: grpc.ServicerContext) -> FindEnvelopesByContentHashResponse:
        """Find envelopes by content hash."""
        try:
            # Find envelopes (run async operation in executor)
            content_hash = bytes.fromhex(request.content_hash)
            future = self.executor.submit(self._find_by_content_hash_async, content_hash, request.limit)
            envelopes = future.result(timeout=30)  # 30 second timeout
            
            # Convert to protobuf
            response = FindEnvelopesByContentHashResponse()
            for envelope in envelopes:
                pb_envelope = self._storage_to_pb_envelope(envelope)
                response.envelopes.append(pb_envelope)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Search error: {str(e)}")
            return FindEnvelopesByContentHashResponse()
    
    def FindEnvelopesByContext(self, request: FindEnvelopesByContextRequest, context: grpc.ServicerContext) -> FindEnvelopesByContextResponse:
        """Find envelopes by context."""
        try:
            # Find envelopes (run async operation in executor)
            context_hash = bytes.fromhex(request.context_hash)
            future = self.executor.submit(self._find_by_context_async, context_hash, request.limit)
            envelopes = future.result(timeout=30)  # 30 second timeout
            
            # Convert to protobuf
            response = FindEnvelopesByContextResponse()
            for envelope in envelopes:
                pb_envelope = self._storage_to_pb_envelope(envelope)
                response.envelopes.append(pb_envelope)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Search error: {str(e)}")
            return FindEnvelopesByContextResponse()
    
    def ListEnvelopesBySender(self, request: ListEnvelopesBySenderRequest, context: grpc.ServicerContext) -> ListEnvelopesBySenderResponse:
        """List envelopes by sender."""
        try:
            # List envelopes (run async operation in executor)
            future = self.executor.submit(self._list_by_sender_async, request.sender, request.limit)
            envelopes = future.result(timeout=30)  # 30 second timeout
            
            # Convert to protobuf
            response = ListEnvelopesBySenderResponse()
            for envelope in envelopes:
                pb_envelope = self._storage_to_pb_envelope(envelope)
                response.envelopes.append(pb_envelope)
            
            response.total_count = len(envelopes)
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"List error: {str(e)}")
            return ListEnvelopesBySenderResponse()
    
    def _store_envelope_async(self, store: EnvelopeStore, envelope) -> str:
        """Async wrapper for envelope storage."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(store.store(envelope))
        finally:
            loop.close()
    
    def _retrieve_envelope_async(self, envelope_id: str):
        """Async wrapper for envelope retrieval."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.retrieve(envelope_id))
        finally:
            loop.close()
    
    def _delete_envelope_async(self, envelope_id: str) -> bool:
        """Async wrapper for envelope deletion."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.delete(envelope_id))
        finally:
            loop.close()
    
    def _envelope_exists_async(self, envelope_id: str) -> bool:
        """Async wrapper for envelope existence check."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.exists(envelope_id))
        finally:
            loop.close()
    
    def _find_by_content_hash_async(self, content_hash: bytes, limit: int) -> List:
        """Async wrapper for finding by content hash."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.findByContentHash(content_hash))
        finally:
            loop.close()
    
    def _find_by_context_async(self, context_hash: bytes, limit: int) -> List:
        """Async wrapper for finding by context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.findByContext(context_hash))
        finally:
            loop.close()
    
    def _list_by_sender_async(self, sender: str, limit: int) -> List:
        """Async wrapper for listing by sender."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.store.listBySender(sender, limit))
        finally:
            loop.close()
    
    def _get_store_by_type(self, storage_type: str) -> Optional[EnvelopeStore]:
        """Get store backend by type name."""
        if storage_type == "redis":
            return RedisEnvelopeStore()
        elif storage_type == "evm":
            return EVMEnvelopeStore()
        elif storage_type == "xrpl":
            return XRPLEnvelopeStore()
        else:
            return None
    
    def _get_store_backend_name(self, store: EnvelopeStore) -> str:
        """Get backend name for store instance."""
        class_name = store.__class__.__name__
        if "Redis" in class_name:
            return "redis"
        elif "EVM" in class_name:
            return "evm"
        elif "XRPL" in class_name:
            return "xrpl"
        else:
            return "unknown"
    
    def _pb_to_storage_envelope(self, pb_envelope: Envelope):
        """Convert protobuf Envelope to storage Envelope."""
        from postfiat.envelope.factory import EnvelopeFactory
        
        # Create envelope using factory
        envelope = EnvelopeFactory.create_envelope(
            version=pb_envelope.version,
            content_hash=bytes(pb_envelope.content_hash),
            message_type=pb_envelope.message_type,
            encryption=pb_envelope.encryption,
            message=bytes(pb_envelope.message),
            reply_to=pb_envelope.reply_to
        )
        
        # Add metadata
        for key, value in pb_envelope.metadata.items():
            envelope.metadata[key] = value
        
        return envelope
    
    def _storage_to_pb_envelope(self, storage_envelope) -> Envelope:
        """Convert storage Envelope to protobuf Envelope."""
        pb_envelope = Envelope()
        pb_envelope.version = storage_envelope.version
        pb_envelope.content_hash = storage_envelope.content_hash
        pb_envelope.message_type = storage_envelope.message_type
        pb_envelope.encryption = storage_envelope.encryption
        pb_envelope.message = storage_envelope.message
        pb_envelope.reply_to = storage_envelope.reply_to
        
        # Add metadata
        for key, value in storage_envelope.metadata.items():
            pb_envelope.metadata[key] = value
        
        return pb_envelope