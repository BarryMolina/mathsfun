#!/usr/bin/env python3
"""
Centralized test user management for integration testing.

This module provides comprehensive user lifecycle management for all types of
integration tests including automation, service layer, and repository layer tests.
It handles user creation, cleanup, state management, and provides isolation
between different test categories.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None


class TestUserCategory(Enum):
    """Categories of test users for different testing purposes."""
    AUTOMATION = "automation"      # pexpect CLI automation tests
    SERVICE = "service"           # Service layer integration tests  
    REPOSITORY = "repository"     # Repository layer integration tests
    INTEGRATION = "integration"   # End-to-end integration tests
    PERFORMANCE = "performance"   # Performance and load tests


@dataclass
class TestUserSpec:
    """Specification for creating a test user."""
    category: TestUserCategory
    email: str
    password: str
    display_name: str
    additional_data: Optional[Dict[str, Any]] = None


class TestUserManager:
    """
    Centralized manager for test user lifecycle in integration testing.
    
    Provides capabilities for:
    - Creating test users with different configurations
    - Managing user state and isolation between tests
    - Cleaning up test users after test execution
    - Supporting different test categories (automation, service, repository)
    """
    
    # Default test user specifications for different categories
    DEFAULT_USER_SPECS = {
        TestUserCategory.AUTOMATION: [
            TestUserSpec(
                category=TestUserCategory.AUTOMATION,
                email="automation.primary@mathsfun.test",
                password="TestPass123!",
                display_name="Automation Primary",
            ),
            TestUserSpec(
                category=TestUserCategory.AUTOMATION,
                email="automation.secondary@mathsfun.test", 
                password="TestPass456!",
                display_name="Automation Secondary",
            ),
            TestUserSpec(
                category=TestUserCategory.AUTOMATION,
                email="automation.signup@mathsfun.test",
                password="TestPassNew789!",
                display_name="Automation Signup",
            ),
        ],
        TestUserCategory.SERVICE: [
            TestUserSpec(
                category=TestUserCategory.SERVICE,
                email="service.test.user@mathsfun.test",
                password="ServicePass123!",
                display_name="Service Test User",
            ),
            TestUserSpec(
                category=TestUserCategory.SERVICE,
                email="service.quiz.user@mathsfun.test",
                password="ServiceQuiz456!",
                display_name="Service Quiz User",
                additional_data={"quiz_history": True}
            ),
        ],
        TestUserCategory.REPOSITORY: [
            TestUserSpec(
                category=TestUserCategory.REPOSITORY,
                email="repo.test.user@mathsfun.test", 
                password="RepoPass123!",
                display_name="Repository Test User",
            ),
            TestUserSpec(
                category=TestUserCategory.REPOSITORY,
                email="repo.edge.case@mathsfun.test",
                password="RepoEdge456!",
                display_name="Repository Edge Case",
                additional_data={"edge_case_data": True}
            ),
        ],
        TestUserCategory.INTEGRATION: [
            TestUserSpec(
                category=TestUserCategory.INTEGRATION,
                email="integration.flow@mathsfun.test",
                password="IntegrationPass123!",
                display_name="Integration Flow User",
                additional_data={"full_data_set": True}
            ),
        ],
        TestUserCategory.PERFORMANCE: [
            TestUserSpec(
                category=TestUserCategory.PERFORMANCE,
                email="performance.load@mathsfun.test",
                password="PerfPass123!",
                display_name="Performance Test User",
            ),
        ],
    }
    
    def __init__(self, environment: str = "local"):
        """
        Initialize the test user manager.
        
        Args:
            environment: Target environment ("local" or "test")
        """
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        
        # Track created users for cleanup
        self.created_users: Set[str] = set()
        self.session_users: Set[str] = set()
        
        # Supabase clients
        self.admin_client: Optional[Client] = None
        self.test_client: Optional[Client] = None
        
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Supabase clients for admin and test operations."""
        if not create_client:
            raise ImportError("Supabase client not available. Install with: pip install supabase")
        
        try:
            if self.environment == "local":
                # Local Supabase configuration
                supabase_url = "http://127.0.0.1:54321"
                anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
                service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
            else:
                # Use environment variables for other environments
                supabase_url = os.getenv("SUPABASE_URL")
                anon_key = os.getenv("SUPABASE_ANON_KEY") 
                service_key = os.getenv("SUPABASE_SERVICE_KEY")
                
                if not all([supabase_url, anon_key, service_key]):
                    raise ValueError("Missing required Supabase environment variables")
            
            # Admin client (service_role) for user management operations
            self.admin_client = create_client(supabase_url, service_key)
            
            # Test client (anon) for simulating real application usage
            self.test_client = create_client(supabase_url, anon_key)
            
            self.logger.info(f"Initialized Supabase clients for {self.environment} environment")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase clients: {e}")
            raise
    
    def create_test_users(self, categories: Optional[List[TestUserCategory]] = None) -> Dict[TestUserCategory, List[Dict[str, Any]]]:
        """
        Create test users for specified categories.
        
        Args:
            categories: List of user categories to create. If None, creates all default users.
            
        Returns:
            Dictionary mapping categories to lists of created user data
        """
        if not self.admin_client:
            raise RuntimeError("Admin client not initialized")
        
        if categories is None:
            categories = list(TestUserCategory)
        
        created_users = {}
        
        for category in categories:
            if category not in self.DEFAULT_USER_SPECS:
                self.logger.warning(f"No default specs for category: {category}")
                continue
                
            category_users = []
            
            for user_spec in self.DEFAULT_USER_SPECS[category]:
                try:
                    user_data = self._create_single_user(user_spec)
                    if user_data:
                        category_users.append(user_data)
                        self.created_users.add(user_spec.email)
                        self.session_users.add(user_spec.email)
                        
                except Exception as e:
                    self.logger.error(f"Failed to create user {user_spec.email}: {e}")
                    continue
            
            created_users[category] = category_users
            self.logger.info(f"Created {len(category_users)} users for category: {category.value}")
        
        return created_users
    
    def _create_single_user(self, user_spec: TestUserSpec) -> Optional[Dict[str, Any]]:
        """
        Create a single test user based on specification.
        
        Args:
            user_spec: User specification
            
        Returns:
            Created user data or None if creation failed
        """
        try:
            # Check if user already exists
            existing_user = self.admin_client.auth.admin.get_user_by_email(user_spec.email)
            if existing_user.user:
                self.logger.info(f"User {user_spec.email} already exists, skipping creation")
                return {
                    "id": existing_user.user.id,
                    "email": existing_user.user.email,
                    "display_name": user_spec.display_name,
                    "category": user_spec.category.value,
                    "created": False  # Indicates it was already existing
                }
            
        except Exception:
            # User doesn't exist, proceed with creation
            pass
        
        try:
            # Create user using admin client
            auth_response = self.admin_client.auth.admin.create_user({
                "email": user_spec.email,
                "password": user_spec.password,
                "email_confirm": True,  # Skip email confirmation for tests
                "user_metadata": {
                    "display_name": user_spec.display_name,
                    "test_category": user_spec.category.value,
                    "created_by": "test_user_manager"
                }
            })
            
            if not auth_response.user:
                self.logger.error(f"Failed to create user {user_spec.email}: No user returned")
                return None
            
            user_data = {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "display_name": user_spec.display_name,
                "category": user_spec.category.value,
                "created": True
            }
            
            # Add any additional data setup if specified
            if user_spec.additional_data:
                user_data.update(user_spec.additional_data)
                # Here you could add logic to create specific test data
                # based on the additional_data specifications
            
            self.logger.info(f"✅ Created test user: {user_spec.email} (ID: {auth_response.user.id})")
            
            # Small delay to ensure user is fully created and available
            time.sleep(0.5)
            
            return user_data
            
        except Exception as e:
            self.logger.error(f"Failed to create user {user_spec.email}: {e}")
            return None
    
    def get_test_user(self, category: TestUserCategory, index: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get a test user for a specific category.
        
        Args:
            category: User category
            index: Index of user within category (default: 0 for primary user)
            
        Returns:
            User data dictionary or None if not found
        """
        if category not in self.DEFAULT_USER_SPECS:
            return None
        
        user_specs = self.DEFAULT_USER_SPECS[category]
        if index >= len(user_specs):
            return None
        
        user_spec = user_specs[index]
        return {
            "email": user_spec.email,
            "password": user_spec.password,
            "display_name": user_spec.display_name,
            "category": user_spec.category.value,
        }
    
    def get_all_test_users(self, category: TestUserCategory) -> List[Dict[str, Any]]:
        """
        Get all test users for a specific category.
        
        Args:
            category: User category
            
        Returns:
            List of user data dictionaries
        """
        if category not in self.DEFAULT_USER_SPECS:
            return []
        
        users = []
        for user_spec in self.DEFAULT_USER_SPECS[category]:
            users.append({
                "email": user_spec.email,
                "password": user_spec.password,
                "display_name": user_spec.display_name,
                "category": user_spec.category.value,
            })
        
        return users
    
    def reset_user_state(self, email: str) -> bool:
        """
        Reset a user's state to clean condition for testing.
        
        Args:
            email: User email to reset
            
        Returns:
            True if reset successful, False otherwise
        """
        if not self.admin_client:
            return False
        
        try:
            # Get user by email
            user_response = self.admin_client.auth.admin.get_user_by_email(email)
            if not user_response.user:
                self.logger.warning(f"User {email} not found for state reset")
                return False
            
            user_id = user_response.user.id
            
            # Clear user's quiz sessions
            self.admin_client.table("quiz_sessions").delete().eq("user_id", user_id).execute()
            
            # Clear user's addition fact performance data  
            self.admin_client.table("addition_fact_performance").delete().eq("user_id", user_id).execute()
            
            # Reset any other user-specific data as needed
            
            self.logger.info(f"✅ Reset state for user: {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset state for user {email}: {e}")
            return False
    
    def cleanup_test_users(self, category: Optional[TestUserCategory] = None) -> int:
        """
        Clean up test users after testing.
        
        Args:
            category: Specific category to clean up. If None, cleans all created users.
            
        Returns:
            Number of users successfully cleaned up
        """
        if not self.admin_client:
            return 0
        
        cleanup_count = 0
        users_to_cleanup = set()
        
        if category:
            # Clean up specific category
            if category in self.DEFAULT_USER_SPECS:
                for user_spec in self.DEFAULT_USER_SPECS[category]:
                    users_to_cleanup.add(user_spec.email)
        else:
            # Clean up all created users
            users_to_cleanup = self.created_users.copy()
        
        for email in users_to_cleanup:
            try:
                # Get user by email
                user_response = self.admin_client.auth.admin.get_user_by_email(email)
                if user_response.user:
                    # Delete user
                    self.admin_client.auth.admin.delete_user(user_response.user.id)
                    cleanup_count += 1
                    self.logger.info(f"🧹 Cleaned up test user: {email}")
                else:
                    self.logger.info(f"User {email} not found (may have been already deleted)")
                
            except Exception as e:
                self.logger.error(f"Failed to clean up user {email}: {e}")
                continue
        
        # Clear tracking sets
        if category:
            # Remove only users from this category
            category_emails = {spec.email for spec in self.DEFAULT_USER_SPECS.get(category, [])}
            self.created_users -= category_emails
            self.session_users -= category_emails
        else:
            # Clear all
            self.created_users.clear()
            self.session_users.clear()
        
        self.logger.info(f"✅ Cleaned up {cleanup_count} test users")
        return cleanup_count
    
    def cleanup_session_users(self) -> int:
        """
        Clean up users created during the current test session.
        
        Returns:
            Number of users successfully cleaned up
        """
        if not self.admin_client:
            return 0
        
        cleanup_count = 0
        
        for email in self.session_users.copy():
            try:
                user_response = self.admin_client.auth.admin.get_user_by_email(email)
                if user_response.user:
                    self.admin_client.auth.admin.delete_user(user_response.user.id)
                    cleanup_count += 1
                    self.logger.info(f"🧹 Session cleanup: {email}")
                
            except Exception as e:
                self.logger.error(f"Failed to clean up session user {email}: {e}")
                continue
        
        self.session_users.clear()
        self.logger.info(f"✅ Session cleanup completed: {cleanup_count} users")
        return cleanup_count
    
    def create_user_with_quiz_history(self, category: TestUserCategory, 
                                    quiz_count: int = 5) -> Optional[Dict[str, Any]]:
        """
        Create a test user with predefined quiz history.
        
        Args:
            category: User category
            quiz_count: Number of quiz sessions to create
            
        Returns:
            Created user data with quiz history
        """
        # For now, return a basic user - quiz history creation would be implemented
        # based on specific test requirements and the quiz session data structure
        return self.get_test_user(category)
    
    def is_local_supabase_available(self) -> bool:
        """
        Check if local Supabase instance is available.
        
        Returns:
            True if local Supabase is accessible, False otherwise
        """
        if not self.test_client:
            return False
        
        try:
            # Simple health check - try to access the auth endpoint
            response = self.test_client.auth.get_session()
            return True
        except Exception:
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        try:
            self.cleanup_session_users()
        except Exception as e:
            self.logger.error(f"Error during context manager cleanup: {e}")


def create_test_user_manager(environment: str = "local") -> TestUserManager:
    """
    Factory function to create a TestUserManager instance.
    
    Args:
        environment: Target environment ("local" or "test")
        
    Returns:
        Configured TestUserManager instance
    """
    return TestUserManager(environment=environment)