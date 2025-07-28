"""
Data models for the AI Registry API based on OpenAPI specification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    MODULE = "module"
    TOOL = "tool"


class ImplementationType(str, Enum):
    FUNCTION = "function"
    REACT_AGENT = "react_agent"


class Error(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")


class VersionInfo(BaseModel):
    """Version information for a component."""
    version: str = Field(..., example="1.0.0")
    download_count: int = Field(..., example=123)
    created_at: datetime = Field(..., example="2024-01-01T10:00:00Z")


class ModuleVersionResponse(BaseModel):
    """Response when creating a module version."""
    module_id: int = Field(..., example=1)
    version_id: int = Field(..., example=2)
    version: str = Field(..., example="1.0.0")


class ToolVersionResponse(BaseModel):
    """Response when creating a tool version."""
    tool_id: int = Field(..., example=1)
    version_id: int = Field(..., example=2)
    version: str = Field(..., example="1.0.0")


class Dependency(BaseModel):
    """Dependency specification."""
    dependency_namespace: str = Field(..., example="utils")
    dependency_name: str = Field(..., example="text-cleaner")
    dependency_version: str = Field(..., example="1.0.0")


class UsageActivityEntry(BaseModel):
    """Usage activity entry."""
    date: datetime = Field(..., example="2024-01-01T10:00:00Z")
    downloads: int = Field(..., example=25)
    version: str = Field(..., example="1.0.0")


class UsageStats(BaseModel):
    """Usage statistics for a component."""
    total_downloads: int = Field(..., example=500)
    version_stats: Dict[str, int] = Field(
        ..., 
        example={"1.0.0": 300, "1.1.0": 200}
    )
    recent_activity: List[UsageActivityEntry]


class SearchResult(BaseModel):
    """Search result for a component."""
    type: ComponentType = Field(..., example="module")
    namespace: str = Field(..., example="nlp")
    name: str = Field(..., example="basic-sentiment")
    description: str = Field(..., example="Basic sentiment analysis using keyword matching")
    tags: Optional[List[str]] = Field(None, example=["sentiment", "nlp", "analysis"])
    versions: List[str] = Field(..., example=["1.0.0", "1.1.0", "1.2.0"])


class Metadata(BaseModel):
    """Component metadata."""
    name: str = Field(..., example="basic-sentiment")
    namespace: str = Field(..., example="nlp")
    version: str = Field(..., example="1.0.0")
    description: Optional[str] = Field(None, example="Basic sentiment analysis using keyword matching")
    author: Optional[str] = Field(None, example="nlp-team@company.com")
    license: Optional[str] = Field(None, example="MIT")
    tags: Optional[List[str]] = Field(None, example=["sentiment", "nlp", "analysis"])


class Interface(BaseModel):
    """Component interface specification."""
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for input validation")
    output_schema: Dict[str, Any] = Field(..., description="JSON Schema for output validation")


class Implementation(BaseModel):
    """Component implementation specification."""
    type: ImplementationType = Field(..., example="function")
    entry_point: str = Field(..., example="./basic_sentiment.py:analyze_sentiment")
    requirements: Optional[List[str]] = Field(None, example=["regex>=2022.3.0"])
    reasoning_engine: Optional[str] = Field(None, example="openai-gpt4")


class Dependencies(BaseModel):
    """Component dependencies specification."""
    modules: Optional[List[str]] = Field(None, example=["utils/text-cleaner@1.0.0"])
    tools: Optional[List[str]] = Field(None, example=["utils/data-validator@2.1.0"])


class TunableParameter(BaseModel):
    """Tunable parameter specification."""
    type: str = Field(..., example="array")
    description: str = Field(..., example="List of positive sentiment words")
    default_value: Any = Field(..., example=["good", "great", "excellent"])


class Tunable(BaseModel):
    """Tunable parameters specification."""
    parameters: Optional[Dict[str, TunableParameter]] = None
    optimization_targets: Optional[List[str]] = Field(None, example=["accuracy"])
    tuning_method: Optional[str] = Field(None, example="manual")


class Spec(BaseModel):
    """Component specification."""
    interface: Interface
    implementation: Implementation
    dependencies: Optional[Dependencies] = None
    tunable: Optional[Tunable] = None


class Manifest(BaseModel):
    """Component manifest (module or tool specification)."""
    apiVersion: str = Field(..., example="ai-registry/v1")
    kind: ComponentType = Field(..., example="module")
    metadata: Metadata
    spec: Spec

    class Config:
        json_schema_extra = {
            "example": {
                "apiVersion": "ai-registry/v1",
                "kind": "module",
                "metadata": {
                    "name": "basic-sentiment",
                    "namespace": "nlp",
                    "version": "1.0.0",
                    "description": "Basic sentiment analysis using keyword matching",
                    "author": "nlp-team@company.com",
                    "license": "MIT",
                    "tags": ["sentiment", "nlp", "analysis"]
                },
                "spec": {
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
                                "sentiment": {
                                    "type": "string",
                                    "enum": ["positive", "negative", "neutral"]
                                },
                                "confidence": {"type": "number"}
                            },
                            "required": ["sentiment", "confidence"]
                        }
                    },
                    "implementation": {
                        "type": "function",
                        "entry_point": "./basic_sentiment.py:analyze_sentiment",
                        "requirements": ["regex>=2022.3.0"]
                    }
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., example="healthy")
    database: bool = Field(..., example=True)