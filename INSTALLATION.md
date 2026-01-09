# Installation Guide for Hierarchical Memory

This guide provides detailed installation instructions for the hierarchical-memory package.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Methods

### Method 1: PyPI Installation (Recommended)

Once published to PyPI:

```bash
# Basic installation
pip install hierarchical-memory

# With vector embeddings support
pip install hierarchical-memory[embeddings]

# With ChromaDB backend
pip install hierarchical-memory[chromadb]

# With FAISS backend
pip install hierarchical-memory[faiss]

# With all optional features
pip install hierarchical-memory[all]
```

### Method 2: Development Installation

For development or testing the latest version:

```bash
# Clone the repository
git clone https://github.com/superinstance/hierarchical-memory.git
cd hierarchical-memory

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e .[dev]
```

### Method 3: From Source Distribution

```bash
# Download source distribution
wget https://github.com/superinstance/hierarchical-memory/archive/v1.0.0.tar.gz

# Extract
tar xzf v1.0.0.tar.gz
cd hierarchical-memory-1.0.0

# Install
pip install .
```

## Dependencies

### Required Dependencies
- **numpy** (>=1.19.0, <2.0.0): Numerical computing

### Optional Dependencies

#### For Vector Embeddings
- **sentence-transformers** (>=2.2.0): Semantic search capabilities

#### For Storage Backends
- **chromadb** (>=0.4.0): Vector database backend
- **faiss-cpu** (>=1.7.0): Efficient similarity search

#### Development Dependencies
- **pytest** (>=7.0.0): Testing framework
- **pytest-cov** (>=4.0.0): Coverage reporting
- **black** (>=23.0.0): Code formatting
- **mypy** (>=1.0.0): Type checking
- **flake8** (>=6.0.0): Linting
- **isort** (>=5.12.0): Import sorting

## Verification

Verify your installation:

```python
# Test import
from hierarchical_memory import HierarchicalMemory

# Check version
import hierarchical_memory
print(hierarchical_memory.__version__)  # Should print: 1.0.0

# Basic functionality test
memory = HierarchicalMemory()
memory.store("test", "value")
result = memory.retrieve("test")
print(result)  # Should print: value
```

## Platform-Specific Notes

### Windows

```cmd
# Use quotes for installation with extras
pip install "hierarchical-memory[all]"

# Activate virtual environment
venv\Scripts\activate
```

### macOS/Linux

```bash
# Standard installation
pip install hierarchical-memory[all]

# Activate virtual environment
source venv/bin/activate
```

### Using system Python on Linux

```bash
# Use pip3 if pip is not available
pip3 install hierarchical-memory

# Or use python3 -m pip
python3 -m pip install hierarchical-memory
```

## Troubleshooting

### Issue: Permission Denied

**Solution**: Use a virtual environment or user installation

```bash
pip install --user hierarchical-memory
```

### Issue: Python Version Too Old

**Solution**: Upgrade Python or use an older version (if available)

```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11

# On macOS with Homebrew
brew install python@3.11
```

### Issue: Build Errors

**Solution**: Install build tools first

```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# On macOS
xcode-select --install

# Then retry installation
pip install hierarchical-memory
```

### Issue: Optional Dependencies Not Installing

**Solution**: Install separately

```bash
pip install hierarchical-memory
pip install sentence-transformers chromadb faiss-cpu
```

## Uninstallation

```bash
pip uninstall hierarchical-memory
```

## Upgrading

```bash
# Upgrade to latest version
pip install --upgrade hierarchical-memory

# Upgrade specific version
pip install hierarchical-memory==1.0.1
```

## Next Steps

After installation:

1. Read the [README.md](README.md) for quick start
2. Check [examples/](examples/) for usage examples
3. Review [API documentation](https://hierarchical-memory.readthedocs.io)
4. Run the example: `python examples/basic_usage.py`

## Getting Help

- **Documentation**: [https://hierarchical-memory.readthedocs.io](https://hierarchical-memory.readthedocs.io)
- **Issues**: [https://github.com/superinstance/hierarchical-memory/issues](https://github.com/superinstance/hierarchical-memory/issues)
- **Email**: contact@superinstance.ai
