"""Base client functionality for PostFiat SDK."""

import asyncio
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import grpc
import httpx

from ..exceptions import NetworkError, AuthenticationError, ConfigurationError


@dataclass
class ClientConfig:
    """Configuration for PostFiat clients."""
    
    # Server connection
    grpc_endpoint: Optional[str] = None
    http_endpoint: Optional[str] = None
    
    # Authentication
    api_key: Optional[str] = None
    session_token: Optional[str] = None
    
    # Connection settings
    timeout: float = 30.0
    max_retries: int = 3
    
    # TLS settings
    use_tls: bool = True
    ca_cert_path: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.grpc_endpoint and not self.http_endpoint:
            raise ConfigurationError("Either grpc_endpoint or http_endpoint must be provided")


class BaseClient:
    """Base client with common functionality for all service clients."""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(getattr(logging, config.log_level.upper()))
        
        # gRPC channel (lazy initialization)
        self._grpc_channel: Optional[grpc.aio.Channel] = None
        
        # HTTP client (lazy initialization)
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    @property
    async def grpc_channel(self) -> grpc.aio.Channel:
        """Get or create gRPC channel."""
        if self._grpc_channel is None:
            if not self.config.grpc_endpoint:
                raise ConfigurationError("grpc_endpoint not configured")
            
            if self.config.use_tls:
                credentials = grpc.ssl_channel_credentials()
                if self.config.ca_cert_path:
                    with open(self.config.ca_cert_path, 'rb') as f:
                        ca_cert = f.read()
                    credentials = grpc.ssl_channel_credentials(root_certificates=ca_cert)
                
                self._grpc_channel = grpc.aio.secure_channel(
                    self.config.grpc_endpoint,
                    credentials
                )
            else:
                self._grpc_channel = grpc.aio.insecure_channel(self.config.grpc_endpoint)
        
        return self._grpc_channel
    
    @property
    async def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            if not self.config.http_endpoint:
                raise ConfigurationError("http_endpoint not configured")
            
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            elif self.config.session_token:
                headers["Authorization"] = f"Bearer {self.config.session_token}"
            
            self._http_client = httpx.AsyncClient(
                base_url=self.config.http_endpoint,
                headers=headers,
                timeout=self.config.timeout
            )
        
        return self._http_client
    
    async def close(self):
        """Close all connections."""
        if self._grpc_channel:
            await self._grpc_channel.close()
            self._grpc_channel = None
        
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def _get_metadata(self) -> list:
        """Get gRPC metadata for requests."""
        metadata = []
        
        if self.config.api_key:
            metadata.append(("authorization", f"Bearer {self.config.api_key}"))
        elif self.config.session_token:
            metadata.append(("authorization", f"Bearer {self.config.session_token}"))
        
        return metadata
    
    async def _handle_grpc_error(self, error: grpc.RpcError) -> None:
        """Handle and convert gRPC errors to SDK exceptions."""
        status_code = error.code()
        details = error.details()
        
        if status_code == grpc.StatusCode.UNAUTHENTICATED:
            raise AuthenticationError(f"Authentication failed: {details}")
        elif status_code == grpc.StatusCode.UNAVAILABLE:
            raise NetworkError(f"Service unavailable: {details}")
        else:
            raise NetworkError(f"gRPC error ({status_code.name}): {details}")
    
    async def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle and convert HTTP errors to SDK exceptions."""
        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {response.text}")
        elif response.status_code >= 500:
            raise NetworkError(f"Server error ({response.status_code}): {response.text}")
        else:
            raise NetworkError(f"HTTP error ({response.status_code}): {response.text}")
