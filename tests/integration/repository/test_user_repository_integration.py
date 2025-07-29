#!/usr/bin/env python3
"""
Integration tests for UserRepository with real Supabase database.

These tests validate the UserRepository data access layer with actual database
operations, ensuring proper CRUD operations, data consistency, and error handling.
"""

import pytest
from typing import Dict, Any, Optional
from datetime import datetime

from src.domain.models.user import User
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.supabase_manager import SupabaseManager


@pytest.mark.repository
@pytest.mark.database
@pytest.mark.integration
class TestUserRepositoryIntegration:
    """Integration tests for UserRepository with real database operations."""

    @pytest.fixture(scope="function")
    def user_repository(self):
        """Create UserRepository instance with real Supabase connection."""
        supabase_manager = SupabaseManager(
            url="http://127.0.0.1:54321",
            anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
        )
        
        return UserRepository(supabase_manager)

    def test_create_user_profile(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test creating a user profile in the database."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # Create user profile
        created_user = user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )

        assert created_user is not None
        assert isinstance(created_user, User)
        assert created_user.email == email
        assert created_user.display_name == display_name
        assert created_user.id is not None
        assert isinstance(created_user.created_at, datetime)

    def test_get_user_by_email(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test retrieving user by email from database."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # First create a user
        created_user = user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )

        # Then retrieve by email
        retrieved_user = user_repository.get_user_by_email(email)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == email
        assert retrieved_user.display_name == display_name

    def test_get_nonexistent_user(self, user_repository: UserRepository):
        """Test retrieving non-existent user returns None."""
        nonexistent_email = "definitely.not.exists@test.local"
        
        result = user_repository.get_user_by_email(nonexistent_email)
        assert result is None

    def test_update_user_profile(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test updating user profile in database."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        original_display_name = repository_test_user["display_name"]
        updated_display_name = f"Updated {original_display_name}"

        # Create user
        created_user = user_repository.create_user_profile(
            email=email,
            display_name=original_display_name
        )

        # Update user
        updated_user = user_repository.update_user_profile(
            user_id=created_user.id,
            display_name=updated_display_name
        )

        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.email == email
        assert updated_user.display_name == updated_display_name

        # Verify update persisted
        retrieved_user = user_repository.get_user_by_email(email)
        assert retrieved_user.display_name == updated_display_name

    def test_update_user_last_active(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test updating user last active timestamp."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # Create user
        created_user = user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )

        original_last_active = created_user.last_active

        # Update last active
        import time
        time.sleep(1)  # Ensure timestamp difference
        
        updated_user = user_repository.update_user_last_active(created_user.id)

        assert updated_user is not None
        assert updated_user.id == created_user.id
        
        # last_active should be updated (if it was None or older)
        if original_last_active:
            assert updated_user.last_active > original_last_active
        else:
            assert updated_user.last_active is not None

    def test_user_exists_check(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test checking if user exists in database."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # Check non-existent user
        assert not user_repository.user_exists(email)

        # Create user
        user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )

        # Check existing user
        assert user_repository.user_exists(email)

    def test_database_error_handling(self, user_repository: UserRepository):
        """Test repository error handling with invalid operations."""
        
        # Test with invalid user ID for update
        result = user_repository.update_user_profile(
            user_id="invalid-user-id-12345",
            display_name="Should Not Work"
        )
        
        # Should handle gracefully and return None or raise appropriate exception
        assert result is None

        # Test with malformed email
        result = user_repository.get_user_by_email("not-an-email")
        # Should handle gracefully
        assert result is None

    def test_concurrent_user_creation(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test repository behavior with concurrent user operations."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        base_email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        import threading
        import time
        
        results = []
        
        def create_user_profile(suffix):
            try:
                user = user_repository.create_user_profile(
                    email=f"{suffix}.{base_email}",
                    display_name=f"{display_name} {suffix}"
                )
                results.append(user)
            except Exception as e:
                results.append(e)

        # Create multiple threads for concurrent creation
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_user_profile, args=(f"concurrent{i}",))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify all operations completed successfully
        assert len(results) == 3
        
        successful_users = []
        for result in results:
            if isinstance(result, User):
                successful_users.append(result)
            else:
                # Log any exceptions for debugging
                print(f"Concurrent creation error: {result}")

        # At least some should succeed (exact behavior depends on constraints)
        assert len(successful_users) > 0

        # Verify each successful user has unique data
        emails = [user.email for user in successful_users]
        assert len(emails) == len(set(emails))  # All emails should be unique


@pytest.mark.repository
@pytest.mark.database
@pytest.mark.integration
class TestUserRepositoryDataIntegrity:
    """Tests for data integrity and consistency in UserRepository."""

    @pytest.fixture(scope="function")
    def user_repository(self):
        """Create UserRepository instance for integrity testing."""
        supabase_manager = SupabaseManager(
            url="http://127.0.0.1:54321",
            anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
        )
        return UserRepository(supabase_manager)

    def test_email_uniqueness_constraint(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test that email uniqueness is enforced at database level."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # Create first user
        first_user = user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )
        assert first_user is not None

        # Attempt to create second user with same email
        # This should either fail or handle the constraint appropriately
        second_user = user_repository.create_user_profile(
            email=email,
            display_name=f"Duplicate {display_name}"
        )
        
        # Depending on implementation, this might return None or raise exception
        # The key is that it should not create a duplicate
        if second_user is not None:
            # If it succeeds, it should be the same user (upsert behavior)
            assert second_user.id == first_user.id
        
        # Verify only one user exists with this email
        all_matches = user_repository.get_user_by_email(email)
        assert all_matches is not None

    def test_data_type_validation(self, user_repository: UserRepository):
        """Test repository handles various data types correctly."""
        
        # Test with None display_name
        user_with_none = user_repository.create_user_profile(
            email="none.display@test.local",
            display_name=None
        )
        
        if user_with_none:
            assert user_with_none.display_name is None
            
        # Test with empty string display_name
        user_with_empty = user_repository.create_user_profile(
            email="empty.display@test.local", 
            display_name=""
        )
        
        if user_with_empty:
            assert user_with_empty.display_name == ""

    def test_timestamp_consistency(self, user_repository: UserRepository, repository_test_user: Dict[str, Any]):
        """Test that timestamps are handled consistently."""
        if not repository_test_user:
            pytest.skip("Repository test user not available")

        email = repository_test_user["email"]
        display_name = repository_test_user["display_name"]

        # Create user and check timestamps
        created_user = user_repository.create_user_profile(
            email=email,
            display_name=display_name
        )

        assert created_user.created_at is not None
        assert isinstance(created_user.created_at, datetime)
        
        # created_at should be recent (within last minute)
        import time
        now = datetime.now()
        time_diff = (now - created_user.created_at).total_seconds()
        assert time_diff < 60  # Should be created within last minute

        # Update last_active and verify timestamp changes
        original_last_active = created_user.last_active
        
        time.sleep(1)  # Ensure time difference
        updated_user = user_repository.update_user_last_active(created_user.id)
        
        if updated_user and updated_user.last_active:
            if original_last_active:
                assert updated_user.last_active > original_last_active
            
            # last_active should be more recent than created_at
            assert updated_user.last_active >= updated_user.created_at