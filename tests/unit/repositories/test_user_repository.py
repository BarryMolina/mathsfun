"""Simplified unit tests for UserRepository class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from repositories.user_repository import UserRepository
from models.user import User


class TestUserRepositoryCore:
    """Core functionality tests for UserRepository."""
    
    def test_get_user_profile_success(self, sample_user, sample_db_response):
        """Test successful user profile retrieval."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_db_response]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.get_user_profile("test-user-123")
        
        # Verify
        assert result is not None
        assert isinstance(result, User)
        assert result.id == "test-user-123"
        assert result.email == "test@example.com"
        assert result.display_name == "Test User"
        
        # Verify correct API usage
        mock_client.table.assert_called_once_with("user_profiles")
    
    def test_get_user_profile_not_found(self):
        """Test user profile retrieval when user doesn't exist."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = []
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.get_user_profile("non-existent-user")
        
        # Verify
        assert result is None
    
    def test_create_user_profile_success(self, sample_user, sample_db_response):
        """Test successful user profile creation."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_db_response]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.create_user_profile(sample_user)
        
        # Verify
        assert result is not None
        assert isinstance(result, User)
        assert result.id == "test-user-123"
        assert result.email == "test@example.com"
        
        # Verify correct API usage
        mock_client.table.assert_called_once_with("user_profiles")
    
    def test_update_user_profile_success(self, sample_user, sample_db_response):
        """Test successful user profile update."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [sample_db_response]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.update_user_profile(sample_user)
        
        # Verify
        assert result is not None
        assert isinstance(result, User)
        assert result.id == "test-user-123"
        
        # Verify correct API usage
        mock_client.table.assert_called_once_with("user_profiles")
    
    @patch('datetime.datetime')
    def test_update_last_active_success(self, mock_datetime):
        """Test successful last active timestamp update."""
        # Setup
        fixed_time = datetime(2023, 12, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{"updated": True}]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.update_last_active("test-user-123")
        
        # Verify
        assert result is True
        
        # Verify correct API usage
        mock_client.table.assert_called_once_with("user_profiles")


class TestUserRepositoryErrorHandling:
    """Test error handling in UserRepository."""
    
    def test_get_user_profile_database_error(self, capsys):
        """Test handling of database errors during profile retrieval."""
        # Setup
        mock_client = Mock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database connection failed")
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.get_user_profile("test-user-123")
        
        # Verify
        assert result is None
        
        # Check error was logged
        captured = capsys.readouterr()
        assert "Error fetching user profile: Database connection failed" in captured.out
    
    def test_create_user_profile_validation_error(self, sample_user, capsys):
        """Test handling of validation errors during profile creation."""
        # Setup
        mock_client = Mock()
        mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("Validation failed")
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.create_user_profile(sample_user)
        
        # Verify
        assert result is None
        
        # Check error was logged
        captured = capsys.readouterr()
        assert "Error creating user profile: Validation failed" in captured.out
    
    def test_update_last_active_network_error(self, capsys):
        """Test handling of network errors during last active update."""
        # Setup
        mock_client = Mock()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Network timeout")
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.update_last_active("test-user-123")
        
        # Verify
        assert result is False
        
        # Check error was logged
        captured = capsys.readouterr()
        assert "Error updating last active: Network timeout" in captured.out


class TestUserRepositoryDataHandling:
    """Test data handling and edge cases in UserRepository."""
    
    def test_get_user_profile_empty_response(self):
        """Test handling of empty database response."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.get_user_profile("test-user-123")
        
        # Verify
        assert result is None
    
    def test_create_user_profile_with_minimal_data(self, minimal_user, minimal_db_response):
        """Test user creation with only required fields."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [minimal_db_response]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.create_user_profile(minimal_user)
        
        # Verify
        assert result is not None
        assert result.id == "minimal-user-456"
        assert result.email == "minimal@example.com"
        assert result.display_name is None
        assert result.created_at is None
    
    def test_update_last_active_no_response_data(self):
        """Test last active update when response has no data."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        repository = UserRepository(mock_client)
        
        # Execute
        result = repository.update_last_active("test-user-123")
        
        # Verify
        assert result is False
    
    def test_user_model_conversion_accuracy(self, sample_db_response):
        """Test accurate conversion between User model and dict."""
        # Create User from dict
        user = User.from_dict(sample_db_response)
        
        # Convert back to dict
        user_dict = user.to_dict()
        
        # Verify key fields are preserved
        assert user_dict["id"] == "test-user-123"
        assert user_dict["display_name"] == "Test User"
        # Note: email is not included in to_dict() by design
    
    def test_datetime_handling_edge_cases(self):
        """Test datetime conversion with various ISO formats."""
        # Test with different timezone formats
        test_cases = [
            "2023-12-01T10:00:00Z",
            "2023-12-01T10:00:00+00:00",
            "2023-12-01T10:00:00.123Z",
        ]
        
        for datetime_str in test_cases:
            data = {
                "id": "test-user",
                "email": "test@example.com",
                "created_at": datetime_str,
                "last_active": datetime_str
            }
            
            user = User.from_dict(data)
            assert user.created_at is not None
            assert user.last_active is not None
            assert isinstance(user.created_at, datetime)
    
    def test_response_handling_patterns(self):
        """Test BaseRepository response handling methods."""
        mock_client = Mock()
        repository = UserRepository(mock_client)
        
        # Test with list containing single item
        response_with_list = Mock()
        response_with_list.data = [{"id": "test", "email": "test@example.com"}]
        
        result = repository._handle_single_response(response_with_list)
        assert result == {"id": "test", "email": "test@example.com"}
        
        # Test with empty list
        response_empty = Mock()
        response_empty.data = []
        
        result = repository._handle_single_response(response_empty)
        assert result is None
        
        # Test with None data
        response_none = Mock()
        response_none.data = None
        
        result = repository._handle_single_response(response_none)
        assert result is None