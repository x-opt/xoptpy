# xopt - eXtreme OPTimization

More optimizing agentic AI with modular, isolated execution environments.

## Overview

xopt is a modular AI framework that allows you to package, distribute, and run AI modules in isolated virtual environments. Each module can have its own dependencies, configurations, and tunables - perfect for optimization workflows where parameters need to be adjusted between runs.

## Key Features

- **Isolated Execution**: Each module runs in its own virtual environment
- **Lightweight Packaging**: Modules packaged as `.xopt` archives (~5-20MB vs 100-500MB containers)  
- **Persistent Configuration**: Tunables and configurables survive between runs
- **Project-Based Dependencies**: Declare dependencies once, run many times
- **Optimization-Friendly**: Modify parameters without reinstalling modules

## Installation

```bash
git clone <repository>
cd xoptpy
poetry install
```

## Quick Start

### 1. Install Example Modules

```bash
# Package the React reasoning module
python3 -m xopt package examples/modules/react

# Package the Calculator module  
python3 -m xopt package examples/modules/calculator

# Install both modules
python3 -m xopt install xopt_react-0.1.0.xopt
python3 -m xopt install xopt_calculator-0.1.0.xopt
```

### 2. Run Modules

```bash
# Run calculator module
python3 -m xopt run "xopt/calculator" "sqrt(16) + 2 * pi"

# Run React reasoning module
python3 -m xopt run "xopt/react" "What is the area of a circle with radius 5?"
```

## CLI Commands

### Module Management

#### `xopt package <module_dir>`
Package a module directory into a `.xopt` archive.

```bash
python3 -m xopt package examples/modules/react
python3 -m xopt package examples/modules/calculator -o my-calc.xopt
```

#### `xopt install <package.xopt>`
Install a module package with isolated virtual environment.

```bash
python3 -m xopt install xopt_react-0.1.0.xopt
```

#### `xopt uninstall <module_name>`
Remove an installed module.

```bash
python3 -m xopt uninstall "xopt/react"
```

#### `xopt list`
List all installed modules.

```bash
python3 -m xopt list
# Output:
# Installed modules:
#   xopt/react@0.1.0 - /home/user/.xopt/modules/xopt_react
#   xopt/calculator@0.1.0 - /home/user/.xopt/modules/xopt_calculator
```

### Running Modules

#### `xopt run <module> "<input>"`
Run an installed module with input.

```bash
python3 -m xopt run "xopt/calculator" "2 + 2"
python3 -m xopt run "xopt/react" "What is 5 times 7?"

# With config overrides
python3 -m xopt run "xopt/react" "Hello" -c '{"tunables": {"react_prompt": "Be very concise"}}'
```

#### `xopt dev <module_dir> <module> "<input>"`
Run a module directly from development directory (no installation required).

```bash
python3 -m xopt dev examples/modules/react "xopt/react" "What is 2+2?"
```

### Project-Based Workflow

#### `xopt init`
Initialize a new xopt project with dependency management.

```bash
python3 -m xopt init
```

Creates:
```
.xopt/
    deps.toml          # Dependency declarations
```

#### `xopt sync`
Install all project dependencies declared in `.xopt/deps.toml`.

```bash
python3 -m xopt sync
```

#### `xopt prun <module> "<input>"`
Run module using project-specific configuration.

```bash
python3 -m xopt prun "xopt/react" "What is the square root of 144?"
```

## Project Structure

### Basic Project Setup

```bash
# 1. Initialize project
python3 -m xopt init

# 2. Edit dependencies
cat > .xopt/deps.toml << EOF
[modules]
"xopt/react" = "0.1.0"
"xopt/calculator" = "0.1.0"

[sources]
"xopt/react" = { path = "examples/modules/react" }
"xopt/calculator" = { path = "examples/modules/calculator" }
EOF

# 3. Create module configurations
cat > .xopt/xopt-react.toml << EOF
[tunables]
react_prompt = "You are a helpful math tutor. Show your work step by step."

[configurables]
tool_list = ["xopt/calculator:0.1.0"]
EOF

# 4. Install dependencies
python3 -m xopt sync

# 5. Run with project config
python3 -m xopt prun "xopt/react" "Calculate 15% of 240"
```

### Configuration Files

#### `.xopt/deps.toml` - Dependency Declaration
```toml
[modules]
"xopt/react" = "0.1.0"
"xopt/calculator" = "0.1.0"

# For development - reference local source
[sources]
"xopt/react" = { path = "examples/modules/react" }
"xopt/calculator" = { path = "examples/modules/calculator" }

# Future: Module registries
[registries]
default = "https://registry.xopt.ai"
```

#### `.xopt/xopt-<module>.toml` - Module Configuration
```toml
# .xopt/xopt-react.toml
[tunables]
react_prompt = """Custom prompt for this project..."""

[configurables]
tool_list = ["xopt/calculator:0.1.0", "xopt/websearch:1.0.0"]
```

## Module Development

### Creating a Module

1. **Create module directory**:
```bash
mkdir my-module
cd my-module
```

2. **Add module metadata** (`xopt.yaml`):
```yaml
my-org/my-module@1.0.0:
  configurables:
    some_list: []
  tunables:
    some_param: "default value"
```

3. **Add dependencies** (`pyproject.toml`):
```toml
[project]
name = "my-module"
version = "1.0.0"
dependencies = [
    "xopt @ file:///path/to/xoptpy"
]
```

4. **Implement module** (`my_module.py`):
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
    def process(input_data: str) -> StepResult:
        # Your module logic here
        return StepResult(
            action="response",
            content=f"Processed: {input_data}"
        )
    
    module.register("process", process, str)
    module.set_start_step("process")
    return module

xopt.register(my_module)
```

5. **Package and install**:
```bash
python3 -m xopt package .
python3 -m xopt install my-org_my-module-1.0.0.xopt
```

## Examples

### Math Calculation Chain
```bash
python3 -m xopt run "xopt/react" "First calculate 12 * 15, then find the square root of that result"
```

### Custom Configuration
```bash
# Create custom React configuration
cat > .xopt/xopt-react.toml << EOF
[tunables]
react_prompt = "You are a precise mathematician. Always show detailed calculations."

[configurables] 
tool_list = ["xopt/calculator:0.1.0"]
EOF

# Run with custom config
python3 -m xopt prun "xopt/react" "What is 25% of 480?"
```

### Optimization Workflow
```python
# optimization.py - Example parameter tuning
import subprocess
import json

prompts = [
    "Be concise and direct.",
    "Show detailed step-by-step reasoning.",
    "Focus on accuracy over speed."
]

for i, prompt in enumerate(prompts):
    config = {"tunables": {"react_prompt": f"You are helpful. {prompt}"}}
    
    result = subprocess.run([
        "python3", "-m", "xopt", "run", "xopt/react",
        "Calculate the area of a circle with radius 7",
        "-c", json.dumps(config)
    ], capture_output=True, text=True)
    
    print(f"Config {i+1}: {result.stdout}")
```

## Architecture

- **Virtual Environment Isolation**: Each module gets its own Python environment (~/.xopt/modules/)
- **Process-Level Execution**: Modules run in separate processes for crash safety
- **Persistent Configuration**: Tunables stored in module directories survive restarts
- **Dependency Management**: Poetry-style dependency resolution with .xopt/deps.toml
- **Trace Generation**: Automatic execution tracing for debugging and optimization

## Development

```bash
# Install in development mode
poetry install

# Run tests
poetry run pytest

# Package for distribution  
poetry build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
