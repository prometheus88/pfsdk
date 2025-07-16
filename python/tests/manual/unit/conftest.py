"""
pytest configuration for PostFiat gRPC service tests.
"""

import pytest
import grpc
from concurrent import futures


@pytest.fixture
def grpc_server():
    """Create a gRPC server for testing."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    yield server
    server.stop(0)


@pytest.fixture
def grpc_context():
    """Create a mock gRPC context."""
    from unittest.mock import Mock
    context = Mock(spec=grpc.ServicerContext)
    context.set_code = Mock()
    context.set_details = Mock()
    return context


@pytest.fixture
def mock_storage():
    """Create a mock storage backend."""
    from unittest.mock import Mock
    storage = Mock()
    storage.store = Mock()
    storage.retrieve = Mock()
    storage.can_handle = Mock(return_value=True)
    return storage


@pytest.fixture
def mock_envelope_store():
    """Create a mock envelope store."""
    from unittest.mock import Mock
    import asyncio
    
    store = Mock()
    store.store = Mock(return_value=asyncio.Future())
    store.retrieve = Mock(return_value=asyncio.Future())
    store.delete = Mock(return_value=asyncio.Future())
    store.exists = Mock(return_value=asyncio.Future())
    
    # Set future results
    store.store.return_value.set_result("test-envelope-id")
    store.retrieve.return_value.set_result(Mock())
    store.delete.return_value.set_result(True)
    store.exists.return_value.set_result(True)
    
    return store
