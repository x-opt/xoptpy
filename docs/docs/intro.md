---
sidebar_position: 1
---

# Introduction to xopt

**xopt** is a modular AI framework that allows you to package, distribute, and run AI modules in isolated virtual environments. Each module can have its own dependencies, configurations, and tunables - perfect for optimization workflows where parameters need to be adjusted between runs.

## What is xopt?

Build and run AI modules in lightweight, isolated environments with persistent configuration.

```bash
# Install and run AI modules with isolated dependencies
xopt run "xopt/react" "What is the area of a circle with radius 5?"

# Create custom module variants with reference configs
xopt install-config math-tutor-react.toml
xopt run "myproject/math-tutor-react" "What is 6 times 8?"
```

## Why xopt Exists

**The Problem**: AI modules often have conflicting dependencies, require complex setup, and can't be easily customized for different use cases without code changes.

**Our Solution**: Isolated module execution with configuration management:
- **Package** AI modules with their dependencies in lightweight archives
- **Isolate** execution in virtual environments to prevent conflicts
- **Customize** modules through reference configs without code changes
- **Optimize** by adjusting tunables between runs for better performance

## Key Features

### 🔧 **Isolated Execution**
```bash
# Each module runs in its own virtual environment
xopt run "xopt/react" "Calculate the square root of 144"
```

### 📦 **Lightweight Packaging**
- Modules packaged as `.xopt` archives (~5-20MB vs 100-500MB containers)
- Virtual environment isolation instead of heavy containerization
- Fast installation and startup times

### 🧩 **Reference Modules**
- Create lightweight variants of existing modules
- Custom tunables and configurations without code duplication
- Inherit from base modules while maintaining isolation

### ⚡ **Optimization Ready**
- Persistent tunables survive between runs
- Modify parameters without reinstalling modules
- Perfect for parameter tuning and optimization workflows

### 🏗️ **Project-Based Dependency Management**
- Declare dependencies in `.xopt/deps.toml`
- Development-friendly source references
- Consistent environments across team members

## Quick Start

### Installation

```bash
pip install xoptpy
```

### Run Your First Module

```bash
# Initialize a project
xopt init

# Package and install example modules
xopt package examples/modules/react
xopt install xopt_react-0.1.0.xopt

# Run the module
xopt run "xopt/react" "What is 2 + 2?"

# List installed modules
xopt list
```

### Create a Custom Module Variant

```bash
# Create a reference module config
cat > math-tutor.toml << EOF
[module]
name = "myproject/math-tutor-react"
base_module = "xopt/react@0.1.0"

[tunables]
react_prompt = "You are a friendly math tutor for students..."
EOF

# Install and run the custom variant
xopt install-config math-tutor.toml
xopt run "myproject/math-tutor-react" "What is 5 times 7?"
```

## Next Steps

- [Get Started](./getting-started) - Install and set up xopt
- [CLI Usage](./cli-usage) - Learn the command-line interface
- [Creating Modules](./creating-modules) - Build your own AI modules
- [API Reference](./api/overview) - Complete API documentation
