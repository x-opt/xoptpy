# Makefile for xopt development and installation

.PHONY: help install update build-exe install-exe clean test lint dev-test check-deps version

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install xopt in development mode"
	@echo "  update        - Update local xopt command (rebuild and install to ~/.local/bin)"
	@echo "  build-exe     - Build standalone executable with PyInstaller"
	@echo "  install-exe   - Build and install standalone executable to ~/.local/bin"
	@echo "  install-system- Install standalone executable to /usr/local/bin (requires sudo)"
	@echo "  uninstall     - Remove installed xopt command"
	@echo "  clean         - Clean build artifacts"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  dev-test      - Test xopt command in development mode"
	@echo "  check-deps    - Check if required tools are installed"
	@echo "  version       - Show current version info"

# Check dependencies
check-deps:
	@echo "🔍 Checking dependencies..."
	@command -v poetry >/dev/null 2>&1 || { echo "❌ Poetry not installed. Install with: curl -sSL https://install.python-poetry.org | python3 -"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not installed"; exit 1; }
	@echo "✅ All dependencies found"

# Install in development mode
install: check-deps
	@echo "📦 Installing xopt in development mode..."
	poetry install
	@echo "✅ Development installation complete"
	@echo "Run 'poetry run python -m xopt.cli --help' to test"

# Update the local xopt command (rebuild everything)
update: clean build-exe install-exe
	@echo "🎉 xopt command updated successfully!"
	@echo "📍 Installed location: ~/.local/bin/xopt"
	@echo "🚀 Run 'xopt --help' to verify installation"

# Build standalone executable
build-exe: check-deps
	@echo "🔨 Building standalone executable..."
	@if ! poetry run python -c "import PyInstaller" 2>/dev/null; then \
		echo "📦 Installing PyInstaller..."; \
		poetry add --group dev pyinstaller; \
	fi
	poetry run pyinstaller --onefile --name xopt xopt/cli.py
	@echo "✅ Executable built at dist/xopt"
	@ls -lh dist/xopt

# Install the standalone executable
install-exe:
	@echo "📥 Installing xopt executable..."
	@if [ ! -f dist/xopt ]; then \
		echo "❌ Executable not found. Run 'make build-exe' first"; \
		exit 1; \
	fi
	@mkdir -p ~/.local/bin
	@if [ -f ~/.local/bin/xopt ]; then \
		echo "⚠️  Backing up existing xopt to ~/.local/bin/xopt.backup"; \
		cp ~/.local/bin/xopt ~/.local/bin/xopt.backup; \
	fi
	cp dist/xopt ~/.local/bin/xopt
	chmod +x ~/.local/bin/xopt
	@echo "✅ xopt installed to ~/.local/bin/xopt"
	@if echo "$$PATH" | grep -q "$$HOME/.local/bin"; then \
		echo "✅ ~/.local/bin is in PATH"; \
	else \
		echo "⚠️  ~/.local/bin is not in PATH. Add this to your shell profile:"; \
		echo "     export PATH=\"\$$HOME/.local/bin:\$$PATH\""; \
	fi
	@~/.local/bin/xopt --help >/dev/null && echo "🚀 Installation verified successfully" || echo "❌ Installation verification failed"

# Install to system (requires sudo)
install-system:
	@echo "📥 Installing xopt executable to system..."
	@if [ ! -f dist/xopt ]; then \
		echo "❌ Executable not found. Run 'make build-exe' first"; \
		exit 1; \
	fi
	@if [ -f /usr/local/bin/xopt ]; then \
		echo "⚠️  Backing up existing xopt to /usr/local/bin/xopt.backup"; \
		sudo cp /usr/local/bin/xopt /usr/local/bin/xopt.backup; \
	fi
	sudo cp dist/xopt /usr/local/bin/xopt
	sudo chmod +x /usr/local/bin/xopt
	@echo "✅ xopt installed to /usr/local/bin/xopt"
	@/usr/local/bin/xopt --help >/dev/null && echo "🚀 Installation verified successfully" || echo "❌ Installation verification failed"

# Uninstall xopt command
uninstall:
	@echo "🗑️  Removing xopt command..."
	@if [ -f ~/.local/bin/xopt ]; then \
		rm ~/.local/bin/xopt; \
		echo "✅ xopt removed from ~/.local/bin/xopt"; \
	elif [ -f /usr/local/bin/xopt ]; then \
		sudo rm /usr/local/bin/xopt; \
		echo "✅ xopt removed from /usr/local/bin/xopt"; \
	else \
		echo "ℹ️  xopt not found in ~/.local/bin or /usr/local/bin"; \
	fi
	@if [ -f ~/.local/bin/xopt.backup ]; then \
		echo "📁 Backup found at ~/.local/bin/xopt.backup"; \
	elif [ -f /usr/local/bin/xopt.backup ]; then \
		echo "📁 Backup found at /usr/local/bin/xopt.backup"; \
	fi

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.spec
	rm -rf __pycache__/
	rm -rf **/__pycache__/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf **/.pytest_cache/
	find . -name "*.pyc" -delete
	@echo "✅ Cleaned"

# Run tests
test: check-deps
	@echo "🧪 Running tests..."
	@if [ ! -d tests ]; then \
		echo "📁 No tests directory found, creating basic test..."; \
		mkdir -p tests; \
		echo "def test_import():\n    import xopt.cli\n    assert True" > tests/test_basic.py; \
	fi
	poetry run python -m pytest tests/ -v

# Run linting (install tools if needed)
lint: check-deps
	@echo "🔍 Running linting..."
	@if ! poetry run python -c "import ruff" 2>/dev/null; then \
		echo "📦 Installing ruff..."; \
		poetry add --group dev ruff; \
	fi
	poetry run ruff check .
	@echo "✅ Linting complete"

# Quick development test
dev-test: check-deps
	@echo "🚀 Testing xopt command in development mode..."
	@poetry run python -m xopt.cli --help
	@echo "✅ Development test complete"

# Show version information
version:
	@echo "📊 Version Information:"
	@echo "Python: $$(python3 --version)"
	@echo "Poetry: $$(poetry --version)"
	@if [ -f pyproject.toml ]; then \
		echo "xopt: $$(grep '^version' pyproject.toml | cut -d'"' -f2)"; \
	fi
	@if command -v xopt >/dev/null 2>&1; then \
		echo "Installed xopt: $$(xopt --help 2>&1 | head -1 || echo 'Version not available')"; \
	else \
		echo "Installed xopt: Not found in PATH"; \
	fi

# Quick development workflow
dev: clean install dev-test
	@echo "🎉 Development setup complete!"