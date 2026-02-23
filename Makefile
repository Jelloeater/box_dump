.PHONY: help install test lint format clean

help:
	@echo "Available targets:"
	@echo "  install  - Install package with dev dependencies"
	@echo "  test     - Run tests"
	@echo "  lint     - Run ruff linter"
	@echo "  format   - Format code"
	@echo "  clean    - Remove build artifacts"

install:
	uv pip install -e ".[dev,viewer]"

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
