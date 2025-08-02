"""Dependency injection container for MathsFun application."""

from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.quiz_repository import QuizRepository
from src.infrastructure.database.repositories.math_fact_repository import (
    MathFactRepository,
)
from src.domain.services.user_service import UserService
from src.domain.services.quiz_service import QuizService
from src.domain.services.math_fact_service import MathFactService
from src.infrastructure.database.supabase_manager import SupabaseManager


class Container:
    """Dependency injection container that wires up all dependencies."""

    def __init__(self, supabase_manager: SupabaseManager):
        """Initialize container with Supabase manager."""
        self.supabase_manager = supabase_manager

        # Initialize repositories
        self.user_repository = UserRepository(supabase_manager)
        self.quiz_repository = QuizRepository(supabase_manager)
        self.math_fact_repository = MathFactRepository(supabase_manager)

        # Initialize services
        self.user_service = UserService(self.user_repository)
        self.quiz_service = QuizService(self.quiz_repository)
        self.math_fact_service = MathFactService(self.math_fact_repository)

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
    def math_fact_repo(self) -> MathFactRepository:
        """Get math fact repository."""
        return self.math_fact_repository

    @property
    def math_fact_svc(self) -> MathFactService:
        """Get math fact service."""
        return self.math_fact_service
