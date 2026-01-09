# Hierarchical Memory Test Suite

Comprehensive test suite for the hierarchical-memory package with 80%+ coverage target.

## Test Structure

### Test Files

- **test_working_memory.py** - Tests for working memory (capacity, decay, eviction)
- **test_episodic_memory.py** - Tests for episodic memory (CRUD, search, consolidation)
- **test_semantic_memory.py** - Tests for semantic memory (concepts, facts, vector DB)
- **test_procedural_memory.py** - Tests for procedural memory (skills, practice, forgetting)
- **test_consolidation.py** - Tests for consolidation pipeline (KL divergence, extraction)
- **test_retrieval.py** - Tests for retrieval system (all 6 search modes)
- **test_sharing.py** - Tests for memory sharing (conflict resolution, sync)
- **test_integration.py** - Integration tests (full system workflows)

### Configuration Files

- **conftest.py** - Shared pytest fixtures and configuration
- **pytest.ini** - Pytest configuration with coverage settings

## Running Tests

### Run All Tests

```bash
# Using the test runner
python run_tests.py

# Using pytest directly
pytest tests/

# With verbose output
pytest tests/ -v
```

### Run Specific Test File

```bash
# Using test runner
python run_tests.py -f test_working_memory.py

# Using pytest
pytest tests/test_working_memory.py
```

### Run Tests by Marker

```bash
# Run only working memory tests
pytest tests/ -m working

# Run only integration tests
pytest tests/ -m integration

# Run only fast unit tests
pytest tests/ -m "not slow"
```

### Generate Coverage Report

```bash
# Using test runner
python run_tests.py --coverage

# Using pytest
pytest --cov=hierarchical_memory --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

- `working_memory` - Fresh working memory instance
- `episodic_memory` - Fresh episodic memory instance
- `semantic_memory` - Fresh semantic memory instance
- `procedural_memory` - Fresh procedural memory instance
- `consolidation_pipeline` - Pipeline with all memory systems
- `memory_retrieval` - Retrieval system with all tiers
- `populated_*_memory` - Pre-populated memory instances with test data

## Test Categories

### Unit Tests

Fast, isolated tests for individual components:
- Basic CRUD operations
- Data validation
- Edge cases

Run with: `pytest -m unit`

### Integration Tests

Slower tests that verify cross-component functionality:
- Consolidation workflows
- Multi-tier retrieval
- Memory sharing

Run with: `pytest -m integration`

## Coverage Goals

The test suite targets 80%+ code coverage:

- **Working Memory**: Capacity, decay, eviction, priority
- **Episodic Memory**: Storage, search by time/location/emotion
- **Semantic Memory**: Concepts, facts, similarity search
- **Procedural Memory**: Skills, practice, forgetting curves
- **Consolidation**: KL divergence, batch consolidation
- **Retrieval**: 6 search modes, multi-tier queries
- **Sharing**: Trust-based sharing, conflict resolution

## Writing New Tests

1. Add test functions to appropriate test file
2. Use descriptive names: `test_<functionality>_<scenario>`
3. Use fixtures from `conftest.py` when possible
4. Add markers for categorization: `@pytest.mark.working`
5. Include docstrings explaining what is being tested

Example:
```python
@pytest.mark.working
def test_capacity_enforcement(working_memory):
    """Test that working memory respects capacity limit."""
    wm = working_memory
    for i in range(25):  # Exceeds capacity of 20
        wm.add(f"Task {i}", importance=5.0)
    assert len(wm) == 20
```

## Continuous Integration

The test suite is configured for CI/CD with:

- Automated test execution on push
- Coverage reporting
- Coverage threshold enforcement (80%)
- Test result reporting

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:
```bash
pip install -e .
```

### Coverage Not Generated

Install pytest-cov:
```bash
pip install pytest-cov
```

### Tests Failing Due to Time

Some tests check for time differences. If these fail on slow systems:
- The tests use small delays (0.01s) to avoid flakiness
- If still failing, the time threshold may need adjustment

## Test Statistics

To see statistics about the test suite:

```bash
pytest tests/ --collect-only
```

This will show:
- Total number of tests
- Tests per module
- Test markers

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Add integration tests for cross-component features
5. Update this README if needed
