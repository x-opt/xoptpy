---
sidebar_position: 5
---

# Working with Tools

Learn how to create, manage, and optimize AI tools and agents in the xopt registry.

## What are Tools?

Tools in xopt are AI-powered components that can perform specific tasks or provide capabilities to other modules. Unlike modules that process data, tools are designed to:
- Interact with external systems
- Provide reasoning capabilities
- Execute complex multi-step operations
- Act as intelligent agents

## Tool Types

### React Agents

Agents that use reasoning and external tools to solve problems:

```yaml
apiVersion: "ai-registry/v1"
kind: "tool"
metadata:
  name: "research-agent"
  namespace: "agents"
  version: "1.0.0"
  description: "AI agent for conducting research tasks"

spec:
  interface:
    input_schema:
      type: "object"
      properties:
        topic:
          type: "string"
          description: "Research topic"
        depth:
          type: "string"
          enum: ["basic", "detailed", "comprehensive"]
          default: "basic"
    output_schema:
      type: "object"
      properties:
        findings:
          type: "array"
          items:
            type: "string"
        sources:
          type: "array"
          items:
            type: "string"
        summary:
          type: "string"

  implementation:
    type: "react_agent"
    entry_point: "./research_agent.py:ResearchAgent"
    reasoning_engine: "openai-gpt4"
    tools:
      - "web_search"
      - "document_reader"
    requirements:
      - "langchain>=0.1.0"
      - "openai>=1.0.0"
```

### Data Processing Tools

Tools for validation, transformation, and analysis:

```yaml
apiVersion: "ai-registry/v1"
kind: "tool"
metadata:
  name: "data-validator"
  namespace: "utils"
  version: "1.0.0"
  description: "Data validation and cleaning tool"

spec:
  interface:
    input_schema:
      type: "object"
      properties:
        data:
          type: "object"
        schema:
          type: "object"
        rules:
          type: "array"
          items:
            type: "string"
    output_schema:
      type: "object"
      properties:
        is_valid:
          type: "boolean"
        errors:
          type: "array"
          items:
            type: "string"
        cleaned_data:
          type: "object"

  implementation:
    type: "function"
    entry_point: "./validator.py:validate_data"
    requirements:
      - "jsonschema>=4.17.0"
      - "pandas>=1.3.0"
```

## Creating Tools

### 1. Define Tool Interface

Start with a clear interface specification:

```python
# validator.py
def validate_data(input_data: dict) -> dict:
    """
    Validate and clean data according to schema and rules.
    
    Args:
        input_data: Dictionary with 'data', 'schema', and 'rules'
        
    Returns:
        Dictionary with validation results and cleaned data
    """
    data = input_data["data"]
    schema = input_data["schema"]
    rules = input_data.get("rules", [])
    
    errors = []
    is_valid = True
    
    # Validation logic here
    try:
        # Schema validation
        validate_schema(data, schema)
        
        # Custom rules validation
        for rule in rules:
            validate_rule(data, rule)
            
        cleaned_data = clean_data(data, rules)
        
    except ValidationError as e:
        errors.append(str(e))
        is_valid = False
        cleaned_data = data
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "cleaned_data": cleaned_data
    }
```

### 2. Agent Implementation

For more complex agents:

```python
# research_agent.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

class ResearchAgent:
    def __init__(self):
        self.tools = self._setup_tools()
        self.agent = self._create_agent()
    
    def _setup_tools(self):
        return [
            Tool(
                name="web_search",
                description="Search the web for information",
                func=self._web_search
            ),
            Tool(
                name="document_reader", 
                description="Read and analyze documents",
                func=self._read_document
            )
        ]
    
    def _create_agent(self):
        # Create ReAct agent with tools
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template
        )
    
    def __call__(self, input_data: dict) -> dict:
        topic = input_data["topic"]
        depth = input_data.get("depth", "basic")
        
        # Execute research task
        result = self.agent.invoke({
            "input": f"Research {topic} with {depth} depth"
        })
        
        return {
            "findings": result["findings"],
            "sources": result["sources"],
            "summary": result["output"]
        }
```

## Tool Management

### Upload Tools

```bash
# Upload tool manifest
xopt tool upload my_tool.yaml

# Override version
xopt tool upload my_tool.yaml --version "2.0.0"
```

