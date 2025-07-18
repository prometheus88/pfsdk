"""Base client functionality for PostFiat SDK."""

import asyncio
from typing import Optional, Dict, Any, Union
from pydantic import BaseSettings, Field, validator
import grpc
import httpx

from ..exceptions import NetworkError, AuthenticationError, ConfigurationError
from ..logging import get_logger


class ClientConfig(BaseSettings):
    """Configuration for PostFiat clients."""
    
    # Server connection
    grpc_endpoint: Optional[str] = Field(None, description="gRPC server endpoint")
    http_endpoint: Optional[str] = Field(None, description="HTTP server endpoint")
    
    # Authentication
    api_key: Optional[str] = Field(None, description="API key for authentication")
    session_token: Optional[str] = Field(None, description="Session token for authentication")
    
    # Connection settings
    timeout: float = Field(30.0, description="Request timeout in seconds", gt=0)
    max_retries: int = Field(3, description="Maximum number of retries", ge=0)
    
    # TLS settings
    use_tls: bool = Field(True, description="Use TLS for connections")
    ca_cert_path: Optional[str] = Field(None, description="Path to CA certificate file")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    
    class Config:
        env_prefix = "POSTFIAT_"
        case_sensitive = False
        
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator('ca_cert_path')
    def validate_ca_cert_path(cls, v):
        """Validate CA certificate path exists if provided."""
        if v:
            import os
            if not os.path.exists(v):
                raise ValueError(f"CA certificate file not found: {v}")
        return v
    
    def __init__(self, **data):
        """Initialize and validate configuration."""
        super().__init__(**data)
        if not self.grpc_endpoint and not self.http_endpoint:
            raise ConfigurationError("Either grpc_endpoint or http_endpoint must be provided")


class BaseClient:
    """Base client with common functionality for all service clients."""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = get_logger(f"client.{self.__class__.__name__}")
        
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
            
            self.logger.info(
                "Creating gRPC channel",
                endpoint=self.config.grpc_endpoint,
                use_tls=self.config.use_tls,
                has_ca_cert=bool(self.config.ca_cert_path)
            )
            
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
            
            self.logger.info(
                "Creating HTTP client",
                endpoint=self.config.http_endpoint,
                timeout=self.config.timeout,
                has_auth=bool(self.config.api_key or self.config.session_token)
            )
            
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
        self.logger.info("Closing client connections")
        
        if self._grpc_channel:
            await self._grpc_channel.close()
            self._grpc_channel = None
            self.logger.debug("Closed gRPC channel")
        
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            self.logger.debug("Closed HTTP client")
    
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
        
        self.logger.error(
            "gRPC error occurred",
            status_code=status_code.name,
            details=details,
            endpoint=self.config.grpc_endpoint,
            exc_info=True
        )
        
        if status_code == grpc.StatusCode.UNAUTHENTICATED:
            raise AuthenticationError(f"Authentication failed: {details}")
        elif status_code == grpc.StatusCode.UNAVAILABLE:
            raise NetworkError(f"Service unavailable: {details}")
        else:
            raise NetworkError(f"gRPC error ({status_code.name}): {details}")
    
    async def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle and convert HTTP errors to SDK exceptions."""
        self.logger.error(
            "HTTP error occurred",
            status_code=response.status_code,
            response_text=response.text,
            endpoint=self.config.http_endpoint,
            url=str(response.url)
        )
        
        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {response.text}")
        elif response.status_code >= 500:
            raise NetworkError(f"Server error ({response.status_code}): {response.text}")
        else:
            raise NetworkError(f"HTTP error ({response.status_code}): {response.text}")
