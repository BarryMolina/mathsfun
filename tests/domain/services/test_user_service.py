"""Comprehensive tests for UserService class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.domain.services.user_service import UserService
from src.domain.models.user import User
from src.infrastructure.database.repositories.user_repository import UserRepository


@pytest.fixture
def mock_user_repository():
    """Create mock user repository."""
    mock_repo = Mock(spec=UserRepository)
    mock_supabase_manager = Mock()
    mock_repo.supabase_manager = mock_supabase_manager
    return mock_repo


@pytest.fixture
def user_service(mock_user_repository):
    """Create UserService instance with mocked dependencies."""
    return UserService(mock_user_repository)


@pytest.fixture
def sample_user():
    """Create sample user for testing."""
    return User(
        id="test-user-123",
        email="test@example.com",
        display_name="Test User",
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        last_active=datetime(2023, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def auth_user_response():
    """Mock auth user response."""
    mock_user = Mock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"full_name": "Test User"}
    return mock_user


class TestUserServiceInit:
    """Test UserService initialization."""

    def test_init_sets_attributes_correctly(self, mock_user_repository):
        """Test that initialization sets all attributes correctly."""
        service = UserService(mock_user_repository)

        assert service.user_repo == mock_user_repository
        assert service.supabase_manager == mock_user_repository.supabase_manager
        assert service._cached_user is None
        assert service._cached_user_id is None


class TestGetOrCreateUserProfile:
    """Test get_or_create_user_profile method."""

    def test_get_existing_user_profile(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test getting an existing user profile."""
        # Setup
        mock_user_repository.get_user_profile.return_value = sample_user

        # Execute
        result = user_service.get_or_create_user_profile(
            "test-user-123", "test@example.com", "Test User"
        )

        # Verify
        assert result == sample_user
        mock_user_repository.get_user_profile.assert_called_once_with("test-user-123")
        mock_user_repository.update_last_active.assert_called_once_with("test-user-123")

    def test_create_new_user_profile(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test creating a new user profile."""
        # Setup
        mock_user_repository.get_user_profile.return_value = None
        mock_user_repository.create_user_profile.return_value = sample_user

        # Execute
        with patch("src.domain.services.user_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            result = user_service.get_or_create_user_profile(
                "test-user-123", "test@example.com", "Test User"
            )

        # Verify
        assert result == sample_user
        mock_user_repository.get_user_profile.assert_called_once_with("test-user-123")
        mock_user_repository.create_user_profile.assert_called_once()

        # Verify the created user object
        created_user_arg = mock_user_repository.create_user_profile.call_args[0][0]
        assert created_user_arg.id == "test-user-123"
        assert created_user_arg.email == "test@example.com"
        assert created_user_arg.display_name == "Test User"

    def test_create_user_with_default_display_name(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test creating a user with default display name from email."""
        # Setup
        mock_user_repository.get_user_profile.return_value = None
        mock_user_repository.create_user_profile.return_value = sample_user

        # Execute
        with patch("src.domain.services.user_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            result = user_service.get_or_create_user_profile(
                "test-user-123", "test@example.com"
            )

        # Verify
        created_user_arg = mock_user_repository.create_user_profile.call_args[0][0]
        assert created_user_arg.display_name == "test"  # From email split

    def test_creation_failed_fallback_to_existing(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test fallback to existing user when creation fails."""
        # Setup
        mock_user_repository.get_user_profile.side_effect = [
            None,
            sample_user,
        ]  # First call returns None, second returns user
        mock_user_repository.create_user_profile.return_value = None  # Creation fails

        # Execute
        with patch("src.domain.services.user_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            result = user_service.get_or_create_user_profile(
                "test-user-123", "test@example.com", "Test User"
            )

        # Verify
        assert result == sample_user
        assert mock_user_repository.get_user_profile.call_count == 2
        mock_user_repository.update_last_active.assert_called_once_with("test-user-123")
        # Should clear cache
        assert user_service._cached_user is None
        assert user_service._cached_user_id is None

    def test_creation_failed_no_fallback(self, user_service, mock_user_repository):
        """Test when both creation and fallback fail."""
        # Setup
        mock_user_repository.get_user_profile.side_effect = [
            None,
            None,
        ]  # Both calls return None
        mock_user_repository.create_user_profile.return_value = None  # Creation fails

        # Execute
        with patch("src.domain.services.user_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            result = user_service.get_or_create_user_profile(
                "test-user-123", "test@example.com", "Test User"
            )

        # Verify
        assert result is None

    def test_creation_successful_clears_cache(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test that successful creation clears cache."""
        # Setup
        user_service._cached_user = sample_user
        user_service._cached_user_id = "old-user"
        mock_user_repository.get_user_profile.return_value = None
        mock_user_repository.create_user_profile.return_value = sample_user

        # Execute
        with patch("src.domain.services.user_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            result = user_service.get_or_create_user_profile(
                "test-user-123", "test@example.com", "Test User"
            )

        # Verify
        assert result == sample_user
        assert user_service._cached_user is None
        assert user_service._cached_user_id is None


class TestUpdateDisplayName:
    """Test update_display_name method."""

    def test_update_display_name_success(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test successful display name update."""
        # Setup
        updated_user = User(
            id="test-user-123",
            email="test@example.com",
            display_name="New Name",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            last_active=datetime(2023, 1, 1, 12, 0, 0),
        )
        mock_user_repository.get_user_profile.return_value = sample_user
        mock_user_repository.update_user_profile.return_value = updated_user

        # Set some cache to verify it gets cleared
        user_service._cached_user = sample_user
        user_service._cached_user_id = "test-user-123"

        # Execute
        result = user_service.update_display_name("test-user-123", "New Name")

        # Verify
        assert result == updated_user
        assert sample_user.display_name == "New Name"  # Object should be modified
        mock_user_repository.get_user_profile.assert_called_once_with("test-user-123")
        mock_user_repository.update_user_profile.assert_called_once_with(sample_user)

        # Cache should be cleared
        assert user_service._cached_user is None
        assert user_service._cached_user_id is None

    def test_update_display_name_user_not_found(
        self, user_service, mock_user_repository
    ):
        """Test display name update when user doesn't exist."""
        # Setup
        mock_user_repository.get_user_profile.return_value = None

        # Execute
        result = user_service.update_display_name("nonexistent-user", "New Name")

        # Verify
        assert result is None
        mock_user_repository.get_user_profile.assert_called_once_with(
            "nonexistent-user"
        )
        mock_user_repository.update_user_profile.assert_not_called()

    def test_update_display_name_update_fails(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test display name update when repository update fails."""
        # Setup
        mock_user_repository.get_user_profile.return_value = sample_user
        mock_user_repository.update_user_profile.return_value = None

        # Set some cache to verify it doesn't get cleared on failure
        user_service._cached_user = sample_user
        user_service._cached_user_id = "test-user-123"

        # Execute
        result = user_service.update_display_name("test-user-123", "New Name")

        # Verify
        assert result is None
        # Cache should not be cleared on failure
        assert user_service._cached_user == sample_user
        assert user_service._cached_user_id == "test-user-123"


class TestGetCurrentUser:
    """Test get_current_user method."""

    def test_get_current_user_not_authenticated(
        self, user_service, mock_user_repository
    ):
        """Test get_current_user when not authenticated."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = False

        # Execute
        result = user_service.get_current_user()

        # Verify
        assert result is None

    def test_get_current_user_cached_without_force_refresh(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test get_current_user returns cached user when available and not forcing refresh."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_session = Mock()
        mock_session.user.id = "test-user-123"
        mock_client.auth.get_session.return_value = mock_session
        mock_user_repository.supabase_manager.get_client.return_value = mock_client

        # Set cache
        user_service._cached_user = sample_user
        user_service._cached_user_id = "test-user-123"

        # Execute
        result = user_service.get_current_user(force_refresh=False)

        # Verify
        assert result == sample_user
        # Should not call get_user_profile since using cache
        mock_user_repository.get_user_profile.assert_not_called()

    def test_get_current_user_force_refresh_with_profile(
        self, user_service, mock_user_repository, sample_user, auth_user_response
    ):
        """Test get_current_user with force_refresh when profile exists."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = auth_user_response
        mock_client.auth.get_user.return_value = mock_response
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = sample_user

        # Execute
        result = user_service.get_current_user(force_refresh=True)

        # Verify
        assert result == sample_user
        mock_user_repository.get_user_profile.assert_called_once_with("test-user-123")
        mock_user_repository.update_last_active.assert_called_once_with("test-user-123")

        # Should cache the result
        assert user_service._cached_user == sample_user
        assert user_service._cached_user_id == "test-user-123"

    def test_get_current_user_no_force_refresh_with_profile(
        self, user_service, mock_user_repository, sample_user, auth_user_response
    ):
        """Test get_current_user without force_refresh when profile exists."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_session = Mock()
        mock_session.user = auth_user_response
        mock_client.auth.get_session.return_value = mock_session
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = sample_user

        # Execute
        result = user_service.get_current_user(force_refresh=False)

        # Verify
        assert result == sample_user
        mock_user_repository.get_user_profile.assert_called_once_with("test-user-123")
        mock_user_repository.update_last_active.assert_called_once_with("test-user-123")

    def test_get_current_user_force_refresh_no_auth_response(
        self, user_service, mock_user_repository
    ):
        """Test get_current_user with force_refresh when auth response is None."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_client.auth.get_user.return_value = None
        mock_user_repository.supabase_manager.get_client.return_value = mock_client

        # Execute
        result = user_service.get_current_user(force_refresh=True)

        # Verify
        assert result is None

    def test_get_current_user_force_refresh_no_user_in_response(
        self, user_service, mock_user_repository
    ):
        """Test get_current_user with force_refresh when response has no user."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = None
        mock_client.auth.get_user.return_value = mock_response
        mock_user_repository.supabase_manager.get_client.return_value = mock_client

        # Execute
        result = user_service.get_current_user(force_refresh=True)

        # Verify
        assert result is None

    def test_get_current_user_no_session(self, user_service, mock_user_repository):
        """Test get_current_user when session is None."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_client.auth.get_session.return_value = None
        mock_user_repository.supabase_manager.get_client.return_value = mock_client

        # Execute
        result = user_service.get_current_user(force_refresh=False)

        # Verify
        assert result is None

    def test_get_current_user_no_user_in_session(
        self, user_service, mock_user_repository
    ):
        """Test get_current_user when session has no user."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_session = Mock()
        mock_session.user = None
        mock_client.auth.get_session.return_value = mock_session
        mock_user_repository.supabase_manager.get_client.return_value = mock_client

        # Execute
        result = user_service.get_current_user(force_refresh=False)

        # Verify
        assert result is None

    def test_get_current_user_create_profile_from_auth_force_refresh(
        self, user_service, mock_user_repository, sample_user, auth_user_response
    ):
        """Test creating profile from auth data with force_refresh."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_response = Mock()
        mock_response.user = auth_user_response
        mock_client.auth.get_user.return_value = mock_response
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = None  # No profile exists

        # Mock get_or_create_user_profile
        with patch.object(
            user_service, "get_or_create_user_profile", return_value=sample_user
        ) as mock_get_or_create:
            # Execute
            result = user_service.get_current_user(force_refresh=True)

        # Verify
        assert result == sample_user
        mock_get_or_create.assert_called_once_with(
            "test-user-123", "test@example.com", "Test User"
        )

        # Should cache the result
        assert user_service._cached_user == sample_user
        assert user_service._cached_user_id == "test-user-123"

    def test_get_current_user_create_profile_from_auth_no_force_refresh(
        self, user_service, mock_user_repository, sample_user, auth_user_response
    ):
        """Test creating profile from auth data without force_refresh."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_session = Mock()
        mock_session.user = auth_user_response
        mock_client.auth.get_session.return_value = mock_session
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = None  # No profile exists

        # Mock get_or_create_user_profile
        with patch.object(
            user_service, "get_or_create_user_profile", return_value=sample_user
        ) as mock_get_or_create:
            # Execute
            result = user_service.get_current_user(force_refresh=False)

        # Verify
        assert result == sample_user
        mock_get_or_create.assert_called_once_with(
            "test-user-123", "test@example.com", "Test User"
        )

    def test_get_current_user_display_name_fallbacks(
        self, user_service, mock_user_repository, sample_user
    ):
        """Test display name fallback logic."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_session = Mock()

        # Test case 1: name in metadata
        auth_user_1 = Mock()
        auth_user_1.id = "test-user-123"
        auth_user_1.email = "test@example.com"
        auth_user_1.user_metadata = {"name": "Metadata Name"}
        mock_session.user = auth_user_1
        mock_client.auth.get_session.return_value = mock_session
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = None

        with patch.object(
            user_service, "get_or_create_user_profile", return_value=sample_user
        ) as mock_get_or_create:
            user_service.get_current_user(force_refresh=False)
            mock_get_or_create.assert_called_with(
                "test-user-123", "test@example.com", "Metadata Name"
            )

        # Clear cache between test cases
        user_service.clear_user_cache()

        # Test case 2: email split fallback
        auth_user_2 = Mock()
        auth_user_2.id = "test-user-456"  # Different user ID to avoid cache issues
        auth_user_2.email = "test@example.com"
        auth_user_2.user_metadata = {}
        mock_session.user = auth_user_2
        mock_user_repository.get_user_profile.return_value = None  # No existing profile

        with patch.object(
            user_service, "get_or_create_user_profile", return_value=sample_user
        ) as mock_get_or_create:
            user_service.get_current_user(force_refresh=False)
            mock_get_or_create.assert_called_with(
                "test-user-456", "test@example.com", "test"
            )

        # Test case 3: Unknown fallback
        auth_user_3 = Mock()
        auth_user_3.id = "test-user-123"
        auth_user_3.email = None
        auth_user_3.user_metadata = {}
        mock_session.user = auth_user_3

        result = user_service.get_current_user(force_refresh=False)
        assert result is None  # Should return None when no email

    def test_get_current_user_exception_handling(
        self, user_service, mock_user_repository
    ):
        """Test get_current_user exception handling."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.side_effect = Exception(
            "Test error"
        )

        # Execute
        with patch("builtins.print") as mock_print:
            result = user_service.get_current_user()

        # Verify
        assert result is None
        mock_print.assert_called_once_with("Error fetching user data: Test error")

    def test_get_current_user_force_refresh_different_user_id(
        self, user_service, mock_user_repository, sample_user, auth_user_response
    ):
        """Test force_refresh with different user ID clears cache and fetches new profile."""
        # Setup
        mock_user_repository.supabase_manager.is_authenticated.return_value = True
        mock_client = Mock()
        mock_response = Mock()
        auth_user_response.id = "different-user-456"  # Different user ID
        mock_response.user = auth_user_response
        mock_client.auth.get_user.return_value = mock_response
        mock_user_repository.supabase_manager.get_client.return_value = mock_client
        mock_user_repository.get_user_profile.return_value = sample_user

        # Set cache with different user
        user_service._cached_user = sample_user
        user_service._cached_user_id = "test-user-123"

        # Execute
        result = user_service.get_current_user(force_refresh=True)

        # Verify
        assert result == sample_user
        mock_user_repository.get_user_profile.assert_called_once_with(
            "different-user-456"
        )
        # Cache should be updated with new user ID
        assert user_service._cached_user_id == "different-user-456"


class TestClearUserCache:
    """Test clear_user_cache method."""

    def test_clear_user_cache(self, user_service, sample_user):
        """Test clearing user cache."""
        # Setup
        user_service._cached_user = sample_user
        user_service._cached_user_id = "test-user-123"

        # Execute
        user_service.clear_user_cache()

        # Verify
        assert user_service._cached_user is None
        assert user_service._cached_user_id is None
