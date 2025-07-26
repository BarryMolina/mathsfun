"""User-related test fixtures for MathsFun application."""

import pytest
from datetime import datetime
from unittest.mock import Mock
from src.domain.models.user import User


@pytest.fixture
def sample_user():
    """Sample User object for testing."""
    return User(
        id="test-user-123",
        email="test@example.com",
        display_name="Test User",
        created_at=datetime(2023, 12, 1, 10, 0, 0),
        last_active=datetime(2023, 12, 1, 10, 0, 0),
    )


@pytest.fixture
def minimal_user():
    """User object with only required fields."""
    return User(id="minimal-user-456", email="minimal@example.com")


@pytest.fixture
def sample_db_response():
    """Sample database response data."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "display_name": "Test User",
        "created_at": "2023-12-01T10:00:00Z",
        "last_active": "2023-12-01T10:00:00Z",
    }


@pytest.fixture
def minimal_db_response():
    """Minimal database response with only required fields."""
    return {
        "id": "minimal-user-456",
        "email": "minimal@example.com",
        "display_name": None,
        "created_at": None,
        "last_active": None,
    }


@pytest.fixture
def empty_db_response():
    """Empty database response."""
    return []


@pytest.fixture
def multiple_users_db_response():
    """Database response with multiple users."""
    return [
        {
            "id": "user-1",
            "email": "user1@example.com",
            "display_name": "User One",
            "created_at": "2023-12-01T10:00:00Z",
            "last_active": "2023-12-01T10:00:00Z",
        },
        {
            "id": "user-2",
            "email": "user2@example.com",
            "display_name": "User Two",
            "created_at": "2023-12-01T11:00:00Z",
            "last_active": "2023-12-01T11:00:00Z",
        },
    ]


@pytest.fixture
def mock_supabase_response():
    """Mock Supabase response object."""
    response = Mock()
    response.data = None
    return response


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for unit tests."""
    client = Mock()

    # Create a mock table that supports method chaining
    table_mock = Mock()
    select_mock = Mock()
    eq_mock = Mock()
    update_mock = Mock()
    insert_mock = Mock()
    execute_mock = Mock()

    # Set up the method chain
    client.table.return_value = table_mock
    table_mock.select.return_value = select_mock
    table_mock.insert.return_value = insert_mock
    table_mock.update.return_value = update_mock
    select_mock.eq.return_value = eq_mock
    update_mock.eq.return_value = eq_mock
    eq_mock.execute.return_value = execute_mock
    insert_mock.execute.return_value = execute_mock

    return client


@pytest.fixture
def user_not_found_response():
    """Response when user is not found."""
    response = Mock()
    response.data = []
    return response


@pytest.fixture
def database_error_response():
    """Response when database error occurs."""
    response = Mock()
    response.data = None
    return response
