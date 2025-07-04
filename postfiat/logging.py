"""Logging configuration for PostFiat SDK."""

import sys
from typing import Optional
import structlog
from loguru import logger as loguru_logger

# Configure loguru
loguru_logger.configure(
    handlers=[
        {
            "sink": sys.stderr,
            "level": "INFO",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        }
    ]
)

# Configure structlog to use loguru
# Global structlog configuration
_configured = False

def _configure_structlog():
    """Configure structlog once."""
    global _configured
    if _configured:
        return

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON renderer for production, console renderer for development
    if "pytest" in sys.modules:
        # Use plain renderer for tests
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Use JSON renderer for production
        processors.append(structlog.processors.JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    _configured = True


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    _configure_structlog()

    # Create and return logger
    logger = structlog.get_logger(name)
    return logger


# Create a FastAPI middleware for request logging
async def logging_middleware(request, call_next):
    """Middleware to log all requests and responses."""
    logger = get_logger("api")
    
    # Extract request info
    request_id = request.headers.get("X-Request-ID", "unknown")
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(
        "Request started",
        request_id=request_id,
        method=method,
        url=url,
        client_host=client_host,
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response
        logger.info(
            "Request completed",
            request_id=request_id,
            status_code=response.status_code,
            method=method,
            url=url,
        )
        
        return response
    except Exception as e:
        # Log exception
        logger.exception(
            "Request failed",
            request_id=request_id,
            method=method,
            url=url,
            error=str(e),
        )
        raise


# Exception handler for FastAPI
async def log_exception_handler(request, exc):
    """Log exceptions raised during request processing."""
    logger = get_logger("api.error")
    
    # Extract request info
    request_id = request.headers.get("X-Request-ID", "unknown")
    method = request.method
    url = str(request.url)
    
    # Log exception
    logger.exception(
        "Unhandled exception",
        request_id=request_id,
        method=method,
        url=url,
        error=str(exc),
        error_type=type(exc).__name__,
    )
    
    # Let FastAPI handle the exception
    raise exc