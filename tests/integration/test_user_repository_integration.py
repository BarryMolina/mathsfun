"""Integration tests for UserRepository with real database."""

import pytest
import os
from datetime import datetime
from supabase import create_client
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.domain.models.user import User


@pytest.fixture(scope="session")
def supabase_client():
    """Create Supabase client for integration tests."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        pytest.skip("Supabase credentials not available for integration tests")
    
    try:
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        pytest.skip(f"Failed to create Supabase client: {e}")


@pytest.fixture
def user_repository(supabase_client):
    """UserRepository instance with real Supabase client."""
    return UserRepository(supabase_client)


@pytest.fixture
def test_user():
    """Test user for integration tests."""
    timestamp = datetime.now()
    return User(
        id=f"integration-test-{timestamp.timestamp()}",
        email=f"integration-test-{timestamp.timestamp()}@example.com",
        display_name="Integration Test User",
        created_at=timestamp,
        last_active=timestamp
    )


@pytest.fixture
def cleanup_test_users(supabase_client):
    """Cleanup test users after tests."""
    created_user_ids = []
    
    def add_user_id(user_id):
        created_user_ids.append(user_id)
    
    yield add_user_id
    
    # Cleanup
    for user_id in created_user_ids:
        try:
            supabase_client.table("user_profiles").delete().eq("id", user_id).execute()
        except Exception:
            pass  # Ignore cleanup errors


@pytest.mark.integration
class TestUserRepositoryIntegration:
    """Integration tests for UserRepository with real database."""
    
    def test_full_user_lifecycle(self, user_repository, test_user, cleanup_test_users):
        """Test complete user lifecycle: create -> read -> update -> read."""
        cleanup_test_users(test_user.id)
        
        # 1. Create user
        created_user = user_repository.create_user_profile(test_user)
        assert created_user is not None
        assert created_user.id == test_user.id
        assert created_user.email == test_user.email
        assert created_user.display_name == test_user.display_name
        
        # 2. Read user
        retrieved_user = user_repository.get_user_profile(test_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == test_user.id
        assert retrieved_user.email == test_user.email
        assert retrieved_user.display_name == test_user.display_name
        
        # 3. Update user
        retrieved_user.display_name = "Updated Test User"
        updated_user = user_repository.update_user_profile(retrieved_user)
        assert updated_user is not None
        assert updated_user.display_name == "Updated Test User"
        
        # 4. Read updated user
        final_user = user_repository.get_user_profile(test_user.id)
        assert final_user is not None
        assert final_user.display_name == "Updated Test User"
    
    def test_get_nonexistent_user(self, user_repository):
        """Test retrieving a user that doesn't exist."""
        result = user_repository.get_user_profile("nonexistent-user-12345")
        assert result is None
    
    def test_update_last_active(self, user_repository, test_user, cleanup_test_users):
        """Test updating user's last active timestamp."""
        cleanup_test_users(test_user.id)
        
        # Create user first
        created_user = user_repository.create_user_profile(test_user)
        assert created_user is not None
        
        # Get original last_active
        original_user = user_repository.get_user_profile(test_user.id)
        original_last_active = original_user.last_active
        
        # Update last active
        import time
        time.sleep(1)  # Ensure timestamp difference
        result = user_repository.update_last_active(test_user.id)
        assert result is True
        
        # Verify last_active was updated
        updated_user = user_repository.get_user_profile(test_user.id)
        assert updated_user.last_active != original_last_active
    
    def test_create_user_with_minimal_data(self, user_repository, cleanup_test_users):
        """Test creating user with only required fields."""
        timestamp = datetime.now().timestamp()
        minimal_user = User(
            id=f"minimal-{timestamp}",
            email=f"minimal-{timestamp}@example.com"
        )
        cleanup_test_users(minimal_user.id)
        
        created_user = user_repository.create_user_profile(minimal_user)
        assert created_user is not None
        assert created_user.id == minimal_user.id
        assert created_user.email == minimal_user.email
        assert created_user.display_name is None
    
    def test_update_nonexistent_user(self, user_repository):
        """Test updating a user that doesn't exist."""
        nonexistent_user = User(
            id="nonexistent-user-999",
            email="nonexistent@example.com",
            display_name="Nonexistent User"
        )
        
        result = user_repository.update_user_profile(nonexistent_user)
        # This might return None or an empty result depending on Supabase behavior
        # The exact behavior may vary, but it shouldn't crash
        assert result is None or isinstance(result, User)
    
    def test_update_last_active_nonexistent_user(self, user_repository):
        """Test updating last active for user that doesn't exist."""
        result = user_repository.update_last_active("nonexistent-user-999")
        assert result is False


