---
sidebar_position: 4
---

# Creating Modules

Learn how to create and package your own AI modules for xopt.

## Module Structure

A module directory consists of:
1. **xopt.yaml** - Module configuration with tunables and configurables
2. **pyproject.toml** - Python dependencies and build configuration
3. **Implementation files** - Python code that implements the module logic
4. **README.md** (optional) - Documentation for the module

## Step-by-Step Module Creation

### 1. Create Module Directory

```bash
mkdir my-module
cd my-module
```

### 2. Create xopt.yaml Configuration

Define your module's interface and default settings:

```yaml
my-org/my-module@1.0.0:
  configurables:
    # Static configuration that doesn't change between runs
    model_name: "default-model"
    max_tokens: 1000
  tunables:
    # Parameters that can be optimized/changed between runs
    temperature: 0.7
    prompt_template: "Process this input: {input}"
```

### 3. Create pyproject.toml Dependencies

Define Python dependencies:

```toml
[project]
name = "my-module"
version = "1.0.0"
description = "My custom AI module"
dependencies = [
    "xopt @ file:///path/to/xoptpy",
    "requests>=2.25.0",
    "numpy>=1.21.0"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
### 4. Implement Module Logic

Create the main module file (e.g., `my_module.py`):

```python
import xopt
from xopt.models import Module, StepResult

@xopt.module
def my_module() -> Module:
    module = Module(
        name="my-org/my-module",
        version="1.0.0",
        description="My custom module"
    )
    
    @xopt.step
    def process_input(input_data: str) -> StepResult:
        # Access tunables and configurables
        client = xopt.get_client()
        config = client.config["my-org/my-module@1.0.0"]
        
        temperature = config["tunables"]["temperature"]
        prompt_template = config["tunables"]["prompt_template"]
        model_name = config["configurables"]["model_name"]
        
        # Your module logic here
        processed_data = prompt_template.format(input=input_data)
        result = f"Processed with {model_name} at temp {temperature}: {processed_data}"
        
        return StepResult(
            action="response",
            content=result
        )
    
    # Register the step and set as entry point
    module.register("process_input", process_input, str)
    module.set_start_step("process_input")
    return module

# Register the module with xopt
xopt.register(my_module)
```

### 5. Package and Test

```bash
# Test in development mode
xopt dev . "my-org/my-module" "test input"

# Package for distribution
xopt package .

# Install and test
xopt install my-org_my-module-1.0.0.xopt
xopt run "my-org/my-module" "hello world"
## Advanced Examples

### React Reasoning Module

Here's how the React reasoning module is implemented:

```python
import xopt
from xopt.models import Module, StepResult

@xopt.module  
def react_module() -> Module:
    module = Module(
        name="xopt/react",
        version="0.1.0",
        description="ReAct reasoning with tool usage"
    )
    
    @xopt.step
    def react_step(input_data: str) -> StepResult:
        client = xopt.get_client()
        config = client.config["xopt/react@0.1.0"]
        
        prompt = config["tunables"]["react_prompt"]
        tools = config["configurables"]["tool_list"]
        
        # Your ReAct reasoning logic here
        # This would include LLM calls, tool usage, etc.
        
        return StepResult(
            action="response", 
            content="Processed using ReAct reasoning"
        )
    
    module.register("react_step", react_step, str)
    module.set_start_step("react_step")
    return module

xopt.register(react_module)
```

## Configuration Best Practices

### Tunables vs Configurables

**Tunables** - Parameters that change during optimization:
- Temperature, learning rates, thresholds
- Prompt variations, model parameters
- Values that affect module behavior

**Configurables** - Static settings that rarely change:
- Model names, file paths, tool lists
- System settings, API endpoints
- Infrastructure configuration

### Example Configuration

```yaml
my-org/sentiment-analyzer@1.0.0:
  configurables:
    model_name: "bert-base-uncased"
    max_sequence_length: 512
    device: "cuda"
  tunables:
    temperature: 0.7
    confidence_threshold: 0.8
    batch_size: 32
```

## Testing and Development

### Development Workflow

```bash
# 1. Create and edit your module
mkdir my-module && cd my-module

# 2. Test directly without packaging
xopt dev . "my-org/my-module" "test input"

# 3. Make changes and test again
xopt dev . "my-org/my-module" "another test"

# 4. Package when ready
xopt package .

# 5. Install and test final version
xopt install my-org_my-module-1.0.0.xopt
xopt run "my-org/my-module" "final test"
```

### Error Handling in Modules

```python
@xopt.step
def robust_step(input_data: str) -> StepResult:
    try:
        # Your processing logic
        result = process_data(input_data)
        
        return StepResult(
            action="response",
            content=result
        )
    except Exception as e:
        # Log error and return graceful failure
        return StepResult(
            action="error",
            content=f"Processing failed: {str(e)}"
        )
```

## Distribution and Sharing

### Creating Reference Modules

Instead of duplicating code, create reference modules for variants:

```toml
# math-expert.toml
[module]
name = "myproject/math-expert"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "You are an expert mathematician. Show detailed proofs."
temperature = 0.3

[configurables]
tool_list = ["xopt/calculator:0.1.0", "xopt/wolfram:0.2.0"]
```

```bash
# Share just the config file
xopt install-config math-expert.toml
```

### Project-Based Distribution

Use `.xopt/deps.toml` for team sharing:

```toml
[modules]
"xopt/react" = "0.1.0"
"myorg/custom-classifier" = "2.1.0"

[sources]
"myorg/custom-classifier" = { path = "modules/classifier" }
```

Team members just run:
```bash
git clone repo && cd repo
xopt sync  # Installs all declared dependencies
```

## Next Steps

- [Working with Tools](./working-with-tools) - Create AI tools and agents
- [API Reference](./api/overview) - Complete API documentation
- [CLI Usage](./cli-usage) - Command-line reference