"""
Unit tests for content storage classes.

Tests the manual ContentStorage implementations: IPFSStorage, RedisStorage, 
InlineStorage, MultipartStorage, and CompositeStorage.
"""

import pytest
import hashlib
import base64
import json
from unittest.mock import Mock, patch, MagicMock
from typing import List

from postfiat.envelope.storage import (
    ContentStorage, IPFSStorage, RedisStorage, InlineStorage, 
    MultipartStorage, CompositeStorage
)
from postfiat.v3.messages_pb2 import ContentDescriptor
from postfiat.exceptions import ValidationError


class TestInlineStorage:
    """Test InlineStorage implementation."""
    
    def setup_method(self):
        self.storage = InlineStorage()
        self.test_content = b"Hello, World!"
        self.test_content_type = "text/plain"
    
    def test_store_content(self):
        """Test storing content inline."""
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        assert descriptor.uri == "inline://data"
        assert descriptor.content_type == self.test_content_type
        assert descriptor.content_length == len(self.test_content)
        assert descriptor.content_hash == hashlib.sha256(self.test_content).digest()
        assert descriptor.metadata["storage_provider"] == "inline"
        assert "content_data" in descriptor.metadata
        
        # Verify content is base64 encoded
        stored_content = base64.b64decode(descriptor.metadata["content_data"])
        assert stored_content == self.test_content
    
    def test_retrieve_content(self):
        """Test retrieving content inline."""
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        retrieved_content = self.storage.retrieve(descriptor)
        
        assert retrieved_content == self.test_content
    
    def test_can_handle_uri(self):
        """Test URI handling."""
        assert self.storage.can_handle("inline://data")
        assert not self.storage.can_handle("ipfs://QmTest")
        assert not self.storage.can_handle("redis://test")
    
    def test_retrieve_invalid_uri(self):
        """Test retrieving with invalid URI."""
        descriptor = ContentDescriptor()
        descriptor.uri = "ipfs://invalid"
        
        with pytest.raises(ValidationError, match="Invalid inline URI"):
            self.storage.retrieve(descriptor)
    
    def test_retrieve_missing_content_data(self):
        """Test retrieving with missing content data."""
        descriptor = ContentDescriptor()
        descriptor.uri = "inline://data"
        
        with pytest.raises(IOError, match="No inline content data found"):
            self.storage.retrieve(descriptor)
    
    def test_retrieve_hash_mismatch(self):
        """Test retrieving with hash mismatch."""
        descriptor = ContentDescriptor()
        descriptor.uri = "inline://data"
        descriptor.content_hash = b"wrong_hash"
        descriptor.metadata["content_data"] = base64.b64encode(self.test_content).decode()
        
        with pytest.raises(IOError, match="Content hash mismatch"):
            self.storage.retrieve(descriptor)


class TestRedisStorage:
    """Test RedisStorage implementation."""
    
    def setup_method(self):
        self.storage = RedisStorage()
        self.test_content = b"Hello, Redis!"
        self.test_content_type = "text/plain"
    
    @patch('redis.from_url')
    def test_store_content(self, mock_from_url):
        """Test storing content in Redis."""
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        # Verify Redis client was called
        mock_from_url.assert_called_once_with("redis://localhost:6379")
        mock_client.set.assert_called_once()
        
        # Verify descriptor
        content_hash = hashlib.sha256(self.test_content).digest()
        assert descriptor.uri == f"redis://{content_hash.hex()}"
        assert descriptor.content_type == self.test_content_type
        assert descriptor.content_length == len(self.test_content)
        assert descriptor.content_hash == content_hash
        assert descriptor.metadata["storage_provider"] == "redis"
    
    @patch('redis.from_url')
    def test_retrieve_content(self, mock_from_url):
        """Test retrieving content from Redis."""
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        
        # Store first to get descriptor
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        # Mock Redis get response
        content_data = {
            "content": base64.b64encode(self.test_content).decode(),
            "content_type": self.test_content_type,
            "content_length": len(self.test_content),
            "content_hash": hashlib.sha256(self.test_content).digest().hex()
        }
        mock_client.get.return_value = json.dumps(content_data)
        
        retrieved_content = self.storage.retrieve(descriptor)
        assert retrieved_content == self.test_content
    
    @patch('redis.from_url')
    def test_retrieve_not_found(self, mock_from_url):
        """Test retrieving non-existent content."""
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        mock_client.get.return_value = None
        
        descriptor = ContentDescriptor()
        descriptor.uri = "redis://nonexistent"
        
        with pytest.raises(IOError, match="Content not found in Redis"):
            self.storage.retrieve(descriptor)
    
    def test_can_handle_uri(self):
        """Test URI handling."""
        assert self.storage.can_handle("redis://test")
        assert not self.storage.can_handle("ipfs://QmTest")
        assert not self.storage.can_handle("inline://data")
    
    def test_import_error(self):
        """Test behavior when Redis is not installed."""
        with patch('redis.from_url', side_effect=ImportError):
            with pytest.raises(ImportError, match="redis is required"):
                _ = self.storage.client


