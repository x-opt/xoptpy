---
sidebar_position: 4
---

# Exceptions Reference

Exception classes and error handling in the xopt Python client library.

## Exception Hierarchy

```
XoptRegistryClientError (base)
├── APIError
│   ├── AuthenticationError (401)
│   ├── AuthorizationError (403)
│   ├── NotFoundError (404)
│   ├── ConflictError (409)
│   └── ServerError (5xx)
├── ConnectionError
├── TimeoutError
└── ValidationError
```

## Base Exception

### XoptRegistryClientError

Base exception class for all xopt client errors.

```python
class XoptRegistryClientError(Exception):
    """Base exception for xopt registry client errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
```

**Usage:**
```python
from xoptpy.exceptions import XoptRegistryClientError

try:
    # xopt operations
    client.search_components("query")
except XoptRegistryClientError as e:
    print(f"xopt error: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

## API Exceptions

### APIError

General API error for HTTP-related issues.

```python
class APIError(XoptRegistryClientError):
    """General API error."""
    
    def __init__(self, message: str, status_code: int, details: dict = None):
        self.status_code = status_code
        super().__init__(message, details)
```

**Usage:**
```python
from xoptpy.exceptions import APIError

try:
    result = client.upload_module(manifest)
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### AuthenticationError

Authentication failed (HTTP 401).

```python
class AuthenticationError(APIError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, 401, details)
```

**Example:**
```python
from xoptpy.exceptions import AuthenticationError

try:
    client.upload_module(manifest)
except AuthenticationError:
    print("Please check your API credentials")
    # Prompt for new credentials or refresh token
```

### AuthorizationError

Authorization failed - authenticated but not permitted (HTTP 403).

```python
class AuthorizationError(APIError):
    """Authorization failed."""
    
    def __init__(self, message: str = "Authorization failed", details: dict = None):
        super().__init__(message, 403, details)
```

**Example:**
```python
from xoptpy.exceptions import AuthorizationError

try:
    client.upload_module(manifest, namespace="restricted")
except AuthorizationError:
    print("You don't have permission to upload to this namespace")
```

### NotFoundError

Resource not found (HTTP 404).

```python
class NotFoundError(APIError):
    """Resource not found."""
    
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, 404, details)
```

**Example:**
```python
from xoptpy.exceptions import NotFoundError

try:
    manifest = client.get_module_manifest("nonexistent", "module", "1.0.0")
except NotFoundError as e:
    print(f"Module not found: {e.message}")
    # Suggest similar modules or check spelling
```

### ConflictError

Resource conflict, usually during creation (HTTP 409).

```python
class ConflictError(APIError):
    """Resource conflict."""
    
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(message, 409, details)
```

**Example:**
```python
from xoptpy.exceptions import ConflictError

try:
    client.upload_module(manifest)
except ConflictError:
    print("A module with this name and version already exists")
    # Suggest incrementing version or using different name
```

### ServerError

Server-side error (HTTP 5xx).

```python
class ServerError(APIError):
    """Server-side error."""
    
    def __init__(self, message: str = "Server error", status_code: int = 500, details: dict = None):
        super().__init__(message, status_code, details)
```

**Example:**
```python
from xoptpy.exceptions import ServerError

try:
    results = client.search_components("query")
except ServerError as e:
    print(f"Server error {e.status_code}: {e.message}")
    # Implement retry logic or fallback
```

## Network Exceptions

### ConnectionError

Network connection issues.

```python
class ConnectionError(XoptRegistryClientError):
    """Connection error."""
    
    def __init__(self, message: str = "Connection failed", details: dict = None):
        super().__init__(message, details)
```

**Example:**
```python
from xoptpy.exceptions import ConnectionError

try:
    health = client.health()
except ConnectionError:
    print("Unable to connect to xopt registry")
    print("Please check your network connection and registry URL")
```

### TimeoutError

Request timeout.

```python
class TimeoutError(XoptRegistryClientError):
    """Request timeout."""
    
    def __init__(self, message: str = "Request timed out", timeout: int = None, details: dict = None):
        self.timeout = timeout
        super().__init__(message, details)
```

