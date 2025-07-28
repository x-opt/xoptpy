---
sidebar_position: 3
---

# CLI Usage Guide

The XOptPy CLI provides a command-line interface for interacting with the AI Registry API.

## Basic Commands

### Health Check

Check if the API server is running and healthy:

```bash
xopt health
```

### Search Components

Search for modules and tools:

```bash
# Basic search
xopt search components "sentiment"

# Search only modules
xopt search components "sentiment" --type module

# Search only tools  
xopt search components "validation" --type tool

# Get JSON output
xopt search components "sentiment" --json-output
```

## Module Management

### Upload a Module

Upload a module from a YAML manifest file:

```bash
# Upload with version from manifest
xopt module upload test_data/simple_module.yaml

# Override version
xopt module upload test_data/simple_module.yaml --version "2.0.0"

# Override namespace, name, and version
xopt module upload test_data/simple_module.yaml \
  --namespace "custom" --name "my-module" --version "1.0.0"
```

### List Module Versions

```bash
xopt module list-versions examples hello-world

# JSON output
xopt module list-versions examples hello-world --json-output
```

### Get Module Manifest

```bash
# Print to stdout
xopt module get-manifest examples hello-world 1.0.0

# Save to file (YAML)
xopt module get-manifest examples hello-world 1.0.0 --output manifest.yaml

# Save to file (JSON) 
xopt module get-manifest examples hello-world 1.0.0 --output manifest.json
```

### Get Module Dependencies

```bash
xopt module get-dependencies nlp sentiment-analyzer 1.0.0

# JSON output
xopt module get-dependencies nlp sentiment-analyzer 1.0.0 --json-output
```

### Get Module Usage Statistics

```bash
xopt module get-stats examples hello-world

# JSON output
xopt module get-stats examples hello-world --json-output
```

## Tool Management

Tool commands have the same structure as module commands:

```bash
# Upload tool
xopt tool upload test_data/data_validator_tool.yaml

# List versions
xopt tool list-versions utils data-validator

# Get manifest
xopt tool get-manifest utils data-validator 1.0.0

# Get dependencies
xopt tool get-dependencies utils data-validator 1.0.0

# Get stats
xopt tool get-stats utils data-validator
```

## YAML Manifest Files

### Module Manifest Example

```yaml
apiVersion: "ai-registry/v1"
kind: "module"
metadata:
  name: "sentiment-analyzer"
  namespace: "nlp"
  version: "1.0.0"
  description: "Sentiment analysis module"
  author: "team@company.com"
  license: "MIT"
  tags:
    - "sentiment"
    - "nlp"
spec:
  interface:
    input_schema:
      type: "object"
      properties:
        text:
          type: "string"
      required: ["text"]
    output_schema:
      type: "object"
      properties:
        sentiment:
          type: "string"
          enum: ["positive", "negative", "neutral"]
        confidence:
          type: "number"
      required: ["sentiment", "confidence"]
  implementation:
    type: "function"
    entry_point: "./sentiment.py:analyze"
    requirements:
      - "transformers>=4.21.0"
  dependencies:
    modules:
      - "utils/text-cleaner@1.0.0"
```

### Tool Manifest Example

```yaml
apiVersion: "ai-registry/v1"
kind: "tool"
metadata:
  name: "data-validator"
  namespace: "utils"
  version: "1.0.0"
  description: "Data validation tool"
  author: "team@company.com"
  license: "MIT"
  tags:
    - "validation"
    - "data"
spec:
  interface:
    input_schema:
      type: "object"
      properties:
        data:
          type: "object"
        schema:
          type: "object"
      required: ["data", "schema"]
    output_schema:
      type: "object"
      properties:
        is_valid:
          type: "boolean"
        errors:
          type: "array"
      required: ["is_valid"]
  implementation:
    type: "react_agent"
    entry_point: "./validator.py:ValidationAgent"
    requirements:
      - "jsonschema>=4.17.0"
    reasoning_engine: "openai-gpt4"
```

## Global Options

All commands support these global options:

```bash
# Override base URL
xopt --base-url "http://other-server:8080" health

# Set timeout
xopt --timeout 60 search components "sentiment"

# Enable verbose logging
xopt --verbose health
```

## Error Handling

The CLI provides specific exit codes for different error conditions:

- `0`: Success
- `1`: General error
- `404`: Resource not found

Use JSON output for programmatic processing:

```bash
# Check if command succeeded
if xopt search components "nonexistent" --json-output > /dev/null 2>&1; then
    echo "Found components"
else
    echo "No components found or error occurred"
fi
```

## Examples

### Complete Workflow

```bash
# 1. Check API health
xopt health

# 2. Search for existing components
xopt search components "sentiment"

# 3. Upload a new module
xopt module upload my_module.yaml

# 4. List versions of the uploaded module
xopt module list-versions my-namespace my-module

# 5. Get usage statistics
xopt module get-stats my-namespace my-module
```

### Batch Operations

```bash
# Upload multiple modules
for file in modules/*.yaml; do
    xopt module upload "$file"
done

# Search and export all sentiment-related modules
xopt search components "sentiment" --json-output | \
    jq -r '.[] | select(.type == "module") | "\(.namespace)/\(.name)"' | \
    while read module; do
        namespace=$(echo $module | cut -d'/' -f1)
        name=$(echo $module | cut -d'/' -f2)
        xopt module get-stats "$namespace" "$name"
    done
```