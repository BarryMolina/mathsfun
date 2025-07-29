# MathsFun Test Infrastructure

This document describes the comprehensive test infrastructure for the MathsFun application, including the centralized user management system and test categorization.

## Overview

The test infrastructure provides:

- **Centralized user management** for integration testing
- **Automatic test categorization** with pytest markers
- **Comprehensive cleanup mechanisms** for reliable test execution
- **Support for multiple test layers** (automation, service, repository)
- **Session-scoped resource management** with proper isolation

## Test Categories

### Pytest Markers

Tests are automatically categorized using pytest markers:

- `@pytest.mark.automation` - pexpect-based CLI automation tests
- `@pytest.mark.service` - Service layer integration tests  
- `@pytest.mark.repository` - Repository layer integration tests
- `@pytest.mark.integration` - End-to-end integration tests
- `@pytest.mark.database` - Database-specific integration tests
- `@pytest.mark.slow_integration` - Slow-running integration tests
- `@pytest.mark.requires_local_supabase` - Tests requiring local Supabase instance

### Running Tests by Category

```bash
# Run all tests (excludes automation by default)
pytest

# Run only automation tests
pytest -m automation

# Run service layer integration tests
pytest -m service

# Run repository layer tests
pytest -m repository

# Run all integration tests (excluding automation)
pytest -m "integration and not automation"

# Run both service and repository tests
pytest -m "service or repository"

# Run everything except slow tests
pytest -m "not slow_integration"
```

## Test User Management

### Centralized User Manager

The `TestUserManager` provides centralized user lifecycle management for integration testing:

```python
from tests.fixtures.user_manager import TestUserManager, TestUserCategory

# Create user manager
manager = TestUserManager(environment="local")

# Create users for specific categories
users = manager.create_test_users([TestUserCategory.SERVICE])

# Get user for testing
user = manager.get_test_user(TestUserCategory.AUTOMATION)

# Reset user state between tests
manager.reset_user_state(user["email"])

# Cleanup users after testing
manager.cleanup_test_users()
```

### Available Test Users

Each category has dedicated test users:

**Automation Users:**
- `automation.primary@mathsfun.test` - Primary CLI testing
- `automation.secondary@mathsfun.test` - Secondary user scenarios
- `automation.signup@mathsfun.test` - Signup flow testing

**Service Users:**
- `service.test.user@mathsfun.test` - General service testing
- `service.quiz.user@mathsfun.test` - Quiz-specific testing

**Repository Users:**
- `repo.test.user@mathsfun.test` - General repository testing
- `repo.edge.case@mathsfun.test` - Edge case testing

**Integration Users:**
- `integration.flow@mathsfun.test` - End-to-end flow testing

## Test Fixtures

### Session-Scoped Fixtures

```python
def test_example(test_user_manager, session_test_users):
    """Test using session-scoped user management."""
    # Users are created once per session and shared
    automation_users = session_test_users[TestUserCategory.AUTOMATION]
```

### Function-Scoped Fixtures

```python
def test_service_logic(service_test_user):
    """Test using clean service user."""
    # User state is reset before each test
    assert service_test_user["email"] == "service.test.user@mathsfun.test"

def test_automation_flow(automation_test_users):
    """Test using automation users."""
    primary = automation_test_users["primary"]
    secondary = automation_test_users["secondary"]
```

## Writing Integration Tests

### Service Layer Tests

```python
# tests/integration/service/test_my_service.py
import pytest

@pytest.mark.service
@pytest.mark.integration
class TestMyServiceIntegration:
    def test_business_logic(self, service_test_user):
        # Test service layer with real database
        pass
```

### Repository Layer Tests

```python
# tests/integration/repository/test_my_repo.py
import pytest

@pytest.mark.repository
@pytest.mark.database
@pytest.mark.integration
class TestMyRepositoryIntegration:
    def test_crud_operations(self, repository_test_user):
        # Test data access with real database
        pass
```

### Automation Tests

```python
# tests/automation/test_cli_flow.py
import pytest

@pytest.mark.automation
class TestCLIFlow:
    def test_user_journey(self, navigator, automation_test_users):
        # Test CLI automation with pexpect
        primary_user = automation_test_users["primary"]
        # ...
```

## Cleanup and Resource Management

### Automatic Cleanup

The test infrastructure provides automatic cleanup via the cleanup plugin:

- **Process cleanup** - Terminates test processes (pexpect, etc.)
- **User cleanup** - Removes test users after session
- **File cleanup** - Removes temporary files
- **Environment cleanup** - Resets test environment variables

### Manual Cleanup Tracking

```python
def test_with_cleanup(cleanup_tracker):
    """Test that tracks resources for cleanup."""
    
    # Track temporary file
    temp_file = "/tmp/test_file.txt"
    cleanup_tracker.track_file(temp_file)
    
    # Track process
    import subprocess
    proc = subprocess.Popen(["sleep", "10"])
    cleanup_tracker.track_process(proc.pid)
    
    # Register custom cleanup
    def custom_cleanup():
        print("Custom cleanup executed")
    cleanup_tracker.register_hook(custom_cleanup)
```

### Emergency Cleanup

The system performs emergency cleanup when:
- Tests fail unexpectedly
- Processes are left running
- Test session exits with errors

## Environment Setup

### Local Supabase

Tests require local Supabase instance:

```bash
# Start local Supabase
supabase start

# Run integration tests
pytest -m integration

# Stop local Supabase
supabase stop
```

### Environment Variables

The following environment variables are automatically set for tests:

- `MATHSFUN_TEST_MODE=1` - Enables test mode (bypasses getpass)
- `ENVIRONMENT=local` - Uses local Supabase configuration

## Best Practices

### Test Isolation

- Use function-scoped fixtures for test isolation
- Reset user state between tests
- Avoid shared mutable state between tests

### Performance

- Use session-scoped fixtures for expensive setup
- Batch user creation for better performance
- Use appropriate test markers to run only needed tests

### Reliability

- Handle test failures gracefully
- Provide clear error messages
- Use automatic cleanup for consistent state

### Debugging

- Enable verbose logging for troubleshooting
- Use test markers to isolate problem areas
- Check cleanup logs for resource leaks

## Troubleshooting

### Common Issues

**"Local Supabase not available"**
- Ensure `supabase start` is running
- Check local Supabase health at http://127.0.0.1:54321

**"Test user not available"**
- Verify user manager initialization
- Check local Supabase connectivity
- Review user creation logs

**"Authentication failed"**
- Verify test users exist in database
- Check user credentials in fixtures
- Reset user state between tests

**"Process cleanup warnings"**
- Normal for pexpect-based tests
- Check for orphaned processes: `ps aux | grep python`
- Restart if processes accumulate

### Debugging Commands

```bash
# Run with verbose output
pytest -v -s

# Run specific test category with logging
pytest -m service --log-cli-level=INFO

# Run single test with maximum detail
pytest -v -s tests/integration/service/test_user_service_integration.py::TestUserServiceIntegration::test_user_profile_creation_and_retrieval

# Check test markers
pytest --markers

# Dry run to see test collection
pytest --collect-only
```