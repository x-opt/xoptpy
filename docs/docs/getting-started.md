---
sidebar_position: 2
---

# Getting Started

This guide will help you install and start using xopt to package, install, and run AI modules in isolated environments.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install xoptpy

```bash
pip install xoptpy
```

This installs the `xopt` command-line tool globally on your system.

### Verify Installation

Check that xopt is installed correctly:

```bash
xopt --help
```

You should see the xopt CLI help message with available commands:
- `package` - Package a module directory
- `install` - Install a module package
- `install-config` - Install a reference module
- `run` - Run an installed module
- `list` - List installed modules
- `init` - Initialize a project
- `sync` - Install project dependencies

## Basic Usage

### Initialize a Project

Start by initializing a new xopt project:

```bash
xopt init
```

This creates a `.xopt/` directory with `deps.toml` for dependency management.

### Package Example Modules

Package the included example modules:

```bash
# Package React reasoning module
xopt package examples/modules/react

# Package Calculator module
xopt package examples/modules/calculator
```

This creates `.xopt` archive files that can be installed.

### Install Modules

Install the packaged modules:

```bash
xopt install xopt_react-0.1.0.xopt
xopt install xopt_calculator-0.1.0.xopt
```

Each module gets its own isolated virtual environment with dependencies.

### Run Modules

Execute installed modules:

```bash
# Run calculator module
xopt run "xopt/calculator" "sqrt(16) + 2 * pi"

# Run React reasoning module
xopt run "xopt/react" "What is the area of a circle with radius 5?"

# List all installed modules
xopt list
```

### Create Reference Modules

Create lightweight variants with custom configurations:

```bash
# Create a custom configuration
cat > math-tutor.toml << EOF
[module]
name = "myproject/math-tutor-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "You are a helpful math tutor. Show your work step by step."

[configurables]
tool_list = ["xopt/calculator:0.1.0"]
EOF

# Install the reference module
xopt install-config math-tutor.toml

# Run with custom behavior
xopt run "myproject/math-tutor-react" "What is 15% of 240?"
```

## Project Configuration

### Dependency Management

Use `.xopt/deps.toml` to declare project dependencies:

```toml
[modules]
"xopt/react" = "0.1.0"
"xopt/calculator" = "0.1.0"

# For development - reference local source
[sources]
"xopt/react" = { path = "examples/modules/react" }
"xopt/calculator" = { path = "examples/modules/calculator" }
```

### Installing Project Dependencies

```bash
# Install all declared dependencies
xopt sync
```

### Development Workflow

For development, you can run modules directly without packaging:

```bash
# Run from development directory
xopt dev examples/modules/react "xopt/react" "What is 2+2?"
```

### Module Storage

Modules are installed to `~/.xopt/modules/` with isolated virtual environments:

```
~/.xopt/modules/
├── xopt_react/
│   ├── venv/          # Virtual environment
│   ├── react.py       # Module code
│   └── xopt.yaml      # Module configuration
└── xopt_calculator/
    ├── venv/
    ├── calculator.py
    └── xopt.yaml
```

## Next Steps

- [CLI Usage Guide](./cli-usage) - Detailed CLI command reference
- [Creating Modules](./creating-modules) - Learn how to build and publish modules
- [Working with Tools](./working-with-tools) - Manage AI tools and agents
- [API Reference](./api/overview) - Complete API documentation