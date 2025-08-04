# Development Guide

This guide covers how to develop and maintain the xopt CLI tool.

## Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Make (for build automation)

## Quick Start

```bash
# Install dependencies and set up development environment
make install

# Test in development mode
make dev-test

# Build and install standalone executable
make update
```

## Makefile Commands

The project includes a comprehensive Makefile for common development tasks:

### Installation Commands

- `make install` - Install xopt in development mode using Poetry
- `make update` - Complete update workflow: clean → build → install standalone executable
- `make build-exe` - Build standalone executable using PyInstaller
- `make install-exe` - Install standalone executable to `~/.local/bin/xopt`
- `make install-system` - Install standalone executable to `/usr/local/bin/xopt` (requires sudo)

### Development Commands

- `make dev-test` - Test xopt command in development mode
- `make test` - Run test suite (creates basic tests if none exist)
- `make lint` - Run code linting with ruff
- `make clean` - Clean all build artifacts
- `make dev` - Complete development setup: clean → install → test

### Utility Commands

- `make check-deps` - Verify required tools (Python, Poetry) are installed
- `make version` - Show version information for Python, Poetry, and xopt
- `make uninstall` - Remove installed xopt command from system
- `make help` - Show all available commands

## Development Workflow

### 1. Initial Setup

```bash
# Clone and set up the project
git clone <repository>
cd xoptpy
make install
```

### 2. Making Changes

```bash
# Make your code changes
# Test in development mode
make dev-test

# Run tests and linting
make test
make lint
```

### 3. Installing Updated CLI

```bash
# Quick update (recommended)
make update

# Or step by step
make clean
make build-exe
make install-exe
```

### 4. Testing Installation

```bash
# Verify installation
xopt --help
xopt list

# Check version info
make version
```

## File Structure

```
xoptpy/
├── xopt/                   # Main package
│   ├── cli.py             # CLI entry point
│   ├── client.py          # Core client functionality
│   ├── runner.py          # Module execution engine
│   └── commands/          # Individual CLI commands
├── examples/              # Example modules
├── Makefile              # Build automation
├── pyproject.toml        # Poetry configuration
└── README.md             # User documentation
```

## Installation Locations

- **Development mode**: Uses Poetry virtual environment
- **User installation**: `~/.local/bin/xopt` (no sudo required)
- **System installation**: `/usr/local/bin/xopt` (requires sudo)

The Makefile automatically handles PATH configuration and creates backups of existing installations.

## Troubleshooting

### Command not found after installation

If `xopt` command is not found, ensure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission errors

Use `make install-exe` (user installation) instead of `make install-system` to avoid sudo requirements.

### Build failures

Run `make check-deps` to verify all required tools are installed.

### Clean rebuild

```bash
make clean
make update
```