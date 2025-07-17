"""
XRPL envelope storage implementation.

This module provides XRPL-based envelope storage using transaction memos.
"""

import json
import hashlib
import base64
from typing import List, Dict, Optional, Any
from datetime import datetime

from ..envelope_store import EnvelopeStore, EnvelopeNotFoundError, StorageError
from ...v3.messages_pb2 import Envelope


class XRPLEnvelopeStore(EnvelopeStore):
    """XRPL-based envelope storage using transaction memos."""
    
    def __init__(self, 
                 node_url: str = "https://s1.ripple.com:51234",
                 wallet_seed: Optional[str] = None,
                 destination: Optional[str] = None,
                 network: str = "mainnet"):
        """Initialize XRPL envelope store.
        
        Args:
            node_url: XRPL node URL
            wallet_seed: Wallet seed for sending transactions
            destination: Destination address for envelope transactions
            network: XRPL network (mainnet, testnet, devnet)
        """
        self.node_url = node_url
        self.wallet_seed = wallet_seed
        self.destination = destination
        self.network = network
        self._client = None
        self._wallet = None
    
    @property
    def client(self):
        """Lazy-load XRPL client."""
        if self._client is None:
            try:
                from xrpl.clients import JsonRpcClient
                self._client = JsonRpcClient(self.node_url)
            except ImportError:
                raise ImportError(
                    "xrpl-py is required for XRPL storage. "
                    "Install with: pip install postfiat-sdk[blockchain]"
                )
        return self._client
    
    @property
    def wallet(self):
        """Lazy-load wallet."""
        if self._wallet is None:
            if not self.wallet_seed:
                raise ValueError("Wallet seed is required for XRPL transactions")
            
            try:
                from xrpl.wallet import Wallet
                self._wallet = Wallet.from_seed(self.wallet_seed)
            except ImportError:
                raise ImportError(
                    "xrpl-py is required for XRPL storage. "
                    "Install with: pip install postfiat-sdk[blockchain]"
                )
        return self._wallet
    
    def _generate_envelope_id(self, envelope: Envelope) -> str:
        """Generate envelope ID from envelope content."""
        envelope_bytes = envelope.SerializeToString()
        return hashlib.sha256(envelope_bytes).hexdigest()
    
    def _envelope_to_memo(self, envelope: Envelope) -> Dict[str, str]:
        """Convert envelope to XRPL memo format."""
        envelope_data = envelope.SerializeToString()
        
        # XRPL memo fields are limited to 1KB each
        # For larger envelopes, we'd need to use multiple memos or external storage
        if len(envelope_data) > 1024:
            raise ValueError(f"Envelope too large for XRPL memo: {len(envelope_data)} bytes")
        
        memo_data = base64.b64encode(envelope_data).decode('ascii')
        
        return {
            "Memo": {
                "MemoType": base64.b64encode(b"postfiat/envelope").decode('ascii'),
                "MemoData": memo_data
            }
        }
    
    def _memo_to_envelope(self, memo: Dict[str, str]) -> Envelope:
        """Convert XRPL memo to envelope."""
        memo_data = memo.get("MemoData", "")
        if not memo_data:
            raise ValueError("No memo data found")
        
        envelope_data = base64.b64decode(memo_data)
        
        envelope = Envelope()
        envelope.ParseFromString(envelope_data)
        
        return envelope
    
    async def store(self, envelope: Envelope) -> str:
        """Store envelope on XRPL using transaction memo."""
        try:
            envelope_id = self._generate_envelope_id(envelope)
            
            # Add XRPL-specific metadata
            envelope.metadata["storage_backend"] = "xrpl"
            envelope.metadata["network"] = self.network
            envelope.metadata["envelope_id"] = envelope_id
            
            # Convert envelope to memo
            memo = self._envelope_to_memo(envelope)
            
            # Create payment transaction with memo
            from xrpl.models.transactions import Payment
            from xrpl.models.amounts import IssuedCurrencyAmount
            from xrpl.transaction import submit_and_wait
            
            if not self.destination:
                # If no destination specified, send to self
                self.destination = self.wallet.address
            
            payment = Payment(
                account=self.wallet.address,
                destination=self.destination,
                amount="1",  # Minimum XRP amount (1 drop)
                memos=[memo]
            )
            
            # Submit transaction
            response = submit_and_wait(payment, self.client, self.wallet)
            
            if response.result.get("engine_result") != "tesSUCCESS":
                raise StorageError(f"XRPL transaction failed: {response.result}")
            
            # Add transaction info to envelope metadata
            tx_hash = response.result["tx_json"]["hash"]
            envelope.metadata["transaction_hash"] = tx_hash
            envelope.metadata["ledger_index"] = str(response.result.get("ledger_index", ""))
            
            return envelope_id
            
        except Exception as e:
            raise StorageError(f"Failed to store envelope on XRPL: {e}")
    
    async def retrieve(self, envelope_id: str) -> Envelope:
        """Retrieve envelope from XRPL transaction."""
        try:
            # For XRPL, we need to find the transaction by envelope ID
            # This is a simplified implementation - in practice, you'd need
            # to maintain an index of envelope_id -> transaction_hash
            
            # This would require searching transaction history or maintaining an index
            raise NotImplementedError(
                "XRPL envelope retrieval by ID requires transaction indexing. "
                "Use retrieve_by_transaction_hash() instead."
            )
            
        except Exception as e:
            raise StorageError(f"Failed to retrieve envelope from XRPL: {e}")
    
    async def retrieve_by_transaction_hash(self, tx_hash: str) -> Envelope:
        """Retrieve envelope by XRPL transaction hash."""
        try:
            from xrpl.models.requests import Tx
            
            # Get transaction details
            tx_request = Tx(transaction=tx_hash)
            response = self.client.request(tx_request)
            
            if not response.is_successful():
                raise EnvelopeNotFoundError(f"Transaction '{tx_hash}' not found")
            
            tx_data = response.result
            memos = tx_data.get("Memos", [])
            
            # Find PostFiat envelope memo
            for memo in memos:
                memo_obj = memo.get("Memo", {})
                memo_type = memo_obj.get("MemoType", "")
                
                if memo_type:
                    decoded_type = base64.b64decode(memo_type).decode('ascii')
                    if decoded_type == "postfiat/envelope":
                        return self._memo_to_envelope(memo_obj)
            
            raise EnvelopeNotFoundError(f"No PostFiat envelope found in transaction '{tx_hash}'")
            
        except EnvelopeNotFoundError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to retrieve envelope from XRPL: {e}")
    
    async def find_by_content_hash(self, content_hash: bytes) -> List[Envelope]:
        """Find envelopes by content hash (requires indexing)."""
        # Note: This would require scanning transaction history or maintaining an index
        # For now, return empty list
        return []
    
    async def find_by_context(self, context_hash: bytes) -> List[Envelope]:
        """Find envelopes by context reference (requires indexing)."""
        # Note: This would require scanning transaction history or maintaining an index
        # For now, return empty list
        return []
    
    async def list_by_sender(self, sender: str, limit: int = 100) -> List[Envelope]:
        """List envelopes by sender (requires indexing)."""
        # Note: This would require scanning transaction history or maintaining an index
        # For now, return empty list
        return []
    
    async def delete(self, envelope_id: str) -> bool:
        """Delete envelope (not supported on immutable ledger)."""
        raise NotImplementedError("Envelope deletion not supported on immutable XRPL ledger")
    
    async def exists(self, envelope_id: str) -> bool:
        """Check if envelope exists (requires indexing)."""
        # Note: This would require maintaining an index of envelope_id -> transaction_hash
        # For now, return False
        return False
    
    async def get_envelope_metadata(self, envelope_id: str) -> Dict[str, str]:
        """Get XRPL-specific storage metadata."""
        try:
            # This would require retrieving the envelope first
            # Simplified implementation
            return {
                "storage_backend": "xrpl",
                "network": self.network,
                "node_url": self.node_url
            }
            
        except Exception as e:
            raise StorageError(f"Failed to get XRPL envelope metadata: {e}")
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get XRPL backend information."""
        return {
            "type": "xrpl",
            "node_url": self.node_url,
            "network": self.network,
            "wallet_address": self.wallet.address if self.wallet else None
        }