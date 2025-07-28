"""
XOptPy - xopt Registry Client Library

A Python client library for interacting with the xopt registry API.
"""

__version__ = "0.1.0"

from .client import XoptRegistryClient
from .models import (
    ComponentType,
    Error,
    VersionInfo,
    ModuleVersionResponse,
    ToolVersionResponse,
    Dependency,
    UsageStats,
    UsageActivityEntry,
    SearchResult,
    Manifest,
)
from .exceptions import (
    XoptRegistryClientError,
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ConnectionError,
    NotFoundError,
    ServerError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "XoptRegistryClient",
    "ComponentType",
    "Error",
    "VersionInfo", 
    "ModuleVersionResponse",
    "ToolVersionResponse",
    "Dependency",
    "UsageStats",
    "UsageActivityEntry",
    "SearchResult",
    "Manifest",
    "XoptRegistryClientError",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "ConnectionError",
    "NotFoundError",
    "ServerError",
    "TimeoutError",
    "ValidationError",
]