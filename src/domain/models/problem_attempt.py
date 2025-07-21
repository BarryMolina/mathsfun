"""Problem attempt model for MathsFun application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProblemAttempt:
    """Represents a single problem attempt in a quiz session."""
    
    id: str
    session_id: str
    problem: str
    correct_answer: int
    is_correct: bool
    response_time_ms: int
    timestamp: datetime
    user_answer: Optional[int] = None
    
    @property
    def response_time_seconds(self) -> float:
        """Get response time in seconds."""
        return self.response_time_ms / 1000.0
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProblemAttempt":
        """Create ProblemAttempt instance from dictionary data."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            problem=data["problem"],
            correct_answer=data["correct_answer"],
            is_correct=data["is_correct"],
            response_time_ms=data["response_time_ms"],
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
            user_answer=data.get("user_answer"),
        )
    
    def to_dict(self) -> dict:
        """Convert ProblemAttempt instance to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "problem": self.problem,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }