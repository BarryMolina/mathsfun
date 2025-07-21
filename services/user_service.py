"""User service for MathsFun application."""

from typing import Optional
from datetime import datetime
from repositories.user_repository import UserRepository
from models.user import User


class UserService:
    """Service for user-related business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize service with user repository."""
        self.user_repo = user_repository
    
    def get_or_create_user_profile(self, user_id: str, email: str, display_name: Optional[str] = None) -> Optional[User]:
        """Get existing user profile or create new one."""
        # Try to get existing profile
        user = self.user_repo.get_user_profile(user_id)
        
        if user:
            # Update last active
            self.user_repo.update_last_active(user_id)
            return user
        
        # Create new profile
        new_user = User(
            id=user_id,
            email=email,
            display_name=display_name or email.split('@')[0],
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        created_user = self.user_repo.create_user_profile(new_user)
        
        # If creation failed due to duplicate key, try to fetch the existing user
        if not created_user:
            user = self.user_repo.get_user_profile(user_id)
            if user:
                # Update last active for the existing user
                self.user_repo.update_last_active(user_id)
                return user
        
        return created_user
    
    def update_display_name(self, user_id: str, display_name: str) -> Optional[User]:
        """Update user's display name."""
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            return None
        
        user.display_name = display_name
        return self.user_repo.update_user_profile(user)