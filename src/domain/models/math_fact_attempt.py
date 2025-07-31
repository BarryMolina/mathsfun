"""Domain model for individual math fact attempts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MathFactAttempt:
    """Represents a single attempt at solving a math fact.

    This model stores time series data for each individual attempt,
    enabling detailed analysis of learning patterns and progress.
    """

    id: str
    user_id: str
    fact_key: str  # e.g., "7+8", "3+5"
    operand1: int
    operand2: int
    user_answer: Optional[int]  # None if user didn't provide an answer
    correct_answer: int
    is_correct: bool
    response_time_ms: int
    incorrect_attempts_in_session: int = (
        0  # How many times user got it wrong before this attempt
    )
    sm2_grade: Optional[int] = None  # SM-2 grade (0-5) calculated from this attempt
    attempted_at: Optional[datetime] = None

    @property
    def response_time_seconds(self) -> float:
        """Get response time in seconds.

        Returns:
            Response time converted to seconds
        """
        return self.response_time_ms / 1000

    @classmethod
    def create_new(
        cls,
        user_id: str,
        fact_key: str,
        operand1: int,
        operand2: int,
        user_answer: Optional[int],
        correct_answer: int,
        is_correct: bool,
        response_time_ms: int,
        incorrect_attempts_in_session: int = 0,
        sm2_grade: Optional[int] = None,
        id: Optional[str] = None,
    ) -> "MathFactAttempt":
        """Create a new MathFactAttempt instance.

        Args:
            user_id: ID of the user making the attempt
            fact_key: The math fact key (e.g., "7+8")
            operand1: First operand of the math fact
            operand2: Second operand of the math fact
            user_answer: User's answer (None if no answer provided)
            correct_answer: The correct answer
            is_correct: Whether the user's answer was correct
            response_time_ms: Time taken to respond in milliseconds
            incorrect_attempts_in_session: Number of incorrect attempts before this one
            sm2_grade: SM-2 grade (0-5) for this attempt
            id: Optional ID (will be generated if not provided)

        Returns:
            New MathFactAttempt instance
        """
        import uuid

        return cls(
            id=id or str(uuid.uuid4()),
            user_id=user_id,
            fact_key=fact_key,
            operand1=operand1,
            operand2=operand2,
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            incorrect_attempts_in_session=incorrect_attempts_in_session,
            sm2_grade=sm2_grade,
            attempted_at=datetime.now(),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "MathFactAttempt":
        """Create MathFactAttempt from dictionary data.

        Args:
            data: Dictionary containing attempt data

        Returns:
            MathFactAttempt instance
        """
        attempted_at = None
        if data.get("attempted_at"):
            attempted_at_str = data["attempted_at"].replace("Z", "+00:00")
            attempted_at = datetime.fromisoformat(attempted_at_str)

        return cls(
            id=data["id"],
            user_id=data["user_id"],
            fact_key=data["fact_key"],
            operand1=data["operand1"],
            operand2=data["operand2"],
            user_answer=data.get("user_answer"),
            correct_answer=data["correct_answer"],
            is_correct=data["is_correct"],
            response_time_ms=data["response_time_ms"],
            incorrect_attempts_in_session=data.get("incorrect_attempts_in_session", 0),
            sm2_grade=data.get("sm2_grade"),
            attempted_at=attempted_at,
        )

    def to_dict(self) -> dict:
        """Convert MathFactAttempt to dictionary.

        Returns:
            Dictionary representation suitable for database storage
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fact_key": self.fact_key,
            "operand1": self.operand1,
            "operand2": self.operand2,
            "user_answer": self.user_answer,
            "correct_answer": self.correct_answer,
            "is_correct": self.is_correct,
            "response_time_ms": self.response_time_ms,
            "incorrect_attempts_in_session": self.incorrect_attempts_in_session,
            "sm2_grade": self.sm2_grade,
            "attempted_at": (
                self.attempted_at.isoformat() if self.attempted_at else None
            ),
        }
