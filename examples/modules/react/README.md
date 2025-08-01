# React Module

A ReAct (Reasoning and Acting) module for xopt that enables step-by-step reasoning with tool usage.

## Features

- Step-by-step reasoning using the ReAct framework
- Tool integration for external actions
- Configurable prompt and tool list
- Calculator tool included

## Usage

```python
import xopt

# Start the react module
react = xopt.start("xopt/react@0.1.0")

# Use it for reasoning and tool usage
result = react.call("What is 2 + 2?")
print(result.content)
```