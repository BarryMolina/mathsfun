#!/usr/bin/env python3
"""Shared test fixtures and utilities for MathsFun tests."""

import pytest
import logging
from unittest.mock import Mock
from src.presentation.controllers.addition import ProblemGenerator

# Import fixtures from fixtures module
from tests.fixtures.user_fixtures import *
from tests.fixtures.user_manager import TestUserManager, TestUserCategory, create_test_user_manager

# Enable comprehensive cleanup plugin
pytest_plugins = ["tests.fixtures.cleanup_plugin"]


@pytest.fixture
def mock_generator():
    """Create a mock problem generator for testing."""
    generator = Mock()
    generator.is_unlimited = False
    generator.num_problems = 5
    generator.get_total_generated.return_value = 3
    return generator


@pytest.fixture
def unlimited_generator():
    """Create a mock unlimited problem generator for testing."""
    generator = Mock()
    generator.is_unlimited = True
    generator.get_total_generated.return_value = 10
    return generator


@pytest.fixture
def real_generator():
    """Create a real problem generator for integration tests."""
    return ProblemGenerator(low_difficulty=1, high_difficulty=2, num_problems=3)


@pytest.fixture
def sample_quiz_results():
    """Sample quiz results for testing result display."""
    return {
        "correct": 8,
        "total": 10,
        "duration": 125.5,  # 2m 5.5s
    }


# ============================================================================
# Integration Test User Management Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_user_manager():
    """
    Session-scoped test user manager for integration testing.
    
    Provides centralized user management across all integration test types
    including automation, service layer, and repository layer tests.
    
    The manager handles user creation, cleanup, and state management.
    """
    # Set up logging for test user manager
    logging.basicConfig(level=logging.INFO)
    
    manager = create_test_user_manager(environment="local")
    
    yield manager
    
    # Session cleanup - remove all users created during this test session
    try:
        manager.cleanup_session_users()
    except Exception as e:
        print(f"Warning: Failed to cleanup session users: {e}")


@pytest.fixture(scope="session") 
def session_test_users(test_user_manager):
    """
    Session-scoped fixture that creates all default test users.
    
    Creates users for all categories and keeps them available throughout
    the entire test session. Users are cleaned up at session end.
    
    Returns:
        Dictionary mapping TestUserCategory to lists of user data
    """
    # Check if local Supabase is available
    if not test_user_manager.is_local_supabase_available():
        pytest.skip("Local Supabase not available - skipping integration tests")
    
    # Create all default test users
    created_users = test_user_manager.create_test_users()
    
    return created_users


@pytest.fixture(scope="function")
def clean_test_user(test_user_manager):
    """
    Function-scoped fixture providing a clean test user for individual tests.
    
    The user's state is reset before each test to ensure isolation.
    This fixture is suitable for tests that need a dedicated, clean user.
    
    Returns:
        Test user data for automation category (primary user)
    """
    # Get primary automation user for individual test use
    user_data = test_user_manager.get_test_user(TestUserCategory.AUTOMATION, index=0)
    
    if user_data:
        # Reset user state to clean condition
        test_user_manager.reset_user_state(user_data["email"])
    
    return user_data


@pytest.fixture(scope="function")
def automation_test_users(test_user_manager):
    """
    Function-scoped fixture providing automation test users.
    
    Returns all automation test users with clean state for CLI testing.
    
    Returns:
        Dictionary with automation user data (primary, secondary, signup)
    """
    users = test_user_manager.get_all_test_users(TestUserCategory.AUTOMATION)
    
    # Reset state for all automation users
    for user in users:
        test_user_manager.reset_user_state(user["email"])
    
    # Return as dictionary for easy access
    return {
        "primary": users[0] if len(users) > 0 else None,
        "secondary": users[1] if len(users) > 1 else None,
        "signup": users[2] if len(users) > 2 else None,
    }


@pytest.fixture(scope="function")
def service_test_user(test_user_manager):
    """
    Function-scoped fixture providing a service layer test user.
    
    Suitable for testing business logic and service layer integration.
    User state is reset before each test.
    
    Returns:
        Service test user data
    """
    user_data = test_user_manager.get_test_user(TestUserCategory.SERVICE, index=0)
    
    if user_data:
        test_user_manager.reset_user_state(user_data["email"])
    
    return user_data


@pytest.fixture(scope="function") 
def repository_test_user(test_user_manager):
    """
    Function-scoped fixture providing a repository layer test user.
    
    Suitable for testing data access layer and repository integration.
    User state is reset before each test.
    
    Returns:
        Repository test user data
    """
    user_data = test_user_manager.get_test_user(TestUserCategory.REPOSITORY, index=0)
    
    if user_data:
        test_user_manager.reset_user_state(user_data["email"])
    
    return user_data


@pytest.fixture(scope="function")
def integration_test_user(test_user_manager):
    """
    Function-scoped fixture providing an end-to-end integration test user.
    
    Suitable for complete business flow testing with realistic data.
    User state is reset before each test.
    
    Returns:
        Integration test user data
    """
    user_data = test_user_manager.get_test_user(TestUserCategory.INTEGRATION, index=0)
    
    if user_data:
        test_user_manager.reset_user_state(user_data["email"])
    
    return user_data


@pytest.fixture(scope="function")
def test_user_with_quiz_history(test_user_manager):
    """
    Function-scoped fixture providing a test user with quiz history.
    
    Creates a user with predefined quiz session data for testing
    scenarios that require existing user performance data.
    
    Returns:
        Test user data with quiz history
    """
    user_data = test_user_manager.create_user_with_quiz_history(
        TestUserCategory.SERVICE, 
        quiz_count=3
    )
    
    return user_data


# ============================================================================
# Pytest Configuration and Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers for test categorization."""
    # Register markers for different test categories
    config.addinivalue_line("markers", "automation: pexpect-based CLI automation tests")
    config.addinivalue_line("markers", "service: service layer integration tests") 
    config.addinivalue_line("markers", "repository: repository layer integration tests")
    config.addinivalue_line("markers", "integration: end-to-end integration tests")
    config.addinivalue_line("markers", "database: database-specific integration tests")
    config.addinivalue_line("markers", "slow_integration: slow-running integration tests")
    config.addinivalue_line("markers", "requires_local_supabase: tests requiring local Supabase instance")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to automatically add markers based on test location and patterns.
    
    This automatically adds appropriate markers to tests based on their file paths
    and naming patterns, reducing the need for manual marker decoration.
    """
    for item in items:
        # Add markers based on file path
        if "tests/automation" in str(item.fspath):
            item.add_marker(pytest.mark.automation)
            item.add_marker(pytest.mark.requires_local_supabase)
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.requires_local_supabase)
            
            # Add specific markers based on subdirectory
            if "tests/integration/service" in str(item.fspath):
                item.add_marker(pytest.mark.service)
            elif "tests/integration/repository" in str(item.fspath):
                item.add_marker(pytest.mark.repository)
                item.add_marker(pytest.mark.database)
        
        # Add markers based on test name patterns
        if "slow" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow_integration)


@pytest.fixture(autouse=True, scope="session")
def setup_integration_test_environment():
    """
    Session-scoped fixture to set up the integration test environment.
    
    This fixture runs automatically for all test sessions and ensures
    the test environment is properly configured for integration testing.
    """
    # Set environment variables for test mode
    import os
    os.environ['MATHSFUN_TEST_MODE'] = '1'
    os.environ['ENVIRONMENT'] = 'local'
    
    yield
    
    # Cleanup environment after session
    os.environ.pop('MATHSFUN_TEST_MODE', None)
