"""
xopt Registry API Client

A client for interacting with the xopt registry API endpoints.
"""

import json
import logging
from typing import List, Optional, Union
from urllib.parse import quote

import requests
from pydantic import ValidationError as PydanticValidationError

from .models import (
    ComponentType,
    Dependency,
    Error,
    HealthResponse,
    Manifest,
    ModuleVersionResponse,
    SearchResult,
    ToolVersionResponse,
    UsageStats,
    VersionInfo,
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
from .config import ClientConfig, load_config, setup_logging


class XoptRegistryClient:
    """Client for the xopt registry API."""
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        timeout: Optional[int] = None, 
        config: Optional[ClientConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the xopt registry client.
        
        Args:
            base_url: Base URL of the xopt registry API (overrides config)
            timeout: Request timeout in seconds (overrides config)
            config: ClientConfig instance (if not provided, loads from environment/file)
            logger: Optional logger instance
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.base_url = (base_url or config.base_url).rstrip("/")
        self.timeout = timeout or config.timeout
        
        # Set up logging
        if logger is None:
            self.logger = setup_logging(config.log_level)
        else:
            self.logger = logger
            
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        self.logger.info(f"Initialized xopt registry client for {self.base_url}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        self.logger.debug(f"Making {method} request to {url}")
        if data:
            self.logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        if params:
            self.logger.debug(f"Request params: {params}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout for {url}: {e}")
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error for {url}: {e}")
            raise ConnectionError(f"Failed to connect to {url}: {e}")
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            raise XoptRegistryClientError(f"Request failed: {e}")
        
        self.logger.debug(f"Response status: {response.status_code}")
        
        if not response.ok:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Unknown error")
            except (json.JSONDecodeError, KeyError):
                error_msg = response.text or f"HTTP {response.status_code}"
                error_data = {}
            
            self.logger.error(f"API error {response.status_code}: {error_msg}")
            
            # Raise specific exception types based on status code
            if response.status_code == 401:
                raise AuthenticationError(response.status_code, error_msg, error_data)
            elif response.status_code == 403:
                raise AuthorizationError(response.status_code, error_msg, error_data)
            elif response.status_code == 404:
                raise NotFoundError(response.status_code, error_msg, error_data)
            elif response.status_code == 409:
                raise ConflictError(response.status_code, error_msg, error_data)
            elif response.status_code >= 500:
                raise ServerError(response.status_code, error_msg, error_data)
            else:
                raise APIError(response.status_code, error_msg, error_data)
        
        return response
    
    def _parse_response(self, response: requests.Response, model_class):
        """Parse response JSON into a Pydantic model."""
        try:
            data = response.json()
            self.logger.debug(f"Parsing response data for {model_class.__name__}: {data}")
            
            if isinstance(data, list):
                # Filter out None items
                valid_items = [item for item in data if item is not None]
                return [model_class(**item) for item in valid_items]
            else:
                if data is None:
                    self.logger.warning(f"Received null response for {model_class.__name__}")
                    return None
                return model_class(**data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise ValidationError(f"Invalid JSON response: {e}")
        except PydanticValidationError as e:
            self.logger.error(f"Failed to validate response data: {e}")
            self.logger.debug(f"Raw response data: {data}")
            raise ValidationError(f"Response validation failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing response: {e}")
            self.logger.debug(f"Raw response data: {data}")
            raise XoptRegistryClientError(f"Failed to parse response: {e}")
    
    # Health endpoints
    
    def health_check(self) -> HealthResponse:
        """Check the health status of the API and database connection."""
        response = self._make_request("GET", "/health")
        return self._parse_response(response, HealthResponse)
    
    # Module endpoints
    
    def get_module_versions(self, namespace: str, name: str) -> List[VersionInfo]:
        """Get all versions of a specific module."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/versions"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, VersionInfo)
    
    def upload_module_version(
        self, 
        namespace: str, 
        name: str, 
        version: str, 
        manifest: Manifest
    ) -> ModuleVersionResponse:
        """Upload a new version of a module with its manifest."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/versions/{quote(version)}"
        data = manifest.model_dump()
        response = self._make_request("POST", endpoint, data=data)
        return self._parse_response(response, ModuleVersionResponse)
    
    def get_module_manifest(self, namespace: str, name: str, version: str) -> Manifest:
        """Get the manifest for a specific module version."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/manifest"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, Manifest)
    
    def get_module_file(self, namespace: str, name: str, version: str, file_path: str) -> bytes:
        """Download a specific file from a module version."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/files/{quote(file_path)}"
        response = self._make_request("GET", endpoint)
        return response.content
    
    def get_module_dependencies(
        self, 
        namespace: str, 
        name: str, 
        version: str
    ) -> List[Dependency]:
        """Get dependencies for a specific module version."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/dependencies"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, Dependency)
    
    def get_module_usage_stats(self, namespace: str, name: str) -> UsageStats:
        """Get usage statistics for a module."""
        endpoint = f"/api/v1/modules/{quote(namespace)}/{quote(name)}/usage-stats"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, UsageStats)
    
    # Tool endpoints
    
    def get_tool_versions(self, namespace: str, name: str) -> List[VersionInfo]:
        """Get all versions of a specific tool."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/versions"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, VersionInfo)
    
    def upload_tool_version(
        self, 
        namespace: str, 
        name: str, 
        version: str, 
        manifest: Manifest
    ) -> ToolVersionResponse:
        """Upload a new version of a tool with its manifest."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/versions/{quote(version)}"
        data = manifest.model_dump()
        response = self._make_request("POST", endpoint, data=data)
        return self._parse_response(response, ToolVersionResponse)
    
    def get_tool_manifest(self, namespace: str, name: str, version: str) -> Manifest:
        """Get the manifest for a specific tool version."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/manifest"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, Manifest)
    
    def get_tool_file(self, namespace: str, name: str, version: str, file_path: str) -> bytes:
        """Download a specific file from a tool version."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/files/{quote(file_path)}"
        response = self._make_request("GET", endpoint)
        return response.content
    
    def get_tool_dependencies(
        self, 
        namespace: str, 
        name: str, 
        version: str
    ) -> List[Dependency]:
        """Get dependencies for a specific tool version."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/versions/{quote(version)}/dependencies"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, Dependency)
    
    def get_tool_usage_stats(self, namespace: str, name: str) -> UsageStats:
        """Get usage statistics for a tool."""
        endpoint = f"/api/v1/tools/{quote(namespace)}/{quote(name)}/usage-stats"
        response = self._make_request("GET", endpoint)
        return self._parse_response(response, UsageStats)
    
    # Search endpoints
    
    def search(
        self, 
        query: str, 
        component_type: Optional[ComponentType] = None
    ) -> List[SearchResult]:
        """Search for modules and tools by name or description."""
        params = {"q": query}
        if component_type:
            params["type"] = component_type.value
        
        response = self._make_request("GET", "/api/v1/search", params=params)
        return self._parse_response(response, SearchResult)
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()