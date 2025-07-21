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
    
    def get_current_user(self, supabase_client) -> Optional[User]:
        """Get current user data from Supabase client and fetch full profile from repository."""
        try:
            if not supabase_client.is_authenticated():
                return None
                
            client = supabase_client.get_client()
            response = client.auth.get_user()
            
            if response and response.user:
                user_id = response.user.id
                
                # Fetch full user profile from repository
                user_profile = self.user_repo.get_user_profile(user_id)
                
                if user_profile:
                    # Update last active timestamp
                    self.user_repo.update_last_active(user_id)
                    return user_profile
                else:
                    # If no profile exists, create one from auth data
                    auth_user = response.user
                    display_name = (
                        auth_user.user_metadata.get("full_name") if auth_user.user_metadata
                        else auth_user.user_metadata.get("name") if auth_user.user_metadata
                        else auth_user.email.split('@')[0] if auth_user.email
                        else "Unknown"
                    )
                    
                    # Use get_or_create_user_profile to handle creation
                    return self.get_or_create_user_profile(
                        user_id, 
                        auth_user.email, 
                        display_name
                    )
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None