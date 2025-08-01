---
sidebar_position: 3
---

# CLI Usage Guide

The xopt CLI provides commands for packaging, installing, and running AI modules in isolated virtual environments.

## Basic Commands

### Initialize Project

Create a new xopt project with dependency management:

```bash
xopt init
```

Creates `.xopt/deps.toml` for managing project dependencies.

### List Installed Modules

Show all installed modules:

```bash
xopt list
```

Output shows module names, versions, and installation paths:
```
Installed modules:
  xopt/react@0.1.0 - /home/user/.xopt/modules/xopt_react
  xopt/calculator@0.1.0 - /home/user/.xopt/modules/xopt_calculator
```

## Module Management

### Package a Module

Package a module directory into a `.xopt` archive:

```bash
# Package example modules
xopt package examples/modules/react
xopt package examples/modules/calculator

# Package with custom output name
xopt package examples/modules/react -o custom-react.xopt
```

This creates a compressed archive containing the module code, dependencies, and metadata.

### Install a Module

Install a packaged module with isolated virtual environment:

```bash
# Install from .xopt file
xopt install xopt_react-0.1.0.xopt
xopt install xopt_calculator-0.1.0.xopt
```

Each module gets its own virtual environment in `~/.xopt/modules/`.

### Uninstall a Module

Remove an installed module and its virtual environment:

```bash
xopt uninstall "xopt/react"
xopt uninstall "xopt/calculator"
```

This removes the module directory and all its dependencies.

### Install Project Dependencies

Install all modules declared in `.xopt/deps.toml`:

```bash
xopt sync
```

This reads the project configuration and installs any missing dependencies.

## Running Modules

### Execute Installed Modules

Run modules with input data:

```bash
# Run calculator module
xopt run "xopt/calculator" "sqrt(16) + 2 * pi"

# Run React reasoning module
xopt run "xopt/react" "What is the area of a circle with radius 5?"

# Run with config overrides
xopt run "xopt/react" "Hello" -c '{"tunables": {"react_prompt": "Be concise"}}'
```

### Development Mode

Run modules directly from source without packaging:

```bash
# Run from development directory
xopt dev examples/modules/react "xopt/react" "What is 2+2?"
```

This is useful during module development for quick testing.

## Reference Modules

### Install Reference Module

Create lightweight module variants with custom configurations:

```bash
# Create reference module config
cat > math-tutor-react.toml << EOF
[module]
name = "myproject/math-tutor-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "You are a friendly math tutor for 5th graders..."

[configurables]
tool_list = ["xopt/calculator:0.1.0"]
EOF

# Install the reference module
xopt install-config math-tutor-react.toml
```

### Run Reference Module

Reference modules run using the base module's virtual environment but with custom settings:

```bash
# Run with customized behavior
xopt run "myproject/math-tutor-react" "What is 6 times 8?"
```

Reference modules are perfect for:
- Custom prompts for different use cases
- Different tool configurations
- Project-specific module variants

## Module Configuration Files

### xopt.yaml - Module Configuration

Each module directory contains an `xopt.yaml` file defining the module:

```yaml
xopt/react@0.1.0:
  configurables:
    tool_list: ["xopt/calculator:0.1.0"]
  tunables:
    react_prompt: |
      You are a helpful AI assistant that can reason through problems step by step.
      
      Thought: I need to think about what the user is asking and determine if I need to use any tools.
      Action: [tool_name] (only if you need to use a tool, otherwise skip this line)  
      Action Input: [input_for_tool] (only if you used Action, otherwise skip this line)
      
      STOP HERE if you used Action. The system will provide the Observation.
      
      Final Answer: [your response] (only if no tools were needed)
```

### pyproject.toml - Module Dependencies

Each module also has a `pyproject.toml` for Python dependencies:

```toml
[project]
name = "react"
version = "0.1.0"
dependencies = [
    "xopt @ file:///path/to/xoptpy"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

## Command-Specific Options

### Package Options

```bash
# Package with custom output filename
xopt package examples/modules/react -o custom-name.xopt
```

### Run Options

```bash
# Run with configuration overrides
xopt run "xopt/react" "input" -c '{"tunables": {"param": "value"}}'

# Run with JSON configuration file
xopt run "xopt/react" "input" --config-file config.json
```

## Error Handling

The CLI provides helpful error messages and exit codes:

- `0`: Success
- `1`: General error (module not found, installation failed, etc.)

Common error scenarios:

```bash
# Module not installed
$ xopt run "nonexistent/module" "test"
Error: Module nonexistent/module is not installed. Run 'xopt sync' first.

# Invalid module package
$ xopt install invalid.xopt
Error installing module: Invalid archive format
```

## Examples

### Complete Workflow

```bash
# 1. Initialize project
xopt init

# 2. Package example modules
xopt package examples/modules/react
xopt package examples/modules/calculator

# 3. Install modules
xopt install xopt_react-0.1.0.xopt
xopt install xopt_calculator-0.1.0.xopt

# 4. List installed modules
xopt list

# 5. Run modules
xopt run "xopt/calculator" "2 + 2"
xopt run "xopt/react" "What is the square root of 16?"
```

### Reference Module Workflow

```bash
# 1. Create custom variant
cat > precise-math.toml << EOF
[module]
name = "myproject/precise-math-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "Be very precise and show all calculation steps."
EOF

# 2. Install reference module
xopt install-config precise-math.toml

# 3. Run with custom behavior
xopt run "myproject/precise-math-react" "Calculate 15% of 240"

# 4. List all modules (base + reference)
xopt list
```

### Development Workflow

```bash
# 1. Create new module directory
mkdir my-module && cd my-module

# 2. Create module files (xopt.yaml, pyproject.toml, code)

# 3. Test without packaging
xopt dev . "my-org/my-module" "test input"

# 4. Package when ready
xopt package .

# 5. Install for production use
xopt install my-org_my-module-1.0.0.xopt
```