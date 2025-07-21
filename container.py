"""Dependency injection container for MathsFun application."""

from supabase import Client
from repositories.user_repository import UserRepository
from repositories.quiz_repository import QuizRepository
from services.user_service import UserService
from services.quiz_service import QuizService


class Container:
    """Dependency injection container that wires up all dependencies."""
    
    def __init__(self, supabase_client: Client):
        """Initialize container with Supabase client."""
        self.supabase_client = supabase_client
        
        # Initialize repositories
        self.user_repository = UserRepository(supabase_client)
        self.quiz_repository = QuizRepository(supabase_client)
        
        # Initialize services
        self.user_service = UserService(self.user_repository)
        self.quiz_service = QuizService(self.quiz_repository)
    
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