### List and Query Tools

```bash
# List tool versions
xopt tool list-versions utils data-validator

# Get tool manifest
xopt tool get-manifest utils data-validator 1.0.0

# Get tool dependencies
xopt tool get-dependencies utils data-validator 1.0.0

# Get usage statistics
xopt tool get-stats utils data-validator
```

### Search Tools

```bash
# Search for tools
xopt search components "validation" --type tool

# Search for agents
xopt search components "agent" --type tool
```

## Tool Integration

### Using Tools in Modules

Reference tools as dependencies:

```yaml
# In a module manifest
dependencies:
  tools:
    - "utils/data-validator@1.0.0"
    - "agents/research-agent@2.1.0"
```

### Composing Workflows

Chain tools together:

```python
def process_research_data(input_data: dict) -> dict:
    # Step 1: Validate input data
    validator = load_tool("utils/data-validator@1.0.0")
    validation_result = validator({
        "data": input_data["raw_data"],
        "schema": input_data["schema"]
    })
    
    if not validation_result["is_valid"]:
        return {"error": "Invalid input data", "details": validation_result["errors"]}
    
    # Step 2: Conduct research
    research_agent = load_tool("agents/research-agent@2.1.0")
    research_result = research_agent({
        "topic": input_data["topic"],
        "depth": "detailed"
    })
    
    return {
        "validated_data": validation_result["cleaned_data"],
        "research_findings": research_result["findings"],
        "summary": research_result["summary"]
    }
```

## Best Practices

### 1. Clear Capabilities

Define what your tool can and cannot do:

```yaml
metadata:
  description: "Data validation tool for JSON and CSV formats. Supports schema validation, custom rules, and data cleaning."
  capabilities:
    - "JSON schema validation"
    - "CSV format validation"
    - "Custom rule enforcement"
    - "Data cleaning and normalization"
  limitations:
    - "Does not support binary data formats"
    - "Maximum file size: 100MB"
```

### 2. Error Handling

Implement robust error handling:

```python
def process_data(input_data: dict) -> dict:
    try:
        # Processing logic
        result = perform_processing(input_data)
        return {"success": True, "result": result}
        
    except ValidationError as e:
        return {"success": False, "error": "validation_error", "message": str(e)}
    except ProcessingError as e:
        return {"success": False, "error": "processing_error", "message": str(e)}
    except Exception as e:
        return {"success": False, "error": "unknown_error", "message": "An unexpected error occurred"}
```

### 3. Resource Management

Handle resources properly:

```python
class DataProcessor:
    def __init__(self):
        self.connection = None
    
    def __enter__(self):
        self.connection = create_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
    
    def process(self, data):
        # Use self.connection
        pass
```

### 4. Configuration

Support configuration options:

```yaml
spec:
  configuration:
    parameters:
      timeout:
        type: "integer"
        default: 30
        description: "Request timeout in seconds"
      retry_count:
        type: "integer"
        default: 3
        description: "Number of retry attempts"
      model_name:
        type: "string"
        default: "gpt-4"
        description: "LLM model to use"
```

## Advanced Topics

### Optimization

Tools can be optimized for performance:

```yaml
spec:
  optimization:
    parameters:
      batch_size:
        type: "integer"
        range: [1, 100]
        default: 10
      temperature:
        type: "float"
        range: [0.0, 2.0]
        default: 0.7
    metrics:
      - name: "accuracy"
        type: "float"
        higher_is_better: true
      - name: "latency"
        type: "float"
        higher_is_better: false
```

### Monitoring

Implement monitoring and logging:

```python
import logging
from xopt.monitoring import track_usage, log_performance

def process_with_monitoring(input_data: dict) -> dict:
    with track_usage("data-validator", "1.0.0"):
        start_time = time.time()
        
        try:
            result = process_data(input_data)
            
            # Log success metrics
            log_performance(
                tool="data-validator",
                operation="validation",
                duration=time.time() - start_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            # Log error metrics
            log_performance(
                tool="data-validator",
                operation="validation", 
                duration=time.time() - start_time,
                success=False,
                error=str(e)
            )
            raise
```

## Next Steps

- [API Reference](./api/overview) - Complete API documentation
- [Creating Modules](./creating-modules) - Learn about modules vs tools
- [CLI Usage](./cli-usage) - Command-line reference