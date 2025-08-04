---
sidebar_position: 1
---

# Introduction to xopt

**xopt** is a modular AI framework that allows you to package, distribute, and run AI modules in isolated virtual environments. Each module can have its own dependencies, configurations, and can automatically discover and use other installed modules as tools.

## What is xopt?

Build and run AI modules with cross-module tool integration in lightweight, isolated environments.

```bash
# Install and run AI modules with isolated dependencies
xopt run "xopt/react" "What is the area of a circle with radius 5?"

# Modules automatically discover and use other installed modules as tools
xopt install xopt_calculator-0.1.0.xopt
xopt run "xopt/react" "Calculate 23 * 47"  # React uses calculator automatically
```

## Why xopt Exists

**The Problem**: AI modules often have conflicting dependencies, require complex setup, and can't be easily customized for different use cases without code changes.

**Our Solution**: Isolated module execution with automatic tool discovery:
- **Package** AI modules with their dependencies in lightweight archives
- **Isolate** execution in virtual environments to prevent conflicts  
- **Discover** other installed modules automatically as tools during runtime
- **Configure** modules through declarative YAML configurations
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

### 🧩 **Cross-Module Tool Integration**
- Modules automatically discover other installed modules as tools
- ReAct reasoning modules can use calculator, search, and other tool modules
- Tool configurations declared in module YAML files
- Runtime module loading ensures all tools are available

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
xopt package examples/modules/calculator
xopt package examples/modules/react
xopt install xopt_calculator-0.1.0.xopt
xopt install xopt_react-0.1.0.xopt

# Run individual modules
xopt run "xopt/calculator" "sqrt(16)"
xopt run "xopt/react" "What is 2 + 2?"

# React automatically uses calculator for math
xopt run "xopt/react" "Calculate the square root of 156"

# List installed modules
xopt list
```

## Next Steps

- [Get Started](./getting-started) - Install and set up xopt
- [CLI Usage](./cli-usage) - Learn the command-line interface
- [Creating Modules](./creating-modules) - Build your own AI modules
- [API Reference](./api/overview) - Complete API documentation
