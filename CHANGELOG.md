# Changelog

All notable changes to the hierarchical-memory package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of hierarchical-memory package
- 4-tier memory architecture (Immediate, Working, Episodic, Semantic)
- Vector embedding support with sentence-transformers
- Pluggable backend system (in-memory, ChromaDB, FAISS)
- Automatic memory consolidation and compression
- Thread-safe operations
- Full type annotations
- Comprehensive test suite
- Documentation and examples

## [1.0.0] - 2024-01-15

### Added
- Initial public release
- HierarchicalMemory class with full 4-tier architecture
- ImmediateMemory, WorkingMemory, EpisodicMemory, and SemanticMemory tiers
- Vector embedding integration for semantic search
- Multiple storage backends (InMemoryBackend, ChromaDBBackend, FAISSBackend)
- Consolidation strategies for memory compression
- Comprehensive API for memory operations (store, retrieve, search, delete)
- Metadata support for all memory operations
- Semantic search functionality
- Time-based retrieval
- Memory statistics and monitoring
- Full Python type hints
- pytest-based test suite with 90%+ coverage
- Documentation with Sphinx
- Example usage scripts
- CI/CD workflows
- Pre-commit hooks for code quality
- Black, isort, mypy, flake8 configurations

[Unreleased]: https://github.com/superinstance/hierarchical-memory/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/superinstance/hierarchical-memory/releases/tag/v1.0.0
