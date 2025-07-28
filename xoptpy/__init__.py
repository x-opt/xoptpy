"""
XOptPy - AI Registry Client Library

A Python client library for interacting with the AI Registry API.
"""

__version__ = "0.1.0"

from .client import AIRegistryClient
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
    AIRegistryClientError,
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
    "AIRegistryClient",
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
    "AIRegistryClientError",
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