**Example:**
```python
from xoptpy.exceptions import TimeoutError

try:
    result = client.upload_module(large_manifest)
except TimeoutError as e:
    print(f"Upload timed out after {e.timeout} seconds")
    # Suggest splitting large uploads or increasing timeout
```

## Validation Exceptions

### ValidationError

Input validation failed.

```python
class ValidationError(XoptRegistryClientError):
    """Input validation error."""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        self.field = field
        super().__init__(message, details)
```

**Example:**
```python
from xoptpy.exceptions import ValidationError

try:
    client.get_module_manifest("", "module", "1.0.0")  # Empty namespace
except ValidationError as e:
    print(f"Validation error in field '{e.field}': {e.message}")
```

## Error Handling Patterns

### Basic Error Handling

```python
from xoptpy import XoptRegistryClient
from xoptpy.exceptions import XoptRegistryClientError

client = XoptRegistryClient()

try:
    results = client.search_components("sentiment")
    print(f"Found {len(results)} components")
except XoptRegistryClientError as e:
    print(f"Error: {e.message}")
```

### Specific Exception Handling

```python
from xoptpy.exceptions import (
    NotFoundError,
    AuthenticationError, 
    ConnectionError,
    TimeoutError
)

try:
    manifest = client.get_module_manifest("nlp", "tokenizer", "1.0.0")
except NotFoundError:
    print("Module not found. Check the namespace, name, and version.")
except AuthenticationError:
    print("Authentication failed. Please check your credentials.")
except ConnectionError:
    print("Unable to connect to the registry. Check your network connection.")
except TimeoutError:
    print("Request timed out. The server may be overloaded.")
```

### Retry Logic

```python
import time
from xoptpy.exceptions import ServerError, TimeoutError

def upload_with_retry(client, manifest, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.upload_module(manifest)
        except (ServerError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e.message}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Graceful Degradation

```python
from xoptpy.exceptions import NotFoundError, ConnectionError

def get_module_info(client, namespace, name, version):
    try:
        # Try to get full manifest
        manifest = client.get_module_manifest(namespace, name, version)
        return {
            "available": True,
            "description": manifest.metadata.description,
            "author": manifest.metadata.author,
            "full_info": True
        }
    except NotFoundError:
        return {
            "available": False,
            "description": "Module not found",
            "full_info": False
        }
    except ConnectionError:
        # Fallback to cached or minimal info
        return {
            "available": "unknown",
            "description": "Unable to check - using cached info",
            "full_info": False
        }
```

### Logging Errors

```python
import logging
from xoptpy.exceptions import XoptRegistryClientError

logger = logging.getLogger(__name__)

def safe_search(client, query):
    try:
        return client.search_components(query)
    except XoptRegistryClientError as e:
        logger.error(
            "Search failed",
            extra={
                "query": query,
                "error": e.message,
                "details": e.details
            }
        )
        return []
```

## Custom Exception Handling

You can create custom exception handlers:

```python
from xoptpy.exceptions import XoptRegistryClientError

class XoptErrorHandler:
    def __init__(self, client):
        self.client = client
        self.error_counts = {}
    
    def handle_error(self, error: XoptRegistryClientError, operation: str):
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Custom handling logic
        if error_type == "AuthenticationError":
            self._refresh_credentials()
        elif error_type == "RateLimitError":
            self._wait_for_rate_limit()
        
        # Log error
        self._log_error(error, operation)
    
    def _refresh_credentials(self):
        # Implement credential refresh
        pass
    
    def _wait_for_rate_limit(self):
        # Implement rate limit waiting
        pass
    
    def _log_error(self, error, operation):
        print(f"Operation '{operation}' failed: {error.message}")
```

## Error Details

Many exceptions include additional details in the `details` attribute:

```python
try:
    client.upload_module(invalid_manifest)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    if e.details:
        for field, issue in e.details.items():
            print(f"  {field}: {issue}")
```

Common detail fields:
- `field`: The specific field that failed validation
- `expected`: Expected value or format
- `received`: Actual value received
- `suggestion`: Suggested fix
- `documentation_url`: Link to relevant documentation