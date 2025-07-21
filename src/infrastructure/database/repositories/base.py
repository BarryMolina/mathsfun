"""Base repository for MathsFun application."""

from abc import ABC
from typing import Any, Callable, TypeVar, Optional
from functools import wraps
from supabase import Client
from src.infrastructure.database.supabase_manager import SupabaseManager

# Type variable for return type preservation
T = TypeVar("T")


def requires_authentication(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    Decorator that ensures the user is authenticated before executing the method.

    Returns None if the user is not authenticated, otherwise executes the original method.
    Can be applied to any repository method that requires authentication.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Optional[T]:
        if not hasattr(self, "supabase_manager"):
            print("Error: Repository does not have supabase_manager")
            return None

        if not self.supabase_manager.is_authenticated():
            print("User not authenticated")
            return None

        return func(self, *args, **kwargs)

    return wrapper


class BaseRepository(ABC):
    """Base repository class providing common database operations."""

    def __init__(self, supabase_manager: SupabaseManager):
        """Initialize repository with Supabase manager."""
        self.supabase_manager = supabase_manager

    def _handle_response(self, response: Any) -> Any:
        """Handle Supabase response and extract data."""
        if hasattr(response, "data") and response.data is not None:
            return response.data
        return None

    def _handle_single_response(self, response: Any) -> Any:
        """Handle Supabase response for single record."""
        data = self._handle_response(response)
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return data if data and not isinstance(data, list) else None
