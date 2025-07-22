"""Quiz session model for MathsFun application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class QuizType(Enum):
    """Quiz type enumeration."""

    ADDITION = "addition"
    TABLES = "tables"


class SessionStatus(Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class QuizSession:
    """Represents a quiz session in the system."""

    id: str
    user_id: str
    quiz_type: QuizType
    difficulty_level: int
    start_time: datetime
    total_problems: int = 0
    correct_answers: int = 0
    status: SessionStatus = SessionStatus.ACTIVE
    end_time: Optional[datetime] = None

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_problems == 0:
            return 0.0
        return (self.correct_answers / self.total_problems) * 100

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate session duration in seconds."""
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds()

    @property
    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.status == SessionStatus.COMPLETED

    @classmethod
    def from_dict(cls, data: dict) -> "QuizSession":
        """Create QuizSession instance from dictionary data."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            quiz_type=QuizType(data["quiz_type"]),
            difficulty_level=data["difficulty_level"],
            start_time=datetime.fromisoformat(
                data["start_time"].replace("Z", "+00:00")
            ),
            total_problems=data.get("total_problems", 0),
            correct_answers=data.get("correct_answers", 0),
            status=SessionStatus(data.get("status", "active")),
            end_time=(
                datetime.fromisoformat(data["end_time"].replace("Z", "+00:00"))
                if data.get("end_time")
                else None
            ),
        )

    def to_dict(self) -> dict:
        """Convert QuizSession instance to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "quiz_type": self.quiz_type.value,
            "difficulty_level": self.difficulty_level,
            "start_time": self.start_time.isoformat(),
            "total_problems": self.total_problems,
            "correct_answers": self.correct_answers,
            "status": self.status.value,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }
