"""
Unit tests for envelope store classes.

Tests the manual EnvelopeStore implementations: RedisEnvelopeStore, 
EVMEnvelopeStore, XRPLEnvelopeStore, and CompositeEnvelopeStore.
"""

import pytest
import hashlib
import json
import base64
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from typing import Dict, Any
import sys

# Skip integration tests if dependencies aren't available
try:
    import redis.asyncio
    redis_available = True
except ImportError:
    redis_available = False

try:
    import web3
    web3_available = True
except ImportError:
    web3_available = False

from postfiat.envelope.envelope_store import (
    EnvelopeStore, CompositeEnvelopeStore, EnvelopeNotFoundError, StorageError
)
from postfiat.envelope.stores.redis_store import RedisEnvelopeStore
from postfiat.envelope.stores.evm_store import EVMEnvelopeStore
from postfiat.envelope.stores.xrpl_store import XRPLEnvelopeStore
from postfiat.v3.messages_pb2 import Envelope, MessageType, EncryptionMode


@pytest.mark.skipif(not redis_available, reason="redis not available")
class TestRedisEnvelopeStore:
    """Test RedisEnvelopeStore implementation."""
    
    def setup_method(self):
        self.store = RedisEnvelopeStore()
        self.test_envelope = Envelope()
        self.test_envelope.version = 1
        self.test_envelope.content_hash = b"test_hash"
        self.test_envelope.message_type = MessageType.CORE_MESSAGE
        self.test_envelope.encryption = EncryptionMode.PROTECTED
        self.test_envelope.message = b"test_message"
        self.test_envelope.metadata["sender"] = "test_sender"
        self.test_envelope.metadata["timestamp"] = str(datetime.now().timestamp())
    
    @pytest.mark.asyncio
    async def test_store_envelope(self):
        """Test storing an envelope in Redis."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        mock_pipeline = AsyncMock()
        mock_client.pipeline.return_value = mock_pipeline
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            envelope_id = await self.store.store(self.test_envelope)
        
            # Verify Redis operations
            mock_asyncio.from_url.assert_called_once_with("redis://localhost:6379")
        mock_client.pipeline.assert_called_once()
        mock_pipeline.set.assert_called()
        mock_pipeline.sadd.assert_called()
        mock_pipeline.exec.assert_called_once()
        
        # Verify envelope_id is a valid hash
        assert isinstance(envelope_id, str)
        assert len(envelope_id) == 64  # SHA256 hex length
        
        # Verify metadata was added
        assert self.test_envelope.metadata["storage_backend"] == "redis"
        assert self.test_envelope.metadata["envelope_id"] == envelope_id
    
    @pytest.mark.asyncio
    async def test_retrieve_envelope(self):
        """Test retrieving an envelope from Redis."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        
        # Mock envelope data
        envelope_data = self.test_envelope.SerializeToString()
        mock_client.get.return_value = envelope_data
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            envelope_id = "test_id"
            retrieved_envelope = await self.store.retrieve(envelope_id)
        
        # Verify Redis call
        mock_client.get.assert_called_once_with(f"postfiat:envelope:{envelope_id}")
        
        # Verify envelope content
        assert retrieved_envelope.version == self.test_envelope.version
        assert retrieved_envelope.content_hash == self.test_envelope.content_hash
        assert retrieved_envelope.message_type == self.test_envelope.message_type
    
    @pytest.mark.asyncio
    async def test_retrieve_not_found(self):
        """Test retrieving non-existent envelope."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        mock_client.get.return_value = None
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            with pytest.raises(EnvelopeNotFoundError, match="Envelope 'nonexistent' not found"):
                await self.store.retrieve("nonexistent")
    
    @pytest.mark.asyncio
    async def test_find_by_content_hash(self):
        """Test finding envelopes by content hash."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            # Mock Redis responses
            mock_client.smembers.return_value = [b"envelope_id_1", b"envelope_id_2"]
            envelope_data = self.test_envelope.SerializeToString()
            mock_client.get.return_value = envelope_data
            
            content_hash = b"test_hash"
            envelopes = await self.store.find_by_content_hash(content_hash)
        
        # Verify Redis operations
        expected_key = f"postfiat:content_hash:{content_hash.hex()}"
        mock_client.smembers.assert_called_once_with(expected_key)
        
        # Should retrieve each envelope
        assert len(envelopes) == 2
        assert all(isinstance(env, Envelope) for env in envelopes)
    
    @pytest.mark.asyncio
    async def test_exists(self):
        """Test checking if envelope exists."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        mock_client.exists.return_value = 1
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            exists = await self.store.exists("test_id")
            
            assert exists is True
            mock_client.exists.assert_called_once_with("postfiat:envelope:test_id")
    
    @pytest.mark.asyncio
    async def test_delete_envelope(self):
        """Test deleting an envelope."""
        mock_redis = MagicMock()
        mock_asyncio = MagicMock()
        mock_client = AsyncMock()
        mock_asyncio.from_url.return_value = mock_client
        
        with patch.dict('sys.modules', {'redis': mock_redis, 'redis.asyncio': mock_asyncio}):
            # Mock retrieve for cleanup
            envelope_data = self.test_envelope.SerializeToString()
            mock_client.get.return_value = envelope_data
            
            # Mock pipeline operations
            mock_pipeline = AsyncMock()
            mock_client.pipeline.return_value = mock_pipeline
            mock_pipeline.exec.return_value = [[1], [1]]  # Simulate successful deletion
            
            deleted = await self.store.delete("test_id")
            
            assert deleted is True
            mock_client.pipeline.assert_called_once()
            mock_pipeline.delete.assert_called()
            mock_pipeline.exec.assert_called_once()
    
    def test_get_backend_info(self):
        """Test getting backend information."""
        info = self.store.get_backend_info()
        
        assert info["type"] == "redis"
        assert info["url"] == "redis://localhost:6379"
        assert info["key_prefix"] == "postfiat"
    
    def test_import_error(self):
        """Test behavior when Redis is not installed."""
        # Mock the import at the module level
        with patch.dict('sys.modules', {'redis.asyncio': None}):
            # Create a new store instance to trigger the import error
            from postfiat.envelope.stores.redis_store import RedisEnvelopeStore
            store = RedisEnvelopeStore()
            with pytest.raises(ImportError, match="redis is required"):
                _ = store.client


@pytest.mark.skipif(not web3_available, reason="web3 not available")
class TestEVMEnvelopeStore:
    """Test EVMEnvelopeStore implementation."""
    
    def setup_method(self):
        self.store = EVMEnvelopeStore(
            contract_address="0x123...",
            private_key="0xabc...",
            chain_id=1
        )
        self.test_envelope = Envelope()
        self.test_envelope.version = 1
        self.test_envelope.content_hash = b"test_hash"
        self.test_envelope.message_type = MessageType.CORE_MESSAGE
        self.test_envelope.message = b"test_message"
    
    @pytest.mark.asyncio
    async def test_store_envelope(self):
        """Test storing an envelope on EVM."""
        # Mock Web3 module
        mock_web3_module = MagicMock()
        mock_web3 = Mock()
        mock_web3_module.Web3.return_value = mock_web3
        mock_web3.HTTPProvider.return_value = "provider"
        
        with patch.dict('sys.modules', {'web3': mock_web3_module}):
            mock_contract = Mock()
            mock_web3.eth.contract.return_value = mock_contract
            
            # Mock account and transaction
            mock_account = Mock()
            mock_account.address = "0x123..."
            mock_web3.eth.account.from_key.return_value = mock_account
            
            mock_web3.eth.gas_price = 20000000000
            mock_web3.eth.get_transaction_count.return_value = 1
            
            # Mock transaction building and signing
            mock_transaction = {"hash": "0xabc..."}
            mock_contract.functions.storeEnvelope.return_value.build_transaction.return_value = mock_transaction
            
            mock_signed_txn = Mock()
            mock_signed_txn.rawTransaction = b"raw_tx"
            mock_web3.eth.account.sign_transaction.return_value = mock_signed_txn
            
            mock_web3.eth.send_raw_transaction.return_value = "0xhash"
            
            # Mock receipt
            mock_receipt = Mock()
            mock_receipt.transactionHash.hex.return_value = "0xhash"
            mock_receipt.blockNumber = 12345
            mock_receipt.gasUsed = 100000
            mock_web3.eth.wait_for_transaction_receipt.return_value = mock_receipt
            
            envelope_id = await self.store.store(self.test_envelope)
        
        # Verify envelope_id is valid
        assert isinstance(envelope_id, str)
        assert len(envelope_id) == 64  # SHA256 hex length
        
        # Verify metadata was added
        assert self.test_envelope.metadata["storage_backend"] == "evm"
        assert self.test_envelope.metadata["chain_id"] == "1"
        assert self.test_envelope.metadata["transaction_hash"] == "0xhash"
        assert self.test_envelope.metadata["block_number"] == "12345"
    
    @pytest.mark.asyncio
    async def test_retrieve_envelope(self):
        """Test retrieving an envelope from EVM."""
        mock_web3_module = MagicMock()
        mock_web3 = Mock()
        mock_web3_module.Web3.return_value = mock_web3
        
        with patch.dict('sys.modules', {'web3': mock_web3_module}):
            mock_contract = Mock()
            mock_web3.eth.contract.return_value = mock_contract
            
            # Mock contract call
            envelope_data = self.test_envelope.SerializeToString()
            mock_contract.functions.getEnvelope.return_value.call.return_value = envelope_data
            
            envelope_id = "1234567890abcdef1234567890abcdef12345678901234567890abcdef123456"  # Valid 64-char hex
            retrieved_envelope = await self.store.retrieve(envelope_id)
        
        # Verify contract call
        mock_contract.functions.getEnvelope.assert_called_once()
        
        # Verify envelope content
        assert retrieved_envelope.version == self.test_envelope.version
        assert retrieved_envelope.content_hash == self.test_envelope.content_hash
    
    @pytest.mark.asyncio
    async def test_delete_not_supported(self):
        """Test that delete is not supported on immutable blockchain."""
        with pytest.raises(NotImplementedError, match="not supported on immutable EVM blockchain"):
            await self.store.delete("test_id")
    
    def test_get_backend_info(self):
        """Test getting backend information."""
        info = self.store.get_backend_info()
        
        assert info["type"] == "evm"
        assert info["contract_address"] == "0x123..."
        assert info["chain_id"] == 1
    
    def test_import_error(self):
        """Test behavior when web3 is not installed."""
        # Mock the import at the module level
        with patch.dict('sys.modules', {'web3': None}):
            # Create a new store instance to trigger the import error
            from postfiat.envelope.stores.evm_store import EVMEnvelopeStore
            store = EVMEnvelopeStore(contract_address="0x123...", private_key="0xabc...", chain_id=1)
            with pytest.raises(ImportError, match="web3 is required"):
                _ = store.web3


class TestXRPLEnvelopeStore:
    """Test XRPLEnvelopeStore implementation."""
    
    def setup_method(self):
        self.store = XRPLEnvelopeStore(
            wallet_seed="sEdTM1uX8pu2do5XvTnutH6HsouMaM2",  # Valid test seed
            destination="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH"  # Valid test address
        )
        self.test_envelope = Envelope()
        self.test_envelope.version = 1
        self.test_envelope.content_hash = b"test_hash"
        self.test_envelope.message_type = MessageType.CORE_MESSAGE
        self.test_envelope.message = b"small_message"  # Keep small for memo limit
    
    @patch('xrpl.clients.JsonRpcClient')
    @patch('xrpl.wallet.Wallet')
    @patch('xrpl.transaction.submit_and_wait')
    @pytest.mark.asyncio
    async def test_store_envelope(self, mock_submit, mock_wallet_class, mock_client_class):
        """Test storing an envelope on XRPL."""
        # Mock wallet
        mock_wallet = Mock()
        mock_wallet.address = "rSender..."
        mock_wallet_class.from_seed.return_value = mock_wallet
        
        # Mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock transaction response
        mock_response = Mock()
        mock_response.result = {
            "engine_result": "tesSUCCESS",
            "tx_json": {"hash": "ABC123..."},
            "ledger_index": 12345
        }
        mock_submit.return_value = mock_response
        
        envelope_id = await self.store.store(self.test_envelope)
        
        # Verify envelope_id is valid
        assert isinstance(envelope_id, str)
        assert len(envelope_id) == 64  # SHA256 hex length
        
        # Verify metadata was added
        assert self.test_envelope.metadata["storage_backend"] == "xrpl"
        assert self.test_envelope.metadata["transaction_hash"] == "ABC123..."
        assert self.test_envelope.metadata["ledger_index"] == "12345"
    
    @patch('xrpl.clients.JsonRpcClient')
    @patch('xrpl.wallet.Wallet')
    @pytest.mark.asyncio
    async def test_retrieve_by_transaction_hash(self, mock_wallet_class, mock_client_class):
        """Test retrieving an envelope by transaction hash."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock transaction response with memo
        envelope_data = self.test_envelope.SerializeToString()
        memo_data = base64.b64encode(envelope_data).decode('ascii')
        memo_type = base64.b64encode(b"postfiat/envelope").decode('ascii')
        
        mock_response = Mock()
        mock_response.is_successful.return_value = True
        mock_response.result = {
            "Memos": [{
                "Memo": {
                    "MemoType": memo_type,
                    "MemoData": memo_data
                }
            }]
        }
        mock_client.request.return_value = mock_response
        
        retrieved_envelope = await self.store.retrieve_by_transaction_hash("ABC123...")
        
        # Verify envelope content
        assert retrieved_envelope.version == self.test_envelope.version
        assert retrieved_envelope.content_hash == self.test_envelope.content_hash
    
    @pytest.mark.asyncio
    async def test_envelope_too_large(self):
        """Test that large envelopes are rejected."""
        large_envelope = Envelope()
        large_envelope.message = b"x" * 2000  # Too large for XRPL memo
        
        with pytest.raises(StorageError, match="Envelope too large for XRPL memo"):
            await self.store.store(large_envelope)
    
    @pytest.mark.asyncio
    async def test_delete_not_supported(self):
        """Test that delete is not supported on immutable ledger."""
        with pytest.raises(NotImplementedError, match="not supported on immutable XRPL ledger"):
            await self.store.delete("test_id")
    
    def test_get_backend_info(self):
        """Test getting backend information."""
        info = self.store.get_backend_info()
        
        assert info["type"] == "xrpl"
        assert info["network"] == "mainnet"
    
    def test_import_error(self):
        """Test behavior when xrpl-py is not installed."""
        # Mock the import at the module level  
        with patch.dict('sys.modules', {'xrpl.clients': None}):
            # Create a new store instance to trigger the import error
            from postfiat.envelope.stores.xrpl_store import XRPLEnvelopeStore
            store = XRPLEnvelopeStore(wallet_seed="sEdTM1uX8pu2do5XvTnutH6HsouMaM2", destination="rN7n7otQDd6FczFgLdSqtcsAUxDkw6fzRH")
            with pytest.raises(ImportError, match="xrpl-py is required"):
                _ = store.client


