.PHONY: help install install-dev test lint format type-check clean build upload docs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"
	pre-commit install

install-all: ## Install the package with all optional dependencies
	pip install -e ".[all,dev]"
	pre-commit install

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=hierarchical_memory --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 hierarchical_memory/
	isort --check-only hierarchical_memory/

format: ## Format code with black and isort
	black hierarchical_memory/
	isort hierarchical_memory/

type-check: ## Run type checking with mypy
	mypy hierarchical_memory/

check: lint type-check test ## Run all checks (lint, type-check, test)

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	python -m build

upload: build ## Upload to PyPI (requires credentials)
	twine upload dist/*

upload-test: build ## Upload to Test PyPI
	twine upload --repository testpypi dist/

docs: ## Build documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs && make livehtml

example: ## Run basic example
	python examples/basic_usage.py
