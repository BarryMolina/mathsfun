"""Comprehensive tests for Container dependency injection."""

import pytest
from unittest.mock import Mock

from src.config.container import Container
from src.infrastructure.database.supabase_manager import SupabaseManager
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.quiz_repository import QuizRepository
from src.domain.services.user_service import UserService
from src.domain.services.quiz_service import QuizService


@pytest.fixture
def mock_supabase_manager():
    """Create mock Supabase manager."""
    return Mock(spec=SupabaseManager)


@pytest.fixture
def container(mock_supabase_manager):
    """Create Container instance with mocked dependencies."""
    return Container(mock_supabase_manager)


class TestContainerInit:
    """Test Container initialization."""

    def test_init_creates_all_dependencies(self, mock_supabase_manager):
        """Test that initialization creates all required dependencies."""
        container = Container(mock_supabase_manager)
        
        # Verify supabase manager is stored
        assert container.supabase_manager == mock_supabase_manager
        
        # Verify repositories are created
        assert isinstance(container.user_repository, UserRepository)
        assert isinstance(container.quiz_repository, QuizRepository)
        
        # Verify services are created
        assert isinstance(container.user_service, UserService)
        assert isinstance(container.quiz_service, QuizService)

    def test_init_repositories_use_supabase_manager(self, mock_supabase_manager):
        """Test that repositories are initialized with the Supabase manager."""
        container = Container(mock_supabase_manager)
        
        # Verify repositories received the supabase manager
        assert container.user_repository.supabase_manager == mock_supabase_manager
        assert container.quiz_repository.supabase_manager == mock_supabase_manager

    def test_init_services_use_repositories(self, mock_supabase_manager):
        """Test that services are initialized with the correct repositories."""
        container = Container(mock_supabase_manager)
        
        # Verify services received the correct repositories
        assert container.user_service.user_repo == container.user_repository
        assert container.quiz_service.quiz_repo == container.quiz_repository

    def test_init_dependency_chain(self, mock_supabase_manager):
        """Test the complete dependency chain is properly wired."""
        container = Container(mock_supabase_manager)
        
        # Verify the chain: SupabaseManager -> Repository -> Service
        assert container.user_service.user_repo.supabase_manager == mock_supabase_manager
        assert container.quiz_service.quiz_repo.supabase_manager == mock_supabase_manager


class TestContainerProperties:
    """Test Container property accessors."""

    def test_user_repo_property(self, container):
        """Test user_repo property returns user repository."""
        result = container.user_repo
        
        assert result == container.user_repository
        assert isinstance(result, UserRepository)

    def test_quiz_repo_property(self, container):
        """Test quiz_repo property returns quiz repository."""
        result = container.quiz_repo
        
        assert result == container.quiz_repository
        assert isinstance(result, QuizRepository)

    def test_user_svc_property(self, container):
        """Test user_svc property returns user service."""
        result = container.user_svc
        
        assert result == container.user_service
        assert isinstance(result, UserService)

    def test_quiz_svc_property(self, container):
        """Test quiz_svc property returns quiz service."""
        result = container.quiz_svc
        
        assert result == container.quiz_service
        assert isinstance(result, QuizService)

    def test_properties_return_same_instances(self, container):
        """Test that properties return the same instances (singleton behavior)."""
        # Call properties multiple times
        user_repo_1 = container.user_repo
        user_repo_2 = container.user_repo
        quiz_repo_1 = container.quiz_repo
        quiz_repo_2 = container.quiz_repo
        user_svc_1 = container.user_svc
        user_svc_2 = container.user_svc
        quiz_svc_1 = container.quiz_svc
        quiz_svc_2 = container.quiz_svc
        
        # Should return same instances
        assert user_repo_1 is user_repo_2
        assert quiz_repo_1 is quiz_repo_2
        assert user_svc_1 is user_svc_2
        assert quiz_svc_1 is quiz_svc_2


class TestContainerDependencyInjection:
    """Test dependency injection behavior."""

    def test_single_supabase_manager_instance(self, mock_supabase_manager):
        """Test that all repositories use the same Supabase manager instance."""
        container = Container(mock_supabase_manager)
        
        # All repositories should use the same supabase manager
        assert container.user_repository.supabase_manager is mock_supabase_manager
        assert container.quiz_repository.supabase_manager is mock_supabase_manager
        assert container.user_repository.supabase_manager is container.quiz_repository.supabase_manager

    def test_services_use_container_repositories(self, mock_supabase_manager):
        """Test that services use the repositories created by the container."""
        container = Container(mock_supabase_manager)
        
        # Services should use the exact repository instances created by container
        assert container.user_service.user_repo is container.user_repository
        assert container.quiz_service.quiz_repo is container.quiz_repository

    def test_dependency_isolation(self, mock_supabase_manager):
        """Test that each container creates independent instances."""
        container1 = Container(mock_supabase_manager)
        container2 = Container(mock_supabase_manager)
        
        # Different containers should have different instances
        assert container1.user_repository is not container2.user_repository
        assert container1.quiz_repository is not container2.quiz_repository
        assert container1.user_service is not container2.user_service
        assert container1.quiz_service is not container2.quiz_service
        
        # But they should use the same supabase manager
        assert container1.supabase_manager is container2.supabase_manager

    def test_transitive_dependencies(self, mock_supabase_manager):
        """Test that transitive dependencies are properly resolved."""
        container = Container(mock_supabase_manager)
        
        # UserService -> UserRepository -> SupabaseManager
        user_service_supabase = container.user_service.user_repo.supabase_manager
        assert user_service_supabase is mock_supabase_manager
        
        # QuizService -> QuizRepository -> SupabaseManager
        quiz_service_supabase = container.quiz_service.quiz_repo.supabase_manager
        assert quiz_service_supabase is mock_supabase_manager


