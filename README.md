**Warning! This repo is under active and breaking development. It is not stable enough to be used! This warning will be removed when the project is stable.**

<div align="center">

# xopt

[![PyPI version](https://badge.fury.io/py/xoptpy.svg)](https://badge.fury.io/py/xoptpy)
[![PyPI downloads](https://img.shields.io/pypi/dm/xoptpy.svg)](https://pypi.org/project/xoptpy/)
[![Python versions](https://img.shields.io/pypi/pyversions/xoptpy.svg)](https://pypi.org/project/xoptpy/)
[![License](https://img.shields.io/pypi/l/xoptpy.svg)](https://github.com/x-opt/xoptpy/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://xoptpy.github.io)
[![GitHub stars](https://img.shields.io/github/stars/x-opt/xoptpy.svg?style=social&label=Star)](https://github.com/x-opt/xoptpy)
[![Tests](https://github.com/x-opt/xoptpy/workflows/Test%20and%20Build/badge.svg)](https://github.com/x-opt/xoptpy/actions)

### Join the discord!

[![](https://dcbadge.limes.pink/api/server/https://discord.gg/5A6VzEnK3g)](https://discord.gg/https://discord.gg/5A6VzEnK3g)

**Modular AI framework with isolated execution environments**

*Package, distribute, and run AI modules in lightweight virtual environments*

</div>

## 📝 Overview

xopt is a modular AI framework that allows you to package, distribute, and run AI modules in isolated virtual environments. Each module can have its own dependencies, configurations, and tunables - perfect for AI workflows where parameters need to be adjusted between runs.

## ✨ Key Features

- 🔒 **Isolated Execution** - Each module runs in its own virtual environment
- 📦 **Lightweight Packaging** - Modules packaged as `.xopt` archives (~5-20MB vs 100-500MB containers)  
- 💾 **Persistent Configuration** - Tunables and configurables survive between runs
- 🔗 **Reference Modules** - Create lightweight variants of existing modules with custom settings
- 📋 **Project-Based Dependencies** - Declare dependencies once, run many times
- ⚡ **Developer-Friendly** - Modify parameters without reinstalling modules

## 🚀 Installation

<div align="center">

### Quick Install

```bash
pip install xoptpy
```

[![PyPI](https://img.shields.io/badge/PyPI-xoptpy-blue?logo=pypi&logoColor=white)](https://pypi.org/project/xoptpy/)

*Requires Python 3.9+*

</div>

## 🚀 Quick Start

### 1. Initialize and Set Up Project

```bash
# Initialize a new xopt project
xopt init

# This creates .xopt/deps.toml for dependency management
```

### 2. Install Example Modules

```bash
# Package the React reasoning module
xopt package examples/modules/react

# Package the Calculator module  
xopt package examples/modules/calculator

# Install both modules
xopt install xopt_react-0.1.0.xopt
xopt install xopt_calculator-0.1.0.xopt
```

### 3. Run Modules

```bash
# Run calculator module
xopt run "xopt/calculator" "sqrt(16) + 2 * pi"

# Run React reasoning module
xopt run "xopt/react" "What is the area of a circle with radius 5?"

# List all installed modules
xopt list
```

## ⚙️ CLI Commands Reference

After installing with `pip install xoptpy`, all commands are available as `xopt <command>`.

```bash
xopt --help  # Show all available commands
```

**Available Commands:**
- `package` - Package a module directory into .xopt archive
- `install` - Install a module package (.xopt file)
- `install-config` - Install a reference module from TOML config
- `uninstall` - Remove an installed module
- `list` - List all installed modules
- `run` - Run an installed module with input
- `dev` - Run a module directly from development directory
- `init` - Initialize a new xopt project
- `sync` - Install project dependencies from .xopt/deps.toml

### Module Management

#### `xopt package <module_dir>`
Package a module directory into a `.xopt` archive.

```bash
xopt package examples/modules/react
xopt package examples/modules/calculator -o my-calc.xopt
```

#### `xopt install <package.xopt>`
Install a module package with isolated virtual environment.

```bash
xopt install xopt_react-0.1.0.xopt
```

#### `xopt uninstall <module_name>`
Remove an installed module.

```bash
xopt uninstall "xopt/react"
```

#### `xopt list`
List all installed modules.

```bash
xopt list
# Output:
# Installed modules:
#   xopt/react@0.1.0 - /home/user/.xopt/modules/xopt_react
#   xopt/calculator@0.1.0 - /home/user/.xopt/modules/xopt_calculator
```

### Running Modules

#### `xopt run <module> "<input>"`
Run an installed module with input.

```bash
xopt run "xopt/calculator" "2 + 2"
xopt run "xopt/react" "What is 5 times 7?"

# With config overrides
xopt run "xopt/react" "Hello" -c '{"tunables": {"react_prompt": "Be very concise"}}'
```

#### `xopt dev <module_dir> <module> "<input>"`
Run a module directly from development directory (no installation required).

```bash
xopt dev examples/modules/react "xopt/react" "What is 2+2?"
```

### Project-Based Workflow

#### `xopt init`
Initialize a new xopt project with dependency management.

```bash
xopt init
```

Creates:
```
.xopt/
    deps.toml          # Dependency declarations
```

#### `xopt sync`
Install all project dependencies declared in `.xopt/deps.toml`.

```bash
xopt sync
```

### Reference Modules

#### `xopt install-config <config.toml>`
Install a reference module that inherits from a base module with custom settings.

```bash
# Create a custom variant
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

# Run the customized module
xopt run "myproject/math-tutor-react" "What is 6 times 8?"
```

## 📁 Project Structure

### Basic Project Setup

```bash
# 1. Initialize project
xopt init

# 2. Edit dependencies
cat > .xopt/deps.toml << EOF
[modules]
"xopt/react" = "0.1.0"
"xopt/calculator" = "0.1.0"

[sources]
"xopt/react" = { path = "examples/modules/react" }
"xopt/calculator" = { path = "examples/modules/calculator" }
EOF

# 3. Install dependencies
xopt sync

# 4. Run modules
xopt run "xopt/react" "Calculate 15% of 240"
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

#### Reference Module Configuration Files
```toml
# math-tutor-react.toml - Custom module variant
[module]
name = "myproject/math-tutor-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = """You are a friendly math tutor for 5th graders..."""

[configurables]
tool_list = ["xopt/calculator:0.1.0"]
```

## 🔧 Module Development

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
xopt package .
xopt install my-org_my-module-1.0.0.xopt
```

## 📖 Examples

### Math Calculation Chain
```bash
xopt run "xopt/react" "First calculate 12 * 15, then find the square root of that result"
```

### Custom Reference Module
```bash
# Create custom React configuration
cat > precise-math-react.toml << EOF
[module]
name = "myproject/precise-math-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "You are a precise mathematician. Always show detailed calculations."

[configurables] 
tool_list = ["xopt/calculator:0.1.0"]
EOF

# Install and run with custom config
xopt install-config precise-math-react.toml
xopt run "myproject/precise-math-react" "What is 25% of 480?"
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
        "xopt", "run", "xopt/react",
        "Calculate the area of a circle with radius 7",
        "-c", json.dumps(config)
    ], capture_output=True, text=True)
    
    print(f"Config {i+1}: {result.stdout}")
```

## 🏗️ Architecture

- 🐍 **Virtual Environment Isolation** - Each module gets its own Python environment (`~/.xopt/modules/`)
- ⚙️ **Process-Level Execution** - Modules run in separate processes for crash safety
- 💾 **Persistent Configuration** - Tunables stored in module directories survive restarts
- 📦 **Dependency Management** - Poetry-style dependency resolution with `.xopt/deps.toml`
- 🔍 **Trace Generation** - Automatic execution tracing for debugging and analysis

## 🛠️ Development

### For Contributors

```bash
# Clone and setup development environment
git clone https://github.com/x-opt/xoptpy
cd xoptpy
poetry install

# Run tests
poetry run pytest

# Test CLI commands
poetry run xopt --help

# Package for distribution  
poetry build
```

### For Users

```bash
# Install from PyPI
pip install xoptpy

# Verify installation
xopt --help
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🐛 Reporting Issues
- Use [GitHub Issues](https://github.com/x-opt/xoptpy/issues) for bug reports
- Include steps to reproduce and system information
- Check existing issues before creating new ones

### 🔧 Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests and ensure they pass
5. Update documentation if needed
6. Submit a pull request

### 📋 Pull Request Guidelines
- Follow the existing code style
- Include tests for new functionality
- Update documentation for user-facing changes
- Keep commits focused and descriptive

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by the xopt team**

[![GitHub stars](https://img.shields.io/github/stars/x-opt/xoptpy.svg?style=social&label=Star)](https://github.com/x-opt/xoptpy)

</div>