class TestIPFSStorage:
    """Test IPFSStorage implementation."""
    
    def setup_method(self):
        self.storage = IPFSStorage()
        self.test_content = b"Hello, IPFS!"
        self.test_content_type = "text/plain"
    
    @patch('ipfshttpclient.connect')
    def test_store_content_success(self, mock_connect):
        """Test successful content storage in IPFS."""
        mock_client = Mock()
        mock_connect.return_value = mock_client
        mock_client.add_bytes.return_value = "QmTestHash"
        
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        # Verify IPFS client was called
        mock_connect.assert_called_once_with("http://localhost:5001")
        mock_client.add_bytes.assert_called_once_with(self.test_content)
        
        # Verify descriptor
        assert descriptor.uri == "ipfs://QmTestHash"
        assert descriptor.content_type == self.test_content_type
        assert descriptor.metadata["storage_provider"] == "ipfs"
        assert "simulated" not in descriptor.metadata
    
    @patch('ipfshttpclient.connect')
    def test_store_content_fallback(self, mock_connect):
        """Test content storage fallback when IPFS fails."""
        mock_connect.side_effect = Exception("IPFS connection failed")
        
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        # Should fall back to simulated CID
        content_hash = hashlib.sha256(self.test_content).digest()
        expected_cid = f"Qm{content_hash.hex()[:44]}"
        
        assert descriptor.uri == f"ipfs://{expected_cid}"
        assert descriptor.metadata["simulated"] == "true"
        assert "error" in descriptor.metadata
    
    @patch('ipfshttpclient.connect')
    def test_retrieve_content(self, mock_connect):
        """Test retrieving content from IPFS."""
        mock_client = Mock()
        mock_connect.return_value = mock_client
        mock_client.cat.return_value = self.test_content
        
        descriptor = ContentDescriptor()
        descriptor.uri = "ipfs://QmTestHash"
        
        retrieved_content = self.storage.retrieve(descriptor)
        
        mock_client.cat.assert_called_once_with("QmTestHash")
        assert retrieved_content == self.test_content
    
    def test_can_handle_uri(self):
        """Test URI handling."""
        assert self.storage.can_handle("ipfs://QmTest")
        assert not self.storage.can_handle("redis://test")
        assert not self.storage.can_handle("inline://data")
    
    def test_import_error(self):
        """Test behavior when IPFS client is not installed."""
        with patch('ipfshttpclient.connect', side_effect=ImportError):
            with pytest.raises(ImportError, match="ipfshttpclient is required"):
                _ = self.storage.client


class TestMultipartStorage:
    """Test MultipartStorage implementation."""
    
    def setup_method(self):
        self.storage = MultipartStorage(max_part_size=100)
        self.test_content = b"x" * 250  # Will need 3 parts
        self.test_content_type = "application/octet-stream"
    
    def test_store_content(self):
        """Test storing content that requires multipart."""
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        assert descriptor.uri.startswith("multipart://")
        assert descriptor.content_type == self.test_content_type
        assert descriptor.content_length == len(self.test_content)
        assert descriptor.content_hash == hashlib.sha256(self.test_content).digest()
        assert descriptor.metadata["storage_provider"] == "multipart"
        assert descriptor.metadata["total_parts"] == "3"
        assert descriptor.metadata["part_size"] == "100"
    
    def test_create_part_envelopes(self):
        """Test creating multipart envelopes."""
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        envelopes = self.storage.create_part_envelopes(self.test_content, descriptor)
        
        assert len(envelopes) == 3
        
        # Check envelope content
        parts = []
        for envelope in envelopes:
            # Parse the envelope message to get the multipart message part
            # This is a simplified test - in reality we'd parse the protobuf
            parts.append(envelope)
        
        assert len(parts) == 3
    
    def test_can_handle_uri(self):
        """Test URI handling."""
        assert self.storage.can_handle("multipart://test-id")
        assert not self.storage.can_handle("ipfs://QmTest")
        assert not self.storage.can_handle("redis://test")
    
    def test_single_part_content(self):
        """Test content that fits in a single part."""
        small_content = b"small"
        storage = MultipartStorage(max_part_size=100)
        
        descriptor = storage.store(small_content, self.test_content_type)
        
        assert descriptor.metadata["total_parts"] == "1"


class TestCompositeStorage:
    """Test CompositeStorage implementation."""
    
    def setup_method(self):
        self.inline_storage = InlineStorage()
        self.redis_storage = RedisStorage()
        self.ipfs_storage = IPFSStorage()
        
        self.storage = CompositeStorage([
            self.inline_storage,
            self.redis_storage,
            self.ipfs_storage
        ])
        
        self.test_content = b"Hello, Composite!"
        self.test_content_type = "text/plain"
    
    def test_store_uses_first_storage(self):
        """Test that store uses the first storage backend."""
        descriptor = self.storage.store(self.test_content, self.test_content_type)
        
        # Should use inline storage (first in list)
        assert descriptor.uri == "inline://data"
        assert descriptor.metadata["storage_provider"] == "inline"
    
    def test_retrieve_finds_appropriate_storage(self):
        """Test that retrieve finds the appropriate storage backend."""
        # Store content in inline storage
        inline_descriptor = self.inline_storage.store(self.test_content, self.test_content_type)
        
        # Should retrieve using inline storage
        retrieved_content = self.storage.retrieve(inline_descriptor)
        assert retrieved_content == self.test_content
    
    def test_retrieve_unsupported_uri(self):
        """Test retrieving with unsupported URI."""
        descriptor = ContentDescriptor()
        descriptor.uri = "unknown://test"
        
        with pytest.raises(ValidationError, match="No storage backend can handle URI"):
            self.storage.retrieve(descriptor)
    
    def test_can_handle_multiple_schemes(self):
        """Test that composite storage can handle multiple URI schemes."""
        assert self.storage.can_handle("inline://data")
        assert self.storage.can_handle("redis://test")
        assert self.storage.can_handle("ipfs://QmTest")
        assert not self.storage.can_handle("unknown://test")


if __name__ == "__main__":
    pytest.main([__file__])