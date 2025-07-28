---
sidebar_position: 1
---

# API Overview

The xopt Python client library provides a programmatic interface to interact with the xopt registry API.

## Installation

```bash
pip install xoptpy
```

## Quick Start

```python
from xoptpy import XoptRegistryClient

# Initialize the client
client = XoptRegistryClient(base_url="http://localhost:8080")

# Search for components
results = client.search_components("sentiment")

# Upload a module
with open("module.yaml", "r") as f:
    manifest = f.read()
client.upload_module(manifest)
```

## Client Configuration

### Basic Configuration

```python
from xoptpy import XoptRegistryClient

client = XoptRegistryClient(
    base_url="http://localhost:8080",
    timeout=30
)
```

### Environment Variables

Set these environment variables:

```bash
export XOPTPY_BASE_URL="http://localhost:8080"
export XOPTPY_TIMEOUT=30
export XOPTPY_LOG_LEVEL="INFO"
```

### Configuration File

Create `xoptpy.json`:

```json
{
  "base_url": "http://localhost:8080",
  "timeout": 30,
  "log_level": "INFO"
}
```

## Error Handling

The client raises specific exceptions for different error conditions:

```python
from xoptpy import XoptRegistryClient
from xoptpy.exceptions import NotFoundError, ValidationError

client = XoptRegistryClient()

try:
    result = client.get_module_manifest("namespace", "module", "1.0.0")
except NotFoundError:
    print("Module not found")
except ValidationError as e:
    print(f"Invalid request: {e}")
```

## Available Exceptions

- `XoptRegistryClientError` - Base exception class
- `APIError` - General API errors
- `AuthenticationError` - Authentication failed
- `AuthorizationError` - Authorization failed
- `ConflictError` - Resource conflicts
- `ConnectionError` - Connection issues
- `NotFoundError` - Resource not found
- `ServerError` - Server-side errors
- `TimeoutError` - Request timeouts
- `ValidationError` - Input validation errors

## Response Models

The client uses Pydantic models for type safety:

```python
from xoptpy.models import SearchResult, ModuleVersionResponse

# Search results are typed
results: list[SearchResult] = client.search_components("nlp")

# Module information is typed
versions: ModuleVersionResponse = client.list_module_versions("nlp", "tokenizer")
```

## Async Support

For async applications, use the async client:

```python
import asyncio
from xoptpy import AsyncXoptRegistryClient

async def main():
    async with AsyncXoptRegistryClient() as client:
        results = await client.search_components("sentiment")
        print(results)

asyncio.run(main())
```

## Next Steps

- [Client Reference](./client) - Complete client API reference
- [Models Reference](./models) - Data models and types
- [Exceptions Reference](./exceptions) - Error handling details