"""
PostFiat Content Storage Service Implementation

Generated service implementation that uses the existing storage backends.
"""

import grpc
from typing import Optional

from postfiat.v3.messages_pb2_grpc import PostFiatContentStorageServiceServicer
from postfiat.v3.messages_pb2 import (
    StoreContentRequest, 
    StoreContentResponse,
    RetrieveContentRequest, 
    RetrieveContentResponse,
    DeleteContentRequest,
    CanHandleUriRequest,
    CanHandleUriResponse,
    ContentDescriptor
)
from postfiat.envelope.storage import (
    ContentStorage,
    InlineStorage,
    RedisStorage,
    IPFSStorage,
    MultipartStorage,
    CompositeStorage
)
from postfiat.exceptions import ValidationError
from google.protobuf.empty_pb2 import Empty


class ContentStorageServiceImpl(PostFiatContentStorageServiceServicer):
    """Implementation of PostFiatContentStorage service using existing storage backends."""
    
    def __init__(self, storage: Optional[ContentStorage] = None):
        """Initialize with storage backend.
        
        Args:
            storage: Content storage backend. If None, creates default composite storage.
        """
        self.storage = storage or self._create_default_storage()
    
    def _create_default_storage(self) -> ContentStorage:
        """Create default composite storage with all backends."""
        return CompositeStorage([
            InlineStorage(),
            RedisStorage(),
            IPFSStorage(),
            MultipartStorage()
        ])
    
    def StoreContent(self, request: StoreContentRequest, context: grpc.ServicerContext) -> StoreContentResponse:
        """Store content and return descriptor."""
        try:
            # Convert request to storage parameters
            content = bytes(request.content)
            content_type = request.content_type
            
            # Use preferred storage if specified and available
            storage = self.storage
            if request.preferred_storage:
                storage = self._get_storage_by_type(request.preferred_storage)
                if not storage:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(f"Unknown storage type: {request.preferred_storage}")
                    return ContentDescriptor()
            
            # Store content
            descriptor = storage.store(content, content_type)
            
            # Convert to protobuf response
            pb_descriptor = ContentDescriptor()
            pb_descriptor.uri = descriptor.uri
            pb_descriptor.content_type = descriptor.content_type
            pb_descriptor.content_length = descriptor.content_length
            pb_descriptor.content_hash = descriptor.content_hash
            
            # Convert metadata
            for key, value in descriptor.metadata.items():
                pb_descriptor.metadata[key] = value
            
            return StoreContentResponse(descriptor=pb_descriptor)
            
        except ValidationError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return StoreContentResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Storage error: {str(e)}")
            return StoreContentResponse()
    
    def RetrieveContent(self, request: RetrieveContentRequest, context: grpc.ServicerContext) -> RetrieveContentResponse:
        """Retrieve content by descriptor."""
        try:
            # Convert protobuf descriptor to storage descriptor
            descriptor = self._pb_to_storage_descriptor(request.descriptor)
            
            # Retrieve content
            content = self.storage.retrieve(descriptor)
            
            # Create response
            response = RetrieveContentResponse()
            response.content = content
            response.content_type = descriptor.content_type
            response.content_length = len(content)
            
            return response
            
        except ValidationError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return RetrieveContentResponse()
        except FileNotFoundError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Content not found")
            return RetrieveContentResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Retrieval error: {str(e)}")
            return RetrieveContentResponse()
    
    def DeleteContent(self, request: DeleteContentRequest, context: grpc.ServicerContext) -> Empty:
        """Delete content (placeholder - not implemented in current storage)."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Delete operation not implemented")
        return Empty()
    
    def CanHandleUri(self, request: CanHandleUriRequest, context: grpc.ServicerContext) -> CanHandleUriResponse:
        """Check if storage can handle URI."""
        try:
            can_handle = self.storage.can_handle(request.uri)
            
            # Determine storage provider
            storage_provider = "unknown"
            if can_handle:
                if isinstance(self.storage, CompositeStorage):
                    # Find which storage can handle this URI
                    for storage in self.storage.storages:
                        if storage.can_handle(request.uri):
                            storage_provider = self._get_storage_provider_name(storage)
                            break
                else:
                    storage_provider = self._get_storage_provider_name(self.storage)
            
            response = CanHandleUriResponse()
            response.can_handle = can_handle
            response.storage_provider = storage_provider
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"URI check error: {str(e)}")
            return CanHandleUriResponse()
    
    def _get_storage_by_type(self, storage_type: str) -> Optional[ContentStorage]:
        """Get storage backend by type name."""
        if isinstance(self.storage, CompositeStorage):
            for storage in self.storage.storages:
                if self._get_storage_provider_name(storage) == storage_type:
                    return storage
        elif self._get_storage_provider_name(self.storage) == storage_type:
            return self.storage
        return None
    
    def _get_storage_provider_name(self, storage: ContentStorage) -> str:
        """Get provider name for storage instance."""
        class_name = storage.__class__.__name__
        if "Inline" in class_name:
            return "inline"
        elif "Redis" in class_name:
            return "redis"
        elif "IPFS" in class_name:
            return "ipfs"
        elif "Multipart" in class_name:
            return "multipart"
        else:
            return "unknown"
    
    def _pb_to_storage_descriptor(self, pb_descriptor: ContentDescriptor):
        """Convert protobuf ContentDescriptor to storage ContentDescriptor."""
        from postfiat.envelope.storage import ContentDescriptor as StorageDescriptor
        
        metadata = dict(pb_descriptor.metadata)
        
        return StorageDescriptor(
            uri=pb_descriptor.uri,
            content_type=pb_descriptor.content_type,
            content_length=pb_descriptor.content_length,
            content_hash=bytes(pb_descriptor.content_hash),
            metadata=metadata
        )