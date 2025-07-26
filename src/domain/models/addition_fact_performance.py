"""Domain model for addition fact performance tracking."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .mastery_level import MasteryLevel


@dataclass
class AdditionFactPerformance:
    """Represents performance tracking for a specific addition fact.

    Tracks accuracy, speed, and mastery progression for individual
    addition facts like "7+8" or "3+5".
    """

    id: str
    user_id: str
    fact_key: str  # e.g., "7+8", "3+5"
    total_attempts: int = 0
    correct_attempts: int = 0
    total_response_time_ms: int = 0
    fastest_response_ms: Optional[int] = None
    slowest_response_ms: Optional[int] = None
    last_attempted: Optional[datetime] = None
    mastery_level: MasteryLevel = MasteryLevel.LEARNING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage.

        Returns:
            Accuracy as a percentage (0.0 to 100.0)
        """
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_attempts / self.total_attempts) * 100

    @property
    def average_response_time_ms(self) -> float:
        """Calculate average response time in milliseconds.

        Returns:
            Average response time for correct attempts only
        """
        if self.correct_attempts == 0:
            return 0.0
        return self.total_response_time_ms / self.correct_attempts

    @property
    def average_response_time_seconds(self) -> float:
        """Calculate average response time in seconds.

        Returns:
            Average response time for correct attempts in seconds
        """
        return self.average_response_time_ms / 1000

    def update_performance(
        self,
        is_correct: bool,
        response_time_ms: int,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Update performance metrics with a new attempt.

        Args:
            is_correct: Whether the attempt was correct
            response_time_ms: Response time in milliseconds
            timestamp: When the attempt was made (defaults to now)
        """
        self.total_attempts += 1
        self.last_attempted = timestamp or datetime.now()

        if is_correct:
            self.correct_attempts += 1
            self.total_response_time_ms += response_time_ms

            # Update fastest/slowest times for correct responses only
            if (
                self.fastest_response_ms is None
                or response_time_ms < self.fastest_response_ms
            ):
                self.fastest_response_ms = response_time_ms
            if (
                self.slowest_response_ms is None
                or response_time_ms > self.slowest_response_ms
            ):
                self.slowest_response_ms = response_time_ms

    def determine_mastery_level(self) -> MasteryLevel:
        """Determine the appropriate mastery level based on performance.

        Logic:
        - LEARNING: < 80% accuracy OR < 5 attempts
        - PRACTICING: 80-94% accuracy with 5+ attempts
        - MASTERED: 95%+ accuracy with 10+ attempts

        Returns:
            Appropriate MasteryLevel for current performance
        """
        if self.total_attempts < 5:
            return MasteryLevel.LEARNING

        accuracy = self.accuracy

        if accuracy >= 95 and self.total_attempts >= 10:
            return MasteryLevel.MASTERED
        elif accuracy >= 80:
            return MasteryLevel.PRACTICING
        else:
            return MasteryLevel.LEARNING

    @classmethod
    def create_new(
        cls, user_id: str, fact_key: str, id: Optional[str] = None
    ) -> "AdditionFactPerformance":
        """Create a new AdditionFactPerformance instance.

        Args:
            user_id: ID of the user
            fact_key: The addition fact key (e.g., "7+8")
            id: Optional ID (will be generated if not provided)

        Returns:
            New AdditionFactPerformance instance
        """
        import uuid

        return cls(
            id=id or str(uuid.uuid4()),
            user_id=user_id,
            fact_key=fact_key,
            mastery_level=MasteryLevel.LEARNING,
            created_at=datetime.now(),
        )

    @classmethod
    def from_dict(cls, data: dict) -> "AdditionFactPerformance":
        """Create AdditionFactPerformance from dictionary data.

        Args:
            data: Dictionary containing performance data

        Returns:
            AdditionFactPerformance instance
        """
        # Parse timestamps
        created_at = None
        if data.get("created_at"):
            created_at_str = data["created_at"].replace("Z", "+00:00")
            created_at = datetime.fromisoformat(created_at_str)

        updated_at = None
        if data.get("updated_at"):
            updated_at_str = data["updated_at"].replace("Z", "+00:00")
            updated_at = datetime.fromisoformat(updated_at_str)

        last_attempted = None
        if data.get("last_attempted"):
            last_attempted_str = data["last_attempted"].replace("Z", "+00:00")
            last_attempted = datetime.fromisoformat(last_attempted_str)

        # Parse mastery level
        mastery_level = MasteryLevel.from_string(data.get("mastery_level", "learning"))

        return cls(
            id=data["id"],
            user_id=data["user_id"],
            fact_key=data["fact_key"],
            total_attempts=data.get("total_attempts", 0),
            correct_attempts=data.get("correct_attempts", 0),
            total_response_time_ms=data.get("total_response_time_ms", 0),
            fastest_response_ms=data.get("fastest_response_ms"),
            slowest_response_ms=data.get("slowest_response_ms"),
            last_attempted=last_attempted,
            mastery_level=mastery_level,
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict:
        """Convert AdditionFactPerformance to dictionary.

        Returns:
            Dictionary representation suitable for database storage
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fact_key": self.fact_key,
            "total_attempts": self.total_attempts,
            "correct_attempts": self.correct_attempts,
            "total_response_time_ms": self.total_response_time_ms,
            "fastest_response_ms": self.fastest_response_ms,
            "slowest_response_ms": self.slowest_response_ms,
            "last_attempted": (
                self.last_attempted.isoformat() if self.last_attempted else None
            ),
            "mastery_level": self.mastery_level.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
