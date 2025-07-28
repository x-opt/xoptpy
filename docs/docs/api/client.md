---
sidebar_position: 2
---

# Client Reference

Complete reference for the `XoptRegistryClient` class.

## XoptRegistryClient

The main client class for interacting with the xopt registry API.

### Constructor

```python
XoptRegistryClient(
    base_url: str = None,
    timeout: int = None,
    headers: dict = None
)
```

**Parameters:**
- `base_url` (str, optional): API base URL. Defaults to environment variable or config file.
- `timeout` (int, optional): Request timeout in seconds. Defaults to 30.
- `headers` (dict, optional): Additional HTTP headers to send with requests.

### Search Methods

#### search_components

Search for modules and tools in the registry.

```python
def search_components(
    self,
    query: str,
    component_type: ComponentType = None,
    limit: int = 50
) -> list[SearchResult]
```

**Parameters:**
- `query` (str): Search query string
- `component_type` (ComponentType, optional): Filter by "module" or "tool"
- `limit` (int): Maximum number of results (default: 50)

**Returns:** List of `SearchResult` objects

**Example:**
```python
# Search all components
results = client.search_components("sentiment analysis")

# Search only modules
from xoptpy.models import ComponentType
results = client.search_components("nlp", ComponentType.MODULE)
```

### Module Methods

#### upload_module

Upload a module to the registry.

```python
def upload_module(
    self,
    manifest: str,
    namespace: str = None,
    name: str = None,
    version: str = None
) -> dict
```

**Parameters:**
- `manifest` (str): YAML manifest content
- `namespace` (str, optional): Override namespace from manifest
- `name` (str, optional): Override name from manifest  
- `version` (str, optional): Override version from manifest

**Returns:** Upload confirmation dictionary

**Example:**
```python
with open("module.yaml", "r") as f:
    manifest = f.read()

result = client.upload_module(
    manifest,
    namespace="my-org",
    version="2.0.0"
)
```

#### list_module_versions

List all versions of a module.

```python
def list_module_versions(
    self,
    namespace: str,
    name: str
) -> ModuleVersionResponse
```

**Parameters:**
- `namespace` (str): Module namespace
- `name` (str): Module name

**Returns:** `ModuleVersionResponse` object with version list

**Example:**
```python
versions = client.list_module_versions("nlp", "sentiment-analyzer")
for version in versions.versions:
    print(f"Version: {version.version}, Created: {version.created_at}")
```

#### get_module_manifest

Retrieve a module's manifest.

```python
def get_module_manifest(
    self,
    namespace: str,
    name: str,
    version: str
) -> Manifest
```

**Parameters:**
- `namespace` (str): Module namespace
- `name` (str): Module name
- `version` (str): Module version

**Returns:** `Manifest` object

**Example:**
```python
manifest = client.get_module_manifest("nlp", "tokenizer", "1.0.0")
print(f"Description: {manifest.metadata.description}")
print(f"Author: {manifest.metadata.author}")
```

#### get_module_dependencies

Get module dependencies.

```python
def get_module_dependencies(
    self,
    namespace: str,
    name: str,
    version: str
) -> list[Dependency]
```

**Parameters:**
- `namespace` (str): Module namespace
- `name` (str): Module name
- `version` (str): Module version

**Returns:** List of `Dependency` objects

**Example:**
```python
deps = client.get_module_dependencies("nlp", "sentiment-analyzer", "1.0.0")
for dep in deps:
    print(f"Depends on: {dep.namespace}/{dep.name}@{dep.version}")
```

#### get_module_stats

Get module usage statistics.

```python
def get_module_stats(
    self,
    namespace: str,
    name: str
) -> UsageStats
```

**Parameters:**
- `namespace` (str): Module namespace
- `name` (str): Module name

**Returns:** `UsageStats` object

**Example:**
```python
stats = client.get_module_stats("nlp", "sentiment-analyzer")
print(f"Total downloads: {stats.total_downloads}")
print(f"This month: {stats.downloads_this_month}")
```

### Tool Methods

Tool methods follow the same pattern as module methods:

#### upload_tool

```python
def upload_tool(
    self,
    manifest: str,
    namespace: str = None,
    name: str = None,
    version: str = None
) -> dict
```

#### list_tool_versions

```python
def list_tool_versions(
    self,
    namespace: str,
    name: str
) -> ToolVersionResponse
```

#### get_tool_manifest

```python
def get_tool_manifest(
    self,
    namespace: str,
    name: str,
    version: str
) -> Manifest
```

#### get_tool_dependencies

```python
def get_tool_dependencies(
    self,
    namespace: str,
    name: str,
    version: str
) -> list[Dependency]
```

#### get_tool_stats

```python
def get_tool_stats(
    self,
    namespace: str,
    name: str
) -> UsageStats
```

### Health Check

#### health

Check API server health.

```python
def health(self) -> dict
```

**Returns:** Health status dictionary

**Example:**
```python
health = client.health()
print(f"Status: {health['status']}")
print(f"Version: {health['version']}")
```

## Context Manager Support

The client supports context manager protocol for automatic resource cleanup:

```python
with XoptRegistryClient() as client:
    results = client.search_components("nlp")
    # Client automatically cleaned up
```

## Async Client

For async applications, use `AsyncXoptRegistryClient`:

```python
import asyncio
from xoptpy import AsyncXoptRegistryClient

async def main():
    async with AsyncXoptRegistryClient() as client:
        results = await client.search_components("sentiment")
        print(results)

asyncio.run(main())
```

The async client has the same methods as the sync client, but all methods are coroutines that must be awaited.