class TestCompositeEnvelopeStore:
    """Test CompositeEnvelopeStore implementation."""
    
    def setup_method(self):
        self.redis_store = Mock(spec=EnvelopeStore)
        self.evm_store = Mock(spec=EnvelopeStore)
        
        self.stores = {
            "redis": self.redis_store,
            "evm": self.evm_store
        }
        
        self.composite_store = CompositeEnvelopeStore(self.stores, "redis")
        
        self.test_envelope = Envelope()
        self.test_envelope.version = 1
        self.test_envelope.content_hash = b"test_hash"
    
    @pytest.mark.asyncio
    async def test_store_uses_default(self):
        """Test that store uses default store."""
        self.redis_store.store.return_value = "envelope_id"
        
        envelope_id = await self.composite_store.store(self.test_envelope)
        
        self.redis_store.store.assert_called_once_with(self.test_envelope)
        assert envelope_id == "envelope_id"
    
    @pytest.mark.asyncio
    async def test_retrieve_tries_all_stores(self):
        """Test that retrieve tries all stores until found."""
        # First store raises not found, second succeeds
        self.redis_store.retrieve.side_effect = EnvelopeNotFoundError("Not found")
        self.evm_store.retrieve.return_value = self.test_envelope
        
        envelope = await self.composite_store.retrieve("test_id")
        
        self.redis_store.retrieve.assert_called_once_with("test_id")
        self.evm_store.retrieve.assert_called_once_with("test_id")
        assert envelope == self.test_envelope
    
    @pytest.mark.asyncio
    async def test_retrieve_not_found_in_any_store(self):
        """Test retrieve when envelope not found in any store."""
        self.redis_store.retrieve.side_effect = EnvelopeNotFoundError("Not found")
        self.evm_store.retrieve.side_effect = EnvelopeNotFoundError("Not found")
        
        with pytest.raises(EnvelopeNotFoundError, match="not found in any store"):
            await self.composite_store.retrieve("test_id")
    
    @pytest.mark.asyncio
    async def test_exists_checks_all_stores(self):
        """Test that exists checks all stores."""
        self.redis_store.exists.return_value = False
        self.evm_store.exists.return_value = True
        
        exists = await self.composite_store.exists("test_id")
        
        assert exists is True
        self.redis_store.exists.assert_called_once_with("test_id")
        self.evm_store.exists.assert_called_once_with("test_id")
    
    def test_get_store_by_name(self):
        """Test getting a specific store by name."""
        store = self.composite_store.get_store("evm")
        assert store == self.evm_store
    
    def test_get_default_store(self):
        """Test getting default store."""
        store = self.composite_store.get_store()
        assert store == self.redis_store
    
    def test_get_nonexistent_store(self):
        """Test getting nonexistent store."""
        with pytest.raises(ValueError, match="Store 'nonexistent' not found"):
            self.composite_store.get_store("nonexistent")
    
    def test_invalid_default_store(self):
        """Test creating composite store with invalid default."""
        with pytest.raises(ValueError, match="Default store 'invalid' not found"):
            CompositeEnvelopeStore(self.stores, "invalid")
    
    def test_get_backend_info(self):
        """Test getting backend information."""
        self.redis_store.get_backend_info.return_value = {"type": "redis"}
        self.evm_store.get_backend_info.return_value = {"type": "evm"}
        
        info = self.composite_store.get_backend_info()
        
        assert info["type"] == "composite"
        assert info["default_store"] == "redis"
        assert info["stores"]["redis"] == {"type": "redis"}
        assert info["stores"]["evm"] == {"type": "evm"}


if __name__ == "__main__":
    pytest.main([__file__])