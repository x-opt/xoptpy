---
sidebar_position: 5
---

# Working with Tools

Learn how xopt modules automatically discover and use other installed modules as tools.

## How Tool Discovery Works

xopt modules can automatically discover and use other installed modules as tools during runtime. This enables powerful cross-module interactions like ReAct reasoning agents that can use calculator, search, and other specialized modules.

### Automatic Module Loading

When any module runs, xopt automatically:

1. **Discovers all installed modules** in `~/.xopt/modules/`
2. **Loads them into the module registry** so they can be called as tools  
3. **Provides tool information** to modules that need it (like ReAct agents)

```bash
# When you run React, it automatically discovers calculator
xopt list
# Output:
#   xopt/calculator@0.1.0 - /home/user/.xopt/modules/xopt_calculator
#   xopt/react@0.1.0 - /home/user/.xopt/modules/xopt_react

xopt run "xopt/react" "What is 15 * 23?"
# React automatically uses calculator tool: 15 * 23 = 345
```

## Tool Configuration

### Declaring Tool Dependencies

Modules declare which tools they can use in their `xopt.yaml` configuration:

```yaml
name: "xopt/react"
version: "0.1.0"
tunables:
  react_prompt: |
    You are a helpful assistant. You can use tools when needed...
configurables:
  tool_list: [
    "xopt/calculator:0.1.0"
  ]
```

### Tool Resolution

At runtime, xopt resolves tool references:
- `"xopt/calculator:0.1.0"` → Uses the installed `xopt/calculator` module
- Tool descriptions are provided to ReAct agents so they know what tools are available
- Tools are called as separate module executions in their own virtual environments

## ReAct Reasoning with Tools

### How ReAct Modules Work

The React module implements the ReAct (Reasoning + Acting) pattern:

1. **Thought**: LLM thinks about the problem
2. **Action**: LLM decides to use a tool (e.g., `xopt/calculator`)
3. **Action Input**: LLM provides input for the tool (e.g., `"15 * 23"`)
4. **Observation**: Tool executes and returns result (e.g., `345.0`)
5. **Final Answer**: LLM provides final response using the tool result

### Example ReAct Flow

```bash
xopt run "xopt/react" "Calculate the square root of 156"
```

Internal flow:
```
Thought: I need to calculate the square root of 156.
Action: xopt/calculator  
Action Input: sqrt(156)
Observation: 12.49 (returned by calculator module)
Final Answer: The square root of 156 is approximately 12.49.
```

## Creating Tool-Enabled Modules

### Basic Tool Usage

Create a module that can call other modules as tools:

```python
import xopt
from xopt.models import Module

@xopt.module
def my_agent() -> Module:
    module = Module(
        name="myorg/agent",
        version="1.0.0",
        description="Agent that uses tools"
    )
    
    @xopt.step
    def agent_step(input_data: str):
        # Get available tools from configuration
        client = xopt.get_client()
        config = client.config["myorg/agent@1.0.0"]
        tool_list = config.get("configurables", {}).get("tool_list", [])
        
        # Use xopt.details() to get tool information
        for tool_name in tool_list:
            tool_info = xopt.details(tool_name)
            if tool_info:
                print(f"Available tool: {tool_info['name']}")
                print(f"Description: {tool_info['long_description']}")
        
        # Call a tool module
        if "xopt/calculator:0.1.0" in tool_list:
            # Tools are called as separate module executions
            result = xopt.call_module("xopt/calculator", "2 + 2")
            return f"Calculator result: {result}"
        
        return "No tools available"
    
    module.register("agent_step", agent_step, str)
    module.set_start_step("agent_step")
    return module

xopt.register(my_agent)
```

### Module Configuration

Configure your module to use specific tools:

```yaml
# myorg_agent/xopt.yaml
name: "myorg/agent"
version: "1.0.0"
configurables:
  tool_list: [
    "xopt/calculator:0.1.0",
    "xopt/search:0.2.0"
  ]
tunables:
  agent_prompt: "You are a helpful agent with access to tools."
```

## Available Tool Modules

### Calculator Module

Mathematical expression evaluation:

```bash
# Direct usage
xopt run "xopt/calculator" "sqrt(16) + 2 * pi"

# Available in React
xopt run "xopt/react" "What is the area of a circle with radius 5?"
```

**Capabilities:**
- Basic arithmetic (`+`, `-`, `*`, `/`)
- Mathematical functions (`sqrt`, `sin`, `cos`, `tan`, `exp`, `log`)
- Constants (`pi`, `e`)
- Safe expression evaluation (no imports allowed)

### React Reasoning Module

ReAct reasoning agent that can use other modules as tools:

```bash
xopt run "xopt/react" "Solve this step by step: (5 + 3) * sqrt(9)"
```

**Capabilities:**
- Step-by-step reasoning
- Automatic tool selection and usage
- Tool result integration
- Conversational responses

## Tool Development Best Practices

### 1. Clear Module Interfaces

Design modules with clear input/output interfaces:

```python
@xopt.step
def calculate(step_input) -> float:
    """
    Evaluates mathematical expressions.
    
    Args:
        step_input: String containing mathematical expression
        
    Returns:
        float: Result of the calculation
        
    Raises:
        ValueError: If expression is invalid or contains imports
    """
    # Implementation...
```

### 2. Safe Execution

Ensure tools execute safely:

```python
def safe_calculate(expression: str) -> float:
    # Validate input
    if 'import' in expression:
        raise ValueError("Import statements are not allowed")
    
    # Use safe evaluation
    safe_dict = {'sin': math.sin, 'cos': math.cos, 'pi': math.pi}
    return eval(expression, {"__builtins__": {}}, safe_dict)
```

### 3. Good Documentation

Provide clear descriptions in module metadata:

```python
module = Module(
    name="xopt/calculator",
    version="0.1.0",
    description="A simple calculator module that evaluates mathematical expressions.",
    long_description="This module evaluates mathematical expressions using Python syntax. Available functions: sin, cos, tan, exp, log, sqrt, pow, abs, floor, ceil, pi, e. Input the mathematical expression directly without quotes."
)
```

## Debugging Tool Integration

### Checking Tool Discovery

```bash
# List all installed modules
xopt list

# Run with verbose output to see tool loading
xopt run "xopt/react" "test" --verbose
```

### Module Registry Inspection

The xopt system automatically loads all installed modules into the registry. You can verify this by checking the module loading process or examining trace files generated during execution.

### Common Issues

1. **Tool not found**: Ensure the tool module is installed with `xopt list`
2. **Version mismatch**: Check that tool_list references match installed versions
3. **Configuration errors**: Verify xopt.yaml syntax and tool_list format

## Next Steps

- [Creating Modules](./creating-modules) - Learn how to build modules that can serve as tools  
- [CLI Usage](./cli-usage) - Command-line reference for managing modules
- [API Reference](./api/overview) - Complete API documentation