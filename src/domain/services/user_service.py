"""User service for MathsFun application."""

from typing import Optional
from datetime import datetime, timezone
from src.infrastructure.database.repositories.user_repository import UserRepository
from ..models.user import User


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository):
        """Initialize service with user repository and supabase manager."""
        self.user_repo = user_repository
        self.supabase_manager = user_repository.supabase_manager
        self._cached_user: Optional[User] = None
        self._cached_user_id: Optional[str] = None

    def get_or_create_user_profile(
        self, user_id: str, email: str, display_name: Optional[str] = None
    ) -> Optional[User]:
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
            display_name=display_name or email.split("@")[0],
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc),
        )

        created_user = self.user_repo.create_user_profile(new_user)

        # If creation failed due to duplicate key, try to fetch the existing user
        if not created_user:
            user = self.user_repo.get_user_profile(user_id)
            if user:
                # Update last active for the existing user
                self.user_repo.update_last_active(user_id)
                # Clear cache to ensure fresh data on next get_current_user call
                self.clear_user_cache()
                return user
        else:
            # Clear cache when new profile is created
            self.clear_user_cache()

        return created_user

    def update_display_name(self, user_id: str, display_name: str) -> Optional[User]:
        """Update user's display name."""
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            return None

        user.display_name = display_name
        updated_user = self.user_repo.update_user_profile(user)

        # Clear cache after profile update
        if updated_user:
            self.clear_user_cache()

        return updated_user

    def get_current_user(self, force_refresh: bool = False) -> Optional[User]:
        """Get current user data with smart caching for auth and profile data."""
        try:
            if not self.supabase_manager.is_authenticated():
                return None

            client = self.supabase_manager.get_client()

            # Choose auth method based on force_refresh
            if force_refresh:
                # Fresh API call for accurate auth verification
                response = client.auth.get_user()
                if not response or not response.user:
                    return None
                user_id = response.user.id
            else:
                # Use cached session for performance
                session = client.auth.get_session()
                if not session or not session.user:
                    return None
                user_id = session.user.id

            # Return cached profile if same user and no force refresh
            if (
                not force_refresh
                and self._cached_user
                and self._cached_user_id == user_id
            ):
                return self._cached_user

            # Fetch fresh profile data and cache it
            user_profile = self.user_repo.get_user_profile(user_id)

            if user_profile:
                # Cache the profile data
                self._cached_user = user_profile
                self._cached_user_id = user_id
                # Update last active timestamp
                self.user_repo.update_last_active(user_id)
                return user_profile
            else:
                # If no profile exists, create one from auth data
                if force_refresh:
                    if not response:
                        return None
                    auth_user = response.user
                else:
                    if not session:
                        return None
                    auth_user = session.user
                display_name = None
                if auth_user.user_metadata:
                    display_name = auth_user.user_metadata.get(
                        "full_name"
                    ) or auth_user.user_metadata.get("name")

                if not display_name:
                    display_name = (
                        auth_user.email.split("@")[0] if auth_user.email else "Unknown"
                    )

                # Use get_or_create_user_profile to handle creation
                if not auth_user.email:
                    return None
                created_user = self.get_or_create_user_profile(
                    user_id, auth_user.email, display_name
                )

                # Cache the newly created profile
                if created_user:
                    self._cached_user = created_user
                    self._cached_user_id = user_id

                return created_user

        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None

    def clear_user_cache(self):
        """Clear cached user data - call after profile updates or when needed."""
        self._cached_user = None
        self._cached_user_id = None
