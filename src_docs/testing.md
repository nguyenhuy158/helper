# Testing Guide

## Overview
This document outlines the testing strategy and conventions for the Helper CLI project.

## Testing Framework
The project uses pytest for unit testing with the following plugins:
- pytest-mock for mocking dependencies
- pytest for test discovery and execution

## Test Structure
Tests are organized in the `tests/` directory with the following structure:
- `tests/commands/` - Tests for CLI command modules
- `tests/conftest.py` - Shared test fixtures and configuration

## Test Conventions

### File Naming
- Test files follow the pattern `test_*.py`
- Test classes follow the pattern `Test*`
- Test methods follow the pattern `test_*`

### Documentation Standards
All test classes and methods must include comprehensive docstrings that explain:
- The purpose of the test
- The scenario being tested
- Expected inputs and outputs
- Edge cases and error conditions

### Mocking Strategy
- Use `unittest.mock.patch` for external dependencies
- Mock subprocess calls, network requests, and system interactions
- Ensure mocks accurately represent real behavior

### Assertion Patterns
- Test both success and error paths
- Verify return values, side effects, and error handling
- Use descriptive assertion messages

## Running Tests
```bash
# Run all tests
make test

# Run specific test file
pytest tests/commands/test_arch.py

# Run with coverage
pytest --cov=helper
```

## Test Categories
- Unit tests for individual functions
- Integration tests for command execution
- Error handling tests for edge cases
- Mock-based tests for external dependencies