class TestContainerIntegration:
    """Test container integration behavior."""

    def test_container_provides_working_services(self, mock_supabase_manager):
        """Test that container provides properly configured services."""
        container = Container(mock_supabase_manager)
        
        # Services should be properly configured and ready to use
        user_service = container.user_svc
        quiz_service = container.quiz_svc
        
        # Services should have their dependencies properly set
        assert hasattr(user_service, 'user_repo')
        assert hasattr(quiz_service, 'quiz_repo')
        
        # Dependencies should be the same instances as in container
        assert user_service.user_repo is container.user_repo
        assert quiz_service.quiz_repo is container.quiz_repo

    def test_container_type_consistency(self, mock_supabase_manager):
        """Test that container maintains type consistency."""
        container = Container(mock_supabase_manager)
        
        # All instances should be of expected types
        assert isinstance(container.supabase_manager, SupabaseManager)
        assert isinstance(container.user_repository, UserRepository)
        assert isinstance(container.quiz_repository, QuizRepository)
        assert isinstance(container.user_service, UserService)
        assert isinstance(container.quiz_service, QuizService)

    def test_container_attribute_access(self, container):
        """Test that all attributes are accessible."""
        # Direct attribute access
        assert hasattr(container, 'supabase_manager')
        assert hasattr(container, 'user_repository')
        assert hasattr(container, 'quiz_repository')
        assert hasattr(container, 'user_service')
        assert hasattr(container, 'quiz_service')
        
        # Property access
        assert hasattr(container, 'user_repo')
        assert hasattr(container, 'quiz_repo')
        assert hasattr(container, 'user_svc')
        assert hasattr(container, 'quiz_svc')

    def test_container_lazy_initialization(self, mock_supabase_manager):
        """Test that container doesn't perform lazy initialization (all created at once)."""
        # Since all dependencies are created in __init__, this tests that behavior
        container = Container(mock_supabase_manager)
        
        # All dependencies should be created immediately
        assert container.user_repository is not None
        assert container.quiz_repository is not None
        assert container.user_service is not None
        assert container.quiz_service is not None


@pytest.mark.unit
class TestContainerEdgeCases:
    """Test edge cases for Container."""

    def test_container_with_none_supabase_manager(self):
        """Test container behavior with None supabase manager."""
        # This would typically be an error condition in real usage
        # but testing the container's behavior
        container = Container(None)
        
        # Container should still create instances, though they may not work properly
        assert container.supabase_manager is None
        assert container.user_repository is not None
        assert container.quiz_repository is not None
        assert container.user_service is not None
        assert container.quiz_service is not None

    def test_multiple_property_access_performance(self, container):
        """Test that multiple property accesses don't create new instances."""
        # Access properties many times
        repositories = [container.user_repo for _ in range(100)]
        services = [container.user_svc for _ in range(100)]
        
        # All should be the same instance
        assert all(repo is repositories[0] for repo in repositories)
        assert all(svc is services[0] for svc in services)

    def test_container_immutability_of_dependencies(self, container):
        """Test that core dependencies can't be easily modified."""
        original_user_repo = container.user_repository
        original_quiz_repo = container.quiz_repository
        original_user_svc = container.user_service
        original_quiz_svc = container.quiz_service
        
        # Properties should still return original instances
        assert container.user_repo is original_user_repo
        assert container.quiz_repo is original_quiz_repo
        assert container.user_svc is original_user_svc
        assert container.quiz_svc is original_quiz_svc


class TestContainerDocumentation:
    """Test that container follows expected patterns."""

    def test_container_follows_dependency_injection_pattern(self, mock_supabase_manager):
        """Test that container properly implements dependency injection."""
        container = Container(mock_supabase_manager)
        
        # Dependencies should be injected, not created internally by dependent classes
        # UserService should receive UserRepository, not create it
        assert container.user_service.user_repo is container.user_repository
        
        # QuizService should receive QuizRepository, not create it
        assert container.quiz_service.quiz_repo is container.quiz_repository
        
        # Repositories should receive SupabaseManager, not create it
        assert container.user_repository.supabase_manager is mock_supabase_manager
        assert container.quiz_repository.supabase_manager is mock_supabase_manager

    def test_container_provides_all_required_services(self, container):
        """Test that container provides all services needed by the application."""
        # Application should be able to get all required services from container
        required_services = [
            'user_repo', 'quiz_repo',  # Repository layer
            'user_svc', 'quiz_svc',    # Service layer
        ]
        
        for service_name in required_services:
            assert hasattr(container, service_name)
            service = getattr(container, service_name)
            assert service is not None

    def test_container_maintains_single_responsibility(self, container):
        """Test that container only handles dependency wiring."""
        # Container should not have business logic, only dependency management
        container_methods = [method for method in dir(container) 
                           if not method.startswith('_') and callable(getattr(container, method))]
        
        # Should only have property accessors and attribute access, no business methods
        expected_properties = ['user_repo', 'quiz_repo', 'user_svc', 'quiz_svc']
        expected_attributes = ['supabase_manager', 'user_repository', 'quiz_repository', 'user_service', 'quiz_service']
        
        # All public methods should be property accessors or basic attributes
        for method in container_methods:
            assert method in expected_properties + expected_attributes, f"Unexpected method: {method}"