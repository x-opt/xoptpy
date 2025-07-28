---
sidebar_position: 3
---

# Models Reference

Data models and types used by the xopt Python client library.

## Core Models

### ComponentType

Enumeration for component types.

```python
from enum import Enum

class ComponentType(str, Enum):
    MODULE = "module"
    TOOL = "tool"
```

### SearchResult

Represents a search result from the registry.

```python
from pydantic import BaseModel
from typing import List, Optional

class SearchResult(BaseModel):
    """Search result for a component in the registry."""
    
    namespace: str
    name: str
    version: str
    type: ComponentType
    description: str
    author: Optional[str] = None
    tags: List[str] = []
    created_at: str
    updated_at: str
    download_count: int = 0
    rating: Optional[float] = None
```

**Example:**
```python
result = SearchResult(
    namespace="nlp",
    name="sentiment-analyzer",
    version="1.0.0",
    type=ComponentType.MODULE,
    description="Sentiment analysis module",
    author="team@company.com",
    tags=["nlp", "sentiment"],
    created_at="2024-01-15T10:30:00Z",
    updated_at="2024-01-15T10:30:00Z",
    download_count=1250,
    rating=4.8
)
```

### VersionInfo

Information about a specific version of a component.

```python
class VersionInfo(BaseModel):
    """Version information for a component."""
    
    version: str
    created_at: str
    description: Optional[str] = None
    author: Optional[str] = None
    size: Optional[int] = None  # Size in bytes
    checksum: Optional[str] = None
```

**Example:**
```python
version = VersionInfo(
    version="1.2.0",
    created_at="2024-02-01T14:20:00Z",
    description="Added support for multilingual text",
    author="dev@company.com",
    size=2048576,
    checksum="sha256:abc123..."
)
```

### ModuleVersionResponse

Response containing all versions of a module.

```python
class ModuleVersionResponse(BaseModel):
    """Response containing module versions."""
    
    namespace: str
    name: str
    versions: List[VersionInfo]
    total_count: int
```

**Example:**
```python
response = ModuleVersionResponse(
    namespace="nlp",
    name="tokenizer",
    versions=[
        VersionInfo(version="1.0.0", created_at="2024-01-01T00:00:00Z"),
        VersionInfo(version="1.1.0", created_at="2024-01-15T12:00:00Z"),
        VersionInfo(version="1.2.0", created_at="2024-02-01T14:20:00Z")
    ],
    total_count=3
)
```

### ToolVersionResponse

Response containing all versions of a tool.

```python
class ToolVersionResponse(BaseModel):
    """Response containing tool versions."""
    
    namespace: str
    name: str
    versions: List[VersionInfo]
    total_count: int
```

## Manifest Models

### Metadata

Component metadata information.

```python
class Metadata(BaseModel):
    """Component metadata."""
    
    name: str
    namespace: str
    version: str
    description: str
    author: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

### Interface

Component interface specification.

```python
class Interface(BaseModel):
    """Component interface specification."""
    
    input_schema: dict
    output_schema: dict
    examples: Optional[List[dict]] = []
```

### Implementation

Component implementation details.

```python
class Implementation(BaseModel):
    """Component implementation details."""
    
    type: str  # "function", "class", "react_agent", etc.
    entry_point: str
    requirements: List[str] = []
    reasoning_engine: Optional[str] = None
    tools: Optional[List[str]] = []
```

### Manifest

Complete component manifest.

```python
class Manifest(BaseModel):
    """Complete component manifest."""
    
    apiVersion: str
    kind: str  # "module" or "tool"
    metadata: Metadata
    spec: dict  # Contains interface, implementation, dependencies, etc.
