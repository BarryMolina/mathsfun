"""Dependency injection container for MathsFun application."""

from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.quiz_repository import QuizRepository
from src.infrastructure.database.repositories.addition_fact_repository import AdditionFactRepository
from src.domain.services.user_service import UserService
from src.domain.services.quiz_service import QuizService
from src.domain.services.addition_fact_service import AdditionFactService
from src.infrastructure.database.supabase_manager import SupabaseManager


class Container:
    """Dependency injection container that wires up all dependencies."""

    def __init__(self, supabase_manager: SupabaseManager):
        """Initialize container with Supabase manager."""
        self.supabase_manager = supabase_manager

        # Initialize repositories
        self.user_repository = UserRepository(supabase_manager)
        self.quiz_repository = QuizRepository(supabase_manager)
        self.addition_fact_repository = AdditionFactRepository(supabase_manager)

        # Initialize services
        self.user_service = UserService(self.user_repository)
        self.quiz_service = QuizService(self.quiz_repository)
        self.addition_fact_service = AdditionFactService(self.addition_fact_repository)

    @property
    def user_repo(self) -> UserRepository:
        """Get user repository."""
        return self.user_repository

    @property
    def quiz_repo(self) -> QuizRepository:
        """Get quiz repository."""
        return self.quiz_repository

    @property
    def user_svc(self) -> UserService:
        """Get user service."""
        return self.user_service

    @property
    def quiz_svc(self) -> QuizService:
        """Get quiz service."""
        return self.quiz_service

    @property
    def addition_fact_repo(self) -> AdditionFactRepository:
        """Get addition fact repository."""
        return self.addition_fact_repository

    @property
    def addition_fact_svc(self) -> AdditionFactService:
        """Get addition fact service."""
        return self.addition_fact_service
