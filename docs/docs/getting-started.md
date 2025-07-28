---
sidebar_position: 2
---

# Getting Started

This guide will help you install and start using xopt to manage AI modules and tools.

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

You should see the xopt CLI help message with available commands.

## Basic Usage

### Health Check

First, check if the xopt registry API is accessible:

```bash
xopt health
```

### Search for Components

Search for existing modules and tools in the registry:

```bash
# Search for sentiment analysis modules
xopt search components "sentiment"

# Search only for modules
xopt search components "sentiment" --type module

# Search only for tools
xopt search components "validation" --type tool
```

### Working with Modules

#### Upload a Module

Create a module manifest file (YAML format) and upload it:

```bash
xopt module upload my_module.yaml
```

#### List Module Versions

```bash
xopt module list-versions namespace module-name
```

#### Get Module Information

```bash
# Get module manifest
xopt module get-manifest namespace module-name version

# Get module dependencies
xopt module get-dependencies namespace module-name version

# Get usage statistics
xopt module get-stats namespace module-name
```

## Configuration

### Environment Variables

Set these environment variables to configure xopt:

```bash
export XOPTPY_BASE_URL="http://localhost:8080"
export XOPTPY_TIMEOUT=30
export XOPTPY_LOG_LEVEL="INFO"
```

### Configuration File

Create a `xoptpy.json` file in your project directory:

```json
{
  "base_url": "http://localhost:8080",
  "timeout": 30,
  "log_level": "INFO"
}
```

### Command Line Options

Override configuration on the command line:

```bash
# Override base URL
xopt --base-url "http://other-server:8080" health

# Set timeout
xopt --timeout 60 search components "sentiment"

# Enable verbose logging
xopt --verbose health
```

## Next Steps

- [CLI Usage Guide](./cli-usage) - Detailed CLI command reference
- [Creating Modules](./creating-modules) - Learn how to build and publish modules
- [Working with Tools](./working-with-tools) - Manage AI tools and agents
- [API Reference](./api/overview) - Complete API documentation