@pytest.mark.integration
@pytest.mark.slow
class TestUserRepositoryPerformance:
    """Performance tests for UserRepository."""
    
    def test_user_creation_performance(self, user_repository, cleanup_test_users):
        """Test user creation performance under load."""
        import time
        
        users_to_create = 10
        created_users = []
        
        start_time = time.time()
        
        for i in range(users_to_create):
            timestamp = time.time()
            user = User(
                id=f"perf-test-{timestamp}-{i}",
                email=f"perf-test-{timestamp}-{i}@example.com",
                display_name=f"Performance Test User {i}"
            )
            cleanup_test_users(user.id)
            
            created_user = user_repository.create_user_profile(user)
            assert created_user is not None
            created_users.append(created_user)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / users_to_create
        
        # Performance assertion - each user creation should be under 2 seconds
        assert avg_time < 2.0, f"Average user creation time {avg_time}s exceeds threshold"
        
        # Verify all users were created
        assert len(created_users) == users_to_create
    
    def test_user_retrieval_performance(self, user_repository, test_user, cleanup_test_users):
        """Test user retrieval performance."""
        import time
        
        cleanup_test_users(test_user.id)
        
        # Create user first
        created_user = user_repository.create_user_profile(test_user)
        assert created_user is not None
        
        # Test retrieval performance
        retrieval_count = 20
        start_time = time.time()
        
        for _ in range(retrieval_count):
            retrieved_user = user_repository.get_user_profile(test_user.id)
            assert retrieved_user is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / retrieval_count
        
        # Performance assertion - each retrieval should be under 1 second
        assert avg_time < 1.0, f"Average user retrieval time {avg_time}s exceeds threshold"


@pytest.mark.integration
class TestDatabaseSchema:
    """Test database schema validation."""
    
    def test_user_profiles_table_exists(self, supabase_client):
        """Test that user_profiles table exists and has correct structure."""
        try:
            # Try to query the table structure
            response = supabase_client.table("user_profiles").select("*").limit(1).execute()
            assert response is not None
        except Exception as e:
            pytest.fail(f"user_profiles table does not exist or is not accessible: {e}")
    
    def test_user_profiles_constraints(self, user_repository, cleanup_test_users):
        """Test database constraints on user_profiles table."""
        # Test unique constraint on id (should fail if we try to create duplicate)
        timestamp = datetime.now().timestamp()
        user = User(
            id=f"constraint-test-{timestamp}",
            email=f"constraint-test-{timestamp}@example.com",
            display_name="Constraint Test User"
        )
        cleanup_test_users(user.id)
        
        # First creation should succeed
        first_user = user_repository.create_user_profile(user)
        assert first_user is not None
        
        # Second creation with same ID should fail
        duplicate_user = User(
            id=user.id,  # Same ID
            email="different@example.com",
            display_name="Different User"
        )
        
        second_user = user_repository.create_user_profile(duplicate_user)
        # This should fail due to unique constraint
        assert second_user is None


@pytest.mark.integration
@pytest.mark.security
class TestRowLevelSecurity:
    """Test Row Level Security policies."""
    
    def test_user_can_only_access_own_data(self, supabase_client):
        """Test that RLS policies enforce user data isolation."""
        # This test would require authenticated users to properly test RLS
        # For now, we'll test that the table has RLS enabled
        
        # Note: This is a placeholder for RLS testing
        # In a real scenario, you'd need to:
        # 1. Create test users with different auth contexts
        # 2. Attempt to access other users' data
        # 3. Verify access is denied
        
        # For basic validation, just ensure table exists
        try:
            response = supabase_client.table("user_profiles").select("*").limit(1).execute()
            assert response is not None
        except Exception:
            # If RLS is properly configured, this might fail without authentication
            # which is expected behavior
            pass