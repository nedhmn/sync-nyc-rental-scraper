# Force Git Bash on Windows 
SHELL := C:/Program Files/Git/bin/bash.exe

.PHONY: clean lint help

# Show help by default
.DEFAULT_GOAL := help

# Linting
lint:
	uv run ruff check .
	uv run ruff format .

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Help command
help:
	@echo "Available commands:"
	@echo "  lint         : Run code formatters and linters"
	@echo "  clean        : Remove Python cache files and build artifacts"
