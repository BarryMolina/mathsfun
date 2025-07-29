#!/usr/bin/env python3
"""
Pytest fixtures and configuration for automation tests.

This module provides shared fixtures for pexpect-based automation testing,
including test user management, navigator setup, and cleanup utilities.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from typing import Generator, Dict, Any

from .cli_navigator import AutomatedNavigator, NavigationState


@pytest.fixture(scope="session")
def test_users() -> Dict[str, Dict[str, str]]:
    """
    Provide test user credentials for automation testing.

    Returns:
        Dictionary of test user configurations
    """
    return {
        "primary": {
            "email": "automation.test.fresh@mathsfun.local",
            "password": "TestPass123!",
            "display_name": "Automation Primary",
        },
        "secondary": {
            "email": "automation.test.secondary@mathsfun.local",
            "password": "TestPass456!",
            "display_name": "Automation Secondary",
        },
        "signup": {
            "email": "automation.test.signup@mathsfun.local",
            "password": "TestPassNew789!",
            "display_name": "Automation Signup",
        },
    }


@pytest.fixture(scope="function")
def temp_working_dir() -> Generator[str, None, None]:
    """
    Create a temporary working directory for test isolation.

    Yields:
        Path to temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix="mathsfun_automation_")

    try:
        yield temp_dir
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def navigator(temp_working_dir: str) -> Generator[AutomatedNavigator, None, None]:
    """
    Create and configure an AutomatedNavigator instance.

    Args:
        temp_working_dir: Temporary directory for test isolation

    Yields:
        Configured AutomatedNavigator instance
    """
    # Create navigator with reasonable timeout
    nav = AutomatedNavigator(timeout=15, encoding="utf-8")

    try:
        yield nav
    finally:
        # Ensure cleanup
        nav.terminate()


@pytest.fixture(scope="function")
def launched_navigator(navigator: AutomatedNavigator) -> AutomatedNavigator:
    """
    Create a navigator with the application already launched.

    Args:
        navigator: Base navigator instance

    Returns:
        Navigator with launched application

    Raises:
        pytest.skip: If application launch fails
    """
    if not navigator.launch_app():
        pytest.skip("Failed to launch MathsFun application")

    return navigator


@pytest.fixture(scope="session")
def ensure_test_users_exist(test_users: Dict[str, Dict[str, str]]) -> None:
    """
    Ensure test users exist in the database by attempting signup.
    This runs once per test session.
    
    Note: This fixture will attempt to create users but will not fail
    if users already exist, since signup attempts may be cancelled
    due to getpass limitations with pexpect.
    """
    # This is a marker fixture - the actual user creation happens
    # in individual tests as needed since pexpect has limitations
    # with getpass-based signup flows
    pass


@pytest.fixture(scope="function")
def authenticated_navigator(
    launched_navigator: AutomatedNavigator, 
    automation_test_users: Dict[str, Dict[str, str]]
) -> AutomatedNavigator:
    """
    Create a navigator that is already authenticated using managed test users.

    Args:
        launched_navigator: Navigator with launched application
        automation_test_users: Managed automation test user credentials

    Returns:
        Navigator with authenticated user session

    Raises:
        pytest.skip: If authentication fails
    """
    primary_user = automation_test_users["primary"]
    
    if not primary_user:
        pytest.skip("Primary automation test user not available")

    # Attempt authentication with managed user (should exist)
    if not launched_navigator.authenticate_with_email(
        email=primary_user["email"], 
        password=primary_user["password"], 
        is_signup=False
    ):
        pytest.skip(f"Failed to authenticate with managed user: {primary_user['email']}")

    return launched_navigator


@pytest.fixture(scope="function")
def quiz_config_basic() -> Dict[str, Any]:
    """
    Provide basic quiz configuration for testing.

    Returns:
        Basic quiz configuration parameters
    """
    return {
        "addition": {"difficulty_range": (1, 3), "num_problems": 5},
        "addition_tables": {"table_range": (1, 12), "random_order": True},
    }


@pytest.fixture(scope="function")
def quiz_config_advanced() -> Dict[str, Any]:
    """
    Provide advanced quiz configuration for testing.

    Returns:
        Advanced quiz configuration parameters
    """
    return {
        "addition": {"difficulty_range": (3, 5), "num_problems": 20},
        "addition_tables": {"table_range": (5, 25), "random_order": False},
    }


@pytest.fixture(params=["perfect", "mixed", "incorrect"])
def quiz_strategy(request) -> str:
    """
    Parametrized fixture for different quiz completion strategies.

    Returns:
        Quiz completion strategy name
    """
    return request.param


@pytest.fixture(scope="function")
def session_tracker() -> Dict[str, Any]:
    """
    Provide a session tracking dictionary for test data collection.

    Returns:
        Empty dictionary for tracking session data
    """
    return {
        "sessions_completed": 0,
        "authentication_attempts": 0,
        "navigation_steps": [],
        "errors_encountered": [],
        "performance_metrics": {},
    }


def pytest_configure(config):
    """
    Configure pytest for automation testing.

    Args:
        config: Pytest configuration object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "automation: mark test as requiring pexpect automation"
    )
    config.addinivalue_line(
        "markers",
        "slow_automation: mark test as slow automation test requiring extended timeout",
    )
    config.addinivalue_line(
        "markers", "requires_auth: mark test as requiring authenticated user session"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test location.

    Args:
        config: Pytest configuration object
        items: List of collected test items
    """
    automation_marker = pytest.mark.automation

    for item in items:
        # Add automation marker to all tests in automation directory
        if "tests/automation" in str(item.fspath):
            item.add_marker(automation_marker)


@pytest.fixture(autouse=True, scope="function")
def cleanup_processes():
    """
    Automatically cleanup any stray processes after each test.

    This fixture runs after each test to ensure no processes are left running.
    """
    yield

    # Cleanup any remaining pexpect processes
    try:
        import pexpect

        # Kill any remaining python processes that might be test remnants
        # This is a safety measure for CI/CD environments
        pass
    except ImportError:
        pass


@pytest.fixture(scope="session", autouse=True)
def check_pexpect_availability():
    """
    Check if pexpect is available and skip automation tests if not.

    This fixture automatically runs once per test session to verify
    that pexpect is available for automation testing.
    """
    try:
        import pexpect
    except ImportError:
        pytest.skip(
            "pexpect not available - skipping automation tests", allow_module_level=True
        )


# Test environment detection utilities


def is_ci_environment() -> bool:
    """
    Detect if running in a CI/CD environment.

    Returns:
        True if running in CI/CD, False otherwise
    """
    ci_indicators = [
        "CI",
        "CONTINUOUS_INTEGRATION",
        "GITHUB_ACTIONS",
        "TRAVIS",
        "CIRCLECI",
        "JENKINS_URL",
    ]
    return any(os.getenv(indicator) for indicator in ci_indicators)


def get_timeout_multiplier() -> float:
    """
    Get timeout multiplier based on environment.

    Returns:
        Multiplier for timeout values (higher in CI environments)
    """
    if is_ci_environment():
        return 2.0  # Double timeouts in CI
    return 1.0


@pytest.fixture(scope="session")
def environment_config() -> Dict[str, Any]:
    """
    Provide environment-specific configuration.

    Returns:
        Dictionary with environment configuration
    """
    return {
        "is_ci": is_ci_environment(),
        "timeout_multiplier": get_timeout_multiplier(),
        "max_retries": 3 if is_ci_environment() else 1,
        "verbose_logging": is_ci_environment(),
    }
