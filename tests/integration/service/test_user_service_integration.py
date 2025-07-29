#!/usr/bin/env python3
"""
Integration tests for UserService with real Supabase database.

These tests validate the UserService business logic with actual database
operations, ensuring proper integration between the service layer and
the data persistence layer.
"""

import pytest
from typing import Dict, Any

from src.domain.services.user_service import UserService
from src.infrastructure.database.supabase_manager import SupabaseManager
from src.config.container import Container


@pytest.mark.service
@pytest.mark.integration
class TestUserServiceIntegration:
    """Integration tests for UserService with real database operations."""

    @pytest.fixture(scope="function")
    def user_service(self):
        """Create UserService instance with real Supabase connection."""
        container = Container()
        container.config.from_dict({
            'supabase': {
                'url': 'http://127.0.0.1:54321',
                'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
            }
        })
        container.wire(modules=[__name__])
        
        # Get UserService from container
        user_service = container.user_service()
        return user_service

    def test_user_profile_creation_and_retrieval(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test creating and retrieving user profile through service layer."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        display_name = service_test_user["display_name"]

        # Test user profile creation through service
        created_user = user_service.create_or_update_profile(
            email=email,
            display_name=display_name
        )

        assert created_user is not None
        assert created_user.email == email
        assert created_user.display_name == display_name

        # Test user profile retrieval
        retrieved_user = user_service.get_user_profile(email)
        
        assert retrieved_user is not None
        assert retrieved_user.email == email
        assert retrieved_user.display_name == display_name
        assert retrieved_user.id == created_user.id

    def test_user_profile_update(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test updating user profile through service layer."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        original_display_name = service_test_user["display_name"]
        updated_display_name = f"Updated {original_display_name}"

        # Create initial profile
        user_service.create_or_update_profile(
            email=email,
            display_name=original_display_name
        )

        # Update profile
        updated_user = user_service.create_or_update_profile(
            email=email,
            display_name=updated_display_name
        )

        assert updated_user is not None
        assert updated_user.email == email
        assert updated_user.display_name == updated_display_name

        # Verify update persisted
        retrieved_user = user_service.get_user_profile(email)
        assert retrieved_user.display_name == updated_display_name

    def test_user_caching_behavior(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test user service caching behavior."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        display_name = service_test_user["display_name"]

        # Create user profile
        created_user = user_service.create_or_update_profile(
            email=email,
            display_name=display_name
        )

        # First retrieval (should cache)
        first_retrieval = user_service.get_user_profile(email)
        
        # Second retrieval (should use cache)
        second_retrieval = user_service.get_user_profile(email)

        # Both should return the same user data
        assert first_retrieval.id == second_retrieval.id
        assert first_retrieval.email == second_retrieval.email
        assert first_retrieval.display_name == second_retrieval.display_name

        # Test cache invalidation after update
        updated_display_name = f"Cache Test {display_name}"
        user_service.create_or_update_profile(
            email=email,
            display_name=updated_display_name
        )

        # Retrieval after update should reflect changes
        post_update_retrieval = user_service.get_user_profile(email)
        assert post_update_retrieval.display_name == updated_display_name

    def test_nonexistent_user_handling(self, user_service: UserService):
        """Test service behavior with non-existent users."""
        nonexistent_email = "nonexistent.user@test.local"

        # Should return None for non-existent user
        result = user_service.get_user_profile(nonexistent_email)
        assert result is None

    def test_user_authentication_flow(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test user authentication and profile management flow."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        display_name = service_test_user["display_name"]

        # Simulate authentication flow
        # 1. User signs in (profile may not exist yet)
        existing_profile = user_service.get_user_profile(email)
        
        if not existing_profile:
            # 2. Create profile if it doesn't exist
            created_profile = user_service.create_or_update_profile(
                email=email,
                display_name=display_name
            )
            assert created_profile is not None
        
        # 3. Verify profile exists and is accessible
        final_profile = user_service.get_user_profile(email)
        assert final_profile is not None
        assert final_profile.email == email


@pytest.mark.service
@pytest.mark.integration
@pytest.mark.slow_integration
class TestUserServicePerformance:
    """Performance tests for UserService operations."""

    @pytest.fixture(scope="function")
    def user_service(self):
        """Create UserService instance for performance testing."""
        container = Container()
        container.config.from_dict({
            'supabase': {
                'url': 'http://127.0.0.1:54321',
                'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
            }
        })
        container.wire(modules=[__name__])
        return container.user_service()

    def test_repeated_user_retrieval_performance(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test performance of repeated user retrievals (cache effectiveness)."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        display_name = service_test_user["display_name"]

        # Create user profile
        user_service.create_or_update_profile(
            email=email,
            display_name=display_name
        )

        import time
        
        # Measure first retrieval (cache miss)
        start_time = time.time()
        first_result = user_service.get_user_profile(email)
        first_duration = time.time() - start_time

        # Measure second retrieval (cache hit)
        start_time = time.time()
        second_result = user_service.get_user_profile(email)
        second_duration = time.time() - start_time

        # Both should return valid results
        assert first_result is not None
        assert second_result is not None
        assert first_result.email == second_result.email

        # Second retrieval should be faster due to caching
        # This is a rough performance check - exact timing depends on system
        assert second_duration <= first_duration * 2  # Allow some variance

    def test_concurrent_user_operations(self, user_service: UserService, service_test_user: Dict[str, Any]):
        """Test user service behavior under concurrent operations."""
        if not service_test_user:
            pytest.skip("Service test user not available")

        email = service_test_user["email"]
        base_display_name = service_test_user["display_name"]

        # Simulate concurrent profile updates
        import threading
        import time
        
        results = []
        
        def update_profile(suffix):
            try:
                updated_user = user_service.create_or_update_profile(
                    email=email,
                    display_name=f"{base_display_name} {suffix}"
                )
                results.append(updated_user)
            except Exception as e:
                results.append(e)

        # Create multiple threads for concurrent updates
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_profile, args=(f"Thread{i}",))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert result.email == email

        # Verify final state is consistent
        final_profile = user_service.get_user_profile(email)
        assert final_profile is not None
        assert final_profile.email == email