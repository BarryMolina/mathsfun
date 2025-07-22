"""User model for MathsFun application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Represents a user profile in the system."""

    id: str
    email: str
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create User instance from dictionary data."""
        return cls(
            id=data["id"],
            email=data["email"],
            display_name=data.get("display_name"),
            created_at=(
                datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                if data.get("created_at")
                else None
            ),
            last_active=(
                datetime.fromisoformat(data["last_active"].replace("Z", "+00:00"))
                if data.get("last_active")
                else None
            ),
        )

    def to_dict(self) -> dict:
        """Convert User instance to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }
