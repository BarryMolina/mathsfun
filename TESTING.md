# Testing Guide for MathsFun

This document describes the testing strategy and how to run tests for the MathsFun application.

## Testing Framework

We use **pytest** as our primary testing framework along with supporting libraries:

- **pytest**: Main testing framework
- **pytest-mock**: Simplified mocking for UI interactions
- **pytest-cov**: Test coverage reporting
- **hypothesis**: Property-based testing for mathematical correctness

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test utilities
├── test_ui.py              # UI layer tests with mocking
├── test_session.py         # Session management tests
├── test_addition.py        # Addition logic and problem generation tests
└── test_integration.py     # End-to-end integration tests
```

## Test Categories

### 1. Unit Tests

**Core Logic Tests** (`test_addition.py`, `test_session.py`)
- Problem generation functions
- Mathematical correctness
- Session formatting and results
- Pure functions without side effects

**UI Tests** (`test_ui.py`)
- Input/output behavior using mocks
- User input validation
- Menu display functionality

### 2. Integration Tests (`test_integration.py`)

- Complete user flow scenarios
- Module interaction testing
- Error handling paths
- End-to-end workflows

### 3. Property-Based Tests

Using Hypothesis to test mathematical properties:
- Generated problems are always mathematically correct
- Number ranges match difficulty constraints
- Carrying logic works correctly

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Using the Test Runner

```bash
# Run comprehensive test suite
python run_tests.py
```

### Specific Test Commands

```bash
# Run specific test files
pytest tests/test_ui.py -v
pytest tests/test_addition.py -v
pytest tests/test_session.py -v
pytest tests/test_integration.py -v

# Run tests by category
pytest -m "not slow"           # Skip slow tests
pytest -m "integration"        # Only integration tests
pytest -m "ui"                 # Only UI tests

# Run with different verbosity
pytest -v                      # Verbose
pytest -s                      # Show print statements
pytest --tb=short             # Shorter traceback format
```

## UI Testing Strategy

Testing functions that use `input()` and `print()` requires special handling:

### Mocking Input
```python
def test_user_input(mocker):
    mock_input = mocker.patch('builtins.input', return_value='test')
    result = get_user_input("Prompt")
    assert result == "test"
```

### Capturing Output
```python
def test_print_output(capsys):
    print_welcome()
    captured = capsys.readouterr()
    assert "Welcome to MathsFun" in captured.out
```

### Testing Input Loops
```python
def test_validation_loop(mocker, capsys):
    # Test invalid then valid input
    mock_input = mocker.patch('ui.get_user_input', side_effect=['invalid', 'valid'])
    result = get_difficulty_range()
    # Check error messages appeared
    captured = capsys.readouterr()
    assert "❌ Please enter" in captured.out
```

## Coverage Goals

- **Target**: 100% overall coverage
- **Unit Tests**: 100% coverage for pure logic
- **Integration Tests**: Focus on user flows and error paths
- **UI Tests**: Cover all input/output scenarios

## Test Data and Fixtures

### Shared Fixtures (`conftest.py`)

- `mock_generator`: Mock problem generator for testing
- `unlimited_generator`: Mock unlimited session generator
- `real_generator`: Real generator for integration tests
- `sample_quiz_results`: Standard test data for results

### Custom Test Utilities

- Property-based testing for mathematical correctness
- Parameterized tests for multiple scenarios
- Mock generators with predictable behavior

## Adding New Tests

### For New Features

1. **Unit Tests**: Test the core logic in isolation
2. **UI Tests**: Test user interactions with mocks
3. **Integration Tests**: Test the complete feature flow

### For Bug Fixes

1. Write a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Add edge case tests to prevent regression

## Continuous Integration

The test suite is designed to be run in CI environments:

- All tests should pass consistently
- No external dependencies required
- Fast execution (< 30 seconds for full suite)
- Clear failure messages and diagnostics

## Debugging Tests

```bash
# Run a single test with detailed output
pytest tests/test_ui.py::TestGetUserInput::test_get_user_input_no_default -v -s

# Drop into debugger on failure
pytest --pdb

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest --tb=long
```

## Performance Testing

For performance-sensitive code:

```bash
# Run stress tests (marked as slow)
pytest -m slow

# Profile test execution
pytest --durations=10
```

This testing strategy ensures comprehensive coverage while maintaining fast, reliable test execution.