```

**Example:**
```python
manifest = Manifest(
    apiVersion="ai-registry/v1",
    kind="module",
    metadata=Metadata(
        name="sentiment-analyzer",
        namespace="nlp",
        version="1.0.0",
        description="Sentiment analysis module",
        author="team@company.com",
        license="MIT",
        tags=["nlp", "sentiment"]
    ),
    spec={
        "interface": {
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            },
            "output_schema": {
                "type": "object", 
                "properties": {
                    "sentiment": {"type": "string"},
                    "confidence": {"type": "number"}
                },
                "required": ["sentiment", "confidence"]
            }
        },
        "implementation": {
            "type": "function",
            "entry_point": "./sentiment.py:analyze",
            "requirements": ["transformers>=4.21.0"]
        }
    }
)
```

## Dependency Models

### Dependency

Represents a dependency on another component.

```python
class Dependency(BaseModel):
    """Component dependency."""
    
    namespace: str
    name: str
    version: str
    type: ComponentType
    required: bool = True
```

**Example:**
```python
dep = Dependency(
    namespace="utils",
    name="text-cleaner",
    version="1.0.0",
    type=ComponentType.MODULE,
    required=True
)
```

## Statistics Models

### UsageActivityEntry

Individual usage activity record.

```python
class UsageActivityEntry(BaseModel):
    """Usage activity entry."""
    
    date: str  # ISO date format
    downloads: int
    unique_users: int
```

### UsageStats

Complete usage statistics for a component.

```python
class UsageStats(BaseModel):
    """Component usage statistics."""
    
    namespace: str
    name: str
    type: ComponentType
    total_downloads: int
    downloads_this_month: int
    downloads_this_week: int
    unique_users: int
    rating: Optional[float] = None
    rating_count: int = 0
    activity: List[UsageActivityEntry] = []
```

**Example:**
```python
stats = UsageStats(
    namespace="nlp",
    name="sentiment-analyzer",
    type=ComponentType.MODULE,
    total_downloads=5420,
    downloads_this_month=324,
    downloads_this_week=89,
    unique_users=1230,
    rating=4.7,
    rating_count=45,
    activity=[
        UsageActivityEntry(
            date="2024-01-15",
            downloads=23,
            unique_users=18
        ),
        UsageActivityEntry(
            date="2024-01-16", 
            downloads=31,
            unique_users=25
        )
    ]
)
```

## Error Models

### Error

Standard error response format.

```python
class Error(BaseModel):
    """Standard error response."""
    
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: Optional[str] = None
```

**Example:**
```python
error = Error(
    error="not_found",
    message="Module nlp/nonexistent version 1.0.0 not found",
    details={
        "namespace": "nlp",
        "name": "nonexistent",
        "version": "1.0.0"
    },
    timestamp="2024-01-15T10:30:00Z"
)
```

## Type Annotations

The client library uses type hints throughout. Import types for better IDE support:

```python
from typing import List, Optional, Dict, Any
from xoptpy.models import (
    SearchResult,
    ModuleVersionResponse,
    ToolVersionResponse,
    Manifest,
    Dependency,
    UsageStats,
    ComponentType,
    Error
)

# Function with proper type hints
def process_search_results(results: List[SearchResult]) -> Dict[str, Any]:
    modules = [r for r in results if r.type == ComponentType.MODULE]
    tools = [r for r in results if r.type == ComponentType.TOOL]
    
    return {
        "modules": len(modules),
        "tools": len(tools),
        "total": len(results)
    }
```

## Validation

All models use Pydantic for validation. Invalid data will raise `ValidationError`:

```python
from pydantic import ValidationError
from xoptpy.models import SearchResult

try:
    result = SearchResult(
        namespace="",  # Invalid: empty namespace
        name="test",
        version="1.0.0",
        type="invalid_type",  # Invalid: not a valid ComponentType
        description="Test"
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Serialization

Models can be serialized to/from JSON:

```python
# To JSON
result_json = result.model_dump_json()

# From JSON
result_data = SearchResult.model_validate_json(result_json)

# To dictionary
result_dict = result.model_dump()

# From dictionary  
result_data = SearchResult.model_validate(result_dict)
```

## Custom Models

You can extend the base models for custom applications:

```python
from xoptpy.models import SearchResult

class ExtendedSearchResult(SearchResult):
    """Extended search result with additional fields."""
    
    custom_field: Optional[str] = None
    metadata: Dict[str, Any] = {}
```