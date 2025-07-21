"""User repository for MathsFun application."""

from typing import Optional
from .base import BaseRepository
from models.user import User


class UserRepository(BaseRepository):
    """Repository for user-related database operations."""
    
    def get_user_profile(self, user_id: str) -> Optional[User]:
        """Get user profile by ID."""
        try:
            response = self.client.table("user_profiles").select("*").eq("id", user_id).execute()
            data = self._handle_single_response(response)
            return User.from_dict(data) if data else None
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
    
    def create_user_profile(self, user: User) -> Optional[User]:
        """Create a new user profile."""
        try:
            response = self.client.table("user_profiles").insert(user.to_dict()).execute()
            data = self._handle_single_response(response)
            return User.from_dict(data) if data else None
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return None
    
    def update_user_profile(self, user: User) -> Optional[User]:
        """Update existing user profile."""
        try:
            response = self.client.table("user_profiles").update(user.to_dict()).eq("id", user.id).execute()
            data = self._handle_single_response(response)
            return User.from_dict(data) if data else None
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return None
    
    def update_last_active(self, user_id: str) -> bool:
        """Update user's last active timestamp."""
        try:
            from datetime import datetime
            response = self.client.table("user_profiles").update({
                "last_active": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            return self._handle_response(response) is not None
        except Exception as e:
            print(f"Error updating last active: {e}")
            return False