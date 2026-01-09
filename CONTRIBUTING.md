# Contributing to Hierarchical Memory

Thank you for your interest in contributing to Hierarchical Memory! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and its contributors are expected to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to contact@superinstance.ai.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**: Explain the problem clearly
- **Steps to reproduce**: Provide minimal reproducible example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, package version
- **Logs/error messages**: Full traceback if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear and descriptive title
- Provide a detailed explanation of the enhancement
- Explain why it would be useful to most users
- List examples or use cases
- Include implementation ideas if applicable

### Pull Requests

1. **Fork and clone** the repository
2. **Create a branch** for your work: `git checkout -b feature/your-feature-name`
3. **Make your changes** following our coding standards
4. **Write tests** for your changes
5. **Ensure all tests pass**: `pytest`
6. **Format your code**: `black hierarchical_memory/`
7. **Check types**: `mypy hierarchical_memory/`
8. **Commit your changes** with clear messages
9. **Push to your fork**: `git push origin feature/your-feature-name`
10. **Create a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/superinstance/hierarchical-memory.git
cd hierarchical-memory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hierarchical_memory --cov-report=html

# Run specific test file
pytest tests/test_memory.py

# Run with markers
pytest -m unit
pytest -m "not slow"
```

### Code Quality

```bash
# Format code
black hierarchical_memory/

# Sort imports
isort hierarchical_memory/

# Type checking
mypy hierarchical_memory/

# Linting
flake8 hierarchical_memory/

# Run all checks at once
pre-commit run --all-files
```

## Coding Standards

### Style Guide

- Follow **PEP 8** style guide
- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use **type hints** for all functions and methods
- Write **docstrings** for all public modules, classes, and functions (Google style)

### Documentation

```python
def store(self, key: str, value: Any, **kwargs) -> bool:
    """Store a value in the memory system.

    Args:
        key: The unique identifier for the memory
        value: The value to store
        **kwargs: Additional options (metadata, tier, etc.)

    Returns:
        True if the value was stored successfully

    Raises:
        ValueError: If the key is invalid

    Example:
        >>> memory.store("user", "Alice")
        True
    """
```

### Naming Conventions

- **Modules**: `lowercase_with_underscores`
- **Classes**: `CapitalizedWords`
- **Functions/Methods**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`

### Testing

- Write tests for all new functionality
- Maintain >90% code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Use fixtures for common setup

```python
def test_retrieve_stored_memory(memory):
    """Test retrieving a previously stored memory."""
    # Arrange
    memory.store("key", "value")

    # Act
    result = memory.retrieve("key")

    # Assert
    assert result == "value"
```

## Project Structure

```
hierarchical-memory/
├── hierarchical_memory/
│   ├── __init__.py
│   ├── core.py
│   ├── backends/
│   ├── consolidation/
│   └── utils.py
├── tests/
│   ├── test_core.py
│   ├── test_backends.py
│   └── test_consolidation.py
├── examples/
├── docs/
├── README.md
├── setup.py
├── pyproject.toml
└── CHANGELOG.md
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add FAISS backend support
fix: resolve race condition in memory consolidation
docs: update API documentation
test: add integration tests for ChromaDB backend
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code passes all tests
- [ ] Code is formatted with Black
- [ ] Type checking passes with mypy
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] PR description clearly explains changes

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Release Process

Releases are managed by the maintainers:

1. Update version in `__init__.py`
2. Update `CHANGELOG.md`
3. Create git tag
4. Build and publish to PyPI
5. Create GitHub release

## Questions?

Feel free to open an issue or contact us at contact@superinstance.ai.

Thank you for your contributions!
