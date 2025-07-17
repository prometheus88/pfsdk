"""
Ethereum EVM envelope storage implementation.

This module provides EVM-based envelope storage using smart contracts.
"""

import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime

from ..envelope_store import EnvelopeStore, EnvelopeNotFoundError, StorageError
from ...v3.messages_pb2 import Envelope


class EVMEnvelopeStore(EnvelopeStore):
    """EVM-based envelope storage using smart contracts."""
    
    def __init__(self, 
                 rpc_url: str = "http://localhost:8545",
                 contract_address: Optional[str] = None,
                 private_key: Optional[str] = None,
                 chain_id: int = 1):
        """Initialize EVM envelope store.
        
        Args:
            rpc_url: EVM JSON-RPC endpoint URL
            contract_address: Deployed envelope storage contract address
            private_key: Private key for sending transactions
            chain_id: EVM chain ID (1 for mainnet, 5 for goerli, etc.)
        """
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.private_key = private_key
        self.chain_id = chain_id
        self._web3 = None
        self._contract = None
    
    @property
    def web3(self):
        """Lazy-load Web3 instance."""
        if self._web3 is None:
            try:
                from web3 import Web3
                self._web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            except ImportError:
                raise ImportError(
                    "web3 is required for EVM storage. "
                    "Install with: pip install postfiat-sdk[blockchain]"
                )
        return self._web3
    
    @property
    def contract(self):
        """Lazy-load contract instance."""
        if self._contract is None:
            if not self.contract_address:
                raise ValueError("Contract address is required for EVM storage")
            
            # Simple envelope storage contract ABI
            abi = [
                {
                    "inputs": [
                        {"name": "envelopeHash", "type": "bytes32"},
                        {"name": "envelopeData", "type": "bytes"}
                    ],
                    "name": "storeEnvelope",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "envelopeHash", "type": "bytes32"}],
                    "name": "getEnvelope",
                    "outputs": [{"name": "", "type": "bytes"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "envelopeHash", "type": "bytes32"}],
                    "name": "envelopeExists",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"name": "envelopeHash", "type": "bytes32"},
                        {"name": "sender", "type": "address"}
                    ],
                    "name": "EnvelopeStored",
                    "type": "event"
                }
            ]
            
            self._contract = self.web3.eth.contract(
                address=self.contract_address,
                abi=abi
            )
        
        return self._contract
    
    def _generate_envelope_id(self, envelope: Envelope) -> str:
        """Generate envelope ID from envelope content."""
        envelope_bytes = envelope.SerializeToString()
        return hashlib.sha256(envelope_bytes).hexdigest()
    
    def _get_account(self):
        """Get account from private key."""
        if not self.private_key:
            raise ValueError("Private key is required for EVM transactions")
        
        account = self.web3.eth.account.from_key(self.private_key)
        return account
    
    async def store(self, envelope: Envelope) -> str:
        """Store envelope on EVM blockchain."""
        try:
            envelope_id = self._generate_envelope_id(envelope)
            
            # Add EVM-specific metadata
            envelope.metadata["storage_backend"] = "evm"
            envelope.metadata["chain_id"] = str(self.chain_id)
            envelope.metadata["envelope_id"] = envelope_id
            
            # Serialize envelope
            envelope_data = envelope.SerializeToString()
            envelope_hash = hashlib.sha256(envelope_data).digest()
            
            # Get account for transaction
            account = self._get_account()
            
            # Build transaction
            transaction = self.contract.functions.storeEnvelope(
                envelope_hash,
                envelope_data
            ).build_transaction({
                'from': account.address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(account.address),
                'chainId': self.chain_id
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Add transaction info to envelope metadata
            envelope.metadata["transaction_hash"] = receipt.transactionHash.hex()
            envelope.metadata["block_number"] = str(receipt.blockNumber)
            envelope.metadata["gas_used"] = str(receipt.gasUsed)
            
            return envelope_id
            
        except Exception as e:
            raise StorageError(f"Failed to store envelope on EVM: {e}")
    
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve envelope from EVM blockchain."""
        try:
            # Convert envelope ID to hash
            envelope_hash = bytes.fromhex(envelope_id)
            
            # Call contract to get envelope data
            envelope_data = self.contract.functions.getEnvelope(envelope_hash).call()
            
            if not envelope_data:
                raise EnvelopeNotFoundError(f"Envelope '{envelope_id}' not found on EVM")
            
            # Deserialize envelope
            envelope = Envelope()
            envelope.ParseFromString(envelope_data)
            
            return envelope
            
        except EnvelopeNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve envelope from EVM: {e}")
    
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find envelopes by content hash (requires indexing)."""
        # Note: This would require additional contract functionality or event indexing
        # For now, return empty list
        return []
    
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find envelopes by context reference (requires indexing)."""
        # Note: This would require additional contract functionality or event indexing
        # For now, return empty list
        return []
    
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List envelopes by sender (requires indexing)."""
        # Note: This would require additional contract functionality or event indexing
        # For now, return empty list
        return []
    
    async def delete(self, envelope_id: str) -> bool:
        """Delete envelope (not supported on immutable blockchain)."""
        raise NotImplementedError("Envelope deletion not supported on immutable EVM blockchain")
    
    async def exists(self, envelope_id: str) -> bool:
        """Check if envelope exists on EVM."""
        try:
            envelope_hash = bytes.fromhex(envelope_id)
            return self.contract.functions.envelopeExists(envelope_hash).call()
        except Exception as e:
            raise StorageError(f"Failed to check envelope existence on EVM: {e}")
    
    async def get_envelope_metadata(self, envelope_id: str) -> Dict[str, str]:
        """Get EVM-specific storage metadata."""
        try:
            # For EVM, we'd need to get transaction details
            # This is a simplified implementation
            envelope = await self.retrieve(envelope_id)
            
            return {
                "storage_backend": "evm",
                "chain_id": envelope.metadata.get("chain_id", ""),
                "transaction_hash": envelope.metadata.get("transaction_hash", ""),
                "block_number": envelope.metadata.get("block_number", ""),
                "gas_used": envelope.metadata.get("gas_used", "")
            }
            
        except Exception as e:
            raise StorageError(f"Failed to get EVM envelope metadata: {e}")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get EVM backend information."""
        return {
            "type": "evm",
            "rpc_url": self.rpc_url,
            "contract_address": self.contract_address,
            "chain_id": self.chain_id
        }