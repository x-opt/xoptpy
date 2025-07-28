---
sidebar_position: 4
---

# Creating Modules

Learn how to create and publish your own AI modules to the xopt registry.

## Module Structure

A module consists of:
1. **Manifest file** (YAML) - Defines metadata, interface, and implementation
2. **Implementation** - The actual code that runs when the module is executed
3. **Dependencies** - Required packages and other modules

## Creating a Module Manifest

### Basic Module Structure

Create a `manifest.yaml` file:

```yaml
apiVersion: "ai-registry/v1"
kind: "module"
metadata:
  name: "my-classifier"
  namespace: "ml"
  version: "1.0.0"
  description: "Custom text classifier"
  author: "your-email@example.com"
  license: "MIT"
  tags:
    - "classification"
    - "nlp"
    - "machine-learning"

spec:
  interface:
    input_schema:
      type: "object"
      properties:
        text:
          type: "string"
          description: "Text to classify"
      required: ["text"]
    
    output_schema:
      type: "object"
      properties:
        category:
          type: "string"
          description: "Predicted category"
        confidence:
          type: "number"
          minimum: 0
          maximum: 1
          description: "Confidence score"
      required: ["category", "confidence"]
  
  implementation:
    type: "function"
    entry_point: "./classifier.py:classify"
    requirements:
      - "scikit-learn>=1.0.0"
      - "numpy>=1.21.0"
  
  dependencies:
    modules:
      - "nlp/text-preprocessor@1.2.0"
```

### Metadata Fields

- **name**: Module name (lowercase, hyphens allowed)
- **namespace**: Organizational namespace (e.g., `nlp`, `ml`, `utils`)
- **version**: Semantic version (e.g., `1.0.0`)
- **description**: Brief description of functionality
- **author**: Author email or name
- **license**: License type (MIT, Apache-2.0, etc.)
- **tags**: Searchable keywords

### Interface Definition

Define clear input and output schemas using JSON Schema:

```yaml
interface:
  input_schema:
    type: "object"
    properties:
      text:
        type: "string"
        description: "Input text to process"
        maxLength: 10000
      options:
        type: "object"
        properties:
          language:
            type: "string"
            enum: ["en", "es", "fr"]
            default: "en"
    required: ["text"]
  
  output_schema:
    type: "object"
    properties:
      result:
        type: "string"
      metadata:
        type: "object"
        properties:
          processing_time:
            type: "number"
          model_version:
            type: "string"
    required: ["result"]
```

## Implementation Types

### Function Implementation

Most common type - a simple Python function:

```yaml
implementation:
  type: "function"
  entry_point: "./my_module.py:process_text"
  requirements:
    - "transformers>=4.21.0"
    - "torch>=1.12.0"
```

Implementation file (`my_module.py`):

```python
def process_text(input_data: dict) -> dict:
    """
    Process text according to the module interface.
    
    Args:
        input_data: Dictionary matching input_schema
        
    Returns:
        Dictionary matching output_schema
    """
    text = input_data["text"]
    
    # Your processing logic here
    result = analyze_text(text)
    
    return {
        "result": result,
        "metadata": {
            "processing_time": 0.5,
            "model_version": "1.0"
        }
    }
```

### Class Implementation

For more complex modules:

```yaml
implementation:
  type: "class"
  entry_point: "./my_module.py:TextProcessor"
  requirements:
    - "transformers>=4.21.0"
```

```python
class TextProcessor:
    def __init__(self):
        # Initialize your model/resources
        self.model = load_model()
    
    def __call__(self, input_data: dict) -> dict:
        # Process the input
        return self.process(input_data)
    
    def process(self, input_data: dict) -> dict:
        # Your processing logic
        return {"result": "processed"}
```

### Agent Implementation

For complex AI agents:

```yaml
implementation:
  type: "react_agent"
  entry_point: "./agent.py:MyAgent"
  requirements:
    - "langchain>=0.1.0"
  reasoning_engine: "openai-gpt4"
  tools:
    - "web_search"
    - "calculator"
```

## Dependencies

### Module Dependencies

Reference other modules in the registry:

```yaml
dependencies:
  modules:
    - "nlp/tokenizer@1.0.0"
    - "utils/data-validator@2.1.0"
```

### Python Package Requirements

Specify Python packages:

```yaml
implementation:
  requirements:
    - "numpy>=1.21.0"
    - "pandas>=1.3.0"
    - "scikit-learn==1.2.0"  # Exact version
    - "transformers>=4.21.0,<5.0.0"  # Version range
```

## Testing Your Module

### Local Testing

Test your module locally before uploading:

```bash
# Test with sample input
xopt run . text="sample input"

# Test with input file
xopt run . --input test_input.json
```

### Validation

Validate your manifest:

```bash
xopt validate manifest.yaml
```

## Publishing Your Module

### Upload to Registry

```bash
# Upload with default settings
xopt module upload manifest.yaml

# Override version
xopt module upload manifest.yaml --version "2.0.0"

# Upload to specific namespace
xopt module upload manifest.yaml --namespace "my-org"
```

### Versioning Best Practices

Follow semantic versioning:
- **1.0.0** → **1.0.1**: Bug fixes
- **1.0.0** → **1.1.0**: New features (backward compatible)
- **1.0.0** → **2.0.0**: Breaking changes

### Documentation

Include comprehensive documentation:

```yaml
metadata:
  description: "Detailed description of what the module does"
  documentation_url: "https://github.com/user/repo/blob/main/README.md"
  examples:
    - input: {"text": "Hello world"}
      output: {"category": "greeting", "confidence": 0.95}
```

## Best Practices

### 1. Clear Interfaces

- Use descriptive property names
- Include detailed descriptions
- Specify data types and constraints
- Provide examples

### 2. Error Handling

```python
def process_text(input_data: dict) -> dict:
    try:
        text = input_data.get("text", "")
        if not text:
            raise ValueError("Text input is required")
        
        result = analyze_text(text)
        return {"result": result}
        
    except Exception as e:
        return {
            "error": str(e),
            "result": None
        }
```

### 3. Resource Management

- Clean up resources properly
- Use context managers for file handling
- Consider memory usage for large models

### 4. Configuration

Support configuration through input parameters:

```yaml
input_schema:
  properties:
    text:
      type: "string"
    config:
      type: "object"
      properties:
        model_name:
          type: "string"
          default: "default-model"
        batch_size:
          type: "integer"
          default: 32
```

## Advanced Topics

### Optimization Parameters

Expose parameters for optimization:

```yaml
spec:
  optimization:
    parameters:
      learning_rate:
        type: "float"
        range: [0.001, 0.1]
        default: 0.01
      batch_size:
        type: "integer"
        range: [16, 128]
        default: 32
```

### Performance Metrics

Define metrics for evaluation:

```yaml
spec:
  metrics:
    - name: "accuracy"
      type: "float"
      higher_is_better: true
    - name: "latency"
      type: "float"
      higher_is_better: false
      unit: "seconds"
```

## Next Steps

- [Working with Tools](./working-with-tools) - Create AI tools and agents
- [API Reference](./api/overview) - Complete API documentation
- [CLI Usage](./cli-usage) - Command-line reference