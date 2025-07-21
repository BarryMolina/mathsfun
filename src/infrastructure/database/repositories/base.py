"""Base repository for MathsFun application."""

from abc import ABC
from typing import Any
from supabase import Client


class BaseRepository(ABC):
    """Base repository class providing common database operations."""
    
    def __init__(self, supabase_client: Client):
        """Initialize repository with Supabase client."""
        self.client = supabase_client
    
    def _handle_response(self, response: Any) -> Any:
        """Handle Supabase response and extract data."""
        if hasattr(response, 'data') and response.data is not None:
            return response.data
        return None
    
    def _handle_single_response(self, response: Any) -> Any:
        """Handle Supabase response for single record."""
        data = self._handle_response(response)
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return data if data and not isinstance(data, list) else None